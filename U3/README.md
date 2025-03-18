# Circular Chariot Racing Simulation with Apache Kafka

## Overview
This project implements a distributed chariot racing simulation using Apache Kafka for message passing between race track segments. Each chariot (token) races through various segments including bottlenecks, Caesar meeting points, and regular track segments.

## Architecture
- Uses Apache Kafka with 3 brokers for distributed messaging
- Track segments run as independent Python processes
- Configurable number of tracks, track lengths, and chariots
- Special segments:
    - Start/Goal: Manages race start/end and lap counting
    - Bottleneck: Forces chariots to wait randomly
    - Caesar: Special meeting point each chariot must visit once
    - Normal: Standard track segments

## Prerequisites
- Python 3.12+ with poetry
- Docker and Docker Compose
- Required Python packages (installed via poetry):
    - kafka-python
    - Other dependencies listed in pyproject.toml

## Setup & Installation
1. Clone the repository
2. Install dependencies:
```bash
poetry install
```

## Running the Simulation
Use either the batch or shell script to start all components:

Windows:
```bash
run_all.bat [NUM_TRACKS] [LENGTH_OF_TRACK] [NUM_ROUNDS] [NUM_CHARIOTS]
```

Linux/Mac:
```bash
./run_all.sh [NUM_TRACKS] [LENGTH_OF_TRACK] [NUM_ROUNDS] [NUM_CHARIOTS]
```

Default values if not specified:
- NUM_TRACKS: 1
- LENGTH_OF_TRACK: 5
- NUM_ROUNDS: 6
- NUM_CHARIOTS: 4

## Project Structure
- `circular-course.py` - Generates track layout JSON
- `generate_architecture.py` - Creates Python files for track segments
- `docker-compose.yml` - Kafka/ZooKeeper configuration
- `generated_segments/` - Generated Python files for each segment
- `run_all.bat/sh` - Automation scripts

## Stopping the Simulation
1. The simulation ends automatically when all chariots complete their rounds
2. Stop Docker containers with:
```bash
docker-compose down
```

## License
This project is part of university coursework for the Module Software Architecture for Enterprise at Universität Trier.