import psycopg2
import os
import requests
import sys
import json
from flaskClass import FlaskClass

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
    def retrieve_local_places(self, place_ids):
        # Build a dictionary mapping for places already in the DB
        local_places = {}
        if not place_ids:
            return local_places
        
        # SQL Query Explanation:
        # - The main FROM clause selects from the 'locations' table (aliased as l).
        # - Two LEFT JOIN subqueries aggregate the records from 'opening_hours' and 'wait_times'
        #   into JSON arrays.
        #
        #   a) The first subquery (aliased as oh_agg) groups rows in the opening_hours table by
        #      location_id and uses json_agg with json_build_object to create a JSON array of objects.
        #      Each object in the array has keys: day, open_time, and close_time.
        #
        #   b) The second subquery (aliased as wt_agg) groups rows in the wait_times table by
        #      location_id and aggregates rows into a JSON array of objects that now include the day
        #      field (in addition to hour, wait_time, sample_count, and updated_at).
        #
        # - COALESCE is used to return an empty JSON array ('[]') if there are no matching records in 
        #   either joined table.
        #
        # - The WHERE clause filters locations based on the provided placed_ids.
        
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
                    COALESCE(oh_agg.opening_hours, '[]'::json) AS opening_hours,
                    COALESCE(wt_agg.wait_times, '[]'::json) AS wait_times
                FROM locations l
                LEFT JOIN (
                    SELECT 
                        location_id,
                        json_agg(json_build_object(
                            'day', day,
                            'open_time', open_time,
                            'close_time', close_time
                        )) AS opening_hours
                    FROM opening_hours
                    GROUP BY location_id
                ) AS oh_agg ON oh_agg.location_id = l.id
                LEFT JOIN (
                    SELECT
                        location_id,
                        json_agg(json_build_object(
                            'day', day,
                            'hour', hour,
                            'wait_time', wait_time,
                            'sample_count', sample_count,
                            'updated_at', updated_at
                        )) AS wait_times
                    FROM wait_times
                    GROUP BY location_id
                    ) AS wt_agg ON wt_agg.location_id = l.id
                    WHERE l.place_id IN %s;
            """
            cursor.execute(query, (format_ids, ))
            results = cursor.fetchall()

            # For each row from the result, populate the local_laces dictionary
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
                    "opening_hours": row[8], # Aggregated JSON array for all opening hours
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
            "types,websiteUri,id"
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
            lat = location.get("lat") if location else None
            lng = location.get("lng") if location else None
            latlong = f"({lng}, {lat})" if (lat is not None and lng is not None) else None

            types_field = place_data.get("types", [])

            photos = json.dumps(place_data.get("photos", []))
            websiteURI = place_data.get("websiteUri") or ""

            query = """
                INSERT INTO locations (place_id, displayName, delivery, address, latlong, type, photos, websiteURI)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING place_id, displayName, delivery, address, latlong, type, photos, websiteURI;
            """
            cursor.execute(query, (place_id, display_name, delivery, address, latlong, types_field, photos, websiteURI))
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
                "websiteURI": record[7]
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
                    else:
                        complete_places[pid] = api_details
        else:
            complete_places[pid] = place
        return complete_places




