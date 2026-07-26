from src.debug import report_issue
import time
import random
import src.user_manager as user_manager

MAX_PASSENGERS_PER_BUDDY = 350

def handle_buddyCollectPassenger(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = None

    # For now those are just some random values, might need to check how exactly
    # this is handled in the actual game.
    collected_passengers_myself = random.randint(1, 5)
    collected_passengers_buddy = random.randint(75, 100)

    # Add collected passengers to us
    json_data["playerData"]["passengers"] += collected_passengers_myself
    buddy_data = user_manager.load_save_by_id(request["p"])

    if isinstance(buddy_data, int):
        report_issue("warning", f"buddy_collectPassenger: Failed to load buddy data for user_id {request['p']} from user_id {user_id}")
        rpcResult["r"] = False
        return

    buddies = buddy_data["buddyStuff"]["buddies"]

    # This controls the passengers for the buddy (the one being collected from)
    for buddy in buddies:
        if int(buddy["lo_player_id"]) == int(request["p"]) and int(buddy["hi_player_id"]) == int(user_id):
            # This is to prevent unnecessary db writes to prevent crashes or other issues, might increase the limit in the future
            if int(buddy["received_passengers"]) < MAX_PASSENGERS_PER_BUDDY:
                buddy["received_passengers"] = int(buddy["received_passengers"]) + collected_passengers_buddy
                user_manager.modify_save_by_id(request["p"], buddy_data)
            break
    
    # This controls the cooldown for us (the collector) 
    # -> Doesn't work, help wanted, broken in actual game too not just in ours.
    # Unless I misunderstood what is this meant to do which is likely too.
    for my_buddy in json_data["buddyStuff"]["buddies"]:
        if int(my_buddy["lo_player_id"]) == int(user_id) and int(my_buddy["hi_player_id"]) == int(request["p"]):
            # Reset 24hr cooldown
            if int(time.time()) - int(my_buddy["todays_first_collected_passengers_time"]) > 86400:  # 24 hours in seconds
                my_buddy["todays_collected_passengers"] = 0
                my_buddy["todays_first_collected_passengers_time"] = int(time.time())
            
            my_buddy["todays_collected_passengers"] = int(my_buddy["todays_collected_passengers"]) + collected_passengers_buddy
            break

    rpcResult["r"] = True

