from src.debug import report_issue
from src.plane_manager import add_plane

from src.enums import PlaneState

import random
import time
import src.user_manager as user_manager

def handle_planesSend(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = {}
    rpcResult["r"]["planes"] = {}

    receiver_data = None

    for plane in json_data["planes"]:
        if int(plane["id"]) == request["p"]["id"]:
            plane["departure_time"] = request["p"]["departure_time"]
            plane["kerosene_boost_flag"] = request["p"]["kerosene_boost_flag"]
            plane["last_state_change_time"] = request["p"]["last_state_change_time"]
            plane["subcontainer_id"] = request["p"]["subcontainer_id"]
            plane["container_id"] = request["p"]["container_id"]
            plane["arrival_time"] = request["p"]["arrival_time"]  
            plane["flight_status"] = PlaneState.FLYING_TO_BUDDY.value # 77
            plane["from_user_name"] = json_data["playerData"]["user_name"]
            plane["from_location_id"] = json_data["playerData"]["location_id"]
            plane["buddy_points"] = 0
            plane["fromUser_objectId"] = int(plane["id"]) # So buddies know the right plane id
                
            plane_type_id = int(plane["plane_type_id"])

            for plane_type in init_data["planeTypes"]:
                if int(plane_type["id"]) == plane_type_id:
                    xp = plane_type["xp_yield"]
                    coins = plane_type["air_coins_yield"]
                    buddy_points = int(plane_type["buddy_points_yield"])
                    load_type = plane_type["load_type"]
                    wares_revenue = int(plane_type["wares_revenue_capacity"])
                    contents_count = int(plane_type["capacity"])
                    recycling_value = int(plane_type["recyclingValue"]) # L parts drop is depending on this number (6 random sequences)
                    break
                
            # Setup xp and coins (will be doubled in planes.sendback when the plane gets serviced by the buddy)
            plane["xp"] = xp
            plane["air_coins"] = coins    

            location = get_location_from_id(json_data, plane["to_location_id"])

            if location is None:
                report_issue("warning", f"planes_send: Location not found for plane id {plane['id']}, User: {json_data['playerData']['user_name']}")
                rpcResult["i"] = -1
                return

            check_and_handle_continent_progress(location, json_data, init_data, user_id)

            if load_type == "Cargo":  # Cargo planes don't drop souvenirs, but cargo + L parts
                # Setup cargo
                plane["contents_count"] = contents_count
                plane["wares_revenue"] = wares_revenue

                # Setup L parts
                material_chances = init_data["materialChances"][str(recycling_value)]
                random_chance = random.random()
                chance = float(0)

                for material in material_chances:
                    chance += float(material["Chance"])
                    if chance > random_chance:
                        material_id = int(material["MaterialId"])
                        amount = random.randint(int(material["MinAmount"]), int(material["MaxAmount"]))
                        plane["drop_material"] = material_id
                        plane["drop_material_amount"] = amount
                        break
            else:
                plane["drop_material"] = 0
                plane["drop_material_amount"] = 0

                if plane.get("to_location_id") is None:
                    plane["souvenir_types_id"] = -1
                    report_issue("warning", f"planes_send: to_location_id is None for plane id {plane['id']}, User: {json_data['playerData']['user_name']}")
                    rpcResult["i"] = -1
                    return

                flight_time_seconds = 0
                for plane_data in init_data["planeTypes"]:
                    if int(plane_data["id"]) == plane_type_id:
                        flight_time_seconds = int(plane_data.get("flight_time", 3600))
                        break

                event_currency_chance = determine_event_currency_drop_chance(flight_time_seconds)
                souvenir = pick_souvenir(event_currency_chance, location)
                plane["souvenir_types_id"] = souvenir

            if int(plane["to_player_id"]) != 800:  # ID 800 = NPC player
                receiver_data = user_manager.load_save_by_id(plane["to_player_id"])

                if receiver_data == -1 or not isinstance(receiver_data, dict):
                    report_issue("error", f"planes_send: Cannot load buddy data for player {plane['to_player_id']}, plane will be treated as NPC plane")
                    receiver_data = None
                else:
                    last_id = int(receiver_data["playerData"]["next_object_id"])
                    copy = plane.copy()
                    copy["id"] = last_id + 1
                    copy["buddy_points"] = buddy_points
                    copy["xp"] = xp * 2  # Servicing a buddy's plane gives double xp, but same amount of coins
                    copy["air_coins"] = coins

                    receiver_data["planes"].append(copy)
                    receiver_data["playerData"]["next_object_id"] = last_id + 1

                    user_manager.modify_save_by_id(receiver_data["playerData"]["account_id"], receiver_data)

            rpcResult["r"]["planes"][str(request["p"]["id"])] = plane

def get_location_from_id(json_data: dict, location_id: int) -> dict | None:
    for location in json_data["locations"]:
        if int(location["id"]) == int(location_id):
            return location
    return None

def determine_event_currency_drop_chance(flight_time_seconds: int) -> float:
    flight_time_hours = flight_time_seconds / 3600

    if flight_time_hours >= 24:
        return 0.60
    elif flight_time_hours >= 18:
        return 0.45
    elif flight_time_hours >= 16:
        return 0.40
    elif flight_time_hours >= 12:
        return 0.30
    elif flight_time_hours >= 10:
        return 0.25
    elif flight_time_hours >= 8:
        return 0.20
    elif flight_time_hours >= 6:
        return 0.15
    elif flight_time_hours >= 4:
        return 0.10
    elif flight_time_hours >= 2:
        return 0.05
    else:
        return 0.01
    
def pick_souvenir(event_currency_chance: float, location: dict) -> int:
    if random.random() < event_currency_chance:
        return -2  # Event currency drop
    else:
        souvenir_num = random.randint(1, 3)
        return location[f"souvenir_types_id_{souvenir_num}"]
    
def check_and_handle_continent_progress(location: dict, json_data: dict, init_data: dict, user_id: int) -> None:
    continent_finished = _handle_continent_progress(location, json_data, init_data, user_id)

    if continent_finished:
        _handle_world_progress(json_data, init_data)

def _handle_continent_progress(location: dict, json_data: dict, init_data: dict, user_id: int) -> bool:
    if location["visited"]:
        return False
    
    location["visited"] = True
    continent_name = location["continent"]

    # Get all locations in the same continent
    continent_locations = [loc for loc in json_data["locations"] if loc["continent"] == continent_name]

    # Check if all locations in the continent have been visited
    if all(loc["visited"] for loc in continent_locations):
        for reward in init_data["unlock_rewards"]:
            if reward["region"] == continent_name:
                if reward["air_coins"] > 0:
                    json_data["playerData"]["air_coins"] += reward["air_coins"]

                if reward["reward_obj_type"] == "Landside_Building":
                    building_id = reward["reward_obj_id"]
                    
                    landside_building = {
                        "landside_building_types_id": building_id,
                        "last_harvest_time": 0,
                        "set_in_storage_time": 0,
                        "id": json_data["playerData"]["next_object_id"],
                        "position_x": -100,
                        "position_y": -100,
                        "direction": 0,
                        "player_id": user_id
                    }

                    json_data["landsideBuildings"].append(landside_building)
                    json_data["playerData"]["next_object_id"] += 1
        return True
    return False

def _handle_world_progress(json_data: dict, init_data: dict) -> None:
    if all(location["visited"] for location in json_data["locations"]):
        for reward in init_data["unlock_rewards"]:
            if reward["region"] == "world":
                if reward["air_coins"] > 0:
                    json_data["playerData"]["air_coins"] += reward["air_coins"]

                if reward["reward_obj_type"] == "Plane":
                    add_plane(json_data, reward["reward_obj_id"], json_data["playerData"]["account_id"], init_data)

