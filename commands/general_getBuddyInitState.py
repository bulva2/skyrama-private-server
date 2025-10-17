import time
import src.userManager as userManager

def handle_getBuddyInitState(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())

    '''
    p = Path(__file__).parents[1]  

    for file in os.listdir(os.path.join(p, "data")):
      if file[0:8] == str(request["p"]):
        break
    f = open(os.path.join(p, "data", file), "r")
    json2_data = json.loads(str(f.read()))
    f.close()

    '''

    json2_data = userManager.load_save_by_id(request["p"])

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
    