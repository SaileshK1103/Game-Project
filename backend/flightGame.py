from backend import config
from database.database import db
from airport import Airport
import random


class FlightGame:
    def __init__(self, player_name, start_money=config.start_money, player_range=config.player_range):
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
                 FROM Airport WHERE continent = 'EU' AND type='large_airport' 
                 ORDER BY RAND() LIMIT 7;"""
        cur = db.cursor(dictionary=True)
        cur.execute(sql)
        return cur.fetchall()

    def create_game(self):
        # Insert game into DB
        sql = "INSERT INTO game (money, player_range, location, screen_name) VALUES (%s, %s, %s, %s)"
        cur = db.cursor(dictionary=True)
        cur.execute(sql, (self.money, self.player_range, self.current_airport.ident, self.player_name))

        return cur.lastrowid

    def assign_elements(self):
        # Fetch all elements
        sql = "SELECT id, name FROM element"
        cur = db.cursor(dictionary=True)
        cur.execute(sql)
        elements = cur.fetchall()

        element_list = [elem['id'] for elem in elements]
        random.shuffle(element_list)
        self.assigned_airports = set()
        self.assigned_countries = set()

        for elem_id in element_list:
            available_ports = [
                port for port in self.airports
                if port['ident'] not in self.assigned_airports and port['iso_country'] not in self.assigned_countries
            ]
            if not available_ports:
                raise Exception("Not enough unique airports or countries.")
            selected_port = random.choice(available_ports)
            self.assigned_airports.add(selected_port['ident'])
            self.assigned_countries.add(selected_port['iso_country'])

            # Insert into port_contents
            sql = "INSERT INTO port_contents (game_id, airport, content_type, content_value) VALUES (%s, %s, %s, %s)"
            element_name = self.get_element_name_by_id(elem_id)
            cur.execute(sql, (self.game_id, selected_port['ident'], 'element', element_name))
        # assign a lucky box to one airport
        available_ports = [
            port for port in self.airports
            if port['ident'] not in self.assigned_airports and port['iso_country'] not in self.assigned_countries
        ]
        if available_ports:
            selected_port = random.choice(available_ports)
            self.assigned_airports.add(selected_port['ident'])
            if available_ports:
                selected_port = random.choice(available_ports)
                self.assigned_airports.add(selected_port['ident'])
                lucky_box_element = random.choice([None] + element_list)  # Element or empty box
                sql = "INSERT INTO port_contents (game_id, airport, content_type, content_value) VALUES (%s, %s, %s, %s)"
                cur.execute(sql, (self.game_id, selected_port['ident'], 'lucky_box', lucky_box_element))
    @staticmethod
    def get_element_name_by_id(element_id):
        # Fetch element name by ID
        sql = "SELECT name FROM element WHERE id = %s"
        cur = db.cursor(dictionary=True)
        cur.execute(sql, (element_id,))
        result = cur.fetchone()
        return result['name'] if result else None

    def airports_in_range(self):
        # Get airports within range
        in_range = []
        for port in self.airports:
            airport_obj = Airport(port['ident'], port)
            distance = self.current_airport.distance_to(airport_obj)
            if distance <= self.player_range and distance != 0:
                in_range.append({
                    "ident": port['ident'],
                    "name": port['name'],
                    "iso_country": port['iso_country'],
                    "latitude_deg": port['latitude_deg'],
                    "longitude_deg": port['longitude_deg'],
                    "distance":distance
                })
        return in_range

    def update_location(self, destination_ident):
        destination = Airport(destination_ident)
        distance = self.current_airport.distance_to(destination)
        if distance > self.player_range:
            raise Exception("Insufficient range to reach destination.")

        self.player_range -= distance
        self.current_airport = destination

        # Update game location in DB
        sql = "UPDATE game SET location = %s, player_range = %s WHERE id = %s"
        cur = db.cursor(dictionary=True)
        cur.execute(sql, (destination.ident, self.player_range, self.game_id))

    def collect_content(self):
        # Check for content at the current airport
        sql = """SELECT id, content_type, content_value 
                 FROM port_contents WHERE game_id = %s AND airport = %s AND found = 0"""
        cur = db.cursor(dictionary=True)
        cur.execute(sql, (self.game_id, self.current_airport.ident))
        contents = cur.fetchall()

        for content in contents:
            if content['content_type'] == 'element':
                self.collected_elements.append(content['content_value'])
            elif content['content_type'] == 'lucky_box':
                print(f"A lucky box is available at {self.current_airport}.")
                open_box = input("Do you want to open the lucky box for $100? (Y/N): ").strip().upper()

                if open_box == 'Y':
                    if self.money >= 100:
                        self.money -= 100
                        print(f"You opened the lucky box for $100. You have €{self.money} left.")

                        # Handle potential empty lucky boxes
                        if content['content_value']:
                            print(f"The lucky box contains Element {content['content_value']}!")
                            if content['content_value'] not in self.collected_elements:
                                self.collected_elements.append(content['content_value'])
                            else:
                                print("You already have this element.")
                        else:
                            print("Unfortunately, this lucky box was empty.")

                        # Mark the lucky box as found
                        self.mark_content_found(content['id'])
                    else:
                        print("You don't have enough money to open the lucky box.")
                else:
                    print("You chose not to open the lucky box.")
            self.mark_content_found(content['id'])

            # Mark content as found
            sql = "UPDATE port_contents SET found = 1 WHERE id = %s"
            cur.execute(sql, (content['id'],))

    def mark_content_found(self, content_id):
        sql = "UPDATE game SET found = 1 WHERE id = %s"
        cur = db.cursor(dictionary=True)
        cur.execute(sql, (content_id,))

    def buy_extra_range(self,range_to_buy):
        # Calculate cost (based on range_to_buy)
        cost = (range_to_buy // 200) * 100

        if cost > self.money:
            raise Exception("Insufficient funds.")

        # Deduct the cost from money and add range
        self.money -= cost
        self.player_range += range_to_buy
        print(f"Bought extra {range_to_buy} km range.")
    def is_game_won(self):
        #required_elements = ['A', 'B', 'C', 'D']
        # Fetch required elements for the game from the database
        sql = "SELECT element_name FROM game_requirements WHERE game_id = %s"
        cur = db.cursor(dictionary=True)
        cur.execute(sql, (self.game_id,))
        required_elements = [row['element_name'] for row in cur.fetchall()]
        return all(elem in self.collected_elements for elem in required_elements);


