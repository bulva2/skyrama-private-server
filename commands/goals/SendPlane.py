def handle_SendPlane(request, user_id, json_data, task, task_number, init_data, quest_seq):
    if request["m"] == "planes.send":
        print(task)

        conditions_completed = 0
        type_id = 34 # Edge case: Fly-By
        to_location_id = None
        size = None
        plane_type = None
        continent = None
        for i in json_data["planes"]:
            if int(i["id"]) == int(request["p"]["id"]):
                type_id = int(i["plane_type_id"])
                to_location_id = int(i["to_location_id"])
                break

        for i in init_data["planeTypes"]:
            if int(i["id"]) == type_id:
                size = i["size"]
                plane_type = i["type"]
                for j in json_data["locations"]:
                    if int(j["id"]) == to_location_id:
                        continent = j["continent"]
                        break

        if int(task["obj_type_id"]) == type_id or int(task["obj_type_id"]) == -1:
            conditions_completed += 1
        
        if task["size"] == size or task["size"] == None:
            conditions_completed += 1

        if task["plane_type"] == plane_type or task["plane_type"] == None:
            conditions_completed += 1

        if task["continent"] == continent or task["continent"] == None:
            conditions_completed += 1

        if task["location_id"] == to_location_id or task["location_id"] == None:
            conditions_completed += 1

        if conditions_completed == 5:
            json_data["goals"]["goals"][quest_seq]["tasks"][task_number]["num_completed"] += 1

#        if int(task["goal_types_id"]) == 4: # Tutorial, speed up Cashcow
#            json_data["planes"][0]["departure_time"] = int(time.time()) - 0
#            json_data["planes"][0]["arrival_time"] = int(time.time()) + 150

    return json_data
