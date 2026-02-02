import time

def handle_planesRemoveFlyByPlane(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = None

    if request["p"]["id"] != 0:
        for idx, plane in enumerate(json_data["planes"]):
            if int(plane["id"]) == request["p"]["id"]:
                json_data["planes"].pop(idx)
                break
