import math
import time
from src.easy_events import get_pax_multiplier

def handle_landside_buildingsHarvest(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = None

    if request["p"]["obj_type"] == "terminal":
        j = 0
        for i in json_data["terminals"]:
            if int(i["id"]) == request["p"]["id"]:
                json_data["terminals"][j]["last_harvest_time"] = request["p"]["last_harvest_time"]
                terminal_types_id = json_data["terminals"][j]["terminal_types_id"]
                for g in init_data["terminalTypes"]:
                    if int(g["id"]) == int(terminal_types_id):
                        num_received_passengers = math.floor(g["capacity"] * get_pax_multiplier())
                json_data["playerData"]["passengers"] += num_received_passengers
                request["p"]["num_received_passengers"] = num_received_passengers # Simplify the GetPassengers quest script.
            j = j + 1

    elif request["p"]["obj_type"] == "landside_building":
        for i in json_data["landsideBuildings"]:
            if int(i["id"]) == request["p"]["id"]:
                i["last_harvest_time"] = request["p"]["last_harvest_time"]
                landside_building_types_id = i["landside_building_types_id"]
                for g in init_data["landsideBuildingTypes"]:
                    if int(g["id"]) == int(landside_building_types_id):
                        num_received_passengers = math.floor(g["capacity"] * get_pax_multiplier())
                json_data["playerData"]["passengers"] += num_received_passengers
                request["p"]["num_received_passengers"] = num_received_passengers # Simplify the GetPassengers quest script.