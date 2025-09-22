import time

def handle_planesGet(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = str(int(time.time()))

    # Make cashcow reappear on the radar
    for i in json_data["planes"]:
        if int(i["id"]) == 0:
            if i["flight_status"] == 122:
                i["flight_status"] = 77
                i["departure_time"] = int(time.time()) - 450
                i["arrival_time"] = int(time.time()) + 450 # Disappears before arrival time, but apparently that's normal?
            break

    rpcResult["r"] = json_data["planes"]
