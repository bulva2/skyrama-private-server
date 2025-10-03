import time
from pathlib import Path
import logging
import random
import src.userManager as userManager

def handle_planesSend(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = str(int(time.time()))
    rpcResult["r"] = {}
    rpcResult["r"]["planes"] = {}

    p = Path(__file__).parents[1]  

    json2_data = None
    #player_to_file = 0
    j = 0
    for i in json_data["planes"]:
        if int(i["id"]) == request["p"]["id"]:
            json_data["planes"][j]["departure_time"] = request["p"]["departure_time"]
            json_data["planes"][j]["kerosene_boost_flag"] = request["p"]["kerosene_boost_flag"]
            json_data["planes"][j]["last_state_change_time"] = request["p"]["last_state_change_time"]
            json_data["planes"][j]["subcontainer_id"] = request["p"]["subcontainer_id"]
            json_data["planes"][j]["container_id"] = request["p"]["container_id"]
            json_data["planes"][j]["arrival_time"] = request["p"]["arrival_time"]  
            json_data["planes"][j]["flight_status"] = 77
            json_data["planes"][j]["from_user_name"] = json_data["playerData"]["user_name"]
            json_data["planes"][j]["from_location_id"] = json_data["playerData"]["location_id"]
            json_data["planes"][j]["buddy_points"] = 0
            json_data["planes"][j]["fromUser_objectId"] = int(i["id"]) # So buddies know the right plane id
                
            plane_type_id = int(i["plane_type_id"])
            for g in init_data["planeTypes"]:
                if int(g["id"]) == plane_type_id:
                    xp = g["xp_yield"]
                    coins = g["air_coins_yield"]
                    service_time = g["service_length"]
                    quick_start_coins_cost = g["quick_start_coins_cost"]
                    buddy_points = int(g["buddy_points_yield"])
                    load_type = g["load_type"]
                    wares_revenue = int(g["wares_revenue_capacity"])
                    contents_count = int(g["capacity"])
                    recycling_value = int(g["recyclingValue"]) # L parts drop is depending on this number (6 random sequences)
                    break
                
            # Setup xp and coins (will be doubled in planes.sendback when the plane gets serviced by the buddy)

            json_data["planes"][j]["xp"] = xp
            json_data["planes"][j]["air_coins"] = coins            

            if load_type == "Cargo": # Cargo planes don't drop souvenirs, but cargo + L parts

              # Setup cargo

              json_data["planes"][j]["contents_count"] = contents_count
              json_data["planes"][j]["wares_revenue"] = wares_revenue

              # Setup L parts

              material_chances = init_data["materialChances"][str(recycling_value)]
              random_chance = random.random()
              chance = float(0)
              for g in material_chances:
                 chance += float(g["Chance"])
                 if chance > random_chance:
                    material_id = int(g["MaterialId"])
                    amount = random.randint(int(g["MinAmount"]), int(g["MaxAmount"]))
                    json_data["planes"][j]["drop_material"] = material_id
                    json_data["planes"][j]["drop_material_amount"] = amount

            else:
              json_data["planes"][j]["drop_material"] = 0
              json_data["planes"][j]["drop_material_amount"] = 0

              # Handle souvenir drop / avoid race condition
              if json_data["planes"][j].get("to_location_id") is None:
                json_data["planes"][j]["souvenir_types_id"] = -1
                logging.warning("planes_send: to_location_id is None! This has to be a race condition!")
              else:
                for g in json_data["locations"]:
                  if int(g["id"]) == int(json_data["planes"][j]["to_location_id"]):

                    # Flight time from initData
                    flight_time_seconds = 0
                    for plane_data in init_data["planeTypes"]:
                        if int(plane_data["id"]) == plane_type_id:
                            flight_time_seconds = int(plane_data.get("flight_time", 3600))
                            break
                      
                    flight_time_hours = flight_time_seconds / 3600

                    # Determine event currency drop chance based on flight time
                    if flight_time_hours >= 24:
                        event_currency_chance = 0.60
                    elif flight_time_hours >= 18:
                        event_currency_chance = 0.45
                    elif flight_time_hours >= 16:
                        event_currency_chance = 0.40
                    elif flight_time_hours >= 12:
                        event_currency_chance = 0.30
                    elif flight_time_hours >= 10:
                        event_currency_chance = 0.25
                    elif flight_time_hours >= 8:
                        event_currency_chance = 0.20
                    elif flight_time_hours >= 6:
                        event_currency_chance = 0.15
                    elif flight_time_hours >= 4:
                        event_currency_chance = 0.10
                    else:
                        event_currency_chance = 0.03 # 3% for shorter flights than 4hrs so ppl don't abuse it to farm event currency
                    
                    # Let's go gambliing! (Event currency drop)
                    if random.random() < event_currency_chance:
                        souvenir = -2  # Event currency drop yupieee
                    else:
                        # Oh dang it
                        souvenir_num = random.randint(1, 3)
                        souvenir = g["souvenir_types_id_" + str(souvenir_num)]

                    json_data["planes"][j]["souvenir_types_id"] = souvenir
                    break
                    
            if (int(request["t"]) - int(i["start_service_time"])) < ((int(service_time) / 3) * 2) or int(i["start_service_time"]) == 0:
              if int(request["t"]) > int(json_data["playerData"]["aycqs_start_time"]):
                json_data["playerData"]["air_cash"] = int(json_data["playerData"]["air_cash"]) - int(quick_start_coins_cost)   

                
                
            if int(json_data["planes"][j]["to_player_id"]) != 800: # ID 800 = NPC player
              '''
              print(os.listdir(os.path.join(p, "data")))
              for file in os.listdir(os.path.join(p, "data")):
                print(str(json_data["planes"][j]["to_player_id"]))

                if file[0:8] == str(json_data["planes"][j]["to_player_id"]):
                  print(file)
                  player_to_file = file
                  break

              f = open(os.path.join(p, "data", player_to_file), "r")
              json2_data = json.loads(str(f.read()))
              f.close()
              '''
              json2_data = userManager.load_save_by_id(json_data["planes"][j]["to_player_id"])
              
              last_id = int(json2_data["playerData"]["next_object_id"])
              copy = json_data["planes"][j].copy()
              copy["id"] = last_id + 1
              copy["buddy_points"] = buddy_points
              copy["xp"] = xp * 2 # Servicing a buddy's plane gives double xp, but same amount of coins
              copy["air_coins"] = coins

              json2_data["planes"].append(copy)
              
              json2_data["playerData"]["next_object_id"] = int(json2_data["playerData"]["next_object_id"]) + 1

              rpcResult["r"]["planes"][str(request["p"]["id"])] = json_data["planes"][j]
        j = j + 1
    
    if json2_data != None:
      '''
      f = open(os.path.join(p, "data", player_to_file), "w")
      f.write(json.dumps(json2_data))
      f.close()
      '''
      userManager.modify_save_by_id(json2_data["playerData"]["account_id"], json2_data)