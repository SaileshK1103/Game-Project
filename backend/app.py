from flask import Flask, jsonify, request
from flask_cors import CORS
from backend.database.database import db
from backend.flightGame import FlightGame

app = Flask(__name__)
cors = CORS(app)
active_games = {}

@app.route('/start_game', methods=['POST'])
def start_game():
    """
        Start a new game.
        Request Body: { "player_name": "PlayerName" }
        Response: { "game_id": int, "current_airport": str, "money": int, "player_range": float }
        """
    data = request.get_json()
    player_name = data.get('player_name')
    if not player_name:
        return jsonify({"error": "Player name is required"}), 400

    #Initialize the game
    game = FlightGame(player_name)
    game.assign_elements()
    active_games[game.game_id] = game

    return jsonify(({
        "game_id": game.game_id,
        "current_airport": game.current_airport.name,
        "money": game.money,
        "player_range": game.player_range
    }))

@app.route('/airport_in_range', methods=['GET'])
def airport_in_range():
    """
        Get a list of airports within range.
        Query Params: game_id
        Response: { "airports": [{ "ident": str, "name": str }] }
        """
    game_id = request.args.get('game_id')
    if not game_id or int(game_id) not in active_games:
        return jsonify({"error": "Invalid or missing game_id"}), 400

    game = active_games[int(game_id)]
    airports = game.airports_in_range()

    return jsonify({"airports": airports})

@app.route('/fly_to', methods=['POST'])
def fly_to():
    """
        Fly to a specific destination.
        Request Body: { "game_id": int, "destination_ident": str }
        Response: { "success": bool, "current_airport": str, "player_range": float, "money": int }
        """
    data = request.get_json()
    game_id = data.get('game_id')
    destination_ident = data.get('destination_ident')
    if not game_id or int(game_id) not in active_games:
        return jsonify({"error": "Invalid or missing game_id"}), 400
    if not destination_ident:
        return jsonify({"error": "Destination ident is required"}), 400
    game = active_games[int(game_id)]

    try:
        game.update_location(destination_ident)
        return jsonify({
            "success": True,
            "current_airport": game.current_airport.name,
            "player_range": game.player_range,
            "money": game.money
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/collect_content', methods=['POST'])
def collect_content():
    """
        Collect content at the current airport.
        Request Body: { "game_id": int }
        Response: { "collected_elements": list }
        """
    data = request.get_json()
    game_id = data.get('game_id')
    if not game_id or int(game_id) not in active_games:
        return jsonify({"error": "Invalid or missing game_id"}), 400
    game = active_games[int(game_id)]
    game.collect_content()
    return jsonify({"collected_elements": game.collected_elements})

@app.route('/check_game_status', methods=['GET'])
def check_game_status():
    """
        Check if the game is won.
        Query Params: game_id
        Response: { "game_won": bool, "collected_elements": list }
        """
    game_id = request.args.get('game_id')
    if not game_id or int(game_id) not in active_games:
        return jsonify({"error": "Invalid or missing game_id"}), 400
    game = active_games[int(game_id)]
    game_won = game.is_game_won()

    return jsonify({
        "game_won": game_won,
        "collected_elements": game.collected_elements
    })

@app.route('/end_game', methods=['POST'])
def end_game():
    """
        End the game and clean up resources.
        Request Body: { "game_id": int }
        Response: { "success": bool }
        """
    data = request.get_json()
    game_id = data.get('game_id')
    if not game_id or int(game_id) not in active_games:
        return jsonify({"error": "Invalid or missing game_id"}), 400
    del active_games[int(game_id)]
    return jsonify({"success": True})

@app.route('/buy_extra_range', methods=['POST'])
def buy_extra_range():
    """
            Buy extra range.
            Request Body: { "game_id": int, "range_to_buy": int }
            Response: { "success": bool, "player_range": float, "money": int }
            """
    data = request.get_json()
    game_id = data.get('game_id')
    range_to_buy = data.get('range_to_buy')
    if not game_id or int(game_id) not in active_games:
        return jsonify({"error": "Invalid or missing game_id"}), 400
    game = active_games[int(game_id)]
    try:
        game.buy_extra_range(range_to_buy)
        return jsonify({
            "success": True,
            "player_range": game.player_range,
            "money": game.money
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    db.connect()
    app.run(debug=True, host='127.0.0.1', port=5000)