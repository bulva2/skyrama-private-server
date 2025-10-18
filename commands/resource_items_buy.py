import time
from src.utils import get_level_from_xp

def handle_resourceItemsBuy(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = None

    for i in init_data["store_items"]["resources"]:
        if i["name"] == request["p"]["name"]:
            air_cash_cost = i["air_cash_cost"]
            required_level = i["required_level"]
            amount = i["amount"]

    current_level = get_level_from_xp(int(json_data["playerData"]["xp"]), init_data["playerData"]["xp_level_caps"])

    if current_level < required_level or json_data["playerData"]["air_cash"] < air_cash_cost:
        rpcResult["i"] = -1 # Possible cheat, disconnect user

    if request["p"]["name"] == "allyoucanquickservice":
        json_data["playerData"]["air_cash"] -= air_cash_cost
        json_data["playerData"]["aycqs_start_time"] = request["p"]["time"] + (amount * 3600) # amount = number of hours

    elif request["p"]["name"] == "aircoins":
        json_data["playerData"]["air_cash"] -= air_cash_cost
        json_data["playerData"]["air_coins"] += amount

    elif request["p"]["name"] == "passengers":
        json_data["playerData"]["air_cash"] -= air_cash_cost
        json_data["playerData"]["passengers"] += amount

    elif request["p"]["name"].startswith("eventcurrency"):
        json_data["playerData"]["air_cash"] -= air_cash_cost
        json_data["playerData"]["event_currency"] += amount

    elif request["p"]["name"].startswith("superfuel"):
        json_data["playerData"]["air_cash"] -= air_cash_cost
        json_data["playerData"]["super_fuel"] += amount