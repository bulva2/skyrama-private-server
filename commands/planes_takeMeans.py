import math
import time
from src.debug import report_issue
from src.easy_events import get_coin_multiplier, get_xp_multiplier

def calculate_warehouse_capacity(upgrade_level, init_data):
    start_amount = int(init_data["cargoUpgrades"][0]["increment"])
    upgrade_amount = int(init_data["cargoUpgrades"][1]["increment"])
    warehouse_capacity = start_amount + \
        (int(upgrade_level) - 1) * upgrade_amount

    return warehouse_capacity


def handle_planesTakeMeans(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = None

    for plane in json_data["planes"]:
        if int(plane["id"]) == request["p"]["plane_id"]:
            plane_type_id = int(plane["plane_type_id"])

            ######################################
            # Required because not being sent \/ #
            ######################################

            # Check own/buddy plane's location
            if int(request["p"]["owner_id"]) == int(user_id):
                # Own plane - should use destination location (to_location_id)
                if "to_location_id" in plane and plane["to_location_id"] is not None:
                    location_id = int(plane["to_location_id"])
                else:
                    # Race condition detected - setState hasn't run yet
                    report_issue("warning", f"planes_takeMeans: Race condition detected for own plane id {plane['id']} - to_location_id missing/None!")
                    if "from_location_id" in plane:
                        report_issue("warning", f"planes_takeMeans: Using 'from_location_id' as fallback for own plane id {plane['id']} (SEMANTICALLY INCORRECT)")
                        location_id = int(plane["from_location_id"])
                    else:
                        report_issue("warning", f"planes_takeMeans: Using player's location as fallback for own plane id {plane['id']}")
                        location_id = json_data["playerData"]["location_id"]
            else:
                # Buddy plane - should use origin location (from_location_id) 
                if "from_location_id" in plane and plane["from_location_id"] is not None:
                    location_id = int(plane["from_location_id"])
                else:
                    # Race condition detected
                    report_issue("warning", f"planes_takeMeans: Race condition detected for buddy plane id {plane['id']} - from_location_id missing/None!")
                    if "to_location_id" in plane:
                        report_issue("warning", f"planes_takeMeans: Using 'to_location_id' as fallback for buddy plane id {plane['id']} (SEMANTICALLY INCORRECT)")
                        location_id = int(plane["to_location_id"])
                    else:
                        report_issue("warning", f"planes_takeMeans: Using player's location as fallback for buddy plane id {plane['id']}")
                        location_id = json_data["playerData"]["location_id"]

            # Check drop material + amount of it (+ workaround for missing data)
            if "drop_material" in plane:
                drop_material = int(plane["drop_material"])
            else:
                drop_material = 0

            if "drop_material_amount" in plane:
                drop_material_amount = int(plane["drop_material_amount"])
            else:
                drop_material_amount = 0

            ############################################################
            # Extra cheat checks (because we don't trust anyone xD) \/ #
            ############################################################

            buddy_points = int(plane["buddy_points"])

            wares_revenue = int(plane["wares_revenue"])

            contents_count = int(plane["contents_count"])

            souvenir_types_id = int(plane["souvenir_types_id"])

            for g in init_data["planeTypes"]:
                if int(g["id"]) == plane_type_id:
                    service_time = g["service_length"]
                    quick_start_coins_cost = g["quick_start_coins_cost"]
                    quick_buddy_serve_coins_cost = g["quick_buddy_serve_coins_cost"]
                    #####################################################################################
                    if "air_coins" in request["p"]:
                        json_data["playerData"]["air_coins"] += math.floor(request["p"]["air_coins"] * get_coin_multiplier())
                    #####################################################################################
                    elif "xp" in request["p"]:
                        json_data["playerData"]["xp"] += math.floor(request["p"]["xp"] * get_xp_multiplier())
                    #####################################################################################
                    elif "buddy_points" in request["p"]:
                        for h in json_data["buddyStuff"]["buddies"]:
                            if int(request["p"]["owner_id"]) == int(user_id): # plane sent by you
                                if int(h["hi_player_id"]) == int(plane["to_player_id"]):
                                    # Possible cheat, disconnect user
                                    if int(request["p"]["buddy_points"]) != buddy_points:
                                        report_issue("warning", f"planes_takeMeans: Buddy points mismatch for plane id {plane['id']}, User: {json_data['playerData']['user_name']} (ID: {user_id}). Expected: {buddy_points}, Reported: {request['p']['buddy_points']}")
                                        rpcResult["i"] = -1
                                        return
                                    h["buddy_points"] = int(h["buddy_points"]) + int(request["p"]["buddy_points"])
                                    break

                            else: # plane sent by your friend
                                if int(h["hi_player_id"]) == int(plane["player_id"]):
                                    h["buddy_points"] = int(h["buddy_points"]) + buddy_points
                                    break
                    #####################################################################################
                    elif "cargo" in request["p"]:
                        for h in json_data["locations"]:
                            if int(h["id"]) == location_id:
                                cargo_type = int(h["cargo_types_id"])
                                # Simplify the GetCargo quest script
                                request["p"]["cargo_types_id"] = cargo_type
                                break

                        setup_new_cargo_item = True
                        for k in json_data["cargo"]:
                            if int(k["cargo_types_id"]) == cargo_type:
                                setup_new_cargo_item = False
                                # Possible cheat, disconnect user
                                if int(request["p"]["cargo"] != contents_count):
                                    report_issue("warning", f"planes_takeMeans: Cargo amount mismatch for plane id {plane['id']}, User: {json_data['playerData']['user_name']} (ID: {user_id}). Expected: {contents_count}, Reported: {request['p']['cargo']}")
                                    rpcResult["i"] = -1
                                    return
                                k["num_in_warehouse"] += int(
                                    request["p"]["cargo"])
                                warehouse_capacity = calculate_warehouse_capacity(
                                    json_data["playerData"]["cargo_capacity_level"], init_data)
                                # Don't overstock (not sure if needed to be checked but it never hurts)
                                if k["num_in_warehouse"] > warehouse_capacity:
                                    k["num_in_warehouse"] = warehouse_capacity
                                break

                        if setup_new_cargo_item:  # Never collected this item before, add it to the list
                            json_data["cargo"].append({"cargo_types_id": cargo_type, "num_in_shop": 0, "num_in_warehouse": int(
                                request["p"]["cargo"]), "player_id": user_id})
                            
                    elif "souvenir_types_id" in request["p"] and int(request["p"]["souvenir_types_id"]) != -1:
                        # Event currency drop (-2)
                        if int(request["p"]["souvenir_types_id"]) == -2:
                            json_data["playerData"]["event_currency"] += 1
                        elif int(request["p"]["souvenir_types_id"]) is not None:
                            for h in json_data["souvenirCollections"]:
                                for k in h["items"]:
                                    if int(k["type_id"]) == int(request["p"]["souvenir_types_id"]):
                                        # Possible cheat, disconnect user
                                        if int(request["p"]["souvenir_types_id"]) != souvenir_types_id:
                                            report_issue("warning", f"planes_takeMeans: Souvenir type mismatch for plane id {plane['id']}, User: {json_data['playerData']['user_name']} (ID: {user_id}). Expected: {souvenir_types_id}, Reported: {request['p']['souvenir_types_id']}")
                                            rpcResult["i"] = -1
                                            return
                                        k["num"] = int(k["num"]) + 1
                        else:
                            report_issue("warning", f"planes_takeMeans: souvenir_types_id is None for plane id {plane['id']}, User: {json_data['playerData']['user_name']} (ID: {user_id})")

                    #####################################################################################
                    elif "drop_material" in request["p"]:
                        # Possible cheat, disconnect user
                        if int(request["p"]["drop_material"]) != drop_material:
                            report_issue("warning", f"planes_takeMeans: Drop material mismatch for plane id {plane['id']}, User: {json_data['playerData']['user_name']} (ID: {user_id}). Expected: {drop_material}, Reported: {request['p']['drop_material']}")
                            rpcResult["i"] = -1
                            return
                        str_drop_mat = str(request["p"]["drop_material"])
                        if str_drop_mat not in json_data["materials"]:
                            json_data["materials"][str_drop_mat] = drop_material_amount
                        else:
                            json_data["materials"][str_drop_mat] += drop_material_amount
                    #####################################################################################
                    elif "products_sold" in request["p"]:
                        highest_stock = 0
                        highest_stock_cargo_types_id = 0
                        for h in json_data["cargo"]:
                            if int(h["num_in_shop"]) > highest_stock:
                                highest_stock = int(h["num_in_shop"])
                                highest_stock_cargo_types_id = int(h["cargo_types_id"])
                        
                        if highest_stock != 0:
                            for k in init_data["cargoTypes"]:
                                if int(k["id"]) == highest_stock_cargo_types_id:
                                    highest_stock_shop_types_id = int(k["shop_id"])
                                    highest_stock_shop_level = int(k["shop_level"])
                                    break
                                
                            cargo_types_to_be_sold = []
                            for k in init_data["cargoTypes"]:
                                if int(k["shop_id"]) == highest_stock_shop_types_id and int(k["shop_level"]) <= highest_stock_shop_level:
                                    cargo_types_to_be_sold.append(int(k["id"]))
                                    break

                            for m in init_data["cargoShopLevels"]:
                                if int(m["shop_id"]) == highest_stock_shop_types_id and int(m["shop_level"]) == highest_stock_shop_level:
                                    level_up_amount = int(m["level_up_amount"])
                                    product_sell_gain = int(m["product_sell_gain"])
                                    break
                            
                            for l in json_data["cargoShops"]:
                                if int(l["cargo_shop_types_id"]) == highest_stock_shop_types_id:

                                    ###########################
                                    # Add the revenue + stats #
                                    ###########################

                                    l["products_sold"] = int(l["products_sold"]) + int(request["p"]["products_sold"])
                                    request["p"]["products_sold"] = int(request["p"]["products_sold"]) # Simplify the SellProducts quest script
                                    request["p"]["types_id"] = int(l["cargo_shop_types_id"]) # Simplify the SellProducts quest script
                                    l["sales_revenue"] = int(l["sales_revenue"]) + (int(request["p"]["products_sold"]) * product_sell_gain)

                                    ##################################
                                    # Remove the cargo from the shop #
                                    ##################################

                                    for h in json_data["cargo"]:
                                        if int(h["cargo_types_id"]) in cargo_types_to_be_sold:
                                            h["num_in_shop"] = int(h["num_in_shop"]) - int(request["p"]["products_sold"])


                                    if l["products_sold"] >= level_up_amount:
                                        l["upgrade_level"] = int(l["upgrade_level"]) + 1
                            
                        
                    break

            # CHECK IF QUICK SERVICE IS USED

            if int(request["p"]["owner_id"]) == int(user_id) and "xp" in request["p"]:
                # Add xp as temporary fix to check if it's the last drop before going into hangar.
                ##########################################################
                # This should be moved to planes.setState to avoid that! #
                ##########################################################
                if "xp" in request["p"]:
                    if (int(request["t"]) - int(plane["start_service_time"])) < (int(service_time) / 3) or int(plane["start_service_time"]) == 0:  # Own plane
                        if int(request["t"]) > int(json_data["playerData"]["aycqs_start_time"]):
                            json_data["playerData"]["air_cash"] -= int(quick_start_coins_cost)

            elif int(request["p"]["owner_id"]) != int(user_id):
                # Add xp as temporary fix. Plane id 0 = Cashcow
                ##########################################################
                # This should be moved to planes.setState to avoid that! #
                ##########################################################
                if ("xp" in request["p"]) or (int(request["p"]["plane_id"]) == 0 and "air_coins" in request["p"]):
                    # Buddy plane
                    if (request["t"] - plane["start_service_time"]) < service_time or plane["start_service_time"] == 0:
                        if int(request["t"]) > int(json_data["playerData"]["aycqs_start_time"]):
                            json_data["playerData"]["air_cash"] -= quick_buddy_serve_coins_cost