def handle_StoreTerminal(request, user_id, json_data, task, task_number, init_data, quest_seq):
    if request["m"] == "placeable.setInStorage":
        if request["p"]["obj_type"] == "terminal":
            # I'm not checking for the terminal size because it would make this code for 1 use unnecessary complicated,
            # TODO Add it in the future if we need it for more quests.
            json_data["goals"]["goals"][quest_seq]["tasks"][task_number]["num_completed"] += 1

    return json_data
