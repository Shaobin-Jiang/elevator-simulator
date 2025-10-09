import os
import webbrowser
import elevator_saga.server.simulator as simulator
from elevator_saga.server.simulator import ElevatorSimulation, app
from flask import jsonify, send_from_directory

from controller import ElevatorBusController


@app.route("/demo/<path:filename>")
def static_file(filename):
    return send_from_directory(
        os.path.join(os.path.dirname(__file__), "templates"), filename
    )


@app.route("/simulation/")
def run_simulation():
    c = ElevatorBusController()
    c.start()
    return jsonify(c.snapshots)


def main():
    host = "127.0.0.1"
    port = 8000

    simulator.simulation = ElevatorSimulation(
        os.path.join(os.path.dirname(simulator.__file__), "..", "traffic")
    )

    print(f"Elevator simulation server running on http://{host}:{port}")
    webbrowser.open(f"http://{host}:{port}/demo/index.html")

    try:
        app.run(host=host, port=port, threaded=True)
    except KeyboardInterrupt:
        print("\nShutting down server...")


if __name__ == "__main__":
    main()
