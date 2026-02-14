import time
from src.enums import PlaneState
from src.utils import subtract_resources

def handle_planesSetState(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = None

    for plane in json_data["planes"]:
        if int(plane["id"]) == request["p"]["id"]:
            plane["last_state_change_time"] = request["p"]["last_state_change_time"]
            plane["player_id"] = request["p"]["player_id"]
            plane["subcontainer_id"] = request["p"]["subcontainer_id"]
            plane["container_id"] = request["p"]["container_id"]
            plane["to_player_id"] = request["p"]["to_player_id"]
            plane["to_location_id"] = request["p"]["to_location_id"]
            plane["instantland"] = request["p"]["instantland"]
            plane["flight_status"] = request["p"]["flight_status"]
            plane["to_user_name"] = request["p"]["to_user_name"]

            flight_status = request["p"]["flight_status"]

            # Not sure if we should only do it with those states? Needs testing
            if flight_status in (
                PlaneState.WAITING_AT_HANGAR.value, # 2
                PlaneState.FUELING.value, # 9
                PlaneState.WAITING_FOR_TRANSFER_BUDDY.value, # 105
                PlaneState.WAITING_FOR_UNLOAD_BUDDY.value, # 118
                PlaneState.WAITING_FOR_TRANSFER_HOME.value, # 1005
                PlaneState.WAITING_FOR_UNLOAD_HOME.value # 1010
            ):
                plane["start_service_time"] = request["p"]["last_state_change_time"]

            # Check if the plane is a cargo plane
            if request["p"]["flight_status"] == PlaneState.WAITING_AT_HANGAR.value: # 2
                for plane_type in init_data["planeTypes"]:
                    if int(plane_type["id"]) == int(plane["plane_type_id"]):
                        contents_count = int(plane_type["capacity"])
                        load_type = plane_type["load_type"]
                        break

                if load_type == "Cargo": # Reduce air coins for starting cargo planes (amount = wares capacity)
                    subtract_resources(json_data, rpcResult, air_coins=contents_count)

            # Instantland aircash reduction
            if int(request["p"]["instantland"]) == 1 and flight_status == PlaneState.WAITING_FOR_TRANSFER_BUDDY.value: # 105
                for plane_type in init_data["planeTypes"]:
                    if int(plane_type["id"]) == int(plane["plane_type_id"]):
                        air_cash_cost = int(plane_type["quick_land_coins_cost"])
                        subtract_resources(json_data, rpcResult, air_cash=air_cash_cost)
                        break
            break