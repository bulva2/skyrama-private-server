import time

def handle_placeablePlace(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = str(int(time.time()))
    rpcResult["r"] = None

    if request["p"]["obj_type"] == "bay":
        for i in json_data["bays"]:
            if int(i["id"]) == int(request["p"]["obj_id"]):
                i["position_x"] = request["p"]["x"]
                i["position_y"] = request["p"]["y"]
                i["direction"] = request["p"]["d"]
    elif request["p"]["obj_type"] == "special":
        for i in json_data["specialBuildings"]:
            if int(i["id"]) == int(request["p"]["obj_id"]):
                i["position_x"] = request["p"]["x"]
                i["position_y"] = request["p"]["y"]
                i["direction"] = request["p"]["d"]
    elif request["p"]["obj_type"] == "runway":
        for i in json_data["runways"]:
            if int(i["id"]) == int(request["p"]["obj_id"]):
                i["position_x"] = request["p"]["x"]
                i["position_y"] = request["p"]["y"]
                i["direction"] = request["p"]["d"]
    elif request["p"]["obj_type"] == "landside_building":
        for i in json_data["landsideBuildings"]:
            if int(i["id"]) == int(request["p"]["obj_id"]):
                i["position_x"] = request["p"]["x"]
                i["position_y"] = request["p"]["y"]
                i["direction"] = request["p"]["d"]
    elif request["p"]["obj_type"] == "terminal":
      for i in json_data["terminals"]:
        if int(i["id"]) == int(request["p"]["obj_id"]):
          i["position_x"] = request["p"]["x"]
          i["position_y"] = request["p"]["y"]
          i["direction"] = request["p"]["d"]
    elif request["p"]["obj_type"] == "warehouse":
      for i in json_data["warehouses"]:
        if int(i["id"]) == int(request["p"]["obj_id"]):
          i["position_x"] = request["p"]["x"]
          i["position_y"] = request["p"]["y"]
          i["direction"] = request["p"]["d"]
    elif request["p"]["obj_type"] == "cargoshop":
      for i in json_data["cargoShops"]:
        if int(i["id"]) == int(request["p"]["obj_id"]):
          i["position_x"] = request["p"]["x"]
          i["position_y"] = request["p"]["y"]
          i["direction"] = request["p"]["d"]
    elif request["p"]["obj_type"] == "hangar":
      for i in json_data["hangars"]:
        if int(i["id"]) == int(request["p"]["obj_id"]):
          i["position_x"] = request["p"]["x"]
          i["position_y"] = request["p"]["y"]
          i["direction"] = request["p"]["d"]