import time
from pathlib import Path
import os
import json
import src.userManager as userManager
def handle_buddyEndRelationship(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = str(int(time.time()))
    rpcResult["r"] = None
    '''
    p = Path(__file__).parents[1]
            
    for file in os.listdir(os.path.join(p, "data")):
        if file[0:8] == str(request["p"]):
            player_to_remove_file = file
            break
    
    f = open(os.path.join(p, "data", player_to_remove_file), "r")
    json2_data = json.loads(str(f.read()))
    f.close()
    '''

    json2_data = userManager.load_save_by_id(request["p"])

    g = 0
    for i in json_data["buddyStuff"]["buddies"]:
      if str(i["hi_player_id"]) == str(request["p"]) and str(i["lo_player_id"]) == str(user_id):
        json_data["buddyStuff"]["buddies"].pop(g)
      g = g + 1
    g = 0    
    for j in json2_data["buddyStuff"]["buddies"]:
      if str(j["lo_player_id"]) == str(request["p"]) and str(j["hi_player_id"]) == str(user_id):
        json2_data["buddyStuff"]["buddies"].pop(g)
      g = g + 1

    '''
    f = open(os.path.join(p, "data", player_to_remove_file), "w")
    f.write(json.dumps(json2_data))
    f.close()
    '''
    userManager.modify_save_by_id(request["p"], json2_data)