import time

# Work in progress, not fully implemented yet
def handle_recyclingStart(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = None

    p = request["p"]

    # plane_id NOT plane_type_id
    processItemId = int(p["processItemId"])
    slotId = int(p["slotId"])
    slotType = int(p["slotType"])

    recycling_duration = 3600  # 1 Hour
    start_time = int(time.time())
    end_time = start_time + recycling_duration

    # Get plane type from plane id
    plane_type_id = None

    # now we get plane_type_id for processData
    for plane in json_data.get("planes", []):
        if int(plane["id"]) == processItemId:
            plane_type_id = int(plane["plane_type_id"])
            break

    # ProcessDataVO
    processData = {
        "endTime": end_time,
        "finished": False,
        # Now it's plane_type_id instead of plane_id!
        "itemId": plane_type_id,
        "startTime": start_time
    }

    # PlaneRecycleBundleVO class
    slot_bundle = {
        "processId": processItemId,
        "slotId": slotId,
        "slotType": slotType,
        "processData": processData
    }

    # Same as crafting, I guess we can just make it dict in the new player data
    if "userRecyclingSlots" not in json_data or not isinstance(json_data["userRecyclingSlots"], dict):
        json_data["userRecyclingSlots"] = {}

    # This needs to be checked, I tried to do it bit differently than in crafting and yeaaah
    # I need to go sleep fr
    json_data["userRecyclingSlots"][str(slotType)] = slot_bundle

    # Return slot_bundle + status: true
    rpcResult["r"] = {
        "success": {
            "status": True
        },
        "0": slot_bundle
    }