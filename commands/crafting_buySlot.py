import time
from src.utils import subtract_resources

def handle_craftingBuySlot(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())

    slot_id = request["p"]["slotId"]
    slot_type = request["p"]["slotType"]

    # Read config
    for k, v in init_data["defaultCraftingSlots"].items():
        if v["SlotType"] == slot_type and v["SlotId"] == slot_id:
            dischargeTime = v["DischargeTime"]
            air_cash_cost = v["RealCurrency"]
            break

    subtract_resources(json_data, rpcResult, air_cash = air_cash_cost)

    # I don't know any cases where this wouldn't be success
    rpcResult["r"] = {"success": True, "slotId": slot_id, "slotType": slot_type} # i offered 10 aircash to find this, it better be worth it :(
    
    # Check if slot was bought before
    for i in json_data["userCraftingSlots"]:
        if i["slotId"] == slot_id:
            i["slotDischarge"] = int(rpcResult["t"]) + dischargeTime
            i["processId"] = 0
            i["processData"] = []
            return
    
    json_data["userCraftingSlots"].append({"slotType": slot_type,
                                           "slotId": slot_id,
                                           "slotDischarge": int(rpcResult["t"]) + dischargeTime,
                                           "processId": 0,
                                           "processData": []})