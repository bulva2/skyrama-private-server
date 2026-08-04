from src.debug import report_issue
from src.enums import BuddyStatus
import time
import src.user_manager as user_manager

def handle_buddyAccept(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = None

    buddy_data = user_manager.load_save_by_id(request["p"]["buddyId"])

    if isinstance(buddy_data, int):
        report_issue("warning", f"buddyAccept: Failed to load buddy data for user_id {request['p']['buddyId']} from user_id {user_id}")
        rpcResult["r"] = {"success": False}
        return

    # Friend both players by setting their status to 5 (active)
    update_buddy_status(json_data["buddyStuff"]["buddies"], request["p"]["buddyId"], user_id)
    update_buddy_status(buddy_data["buddyStuff"]["buddies"], user_id, request["p"]["buddyId"])
    user_manager.modify_save_by_id(request["p"]["buddyId"], buddy_data)

    isOnline = 1 if (buddy_data["playerData"]["last_buddyping_time"] > int(time.time()) - 1800) else 0
    rpcResult["r"] = {"success": True, "buddyId": request["p"]["buddyId"], "buddyUsername": buddy_data["playerData"]["user_name"], "online": isOnline}

#hi_id = his user id, lo_id = local user id
def update_buddy_status(buddies: dict, hi_id: int, lo_id: int):
    for idx, buddy in enumerate(buddies):
        if int(buddy["hi_player_id"]) == int(hi_id) and int(buddy["lo_player_id"]) == int(lo_id):
            buddies[idx]["status"] = BuddyStatus.ACTIVE.value #5
            break