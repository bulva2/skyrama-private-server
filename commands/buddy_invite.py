from src.debug import report_issue
from src.enums import BuddyStatus
import time
import src.user_manager as user_manager

def handle_buddyInvite(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = True

    buddy_data = user_manager.load_save_by_id(request["p"]["buddyId"])

    if isinstance(buddy_data, int):
        report_issue("warning", f"buddy_invite: Failed to load buddy data for user_id {request['p']['buddyId']} from user_id {user_id}")
        rpcResult["r"] = False
        return

    if int(buddy_data["playerData"]["location_id"]) != -1: # Player is still in the tutorial, location_id would be wrong.
        json_data["buddyStuff"]["buddies"].append({
            "lo_player_id": user_id,
            "hi_player_id": request["p"]["buddyId"],
            "status": BuddyStatus.INVITED.value, #1
            "buddy_points": 0, # Game wants 10, do we change it?
            "num_hits": 0,
            "task_visit": 0,
            "num_flights_today": 0,
            "todays_first_flight_time": 0,
            "todays_first_collected_passengers_time": 0,
            "todays_collected_passengers": 0,
            "received_passengers": 0,
            "last_ping_time": 1674583733,
            "last_buddyping_time": 0,
            "xp": buddy_data["playerData"]["xp"],
            "online": 0,
            "location_id": buddy_data["playerData"]["location_id"],
            "username": buddy_data["playerData"]["user_name"]
        })

        buddy_data["buddyStuff"]["buddies"].append({
            "lo_player_id": request["p"]["buddyId"],
            "hi_player_id": user_id,
            "status": BuddyStatus.INVITED_BY.value, #2
            "buddy_points": 0, # Game wants 10, do we change it?
            "num_hits": 0,
            "task_visit": 0,
            "num_flights_today": 0,
            "todays_first_flight_time": 0,
            "todays_first_collected_passengers_time": 0,
            "todays_collected_passengers": 0,
            "received_passengers": 0,
            "last_ping_time": 1674583733,
            "last_buddyping_time": 0,
            "xp": json_data["playerData"]["xp"],
            "online": 0,
            "location_id": json_data["playerData"]["location_id"],
            "username": json_data["playerData"]["user_name"]
        })
    else:
        rpcResult["r"] = False
        return

    user_manager.modify_save_by_id(request["p"]["buddyId"], buddy_data)