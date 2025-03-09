import os
import pytest
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Backend.app.routes.models.findNearbyPlacesClass import FindNearbyPlacesClass, configure
from Backend.app.routes.models.getPlaceDetails import GetPlaceDetailsClass

@pytest.fixture
def finder():
    configure()
    return FindNearbyPlacesClass()

"""
    Integration test that makes a real API call to Google Places API with blank filters.

    Query: "pizza in New York"
    Filters: {} (blank)
    User Location: Coordinates for New York City (latitude 40.7128, longitude -74.0060)
    
    Verifies:
      - The response object is not None.
      - The response includes a 'places' key.
      - If an error is returned (for example due to quota or key issues), the test is skipped.
"""
def test_get_nearby_places_integration(finder):
    
    # Define an actual search query
    query = "Bars in Ann Arbor"
    filters = {}
    user_location = {"latitude": 42.2808, "longitude": -83.7430}  # Center of Ann Arbor

    # Call the function under test (this will make a real API call)
    response = finder.getNearbyPlaces(query, filters, user_location)

    # Basic assertions for a successful API call
    assert response is not None, "Expected a response from Google Places API"

    # If Google returns an error in the JSON (for instance, due to quota issues), skip the test.
    if "error" in response:
        pytest.skip("Google Places API returned an error: " + response.get("message", "Unknown error"))
    else:
        assert "places" in response, "Response should contain a 'places' key"

    print(response)

