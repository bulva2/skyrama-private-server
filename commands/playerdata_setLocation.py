import time

def handle_setLocation(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = None

    json_data["playerData"]["location_id"] = request["p"]["location_id"]
