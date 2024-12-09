import config
from geopy.distance import geodesic
from database.database import db

class Airport:
    def __init__(self, ident, data=None):
        self.ident = ident

        if data is None:
            # Fetch airport details from DB
            sql = "SELECT ident, name, latitude_deg, longitude_deg FROM Airport WHERE ident=%s"
            cur = db.cursor(dictionary=True)
            cur.execute(sql, (ident,))
            res = cur.fetchone()
            if res:
                self.name = res['name']
                self.latitude = float(res['latitude_deg'])
                self.longitude = float(res['longitude_deg'])
        else:
            self.name = data['name']
            self.latitude = float(data['latitude_deg'])
            self.longitude = float(data['longitude_deg'])

    def distance_to(self, target):
        coords_1 = (self.latitude, self.longitude)
        coords_2 = (target.latitude, target.longitude)
        return geodesic(coords_1, coords_2).km
