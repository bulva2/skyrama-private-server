import time

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

            # To-do: clean up code + check ramacopters/waterplanes
            # 2 = getting out of the hangar
            # 1005 = landed, plane still on runway (own plane)
            # 105 = landed, plane still on runway (buddy plane)
            # others: don't remember
            if request["p"]["flight_status"] == 118 or request["p"]["flight_status"] == 1010 or request["p"]["flight_status"] == 9 or request["p"]["flight_status"] == 2 or request["p"]["flight_status"] == 1005 or request["p"]["flight_status"] == 105:
                plane["start_service_time"] = request["p"]["last_state_change_time"]

            # Check if cargo plane
            if request["p"]["flight_status"] == 2:
                for k in init_data["planeTypes"]:
                    if int(k["id"]) == int(plane["plane_type_id"]):
                        contents_count = int(k["capacity"])
                        load_type = k["load_type"]
                        break
                if load_type == "Cargo": # Reduce air coins for starting cargo planes (amount = wares capacity)
                    json_data["playerData"]["air_coins"] -= contents_count

            # Reduce aircash if buddy plane is landed instantly
            if int(request["p"]["instantland"]) == 1:
                if request["p"]["flight_status"] == 105:
                    for g in init_data["planeTypes"]:
                        if int(g["id"]) == int(plane["plane_type_id"]):
                            air_cash_cost = int(g["quick_land_coins_cost"])
                            json_data["playerData"]["air_cash"] = int(json_data["playerData"]["air_cash"]) - air_cash_cost
                            break

            break