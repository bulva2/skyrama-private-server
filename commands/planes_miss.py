import time

def handle_planesMiss(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = {}
    rpcResult["r"]["planes"] = {}

    j = 0
    for i in json_data["planes"]:
      if int(i["id"]) == request["p"]["id"]:
        if request["p"]["player_id"] == 0: # Cashcow, so make it appear on radar again.
            json_data["planes"][j]["flight_status"] = 77
            json_data["planes"][j]["departure_time"] = request["t"] - 450
            json_data["planes"][j]["arrival_time"] = request["t"] + 450
            json_data["planes"][j]["start_service_time"] = 0
            json_data["planes"][j]["last_state_change_time"] = request["t"]
            json_data["planes"][j]["player_id"] = request["p"]["player_id"]
            json_data["planes"][j]["subcontainer_id"] = -1
            json_data["planes"][j]["container_id"] = -1
            json_data["planes"][j]["to_player_id"] = request["p"]["to_player_id"]
            json_data["planes"][j]["instantland"] = 0
        else:
          json_data["planes"].pop(j)
        break
      j = j + 1