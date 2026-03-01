import time

def handle_getStats(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = None

    # Gets called when opening the AC shop, but we don't have this so stubbed it.

    # Ignore the error this gives for now :)