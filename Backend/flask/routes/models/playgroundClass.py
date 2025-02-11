from flaskClass import FlaskClass
from dotenv import load_dotenv
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
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.id"
        }

        # Create the payload with the user-provided query.
        payload = {
            "textQuery": query,
            "pageSize": 5  # Adjust the number of results as needed
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
    configure()

    nearbyRestaurant = PlaygroundClass(regInfo={})

    nearbyRestaurant.dummy_search_restaurant()
    
