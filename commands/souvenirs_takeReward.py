import time

def handle_souvenirsTakeReward(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = None

    collection = request["p"]["collection_types_id"]

    for c in json_data["souvenirCollections"]:
        if c["id"] == collection:
            reward = c["reward"]
            
            # Handle currency rewards
            if reward["air_cash"] is not None and reward["air_cash"] > 0:
                json_data["playerData"]["air_cash"] += reward["air_cash"]
            if reward["air_coins"] is not None and reward["air_coins"] > 0:
                json_data["playerData"]["air_coins"] += reward["air_coins"]
            
            # Handle resource rewards
            if reward["passengers"] is not None and reward["passengers"] > 0:
                json_data["playerData"]["passengers"] += reward["passengers"]
            if reward["cargo"] is not None and reward["cargo"] > 0:
                json_data["playerData"]["cargo"] += reward["cargo"]
            if reward["xp"] is not None and reward["xp"] > 0:
                json_data["playerData"]["xp"] += reward["xp"]
            
            # Handle boost rewards
            if reward["kerosene_boost"] is not None and reward["kerosene_boost"] > 0:
                json_data["playerData"]["super_fuel"] += reward["kerosene_boost"]
            
            # TO-DO: Handle plane rewards
            # if reward["obj_type"] is not None:
            #     if reward["obj_type"] == "Plane":
            #         json_data["planes"].append(
            #             {
            #                 "souvenir_types_id":-1,
            #                 "active_count":1,
            #                 "id":json_data["playerData"]["next_object_id"],
            #                 "plane_type_id":1058, # The plane from lucky luggage
            #                 "container_id":-1,
            #                 "subcontainer_id":-1,
            #                 "to_player_id":-1,
            #                 "departure_time":-1,
            #                 "arrival_time":-1,
            #                 "kerosene_boost_flag":"0",
            #                 "flight_status":"77",
            #                 "buddy_points":0,
            #                 "contents_count":0,
            #                 "air_coins":0,
            #                 "xp":0,
            #                 "wares_revenue":0,
            #                 "banner_id":"-1",
            #                 "start_service_time":"0",
            #                 "last_state_change_time":"0",
            #                 "drop_consumable_id":"0",
            #                 "drop_consumable_amount":"0",
            #                 "instantland":0,
            #                 "player_id":user_id,
            #                 "from_location_id":-1,
            #                 "from_user_name":"drone",
            #                 "upgrade_level":0
            #             }
            #         )
            #         json_data["playerData"]["next_object_id"] += 1
            break