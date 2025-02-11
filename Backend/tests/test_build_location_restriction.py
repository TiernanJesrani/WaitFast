import os
import pytest
import math
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Backend.flask.routes.models.findNearbyPlacesClass import FindNearbyPlacesClass, configure


"""
Notes:
    @pytest.fixture is a decorator provided by pytest that allows you to define a fixture function
    Fixtures are functions that set up a speciic environment or state needed by my tests before they run
    You can inject the fixture into test functions by including a parameter that's the same name as the fixture
"""

@pytest.fixture
def finder():
    # Create an instance of FindNearbyPlacesClass for our tests.
    return FindNearbyPlacesClass()

def test_build_location_restriction_valid(finder):
    """
    Test that when valid filters and a valid user_location are provided,
    the function returns a correctly computed rectangular locationRestriction.
    """
    # Providing distance_max in miles.
    filters = {"distance_max": 1}  # 1 mile 
    user_location = {"latitude": 40.0, "longitude": -75.0}
    result = finder.build_location_restriction(filters, user_location)
    
    # Calculate the expected boundaries.
    effective_distance = filters["distance_max"] * 1609.34  # convert miles to meters
    delta_lat = effective_distance / 111111.0  # degrees change in latitude
    delta_lon = effective_distance / (111111.0 * math.cos(math.radians(user_location["latitude"])))  # degrees change in longitude

    expected_low_lat = user_location["latitude"] - delta_lat
    expected_high_lat = user_location["latitude"] + delta_lat
    expected_low_lon = user_location["longitude"] - delta_lon
    expected_high_lon = user_location["longitude"] + delta_lon

    # We expect the returned dict to contain a "rectangle" key.
    assert "rectangle" in result

    # Due to floating point computations, we use math.isclose for each coordinate.
    actual_low_lat = result["rectangle"]["low"]["latitude"]
    actual_low_lon = result["rectangle"]["low"]["longitude"]
    actual_high_lat = result["rectangle"]["high"]["latitude"]
    actual_high_lon = result["rectangle"]["high"]["longitude"]

    assert math.isclose(actual_low_lat, expected_low_lat, rel_tol=1e-5)
    assert math.isclose(actual_low_lon, expected_low_lon, rel_tol=1e-5)
    assert math.isclose(actual_high_lat, expected_high_lat, rel_tol=1e-5)
    assert math.isclose(actual_high_lon, expected_high_lon, rel_tol=1e-5)

def test_build_location_restriction_no_filters(finder):
    """
    Test that if no filters are provided, the function returns an empty dictionary.
    """
    filters = {}  # No filters present.
    user_location = {"latitude": 40.0, "longitude": -75.0}
    result = finder.build_location_restriction(filters, user_location)
    assert result == {}

def test_build_location_restriction_no_distance_max(finder):
    """
    Test that if filters are provided but distance_max is not included,
    the function returns an empty dictionary.
    """
    filters = {"distance_min": 0.5}  # Only distance_min provided.
    user_location = {"latitude": 40.0, "longitude": -75.0}
    result = finder.build_location_restriction(filters, user_location)
    assert result == {}

def test_build_location_restriction_missing_user_location(finder):
    """
    Test that if user_location is missing necessary latitude or longitude,
    the function returns an empty dictionary.
    """
    filters = {"distance_max": 1}
    # Missing both latitude and longitude.
    user_location = {}
    result = finder.build_location_restriction(filters, user_location)
    assert result == {}

def test_build_location_restriction_none_user_location(finder):
    """
    Test that if the user_location is None, the function returns an empty dictionary.
    """
    filters = {"distance_max": 1}
    user_location = None
    result = finder.build_location_restriction(filters, user_location)
    assert result == {}
