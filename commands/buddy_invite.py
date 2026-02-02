import time
import src.user_manager as user_manager

def handle_buddyInvite(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = True

    json2_data = user_manager.load_save_by_id(request["p"]["buddyId"])

    if int(json2_data["playerData"]["location_id"]) == -1: # Player is still in the tutorial, location_id would be wrong.
        rpcResult["r"] = False
    else:
        json_data["buddyStuff"]["buddies"].append({"lo_player_id":str(user_id),"hi_player_id":str(request["p"]["buddyId"]),"status":"1","buddy_points":"0","num_hits":"0","task_visit":"0","num_flights_today":"0","todays_first_flight_time":"0","todays_first_collected_passengers_time":"0","todays_collected_passengers":"0","received_passengers":"0","last_ping_time":1674583733,"last_buddyping_time":0,"xp":json2_data["playerData"]["xp"],"online":0,"location_id":json2_data["playerData"]["location_id"],"username":json2_data["playerData"]["user_name"]})
        json2_data["buddyStuff"]["buddies"].append({"lo_player_id":str(request["p"]["buddyId"]),"hi_player_id":str(user_id),"status":"2","buddy_points":"0","num_hits":"0","task_visit":"0","num_flights_today":"0","todays_first_flight_time":"0","todays_first_collected_passengers_time":"0","todays_collected_passengers":"0","received_passengers":"0","last_ping_time":1674583733,"last_buddyping_time":0,"xp":json_data["playerData"]["xp"],"online":0,"location_id":json_data["playerData"]["location_id"],"username":json_data["playerData"]["user_name"]})

    user_manager.modify_save_by_id(request["p"]["buddyId"], json2_data)