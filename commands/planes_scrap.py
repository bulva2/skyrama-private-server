import time

def handle_planesScrap(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = str(int(time.time()))
    rpcResult["r"] = None
    items_to_add_to_obj.append("planes")

    if json_data["playerData"]["scrap_block_time"] > int(time.time()):
       # Possible cheat, disconnect user
       rpcResult["i"] = -1

    j = 0
    for i in json_data["planes"]:
      if int(i["id"]) == request["p"]["id"]:
        json_data["planes"].pop(j)
      j = j + 1
      
    json_data["playerData"]["scrap_block_time"] = int(time.time()) + 21600