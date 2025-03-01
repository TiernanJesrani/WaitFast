from flask import Flask
import json
from .models.findNearbyPlacesClass import FindNearbyPlacesClass
from flask import Blueprint

bp = Blueprint('findNearbyPlaces', __name__)

@bp.route("/findNearbyPlaces")
def nearby_places(query, filters, user_location=None):
    nearby_places_inst = FindNearbyPlacesClass()
    nearby_places_data = nearby_places_inst.get_data(query, filters, user_location)
    return json.dumps(nearby_places_data)