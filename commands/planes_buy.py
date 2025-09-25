import time
from src.utils import substract_resources

def handle_planesBuy(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = str(int(time.time()))
    rpcResult["r"] = None

    for i in init_data["planeTypes"]:
        if int(i["id"]) == int(request["p"]["typeId"]):
            substract_resources(json_data, rpcResult, i["air_coins_cost"], i["air_cash_cost"], i["event_currency_cost"])

            json_data["planes"].append({"souvenir_types_id":-1,"active_count":1,"id":json_data["playerData"]["next_object_id"],"plane_type_id":request["p"]["typeId"],"container_id":request["p"]["container_id"],"subcontainer_id":request["p"]["subcontainer_id"],"to_player_id":-1,"departure_time":-1,"arrival_time":-1,"kerosene_boost_flag":"0","flight_status":"77","buddy_points":i["buddy_points_yield"],"contents_count":i["capacity"],"air_coins":i["air_coins_yield"],"xp":i["xp_yield"],"wares_revenue":i["wares_revenue_capacity"],"banner_id":"-1","start_service_time":"0","last_state_change_time":"0","drop_consumable_id":"0","drop_consumable_amount":"0","instantland":0,"player_id":user_id,"from_location_id":-1,"from_user_name":"drone","upgrade_level":0})
            json_data["playerData"]["next_object_id"] = int(json_data["playerData"]["next_object_id"]) + 1
            return
            
    