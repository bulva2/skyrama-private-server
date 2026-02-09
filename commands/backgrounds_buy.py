
from src.utils import subtract_resources
from src.cache_manager import get_background_type_by_id
from src.debug import report_issue
import time

def handle_backgroundsBuy(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = None

    bg_id = int(request["p"]["background_types_id"])
    bg = get_background_type_by_id(bg_id)

    if bg is None:
        report_issue("warning", f"backgrounds_buy: Background type id {bg_id} not found in server cache for user {user_id}")
        rpcResult["i"] = -1
        return
    
    air_coins_cost = bg["air_coins_cost"]
    air_cash_cost = bg["air_cash_cost"]
    event_currency_cost = bg["event_currency_cost"]
    
    subtract_resources(json_data, rpcResult, air_coins_cost, air_cash_cost, event_currency_cost)

    for i in json_data["backgrounds"]:
        # Put the active background in storage
        if int(i["in_storage"]) == 0:
            i["in_storage"] = 1
            
        # Background is already bought, disconnect user
        if int(i["background_types_id"]) == int(request["p"]["background_types_id"]):
            report_issue("warning", f"backgrounds_buy: User {user_id} already owns background type id {bg_id}, possible duplicate buy attempt")
            rpcResult["i"] = -1
            return
            
    json_data["backgrounds"].append({"background_types_id": request["p"]["background_types_id"],"in_storage": "0","player_id": user_id})