import time
import logging

def handle_hangarsBuy(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = None

    for i in init_data["hangarTypes"]:
        if int(i["id"]) == int(request["p"]["types_id"]):
            logging.debug(f"Purchasing hangar type ID {request['p']['types_id']} for user {user_id}")
            if i["air_coins_cost"] != 0:
                json_data["playerData"]["air_coins"] -= i["air_coins_cost"]
            elif i["air_cash_cost"] != 0:
                json_data["playerData"]["air_cash"] -= i["air_cash_cost"]
            elif i["event_currency_cost"] != 0:
                json_data["playerData"]["event_currency"] -= i["event_currency_cost"]
            
            json_data["hangars"].append({
                "hangar_types_id": request["p"]["types_id"],
                "upgrade_level": 1,
                "id": json_data["playerData"]["next_object_id"],
                "position_x": request["p"]["position_x"],
                "position_y": request["p"]["position_y"],
                "direction": request["p"]["direction"],
                "player_id": user_id
            })

            logging.debug(f"Added hangar with ID {json_data['playerData']['next_object_id']} for user {user_id}")
            json_data["playerData"]["next_object_id"] += 1
            break
