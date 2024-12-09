import config
from geopy.distance import geodesic
from database.database import Database, db

class Airport:
    def __init__(self, ident):
        self.ident = ident

        sql = "SELECT ident, name, latitude_deg, longitude_deg FROM Airport WHERE ident=%s"
        cur = db.cursor(dictionary=True)
        cur.execute(sql, (ident,))
        result = cur.fetchone()
        if result:
                self.name = result[1]
                self.latitude = float(result[2])
                self.longitude = float(result[3])


    # Calculate distance between two airports
    def calculate_distance(self, target):
        coords_1 = (self.latitude, self.longitude)
        coords_2 = (target.latitude, target.longitude)
        return geodesic(coords_1, coords_2).km
