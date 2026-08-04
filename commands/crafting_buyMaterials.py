import time
from src.utils import subtract_resources
from src.debug import report_issue

def handle_craftingBuyMaterials(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())

    slot_id = request["p"]["slotId"]
    amount = request["p"]["amount"]
    material_id = request["p"]["materialId"]
    plane_part_id = request["p"]["planePartId"]

    # `amount` comes straight off the wire. A negative value used to produce a
    # negative cost, which sailed through the affordability check and minted air
    # cash instead of spending it. Anything but a positive whole number is a
    # crafted request. (bool is excluded explicitly: it is a subclass of int.)
    if isinstance(amount, bool) or not isinstance(amount, int) or amount <= 0:
        report_issue("warning", f"crafting_buyMaterials: User {user_id} sent a non-positive amount {amount!r} for material id {material_id}, possible exploit attempt")
        rpcResult["i"] = -1 # Disconnect user without saving
        return

    # Unknown ids would otherwise KeyError into a 500.
    material_type = init_data["materialTypes"].get(str(material_id))
    if material_type is None:
        report_issue("warning", f"crafting_buyMaterials: User {user_id} requested unknown material id {material_id}")
        rpcResult["i"] = -1
        return

    # Read config
    air_cash_cost = round(amount * material_type["RealCurrency"])
    if air_cash_cost == 0: # This is the case for tuning parts, we don't want people to get unlimited free tuning parts this way
        report_issue("warning", f"crafting_buyMaterials: User {user_id} attempted to buy crafting material id {material_id} with 0 aircash, possible exploit attempt")
        rpcResult["i"] = -1 # Disconnect user without saving
        return

    # Take payment BEFORE handing over the goods, and stop if it failed - the
    # rejected request is discarded upstream, but granting first and charging
    # second is the wrong order to rely on that.
    subtract_resources(json_data, rpcResult, air_cash = air_cash_cost)
    if rpcResult["i"] == -1:
        return

    # Add parts
    if str(material_id) not in json_data["materials"]:
        json_data["materials"][str(material_id)] = 0
    json_data["materials"][str(material_id)] += amount

    # Collect all crafting materials
    materials = {k: v for k, v in json_data["materials"].items() if init_data["materialTypes"][str(k)]["Type"] == "crafting"}

    # I don't know any cases where this wouldn't be success
    rpcResult["r"] = {"success": True, "slotId": slot_id, "materialId": material_id,
                      "planePartId": plane_part_id, "materials": materials}
    # in memorial for the 26 aircash that were offered for this: R.I.P.