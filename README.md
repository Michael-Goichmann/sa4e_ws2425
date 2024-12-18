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

https://github.com/user-attachments/assets/5428b7cc-d397-4122-ab6f-a269e267a069


```
poetry run python .\U1\task_1_src\ex_1_task_1.py
```
### Task 2
```

https://github.com/user-attachments/assets/1d5e17c2-f648-4dd3-ba2a-3be38bab28e0


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
