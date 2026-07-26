import time
import src.user_manager as user_manager
import logging

def handle_accountGetLatest(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = []

    # The request from the game contains "numAccounts" as well
    # To prevent abusing we hardcode it here instead (numAccounts = 30) + we don't add last_ping_time

    player_list = user_manager.get_accounts_by_location_id(request["p"]["locationId"],30,user_id)

    logging.debug(f"Found {len(player_list)} players in location ID {request['p']['locationId']} for user {user_id}")

    # One query for up to 30 usernames. This used to call load_save_by_id per
    # player - a full save each, planes included - to read one string. It also
    # crashed with TypeError if any id had since been deleted, because
    # load_save_by_id returns -1 rather than a dict.
    usernames = user_manager.get_usernames_bulk([p for p in player_list if p != 800])

    for player in player_list:
        username = "NPC" if player == 800 else usernames.get(player)

        if username is None:
            logging.warning(f"account_getLatest: player {player} is in the world map but not in the database, skipping")
            continue

        rpcResult["r"].append({"username":username,"player_id":player,"last_ping_time":0})