from src.enums import PlaneState
import time

def handle_planesMiss(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = {"planes": {}}

    plane_id = request["p"]["id"]
    player_id = request["p"]["player_id"]

    for idx, plane in enumerate(json_data["planes"]):
        if int(plane["id"]) == plane_id:
            if player_id == 0:
                plane["flight_status"] = PlaneState.FLYING_TO_BUDDY.value # 77
                plane["departure_time"] = request["t"] - 450
                plane["arrival_time"] = request["t"] + 450
                plane["start_service_time"] = 0
                plane["last_state_change_time"] = request["t"]
                plane["player_id"] = player_id
                plane["subcontainer_id"] = -1
                plane["container_id"] = -1
                plane["to_player_id"] = request["p"]["to_player_id"]
                plane["instantland"] = 0
            else:
                json_data["planes"].pop(idx)
            break