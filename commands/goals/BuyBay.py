def handle_BuyBay(request, user_id, json_data, task, task_number, init_data, quest_seq):
    if request["m"] == "bays.buy":
        if int(task["obj_type_id"]) == int(request["p"]["types_id"]):
            json_data["goals"]["goals"][quest_seq]["tasks"][task_number]["num_completed"] += 1

    return json_data
