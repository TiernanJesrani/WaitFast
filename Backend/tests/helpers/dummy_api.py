import requests

class DummyResponse:
    """
    Simulates the requests.Response object.
    """
    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code != 200:
            raise requests.exceptions.RequestException("HTTP Error")

def dummy_post_with_types(url, json, headers):
    """
    This dummy function simulates a Google Places API call for testing getNearbyPlaces
    when the only filter is an includedType.

    It hardcodes 10 dummy places with 'type' attributes:
      - 5 places are marked as 'restaurant'.
      - 5 places are marked as 'bar'.

    The function then filters and returns only those places whose type matches the 
    expected type provided via the "includedType" key in the JSON payload.
    """
    # Extract the expected type from the payload.
    expected_type = json.get("includedType")

    # Define 10 dummy places with hardcoded types.
    all_dummy_places = [
        {"id": "1", "location": {"latitude": 42.2800, "longitude": -83.7400}, "type": "restaurant"},
        {"id": "2", "location": {"latitude": 42.2810, "longitude": -83.7410}, "type": "bar"},
        {"id": "3", "location": {"latitude": 42.2820, "longitude": -83.7420}, "type": "restaurant"},
        {"id": "4", "location": {"latitude": 42.2830, "longitude": -83.7430}, "type": "bar"},
        {"id": "5", "location": {"latitude": 42.2840, "longitude": -83.7440}, "type": "restaurant"},
        {"id": "6", "location": {"latitude": 42.2850, "longitude": -83.7450}, "type": "bar"},
        {"id": "7", "location": {"latitude": 42.2860, "longitude": -83.7460}, "type": "restaurant"},
        {"id": "8", "location": {"latitude": 42.2870, "longitude": -83.7470}, "type": "bar"},
        {"id": "9", "location": {"latitude": 42.2880, "longitude": -83.7480}, "type": "restaurant"},
        {"id": "10", "location": {"latitude": 42.2890, "longitude": -83.7490}, "type": "bar"},
    ]

    # Filter the dummy places based on the expected_type.
    if expected_type:
        filtered_places = [place for place in all_dummy_places if place["type"] == expected_type]
    else:
        filtered_places = all_dummy_places

    return DummyResponse({"places": filtered_places})


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