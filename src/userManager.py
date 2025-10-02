from pathlib import Path
import json
import os
import random
from concurrent.futures import ThreadPoolExecutor

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Assume 'data' is at the project root, one level up from src/
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

'''
Store all save files in memory.
'''
    
__saves = {}
__world_map_players = {}
__playerCount = {"count": len(os.listdir(os.path.join(PROJECT_ROOT, "data", "users"))) - 1}

n = open(os.path.join(PROJECT_ROOT, "data", "new_player.json.def"), "r", encoding="utf-8")
NEW_ACCOUNT_DATA = json.loads(n.read())
n.close()

def store_save_by_id(user_id : int) -> bool:
    try:
        f = open(os.path.join(PROJECT_ROOT, "data", "users", str(user_id) + ".json"), "r", encoding="utf-8")
        json_data = json.loads(str(f.read()))
        __saves[str(user_id)] = json_data
        f.close() 
        return True
    except FileNotFoundError: # Account does not exist
        return False

def load_save_by_id(user_id : int) -> dict | int:
    if not str(user_id) in __saves:
        if store_save_by_id(user_id) == False:
            return -1
    return __saves[str(user_id)]

def load_save_by_name(user_name : str) -> dict | int:
    user_id = get_id_from_name(user_name)
    if user_id == -1:
        return -1
    else:
        return load_save_by_id(user_id)


def modify_save_by_id(user_id : int, json_data : dict) -> None:
    __saves[str(user_id)] = json_data
    f = open(os.path.join(PROJECT_ROOT, "data", "users", str(user_id) + ".json"), "w", encoding="utf-8")
    f.write(json.dumps(json_data))
    f.close()

def get_id_from_name(user_name : str) -> int:
    try:
        f = open(os.path.join(PROJECT_ROOT, "data", "users", "nametoid", str(user_name)), "r", encoding="utf-8")
        user_id = int(f.read())
        f.close()
        return user_id
    except FileNotFoundError:
        return -1

def user_id_exists(user_id : int) -> bool:
    return load_save_by_id(user_id) != -1

def user_name_exists(user_name : str) -> bool:
    return load_save_by_name(user_name) != -1

def create_new_account(uid : int, username : str, password : str, token : str) -> None:
    json_data = NEW_ACCOUNT_DATA.copy()
    f = open(os.path.join(PROJECT_ROOT, "data", "users", str(uid) + ".json"), "w+", encoding="utf-8")
    json_data["playerData"]["account_id"] = uid
    json_data["playerData"]["user_name"] = username
    json_data["playerData"]["password"] = password

    #################################################################
    # Change user-id everywhere [WHY :-( ]                          #
    #################################################################
    json_data["goals"]["player_id"] = uid                           #
    json_data["backgrounds"][0]["player_id"] = uid                  #
    json_data["planes"][0]["to_player_id"] = uid                    #
    json_data["runways"][0]["player_id"] = uid                      #
    json_data["hangars"][0]["player_id"] = uid                      #
    j = 0                                                           #
    for i in json_data["landsideBuildings"]:                        #
        json_data["landsideBuildings"][j]["player_id"] = uid        #
        j = j + 1                                                   #
    json_data["accountData"]["id"] = uid                            #
    json_data["accountData"]["user_name"] = username                #
    json_data["expeditionstatus"]["player_id"] = uid                #
    json_data["playerData"]["token"] = token                        #
    #################################################################

    f.write(json.dumps(json_data))
    f.close()


    # Create a nametoid file
    f = open(os.path.join(PROJECT_ROOT, "data", "users", "nametoid", str(username)), "w+", encoding="utf-8")
    f.write(str(uid))
    f.close()

def read_location_id(file : str) -> tuple[str, int]:
    with open(os.path.join(PROJECT_ROOT, "data", "users", file), "r", encoding="utf-8") as f:
        json_data = json.load(f)
    return file[0:-5], json_data["playerData"]["location_id"]
    

def save_players_by_location_id():
    all_files = [x for x in os.listdir(os.path.join(PROJECT_ROOT, "data", "users")) if x.endswith(".json")]
    with ThreadPoolExecutor() as executor:
        for user_id, result in executor.map(read_location_id, all_files):
            if result not in __world_map_players:
                __world_map_players[result] = []
            __world_map_players[result].append(int(user_id))


    for i in range(241):
        # There are 240 countries right now.
        # Not all ids exist, but we don't care as it doesn't hurt
        if i in __world_map_players:
            # The original game uses a completely random order.
            # We'd like to prioritize online users, but instead of checking this on server start
            # we're putting them on the beginning of the list when they enable their buddyping.
            random.shuffle(__world_map_players[i])
        else:
            __world_map_players[i] = [800] # NPC player

def buddyping_enabled(user_id, location_id):
    player_list = __world_map_players[location_id]
    old_index = player_list.index(int(user_id))
    player_list.insert(0, player_list.pop(old_index))

def get_accounts_by_location_id(location_id, amount, own_user_id):
    player_list = __world_map_players[location_id]
    player_list_cropped = [ x for x in player_list[0:(amount+1 if int(own_user_id) in player_list else amount)] if x != int(own_user_id) ]

    # Ducktape fix for if you're the only person in your country
    if player_list_cropped == []:
        player_list_cropped = [800]

    return player_list_cropped

def get_player_count() -> int:
    return __playerCount["count"]

def add_to_player_count(amount : int) -> None:
    __playerCount["count"] += amount