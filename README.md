# Distributed Firefly Synchronization Simulation

## Overview
This project implements a distributed firefly synchronization simulation using gRPC, demonstrating how individual fireflies can synchronize their phases in a decentralized manner across a network.

## Key Features
- Distributed firefly processes using gRPC
- Kuramoto model-based synchronization
- Torus topology network communication
- Independent firefly state management

## Prerequisites
- Python 3.12
- Poetry (dependency management)

## Installation
1. Clone the repository
2. Install Poetry (if not already installed):
   ```
   pip install poetry
   ```
3. Install project dependencies:
   ```
   poetry install
   ```
4. Generate gRPC code:
   ```
   python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. firefly.proto
   ```

## Running the Simulation
### Task 1

https://github.com/user-attachments/assets/1565a4a9-c958-49d5-b444-6e2a03db20fb


```
poetry run python .\U1\task_1_src\ex_1_task_1.py
```
### Task 2

https://github.com/user-attachments/assets/6c285207-d8d7-4a1b-8682-12e7c5267db6


```
cd .\U1\task_2_src\
poetry run python main.py
```

## Development
- Run tests: `poetry run pytest`
- Type checking: `poetry run mypy .`

## Architecture
- Each firefly runs as an independent process
- Uses gRPC for inter-process communication
- Implements Kuramoto model synchronization logic
- Supports a grid-based network topology with torus connections
