import time

from src.debug import report_issue

def look_for_sell_reward(init_types_data, types_id):
    for i in init_types_data:
        if int(i["id"]) == int(types_id):
            return i["air_coins_sell"] if "air_coins_sell" in i else 0
    return 0

def handle_sell(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = None

    for id in request["p"]["unique_ids"]:
        sell_reward = None

        if request["m"].startswith("bays"):
            for i in json_data["bays"]:
                if int(i["id"]) == int(id):
                    json_data["bays"].remove(i)
                    types_id = i["bay_types_id"]
                    sell_reward = look_for_sell_reward(init_data["bayTypes"], types_id)
                    break

        elif request["m"].startswith("runways"):
            for i in json_data["runways"]:
                if int(i["id"]) == int(id):
                    json_data["runways"].remove(i)
                    types_id = i["runway_types_id"]
                    sell_reward = look_for_sell_reward(init_data["runwayTypes"], types_id)
                    break

        elif request["m"].startswith("landside_buildings"):
            for i in json_data["landsideBuildings"]:
                if int(i["id"]) == int(id):
                    json_data["landsideBuildings"].remove(i)
                    types_id = i["landside_building_types_id"]
                    sell_reward = look_for_sell_reward(init_data["landsideBuildingTypes"], types_id)
                    break

        elif request["m"].startswith("terminals"):
            for i in json_data["terminals"]:
                if int(i["id"]) == int(id):
                    json_data["terminals"].remove(i)
                    types_id = i["terminal_types_id"]
                    sell_reward = look_for_sell_reward(init_data["terminalTypes"], types_id)
                    break

        if sell_reward is None:
            report_issue("warning", f"sell: User {user_id} tried to sell {request['m']} id {id}, which was not found in their save")
            continue

        json_data["playerData"]["air_coins"] += sell_reward
