import time

def handle_updateSettings(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = None

    json_data["playerData"]["quickservice_on"] = request["p"]["quickservice_on"]
    json_data["playerData"]["effects_on"] = request["p"]["effects_on"]
    json_data["playerData"]["sound_on"] = request["p"]["sound_on"]
    json_data["playerData"]["superfuel_on"] = request["p"]["superfuel_on"]
    json_data["playerData"]["animations_on"] = request["p"]["animations_on"]
    if "buddyflag_on" in request["p"]: # For compatibility with original Skyrama
        json_data["playerData"]["buddyflag_on"] = request["p"]["buddyflag_on"]