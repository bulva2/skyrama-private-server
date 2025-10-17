import logging
import time
from src.debug import send_webhook
from src.utils import substract_resources

def handle_craftingInstant(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = False

    p = request["p"]
    found = False

    for slot in json_data.get("userCraftingSlots", {}):
        if slot["slotId"] == int(p["slotId"]):
            process_data = slot.get("processData", -1)

            if process_data == -1:
                send_webhook(json_data, user_id, request)
                rpcResult["i"] = -1
                return

            # Prevent cheating by injecting different planeId
            if p["planeId"] != process_data["itemId"]:
                # To-do: Replace with anticheat webhook
                send_webhook(json_data, user_id, request, additional_data=process_data)
                rpcResult["i"] = -1
                return
            
            # Calculate the price of the skip 
            # (We start at 48 aircoins and deduct 1 for every 30min)
            time_remaining = process_data["endtime"] - int(time.time())
            skip_cost = max(1, min(48, (time_remaining // 1800) + 1))

            substract_resources(json_data, rpcResult, air_cash=skip_cost)
            logging.debug(f"Deducted {skip_cost} air coins for crafting skip for user {user_id}")

            slot["processData"] = []
            slot["processId"] = 0

            found = True
            break

    if not found:
        send_webhook(json_data, user_id, request)
        rpcResult["i"] = -1
        return
    
    currentCraftings = json_data.get("userCurrentCraftings", -1)

    if currentCraftings == -1:
        send_webhook(json_data, user_id, request)
        rpcResult["i"] = -1
        return
    
    for i in init_data["planeTypes"]:
        if int(i["id"]) == int(p["planeId"]):
            json_data["planes"].append(
                {
                    "souvenir_types_id":-1,
                    "active_count":1,
                    "id":json_data["playerData"]["next_object_id"],
                    "plane_type_id":p["planeId"],
                    "container_id":33, # Hardcoded value, no idea what it means
                    "subcontainer_id":1, # Hardcoded value, no idea what it means
                    "to_player_id":-1,
                    "departure_time":-1,
                    "arrival_time":-1,
                    "kerosene_boost_flag":"0",
                    "flight_status":"77",
                    "buddy_points":i["buddy_points_yield"],
                    "contents_count":i["capacity"],
                    "air_coins":i["air_coins_yield"],
                    "xp":i["xp_yield"],
                    "wares_revenue":i["wares_revenue_capacity"],
                    "banner_id":"-1",
                    "start_service_time":"0",
                    "last_state_change_time":"0",
                    "drop_consumable_id":"0",
                    "drop_consumable_amount":"0",
                    "instantland":0,
                    "player_id":user_id,
                    "from_location_id":-1,
                    "from_user_name":"drone",
                    "upgrade_level":0
            }
        )
    
    currentCraftings.pop(str(p["planeId"]), None)

    json_data["playerData"]["crafting_totalXP"] += 10
    json_data["playerData"]["next_object_id"] += 1

    rpcResult["r"] = {
        "status": True, 
        "result": {
            "craftingXp": 10,
            "itemId": p["planeId"]
        },
        "slotId": p["slotId"],
        "slotType": p["slotType"],
        "processType": "crafting"
    }
