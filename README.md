# Elevator Simulator

Algorithm & Visualization for <https://github.com/ZGCA-Forge/Elevator>.

## Environment Management

This project uses [uv](https://github.com/astral-sh/uv) to manage the Python environment.

To install uv, you can follow [official instructions](https://github.com/astral-sh/uv?tab=readme-ov-file#installation).

## Getting Started

You can run the following commands to clone the repo and install the required dependencies:

```bash
git clone https://github.com/Shaobin-Jiang/elevator-simulator
cd elevator-simulator
uv venv
uv sync
```

This will create and manage the virtual environment automatically.

## Running the Simulation

To run the simulation, you can use the following commands:

```bash
uv run server.py
```

The service now runs at <http://127.0.0.1:8000> by default and the web browser will automatically be opened to run the simulation program at <http://127.0.0.1:8000/demo/index.html>.

You can also view a report on the various metrics for different traffics files at <http://127.0.0.1:8000/report>.

### Run Script for Ubuntu 22.04

A `start.sh` has been provided for Ubuntu 22.04 as requested. Just run:

```bash
bash start.sh
```

It will install the necessary dependencies and start the simulation for you.

## TODO List

- [x] implement a basic LOOK algorithm
- [ ] improve effiency of the LOOK algorithm across multiple elevators
- [x] create a visualized version of the simulation program
  - [x] create the basic structure for visualization
  - [x] allow user to select traffic file
  - [x] show metrics
- [x] create `start.sh`
