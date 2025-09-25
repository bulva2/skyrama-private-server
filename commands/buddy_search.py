import time
from pathlib import Path
import os
import json
import src.userManager as userManager

def handle_buddySearch(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = str(int(time.time()))
    rpcResult["r"] = []


    p = Path(__file__).parents[1]
    for file in os.listdir(os.path.join(p, "data", "users", "nametoid")):
        if file.lower().startswith(request["p"]["username"].lower()):
            friendship = "none"
            friend_user_id = userManager.get_id_from_name(file)
            if str(friend_user_id) == str(user_id):
              friendship = "yourself"
            else:
              json2_data = userManager.load_save_by_id(friend_user_id)
              for i in json2_data["buddyStuff"]["buddies"]:
                if int(i["hi_player_id"]) == int(user_id):
                  friendship = "friend"
            rpcResult["r"].append({"player_id":friend_user_id,"username":file,"friendship":friendship})
