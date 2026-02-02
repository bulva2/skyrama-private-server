import time
import logging
import src.user_manager as user_manager

def handle_planesSendback(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = None

    plane_id = request["p"]["id"]
    player_id = request["p"]["player_id"]
    json2_data = None

    for plane in json_data["planes"]:
        if int(plane["id"]) == plane_id:
            plane_type_id = int(plane["plane_type_id"])

            # CashCow Respawn logic
            if player_id == 0:
                plane["flight_status"] = 77
                plane["departure_time"] = request["t"] - 450
                plane["arrival_time"] = request["t"] + 450
                plane["start_service_time"] = 0
                plane["last_state_change_time"] = request["t"]
                plane["player_id"] = 0
                plane["subcontainer_id"] = -1
                plane["container_id"] = -1
                plane["to_player_id"] = user_id
                plane["instantland"] = 0
                break
            else:
                for g in init_data["planeTypes"]:
                    if int(g["id"]) == plane_type_id:
                        buddy_points = int(g["buddy_points_yield"])
                        load_type = g["load_type"]
                        break

                buddy_id = int(plane["player_id"])

                json2_data = user_manager.load_save_by_id(buddy_id)

                # Crash fail safe, needs more testing
                if json2_data == -1 or json2_data is None:
                    logging.critical(f"Crash has been prevented!")
                    logging.critical(f"[planes_sendback] Could not load buddy data for player_id {request['p']['player_id']}: invalid json2_data")
                    json_data["planes"].remove(plane)
                    break

                # When returning a plane from a stranger, add them to the buddylist.
                in_buddy_list = False
                for buddy in json_data["buddyStuff"]["buddies"]:
                    if int(buddy["hi_player_id"]) == buddy_id:
                        in_buddy_list = True
                        break

                if not in_buddy_list:
                    json_data["buddyStuff"]["buddies"].append({"lo_player_id": str(user_id), "hi_player_id": str(buddy_id), "status": "0", "buddy_points": buddy_points, "num_hits": "0", "task_visit": "0", "num_flights_today": "0", "todays_first_flight_time": "0", "todays_first_collected_passengers_time": "0", "todays_collected_passengers": "0", "received_passengers": "0", "last_ping_time": 1674583733, "last_buddyping_time": 0, "xp": json2_data["playerData"]["xp"], "online": 0, "location_id": json2_data["playerData"]["location_id"], "username": json2_data["playerData"]["user_name"]})
                    json2_data["buddyStuff"]["buddies"].append({"lo_player_id": str(buddy_id), "hi_player_id": str(user_id), "status": "0", "buddy_points": "0", "num_hits": "0", "task_visit": "0", "num_flights_today": "0", "todays_first_flight_time": "0", "todays_first_collected_passengers_time": "0", "todays_collected_passengers": "0", "received_passengers": "0", "last_ping_time": 1674583733, "last_buddyping_time": 0, "xp": json_data["playerData"]["xp"], "online": 0, "location_id": json_data["playerData"]["location_id"], "username": json_data["playerData"]["user_name"]})
                    # 0 buddypoints for second player because they still have to handle the plane on their airport
                
                for g in json2_data["planes"]:
                  if int(g["id"]) == int(plane["fromUser_objectId"]):
                    # Returning plane should give buddy points and double xp, aircoins and cargo
                    g["buddy_points"] = buddy_points
                    g["xp"] = int(g["xp"]) * 2
                    g["air_coins"] = int(g["air_coins"]) * 2 # Cargo planes don't give these, but doesn't hurt multliplying 0 by 2 xD
                    if load_type == "Cargo":
                       g["contents_count"] = int(g["contents_count"]) * 2
                    
                    break

                json_data["planes"].remove(plane)

    if request["p"]["player_id"] != 0:
        # Also just a fail safe, needs more testing
        if json2_data != -1 and json2_data is not None and "playerData" in json2_data and "account_id" in json2_data["playerData"]:
            user_manager.modify_save_by_id(json2_data["playerData"]["account_id"], json2_data)
        else:
            logging.critical(f"[planes_sendback] Could not save buddy data for player_id {request['p']['player_id']}: invalid json2_data")
