import time

def handle_getConfig(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())

    rpcResult["r"] = {"viewportWidth":1000,"viewportHeight":600,"cellSize":24,"numCells":40,"cameraAngle":60,"userIdTest":user_id,"nextObjectId":json_data["playerData"]["next_object_id"],"serverTime":int(time.time()),"delta_ping":1800,"sort_buddylist":False,"event_basket_timeout":21600}