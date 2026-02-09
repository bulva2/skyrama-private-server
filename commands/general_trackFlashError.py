import logging
import time
from src.debug import send_trackflash_webhook

def handle_trackFlashError(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = True

    logging.warning(f"Flash error tracked for user {user_id}: {request}")

    try:
        send_trackflash_webhook(json_data, user_id, request)
    except Exception as error:
        logging.error(f"general.trackFlashError: failed to send webhook: {error}")