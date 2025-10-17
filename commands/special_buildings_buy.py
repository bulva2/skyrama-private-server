import time
from src.utils import substract_resources

def handle_specialBuildingsBuy(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = None

    # Prevent people from buying more than one building of each type
    for i in json_data["specialBuildings"]:
       if int(i["special_building_types_id"]) == int(request["p"]["types_id"]):
          rpcResult["i"] = -1
          return

    for i in init_data["specialBuildingTypes"]:
      if int(i["id"]) == int(request["p"]["types_id"]):
        substract_resources(json_data, rpcResult, i["air_coins_cost"], i["air_cash_cost"], i["event_currency_cost"])
            
        json_data["specialBuildings"].append({"sbId":"1","special_building_types_id":request["p"]["types_id"],"id":json_data["playerData"]["next_object_id"],"position_x":request["p"]["position_x"],"position_y":request["p"]["position_y"],"direction":request["p"]["direction"],"player_id":user_id})
        # What is sbId??? Doesn't seem to matter for now
    
        json_data["playerData"]["next_object_id"] = int(json_data["playerData"]["next_object_id"]) + 1