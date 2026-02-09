from src.debug import report_issue
import time

def handle_cargoshopsFillShop(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = None

    for i in json_data["cargoShops"]:
        if int(i["id"]) == int(request["p"]["shops_id"]):
            cargo_shop_types_id = int(i["cargo_shop_types_id"])
            request["p"]["cargo_shop_types_id"] = cargo_shop_types_id # Simplify the FillShop quest script
            upgrade_level = int(i["upgrade_level"])
            break

    for j in init_data["cargoShopLevels"]:
        if int(j["shop_id"]) == cargo_shop_types_id and int(j["shop_level"]) == upgrade_level:
            capacity = int(j["shop_capacity"])
            request["p"]["capacity"] = capacity # Simplify the FillShop quest script
            break

    needed_cargo_types = []
    for k in init_data["cargoTypes"]:
        if int(k["shop_id"]) == cargo_shop_types_id and int(k["shop_level"]) <= upgrade_level:
            needed_cargo_types.append(int(k["id"]))

    lowest_stock = 0
    for l in json_data["cargo"]:
        if int(l["cargo_types_id"]) in needed_cargo_types:
            if int(l["num_in_warehouse"]) > lowest_stock:
                lowest_stock = int(l["num_in_warehouse"])

    if lowest_stock == 0: # Possible cheat, disconnect user
        report_issue("warning", f"cargoshops_fillShop: User {user_id} attempted to fill cargo shop id {request['p']['shops_id']} but has no stock of needed cargo types {needed_cargo_types}, possible cheat attempt")
        rpcResult["i"] = -1
        return

    for l in json_data["cargo"]:
        if int(l["cargo_types_id"]) in needed_cargo_types:
            if lowest_stock >= capacity:
                l["num_in_shop"] = capacity
                l["num_in_warehouse"] = int(l["num_in_warehouse"]) - capacity
            elif lowest_stock < capacity and lowest_stock > 0:
                l["num_in_shop"] = lowest_stock
                l["num_in_warehouse"] = int(l["num_in_warehouse"]) - lowest_stock