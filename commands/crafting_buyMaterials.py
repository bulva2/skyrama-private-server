import time
from src.utils import substract_resources

def handle_craftingBuyMaterials(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())

    slot_id = request["p"]["slotId"]
    amount = request["p"]["amount"]
    material_id = request["p"]["materialId"]
    plane_part_id = request["p"]["planePartId"]

    # Read config
    air_cash_cost = amount * init_data["materialTypes"][str(material_id)]["RealCurrency"]
    if air_cash_cost == 0: # This is the case for tuning parts, we don't want people to get unlimited free tuning parts this way
        rpcResult["i"] = -1 # Disconnect user without saving

    # Add parts
    if str(material_id) not in json_data["materials"]:
        json_data["materials"][str(material_id)] = 0
    json_data["materials"][str(material_id)] += amount

    substract_resources(json_data, rpcResult, air_cash = air_cash_cost)

    # Collect all crafting materials
    materials = {k: v for k, v in json_data["materials"].items() if init_data["materialTypes"][str(k)]["Type"] == "crafting"}

    # I don't know any cases where this wouldn't be success
    rpcResult["r"] = {"success": True, "slotId": slot_id, "materialId": material_id,
                      "planePartId": plane_part_id, "materials": materials}
                    # in memorial for the 26 aircash that were offered for this: R.I.P.