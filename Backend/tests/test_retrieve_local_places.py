import os
import json
import pytest
import sys

from Backend.app.routes.models.getPlaceDetails import GetPlaceDetailsClass
from Backend.tests.helpers.dummy_database_functions import DummyCursor, DummyConnection 


def dummy_get_db_connection():
    """
    Dummy version of get_db_connection that loads robust dummy data 
    from Backend/tests/data/dummy_place_data.json.
    """
    current_dir = os.path.dirname(__file__)
    data_file_path = os.path.join(current_dir, "data", "dummy_place_data.json")
    with open(data_file_path, "r") as f:
        dummy_data = json.load(f)
    dummy_cursor = DummyCursor(dummy_data)
    dummy_conn = DummyConnection(dummy_cursor)
    return dummy_conn, dummy_cursor


# --- Test Cases for retrieve_local_places ---
def test_empty_place_ids(monkeypatch):
    """
    When provided an empty list of place_ids the function should return an empty dictionary.
    """
    details_instance = GetPlaceDetailsClass()
    monkeypatch.setattr(details_instance, "get_db_connection", dummy_get_db_connection)
    
    result = details_instance.retrieve_local_places([])
    assert result == {}


def test_non_existent_place_id(monkeypatch):
    """
    If a non-existent place_id is provided, no matching rows should be returned
    and the dictionary remains empty.
    """
    details_instance = GetPlaceDetailsClass()
    # I am overriding the get_db_connection method in my GetPlaceDetailsClass
    monkeypatch.setattr(details_instance, "get_db_connection", dummy_get_db_connection)
    
    result = details_instance.retrieve_local_places(["non_existent"])
    # Since our dummy data contains only loc_1, loc_2, ..., loc_5 this should return {}
    assert result == {}


def test_valid_info(monkeypatch):
    """
    When valid place_ids are provided, the function should return the matching details.
    Assume the dummy JSON file contains entries for 'loc_1', 'loc_2', ..., etc.
    """
    details_instance = GetPlaceDetailsClass()
    monkeypatch.setattr(details_instance, "get_db_connection", dummy_get_db_connection)
    
    result = details_instance.retrieve_local_places(["loc_1", "loc_3"])
    # Check that only the requested location details are returned.
    assert "loc_1" in result
    assert "loc_3" in result

    # Check that the requested displayNames are returned
    expected_displayName_loc1 = "Location One"
    expected_displayName_loc3 = "Location Three"

    assert result["loc_1"]["displayName"] == expected_displayName_loc1
    assert result["loc_3"]["displayName"] == expected_displayName_loc3

    # Check that the requested delivery status are returned
    expected_delivery_status_loc1 = True
    expected_delivery_status_loc3 = True

    assert result["loc_1"]["delivery"] == expected_delivery_status_loc1
    assert result["loc_3"]["delivery"] == expected_delivery_status_loc3
    
    # Check that the requested address are returned
    expected_address_loc1 = "123 Main St"
    expected_address_loc3 = "789 Oak St"

    assert result["loc_1"]["address"] == expected_address_loc1
    assert result["loc_3"]["address"] == expected_address_loc3

    # Check that the requested latlong are returned
    expected_latlong_loc1 = "(12.34,56.78)"
    expected_latlong_loc3 = "(34.56,78.90)"

    assert result["loc_1"]["latlong"] == expected_latlong_loc1
    assert result["loc_3"]["latlong"] == expected_latlong_loc3

    # Check that the requested types are returned
    expected_types_loc1 = ["restaurant", "bar"]
    expected_types_loc3 = ["bar"]

    assert result["loc_1"]["type"] == expected_types_loc1
    assert result["loc_3"]["type"] == expected_types_loc3

    # Check that the requested photos are returned
    expected_photos_loc1 = [{"photo": "url1"}, {"photo": "url1b"}]
    expected_photos_loc3 = [{"photo": "url3"}]

    photos_loc1 = result["loc_1"]["photos"]
    photos_loc3 = result["loc_3"]["photos"]

    assert photos_loc1 == expected_photos_loc1
    assert photos_loc3 == expected_photos_loc3

    # Check that the requested WebsiteURI is returned
    expected_webURI_loc1 = "http://locationone.example.com"
    expected_webURI_loc3 = "http://locationthree.example.com"

    assert result["loc_1"]["websiteURI"] == expected_webURI_loc1
    assert result["loc_3"]["websiteURI"] == expected_webURI_loc3
