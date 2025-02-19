import os
import json
import requests
import pytest

from Backend.flask.routes.models.getPlaceDetails import GetPlaceDetailsClass

# Dummy response class to simulate the response from requests.get
class DummyResponse:
    def __init__(self, json_data, status_code):
        self._json_data = json_data
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code != 200:
            raise requests.HTTPError("HTTP error occurred")

    def json(self):
        return self._json_data

def test_fetch_api_place_details_missing_api_key(monkeypatch):
    """
    Test that if the GOOGLE_PLACES_API_KEY environment variable is missing,
    the function returns an error with place_id passed.
    """
    # Remove the API key (if it exists)
    # Within the context of the test this environment variable is removed
    monkeypatch.delenv("GOOGLE_PLACES_API_KEY", raising=False)
    
    instance = GetPlaceDetailsClass()
    # Pass a valid place_id
    result = instance.fetch_api_place_details("test_place_id")
    expected = {
        "error": "APIKeyMissing",
        "message": "Missing API key"
    }
    assert result == expected

def test_fetch_api_place_details_success(monkeypatch):
    """
    Test that when the API returns a valid response containing a "places" key,
    the function returns the first place in the list.
    """
    monkeypatch.setenv("GOOGLE_PLACES_API_KEY", "dummy_key")
    
    dummy_place = {
        "id": "test_place_id",
        "displayName": "Test Place",
        "delivery": True,
        "formattedAddress": "123 Test St"
        # Additional fields as needed...
    }
    dummy_json = {"places": [dummy_place]}
    
    # This is our dummy_get that we will use to override the responses.get
    def dummy_get(url, json, headers):
        # Confirm that the correct place_id is being sent in the request payload.
        assert json.get("query") == "test_place_id"
        return DummyResponse(dummy_json, 200)
    
    monkeypatch.setattr(requests, "get", dummy_get)
    
    instance = GetPlaceDetailsClass()
    result = instance.fetch_api_place_details("test_place_id")
    # Expect the first (and only) place in the list to be returned.
    assert result == dummy_place