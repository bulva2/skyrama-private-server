import time

def handle_hangarsUpgrade(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = str(int(time.time()))
    rpcResult["r"] = None

    # upgrade_level = 1 = NO UPGRADE
    # upgrade_level given by request is not reliable, DO NOT USE (instead use the amount of requests)

    for i in json_data["hangars"]:
        if int(i["id"]) == int(request["p"]["id"]):
            types_id = int(i["hangar_types_id"])
            current_upgrade_level = int(i["upgrade_level"])
            i["upgrade_level"] += 1
            break

    for i in init_data["hangarTypes"]:
        if int(i["id"]) == types_id:
            costs = i["costs"]
            levels = i["levels"]
            break

    # It works. Don't ask why it does.
    i = len(levels) - 1
    while current_upgrade_level <= int(levels[i]) and i != -1:
        i -= 1

    if i+1 >= len(costs):
        i = len(costs) - 2

    air_cash_cost = int(costs[i+1])

    if json_data["playerData"]["air_cash"] < air_cash_cost:
        rpcResult["i"] = -1

    json_data["playerData"]["air_cash"] -= air_cash_cost
