import time
import logging
import src.userManager as userManager

def run_buddy_checks(time, json_data):
    for buddy in json_data["buddyStuff"]["buddies"]:
        buddy_data = userManager.load_save_by_id(buddy["hi_player_id"])
        
        # load_save_by_id returns -1 if user isn't found, skip this user
        if buddy_data == -1:
            logging.warning(f"run_buddy_checks ({json_data["playerData"]["user_name"]}): Buddy user {buddy['hi_player_id']} not found, setting offline status")
            buddy["last_buddyping_time"] = 0
            buddy["xp"] = 0
            buddy["status"] = 0  # Set to offline
            continue
            
        buddy["last_buddyping_time"] = buddy_data["playerData"]["last_buddyping_time"]
        buddy["xp"] = buddy_data["playerData"]["xp"]
        # if request accepted
        if int(buddy["status"]) != 1 and int(buddy["status"]) != 2:
            # if buddyping activated
            if time < int(buddy["last_buddyping_time"]):
                buddy["status"] = 5
            else:
                buddy["status"] = 0

def handle_buddyGetAll(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = str(int(time.time()))
    rpcResult["r"] = {}

    '''
    Stuff we need to check for:
    - last_buddyping_time
    - xp
    - status
    Stuff we intentionally DO NOT CHECK (because privacy and absolutely not needed):
    - last_ping_time
    - num_flights_today
    - todays_first_flight_time
    - online



    STATUS NUMBERS:
    1 = you sent an invite to them
    2 = they sent an invite to you
    3 = ?
    4 = ?
    5 = online
    0 = offline
    '''

    run_buddy_checks(request["t"], json_data)

    rpcResult["r"]["buddies"] = json_data["buddyStuff"]["buddies"]
    rpcResult["r"]["packets"] = json_data["buddyStuff"]["packets"]