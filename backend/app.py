from flask import Flask, jsonify, request
from flightGame import FlightGame
from airport import Airport
from database.database import db

# Connect to the database
db.connect()

if __name__ == "__main__":
    player_name = input("Enter your name: ")
    game = FlightGame(player_name)
    game.assign_elements()

    while True:
        print(f"You are at {game.current_airport.name}. Money: €{game.money}, Range: {game.player_range} km")

        in_range_airports = game.airports_in_range()
        if not in_range_airports:
            print("No airports in range. You need to buy more range or the game is over!")

            while True:
                buy_range = input("Do you want to buy more range? (Y/N): ").strip().upper()
                if buy_range == 'Y':
                    game.buy_extra_range()
                    break
                elif buy_range == 'N':
                    print("Game Over! No range left to travel.")
                    exit()
                else:
                    print("Please enter a valid response (Y/N).")

            in_range_airports = game.airports_in_range()
            if not in_range_airports:
                print("Still no airports in range. Game Over!")
                break

        print("Airports in range:")
        for port in in_range_airports:
            print(f"{port['name']} ({port['ident']}) ({round(game.current_airport.distance_to(Airport(port['ident'], port)))} km)")

        dest_ident = input("\nEnter the ICAO of your destination: ").strip()

        try:
            game.update_location(dest_ident)
            print("Checking for content at the airport...")
            game.collect_content()

            print("You have collected the following elements:")
            for element in game.collected_elements:
                print(f"- Element {element}")

            if game.is_game_won():
                print("Congratulations! You collected all elements and won the game!")
                break
        except Exception as e:
            print(f"Error: {e}")
