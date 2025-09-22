import logging
from commands.goals import *

available_task_types = {
    "LandPlane": handle_LandPlane,
    "PlaceBay": handle_PlaceBay,
    "ReturnPlane": handle_ReturnPlane,
    "BuyPlane": handle_BuyPlane,
    "SendPlane": handle_SendPlane,
    "QuickStartPlane": handle_QuickStartPlane,
    "PlaceTerminal": handle_PlaceTerminal,
    "GetPassengers": handle_GetPassengers,
    "BuyBay": handle_BuyBay,
    "BuyLandsideBuilding": handle_BuyLandsideBuilding,
    "CollectSouvenir": handle_CollectSouvenir,
    "GetAirCoins": handle_GetAirCoins,
    "PlaceWarehouse": handle_PlaceWarehouse,
    "GetCargo": handle_GetCargo,
    "PlaceCargoshop": handle_PlaceCargoshop,
    "FillShop": handle_FillShop,
    "SellProducts": handle_SellProducts
}


def give_reward(json_data, init_data, user_id, type_id, type, items_to_add_to_obj):
    if type_id != -1:
        if type == "Bay":
            json_data["bays"].append({"bay_types_id": type_id,"last_harvest_time": 0,"set_in_storage_time": "0","id": json_data["playerData"]["next_object_id"],"position_x": -100,"position_y": -100,"direction": 0,"player_id": user_id})
            json_data["playerData"]["next_object_id"] = int(json_data["playerData"]["next_object_id"]) + 1

        elif type == "Plane":
            for h in init_data["planeTypes"]:
                if int(h["id"]) == type_id:

                    # Add hangar slot + get container id
                    for k in init_data["hangarTypes"]:
                        if k["sml"] == h["size"] and k["aircraft_type"] == h["type"]:
                            hangar_type = int(k["id"])
                            break
                    for k in json_data["hangars"]:
                        if int(k["hangar_types_id"]) == hangar_type:
                            k["upgrade_level"] = int(k["upgrade_level"]) + 1
                            items_to_add_to_obj.append("hangars")
                            container_id = int(k["id"])
                            break



                    json_data["planes"].append({"souvenir_types_id":-1,"active_count":1,"id":json_data["playerData"]["next_object_id"],"plane_type_id":type_id,"container_id":container_id,"subcontainer_id":1,"to_player_id":-1,"departure_time":-1,"arrival_time":-1,"kerosene_boost_flag":"0","flight_status":"77","buddy_points":h["buddy_points_yield"],"contents_count":h["capacity"],"air_coins":h["air_coins_yield"],"xp":h["xp_yield"],"wares_revenue":h["wares_revenue_capacity"],"banner_id":"-1","start_service_time":"0","last_state_change_time":"0","drop_consumable_id":"0","drop_consumable_amount":"0","instantland":0,"player_id":user_id,"from_location_id":-1,"from_user_name":"drone","upgrade_level":0})
                    json_data["playerData"]["next_object_id"] = int(json_data["playerData"]["next_object_id"]) + 1
                    break



        elif type == "Hangar":
            json_data["hangars"].append({"hangar_types_id":type_id,"upgrade_level":"1","id":json_data["playerData"]["next_object_id"],"position_x":-100,"position_y":-100,"direction":"0","player_id":user_id})
            json_data["playerData"]["next_object_id"] = int(json_data["playerData"]["next_object_id"]) + 1



        elif type == "Cargoshop":
            json_data["cargoShops"].append({"cargo_shop_types_id":type_id,"upgrade_level":"0","products_sold":"0","sales_revenue":"0","id":json_data["playerData"]["next_object_id"],"position_x":-100,"position_y":-100,"direction":"0","player_id":user_id})
            json_data["playerData"]["next_object_id"] = int(json_data["playerData"]["next_object_id"]) + 1



        elif type == "Landside_Building":
            json_data["landsideBuildings"].append({"landside_building_types_id":type_id,"last_harvest_time":"0","set_in_storage_time":"0","id":json_data["playerData"]["next_object_id"],"position_x":"-100","position_y":"-100","direction":"0","player_id":user_id})
            json_data["playerData"]["next_object_id"] = int(json_data["playerData"]["next_object_id"]) + 1



        elif type == "Runway":
            json_data["runways"].append({"runway_types_id":type_id,"id":json_data["playerData"]["next_object_id"],"position_x":"-100","position_y":"-100","direction":"0","player_id":user_id})
            json_data["playerData"]["next_object_id"] = int(json_data["playerData"]["next_object_id"]) + 1



        elif type == "Warehouse":
            json_data["warehouses"].append({"warehouse_types_id":type_id,"id":json_data["playerData"]["next_object_id"],"position_x":"-100","position_y":"-100","direction":"0","player_id":user_id})
            json_data["playerData"]["next_object_id"] = int(json_data["playerData"]["next_object_id"]) + 1

    return json_data

