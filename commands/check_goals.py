import logging
from src.debug import report_issue
from src.daily_goals import _get_goal_by_id
from src.enums import PlaneState
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
    "PlaceLandsideBuilding": handle_PlaceLandsideBuilding,
    "CollectSouvenir": handle_CollectSouvenir,
    "GetAirCoins": handle_GetAirCoins,
    "PlaceWarehouse": handle_PlaceWarehouse,
    "GetCargo": handle_GetCargo,
    "PlaceCargoshop": handle_PlaceCargoshop,
    "FillShop": handle_FillShop,
    "SellProducts": handle_SellProducts,
    "StoreTerminal": handle_StoreTerminal,
    "StoreLandsideBuilding": handle_StoreLandsideBuilding
}

def next_quest(quest_seq, init_data, json_data, user_id, items_to_add_to_obj):
    current_goal_types_id = int(json_data["goals"]["goals"][quest_seq]["goal_types_id"])

    # Find the current goal
    old_goal = next((goal_type for goal_type in init_data["goalTypes"] if int(goal_type["id"]) == current_goal_types_id), None)
    
    if old_goal is None:
        report_issue("warning", f"Could not find goal type {current_goal_types_id} for quest sequence: {quest_seq}, user_id: {user_id}")
        return

    old_seq_num = int(old_goal["seq_num"])

    # Give rewards for the completed quest
    give_rewards(json_data, init_data, old_goal, items_to_add_to_obj)

    # Give reward objects
    type_id = old_goal["reward_obj_type_id"]
    type = old_goal["reward_obj_type"]

    if type is not None and type_id is not None:
        give_obj_reward(json_data, init_data, user_id, type_id, type, items_to_add_to_obj)

    type_id = old_goal["alternative_reward_obj_type_id"]
    type = old_goal["alternative_reward_obj_type"]

    if type is not None and type_id is not None:
        give_obj_reward(json_data, init_data, user_id, type_id, type, items_to_add_to_obj)

    # Find the next goal in sequence:
    # lowest seq_num that is > old_seq_num is the next quest
    next_goal = None
    for goal_type in init_data["goalTypes"]:
        if goal_type["seq_type"] == quest_seq and int(goal_type["seq_num"]) > old_seq_num:
            if next_goal is None or int(goal_type["seq_num"]) < int(next_goal["seq_num"]):
                next_goal = goal_type

    if next_goal is None:
        # Quests from this seq_type are finished
        json_data["goals"]["goals"][quest_seq] = {
            "goal_types_id": -1,
            "seq_num": -1,
            "tasks": []
        }
        return

    new_goal_id = next_goal["id"]
    smallest = int(next_goal["seq_num"])

    new_tasks = []
    for j in init_data["taskTypes"]:
        if int(j["goal_types_id"]) == int(new_goal_id):
            new_task = j
            new_task["num_completed"] = 0
            new_tasks.append(new_task)

    json_data["goals"]["goals"][quest_seq] = {
        "goal_types_id": new_goal_id,
        "seq_num": smallest,
        "tasks": new_tasks
    }

def handle_goal(request, user_id, quest_seq, items_to_add_to_obj, json_data, init_data):
    current_goal = json_data["goals"]["goals"].get(quest_seq)
    
    if current_goal is None or "tasks" not in current_goal:
        logging.error(f"No current goal or tasks found for quest sequence: {quest_seq}, user_id: {user_id}")
        return
    
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
        if quest_seq == "daily":
            if not json_data["goals"].get("daily_reward_given", False):
                daily_goal = json_data["goals"]["goals"]["daily"]
                goal_types_id = daily_goal.get("goal_types_id")
                goal_def = _get_goal_by_id(goal_types_id)
                if goal_def:
                    json_data["playerData"]["air_coins"] += goal_def.get("reward_air_coins", 0)
                    json_data["playerData"]["air_cash"] += goal_def.get("reward_air_cash", 0)
                    json_data["playerData"]["xp"] += goal_def.get("reward_xp", 0)
                    json_data["playerData"]["passengers"] += goal_def.get("reward_passengers", 0)
                    type_id = goal_def.get("reward_obj_type_id", -1)
                    type = goal_def.get("reward_obj_type", None)
                    if type_id != -1 and type:
                        give_obj_reward(json_data, init_data, user_id, type_id, type, items_to_add_to_obj)
                    # reward_cargo_capacity_upgrade (TODO: implement if needed)
                    json_data["goals"]["daily_reward_given"] = True
            return
        
        next_quest(quest_seq, init_data, json_data, user_id, items_to_add_to_obj)

