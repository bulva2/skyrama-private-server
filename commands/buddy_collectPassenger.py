from src.debug import report_issue
import time
import random
import src.user_manager as user_manager

# To-do?: Don't edit the buddy data after todays_collected_passengers reaches some limit, to prevent unnecessary db writes.
# Idk if this is what actual skyrama does or not
def handle_buddyCollectPassenger(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = None

    collected_passengers = random.randint(0, 5)

    # Add collected passengers to us
    json_data["playerData"]["passengers"] += collected_passengers
    buddy_data = user_manager.load_save_by_id(request["p"])

    if isinstance(buddy_data, int):
        report_issue("warning", f"buddy_collectPassenger: Failed to load buddy data for user_id {request['p']} from user_id {user_id}")
        rpcResult["r"] = False
        return

    buddies = buddy_data["buddyStuff"]["buddies"]

    # This controls the passengers for the buddy (the one being collected from)
    for buddy in buddies:
        if buddy["lo_player_id"] == request["p"] and buddy["hi_player_id"] == user_id:
            buddy["received_passengers"] += collected_passengers
            user_manager.modify_save_by_id(request["p"], buddy_data)
            break
    
    # This controls the cooldown for us (the collector) 
    # -> Doesn't work, help wanted, broken in actual game too not just in ours.
    # Unless I misunderstood what is this meant to do which is likely too.
    for my_buddy in json_data["buddyStuff"]["buddies"]:
        if my_buddy["lo_player_id"] == user_id and my_buddy["hi_player_id"] == request["p"]:
            # Reset 24hr cooldown
            if int(time.time()) - my_buddy["todays_first_collected_passengers_time"] > 86400:  # 24 hours in seconds
                my_buddy["todays_collected_passengers"] = 0
                my_buddy["todays_first_collected_passengers_time"] = int(time.time())
            
            my_buddy["todays_collected_passengers"] += collected_passengers
            break

    rpcResult["r"] = True

