from src.debug import report_issue

def get_level_from_xp(xp, level_caps):
  for level, cap in enumerate(level_caps):
    if int(cap) > xp:
      return level
    
  return len(level_caps)

# Returns (level, xp into current level, current level cap)
def get_crafting_level_from_xp(xp, level_caps):
  level_caps = level_caps.values()
  total_xp = 0
  xp_in_level = xp
  for level, cap in enumerate(level_caps):
    intcap = int(cap)
    total_xp += intcap
    if xp < total_xp:
      return (level, xp_in_level, intcap)
    xp_in_level -= intcap
  return (len(level_caps) - 1, xp_in_level + intcap, intcap)

def subtract_resources(json_data, rpcResult, air_coins = None, air_cash = None, event_currency = None):
  player_data = json_data["playerData"]
  
  # Anticheat checks (Prevents negative resources)
  if air_coins and player_data["air_coins"] < air_coins:
    rpcResult["i"] = -1
    report_issue("warning", f"utils: Insufficient air_coins for user {player_data['account_id']}: has {player_data['air_coins']}, needs {air_coins}")
    return
  
  if air_cash and player_data["air_cash"] < air_cash:
    rpcResult["i"] = -1
    report_issue("warning", f"utils: Insufficient air_cash for user {player_data['account_id']}: has {player_data['air_cash']}, needs {air_cash}")
    return
  
  if event_currency and player_data["event_currency"] < event_currency:
    rpcResult["i"] = -1
    report_issue("warning", f"utils: Insufficient event_currency for user {player_data['account_id']}: has {player_data['event_currency']}, needs {event_currency}")
    return
  
  if air_coins:
    player_data["air_coins"] -= air_coins
  if air_cash:
    player_data["air_cash"] -= air_cash
  if event_currency:
    player_data["event_currency"] -= event_currency