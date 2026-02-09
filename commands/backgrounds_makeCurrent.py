import time
from src.debug import report_issue

def handle_backgroundsMakeCurrent(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = None

    found = False

    for i in json_data["backgrounds"]:
        # Put the active background in storage
        if int(i["in_storage"]) == 0:
            i["in_storage"] = 1

        if int(i["background_types_id"]) == int(request["p"]["background_types_id"]):
            i["in_storage"] = 0
            found = True

    if not found:
        report_issue("warning", f"backgrounds_makeCurrent: Background type id {request['p']['background_types_id']} not found for user {user_id}")
        rpcResult["i"] = -1
        return