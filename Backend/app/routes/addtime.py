from flask import Flask, request, jsonify
import json
from .models.waitTimeSubmissionClass import WaitTimeSubmissionClass
from .models.getPlaceDetails import GetPlaceDetailsClass
from flask import Blueprint

bp = Blueprint('addtime', __name__)

@bp.route("/addtime/")
def receive_time():
    time = request.args.get('time')
    pid = request.args.get('pid')

    if time is None or pid is None:
        return jsonify({"error": "Missing time or pid parameters"}), 400
    # print(time)
    # print(pid)
    waittimeInst = WaitTimeSubmissionClass()
    getPlaceInst = GetPlaceDetailsClass()
    
    waittimeInst.submit_wait_time(pid, round(int(float(time)) / 60))

    return json.dumps(getPlaceInst.retrieve_new_time(pid))
