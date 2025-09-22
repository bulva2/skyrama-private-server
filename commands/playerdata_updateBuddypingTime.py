import time
import src.userManager as userManager
import logging

def handle_updateBuddypingTime(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = str(int(time.time()))
    rpcResult["r"] = None

    json_data["playerData"]["last_buddyping_time"] = request["t"] + 1800 # = 30 minutes

    location_id = json_data["playerData"]["location_id"]

    try:
        userManager.buddyping_enabled(user_id, location_id)
    except Exception as error:
        logging.error("An error occurred in playerdata.updateBuddypingTime:", type(error).__name__) # Don't care too much if it fails lol
