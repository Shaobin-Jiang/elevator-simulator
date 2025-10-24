from typing import Dict, List, Literal, cast

from elevator_saga.client.base_controller import ElevatorController
from elevator_saga.client.proxy_models import ProxyElevator, ProxyFloor, ProxyPassenger
from elevator_saga.core.models import SimulationEvent

PassengerDirection = Literal["up", "down"]


class ElevatorBusController(ElevatorController):
    def __init__(self, url: str = "http://127.0.0.1:8000"):
        super().__init__(url)
        self.snapshots = []

    def on_init(self, elevators: List[ProxyElevator], floors: List[ProxyFloor]) -> None:
        self.all_floors = floors

        # The next move for each elevator after it stops
        self.next_move: Dict[int, int | None] = {}

        self.car_calls: Dict[int, List[int]] = {}
        for elevator in elevators:
            self.car_calls[elevator.id] = []
            elevator.go_to_floor(elevator.id * (len(floors) - 1) // len(elevators) + 1)

    def on_event_execute_start(
        self,
        tick: int,
        events: List[SimulationEvent],
        elevators: List[ProxyElevator],
        floors: List[ProxyFloor],
    ) -> None:
        pass

    def on_event_execute_end(
        self,
        tick: int,
        events: List[SimulationEvent],
        elevators: List[ProxyElevator],
        floors: List[ProxyFloor],
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
            snapshot["elevators"].append(
                {
                    "id": elevator.id,
                    "floor": elevator.current_floor_float,
                    "passengers": passengers,
                }
            )
        self.snapshots.append(snapshot)
        print(f"-------------Tick {tick}-------------")

    def on_passenger_call(
        self, passenger: ProxyPassenger, floor: ProxyFloor, direction: str
    ) -> None:
        print(
            f"Passenger {passenger.id}: {passenger.origin} -> {passenger.destination}"
        )

    def on_elevator_stopped(self, elevator: ProxyElevator, floor: ProxyFloor) -> None:
        print(f"Elevator {elevator.id} stopped at {floor.floor}")
        car_call = self.car_calls[elevator.id]
        if floor.floor in car_call:
            car_call.remove(floor.floor)

        next_move = self.next_move.get(elevator.id)
        if next_move != None:
            elevator.go_to_floor(next_move)
            self.next_move[elevator.id] = None

    def on_passenger_board(
        self, elevator: ProxyElevator, passenger: ProxyPassenger
    ) -> None:
        print(f"Passenger {passenger.id} boarded elevator {elevator.id}")
        destination = passenger.destination
        car_calls = self.car_calls[elevator.id]
        if destination not in car_calls:
            car_calls.append(destination)

    def on_passenger_alight(
        self, elevator: ProxyElevator, passenger: ProxyPassenger, floor: ProxyFloor
    ) -> None:
        print(f"Passenger {passenger.id} got off elevator {elevator.id}")
        pass

    def on_elevator_approaching(
        self, elevator: ProxyElevator, floor: ProxyFloor, direction: str
    ) -> None:
        """
        Decides what the elevator should do next.

        1. The elevator is about to reach top / bottom floor
        Turn around.

        2. The next floor has a hall call same as the current direction
        Go to the floor above next.

        3. The next floor has no hall call / a hall call opposite to current direction
        If there is a hall call ahead, no matter what direction:
            - if next floor is a car call, go to the floor above
            - else, IMMEDIATELY go to the floor above next

        If there is no more hall calls above, turn around.
        """
        direction = cast(PassengerDirection, direction)
        if direction == "up":
            queue = floor.up_queue
            step = 1
            end = len(self.all_floors) - 1
        else:
            queue = floor.down_queue
            step = -1
            end = 0

        if floor.floor == end:
            self.go_to_floor_next_tick(elevator, end - step)
            return

        if len(queue) > 0:
            self.go_to_floor_next_tick(elevator, floor.floor + step)
            return

        search_start = floor.floor + step
        has_hall_call_ahead = False
        for f in range(search_start, end + step, step):
            search_floor = self.all_floors[f]
            if (
                f in self.car_calls[elevator.id]
                or len(search_floor.up_queue) > 0
                or len(search_floor.down_queue) > 0
            ):
                has_hall_call_ahead = True
                break

        if has_hall_call_ahead:
            if floor.floor in self.car_calls[elevator.id]:
                self.go_to_floor_next_tick(elevator, floor.floor + step)
            else:
                elevator.go_to_floor(floor.floor + step, immediate=True)
        else:
            self.go_to_floor_next_tick(elevator, floor.floor - step)

    def go_to_floor_next_tick(self, elevator: ProxyElevator, floor: int) -> None:
        print(f"Elevator {elevator.id} bound for floor {floor} after next stop.")
        self.next_move[elevator.id] = floor

    def on_elevator_idle(self, elevator: ProxyElevator) -> None:
        pass

    def on_elevator_passing_floor(
        self, elevator: ProxyElevator, floor: ProxyFloor, direction: str
    ) -> None:
        pass


if __name__ == "__main__":
    ElevatorBusController().start()