def next_quest(quest_seq, init_data, json_data, user_id, items_to_add_to_obj):
    g = 0
    for j in init_data["goalTypes"]:
        if int(j["id"]) == int(json_data["goals"]["goals"][quest_seq]["goal_types_id"]):
            old_seq_num = int(j["seq_num"])

            # Check for next quest in sequence
            higher_seq_nums = []
            for l in init_data["goalTypes"]:
                if int(l["seq_num"]) > old_seq_num:
                    if l["seq_type"] == quest_seq:
                        higher_seq_nums.append(int(l["seq_num"]))
                
            smallest = min(higher_seq_nums)

            for l in init_data["goalTypes"]: # Looping 3 times: probably a more efficient way: to-do
                if int(l["seq_num"]) == smallest:
                    if l["seq_type"] == quest_seq:
                        new_goal_id = l["id"]
                        break

            json_data["playerData"]["air_coins"] += j["reward_air_coins"]
            json_data["playerData"]["air_cash"] += j["reward_air_cash"]
            json_data["playerData"]["xp"] += j["reward_xp"]
            json_data["playerData"]["passengers"] += j["reward_passengers"]
            json_data["playerData"]["super_fuel"] += j["reward_kerosene_boost"]

            # reward_goods and reward_map_extension are unused

            if j["reward_hangar_upgrade"] > 0:
                if j["reward_obj_type"] == "Hangar":
                    for h in json_data["hangarTypes"]:
                        if int(h["id"]) == j["reward_obj_type_id"]:
                            h["capacity"] += int(j["reward_hangar_upgrade"])
                            items_to_add_to_obj.append("hangars")
                            logging.debug(f"Quest reward: Upgraded hangar {h['id']} by {j['reward_hangar_upgrade']} levels, current level: {h['capacity']}")
                            break
                else:
                    json_data["hangarTypes"][0]["capacity"] += int(j["reward_hangar_upgrade"])
                    items_to_add_to_obj.append("hangars")
                    logging.debug(f"Quest reward: Upgraded first hangar by {j['reward_hangar_upgrade']} levels, current level: {json_data['hangarTypes'][0]['capacity']}")

            # reward_cargo_capacity_upgrade: Where to change this?


            ################
            # Give objects #
            ################

            type_id = j["reward_obj_type_id"]
            type = j["reward_obj_type"]
            json_data = give_reward(json_data, init_data, user_id, type_id, type, items_to_add_to_obj)

            type_id = j["alternative_reward_obj_type_id"]
            type = j["alternative_reward_obj_type"]
            json_data = give_reward(json_data, init_data, user_id, type_id, type, items_to_add_to_obj)

            break
        g = g + 1
    g = 0
    new_tasks = []
    for j in init_data["taskTypes"]:
        if int(j["goal_types_id"]) == int(new_goal_id):
            new_task = j
            new_task["num_completed"] = 0
            new_tasks.append(new_task)
        g = g + 1
    json_data["goals"]["goals"][quest_seq] = {}
    json_data["goals"]["goals"][quest_seq]["goal_types_id"] = new_goal_id
    json_data["goals"]["goals"][quest_seq]["seq_num"] = smallest
    json_data["goals"]["goals"][quest_seq]["tasks"] = []
    json_data["goals"]["goals"][quest_seq]["tasks"] = new_tasks
    return json_data

def handle_goal(request, user_id, quest_seq, items_to_add_to_obj, json_data, init_data):
    current_goal = json_data["goals"]["goals"][quest_seq]
    num_tasks_completed = 0

    i = 0
    for task in current_goal["tasks"]:
        if task["user_action"] in available_task_types:
            handler = available_task_types[task["user_action"]]
            json_data = handler(request, user_id, json_data, task, i, init_data, quest_seq)


        if json_data["goals"]["goals"][quest_seq]["tasks"][i]["num_completed"] >= json_data["goals"]["goals"][quest_seq]["tasks"][i]["num_required"]:
            num_tasks_completed = num_tasks_completed + 1
        i = i + 1
        
    if num_tasks_completed == len(json_data["goals"]["goals"][quest_seq]["tasks"]):
        # QUEST COMPLETED, GIVE REWARDS AND START NEW QUEST
        json_data = next_quest(quest_seq, init_data, json_data, user_id, items_to_add_to_obj)