import logging

def get_level_from_xp(xp : int, level_caps : list[int]) -> int:
  for level, cap in enumerate(level_caps):
    if int(cap) > xp:
      return level
  return len(level_caps)

def substract_resources(json_data, rpcResult, air_coins = None, air_cash = None, event_currency = None):
  player_data = json_data["playerData"]
  if air_coins is not None:
    player_data["air_coins"] -= air_coins
  if air_cash is not None:
    player_data["air_cash"] -= air_cash
  if event_currency is not None:
    player_data["event_currency"] -= event_currency

  # Anticheat checks
  for i in ["air_coins", "air_cash", "event_currency"]:
    if player_data[i] < 0:
      rpcResult["i"] = -1 # Disconnects user
      logging.warning(f"Negative resources detected for user with id {player_data["account_id"]}")
      return