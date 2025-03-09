import psycopg2
import os
import requests
import sys
import json
from .flaskClass import FlaskClass
import re

current_dir = os.path.dirname(__file__)
secret_loc = os.path.abspath(os.path.join(current_dir, '..', '..', '..', 'database'))
sys.path.insert(0, secret_loc)
from secret import get_secret

class GetPlaceDetailsClass(FlaskClass):
    def __init__(self):
        return
    

    def get_date(self):
        return "hello"

    def get_db_connection(self):
        user, password = get_secret()
        connection = psycopg2.connect(
            dbname = "",
            user=user,
            password=password,
            host = "wait-fast.cwlesuqwe9fs.us-east-1.rds.amazonaws.com",  # or the IP address of your database server
            port = "5432"            
        )
        return connection, connection.cursor()
    
    # Function to retrieve local place details for a list of place_ids
    def retrieve_place_page(self, place_ids):
        # Build a dictionary mapping for places already in the DB
        local_places = {}
        if not place_ids:
            return local_places
        
        
        connection, cursor = self.get_db_connection()
        try: 
            format_ids = tuple(place_ids) # Ensure the list is converted to a tuple
            query = f"""
                SELECT 
                    l.place_id, 
                    l.displayName, 
                    l.delivery,
                    l.address, 
                    l.latlong, 
                    l.type, 
                    l.photos, 
                    l.websiteURI,
                    l.operating_time,
                    COALESCE(wt.wait_times_data, '[]'::jsonb) AS wait_times  -- Select the wait_times JSONB field
                FROM locations l
                LEFT JOIN wait_times wt ON wt.location_id = l.id
                WHERE l.place_id IN %s
            """
            cursor.execute(query, (format_ids, ))
            results = cursor.fetchall()

            # For each row from the result, populate the local_places dictionary
            for row in results:
                place_id = row[0]
                local_places[place_id] = {
                    "id": row[0],
                    "displayName": row[1],
                    "delivery": row[2],
                    "address": row[3],
                    "latlong": row[4],
                    "type": row[5],
                    "photos": row[6],
                    "websiteURI": row[7],
                    "operating_time": row[8], # Aggregated JSON array for all opening hours
                    "wait_times": row[9] # Aggregated JSON array for all wait_times
                }
            return local_places

        except Exception as e:
            print("Error in retrieve_local_places:", e)
            return local_places
        finally:
            cursor.close()
            connection.close()

    
    # Function to retrieve local place details for a list of place_ids
    def retrieve_local_places(self, place_ids):
        # Build a dictionary mapping for places already in the DB
        local_places = {}
        if not place_ids:
            return local_places
        
        
        connection, cursor = self.get_db_connection()
        try: 
            format_ids = tuple(place_ids) # Ensure the list is converted to a tuple
            query = f"""
                SELECT 
                    l.place_id, 
                    l.displayName, 
                    l.delivery,
                    l.address, 
                    l.latlong, 
                    l.type, 
                    l.photos, 
                    l.websiteURI,
                    l.operating_time,
                    wt_td.live_wait_time
                FROM locations l
                LEFT JOIN wait_times_today wt_td 
                ON wt_td.location_id = l.id
                WHERE l.place_id IN %s
                ORDER BY wt_td.day DESC, wt_td.hour DESC
                LIMIT 1;             
            """

            cursor.execute(query, (format_ids, ))
            results = cursor.fetchall()

            # For each row from the result, populate the local_places dictionary
            for row in results:
                place_id = row[0]
                local_places[place_id] = {
                    "place_id": row[0],
                    "displayName": row[1],
                    "delivery": row[2],
                    "address": row[3],
                    "latlong": row[4],
                    "type": row[5],
                    "photos": row[6],
                    "websiteURI": row[7],
                    "operating_time": row[8], # Aggregated JSON array for all opening hours
                    "wait_times": row[9] # Aggregated JSON array for all wait_times
                }
            return local_places

        except Exception as e:
            print("Error in retrieve_local_places:", e)
            return local_places
        finally:
            cursor.close()
            connection.close()

    """
    Calls the Google Places API to get complete details for a given place_id.
    
    Args:
        place_id (str): The place identifier to use in the API query.
    
    Returns:
        dict or None: JSON response (a dict) for the first place returned by the API, 
                      or None if an error occurs or no data is returned.
    """
    
    def fetch_api_place_details(self, place_id):

        """
        Retrieves detailed information for a specific place using the new Google Places API.
        Parameters:
            place_id (str): The unique identifier for the place you want details on.
        Returns:
            dict or None: A dictionary containing the place details, or None if there's an error.
        """
        api_key = os.getenv("GOOGLE_PLACES_API_KEY")
        if not api_key:
            return {
                "error": "APIKeyMissing",
                "message": "Missing API key"
            }
    
        # Construct the endpoint URL using the new API standard
        url = f"https://places.googleapis.com/v1/places/{place_id}"

        field_mask = (
            "currentOpeningHours,delivery,formattedAddress,"
            "displayName,location,photos,"
            "types,websiteUri,id,regularOpeningHours"
        )
    
        # Define the query parameters with desired fields.
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": field_mask
        }
    
        try:
            # Make the GET request (Note: parameters are passed via the URL)
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise exception for HTTP errors
        
            # Parse and return the JSON data
            return response.json()
        except Exception as e:
            print("Error in get_place_details:", e)
            return None


    """
    Grabs the operating time from the google places api
    """
    def get_operating_time(self, place_data):
        operating_time = {}
        if "regularOpeningHours" in place_data:
            
            hours = place_data["regularOpeningHours"]
            descriptions = hours.get("weekdayDescriptions", [])
            for desc in descriptions:
                
                # Split the string into day and times
                try:
                    day_part, times_part = desc.split(":", 1)
                except:
                    continue

                day = day_part.strip()
                times_str = times_part.strip()
            
                if 'Closed' in times_str:
                    operating_time[day] = 'Closed'
                else:
                    # Split the times string on the dash. This regex coers possible extra whitespaces
                    times = re.split(r'\s*–\s*', times_str)
                    if len(times) == 2:
                        # Remove any extra whitespace, including unicode characgers
                        open_time = re.sub(r'\s+', '', times[0])
                        close_time = re.sub(r'\s+', '', times[1])
                        operating_time[day] = {
                            "open_time": open_time,
                            "close_time": close_time
                        }
        return operating_time
        
    """
        Inserts new place details into the 'locations' table using data from the API.
        Extracts and converts fields as needed. The inserted fields include:
           - place_id (unique identifier)
           - displayName
           - delivery (boolean)
           - latlong (a string formatted as "(lng, lat)")
           - type (JSON string for a list of types)
           - photos (JSON string for a list of photos)
           - websiteURI
        Returns a dictionary of the inserted record on success.
    """
    def insert_place_details(self, place_data):
        connection, cursor = self.get_db_connection()

        try:
            place_id = place_data.get("id")
            
            display_name_field = place_data.get("displayName") or place_data.get("name") or ""
            if isinstance(display_name_field, dict):
                display_name = display_name_field.get("text", "")
            else:
                display_name = display_name_field

            delivery = place_data.get("delivery", False)
            
            address = place_data.get("formattedAddress") or ""
           
            # Extract the location details
            location = place_data.get("location")
            lat = location.get("latitude") if location else None
            lng = location.get("longitude") if location else None
            latlong = f"({lng}, {lat})" if (lat is not None and lng is not None) else None

            types_field = place_data.get("types", [])

            all_photos = place_data.get("photos", [])
            photos = json.dumps(all_photos[:3])

            websiteURI = place_data.get("websiteUri") or ""
            
            operating_time = json.dumps(self.get_operating_time(place_data)) 

            query = """
                INSERT INTO locations (place_id, displayName, delivery, address, latlong, type, photos, websiteURI, operating_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (place_id)
                DO UPDATE SET place_id = locations.place_id
                RETURNING place_id, displayName, delivery, address, latlong, type, photos, websiteURI, operating_time;
            """
            cursor.execute(query, (place_id, display_name, delivery, address, latlong, types_field, photos, websiteURI, operating_time))
            connection.commit()
            record = cursor.fetchone()
            return {
                "place_id": record[0],
                "displayName": record[1],
                "delivery": record[2],
                "address": record[3],
                "latlong": record[4],
                "type": record[5],
                "photos": record[6],
                "websiteURI": record[7],
                "operating_time": record[8],
                "wait_times": 'Unknown'
            }
        except Exception as e:
            print("Error in insert_place_details", e)
            connection.rollback()
        finally:
            cursor.close()
            connection.close()

    """
        Given a list of minimal place details (each containing an 'id'),
        this function:
          1. Extracts a list of place IDs.
          2. Retrieves any full details from the local database.
          3. For each place, if full details are missing locally, it:
               - Fetches complete details from the API.
               - Inserts the new details into the database.
          4. Returns a dictionary mapping each place_id to its complete details.
    """
    def get_complete_place_details(self, api_places):
        
        # Extract place IDs from the minimal API details
        api_place_ids = [place.get("id") for place in api_places if place.get("id")]
        # Get local database details, if any
        local_places = self.retrieve_local_places(api_place_ids)

        complete_places = {}
        for place in api_places:
            pid = place.get("id")
            # Use local details if already complete
            if pid in local_places and local_places[pid]:
                #print(local_places[pid].keys())
                print("test 0")
                complete_places[pid] = local_places[pid]
            else:
                # Otherwise, fetch details from the API
                api_details = self.fetch_api_place_details(pid)
                if api_details:
                    # Insert the fetched details into the database
                    inserted_record = self.insert_place_details(api_details)
                    # Use the inserted record if insertion was successful
                    if inserted_record:
                        complete_places[pid] = inserted_record
                        print("test 1")
                    else:
                        print("test 2")
                        complete_places[pid] = api_details
        else:
            complete_places[pid] = place
        #print("test: ", complete_places['ChIJt_YJNEVEOogRp3VYcxU9Da4'].keys())
        return complete_places




