from src.utils import subtract_resources
import time

def handle_cargoshopsBuyCapacity(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = None

    cost = init_data["cargoUpgrades"][1]["air_cash_cost"]
    subtract_resources(json_data, rpcResult, air_cash=cost)
        
    json_data["playerData"]["cargo_capacity_level"] += 1