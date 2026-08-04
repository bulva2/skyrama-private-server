import time
from src.debug import report_issue

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

    defaultRecyclingData = init_data["defaultRecyclingData"]
    recycling_duration = int(defaultRecyclingData["small"]["time"] if slotType == 1 else defaultRecyclingData["medium"]["time"])
    start_time = int(time.time())
    end_time = start_time + recycling_duration

    # Get plane type from plane id
    plane_type_id = None

    # now we get plane_type_id for processData
    for plane in json_data.get("planes", []):
        if int(plane["id"]) == processItemId:
            plane_type_id = int(plane["plane_type_id"])
            break

    if plane_type_id is None:
        report_issue("warning", f"recycling_start: Plane not found for user {user_id}")
        rpcResult["i"] = -1
        return
    
    json_data["planes"].remove(plane)
    items_to_add_to_obj.append("planes")

    # ProcessDataVO
    processData = {
        "endtime": end_time,
        "finished": False,
    # Now it's plane_type_id instead of plane_id!
        "itemId": plane_type_id,
        "starttime": start_time
    }

    # PlaneRecycleBundleVO class
    slot_bundle = {
        "processId": processItemId,
        "slotId": slotId,
        "slotType": slotType,
        "processData": processData
    }

    recycling_slots = json_data["userRecyclingSlots"]

    active_slot = None
    for slot in recycling_slots:
        if slot["slotId"] == slotId and slot["slotType"] == slotType:
            if slot["processId"] != 0:
                report_issue("warning", f"recycling_start: Recycling slot has been found but is already in use for user {user_id}")
                rpcResult["i"] = -1
                return
            slot["processId"] = processItemId
            slot["processData"] = processData
            active_slot = slot
            break

    if active_slot is None:
        report_issue("warning", f"recycling_start: No active recycling slot found for user {user_id} in recyclingStart command")
        rpcResult["i"] = -1
        return

    # Return slot_bundle + status: true
    rpcResult["r"] = {
        "success": {
            "status": True
        },
        "0": slot_bundle
    }