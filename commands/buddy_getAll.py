import time
import src.user_manager as user_manager
from src.enums import BuddyStatus
from src.debug import report_issue

def run_buddy_checks(time, json_data):
    buddies = json_data["buddyStuff"]["buddies"]
    pings = user_manager.get_buddy_pings_bulk([int(b["hi_player_id"]) for b in buddies])

    for buddy in buddies:
        found = pings.get(int(buddy["hi_player_id"]))

        if found is None:
            report_issue("warning", f"run_buddy_checks: Buddy user {buddy['hi_player_id']} not found for user {json_data['playerData']['user_name']} (ID: {json_data['playerData']['account_id']}), setting offline status")
            buddy["last_buddyping_time"] = 0
            buddy["xp"] = 0
            buddy["status"] = BuddyStatus.NONE.value  # Set to offline
            continue

        buddy["last_buddyping_time"], buddy["xp"] = found
        # if request accepted
        if int(buddy["status"]) != BuddyStatus.INVITED.value and int(buddy["status"]) != BuddyStatus.INVITED_BY.value:
            # if buddyping activated
            if time < int(buddy["last_buddyping_time"]):
                buddy["status"] = BuddyStatus.ACTIVE.value #5
            else:
                buddy["status"] = BuddyStatus.NONE.value #0

def handle_buddyGetAll(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = {}

    #Stuff we need to check for:
    # last_buddyping_time
    # xp
    # status
    #Stuff we intentionally DO NOT CHECK (because privacy and absolutely not needed):
    # last_ping_time
    # num_flights_today
    # todays_first_flight_time
    # online

    run_buddy_checks(request["t"], json_data)

    rpcResult["r"]["buddies"] = json_data["buddyStuff"]["buddies"]
    rpcResult["r"]["packets"] = json_data["buddyStuff"]["packets"]