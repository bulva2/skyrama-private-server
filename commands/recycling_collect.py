import random
import time
from src.debug import report_issue

S_PLANE_BASIC_XP = 1
M_PLANE_BASIC_XP = 1
CHANCE_FOR_BONUS = 0.15
MULTIPLIER_BONUS = 5

def handle_recyclingCollect(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = None

    p = request["p"]

    slotId = int(p["slotId"])
    slotType = int(p["slotType"])

    found = False

    # Get recycling slot
    for slot in json_data["userRecyclingSlots"]:
        if slot["slotId"] == slotId and slot["slotType"] == slotType:
            found = True
            processData = slot["processData"]
            plane_type_id = processData["itemId"]
            end_time = processData["endtime"]
            break
    
    if not found:
        report_issue("warning", f"recycling_collect: Slot {slotId} not found for user {user_id}")
        rpcResult["i"] = -1
        return

    # Check if end time has really passed
    if time.time() < end_time:
        report_issue("warning", f"recycling_collect: User {user_id} tried to collect before the recycling is ready (in {end_time - time.time()} seconds)")
        rpcResult["i"] = -1
        return

    found = True

    # Get the recycling value and size
    for plane in init_data["planeTypes"]:
        if plane["id"] == plane_type_id:
            found = True
            recycling_value = plane["recyclingValue"]
            size = plane["size"]
            type = plane["type"] # Both technically not needed but never hurts to double-check
            break

    if not found:
        report_issue("warning", f"recycling_collect: Plane type {plane_type_id} not found in init data for user {user_id}")
        rpcResult["i"] = -1
        return

    # Get the droprates
    material_chances =  init_data["materialChances"][str(recycling_value)]

    material_drops = []

    for drop in material_chances:
        min_amount = drop["MinAmount"]
        max_amount = drop["MaxAmount"]
        chance = drop["Chance"]

        # Bernouilli (i hate it)
        amount = min_amount + sum(random.random() < chance for _ in range(max_amount - min_amount))

        material_drops.append({"materialId": drop["MaterialId"], "amount": amount})

    add_bonus = random.random() < CHANCE_FOR_BONUS
    if size == "Small" and type == "plane" and slotType == 1:
        recycling_xp = S_PLANE_BASIC_XP * MULTIPLIER_BONUS if add_bonus else S_PLANE_BASIC_XP
    elif size == "Medium" and type == "plane" and slotType == 2:
        recycling_xp = M_PLANE_BASIC_XP * MULTIPLIER_BONUS if add_bonus else M_PLANE_BASIC_XP
    else:
        report_issue("warning", f"recycling_collect: Inconsistency between slot type and plane type for user {user_id}")
        rpcResult["i"] = -1
        return   

    # To-do: add to playerData
        

    slot["processData"] = [] # No need for it to be an array but it doesn't hurt either i guess
    slot["processId"] = 0

    rpcResult["r"] = {
        "status": True,
        "slotId": slotId,
        "slotType": slotType,
        "processType": "recycling",
        "result": {
            "materials": material_drops,
            "recyclingXp": recycling_xp,
            "xpCrit": False
        } 
    }