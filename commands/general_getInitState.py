import time
from commands.buddy_getAll import run_buddy_checks
from deepmerge import Merger
from copy import deepcopy

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
                i["start_service_time"] = 0
                i["last_state_change_time"] = request["t"]
                i["player_id"] = 0 # cashcow id = 0
                i["subcontainer_id"] = -1
                i["container_id"] = -1
                i["to_player_id"] = user_id
                i["instantland"] = 0
                break

    # Run buddy.getAll
    run_buddy_checks(request["t"], json_data)

    merger = Merger(
        [(dict, ["merge"]), (list, ["override"]), (set, ["override"])],
        ["override"],
        ["override"]
    ) # Merge dicts, but override lists and sets (to prevent duplicating things)

    rpcResult["r"] = deepcopy(json_data)
    merger.merge(rpcResult["r"], init_data) # Deepmerge both global init and personal user init.

    # Don't send password and token to the game
    # To-do when switching to an acutal database: don't store password between the game data!!!!!!!
    del rpcResult["r"]["playerData"]["password"]
    del rpcResult["r"]["playerData"]["token"]