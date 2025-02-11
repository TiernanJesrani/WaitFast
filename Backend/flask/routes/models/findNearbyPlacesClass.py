from .flaskClass import FlaskClass
from dotenv import load_dotenv
import os
import requests
from math import cos, radians

def configure():
    load_dotenv()


class FindNearbyPlacesClass(FlaskClass):

    def __init__(self):
        return
    

    def get_date(self):
        return "hello"
    
    """
        Builds a rectangular locationRestriction based on the user's location and the provided maximum distance.
        
        The distance_max provided in the filters is in miles. This function converts miles to meters before
        applying the calculation. In particular:
            - If both distance_max (with or without an optional distance_min) is provided, the 
              maximum distance is used to compute a rectangular viewport.
            - If no distance_max is provided (even if distance_min is given), an empty dict is returned.
        
        Parameters:
            filters (dict): May contain 'distance_min' and/or 'distance_max' (in miles).
            user_location (dict): Contains the keys 'latitude' and 'longitude'.
        
        Returns:
            dict: A dictionary representing the locationRestriction, or an empty dict if no maximum distance is provided.
    """
    def build_location_restriction(self, filters, user_location):
        
        if filters and user_location and "distance_max" in filters:
            # Convert distance from miles to meteres
            effective_distance = filters["distance_max"] * 1609.34 
            user_lat = user_location.get("latitude")
            user_lon = user_location.get("longitude")
            # If we don't have latitude or longitude return an empty dict
            if user_lat is None or user_lon is None:
                return {}
            
            # Calculate the change in degrees for the specified distance (in meters)
            # Converting meters to degrees
            delta_lat = effective_distance / 111111.0 # Approximate conversion: 1 degree latitude ≈ 111,111 meters
            delta_lon = effective_distance / (111111.0 * cos(radians(user_lat)))  # Adjust by latitude

            low_lat = user_lat - delta_lat
            high_lat = user_lat + delta_lat
            low_lon = user_lon - delta_lon
            high_lon = user_lon + delta_lon

            return {
                "rectangle": {
                    "low": {"latitude": low_lat, "longitude": low_lon},
                    "high": {"latitude": high_lat, "longitude": high_lon}
                }
            } 

        return {}          

    """
        Makes an API request using a text query and an optional filters dictionary.
        
        For distance filtering:
          - If the filters contain a 'distance_max' (with or without a 'distance_min')
            and a valid user_location is provided, a locationRestriction is built based on the maximum distance.
          - The 'distance_max' is considered to be in miles. It will be converted to meters for the
            computation.
          - If only 'distance_min' is provided (without 'distance_max'), no locationRestriction is built.
          - If neither distance parameter is provided, no locationRestriction is added.
        
        Input:
            query (str): A text string (e.g., "pizza in New York").
            filters (dict): Contains optional filter parameters (e.g., type, distance_min, distance_max in miles,
                            party_size, avg_wait_time, wait_time_min, wait_time_max, etc.).
            user_location (dict): Contains keys "latitude" and "longitude". Required for building a locationRestriction.
            page_token (str): (Optional) The token for fetching the next page of results.
        Returns:
            JSON response from the Google Places API, which may include a nextPageToken or an error dictionary.
    """
    def getNearbyPlaces(self, query, filters, user_location=None, page_token=None):
        
        api_url = "https://places.googleapis.com/v1/places:searchText"
        api_key = os.getenv("GOOGLE_PLACES_API_KEY")
        if not api_key:
            return {
                "error": "APIKeyMissing",
                "message": "Missing API key"
            }
        
        # Set up the field mask as required.
        field_mask = (
            "places.currentOpeningHours,places.delivery,places.formattedAddress,"
            "places.displayName,places.location,places.photos,places.servesBreakfast,"
            "places.servesBrunch,places.servesCocktails,places.servesCoffee,places.servesDessert,"
            "places.servesDinner,places.servesLunch,places.servesVegetarianFood,places.servesWine,"
            "places.types,places.websiteUri,places.id"
        )


        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": field_mask
        } 
        # Make sure that both the search query and the filters aren't blank
        # TODO: Determine how to best handle an error case
        if (not query or query.strip() == "") and (not filters or len(filters) == 0):
            return {
                "error": "InvalidInput",
                "message": "Both query and filters cannot be blank. Please provide at least one."
            }
   

        # Start constructing the payload
        payload = {}

        # This feature is here to provide infinite scrolling
        if page_token:
            # When a page token is provided, just send it to get the next page of results
            payload["pageToken"] = page_token

        # Add the search query if a valid query is provided
        if query and query.strip() != "":
            payload["textQuery"] = query

        # Set a default pageSize if not provided in the filters
        # TODO: Determine where it's best to define pageSize
        if not (filters and "pageSize" in filters):
            payload["pageSize"] = 5

        # Merge the filters into the payload
        # Special handling: if a filter contains a "type", apply it as "included type"
        if filters and isinstance(filters, dict):
            for key, value in filters.items():
                if key == "type" and value is not None and value != "":
                    payload["includedType"] = value
        
        if user_location and filters and "distance_max" in filters:
            location_restriction = self.build_location_restriction(filters, user_location)
            if location_restriction:
                payload["locationRestriction"] = location_restriction

        
        # Make the request
        try:
            response = requests.post(api_url, json=payload, headers=headers)
            response.raise_for_status() # Raise exception if HTTP status error occurs
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": "RequestException",
                "message": str(e)
            }
        

    """
        Combines Google Places results with custom data from our database and then applies custom filtering
        and sorting based on proprietary wait time data.
        
        Custom behavior:
          - If "wait_time_max" is provided in filters, any place with a wait time (from our custom data)
            greater than this value will be excluded.
          - If "avg_wait_time" is provided in filters, the final results will be sorted by the average wait time 
            (in ascending order).
        
        Steps:
          1. Query the Google Places API via getNearbyPlaces.
          2. Extract the place IDs from the Google results.
          3. Query our custom database for each place to retrieve custom data (avg_wait_time and wait_time_max).
          4. Merge the custom data into the Google results, apply filtering based on wait_time_max, and
             optionally sort by avg_wait_time.
        
        Returns:
            dict: A dictionary with key "places" containing the filtered (and possibly sorted) results.
    """
    def getFilteredNearbyPlaces(self, query, filters, user_location=None):

        # Step 1: Get nearby places from Google API
        # TODO: Determine how to use the nextPageToken for infinite scrolling
        google_results = self.getNearbyPlaces(query, filters, user_location)
        if "error" in google_results:
            return google_results
        
        # Step 2: Extract place IDs from Google Resutls
        # place_ids will contain a list of IDs for all valid place objects returned by the API
        places = google_results.get("places", [])
        place_ids = [place.get("id") for place in places if place.get("id")]


        # Step 3: Get custom data from our own datebase
        # This data will store the wait times we have assocaited with places
        # This is going to pretty much just be wait time data
        # TODO: Replace this with a query to our own database
        # ex: cutom_date = self.getCustomData(place_ids, filters)
        custom_data = None

        # Step 4: Merge custom data and apply filters
        # If avg_wait_time is specified, then the results will be sorted in order of avg_wait_time
        # If wait_time_max is specified, then no places greater than wait_time_max will occur
        filtered_places = []
        for place in places:
            pid = place.get("id")
            data = custom_data.get(pid, {})
            meets_criteria = True

            # Filter: If wait_time_max filter is provided, exclude any place that has a custom wait_time above it.
            if "wait_time_max" in filters and data.get("wait_time_max") is not None:
                if data["wait_time_max"] > filters["wait_time_max"]:
                    meets_criteria = False

            if meets_criteria:
                # Merge the custom data (e.g., avg_wait_time) into the Google place result.
                place.update(data)
                filtered_places.append(place)        

        # Step 5: If the avg_wait_time filter is provided, sort results by avg_wait_time in ascending order.
        if "curr_wait_time" in filters:
            filtered_places.sort(key=lambda x: x.get("curr_wait_time", float('inf')))

        return {"places": filtered_places}



