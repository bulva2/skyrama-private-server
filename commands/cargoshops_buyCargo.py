import time

def calculate_cargo_capacity(level, init_data):
    start_capacity = init_data["cargoUpgrades"][0]["increment"]
    increment_capacity = init_data["cargoUpgrades"][1]["increment"]
    capacity = start_capacity
    # level 1 = start capacity
    # every next level = +60
    for i in range(level - 1):
        capacity += increment_capacity
        
    return capacity

def handle_cargoshopsBuyCargo(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    # Buying cargo in the warehouse: 100 cargo for 1 aircash

    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = None

    for i in init_data["cargoTypes"]:
        if int(i["id"]) == request["p"]["cargo_types_id"]:
            amount = i["sale_amount"]
            cost = i["cost"]
            break

    for i in json_data["cargo"]:
        if i["cargo_types_id"] == request["p"]["cargo_types_id"]:
            cargo_capacity = calculate_cargo_capacity(json_data["playerData"]["cargo_capacity_level"], init_data)
            if (i["num_in_warehouse"] + amount) > cargo_capacity or json_data["playerData"]["air_cash"] < cost:
                # Possibly a cheat, disconnect the user
                rpcResult["i"] = -1
            else:
                    i["num_in_warehouse"] += amount
                    json_data["playerData"]["air_cash"] -= cost
            break