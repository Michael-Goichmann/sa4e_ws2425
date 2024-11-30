import tkinter as tk
import threading
import time
import random
import math
import logging
import os
from threading import Lock, Event
from queue import Queue

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(threadName)s - %(levelname)s - %(message)s",
)


class Firefly(threading.Thread):
    def __init__(self, x, y, size, neighbors, update_callback):
        super().__init__(daemon=True)
        self.x = x
        self.y = y
        self.size = size
        self.neighbors = neighbors
        self.phase = random.uniform(0, 2 * math.pi)
        self.sync_rate = 0.1
        self.running = Event()  # Change to Event for better state management
        self.running.set()  # Set it to running initially
        self.update_callback = update_callback
        self.lock = Lock()

    def get_phase(self):
        with self.lock:
            return self.phase

    def adjust_phase(self, adjustment):
        with self.lock:
            self.phase += adjustment
            if self.phase >= 2 * math.pi:
                self.phase -= 2 * math.pi
            elif self.phase < 0:
                self.phase += 2 * math.pi

    def run(self):
        logging.debug(f"Firefly thread started at ({self.x}, {self.y})")
        while self.running.is_set():  # Check if we should continue running
            try:
                # Natural phase progression
                self.adjust_phase(0.1)

                # Only do neighbor calculations if still running
                if self.running.is_set():
                    # Kuramoto model synchronization
                    total_adjustment = 0
                    for neighbor in self.neighbors:
                        neighbor_phase = neighbor.get_phase()
                        current_phase = self.get_phase()
                        delta_phase = math.sin(neighbor_phase - current_phase)
                        total_adjustment += self.sync_rate * delta_phase

                    self.adjust_phase(total_adjustment)

                    # Calculate brightness
                    current_phase = self.get_phase()
                    brightness = int((1 + math.sin(current_phase)) * 127.5)
                    color = f"#{brightness:02x}{brightness:02x}00"

                    # Update visual representation
                    if self.running.is_set():  # Check again before updating
                        self.update_callback(self.x, self.y, color)

                # Short sleep with frequent checks
                for _ in range(5):  # Break sleep into smaller chunks
                    if not self.running.is_set():
                        break
                    time.sleep(0.01)  # 10ms chunks instead of one 50ms sleep

            except Exception as e:
                logging.error(
                    f"Error in firefly {self.name} at ({self.x}, {self.y}): {e}"
                )
                break

        logging.debug(f"Firefly thread at ({self.x}, {self.y}) stopping")

    def stop(self):
        """Stop the firefly thread"""
        self.running.clear()  # Clear the running event


class FireflySimulation:
    def __init__(self, root, rows, cols, size):
        self.root = root
        self.canvas = tk.Canvas(root, width=cols * size, height=rows * size, bg="black")
        self.canvas.pack()
        self.rows = rows
        self.cols = cols
        self.size = size
        self.fireflies = []
        self.rectangles = {}
        self.gui_lock = Lock()
        self.stopping = Event()
        self.update_queue = Queue()  # Queue for GUI updates

        # Create rectangles for visualization
        for i in range(rows):
            for j in range(cols):
                x, y = j * size, i * size
                rect_id = self.canvas.create_rectangle(
                    x, y, x + size, y + size, fill="black", outline=""
                )
                self.rectangles[(i, j)] = rect_id

        # Create firefly threads
        for i in range(rows):
            row = []
            for j in range(cols):
                firefly = Firefly(
                    i,
                    j,
                    size,
                    [],
                    lambda x, y, color, i=i, j=j: self.queue_update(i, j, color),
                )
                row.append(firefly)
            self.fireflies.append(row)

        # Set up neighbors in torus topology
        for i in range(rows):
            for j in range(cols):
                self.fireflies[i][j].neighbors = self.get_neighbors(i, j)

        # Start update processing
        self.process_updates()

    def queue_update(self, x, y, color):
        """Queue a GUI update instead of doing it directly"""
        if not self.stopping.is_set():
            self.update_queue.put((x, y, color))

    def process_updates(self):
        """Process queued updates"""
        try:
            while not self.stopping.is_set() and not self.update_queue.empty():
                x, y, color = self.update_queue.get_nowait()
                rect_id = self.rectangles[(x, y)]
                self.canvas.itemconfig(rect_id, fill=color)
        except Exception as e:
            logging.error(f"Error processing updates: {e}")

        if not self.stopping.is_set():
            self.root.after(16, self.process_updates)  # Schedule next update

    def get_neighbors(self, i, j):
        neighbors = []
        for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ni = (i + di) % self.rows
            nj = (j + dj) % self.cols
            neighbors.append(self.fireflies[ni][nj])
        return neighbors

    def start(self):
        """Start all firefly threads"""
        logging.info("Starting simulation...")
        self.stopping.clear()
        for row in self.fireflies:
            for firefly in row:
                firefly.start()

    def stop(self):
        """Stop all firefly threads"""
        if self.stopping.is_set():
            return

        self.stopping.set()
        logging.info("Stopping simulation...")

        # First: stop all threads
        for row in self.fireflies:
            for firefly in row:
                firefly.stop()

        # Second: wait for threads with progress updates
        timeout = 1.0  # 1 second timeout
        start_time = time.time()
        total_threads = self.rows * self.cols

        while time.time() - start_time < timeout:
            active_threads = sum(
                1 for row in self.fireflies for firefly in row if firefly.is_alive()
            )
            if active_threads == 0:
                logging.info("All threads stopped gracefully")
                return

            logging.info(
                f"Waiting for {active_threads}/{total_threads} threads to stop..."
            )
            time.sleep(0.1)

        # If we get here, some threads didn't stop
        active_count = sum(
            1 for row in self.fireflies for firefly in row if firefly.is_alive()
        )
        if active_count > 0:
            logging.error(f"Failed to stop {active_count} threads gracefully")
            logging.error("Active thread positions:")
            for i, row in enumerate(self.fireflies):
                for j, firefly in enumerate(row):
                    if firefly.is_alive():
                        logging.error(f"Thread at position ({i}, {j}) still active")

            logging.warning("Forcing exit...")

            os._exit(0)


def main():
    root = tk.Tk()
    root.title("Synchronized Fireflies")

    rows, cols, size = 10, 10, 50
    simulation = FireflySimulation(root, rows, cols, size)

    def on_close():
        logging.info("Close requested by user")
        simulation.stop()
        root.after(100, root.destroy)  # Give a moment for cleanup

    root.protocol("WM_DELETE_WINDOW", on_close)
    simulation.start()
    root.mainloop()


if __name__ == "__main__":
    main()
