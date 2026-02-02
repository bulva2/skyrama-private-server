import time
import src.user_manager as user_manager

def handle_buddyAccept(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = None

    json2_data = user_manager.load_save_by_id(request["p"]["buddyId"])

    g = 0
    for i in json_data["buddyStuff"]["buddies"]:
      if str(i["hi_player_id"]) == str(request["p"]["buddyId"]) and str(i["lo_player_id"]) == str(user_id):
        json_data["buddyStuff"]["buddies"][g]["status"] = "0"
      g = g + 1
    g = 0    
    for j in json2_data["buddyStuff"]["buddies"]:
      if str(j["lo_player_id"]) == str(request["p"]["buddyId"]) and str(j["hi_player_id"]) == str(user_id):
        json2_data["buddyStuff"]["buddies"][g]["status"] = "0"
      g = g + 1

    user_manager.modify_save_by_id(request["p"]["buddyId"], json2_data)