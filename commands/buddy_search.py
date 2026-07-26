import time
import src.user_manager as user_manager

def handle_buddySearch(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = []

    found_users = user_manager.search_users_by_name(request["p"]["username"])

    # One query for the buddy lists of everyone the search matched, instead of a
    # full save each (planes included) just to scan buddyStuff.
    buddy_stuff = user_manager.get_buddy_stuff_bulk(
        [uid for uid, _ in found_users if int(uid) != int(user_id)]
    )

    for friend_user_id, friend_username in found_users:
        friendship = "none"

        if int(friend_user_id) == int(user_id):
            friendship = "yourself"
        else:
            for i in buddy_stuff.get(int(friend_user_id), {}).get("buddies", []) or []:
                if int(i.get("hi_player_id", 0)) == int(user_id):
                    friendship = "friend"
                    break

        rpcResult["r"].append({"player_id": friend_user_id, "username": friend_username, "friendship": friendship})
