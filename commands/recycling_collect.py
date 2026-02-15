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

    found = False

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

    # The level caps from initData 'recycling_level_caps'
    init_player_data = init_data.get("playerData", -1)

    if init_player_data == -1:
        report_issue("warning", f"recycling_collect: playerData not found in init data for user {user_id}")
        rpcResult["i"] = -1
        return

    recycling_level_caps = init_player_data.get("recycling_level_caps")
    if recycling_level_caps is None:
        report_issue("warning", f"recycling_collect: recycling_level_caps not found in init data for user {user_id}")
        rpcResult["i"] = -1
        return

    current_level = json_data["playerData"].get("recycling_level", 0)
    level_cap = recycling_level_caps.get(str(current_level + 1), 35000)

    # Level out of scope, idk what actually happens so log for future me or before I test it, for now set it to 35k
    if (level_cap == 35000):
        report_issue("warning", f"recycling_collect: Level cap for level cap (current_level + 1) => {current_level + 1} not found in init data for user {user_id}, defaulting to 35k")

    json_data["playerData"]["recycling_levelCap"] = level_cap

    json_data["playerData"]["recycling_totalXP"] += recycling_xp
    json_data["playerData"]["recycling_levelXP"] += recycling_xp

    # Multi-level up handling even tho it shouldn't ever happen
    while json_data["playerData"]["recycling_levelXP"] >= level_cap:
        json_data["playerData"]["recycling_level"] += 1
        json_data["playerData"]["recycling_levelXP"] -= level_cap

        current_level = json_data["playerData"]["recycling_level"]
        new_cap = recycling_level_caps.get(str(current_level + 1))

        if new_cap:
            json_data["playerData"]["recycling_levelCap"] = new_cap
            level_cap = new_cap

    for drop in material_drops:
        m_id = str(drop["materialId"])
        amount = drop["amount"]

        if m_id in json_data["materials"]:
            json_data["materials"][m_id] += amount
        else:
            json_data["materials"][m_id] = amount
        
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