from src.debug import report_issue
import time

def handle_hangarsUpgrade(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = None
    items_to_add_to_obj.append("hangars")

    # upgrade_level = 1 = NO UPGRADE
    # upgrade_level given by request is not reliable, DO NOT USE (instead use the amount of requests)

    hangar_to_upgrade = None
    for i in json_data["hangars"]:
        if int(i["id"]) == int(request["p"]["id"]):
            hangar_to_upgrade = i
            types_id = int(i["hangar_types_id"])
            current_upgrade_level = int(i["upgrade_level"])
            break

    if hangar_to_upgrade is None:
        rpcResult["i"] = -1
        return

    for i in init_data["hangarTypes"]:
        if int(i["id"]) == types_id:
            costs = i["costs"]
            levels = i["levels"]
            break

    # It works. Don't ask why it does.
    i = len(levels) - 1
    while i != -1 and current_upgrade_level <= int(levels[i]):
        i -= 1

    if i+1 >= len(costs):
        i = len(costs) - 2

    air_cash_cost = int(costs[i+1])

    if json_data["playerData"]["air_cash"] < air_cash_cost:
        report_issue("warning", f"hangars_upgrade: User {user_id} attempted to upgrade hangar id {request['p']['id']} to upgrade level {current_upgrade_level + 1} but has insufficient air cash ({json_data['playerData']['air_cash']}), possible cheat attempt")
        rpcResult["i"] = -1
        return

    json_data["playerData"]["air_cash"] -= air_cash_cost
    hangar_to_upgrade["upgrade_level"] = int(hangar_to_upgrade["upgrade_level"]) + 1

    rpcResult["r"] = 0
    