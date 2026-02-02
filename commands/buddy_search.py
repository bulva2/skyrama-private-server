import time
import src.user_manager as user_manager

def handle_buddySearch(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = []

    found_users = user_manager.search_users_by_name(request["p"]["username"])

    for friend_user_id, friend_username in found_users:
        friendship = "none"
        
        if str(friend_user_id) == str(user_id):
            friendship = "yourself"
        else:
            json2_data = user_manager.load_save_by_id(friend_user_id)
            if json2_data != -1:
                buddies = json2_data.get("buddyStuff", {}).get("buddies", [])
                for i in buddies:
                    if int(i.get("hi_player_id", 0)) == int(user_id):
                        friendship = "friend"
                        break
                        
        rpcResult["r"].append({"player_id": friend_user_id, "username": friend_username, "friendship": friendship})
