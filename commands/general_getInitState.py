import time
from commands.buddy_getAll import run_buddy_checks
from src.daily_goals import handle_daily_goals
from src.easy_events import get_all_easy_events
from deepmerge.merger import Merger
from copy import deepcopy

def handle_getInitState(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    items_to_add_to_obj.append("consumablesTypes")
    items_to_add_to_obj.append("consumables")
    items_to_add_to_obj.append("packagesTypes")
    items_to_add_to_obj.append("planeUpgrades")
    items_to_add_to_obj.append("planeUpgradeTypes")
    items_to_add_to_obj.append("planeUpgradeCostTypes")

    # Store session time
    json_data["playerData"]["session_start_time"] = int(time.time())

    # CashCow logic

    # Find CashCow plane in user's planes
    cashcow = None
    for plane in json_data["planes"]:
        if int(plane["id"]) == 0:
            cashcow = plane
            break
    
    # Recreate CashCow if it doesn't exist for whatever reason
    if cashcow is None:
        cashcow = {
            "souvenir_types_id": -1,
            "active_count": 1,
            "id": 0,
            "plane_type_id": 37,
            "container_id": -1,
            "subcontainer_id": -1,
            "to_player_id": user_id,
            "departure_time": request["t"] - 450,
            "arrival_time": request["t"] + 450,
            "kerosene_boost_flag": 0,
            "flight_status": 77,
            "buddy_points": 0,
            "contents_count": 5,
            "air_coins": 20,
            "xp": 0,
            "wares_revenue": 5,
            "banner_id": -1,
            "start_service_time": 0,
            "last_state_change_time": request["t"],
            "drop_consumable_id": 0,
            "drop_consumable_amount": 0,
            "instantland": 0,
            "player_id": 0,
            "from_location_id": -1,
            "from_user_name": "drone",
            "upgrade_level": 0,
            "to_location_id": -1,
            "to_user_name": "",
            "drop_material": 0,
            "drop_material_amount": 0
        }
        json_data["planes"].insert(0, cashcow)

    # Make CashCow appear on the radar again
    if request["t"] > int(cashcow["arrival_time"]):
        cashcow["departure_time"] = request["t"] - 450
        cashcow["arrival_time"] = request["t"] + 450
        cashcow["flight_status"] = 77  # in air
        cashcow["start_service_time"] = 0
        cashcow["last_state_change_time"] = request["t"]
        cashcow["player_id"] = 0  # cashcow id = 0
        cashcow["subcontainer_id"] = -1
        cashcow["container_id"] = -1
        cashcow["to_player_id"] = user_id
        cashcow["instantland"] = 0

    # Run buddy.getAll
    run_buddy_checks(request["t"], json_data)

    # Check crafting slots for completed planes (causes a visual glitch if we don't do this)
    # It's not a critical glitch, so only checking it on logging in and not on every command (for performance reasons)
    for slot in json_data.get("userCraftingSlots", []):
        if "processData" not in slot or "endtime" not in slot["processData"]:
            continue
        process_data = slot["processData"]
        time_remaining = process_data["endtime"] - int(time.time())
        if time_remaining <= 0:
            process_data["finished"] = True

    daily_goal_def = handle_daily_goals(json_data)

    merger = Merger(
        [(dict, ["merge"]), (list, ["override"]), (set, ["override"])],
        ["override"],
        ["override"]
    ) # Merge dicts, but override lists and sets (to prevent duplicating things)

    rpcResult["r"] = deepcopy(json_data)
    merger.merge(rpcResult["r"], init_data) # Deepmerge both global init and personal user init.

    if daily_goal_def is not None:
        rpcResult["r"]["dailyGoalType"] = daily_goal_def

    rpcResult["r"]["global_events"] = get_all_easy_events()

    # Don't send password and token to the game
    # To-do when switching to an acutal database: don't store password between the game data!!!!!!!
    del rpcResult["r"]["playerData"]["password"]
    del rpcResult["r"]["playerData"]["token"]