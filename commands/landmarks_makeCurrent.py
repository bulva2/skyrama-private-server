from src.debug import report_issue
import time

def handle_landmarksMakeCurrent(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = None

    found = False

    for i in json_data["landmarks"]:
        # Put the active landmark in storage
        if int(i["in_storage"]) == 0:
            i["in_storage"] = 1

        if int(i["landmark_types_id"]) == int(request["p"]["landmark_types_id"]):
            i["in_storage"] = 0
            found = True
            break

    if not found:
        report_issue("warning", f"landmarks_makeCurrent: Landmark type id {request['p']['landmark_types_id']} not found for user {user_id}")
        rpcResult["i"] = -1
        return