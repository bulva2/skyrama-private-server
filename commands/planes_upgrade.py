import time
from src.utils import build_plane_upgrades

def handle_planesUpgrade(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = None
    items_to_add_to_obj.append("planes")
    items_to_add_to_obj.append("planeUpgrades")
    items_to_add_to_obj.append("consumables")

    for i in json_data["planes"]:
        if int(i["id"]) == request["p"]["id"]:
            i["upgrade_level"] = i["upgrade_level"] + 1
            current_upgrade_number = i["upgrade_level"]
            current_plane_type_id = i["plane_type_id"]
            break
        
    for i in init_data["planeUpgradeCostTypes"]:
        if current_plane_type_id in i["planeIds"]:
            for j in i["costs"][str(current_upgrade_number)]:
                if j["type"] == "consumable": # Reduce tuning parts
                    json_data["consumables"][j["id"]] = json_data["consumables"][j["id"]] - j["amount"]
            
                if j["type"] == "currency": # Not checking for id, as only coins are possible?
                    json_data["playerData"]["air_coins"] = json_data["playerData"]["air_coins"] - j["amount"]
            break
      
    # planeUpgrades isn't a persisted field (no DB column for it), so it has to be
    # rebuilt from upgrade_level every time rather than appended to across requests.
    json_data["planeUpgrades"] = build_plane_upgrades(json_data["planes"], init_data)

    # Success, we have to return the planeUpgrades object, else the client gets stuck
    rpcResult["r"] = json_data["planeUpgrades"]