def give_rewards(json_data, init_data, old_goal, items_to_add_to_obj):
    json_data["playerData"]["air_coins"] += old_goal["reward_air_coins"]
    json_data["playerData"]["air_cash"] += old_goal["reward_air_cash"]
    json_data["playerData"]["xp"] += old_goal["reward_xp"]
    json_data["playerData"]["passengers"] += old_goal["reward_passengers"]
    json_data["playerData"]["super_fuel"] += old_goal["reward_kerosene_boost"]
    json_data["playerData"]["cargo_capacity_level"] += old_goal["reward_cargo_capacity_upgrade"]
    # reward_goods and reward_map_extension are unused

    if old_goal["reward_hangar_upgrade"] > 0:
        # Check which hangar needs to be upgraded
        if old_goal["reward_obj_type"] == "Hangar":
            hangar_types_id = int(old_goal["reward_obj_type_id"])
        elif old_goal["reward_obj_type"] == "Plane":
            # Check to which hangar the plane belongs
            for plane_type in init_data["planeTypes"]:
                if plane_type["id"] == old_goal["reward_obj_type_id"]:
                    plane_size = plane_type["size"]
                    plane_type = plane_type["type"]
                    break

            for hangar_type in init_data["hangarTypes"]:
                # If regular plane, check the size as well
                if hangar_type["aircraft_type"] == plane_type and \
                    ((plane_type == "plane" and hangar_type["sml"] == plane_size) or plane_type != "plane"):
                    hangar_types_id = int(hangar_type["id"])
                    break
        else:
            hangar_types_id = int(old_goal["reward_obj_type_id"])

        for hangar in json_data["hangars"]:
            print(f"Checking hangar {hangar['id']} with type {hangar['hangar_types_id']} against required type {hangar_types_id}")
            if int(hangar["hangar_types_id"]) == hangar_types_id:
                hangar["upgrade_level"] = int(hangar["upgrade_level"]) + int(old_goal["reward_hangar_upgrade"])
                items_to_add_to_obj.append("hangars") # Most likely unhandled by the client, remove if verified
                logging.debug(f"Quest reward: Upgraded hangar {hangar['id']} by {old_goal['reward_hangar_upgrade']} levels, current level: {hangar['upgrade_level']}")
                break

def give_obj_reward(json_data, init_data, user_id, type_id, type, items_to_add_to_obj):
    if type_id != -1:
        if type == "Bay":
            json_data["bays"].append({"bay_types_id": type_id,"last_harvest_time": 0,"set_in_storage_time": "0","id": json_data["playerData"]["next_object_id"],"position_x": -100,"position_y": -100,"direction": 0,"player_id": user_id})
            json_data["playerData"]["next_object_id"] += 1

        elif type == "Plane":
            for plane_type in init_data["planeTypes"]:
                if int(plane_type["id"]) == type_id:

                    # Get container id
                    for hangar_type in init_data["hangarTypes"]:
                        if hangar_type["sml"] == plane_type["size"] and hangar_type["aircraft_type"] == plane_type["type"]:
                            hangar_type = int(hangar_type["id"])
                            break

                    for hangar in json_data["hangars"]:
                        if int(hangar["hangar_types_id"]) == hangar_type:
                            container_id = int(hangar["id"])
                            break

                    json_data["planes"].append(
                        {
                            "souvenir_types_id":-1,
                            "active_count":1,
                            "id":json_data["playerData"]["next_object_id"],
                            "plane_type_id":type_id,
                            "container_id":container_id,
                            "subcontainer_id":1,
                            "to_player_id":-1,
                            "departure_time":-1,
                            "arrival_time":-1,
                            "kerosene_boost_flag":0,
                            "flight_status": PlaneState.HANGAR.value, # 0
                            "buddy_points":plane_type["buddy_points_yield"],
                            "contents_count":plane_type["capacity"],
                            "air_coins":plane_type["air_coins_yield"],
                            "xp":plane_type["xp_yield"],
                            "wares_revenue":plane_type["wares_revenue_capacity"],
                            "banner_id":-1,
                            "start_service_time":0,
                            "last_state_change_time":0,
                            "drop_consumable_id":0,
                            "drop_consumable_amount":0,
                            "instantland":0,
                            "player_id":user_id,
                            "from_location_id":-1,
                            "from_user_name":"",
                            "upgrade_level":0
                        }
                    )
                    json_data["playerData"]["next_object_id"] += 1
                    items_to_add_to_obj.append("planes")
                    break

        elif type == "Hangar":
            json_data["hangars"].append({"hangar_types_id":type_id,"upgrade_level":"1","id":json_data["playerData"]["next_object_id"],"position_x":-100,"position_y":-100,"direction":"0","player_id":user_id})
            json_data["playerData"]["next_object_id"] += 1

        elif type == "Cargoshop":
            json_data["cargoShops"].append({"cargo_shop_types_id":type_id,"upgrade_level":"0","products_sold":"0","sales_revenue":"0","id":json_data["playerData"]["next_object_id"],"position_x":-100,"position_y":-100,"direction":"0","player_id":user_id})
            json_data["playerData"]["next_object_id"] += 1

        elif type == "Landside_Building":
            json_data["landsideBuildings"].append({"landside_building_types_id":type_id,"last_harvest_time":"0","set_in_storage_time":"0","id":json_data["playerData"]["next_object_id"],"position_x":"-100","position_y":"-100","direction":"0","player_id":user_id})
            json_data["playerData"]["next_object_id"] += 1

        elif type == "Runway":
            json_data["runways"].append({"runway_types_id":type_id,"id":json_data["playerData"]["next_object_id"],"position_x":"-100","position_y":"-100","direction":"0","player_id":user_id})
            json_data["playerData"]["next_object_id"] += 1

        elif type == "Warehouse":
            json_data["warehouses"].append({"warehouse_types_id":type_id,"id":json_data["playerData"]["next_object_id"],"position_x":"-100","position_y":"-100","direction":"0","player_id":user_id})
            json_data["playerData"]["next_object_id"] += 1