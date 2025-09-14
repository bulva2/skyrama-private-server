import time
from commands.buddy_getAll import run_buddy_checks
from deepmerge import always_merger

def handle_getInitState(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = str(int(time.time()))
    items_to_add_to_obj.append("consumablesTypes")
    items_to_add_to_obj.append("consumables")
    items_to_add_to_obj.append("packagesTypes")
    items_to_add_to_obj.append("planeUpgrades")
    items_to_add_to_obj.append("planeUpgradeTypes")
    items_to_add_to_obj.append("planeUpgradeCostTypes")

    # Store session time
    json_data["playerData"]["session_start_time"] = int(time.time())

    # Make CashCow appear on the radar
    if request["t"] > int(json_data["planes"][0]["arrival_time"]):
        # To-do: Restart tutorial if not completed.
        for i in json_data["planes"]:
            if int(i["id"]) == 0:
                i["departure_time"] = request["t"] - 450
                i["arrival_time"] = request["t"] + 450
                i["flight_status"] = 77 # in air
                break

    # Run buddy.getAll
    run_buddy_checks(request["t"], json_data)

    rpcResult["r"] = always_merger.merge(json_data, init_data) # Deepmerge both global init and personal user init.
    # To-do when switching to an acutal database: don't store password between the game data!!!!!!!
    