import time
from pathlib import Path
import os
import json

def handle_addObj(request, user_id, obj, total_items_to_add_to_obj, json_data, init_data, obj_data):
    obj["player"] = {}
    obj["player"]["next_object_id"] = json_data["playerData"]["next_object_id"]
    obj["player"]["air_coins"] = json_data["playerData"]["air_coins"]
    obj["player"]["air_cash"] = json_data["playerData"]["air_cash"]
    obj["player"]["event_currency"] = json_data["playerData"]["event_currency"]
    obj["player"]["event_materials"] = []
    obj["player"]["xp"] = json_data["playerData"]["xp"]
    obj["player"]["super_fuel"] = json_data["playerData"]["super_fuel"]
    obj["player"]["passengers"] = json_data["playerData"]["passengers"]
    obj["player"]["last_buddyping_time"] = json_data["playerData"]["last_buddyping_time"]
    obj["player"]["aycqs_start_time"] = json_data["playerData"]["aycqs_start_time"]
    obj["player"]["scrap_block_time"] = json_data["playerData"]["scrap_block_time"]

    obj["system"] = obj_data["system"]
    obj["maintenance"] = obj_data["maintenance"]
    obj["events"] = obj_data["events"]
    obj["paymentBaskets"] = obj_data["paymentBaskets"]
    obj["flashCookies"] = []

    for i in total_items_to_add_to_obj:
        splitted = i.split(":")
        name = splitted[0]
        splitted.pop(0)

        if name in json_data:
            data = json_data[name]
        elif name in init_data:
            data = init_data[name]

        if len(splitted) == 0:
            obj[name] = data
        else:
            result = []
            for j in splitted:

                for k in data:
                    if int(k["id"]) == int(j):
                        result.append(k)
                        break

            obj[name] = result
          
        
    