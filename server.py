import json
import os
import webbrowser
import elevator_saga.server.simulator as simulator
from elevator_saga.server.simulator import ElevatorSimulation, app
from flask import jsonify, request, send_from_directory

from controller import ElevatorBusController


@app.route("/demo/<path:filename>")
def static_file(filename):
    return send_from_directory(
        os.path.join(os.path.dirname(__file__), "templates"), filename
    )


@app.route("/list-traffic/")
def list_traffic():
    return jsonify(traffic_names)


@app.route("/simulation/")
def run_simulation():
    traffic_name = request.args.get("traffic")
    if traffic_name == None or traffic_name not in traffic_names:
        traffic_name = traffic_names[0]

    traffic_file = traffic_files[traffic_index[traffic_name]]
    simulator.simulation.traffic_files = [traffic_file]

    info = {}
    with open(str(traffic_file), mode="r", encoding="utf-8") as file:
        data = json.load(file)
        info = data["building"]

    c = ElevatorBusController()
    c.start()

    response = {
        "snapshots": c.snapshots,
        "metrics": simulator.simulation.get_state().metrics.to_dict(),
        "traffic": info,
    }
    return jsonify(response)


def main():
    global traffic_files, traffic_index, traffic_names

    host = "127.0.0.1"
    port = 8000

    simulator.simulation = ElevatorSimulation(
        os.path.join(os.path.dirname(simulator.__file__), "..", "traffic")
    )

    traffic_files = simulator.simulation.traffic_files
    simulator.simulation.traffic_files = [traffic_files[0]]

    traffic_names = [file.name.replace(".json", "") for file in traffic_files]
    traffic_index = dict(
        zip(
            traffic_names,
            range(len(traffic_files)),
        )
    )
    traffic_names.sort()

    print(f"Elevator simulation server running on http://{host}:{port}")
    webbrowser.open(f"http://{host}:{port}/demo/index.html")

    try:
        app.run(host=host, port=port, threaded=True)
    except KeyboardInterrupt:
        print("\nShutting down server...")


if __name__ == "__main__":
    main()
