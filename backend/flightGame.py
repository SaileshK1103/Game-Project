import config
from random import random, shuffle, choice
from geopy.distance import geodesic
from airport import Airport
from database.database import db
db.connect()
class FlightGame:
    def __init__(self, player_name, start_money=10000, player_range=5000):
        self.player_name = player_name
        self.money = start_money
        self.player_range = player_range
        self.collected_elements = []
        self.airports = self.get_airports()
        self.start_airport = Airport(self.airports[0]['ident'], self.airports[0])
        self.current_airport = self.start_airport
        self.game_id = self.create_game()
        self.assigned_airports = {self.start_airport.ident}
        self.assigned_countries = {self.start_airport.ident}

    def get_airports(self):
        # Fetch airports from DB
        sql = """SELECT iso_country, ident, name, latitude_deg, longitude_deg 
                 FROM airport WHERE continent = 'EU' AND type='large_airport' 
                 ORDER BY RAND() LIMIT 7;"""
        cur = db.cursor(dictionary=True)
        cur.execute(sql)
        return cur.fetchall()

    def create_game(self):
        # Insert new game
        sql = "INSERT INTO game (money, player_range, location, screen_name) VALUES (%s, %s, %s, %s)"
        cur = db.cursor(dictionary=True)
        cur.execute(sql, (self.money, self.player_range, self.current_airport.ident, self.player_name))
        db.commit()
        return cur.lastrowid

    def get_element_name_by_id(element_id):
        # Fetch element name by ID
        sql = "SELECT name FROM element WHERE id = %s"
        cur = db.cursor(dictionary=True)
        cur.execute(sql, (element_id,))
        result = cur.fetchone()
        return result['name'] if result else None

    def assign_elements(self):
        # get all elements and their quantities
        sql = "SELECT id, name FROM element"
        cur = db.cursor(dictionary=True)
        cur.execute(sql)
        elements = cur.fetchall()

        element_list = [elem['id'] for elem in elements]
        shuffle(element_list)

        for elem_id in element_list:
            # Filter airports that are not yet assigned and in unique countries
            available_ports = [
                port for port in self.airports
                if port['ident'] not in self.assigned_airports and port['iso_country'] not in self.assigned_countries
            ]
            if not available_ports:
                raise Exception("Not enough unique countries and airports to assign all elements.")
            selected_port = choice(available_ports)
            self.assigned_airports.add(selected_port['ident'])
            self.assigned_countries.add(selected_port['iso_country'])

            # Insert into port_contents
            sql = "INSERT INTO port_contents (game_id, airport, content_type, content_value) VALUES (%s, %s, %s, %s)"
            element_name = self.get_element_name_by_id(elem_id)
            cur.execute(sql, (self.game_id, selected_port['ident'], 'element', element_name))

    def airports_in_range(self):
        in_range = []
        for port in self.airports:
            airport_target = Airport(port['ident'], port)
            distance = self.current_airport.calculate_distance(airport_target)
            if distance <= self.player_range and distance != 0:
                in_range.append(port)
        return in_range

    def update_location(self):
        sql = "UPDATE game SET location = %s, player_range = %s WHERE id = %s"
        cur = db.cursor(dictionary=True)
        cur.execute(sql, self.player_range, self.money, self.game_id))

    def mark_content_found(content_id):
        sql = "UPDATE port_contents SET found = 1 WHERE id = %s"
        cur = db.cursor(dictionary=True)
        cur.execute(sql, (content_id,))
        db.commit()