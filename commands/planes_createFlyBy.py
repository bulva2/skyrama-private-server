from src.enums import PlaneState
import time


def handle_planesCreateFlyBy(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = None

    for i in init_data["flybyTypes"]:
        if int(i["id"]) == int(request["p"]["banner_id"]):
            json_data["playerData"]["air_coins"] = json_data["playerData"]["air_coins"] - i["air_coins_cost"]
            json_data["playerData"]["air_cash"] = json_data["playerData"]["air_cash"] - i["air_cash_cost"]
            json_data["playerData"]["event_currency"] = json_data["playerData"]["event_currency"] - i["event_currency_cost"]

            json_data["planes"].append(
                {
                    "souvenir_types_id": -1,
                    "active_count": 1,
                    "id": json_data["playerData"]["next_object_id"],
                    "plane_type_id": request["p"]["typeId"],
                    "container_id": request["p"]["container_id"],
                    "subcontainer_id": request["p"]["subcontainer_id"],
                    "to_player_id": request["p"]["to_player_id"],
                    "departure_time": -1,
                    "arrival_time": -1,
                    "kerosene_boost_flag": "0",
                    "flight_status": PlaneState.FLY_BY_HOME.value, # 19
                    "buddy_points": 0,
                    "contents_count": 0,
                    "air_coins": 0,
                    "xp": 0,
                    "wares_revenue": 0,
                    "banner_id": request["p"]["banner_id"],
                    "start_service_time": "0",
                    "last_state_change_time": "0",
                    "drop_consumable_id": "0",
                    "drop_consumable_amount": "0",
                    "instantland": 0,
                    "player_id": user_id,
                    "from_location_id": json_data["playerData"]["location_id"],
                    "from_user_name": json_data["playerData"]["user_name"],
                    "upgrade_level": 0,
                    "banner_text": request["p"]["banner_text"]
                }
            )

            json_data["playerData"]["next_object_id"] = int(json_data["playerData"]["next_object_id"]) + 1
            break
