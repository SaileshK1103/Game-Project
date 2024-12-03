import random
import config
from geopy.distance import geodesic
from database.database import connection

class Airport:
    def __init__(self, ident, data=None):
        self.ident = ident
        if data is None:
            # Fetch airport details from DB
            sql = "SELECT ident, name, latitude_deg, longitude_deg FROM Airport WHERE ident=%s"
            cursor = connection.cursor(dictionary=True)
            cursor.execute(sql, (ident,))
            result = cursor.fetchone()
            if result:
                self.name = result['name']
                self.latitude = float(result['latitude_deg'])
                self.longitude = float(result['longitude_deg'])
        else:
            self.name = data['name']
            self.latitude = float(data['latitude_deg'])
            self.longitude = float(data['longitude_deg'])

    # Calculate distance between two airports
    def calculate_distance(self, target):
        coords_1 = (self.latitude, self.longitude)
        coords_2 = (target.latitude, target.longitude)
        return geodesic(coords_1, coords_2).km