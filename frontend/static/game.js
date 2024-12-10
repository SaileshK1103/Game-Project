let gameData = {
    playerName: '',
    gameId: null,
    currentAirport: '',
    money: 10000,
    playerRange: 5000,
    collectedElements: [],
    requiredElements: ['A', 'B', 'C', 'D'],
    win: false,
    availableAirports: [],
    contentId: 0
};

const startButton = document.getElementById('startButton');
const gameDialog = document.getElementById('gameDialog');
const storyDialog = document.getElementById('storyDialog');
const endDialog = document.getElementById('endDialog');
const buyRangeButton = document.getElementById('buyRangeButton');
const playerStatus = document.getElementById('playerStatus');
const airportInfo = document.getElementById('airportInfo');
const collectedElementsElem = document.getElementById('collectedElements');
const playerNameElem = document.getElementById('playerName');
const gameResult = document.getElementById('gameResult');
const restartButton = document.getElementById('restartButton');
const restartButton1 = document.getElementById('restartButton1');
const currentAirportElem = document.getElementById('currentAirport');
const availableAirportsElem = document.getElementById('availableAirports');
const targetAirportInput = document.getElementById('targetAirport');
const travelButton = document.getElementById('travelButton');
const foundItemsElem = document.getElementById('collectedElements');

// API URLs
const apiUrl = 'http://localhost:5003'; // Change this to your backend API URL

startButton.addEventListener('click', startGame);

function startGame() {
    const name = prompt('Enter your player name:');
    if (name) {
        console.log('name', name)
        gameData.playerName = name;
        playerNameElem.textContent = gameData.playerName;
        storyDialog.style.display = 'none';
        gameDialog.style.display = 'block';
        fetchGameStatus();
    }
}

function fetchGameStatus() {
    // Step 1: Fetch airports for the game setup
    fetch(`${apiUrl}/airports`)
    .then(response => response.json())
    .then(data => {
        if (data.length === 0) {
            alert("No airports found. Please try again later.");
            return;
        }

        // Step 2: Set the first airport as the starting point
        const startingAirport = data[0];
        gameData.currentAirport = startingAirport.ident;
        gameData.availableAirports = data;

        // Step 3: Create a new game
        fetch(`${apiUrl}/game`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                player_name: gameData.playerName,
                start_money: gameData.money,
                player_range: gameData.playerRange,
                current_airport: gameData.currentAirport,
                airports: gameData.availableAirports
            })
        })
        .then(response => {
            // 400
            if (!response.ok) {
                return response.json().then(errorData => {
                    const errorMessage = errorData.error || '';
                    alert(errorMessage);
                    location.reload();
                });
            }
            return response.json();
        })
        .then(data => {
            gameData.gameId = data.game_id;
            playerNameElem.textContent = gameData.playerName;
            currentAirportElem.textContent = gameData.currentAirport;
            storyDialog.style.display = 'none';
            gameDialog.style.display = 'block';
            updateGameStatus();
        });
    })
    .catch(error => {
        alert("Error fetching airports: " + error.message);
    });
}

