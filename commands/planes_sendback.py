import time
from pathlib import Path
import os
import json
import src.userManager as userManager

def handle_planesSendback(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = str(int(time.time()))
    rpcResult["r"] = None
    items_to_add_to_obj.append(f"planes:{request["p"]["id"]}")

    p = Path(__file__).parents[1]     
    
    j = 0
    for i in json_data["planes"]:
        if int(i["id"]) == request["p"]["id"]:
            plane_type_id = int(i["plane_type_id"])
            if request["p"]["player_id"] == 0: # Cashcow, so make it appear on radar again.
                json_data["planes"][j]["flight_status"] = 77
                json_data["planes"][j]["departure_time"] = request["t"] - 450
                json_data["planes"][j]["arrival_time"] = request["t"] + 450
                json_data["planes"][j]["start_service_time"] = 0
                json_data["planes"][j]["last_state_change_time"] = request["p"]["last_state_change_time"]
                json_data["planes"][j]["player_id"] = request["p"]["player_id"]
                json_data["planes"][j]["subcontainer_id"] = request["p"]["subcontainer_id"]
                json_data["planes"][j]["container_id"] = request["p"]["container_id"]
                json_data["planes"][j]["to_player_id"] = request["p"]["to_player_id"]
                json_data["planes"][j]["instantland"] = request["p"]["instantland"]
            else:
                for g in init_data["planeTypes"]:
                  if int(g["id"]) == plane_type_id:
                    buddy_points = int(g["buddy_points_yield"])
                    load_type = g["load_type"]
                    break
                  
                '''
                for file in os.listdir(os.path.join(p, "data")):
                    if file[0:8] == str(json_data["planes"][j]["player_id"]):
                        player_from_file = file
                        break
                f = open(os.path.join(p, "data", player_from_file), "r")
                json2_data = json.loads(str(f.read()))
                f.close()
                '''
                buddy_id = int(json_data["planes"][j]["player_id"])

                json2_data = userManager.load_save_by_id(buddy_id)

                # When returning a plane from a stranger, add them to the buddylist.
                in_buddy_list = False
                for buddy in json_data["buddyStuff"]["buddies"]:
                   if int(buddy["hi_player_id"]) == buddy_id:
                      in_buddy_list = True

                if not in_buddy_list:
                    json_data["buddyStuff"]["buddies"].append({"lo_player_id":str(user_id),"hi_player_id":str(buddy_id),"status":"0","buddy_points":buddy_points,"num_hits":"0","task_visit":"0","num_flights_today":"0","todays_first_flight_time":"0","todays_first_collected_passengers_time":"0","todays_collected_passengers":"0","received_passengers":"0","last_ping_time":1674583733,"last_buddyping_time":0,"xp":json2_data["playerData"]["xp"],"online":0,"location_id":json2_data["playerData"]["location_id"],"username":json2_data["playerData"]["user_name"]})
                    json2_data["buddyStuff"]["buddies"].append({"lo_player_id":str(buddy_id),"hi_player_id":str(user_id),"status":"0","buddy_points":"0","num_hits":"0","task_visit":"0","num_flights_today":"0","todays_first_flight_time":"0","todays_first_collected_passengers_time":"0","todays_collected_passengers":"0","received_passengers":"0","last_ping_time":1674583733,"last_buddyping_time":0,"xp":json_data["playerData"]["xp"],"online":0,"location_id":json_data["playerData"]["location_id"],"username":json_data["playerData"]["user_name"]})
                    # 0 buddypoints for second player because they still have to handle the plane on their airport
                
                for g in json2_data["planes"]:
                  if int(g["id"]) == int(i["fromUser_objectId"]):
                    # Returning plane should give buddy points and double xp, aircoins and cargo
                    g["buddy_points"] = buddy_points
                    g["xp"] = int(g["xp"]) * 2
                    g["air_coins"] = int(g["air_coins"]) * 2 # Cargo planes don't give these, but doesn't hurt multliplying 0 by 2 xD
                    if load_type == "Cargo":
                       g["contents_count"] = int(g["contents_count"]) * 2
                    
                    break

                json_data["planes"].pop(j)
            
        j = j + 1
    
    if request["p"]["player_id"] != 0:
      '''
      f = open(os.path.join(p, "data", player_from_file), "w")
      f.write(json.dumps(json2_data))
      f.close()
      '''
      userManager.modify_save_by_id(json2_data["playerData"]["account_id"], json2_data)
