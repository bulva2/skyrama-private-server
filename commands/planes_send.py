import logging
import random
import time
import src.userManager as userManager
from src.debug import send_webhook

def handle_planesSend(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = {}
    rpcResult["r"]["planes"] = {}

    json2_data = None

    for plane in json_data["planes"]:
        if int(plane["id"]) == request["p"]["id"]:
            plane["departure_time"] = request["p"]["departure_time"]
            plane["kerosene_boost_flag"] = request["p"]["kerosene_boost_flag"]
            plane["last_state_change_time"] = request["p"]["last_state_change_time"]
            plane["subcontainer_id"] = request["p"]["subcontainer_id"]
            plane["container_id"] = request["p"]["container_id"]
            plane["arrival_time"] = request["p"]["arrival_time"]  
            plane["flight_status"] = 77
            plane["from_user_name"] = json_data["playerData"]["user_name"]
            plane["from_location_id"] = json_data["playerData"]["location_id"]
            plane["buddy_points"] = 0
            plane["fromUser_objectId"] = int(plane["id"]) # So buddies know the right plane id
                
            plane_type_id = int(plane["plane_type_id"])
            for g in init_data["planeTypes"]:
                if int(g["id"]) == plane_type_id:
                    xp = g["xp_yield"]
                    coins = g["air_coins_yield"]
                    service_time = g["service_length"]
                    quick_start_coins_cost = g["quick_start_coins_cost"]
                    buddy_points = int(g["buddy_points_yield"])
                    load_type = g["load_type"]
                    wares_revenue = int(g["wares_revenue_capacity"])
                    contents_count = int(g["capacity"])
                    recycling_value = int(g["recyclingValue"]) # L parts drop is depending on this number (6 random sequences)
                    break
                
            # Setup xp and coins (will be doubled in planes.sendback when the plane gets serviced by the buddy)

            plane["xp"] = xp
            plane["air_coins"] = coins            

            if load_type == "Cargo":  # Cargo planes don't drop souvenirs, but cargo + L parts

                # Setup cargo
                plane["contents_count"] = contents_count
                plane["wares_revenue"] = wares_revenue

                # Setup L parts
                material_chances = init_data["materialChances"][str(recycling_value)]
                random_chance = random.random()
                chance = float(0)
                for g in material_chances:
                    chance += float(g["Chance"])
                    if chance > random_chance:
                        material_id = int(g["MaterialId"])
                        amount = random.randint(int(g["MinAmount"]), int(g["MaxAmount"]))
                        plane["drop_material"] = material_id
                        plane["drop_material_amount"] = amount
                        break
            else:
                plane["drop_material"] = 0
                plane["drop_material_amount"] = 0

                if plane.get("to_location_id") is None:
                    plane["souvenir_types_id"] = -1
                    logging.warning("planes_send: to_location_id is None! This has to be a race condition!")
                else:
                    for g in json_data["locations"]:
                        if int(g["id"]) == int(plane["to_location_id"]):
                            flight_time_seconds = 0
                            for plane_data in init_data["planeTypes"]:
                                if int(plane_data["id"]) == plane_type_id:
                                    flight_time_seconds = int(plane_data.get("flight_time", 3600))
                                    break

                            flight_time_hours = flight_time_seconds / 3600 # Seconds to hours

                            # Determine event currency drop chance based on flight time
                            if flight_time_hours >= 24:
                                event_currency_chance = 0.60
                            elif flight_time_hours >= 18:
                                event_currency_chance = 0.45
                            elif flight_time_hours >= 16:
                                event_currency_chance = 0.40
                            elif flight_time_hours >= 12:
                                event_currency_chance = 0.30
                            elif flight_time_hours >= 10:
                                event_currency_chance = 0.25
                            elif flight_time_hours >= 8:
                                event_currency_chance = 0.20
                            elif flight_time_hours >= 6:
                                event_currency_chance = 0.15
                            elif flight_time_hours >= 4:
                                event_currency_chance = 0.10
                            else:
                                event_currency_chance = 0.05  # 5% for shorter flights than 4hrs so ppl don't abuse it to farm event currency

                            # Let's go gambling! (Event currency drop)
                            if random.random() < event_currency_chance:
                                souvenir = -2  # Event currency drop yupieee
                            else:
                                # Oh dang it
                                souvenir_num = random.randint(1, 3)
                                souvenir = g[f"souvenir_types_id_{souvenir_num}"]

                            plane["souvenir_types_id"] = souvenir
                            break

            if (int(request["t"]) - int(plane["start_service_time"])) < ((int(service_time) / 3) * 2) or int(plane["start_service_time"]) == 0:
                if int(request["t"]) > int(json_data["playerData"]["aycqs_start_time"]):
                    json_data["playerData"]["air_cash"] = int(json_data["playerData"]["air_cash"]) - int(quick_start_coins_cost)

            if int(plane["to_player_id"]) != 800:  # ID 800 = NPC player
                json2_data = userManager.load_save_by_id(plane["to_player_id"])

                if json2_data == -1 or not isinstance(json2_data, dict):
                    logging.error(
                        f"planes_send: Cannot load buddy data for player {plane['to_player_id']}, plane will be treated as NPC plane"
                    )
                    send_webhook(json_data, user_id, request, additional_data=plane)
                    json2_data = None
                else:
                    last_id = int(json2_data["playerData"]["next_object_id"])
                    copy = plane.copy()
                    copy["id"] = last_id + 1
                    copy["buddy_points"] = buddy_points
                    copy["xp"] = xp * 2  # Servicing a buddy's plane gives double xp, but same amount of coins
                    copy["air_coins"] = coins

                    json2_data["planes"].append(copy)
                    json2_data["playerData"]["next_object_id"] = last_id + 1

                    userManager.modify_save_by_id(json2_data["playerData"]["account_id"], json2_data)

            rpcResult["r"]["planes"][str(request["p"]["id"])] = plane
