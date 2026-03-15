from src.debug import report_issue
from src.utils import subtract_resources
import time
import random
import math

S_PLANE_BASIC_XP = 1
M_PLANE_BASIC_XP = 1
CHANCE_FOR_BONUS = 0.15
MULTIPLIER_BONUS = 5

def handle_recyclingInstant(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
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
            break
    
    if not found:
        report_issue("warning", f"recycling_instant: Slot {slotId} not found for user {user_id}")
        rpcResult["i"] = -1
        return
    
    # We get the price of instant recycling from defaultRecyclingData
    defaultRecyclingData = init_data["defaultRecyclingData"]
    timeRemaining = processData["endtime"] - int(time.time())


    if timeRemaining <= 0:
        # I don't think that we should crash here but it shouldn't happen either
        report_issue("warning", f"recycling_instant: User {user_id} tried to instant recycle but the recycling is already done (time remaining: {timeRemaining} seconds). Price for the service was set to 1.")
        timeRemaining = 3600

    price = math.ceil(float((timeRemaining / 3600)) * float(defaultRecyclingData["costsPerHour"]))

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
        report_issue("warning", f"recycling_instant: Plane type {plane_type_id} not found in init data for user {user_id}")
        rpcResult["i"] = -1
        return
    
    subtract_resources(json_data, rpcResult, air_cash=price)

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
        report_issue("warning", f"recycling_instant: Level cap for level cap (current_level + 1) => {current_level + 1} not found in init data for user {user_id}, defaulting to 35k")

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

    items_to_add_to_obj.append("materials")
        
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