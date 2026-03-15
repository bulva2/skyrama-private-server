import time
import src.utils as utils

def handle_terminalsBuy(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = None

    terminal = {}
    terminal["terminal_types_id"] = request["p"]["types_id"]
    terminal["last_harvest_time"] = request["p"]["last_harvest_time"]
    terminal["set_in_storage_time"] = request["p"]["set_in_storage_time"]
    terminal["id"] = request["p"]["id"]
    terminal["position_x"] = request["p"]["position_x"]
    terminal["position_y"] = request["p"]["position_y"]
    terminal["direction"] = request["p"]["direction"]
    terminal["player_id"] = user_id

    json_data["terminals"].append(terminal)
    
    # CHECK IF THE BUILDING IS ALREADY UNLOCKED
    # If yes: only use air coins, else only use air cash!!!
    for i in init_data["store_items"]["storeItems"]:
      if i["obj_type"] == "Terminal":
        if int(i["obj_type_id"]) == int(request["p"]["types_id"]):
          unlock_lvl = int(i["required_level"])
          break
      
    # Check current level based on xp
    current_xp = int(json_data["playerData"]["xp"])
    current_level = utils.get_level_from_xp(current_xp, init_data["playerData"]["xp_level_caps"])

    if request["p"]["influenceableType"]["air_coins_cost"] != 0:
      if current_level >= unlock_lvl:
        request["p"]["influenceableType"]["air_cash_cost"] = 0
      else:
        request["p"]["influenceableType"]["air_coins_cost"] = 0

    json_data["playerData"]["air_coins"] = json_data["playerData"]["air_coins"] - request["p"]["influenceableType"]["air_coins_cost"]
    json_data["playerData"]["air_cash"] = json_data["playerData"]["air_cash"] - request["p"]["influenceableType"]["air_cash_cost"]
    json_data["playerData"]["event_currency"] = json_data["playerData"]["event_currency"] - request["p"]["influenceableType"]["event_currency_cost"]

    json_data["playerData"]["next_object_id"] += 1