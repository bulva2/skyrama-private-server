import logging
import time

def handle_trackFlashError(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = True

    logging.warning("Flash client error", extra={
        "event": "flash_error",
        "user_id": user_id,
        "username": json_data.get("playerData", {}).get("user_name"),
        "command": request.get("m"),
        "payload": request,
    })
