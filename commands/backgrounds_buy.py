import time

def handle_backgroundsBuy(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = str(int(time.time()))
    rpcResult["r"] = None

    for i in init_data["backgroundTypes"]:
        if int(i["id"]) == int(request["p"]["background_types_id"]):
            air_coins_cost = i["air_coins_cost"]
            air_cash_cost = i["air_cash_cost"]
            event_currency_cost = i["event_currency_cost"]
    
    json_data["playerData"]["air_coins"] -= air_coins_cost
    json_data["playerData"]["air_cash"] -= air_cash_cost
    json_data["playerData"]["event_currency"] -= event_currency_cost

    for i in json_data["backgrounds"]:
        # Put the active background in storage
        if int(i["in_storage"]) == 0:
            i["in_storage"] = 1
            
        # Background is already bought, disconnect user
        if int(i["background_types_id"]) == int(request["p"]["background_types_id"]):
            rpcResult["i"] = -1
            
    json_data["backgrounds"].append({"background_types_id": request["p"]["background_types_id"],"in_storage": "0","player_id": user_id})