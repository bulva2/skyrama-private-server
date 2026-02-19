from src.debug import report_issue
import time
import src.user_manager as user_manager

def handle_buddyDecline(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = None

    buddy_data = user_manager.load_save_by_id(request["p"]["buddyId"])

    if isinstance(buddy_data, int):
      report_issue("warning", f"buddyDecline: Failed to load buddy data for user_id {request['p']['buddyId']} from user_id {user_id}")
      rpcResult["r"] = {"success": False}
      return

    for idx, buddy in enumerate(json_data["buddyStuff"]["buddies"]):
        if buddy["hi_player_id"] == request["p"]["buddyId"] and buddy["lo_player_id"] == user_id:
            json_data["buddyStuff"]["buddies"].pop(idx)
            break
        
    for idx, buddy in enumerate(buddy_data["buddyStuff"]["buddies"]):
        if buddy["lo_player_id"] == request["p"]["buddyId"] and buddy["hi_player_id"] == user_id:
            buddy_data["buddyStuff"]["buddies"].pop(idx)
            break
        
    user_manager.modify_save_by_id(request["p"]["buddyId"], buddy_data)