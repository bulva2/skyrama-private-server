
import time
from src.cache_manager import get_cvs_data

def handle_getCv(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = {}
    rpcResult["r"]["cvs"] = get_cvs_data()