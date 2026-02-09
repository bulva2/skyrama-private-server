import time
from src.debug import report_issue

def handle_craftingStart(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = False

    p = request["p"]
    slotId = int(p["slotId"])
    userCraftingSlots = json_data.get("userCraftingSlots", None)

    if userCraftingSlots is None:
        report_issue("warning", f"crafting_start: userCraftingSlots is None for user {user_id} in craftingStart command")
        rpcResult["i"] = -1
        return
    
    activeSlot = None
    
    for slot in userCraftingSlots:
        if slot["slotId"] == slotId:
            process_data = slot.get("processData")

            # For some reason it's not dict originally
            if not isinstance(process_data, dict):
                process_data = {}
                slot["processData"] = process_data

            process_data["itemId"] = p["processItemId"]
            process_data["starttime"] = int(time.time())
            process_data["endtime"] = int(time.time()) + 86400
            process_data["finished"] = False

            activeSlot = slot
            break

    if activeSlot is None:
        report_issue("warning", f"crafting_start: No active crafting slot found for user {user_id} in craftingStart command")
        rpcResult["i"] = -1
        return
    
    # Anticheat checks
    # Level check
    crafting_level = json_data["playerData"]["crafting_level"] + 1 # Stored from 0 to 4 instead of 1 to 5 like the init data
    if crafting_level < init_data["planeBlueprints"][str(p["processItemId"])]["Level"]:
        report_issue("warning", f"crafting_start: Crafting level {crafting_level} too low for item {p['processItemId']} for user {user_id}")
        rpcResult["i"] = -1
        return
    # Items check
    num_steps = json_data["userCurrentCraftings"][str(p["processItemId"])]["CraftingLevel"]
    num_required_steps = len(init_data["planeBlueprints"][str(p["processItemId"])]["planeParts"]) # Always 4, but doesn't hurt to check
    if num_steps != num_required_steps:
        report_issue("warning", f"crafting_start: User {user_id} has {num_steps} crafting steps for item {p['processItemId']}, but {num_required_steps} are required")
        rpcResult["i"] = -1
        return

    rpcResult["r"] = {
        "success": {
            "status": True
        }, 
        "0": activeSlot["processData"], 
        "params": {
            "slotId": slotId, 
            "processItemId": p["processItemId"], 
            "slotType": p["slotType"], 
            "processType": "crafting"
        }
    }