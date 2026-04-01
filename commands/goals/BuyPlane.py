def handle_BuyPlane(request, user_id, json_data, task, task_number, init_data, quest_seq):
    if request["m"] == "planes.buy":
        if task["obj_type_id"] == request["p"]["typeId"]:
            json_data["goals"]["goals"][quest_seq]["tasks"][task_number]["num_completed"] = json_data["goals"]["goals"][quest_seq]["tasks"][task_number]["num_completed"] + 1
    
    return json_data
