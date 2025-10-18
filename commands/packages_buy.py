import time

def handle_packagesBuy(request, user_id, rpcResult, items_to_add_to_obj, json_data, init_data):
    rpcResult["i"] = request["i"]
    rpcResult["t"] = int(time.time())
    rpcResult["r"] = None
    items_to_add_to_obj.append("consumables")
    
    air_cash_cost = int(init_data["packagesTypes"][str(request["p"]["id"])]["air_cash_cost"])
    
    # Lazy way (amount is only readable in "name"???)
    if request["p"]["id"] == 1:
      res_earn = 25
    elif request["p"]["id"] == 2:
      res_earn = 135
      
    if json_data["consumables"] == []: # New account, initialize tuning items (first item in list doesn't count???)
            json_data["consumables"] = [0,0,0,0,0,0,0]
            
    # Add tuning items to account
    j = 0
    for i in json_data["consumables"]:
      if j != 0:
        json_data["consumables"][j] = json_data["consumables"][j] + res_earn
      j = j + 1
        
    json_data["playerData"]["air_cash"] = json_data["playerData"]["air_cash"] - air_cash_cost