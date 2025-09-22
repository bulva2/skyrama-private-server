import time

def handle_deleteBuddypingTime(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = str(int(time.time()))
    rpcResult["r"] = None

    json_data["playerData"]["last_buddyping_time"] = 0
