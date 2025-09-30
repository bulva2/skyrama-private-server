import time
from pathlib import Path
import os
import json

def handle_GetPassengers(request, user_id, json_data, task, task_number, init_data, quest_seq):
    if request["m"] == "landside_buildings.harvest":
        # Some requests seem to not have this field (bays)
        if "num_received_passengers" in request["p"]:
            json_data["goals"]["goals"][quest_seq]["tasks"][task_number]["num_completed"] = json_data["goals"]["goals"][quest_seq]["tasks"][task_number]["num_completed"] + request["p"]["num_received_passengers"]
    
    return json_data