// Update game status (current airport, money, available airports)
function updateGameStatus() {
    // Check if the player has collected all required elements
    console.log(gameData.requiredElements);
    console.log(gameData.collectedElements);
    if (gameData.requiredElements.every(elem => gameData.collectedElements.includes(elem))) {
        gameData.win = true;
        endGame();
        return;
    }else if (gameData.money == 0 && gameData.playerRange == 0) {
        gameData.win = false;
        endGame();
        return;
    }

    playerStatus.textContent = `Money: $${gameData.money}, Range: ${gameData.playerRange} km`;
    currentAirportElem.textContent = gameData.currentAirport;

    const airportsJson = JSON.stringify(gameData.availableAirports);

    fetch(`${apiUrl}/airports_in_range`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            icao: gameData.currentAirport,
            range: gameData.playerRange,
            airports: gameData.availableAirports
        })
    })
    .then(response => response.json())
    .then(data => {
        // Display available airports
        availableAirportsElem.innerHTML = '';

        if (data.length == 0 && gameData.money == 0) {
            gameData.win = false;
            endGame();
            return;
        }

        data.forEach(item => {
            const listItem = document.createElement('li');
            listItem.textContent = `${item.name}, ICAO: ${item.ident}, Distance: ${item.distance}km`;
            availableAirportsElem.appendChild(listItem);
        });

        // Show collected elements
        foundItemsElem.innerHTML = gameData.collectedElements.map(item => `${item}`).join(',');
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Travel to another airport
travelButton.addEventListener('click', () => {
    const targetAirport = targetAirportInput.value.trim().toUpperCase();
    if (targetAirport) {
        moveToAirport(targetAirport);
    } else {
        alert("Please enter a valid airport ICAO code.");
    }
});

// Move to the next airport and check found items
function moveToAirport(targetAirport) {
    const availableAirports = gameData.availableAirports;

    if (!availableAirports.map(a => a.ident).includes(targetAirport)) {
        alert("The selected airport is not within the available airports you can travel to.");
        return;
    }

    // Calculate the distance between the current and target airports
    fetch(`${apiUrl}/distance?current=${gameData.currentAirport}&target=${targetAirport}`)
    .then(response => response.json())
    .then(data => {
        const selectedDistance = data.distance_km;
        if (selectedDistance > gameData.playerRange) {
            alert("You don't have enough range to fly to this destination.");
            return;
        }

        // Update game state: reduce player range and move to the target airport
        gameData.playerRange -= selectedDistance;
        gameData.currentAirport = targetAirport;

        updateGameInfo(targetAirport);
        getContents(targetAirport);

        // updateGameStatus();
    });
}

function updateGameInfo(targetAirport){
    fetch(`${apiUrl}/game/${gameData.gameId}/update`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            icao: targetAirport,
            player_range: gameData.playerRange,
            money: gameData.money
        })
    })
    .then(response => response.json())
    .then(data => {
        gameData.currentAirport = targetAirport;
    })
    .catch(error => {
        console.error('updateGameInfo:', error);
    });
}

function getContents(targetAirport){
    fetch(`${apiUrl}/game/${gameData.gameId}/get_port_contents`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            icao: targetAirport,
            collected_elements: gameData.collectedElements
        })
    })
    .then(response => response.json())
    .then(data => {
        gameData.collectedElements = data.collected_elements; // Update collected elements
        gameData.contentId = data.content_id; // Update money
        airportInfo.textContent = data.message;
        console.log(data.message);

        if(data.element_type == 'lucky_box'){
            if(confirm("Do you want to open the lucky box for $100?")){
                openLuckyBox();
            }else{
                updateGameStatus();
            }
        }else{
            updateGameStatus();
        }
    })
    .catch(error => {
        console.error('getContents:', error);
    });
}

function openLuckyBox(){
    fetch(`${apiUrl}/game/${gameData.gameId}/open_lucky_box`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            content_id: gameData.contentId,
            collected_elements: gameData.collectedElements,
            money: gameData.money
        })
    })
    .then(response => {
        // 400
        if (!response.ok) {
            return response.json().then(errorData => {
                const errorMessage = errorData.message || '';
                alert(errorMessage);
            });
        }
        return response.json();
    })
    .then(data => {
        gameData.collectedElements = data.collected_elements; // Update collected elements
        gameData.money = data.money; // Update money

        airportInfo.textContent = gameData.message;

        updateGameStatus();
    })
    .catch(error => {
        console.error('open_lucky_box:', error);
    });
}

// Game over and win/loss logic
function endGame() {
    gameDialog.style.display = 'none';
    endDialog.style.display = 'block';

    if (gameData.win) {
        gameResult.textContent = `You won! Congratulations! You collected all the required elements: ${gameData.collectedElements.join(', ')}`;
    } else {
        gameResult.textContent = `You lost! Unfortunately, you didn't collect all the required elements.`;
    }

    restartButton.addEventListener('click', () => {
        location.reload(); // Reload to restart the game
    });
}

// Buy extra range
buyRangeButton.addEventListener('click', () => {
    const rangeToBuy = prompt("How much range would you like to buy? (in km)");
    if (rangeToBuy && rangeToBuy > 0) {
        if (rangeToBuy % 100 != 0){
            alert("Please enter a valid amount (must be a positive multiple of 100).")
        }else{
            const cost = (rangeToBuy / 200) * 100; // Example cost calculation
            if (cost <= gameData.money) {
                gameData.playerRange += parseInt(rangeToBuy);
                gameData.money -= cost;
                updateGameInfo(gameData.currentAirport);

                updateGameStatus();
            } else {
                alert("You don't have enough money to buy this range.");
            }
        }
    } else {
        alert("Please enter a valid range.");
    }
});

// Restart the game
restartButton.addEventListener('click', () => {
    location.reload(); // Reload the page to restart the game
});
restartButton1.addEventListener('click', () => {
    location.reload(); // Reload the page to restart the game
});
