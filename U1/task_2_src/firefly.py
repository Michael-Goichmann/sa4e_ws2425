import grpc
from concurrent import futures
import threading
import time
import random
import math
import sys

import firefly_pb2
import firefly_pb2_grpc

class Firefly(firefly_pb2_grpc.FireflyServiceServicer):
    def __init__(self, address, neighbors):
        self.address = address
        self.neighbors = neighbors
        self.phase = random.uniform(0, 2 * math.pi)
        self.sync_rate = 0.1
        self.lock = threading.Lock()
        self.running = True

    def UpdatePhase(self, request, context):
        with self.lock:
            delta = math.sin(request.phase - self.phase)
            self.phase += self.sync_rate * delta
            self.phase %= 2 * math.pi
        return firefly_pb2.Empty()

    def GetPhase(self, request, context):
        with self.lock:
            return firefly_pb2.PhaseResponse(phase=self.phase)

    def subscribe_to_neighbors(self):
        self.stubs = []
        for neighbor in self.neighbors:
            channel = grpc.insecure_channel(neighbor)
            stub = firefly_pb2_grpc.FireflyServiceStub(channel)
            self.stubs.append(stub)

    def run(self):
        self.subscribe_to_neighbors()
        while self.running:
            with self.lock:
                self.phase += 0.1
                self.phase %= 2 * math.pi
            for stub in self.stubs:
                message = firefly_pb2.PhaseMessage(phase=self.phase)
                try:
                    stub.UpdatePhase(message)
                except grpc.RpcError:
                    pass
            time.sleep(0.05)
    
    def stop(self):
        self.running = False

def serve(firefly):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    firefly_pb2_grpc.add_FireflyServiceServicer_to_server(firefly, server)
    try:
        server.add_insecure_port(firefly.address)
    except Exception as e:
        print(f"Failed to bind to address {firefly.address}: {e}")
        return
    server.start()
    try:
        firefly.run()
    except KeyboardInterrupt:
        pass
    server.stop(0)

if __name__ == '__main__':
    address = sys.argv[1]
    neighbors = sys.argv[2:]
    firefly = Firefly(address, neighbors)
    serve(firefly)