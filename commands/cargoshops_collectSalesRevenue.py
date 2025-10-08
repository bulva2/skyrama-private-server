import time

def handle_cargoshopsCollectSalesRevenue(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = None

    for i in json_data["cargoShops"]:
        if int(i["cargo_shop_types_id"]) == int(request["p"]["types_id"]):
            if i["sales_revenue"] > 0:
                json_data["playerData"]["air_coins"] += i["sales_revenue"]
                i["sales_revenue"] = 0
            break

