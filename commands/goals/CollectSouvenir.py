def handle_CollectSouvenir(request, user_id, json_data, task, task_number, init_data, quest_seq):
    if request["m"] == "planes.takeMeans" and task["user_action"] == "CollectSouvenir":
        if "souvenir_types_id" in request["p"]:
            if int(task["obj_type_id"]) == int(request["p"]["souvenir_types_id"]):
                json_data["goals"]["goals"][quest_seq]["tasks"][task_number]["num_completed"] += 1

            # This is special case for a quest where we need to collect any type of souvenir
            if int(task["obj_type_id"]) == -1 and "souvenir_types_id" in request["p"] and request["p"]["souvenir_types_id"] != -1:
                json_data["goals"]["goals"][quest_seq]["tasks"][task_number]["num_completed"] += 1

    return json_data
