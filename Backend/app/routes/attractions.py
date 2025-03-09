from flask import Flask, request, jsonify
import json
from .models.attractionClass import AttractionClass
from .models.findNearbyPlacesClass import FindNearbyPlacesClass
from flask import Blueprint

bp = Blueprint('attractions', __name__)

@bp.route("/attractions/")
def company_info():
    print("test")
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    query = request.args.get('query')
    filters = request.args.get('filters')

    if lat is None or lon is None:
        return jsonify({"error": "Missing lat or lon parameters"}), 400
    print(lat)
    print(lon)
    user_location = {}
    user_location['lattitude'] = lat
    user_location['longitude'] = lon
    attraction_inst = AttractionClass(query, filters, user_location)
    nearby_places_data = attraction_inst.get_data()

    return json.dumps(nearby_places_data)