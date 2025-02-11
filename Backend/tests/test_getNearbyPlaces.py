import os
import pytest
import math
import sys
import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Backend.flask.routes.models.findNearbyPlacesClass import FindNearbyPlacesClass, configure

# DummyResponse simulates the requests.Response object.
class DummyResponse:
    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code != 200:
            raise requests.exceptions.RequestException("HTTP Error")
        
def dummy_post(url, json, headers):
    """
    This dummy function simulates a Google Places API call.
    It is designed to inspect the payload for a locationRestriction.
    If provided, it filters 10 dummy places so that only those whose 
    coordinates lie within the rectangular bounds are returned.
    """
    # Try to receive the rectangle bounds from the JSON payload   
    location_restriction = json.get("locationRestriction", {})
    rect = location_restriction.get("rectangle", {})
    low_lat = rect.get("low", {}).get("latitude")
    high_lat = rect.get("high", {}).get("latitude")
    low_lon = rect.get("low", {}).get("longitude")
    high_lon = rect.get("high", {}).get("longitude") 

    # Define 10 dummy places.
    all_dummy_places = [
        # Places that should fall inside the computed bounds.
        {"id": "1", "location": {"latitude": 42.2800, "longitude": -83.7400}},
        {"id": "2", "location": {"latitude": 42.2850, "longitude": -83.7500}},
        {"id": "3", "location": {"latitude": 42.2750, "longitude": -83.7300}},
        {"id": "4", "location": {"latitude": 42.2900, "longitude": -83.7500}},
        {"id": "5", "location": {"latitude": 42.2780, "longitude": -83.7400}},
        # Places that should fall outside the computed bounds.
        {"id": "6", "location": {"latitude": 42.2600, "longitude": -83.7300}},  # low latitude
        {"id": "7", "location": {"latitude": 42.3000, "longitude": -83.7500}},  # high latitude
        {"id": "8", "location": {"latitude": 42.2800, "longitude": -83.7700}},  # longitude too low
        {"id": "9", "location": {"latitude": 42.2800, "longitude": -83.7100}},  # longitude too high
        {"id": "10", "location": {"latitude": 42.3100, "longitude": -83.7100}}, # outside both
    ]

    # If we have rectangle bounds, filter the dummy places.
    if low_lat is not None and high_lat is not None and low_lon is not None and high_lon is not None:
        filtered_places = []
        for place in all_dummy_places:
            lat = place["location"]["latitude"]
            lon = place["location"]["longitude"]
            if low_lat <= lat <= high_lat and low_lon <= lon <= high_lon:
                filtered_places.append(place)
        return DummyResponse({"places": filtered_places})
    else:
        # If no restriction, return all dummy places.
        return DummyResponse({"places": all_dummy_places})
    
@pytest.fixture
def finder():
    # Optionally load environment variables (e.g., GOOGLE_PLACES_API_KEY), though not critical for the dummy.
    configure()
    return FindNearbyPlacesClass()

def test_get_nearby_places_max_distance(monkeypatch, finder):
    """
    Test getNearbyPlaces using a filter that specifies a max distance.
    In this test, we set a distance_max filter (1 mile), and the user location is the center of Ann Arbor.
    The dummy_post function returns 10 dummy places but only those 5 that fall within the computed 
    locationRestriction (rectangle) will be returned.
    """
    # Set filter with a max distance of 1 mile.
    filters = {"distance_max": 1}
    user_location = {"latitude": 42.2808, "longitude": -83.7430}  # Center of Ann Arbor
    query = ""  # No query provided.

    # Monkeypatch requests.post so that it uses our dummy_post.
    monkeypatch.setattr(requests, "post", dummy_post)

    # Call the function under test.
    response = finder.getNearbyPlaces(query, filters, user_location)
    
    # Verify the response has a 'places' key.
    assert "places" in response
    places = response["places"]

    # Expect exactly 5 places to be returned by dummy_post.
    assert isinstance(places, list)
    assert len(places) == 5, f"Expected 5 places, got {len(places)}"

    # Retrieve the computed rectangle from build_location_restriction.
    location_restriction = finder.build_location_restriction(filters, user_location)
    rect = location_restriction.get("rectangle", {})
    low_lat = rect.get("low", {}).get("latitude")
    high_lat = rect.get("high", {}).get("latitude")
    low_lon = rect.get("low", {}).get("longitude")
    high_lon = rect.get("high", {}).get("longitude")

    # Confirm that the rectangle boundaries were computed.
    assert low_lat is not None and high_lat is not None
    assert low_lon is not None and high_lon is not None

    # Check that each returned place lies within the expected rectangle.
    for place in places:
        lat = place.get("location", {}).get("latitude")
        lon = place.get("location", {}).get("longitude")
        assert low_lat <= lat <= high_lat, f"Latitude {lat} is not within [{low_lat}, {high_lat}]"
        assert low_lon <= lon <= high_lon, f"Longitude {lon} is not within [{low_lon}, {high_lon}]"
