import time

def handle_buddyReceivePassengers(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = None

    buddies = json_data["buddyStuff"]["buddies"]

    for buddy in buddies:
        if buddy["received_passengers"] > 0 and buddy["lo_player_id"] == user_id:
            print(f"Receiving {buddy['received_passengers']} passengers from buddy with hi_player_id {buddy['hi_player_id']} and lo_player_id {buddy['lo_player_id']}")
            json_data["playerData"]["passengers"] += buddy["received_passengers"]
            buddy["received_passengers"] = 0
        else:
            print(f"No passengers to receive from buddy with hi_player_id {buddy['hi_player_id']} and lo_player_id {buddy['lo_player_id']}")

    rpcResult["r"] = True