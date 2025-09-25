def handle_PlaceLandsideBuilding(request, user_id, json_data, task, task_number, init_data, quest_seq):
    if request["m"] == "placeable.place":
        if request["p"]["obj_type"] == "landside_building":
            for building in json_data["landsideBuildings"]:
                if int(building["id"]) == int(request["p"]["obj_id"]):
                    if int(task["obj_type_id"]) == int(building["landside_building_types_id"]) or int(task["obj_type_id"]) == -1:
                        json_data["goals"]["goals"][quest_seq]["tasks"][task_number]["num_completed"] += 1
                        break
    elif request["m"] == "landside_buildings.buy":
        for building in json_data["landsideBuildings"]:
            if int(building["id"]) == int(request["p"]["id"]):
                if int(task["obj_type_id"]) == int(building["landside_building_types_id"]) or int(task["obj_type_id"]) == -1:
                    json_data["goals"]["goals"][quest_seq]["tasks"][task_number]["num_completed"] += 1
                    break
    
    return json_data
