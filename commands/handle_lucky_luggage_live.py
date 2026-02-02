import time

def handle_lucky_luggage_live(request, user_id, json_data):
    if "next_reward" not in json_data["lucky_luggage_data"]:
       json_data["lucky_luggage_data"]["next_reward"] = 0

    if json_data["lucky_luggage_data"]["next_reward"] < int(time.time()):
      if (json_data["lucky_luggage_data"]["next_reward"] + 86400) < int(time.time()): # If previous spin is not claimed, reset back to 1
        json_data["lucky_luggage_data"]["consecutive_login_days"] = 1
        json_data["playerData"]["consecutive_logins_begin"] = int(time.time())
        json_data["playerData"]["num_consecutive_login_days"] = 1 # Why does this always have to been on so many different places :((
      else:
        json_data["lucky_luggage_data"]["consecutive_login_days"] = json_data["lucky_luggage_data"]["consecutive_login_days"] + 1
        json_data["playerData"]["num_consecutive_login_days"] = json_data["lucky_luggage_data"]["consecutive_login_days"]
        
      days = json_data["lucky_luggage_data"]["consecutive_login_days"]
      
      json_data["lucky_luggage_data"]["next_reward"] = int(time.time()) + 86400 # After 24 hours     
      
      if days < 5:
        num_spins = int(json_data["lucky_luggage_data"]["free_spin_table"][days - 1])
      else:
        num_spins = int(json_data["lucky_luggage_data"]["free_spin_table"][4])
        
      json_data["lucky_luggage_data"]["free_spins"] = json_data["lucky_luggage_data"]["free_spins"] + num_spins
      #json_data["playerData"]["lucky_luggage_free_spins"] = json_data["lucky_luggage_data"]["free_spins"] # Unreferenced client code, if no problems arise, remove
      
      json_data["lucky_luggage_data"]["gotBonus"] = 1 if json_data["lucky_luggage_data"]["free_spins"] > 0 else 0
    else:
      json_data["lucky_luggage_data"]["gotBonus"] = 0