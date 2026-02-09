from src.debug import report_issue
import time
import random

def handle_craftingProcessCraftingStep(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = False

    planeId = str(request["p"]["planeId"])
    userCurrentCraftings = json_data.get("userCurrentCraftings")
    userCraftingSlots = json_data.get("userCraftingSlots", None)
    initDataPlane = None

    if userCurrentCraftings is None:
        report_issue("error", f"userCurrentCraftings is None in crafting_processCraftingStep for user_id {user_id}")
        rpcResult["i"] = -1
        return

    if userCraftingSlots is None:
        report_issue("error", f"userCraftingSlots is None in crafting_processCraftingStep for user_id {user_id}")
        rpcResult["i"] = -1
        return

    for key, plane in init_data["planeBlueprints"].items():
        if key == planeId:
            initDataPlane = plane
            break

    if initDataPlane is None:
        report_issue("error", f"initDataPlane is None in crafting_processCraftingStep for user_id {user_id}, planeId {planeId}")
        rpcResult["i"] = -1
        return
    
    if isinstance(userCurrentCraftings, list):
        userCurrentCraftings = {}
        json_data["userCurrentCraftings"] = userCurrentCraftings

    if planeId not in userCurrentCraftings:
        userCurrentCraftings[planeId] = {
            "id": random.randint(10000, 999999), # I suppose this is needed for database purposes
            "UserId": int(user_id),
            "CraftingType": 0, # Not sure what this is
            "CraftingItem": int(planeId),
            "CraftingLevel": 1,
        }
    else:
        userCurrentCraftings[planeId]["CraftingLevel"] += 1

    partId = initDataPlane["planeParts"][userCurrentCraftings[planeId]["CraftingLevel"] - 1]

    for part in init_data["defaultPlaneParts"].values():
        if partId == part["PlanePartId"]:
            upgradePrice = part["VirtualCurrency"]
            materialsNeeded = part["materials"]
            break

    # Check for lack of aircoins (possible cheating)
    if (json_data["playerData"]["air_coins"] - upgradePrice) < 0:
        report_issue("warning", f"crafting_processCraftingStep: Player {json_data['playerData']['user_name']} ({user_id}) tried to upgrade crafting but didn't have enough aircoins. He is most likely cheating!")

        # Revert cheated changes (needs testing)
        if userCurrentCraftings[planeId]["CraftingLevel"] - 1 == 0:
            del userCurrentCraftings[planeId]
        else:
            userCurrentCraftings[planeId]["CraftingLevel"] -= 1

        rpcResult["i"] = -1 # Crash the client
        return
    
    # Check for lack of materials (also possible cheating)
    for matIdStr in map(str, range(7, 13)): # Material IDs are from 7 to 12
        requiredAmount = materialsNeeded.get(matIdStr, 0)
        if requiredAmount > 0:
            playerAmount = json_data["materials"][matIdStr]

            if playerAmount < requiredAmount:
                report_issue("warning", f"crafting_processCraftingStep: Player {json_data['playerData']['user_name']} ({user_id}) tried to upgrade crafting but didn't have enough of material id {matIdStr}. He is most likely cheating!")

                # Revert cheated changes (needs testing)
                if userCurrentCraftings[planeId]["CraftingLevel"] - 1 == 0:
                    del userCurrentCraftings[planeId]
                else:
                    userCurrentCraftings[planeId]["CraftingLevel"] -= 1

                rpcResult["i"] = -1 # Crash the client
                return
            else:
                json_data["materials"][matIdStr] -= requiredAmount
    
    # If we got here then everything is fine, take the aircoins
    json_data["playerData"]["air_coins"] -= upgradePrice

    for slot in userCraftingSlots:
        if slot["slotId"] == request["p"]["slotId"]:
            slot["processId"] = userCurrentCraftings[planeId]["id"]

    rpcResult["r"] = {
        "status": True,
        "craftinglevel": userCurrentCraftings[planeId]["CraftingLevel"],
        "planeId": int(planeId),
        "partId": partId,
        "slotId": request["p"]["slotId"],
    }


# The userCraftingSlots is for craftings that have already started
# The userCurrentCraftings is only to save the current crafting step (the "level" there is the step)
    