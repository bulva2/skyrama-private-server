import time


def handle_planesOnStartCargoTutorial(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = None


    # NOT SURE WHAT NEEDS TO HAPPEN HERE
    # Apparently the small terminal needs to be put in storage???
    # Planes disappear during time of the tutorial, we have to code that here???

    for i in json_data["terminals"]:
        if int(i["terminal_types_id"]) == 1:
            i["position_x"] = -100
            i["position_y"] = -100
            break