from src.debug import report_issue
import time
import src.user_manager as user_manager

def handle_getBuddyInitState(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
   rpcResult["i"] = request["i"]
   rpcResult["t"] = int(time.time())

   json2_data = user_manager.load_save_by_id(request["p"])

   if isinstance(json2_data, int):
      report_issue("warning", f"getBuddyInitState: Failed to load buddy data for user_id {request['p']} from user_id {user_id}")
      rpcResult["r"] = False
      return

   buddy_data = {}
   buddy_data["hangars"] = json2_data["hangars"]
   buddy_data["bays"] = json2_data["bays"]
   buddy_data["runways"] = json2_data["runways"]
   buddy_data["terminals"] = json2_data["terminals"]
   buddy_data["landsideBuildings"] = json2_data["landsideBuildings"]
   buddy_data["cargoShops"] = json2_data["cargoShops"]
   buddy_data["warehouses"] = json2_data["warehouses"]
   buddy_data["planes"] = json2_data["planes"]
   buddy_data["specialBuildings"] = json2_data["specialBuildings"]

   # Only the active background gets sent.
   for i in json2_data["backgrounds"]:
      if int(i["in_storage"]) == 0:
         buddy_data["background"] = i
         break
      
   buddy_data["max_passengers_per_day"] = 5

   rpcResult["r"] = buddy_data
    