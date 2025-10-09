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
# Suppose you are using fish shell
# If you are using another shell, you need to source the corresponding file in .venv/bin
source .venv/bin/activate.fish
python3 server.py
```

This will automatically open the web browser and run the simulation program.

## TODO List

- [x] implement a basic LOOK algorithm
- [ ] improve effiency of the LOOK algorithm across multiple elevators
- [x] create a visualized version of the simulation program
  - [x] create the basic structure for visualization
  - [x] allow user to select traffic file
  - [x] show metrics
- [ ] create `start.sh`
