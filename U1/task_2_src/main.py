import subprocess
import sys
import time
import tkinter as tk
import threading
import random
import math
import grpc
import firefly_pb2
import firefly_pb2_grpc

# Grid dimensions
ROWS = 5
COLS = 5

BASE_PORT = 60000

class FireflyVisualizer:
    def __init__(self, root, fireflies, size=50):
        self.root = root
        self.canvas = tk.Canvas(root, width=COLS * size, height=ROWS * size, bg="black")
        self.canvas.pack()
        self.size = size
        self.rectangles = {}
        self.fireflies = fireflies  # {(i, j): address}

        # Create rectangles for visualization
        for i in range(ROWS):
            for j in range(COLS):
                x, y = j * size, i * size
                rect_id = self.canvas.create_rectangle(
                    x, y, x + size, y + size, fill="black", outline=""
                )
                self.rectangles[(i, j)] = rect_id

        self.stubs = {}
        self.setup_stubs()
        self.update_visualization()

    def setup_stubs(self):
        for (i, j), address in self.fireflies.items():
            channel = grpc.insecure_channel(address)
            stub = firefly_pb2_grpc.FireflyServiceStub(channel)
            self.stubs[(i, j)] = stub

    def update_visualization(self):
        for (i, j), stub in self.stubs.items():
            try:
                response = stub.GetPhase(firefly_pb2.Empty())
                phase = response.phase
                brightness = int((1 + math.sin(phase)) * 127.5)
                color = f"#{brightness:02x}{brightness:02x}00"
                rect_id = self.rectangles[(i, j)]
                self.canvas.itemconfig(rect_id, fill=color)
            except grpc.RpcError:
                pass
        self.root.after(50, self.update_visualization)

def main():
    processes = []
    fireflies = {}  # {(i, j): address}
    for i in range(ROWS):
        for j in range(COLS):
            port = BASE_PORT + i * COLS + j
            address = f'localhost:{port}'
            fireflies[(i, j)] = address

    # Determine neighbors for each firefly in torus topology
    neighbor_map = {}
    for i in range(ROWS):
        for j in range(COLS):
            neighbors = []
            for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ni = (i + di) % ROWS
                nj = (j + dj) % COLS
                neighbors.append(fireflies[(ni, nj)])
            neighbor_map[(i, j)] = neighbors

    # Start firefly processes
    for (i, j), address in fireflies.items():
        neighbors = neighbor_map[(i, j)]
        cmd = [sys.executable, 'firefly.py', address] + neighbors
        process = subprocess.Popen(cmd)
        processes.append(process)

    # Start visualization
    root = tk.Tk()
    root.title("Synchronized Fireflies")
    visualizer = FireflyVisualizer(root, fireflies)
    try:
        root.mainloop()
    finally:
        # Terminate all firefly processes upon closing the window
        for process in processes:
            process.terminate()
        for process in processes:
            process.wait()

if __name__ == '__main__':
    main()