import time


def handle_planesOnStartCargoTutorial(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = None

    for i in json_data["terminals"]:
        if int(i["terminal_types_id"]) == 1:
            i["position_x"] = -100
            i["position_y"] = -100
            break