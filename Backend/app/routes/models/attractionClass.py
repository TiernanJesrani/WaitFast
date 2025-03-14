from .flaskClass import FlaskClass
from .findNearbyPlacesClass import FindNearbyPlacesClass
from .getPlaceDetails import GetPlaceDetailsClass
from database import view_locations
from datetime import datetime, timedelta

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
        now = datetime.now()
        current_day = now.strftime("%A")
        current_hour = now.hour
        for row in nearby_places_data['places']:
            photoURI = "NA"
            if 'photos' in row.keys():
                photoURI = row['photos'][0]['photoUri']

            print(photoURI)
            if len(row.keys()) > 1:
                t = "food"
                for types in row['type']:
                    if types == "bar":
                        t = "bar"

                long_and_lat = row['latlong'].strip(')')
                long_and_lat = long_and_lat.strip('(')
                long, lat = long_and_lat.split(',')
                # print(current_hour)
                if row['operating_time'] and row['operating_time'][current_day] != "Closed":
                    operating_time = row['operating_time'][current_day]
                    # print()
                    # print(operating_time)
                    open_time = operating_time['open_time']
                    close_time = operating_time['close_time']
                    if 'AM' not in open_time and 'PM' not in open_time:
                        open_time += 'AM'
                    if 'PM' not in close_time and 'AM' not in close_time:
                        close_time += 'PM'
                    left = datetime.strptime(open_time, '%I:%M%p').hour
                    right = datetime.strptime(close_time, '%I:%M%p').hour
                    if current_hour >= left:
                        wait_times = row['wait_times']
                        if wait_times is None:
                            wait_times = {
                                '0': 3,  '1': 2,  '2': 2,  '3': 2,  '4': 5,  '5': 6,  '6': 9,  '7': 15,
                                '8': 18, '9': 20, '10': 24, '11': 25, '12': 19, '13': 15, '14': 18,
                                '15': 21, '16': 17, '17': 28, '18': 30, '19': 26, '20': 22, '21': 27,
                                '22': 16, '23': 10
                            }
                            wait_times = {k: v for k, v in wait_times.items() if left <= int(k) < right}
                        else:
                            wait_times = wait_times[current_day]
                        
                        new_dict = {}
                        for hour_str, wait_time in wait_times.items():
                            time_obj = datetime.strptime(f"{hour_str}:00", "%H:%M")
                            time_str = time_obj.strftime("%I:%M%p")
                            new_dict[time_str] = wait_time
        
                        # print(left)
                        # print(right)
                        # print(wait_times)
                        # print(row["displayName"])
                        
                        reg_info.append({"id": row['id'], "name": row['displayName'], "category": t, 
                                        "lat": lat, "long": long, "operatingTimes": row['operating_time'], 
                                        "dailyWaitTimes": new_dict, "sampleCount": row["sample_count"], 
                                        "waitTimeNow": str(row["wait_time_now"]), "imageURL": photoURI })
                        print()
        return reg_info
                
    def update_place_page(self, pid):
        getPlaceInst = GetPlaceDetailsClass()
        data = getPlaceInst.retrieve_local_places([pid])
        reg_info = []
        for row in data['places']:
            if len(row.keys()) > 1:
                t = "food"
                for types in row['type']:
                    if types == "bar":
                        t = "bar"

                long_and_lat = row['latlong'].strip(')')
                long_and_lat = long_and_lat.strip('(')
                long, lat = long_and_lat.split(',')
                reg_info.append({"id": row['id'], "name": row['displayName'], "category": t, 
                                "lat": lat, "long": long, "operatingTimes": row['operating_time'], 
                                "liveWaitTimes": row['wait_times'], "sampleCount": row["sample_count"], 
                                "waitTimeNow": str(row["wait_time_now"]) })
        return reg_info


def main():
    inst = AttractionClass(1)
    print(inst.get_data())

if __name__ == "__main__":
    main()