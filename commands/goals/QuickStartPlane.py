def handle_QuickStartPlane(request, user_id, json_data, task, task_number, init_data, quest_seq):
    if request["m"] == "planes.takeMeans":
        if request["p"]["plane_id"] == 0: # There's only one mission of this type, do it the lazy way.
            json_data["goals"]["goals"][quest_seq]["tasks"][task_number]["num_completed"] = json_data["goals"]["goals"][quest_seq]["tasks"][task_number]["num_completed"] + 1
    
    return json_data
