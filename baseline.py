from typing import List

from elevator_saga.client.base_controller import ElevatorController
from elevator_saga.client.proxy_models import ProxyElevator, ProxyFloor, ProxyPassenger
from elevator_saga.core.models import Direction, SimulationEvent


class ElevatorBusExampleController(ElevatorController):
    def __init__(self, url: str = "http://127.0.0.1:8000") -> None:
        super().__init__(url)
        self.all_passengers: List[ProxyPassenger] = []
        self.max_floor = 0
        self.snapshots = []

    def on_init(self, elevators: List[ProxyElevator], floors: List[ProxyFloor]) -> None:
        self.max_floor = floors[-1].floor
        self.floors = floors
        for i, elevator in enumerate(elevators):
            target_floor = (i * (len(floors) - 1)) // len(elevators)
            elevator.go_to_floor(target_floor, immediate=True)
        pass

    def on_event_execute_end(
        self, tick: int, events: List[SimulationEvent], elevators: List[ProxyElevator], floors: List[ProxyFloor]
    ) -> None:
        snapshot = {"floors": [], "elevators": []}
        for floor in floors:
            queue = [*floor.down_queue, *floor.up_queue]
            floor_snapshot = []
            for pid in queue:
                p = ProxyPassenger(pid, self.api_client)
                floor_snapshot.append({"id": pid, "o": p.origin, "d": p.destination})
            snapshot["floors"].append(floor_snapshot)
        for elevator in elevators:
            passengers = []
            for pid in elevator.passengers:
                p = ProxyPassenger(pid, self.api_client)
                passengers.append({"id": pid, "o": p.origin, "d": p.destination})
            snapshot["elevators"].append({"id": elevator.id, "floor": elevator.current_floor_float, "passengers": passengers})
        self.snapshots.append(snapshot)

    def on_passenger_call(self, passenger: ProxyPassenger, floor: ProxyFloor, direction: str) -> None:
        self.all_passengers.append(passenger)
        pass

    def on_elevator_idle(self, elevator: ProxyElevator) -> None:
        elevator.go_to_floor(1)

    def on_elevator_stopped(self, elevator: ProxyElevator, floor: ProxyFloor) -> None:
        if elevator.last_tick_direction == Direction.UP and elevator.current_floor == self.max_floor:
            elevator.go_to_floor(elevator.current_floor - 1)
        elif elevator.last_tick_direction == Direction.DOWN and elevator.current_floor == 0:
            elevator.go_to_floor(elevator.current_floor + 1)
        elif elevator.last_tick_direction == Direction.UP:
            elevator.go_to_floor(elevator.current_floor + 1)
        elif elevator.last_tick_direction == Direction.DOWN:
            elevator.go_to_floor(elevator.current_floor - 1)

    def on_event_execute_start(
        self, tick: int, events: List[SimulationEvent], elevators: List[ProxyElevator], floors: List[ProxyFloor]
    ) -> None:
        pass

    def on_passenger_board(self, elevator: ProxyElevator, passenger: ProxyPassenger) -> None:
        pass

    def on_passenger_alight(self, elevator: ProxyElevator, passenger: ProxyPassenger, floor: ProxyFloor) -> None:
        pass

    def on_elevator_passing_floor(self, elevator: ProxyElevator, floor: ProxyFloor, direction: str) -> None:
        pass

    def on_elevator_approaching(self, elevator: ProxyElevator, floor: ProxyFloor, direction: str) -> None:
        pass


if __name__ == "__main__":
    ElevatorBusExampleController().start()
