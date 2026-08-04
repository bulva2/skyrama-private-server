from src.enums import PlaneState
import time

def handle_luckyLuggageSpin(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = None
    items_to_add_to_obj.append("souvenirCollections")
    
    if json_data["lucky_luggage_data"]["free_spins"] > 0:
        json_data["lucky_luggage_data"]["free_spins"] = json_data["lucky_luggage_data"]["free_spins"] - 1
        json_data["playerData"]["lucky_luggage_free_spins"] = json_data["lucky_luggage_data"]["free_spins"] # Is this being used by the game?
    else:
        json_data["playerData"]["air_cash"] = json_data["playerData"]["air_cash"] - int(json_data["lucky_luggage_data"]["paid_spin_cost"])
      
    json_data["lucky_luggage_data"]["spins_taken"] = "{:05d}".format(int(json_data["lucky_luggage_data"]["spins_taken"]) + 1) # Adding leading 0's so it becomes 5 digits. Why? Have to figure out :)
    json_data["playerData"]["lucky_luggage_spins_taken"] = json_data["lucky_luggage_data"]["spins_taken"] # Is this being used by the game?
    
    probSum = 0
    for i in json_data["lucky_luggage_data"]["prizes"]:
        if int(i["id"]) == int(request["p"]["id"]):
            if int(request["p"]["rand"]) >= probSum and int(request["p"]["rand"]) < (probSum + int(i["probability"])): # Check for possible cheat
          
                # GIVE RESOURCES REWARDS
                json_data["playerData"]["air_coins"] += int(i["prize_air_coins"])
                json_data["playerData"]["air_cash"] += int(i["prize_air_cash"])
                json_data["playerData"]["passengers"] += int(i["prize_passengers"])
                json_data["playerData"]["xp"] += int(i["prize_xp"])
          
                # GIVE PLANE REWARD: TO TEST (currently no rewards like this activated)
                if i["prize_obj_type"] == "Plane":
                    for j in json_data["planeTypes"]:
                        if int(j["id"]) == i["prize_obj_type_id"]:
                            if j["size"] == "Small": # To-do when adding new rewards that are not small planes!!!
                                hangar_types_id = 1
                                buddy_points = j["buddy_points_yield"]
                                contents_count = j["capacity"]
                                air_coins = j["air_coins_yield"]
                                xp = j["xp_yield"]
                                wares_revenue = j["wares_revenue_capacity"]
                    for g in json_data["hangars"]:
                        if int(g["hangar_types_id"]) == hangar_types_id:
                            container_id = int(g["id"])
                            g["upgrade_level"] += 1 # Add free new hangar spot
                
                    json_data["planes"].append(
              {
                "souvenir_types_id": -1,
                "active_count": 1,
                "id": json_data["playerData"]["next_object_id"],
                "plane_type_id": i["prize_obj_type_id"],"container_id":container_id,
                "subcontainer_id": 1,
                "to_player_id": -1,
                "departure_time": -1,
                "arrival_time": -1,
                "kerosene_boost_flag": "0",
                "flight_status": PlaneState.HANGAR.value, # 0
                "buddy_points": buddy_points,
                "contents_count": contents_count,
                "air_coins": air_coins,
                "xp": xp,
                "wares_revenue": wares_revenue,
                "banner_id": "-1",
                "start_service_time": "0",
                "last_state_change_time": "0",
                "drop_consumable_id": "0",
                "drop_consumable_amount": "0",
                "instantland": 0,
                "player_id": user_id,
                "from_location_id": -1,
                "from_user_name": "",
                "upgrade_level": 0
              }
            )
          
                # GIVE SOUVENIR REWARD
                if i["prize_obj_type"] == "Souvenir":
                    for j in json_data["souvenirCollections"]:
                        if int(j["id"]) == 1: # The Plane Parts collection for the Rama-Falcon
                            for g in j["items"]:
                                if int(g["type_id"]) == int(i["prize_obj_type_id"]):
                                    g["num"] += 1
                    
                # GIVE LANDSIDE BUILDING REWARD
                if i["prize_obj_type"] == "Landside_Building":
                    # To-do: add terminals, only works for landside buildings right now (or would that reward type be called "Terminals"???)
                    json_data["landsideBuildings"].append({"landside_building_types_id":int(i["prize_obj_type_id"]),"last_harvest_time":"0","set_in_storage_time":-1,"id":json_data["playerData"]["next_object_id"],"position_x":"-100","position_y":"-100","direction":"0","player_id":user_id})
                    json_data["playerData"]["next_object_id"] += 1
            
        probSum = probSum + int(i["probability"])