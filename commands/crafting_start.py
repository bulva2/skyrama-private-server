import time
from src.debug import send_webhook

def handle_craftingStart(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = False

    p = request["p"]
    slotId = int(p["slotId"])
    userCraftingSlots = json_data.get("userCraftingSlots", None)

    if userCraftingSlots is None:
        send_webhook(json_data, user_id, request)
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
        send_webhook(json_data, user_id, request)
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