import orjson
import os
import time
import copy
from datetime import datetime

_CACHED_GOALS = None

def handle_daily_goals(json_data, player_level: int) -> dict | None:
    return _check_daily_goal(json_data, player_level)

def _load_daily_goals(force_reload: bool = False) -> dict:
    global _CACHED_GOALS

    # WIP: Implement force reload in case that we need to change something on the go.
    if force_reload:
        _CACHED_GOALS = None
    
    if _CACHED_GOALS is None:
        _daily_goals_path = os.path.join(os.path.dirname(__file__), "..", "data", "daily_goals.json")
        with open(_daily_goals_path, "rb") as f:
            _CACHED_GOALS = orjson.loads(f.read())
    
    return _CACHED_GOALS

def _get_daily_goal_for_day(day_of_year: int, player_level: int) -> dict:
    daily_goals = _load_daily_goals()

    available_goals = [
        goal for goal in daily_goals["dailyGoals"]
        if goal["min_lvl"] <= player_level <= goal["max_lvl"]
    ]

    if not available_goals:
        # Fallback if for whatever reason there are no goals available
        available_goals = daily_goals["dailyGoals"][:1]
    
    goal_index = day_of_year % len(available_goals)
    return available_goals[goal_index]

def _get_goal_by_id(goal_id) -> dict | None:
    daily_goals_data = _load_daily_goals()

    for goal in daily_goals_data["dailyGoals"]:
        if goal["id"] == goal_id:
            return goal
    return None

def _merge_goal_progress(goal_def: dict, progress_goal: dict) -> dict:
    merged_goal = copy.deepcopy(goal_def)
    
    progress_tasks = progress_goal.get("tasks", [])
    for def_task in merged_goal.get("taskTypes", []):
        for prog_task in progress_tasks:
            if def_task.get("task_id") == prog_task.get("task_id"):
                def_task["num_completed"] = prog_task.get("num_completed", 0)
                break
    return merged_goal

def _check_daily_goal(json_data: dict, player_level: int):
    current_time = time.time()
    last_daily_time = json_data["goals"].get("daily_goal_time", 0)

    last_date = datetime.fromtimestamp(last_daily_time).date() if last_daily_time > 0 else None
    current_date = datetime.fromtimestamp(current_time).date()

    needs_new_goal = (
        last_date is None or 
        current_date > last_date or
        json_data["goals"]["goals"]["daily"].get("goal_types_id") is None
    )

    if needs_new_goal:
        day_of_year = current_date.timetuple().tm_yday
        new_goal = _get_daily_goal_for_day(day_of_year, player_level)

        json_data["goals"]["daily_goal_time"] = current_time
        json_data["goals"]["goals"]["daily"] = {
            "goal_types_id": new_goal["id"],
            "tasks": new_goal["taskTypes"]
        }
        json_data["goals"]["daily_reward_given"] = False
        return new_goal
    
    # goal -> existing goal progress
    goal = json_data["goals"]["goals"].get("daily")
    goal_id = goal.get("goal_types_id") if goal else None
    if goal_id is not None:
        # goal_def -> goal definition from daily_goals.json
        goal_def = _get_goal_by_id(goal_id)
        if goal_def is not None:
            # Idk I might just send all of the data throught the db instead of this in the future, both are meh
            return _merge_goal_progress(goal_def, goal)
        
    return None

    
