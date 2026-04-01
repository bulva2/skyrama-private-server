def handle_StoreLandsideBuilding(request, user_id, json_data, task, task_number, init_data, quest_seq):
    if request["m"] == "placeable.setInStorage":
        if request["p"]["obj_type"] == "landside_building":
            json_data["goals"]["goals"][quest_seq]["tasks"][task_number]["num_completed"] += 1

    return json_data