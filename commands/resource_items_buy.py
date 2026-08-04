import time
from src.debug import report_issue
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
        report_issue("warning", f"resource_items_buy: Level or air cash requirement not met for item {request['p']['name']}, User: {json_data['playerData']['user_name']} (ID: {user_id}). Required level: {required_level}, User level: {current_level}, Air cash cost: {air_cash_cost}, User air cash: {json_data['playerData']['air_cash']}")
        rpcResult["i"] = -1 # Possible cheat, disconnect user
        return

    if request["p"]["name"].startswith("allyoucanquickservice"):
        json_data["playerData"]["air_cash"] -= air_cash_cost
        json_data["playerData"]["aycqs_start_time"] = rpcResult["t"] + (amount * 3600) # amount = number of hours

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