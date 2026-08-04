import time
import src.utils as utils

def handle_cargoshopsBuy(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = None

    # CHECK IF THE BUILDING IS ALREADY UNLOCKED
    # If yes: only use air coins, else only use air cash!!!
    for i in init_data["store_items"]["storeItems"]:
        if i["obj_type"] == "Cargoshop":
            if int(i["obj_type_id"]) == int(request["p"]["types_id"]):
                unlock_lvl = int(i["required_level"])
                break
      
    # Check current level based on xp
    current_xp = int(json_data["playerData"]["xp"])
    current_level = utils.get_level_from_xp(current_xp, init_data["playerData"]["xp_level_caps"])
    
    for i in init_data["cargoShopTypes"]:
        if int(i["id"]) == int(request["p"]["types_id"]):
            if i["air_coins_cost"] != 0:
                if current_level >= unlock_lvl:
                    i["air_cash_cost"] = 0
                else:
                    i["air_coins_cost"] = 0
            
            json_data["playerData"]["air_coins"] = json_data["playerData"]["air_coins"] - i["air_coins_cost"]
            json_data["playerData"]["air_cash"] = json_data["playerData"]["air_cash"] - i["air_cash_cost"]
            json_data["playerData"]["event_currency"] = json_data["playerData"]["event_currency"] - i["event_currency_cost"]
            
            json_data["cargoShops"].append({"cargo_shop_types_id": request["p"]["types_id"],"upgrade_level": "0","products_sold": 0,"sales_revenue": 0,"id": json_data["playerData"]["next_object_id"],"position_x": request["p"]["position_x"],"position_y": request["p"]["position_y"],"direction": request["p"]["direction"],"player_id": user_id})
    
            json_data["playerData"]["next_object_id"] += 1