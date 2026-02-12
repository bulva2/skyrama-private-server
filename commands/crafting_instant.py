from src.debug import report_issue
from src.utils import subtract_resources, get_crafting_level_from_xp
from src.enums import PlaneState
import logging
import time

def handle_craftingInstant(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = False

    p = request["p"]
    found = False

    for slot in json_data.get("userCraftingSlots", {}):
        if slot["slotId"] == int(p["slotId"]):
            process_data = slot.get("processData", -1)

            if process_data == -1:
                report_issue("warning", f"crafting_instant: processData is -1 for user {user_id} in craftingInstant command")
                rpcResult["i"] = -1
                return

            # Prevent cheating by injecting different planeId
            if p["planeId"] != process_data["itemId"]:
                report_issue("warning", f"crafting_instant: User {user_id} tried to instantly collect crafting for item {p['planeId']}, but processData has itemId {process_data['itemId']}, possible cheat attempt")
                rpcResult["i"] = -1
                return
            
            # Calculate the price of the skip 
            # (We start at 48 aircoins and deduct 1 for every 30min)
            time_remaining = process_data["endtime"] - int(time.time())
            skip_cost = max(1, min(48, (time_remaining // 1800) + 1))

            subtract_resources(json_data, rpcResult, air_cash=skip_cost)
            logging.debug(f"Deducted {skip_cost} air coins for crafting skip for user {user_id}")

            slot["processData"] = []
            slot["processId"] = 0

            found = True
            break

    if not found:
        report_issue("warning", f"crafting_instant: No active crafting slot found for user {user_id} in craftingInstant command")
        rpcResult["i"] = -1
        return
    
    currentCraftings = json_data.get("userCurrentCraftings", -1)

    if currentCraftings == -1:
        report_issue("warning", f"crafting_instant: userCurrentCraftings is -1 for user {user_id} in craftingInstant command")
        rpcResult["i"] = -1
        return
    
    # To-do: double-check if hangar has the capacity
    hangar_id = None
    for hangar in json_data["hangars"]:
        if int(hangar["hangar_types_id"]) == 5: # 5 = Large hangar
            hangar_id = hangar["id"]
            break
    if hangar_id is None:
        report_issue("error", f"crafting_instant: Large hangar not found for user {user_id} in craftingInstant command")
        rpcResult["i"] = -1
        return

    for i in init_data["planeTypes"]:
        if int(i["id"]) == int(p["planeId"]):
            json_data["planes"].append(
                {
                    "souvenir_types_id":-1,
                    "active_count":1,
                    "id":json_data["playerData"]["next_object_id"],
                    "plane_type_id":p["planeId"],
                    "container_id": hangar_id,
                    "subcontainer_id":1, # Hangar has no subcontainers, so just 1 (i think that's what it means?)
                    "to_player_id":-1,
                    "departure_time":-1,
                    "arrival_time":-1,
                    "kerosene_boost_flag":"0",
                    "flight_status": PlaneState.HANGAR.value, # 0,
                    "buddy_points":i["buddy_points_yield"],
                    "contents_count":i["capacity"],
                    "air_coins":i["air_coins_yield"],
                    "xp":i["xp_yield"],
                    "wares_revenue":i["wares_revenue_capacity"],
                    "banner_id":"-1",
                    "start_service_time":"0",
                    "last_state_change_time":"0",
                    "drop_consumable_id":"0",
                    "drop_consumable_amount":"0",
                    "instantland":0,
                    "player_id":user_id,
                    "from_location_id":-1,
                    "from_user_name":"",
                    "upgrade_level":0
            }
        )
    
    currentCraftings.pop(str(p["planeId"]), None)

    # Calculate xp
    # Got this data from the German FAQs, can't seem to find them in the config as well
    crafting_level = json_data["playerData"]["crafting_level"]
    if crafting_level == 0: # level 1 in-game
        crafting_xp_per_craft = 5
    elif crafting_level == 1:
        crafting_xp_per_craft = 8
    elif crafting_level == 2:
        crafting_xp_per_craft = 10
    elif crafting_level == 3:
        crafting_xp_per_craft = 15
    elif crafting_level == 4:
        crafting_xp_per_craft = 20
    else:
        crafting_xp_per_craft = 5 # Fallback to fewest xp, just in case

    json_data["playerData"]["crafting_totalXP"] += crafting_xp_per_craft

    # Don't go over the xp limit (causes weird visual glitches)
    if json_data["playerData"]["crafting_totalXP"] > 3850: # All the level caps added = total xp for the end of the maximum level
        json_data["playerData"]["crafting_totalXP"] = 3850
    # To prevent issues: recalculate everything except total xp
    level_calculation = get_crafting_level_from_xp(json_data["playerData"]["crafting_totalXP"], init_data["playerData"]["crafting_level_caps"])
    
    json_data["playerData"]["crafting_level"] = level_calculation[0]
    json_data["playerData"]["crafting_levelXP"] = level_calculation[1]
    json_data["playerData"]["crafting_levelCap"] = level_calculation[2]
    json_data["playerData"]["next_object_id"] += 1

    rpcResult["r"] = {
        "status": True, 
        "result": {
            "craftingXp": crafting_xp_per_craft,
            "itemId": p["planeId"]
        },
        "slotId": p["slotId"],
        "slotType": p["slotType"],
        "processType": "crafting"
    }
