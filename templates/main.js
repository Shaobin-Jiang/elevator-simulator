fetch('/list-traffic')
    .then((response) => response.json())
    .then(function (traffics) {
        let select = document.querySelector('.select-traffic select');
        for (let traffic of traffics) {
            let option = document.createElement('option');
            option.value = traffic;
            option.innerText = traffic;
            select.appendChild(option);
        }

        let simBtn = document.querySelector('#simulation-btn');
        simBtn.addEventListener('click', function () {
            simBtn.disabled = true;
            document.querySelector('#animate-btn').disabled = true;
            simulate(select.value);
        });
    });

function simulate(traffic) {
    fetch(`/simulation?traffic=${traffic}`)
        .then(function (response) {
            return response.json();
        })
        .then(function (data) {
            document.querySelector('#animate-btn').disabled = false;
            document.querySelector('#simulation-btn').disabled = false;

            let description = document.querySelector('.description')
            let html = '<h2>Description</h2>';
            for (let item in data.traffic) {
                html += `<p><b>${item}</b>: ${data.traffic[item]}</p>`
            }
            html += '<br><h2>Metrics</h2>';
            for (let item in data.metrics) {
                html += `<p><b>${item}</b>: ${data.metrics[item]}</p>`
            }
            description.innerHTML = html;
            description.style.display = "block";

            start_simulation(data.snapshots);
        });

    function start_simulation(ticks) {
        const floorsContainer = document.getElementById('floors-container');
        const elevatorBuilding = document.getElementById('elevator-building');

        const animateBtn = document.getElementById('animate-btn');
        const tickCounter = document.getElementById('tick-counter');
        const totalTicksSpan = document.getElementById('total-ticks');
        const tickSlider = document.getElementById('tick-slider');

        let currentTick = 0;
        let animationInterval = null;
        const numFloors = ticks[0].floors.length;
        const numElevators = ticks[0].elevators.length;
        const floorHeight = 120; // from CSS
        const elevatorWidth = 180; // from CSS

        const elevatorElements = [];

        function createPassengerElement(passenger) {
            const p = document.createElement('div');
            p.className = 'passenger';
            const origin = passenger.origin ?? passenger.o;
            const destination = passenger.destination ?? passenger.d;
            p.innerHTML = `<span class="id">${passenger.id}</span><span class="dest">➔${destination}</span>`;
            p.title = `Passenger ${passenger.id}\nOrigin: ${origin}\nDestination: ${destination}`;
            return p;
        }

        function renderTick(tickIndex) {
            const tickData = ticks[tickIndex];
            if (!tickData) return;

            // 1. Update All Elevator Positions and Passengers
            tickData.elevators.forEach((elevatorData, i) => {
                const elevatorEl = elevatorElements[i];
                if (!elevatorEl) return;

                elevatorEl.style.bottom = `${elevatorData.floor * floorHeight}px`;

                const passengersContainer = elevatorEl.querySelector('.elevator-passengers');
                passengersContainer.innerHTML = '';
                elevatorData.passengers.forEach((p) => {
                    passengersContainer.appendChild(createPassengerElement(p));
                });
            });

            // 2. Update Waiting Passengers on Floors
            document.querySelectorAll('.waiting-passengers').forEach((container) => {
                container.innerHTML = '';
            });

            tickData.floors.forEach((floorPassengers, floorIndex) => {
                const floorElement = document.getElementById(`floor-${floorIndex}`);
                const waitingContainer = floorElement.querySelector('.waiting-passengers');
                floorPassengers.forEach((p) => {
                    waitingContainer.appendChild(createPassengerElement(p));
                });
            });

            // 3. Update UI Controls
            currentTick = tickIndex;
            tickCounter.textContent = currentTick + 1;
            tickSlider.value = currentTick;
        }

        function setupScene() {
            // 1. Create Floors
            floorsContainer.innerHTML = '';
            for (let i = numFloors - 1; i >= 0; i--) {
                const floor = document.createElement('div');
                floor.className = 'floor';
                floor.id = `floor-${i}`;
                floor.innerHTML = `
                        <span class="floor-label">Floor ${i}</span>
                        <div class="waiting-passengers"></div>
                    `;
                floorsContainer.appendChild(floor);
            }

            // 2. Create Elevator Shafts and Elevators
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

            // 3. Setup controls
            totalTicksSpan.textContent = ticks.length;
            tickSlider.max = ticks.length - 1;
        }

        function startAnimation() {
            if (animationInterval) return;
            animateBtn.textContent = 'Pause';
            animateBtn.style.backgroundColor = '#ffc107';
            animationInterval = setInterval(() => {
                if (currentTick < ticks.length - 1) {
                    renderTick(currentTick + 1);
                } else {
                    stopAnimation();
                }
            }, 300);
        }

        function stopAnimation() {
            clearInterval(animationInterval);
            animationInterval = null;
            animateBtn.textContent = 'Animate';
            animateBtn.style.backgroundColor = '#28a745';
        }

        animateBtn.addEventListener('click', () => {
            if (animationInterval) {
                stopAnimation();
            } else {
                if (currentTick >= ticks.length - 1) renderTick(0);
                startAnimation();
            }
        });

        tickSlider.addEventListener('input', (e) => {
            stopAnimation();
            renderTick(parseInt(e.target.value, 10));
        });

        setupScene();
        renderTick(0);
    }
}
