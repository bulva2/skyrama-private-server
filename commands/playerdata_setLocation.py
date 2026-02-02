import time
import src.user_manager as user_manager

def handle_setLocation(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = None

    json_data["playerData"]["location_id"] = request["p"]["location_id"]

    # Add player to __world_map_players in userManager
    user_manager.add_player_to_world_list(user_id, request["p"]["location_id"])