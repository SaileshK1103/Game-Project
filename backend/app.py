from flask import Flask, jsonify, request
from flightGame import FlightGame
from airport import Airport
from database.database import db
db.connect()

if __name__ == "__main__":
    player_name = input("Enter your name: ")
