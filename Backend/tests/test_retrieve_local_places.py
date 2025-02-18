import os
import json
import pytest
import sys

from Backend.flask.routes.models.getPlaceDetails import GetPlaceDetailsClass
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


def test_valid_place_ids(monkeypatch):
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
    # You can also validate specific fields based on your dummy data structure.