from geopy.distance import geodesic
from backend.database.database import db


class Airport:

    def __init__(self, ident, data=None):
        self.ident = ident

        if data is None:
            # Fetch airport details from DB
            sql = "SELECT ident, name, latitude_deg, longitude_deg FROM Airport WHERE ident=%s"
            cur = db.cursor(dictionary=True)
            cur.execute(sql, (ident,))
            result = cur.fetchone()
            if result:
                self.name = result['name']
                self.latitude = float(result['latitude_deg'])
                self.longitude = float(result['longitude_deg'])
        else:
            self.name = data['name']
            self.latitude = float(data['latitude_deg'])
            self.longitude = float(data['longitude_deg'])

    # Calculate distance between two airports
    def distance_to(self, target):
        coords_1 = (self.latitude, self.longitude)
        coords_2 = (target.latitude, target.longitude)
        return geodesic(coords_1, coords_2).km
