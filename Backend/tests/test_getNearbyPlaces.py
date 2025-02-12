import os
import pytest
import math
import sys
import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Backend.flask.routes.models.findNearbyPlacesClass import FindNearbyPlacesClass, configure
from Backend.tests.helpers.dummy_api import DummyResponse, dummy_post_with_types, dummy_post

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


"""
Notes:
    The marker is telling the testing framework to run this test function twice
        1) Run with filter_type == restaurant
        2) Run with filter_type == bar
    monkeypath overrides the post request to Google Places API and makes it to the dummy_api
"""
@pytest.mark.parametrize("filter_type", ["restaurant", "bar"])
def test_get_nearby_places_with_only_included_type(monkeypatch, finder, filter_type):
    """
    Test getNearbyPlaces when no text search is provided and the only filter is the place type.
    This test verifies that:
      - The filter (e.g., {"type": "restaurant"}) is correctly mapped to the API payload as "includedType".
      - The dummy API call returns only the dummy places whose hardcoded "type" matches the filter.
    """
    filters = {"type": filter_type}  # The filter key 'type' is mapped to "includedType" in the payload.
    user_location = {"latitude": 42.2808, "longitude": -83.7430}  # Dummy user location.
    query = ""  # No text search provided.
    
    # Monkeypatch requests.post to use our dummy_post_with_types function.
    monkeypatch.setattr(requests, "post", dummy_post_with_types)
    
    # Call the function under test.
    response = finder.getNearbyPlaces(query, filters, user_location)
    
    # Verify that the response includes a 'places' key.
    assert "places" in response, "Response should include a 'places' key"
    places = response["places"]
    
    # Check that every returned place has a 'type' attribute matching filter_type.
    for place in places:
        assert "type" in place, "Each place should have a 'type' attribute"
        assert place["type"] == filter_type, f"Expected place type '{filter_type}', got '{place['type']}'"