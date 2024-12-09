from flask import Flask, jsonify, request
from flightGame import FlightGame
from airport import Airport
from database.database import db
db.connect()

if __name__ == "__main__":
    player_name = input("Enter your name: ")
    game = FlightGame(player_name)
    game.assign_elements()

    while True:
        print(f"You are at {game.current_airport.name}. Money: {game.money}, Range: {game.player_range}")
        in_range_airports = game.airports_in_range()
        if not in_range_airports:
            print("No airports in range. Game Over!")
            break

        print("Airports in range:")
        for port in in_range_airports:
            print(f"{port['name']} ({port['ident']})")

        dest_ident = input("Enter the ICAO of your destination: ").strip()
        try:
            game.update_location(dest_ident)
            game.collect_content()
            if game.is_game_won():
                print("You collected all elements! You win!")
                break
        except Exception as e:
            print(f"Error: {e}")
