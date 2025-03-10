from .flaskClass import FlaskClass
from .findNearbyPlacesClass import FindNearbyPlacesClass
from database import view_locations

class AttractionClass(FlaskClass):
    def __init__(self, query, filters, user_location):
        self.query = query
        self.filters = filters
        self.user_location = user_location

    def get_data(self):
        register_info = self.get_register_info()
        return register_info
    
    def get_register_info(self):
        nearby_places_inst = FindNearbyPlacesClass()
        nearby_places_data = nearby_places_inst.get_data(self.query, self.filters, self.user_location)
        reg_info = []
        for row in nearby_places_data['places']:
            if len(row.keys()) > 1:
                t = "food"
                for types in row['type']:
                    if types == "bar":
                        t = "bar"

                long_and_lat = row['latlong'].strip(')')
                long_and_lat = long_and_lat.strip('(')
                long, lat = long_and_lat.split(',')
                print(long_and_lat)
                reg_info.append({"id": row['id'], "name": row['displayName'], "category": t, 
                                "lat": lat, "long": long, "operatingTimes": row['operating_time'], "liveWaitTimes": row['wait_times']})

        return reg_info


def main():
    inst = AttractionClass(1)
    print(inst.get_data())

if __name__ == "__main__":
    main()