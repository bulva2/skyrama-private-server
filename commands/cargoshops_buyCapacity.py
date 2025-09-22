import time

def handle_cargoshopsBuyCapacity(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = str(int(time.time()))
    rpcResult["r"] = None

    cost = init_data["cargoUpgrades"][1]["air_cash_cost"]

    if json_data["playerData"]["air_cash"] < cost:
        rpcResult["i"] = -1
        
    json_data["playerData"]["cargo_capacity_level"] += 1
    json_data["playerData"]["air_cash"] -= cost