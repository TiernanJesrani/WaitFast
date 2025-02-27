from flaskClass import FlaskClass
from dotenv import load_dotenv
from findNearbyPlacesClass import FindNearbyPlacesClass
from getPlaceDetails import GetPlaceDetailsClass
import os
import requests

def configure():
    load_dotenv()

class PlaygroundClass(FlaskClass):
    def __init__(self, regInfo):
        self.regInfo = regInfo

    def get_data(self):
        return "hello"
    

    def search_restaurant(self, query):
        """
        Makes a test API request to the Google Places Text Search endpoint.
        
        :param query: The text query from the user (e.g., "sushi in San Francisco")
        :return: JSON response from the Google API or error information.
        """
        api_url = "https://places.googleapis.com/v1/places:searchText"

        api_key = os.getenv("GOOGLE_PLACES_API_KEY")

        if not api_key:
            return {
                "error": "API key not found",
                "message": "Ensure that GOOGLE_PLACES_API_KEY is set in your .env file"
            }
        
        # Define the headers including the API key and field mask
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": "places.id,places.regularOpeningHours"
        }

        # Create the payload with the user-provided query.
        payload = {
            "textQuery": query,
            "pageSize": 1  # Adjust the number of results as needed
        }

        try:
            response = requests.post(api_url, json=payload, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": "RequestException",
                "message": str(e)
        }
    
    def get_place_details(self, place_id):
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
    Dummy function to demonstrate how you can search for a restaurant
    """
    def dummy_search_restaurant(self):

        user_query = input("Enter your search query: ")

        restaurant_finder = PlaygroundClass(regInfo={})

        result = restaurant_finder.search_restaurant(user_query)

        print(result)


if __name__ == "__main__":

    # Configure the environment variables
    

    find_nearby_places = FindNearbyPlacesClass()

    restuarants_in_ann_arbor = "Restaurants in Ann Arbor"
    no_query = ""
    no_filters = {}
    restaurant_type = {"type": "restaurant"}
    center_ann_arbor = {
        "latitude": 42.2,
        "longitude": 83.7
    }

    center_long_grove = {
        "latitude": 42.17,
        "longitude": -87.99
    }

    center_lincolnshire = {
        "latitude": 40.14,
        "longitude": -89.36
    }
    
    result = find_nearby_places.getFilteredNearbyPlaces(restuarants_in_ann_arbor, no_filters, center_ann_arbor)



    
    


    
