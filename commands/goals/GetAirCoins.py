def handle_GetAirCoins(request, user_id, json_data, task, task_number, init_data, quest_seq):
    diff = int(json_data["playerData"]["air_coins"]) - int(request["previous_air_coins"])
    if diff > 0:
        json_data["goals"]["goals"][quest_seq]["tasks"][task_number]["num_completed"] = json_data["goals"]["goals"][quest_seq]["tasks"][task_number]["num_completed"] + diff
    
    return json_data
