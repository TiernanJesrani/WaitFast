from flask import Flask
import json
from models.attractionClass import AttractionClass
from flask import Blueprint

bp = Blueprint('attractions', __name__)

@bp.route("/attractions/")
def company_info():
    attractionInst = AttractionClass(1)
    attraction_data = attractionInst.get_data()
    return json.dumps(attraction_data)