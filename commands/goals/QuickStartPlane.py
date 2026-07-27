from src.enums import PlaneState

_QUICK_START_STATES = (PlaneState.QUICK_START.value, PlaneState.QUICK_BUDDY_SERVE.value)

def handle_QuickStartPlane(request, user_id, json_data, task, task_number, init_data, quest_seq):
    if request["m"] == "planes.setState":
        try:
            flight_status = int(request["p"]["flight_status"])
        except (KeyError, TypeError, ValueError):
            return json_data

        if flight_status in _QUICK_START_STATES:
            json_data["goals"]["goals"][quest_seq]["tasks"][task_number]["num_completed"] += 1

    return json_data
