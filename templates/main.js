const floorHeight = 45; // from CSS
const elevatorWidth = 360; // from CSS
const elevatorElements = [];
const urlBase = '/proxy';
let elevator_position = [];
let tick = 0;
const update_interval = 20;

fetch(`${urlBase}?type=state`)
    .then(function (response) {
        return response.json();
    })
    .then(function (data) {
        setupScene(data);
        render(data);
        setTimeout(callback, update_interval);
    });

function callback() {
  fetch(`${urlBase}?type=step&tick=${tick}`).then(function () {
        fetch(`${urlBase}?type=state`)
            .then(function (response) {
                return response.json();
            })
            .then(function (data) {
                console.log(data);
                render(data);
                setTimeout(callback, update_interval);
            });
    });
}

function setupScene(obj) {
    const floorsContainer = document.querySelector('#floors-container');
    const elevatorBuilding = document.querySelector('#elevator-building');
    const numFloors = obj.floors.length;
    const numElevators = obj.elevators.length;

    elevator_position = obj.elevators.map(() => 0);

    floorsContainer.innerHTML = '';
    for (let i = numFloors - 1; i >= 0; i--) {
        const floor = document.createElement('div');
        floor.className = 'floor';
        floor.id = `floor-${i}`;
        floor.innerHTML = `<span class="floor-label">${i + 1}</span><div class="waiting-passengers"></div>`;
        floorsContainer.appendChild(floor);
    }

    elevatorBuilding.innerHTML = '';
    elevatorElements.length = 0; // Clear the array
    elevatorBuilding.style.height = `${numFloors * floorHeight}px`;
    elevatorBuilding.style.width = `${numElevators * elevatorWidth}px`;

    for (let i = 0; i < numElevators; i++) {
        const shaft = document.createElement('div');
        shaft.className = 'elevator-shaft';
        shaft.style.left = `${i * elevatorWidth}px`;

        const elevator = document.createElement('div');
        elevator.className = `elevator elevator-${i % 3}`; // Cycle through 3 colors
        elevator.id = `elevator-${i}`;
        elevator.innerHTML = `<div class="elevator-passengers" id="elevator-passengers-${i}"></div>`;

        shaft.appendChild(elevator);
        elevatorBuilding.appendChild(shaft);
        elevatorElements.push(elevator); // Store for easy access
    }
}

function render(data) {
    if (data.tick < tick) {
        return;
    }
    tick += 1;
    function createPassengerElement(id) {
        let passenger = data.passengers[id];
        const p = document.createElement('div');
        p.className = 'passenger';
        const origin = passenger.origin;
        const destination = passenger.destination;
        p.innerHTML = `<span class="id">${passenger.id}</span><span class="dest">➔${destination}</span>`;
        p.title = `Passenger ${passenger.id}\nOrigin: ${origin}\nDestination: ${destination}`;
        return p;
    }

    data.elevators.forEach((elevatorData, i) => {
        const elevatorEl = elevatorElements[i];
        if (!elevatorEl) return;

        if (elevatorData.run_status == 'stopped') {
            elevator_position[i] = elevatorData.position.current_floor;
        } else {
            let delta = elevatorData.last_tick_direction == 'down' ? -1 : 1;
            if (elevatorData.run_status == 'constant_speed') {
                delta *= 0.2;
            } else {
                delta *= 0.1;
            }
            elevator_position[i] += delta;
        }

        elevatorEl.style.bottom = `${elevator_position[i] * floorHeight}px`;

        const passengersContainer = elevatorEl.querySelector('.elevator-passengers');
        passengersContainer.innerHTML = '';
        elevatorData.passengers.forEach((p) => {
            passengersContainer.appendChild(createPassengerElement(p));
        });
    });

    document.querySelectorAll('.waiting-passengers').forEach((container) => {
        container.innerHTML = '';
    });

    data.floors.forEach((floorObj, floorIndex) => {
        const floorElement = document.querySelector(`#floor-${floorIndex}`);
        floorPassengers = floorObj.up_queue.concat(floorObj.down_queue);
        const waitingContainer = floorElement.querySelector('.waiting-passengers');
        floorPassengers.forEach((p) => {
            waitingContainer.appendChild(createPassengerElement(p));
        });
    });
}
