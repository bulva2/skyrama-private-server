import logging
from typing import List, Dict, Any, Callable
from commands import available_commands, handle_goal, handle_addObj, handle_lucky_luggage_live

from src.debug import report_issue
from src.utils import get_level_from_xp
from state import state

def process_game_commands(user_id: int, commands: List[Dict[str, Any]], json_data: dict, session: dict[str, Any]) -> Dict[str, Any] | int:
    final_response: Dict[str, Any] = {"rpcResults": []}
    items_to_add_to_obj: List[List[Any]] = []

    start_level: int = get_level_from_xp(json_data.get("playerData", {}).get("xp", 0), state.init_data["playerData"]["xp_level_caps"])

    for cmd in commands:
        if cmd["m"] in available_commands:
            rpc_result: Dict[str, Any] = {}
            add_items: List[Any] = []

            handle_lucky_luggage_live(cmd, user_id, json_data)

            # ??? no clue why this is handled this way
            cmd["previous_air_coins"] = json_data["playerData"]["air_coins"]

            cmd_handler: Callable = available_commands[cmd["m"]]
            cmd_handler(cmd, user_id, rpc_result, add_items, json_data, state.init_data)

            if rpc_result.get("i") == -1:
                report_issue("warning", f"AntiCheat triggered for user_id {user_id} on command {cmd['m']}")
                return -1
            
            final_response["rpcResults"].append(rpc_result)

            # Run checks for all current goals (main, pilot, daily)
            for goal in state.goal_types:
                handle_goal(cmd, user_id, goal, add_items, json_data, state.init_data)
            
            items_to_add_to_obj.extend(add_items)
            logging.info(f"Command {cmd['m']} handled")
        else:
            report_issue("warning", f"Unimplemented command {cmd['m']} from user_id {user_id}")
            return -2

    end_level: int = get_level_from_xp(json_data.get("playerData", {}).get("xp", 0), state.init_data["playerData"]["xp_level_caps"])
    
    if start_level != end_level:
        for _ in range(end_level - start_level):
            json_data["playerData"]["air_coins"] += 850
            json_data["playerData"]["air_cash"] += 2

    obj = {}
    handle_addObj(cmd, user_id, obj, items_to_add_to_obj, json_data, state.init_data, state.obj_data)
    final_response["obj"] = obj
    return final_response
    




             
