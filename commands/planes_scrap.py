from src.debug import report_issue
import time

def handle_planesScrap(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = None
    items_to_add_to_obj.append("planes")

    if json_data["playerData"]["scrap_block_time"] > int(time.time()):
        # Possible cheat, disconnect user
        report_issue("warning", f"planes_scrap: User {json_data['playerData']['user_name']} (ID: {user_id}) attempted to scrap a plane while on cooldown. Block time remaining: {json_data['playerData']['scrap_block_time'] - int(time.time())} seconds.")
        rpcResult["i"] = -1
    
    for idx, plane in enumerate(json_data["planes"]):
        if int(plane["id"]) == request["p"]["id"]:
            json_data["planes"].pop(idx)
            break
      
    json_data["playerData"]["scrap_block_time"] = int(time.time()) + 21600