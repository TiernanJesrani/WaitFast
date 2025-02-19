import json
import pytest
from Backend.flask.routes.models.getPlaceDetails import GetPlaceDetailsClass
from Backend.tests.helpers.dummy_database_functions import DummyCursor, DummyConnection

def dummy_get_db_connection(self):
    """
    Create a dummy connection and cursor. We override the `fetchone` method on the dummy cursor
    to simulate the database returning the inserted record.
    """
    # Create a dummy cursor with an empty data list (data is not used here)
    dummy_cursor = DummyCursor(data=[])
    
    # Define a fake fetchone method that returns a tuple in the expected order.
    # The order is: place_id, displayName, delivery, address, latlong, type, photos, websiteURI.
    def fake_fetchone():
        return (
            "loc_test",                   # place_id
            "Test Location",              # displayName
            True,                         # delivery
            "Test Address",               # address
            "(1.0, 2.0)",                 # latlong (formatted as "(lng, lat)")
            ["testType"],                 # type field (list of types)
            json.dumps([{"photo": "test_photo"}]),  # photos stored as JSON string
            "http://test.com"             # websiteURI
        )
    dummy_cursor.fetchone = fake_fetchone  # Override the fetchone method on our dummy cursor.

    dummy_connection = DummyConnection(dummy_cursor)
    return dummy_connection, dummy_cursor

def test_insert_place_details(monkeypatch):
    """
    Test the `insert_place_details` method to verify that it correctly inserts
    a place and returns the expected record.
    """
    details = GetPlaceDetailsClass()
    
    # Monkeypatch the database connection method to return our dummy connection & cursor.
    monkeypatch.setattr(GetPlaceDetailsClass, "get_db_connection", dummy_get_db_connection)
    
    # Set up sample API data for insertion.
    sample_api_data = {
        "id": "loc_test",
        "displayName": "Test Location",
        "delivery": True,
        "formattedAddress": "Test Address",
        "location": {"lat": 2.0, "lng": 1.0},
        "types": ["testType"],
        "photos": [{"photo": "test_photo"}],
        "websiteUri": "http://test.com"
    }
    
    # Call the method under test.
    result = details.insert_place_details(sample_api_data)
    
    # Define the expected record.
    expected = {
        "place_id": "loc_test",
        "displayName": "Test Location",
        "delivery": True,
        "address": "Test Address",
        "latlong": "(1.0, 2.0)",  # Note how latlong is constructed.
        "type": ["testType"],
        "photos": json.dumps([{"photo": "test_photo"}]),
        "websiteURI": "http://test.com"
    }
    
    # Assert the returned record matches expected data.
    assert result == expected