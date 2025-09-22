import time
import src.utils as utils

def handle_mapExpansionsBuy(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = str(int(time.time()))
    rpcResult["r"] = None

    # Check current level based on xp
    current_xp = int(json_data["playerData"]["xp"])
    current_level = utils.get_level_from_xp(current_xp, init_data["playerData"]["xp_level_caps"])

    for i in init_data["map_extensions"]:
        if int(i["grid_size"]) == int(request["p"]["grid_size"]):
            if current_level >= int(i["level"]):
                json_data["playerData"]["air_coins"] = json_data["playerData"]["air_coins"] - i["air_coins_cost"]
            else:
                json_data["playerData"]["air_cash"] = json_data["playerData"]["air_cash"] - i["air_cash_cost"]

            json_data["playerData"]["grid_size"] = int(i["grid_size"])
            break

            
    