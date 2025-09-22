import time

def look_for_sell_reward(init_types_data, types_id):
    for i in init_types_data:
        if int(i["id"]) == int(types_id):
            if "air_coins_sell" in i:
                return i["air_coins_sell"]
            else:
                return 0

def handle_sell(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = str(int(time.time()))
    rpcResult["r"] = None

    for id in request["p"]["unique_ids"]:
        if request["m"].startswith("bays"):
            for i in json_data["bays"]:
                if int(i["id"]) == int(id):
                    json_data["bays"].remove(i)
                    types_id = i["bay_types_id"]
                    sell_reward = look_for_sell_reward(init_data["bayTypes"], types_id)

        elif request["m"].startswith("runways"):
            for i in json_data["runways"]:
                if int(i["id"]) == int(id):
                    json_data["runways"].remove(i)
                    types_id = i["runway_types_id"]
                    sell_reward = look_for_sell_reward(init_data["runwayTypes"], types_id)

        elif request["m"].startswith("landside_buildings"):
            for i in json_data["landsideBuildings"]:
                if int(i["id"]) == int(id):
                    json_data["runways"].remove(i)
                    types_id = i["landside_building_types_id"]
                    sell_reward = look_for_sell_reward(init_data["landsideBuildingTypes"], types_id)

        elif request["m"].startswith("terminals"):
            for i in json_data["terminals"]:
                if int(i["id"]) == int(id):
                    json_data["terminals"].remove(i)
                    types_id = i["terminal_types_id"]
                    sell_reward = look_for_sell_reward(init_data["terminalTypes"], types_id)


        json_data["playerData"]["air_coins"] += sell_reward