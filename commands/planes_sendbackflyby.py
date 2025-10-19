import time


def handle_planesSendBackFlyBy(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = None

    # Remove fly-by from radar (basically copied from planes.miss)

    if request["p"]["id"] != 0:
        for plane in json_data["planes"]:
            if int(plane["id"]) == request["p"]["id"]:
                json_data["planes"].remove(plane)
                break