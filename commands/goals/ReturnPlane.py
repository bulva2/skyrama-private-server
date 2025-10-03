def handle_ReturnPlane(request, user_id, json_data, task, task_number, init_data, quest_seq):
    if request["m"] == "planes.sendback":

        if task["user_action"] != "ReturnPlane":
            return json_data

        # In case this don't change: CashCow
        type_id = 0
        from_location_id = -1
        size = "Small"
        plane_type = "plane"

        for i in json_data["planes"]:
            if int(i["id"]) == int(request["p"]["id"]):
                type_id = int(i["plane_type_id"])
                from_location_id = int(i["from_location_id"])
                for j in init_data["planeTypes"]:
                    if int(j["id"]) == type_id:
                        size = j["size"]
                        plane_type = j["type"]
                        break
                break

        # Apparantly only one thing at a time, might need a fix if we ever add new missions

        if task["obj_type_id"] == type_id:
            json_data["goals"]["goals"][quest_seq]["tasks"][task_number]["num_completed"] += 1
        elif task["size"] == size:
            json_data["goals"]["goals"][quest_seq]["tasks"][task_number]["num_completed"] += 1
        elif task["plane_type"] == plane_type:
            json_data["goals"]["goals"][quest_seq]["tasks"][task_number]["num_completed"] += 1
        elif task["location_id"] == from_location_id:
            json_data["goals"]["goals"][quest_seq]["tasks"][task_number]["num_completed"] += 1
        elif task["size"] == None and task["obj_type_id"] == -1 and task["plane_type"] == None and task["location_id"] == None:
            json_data["goals"]["goals"][quest_seq]["tasks"][task_number]["num_completed"] += 1

    return json_data
