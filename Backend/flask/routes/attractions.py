from flask import Flask, request, jsonify
import json
from .models.attractionClass import AttractionClass
from flask import Blueprint

bp = Blueprint('attractions', __name__)

@bp.route("/attractions/")
def company_info():
    lat = request.args.get('lat')
    lon = request.args.get('lon')

    if lat is None or lon is None:
        return jsonify({"error": "Missing lat or lon parameters"}), 400
    print(lat)
    print(lon)
    attractionInst = AttractionClass(1)
    attraction_data = attractionInst.get_data()
    return json.dumps(attraction_data)