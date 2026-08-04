from src.debug import report_issue
from src.cache_manager import get_plane_upgrade_keys_up_to
import asyncio
import math
from typing import Dict

_user_locks: Dict[int, asyncio.Lock] = {}

def get_user_lock(user_id: int) -> asyncio.Lock:
    """Get or create an asyncio lock for a specific user (prevents concurrent requests)"""
    if user_id not in _user_locks:
        _user_locks[user_id] = asyncio.Lock()
    return _user_locks[user_id]

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

def build_plane_upgrades(planes, init_data):
    """Derive {plane_id: [applied upgrade bracket ids]} from upgrade_level.
	Not persisted anywhere (no DB column for it), so it has to be rebuilt from
	the authoritative Plane.upgrade_level on every read instead of accumulated
	across requests - see planes_upgrade.py.
	"""

    result = {}
    for plane in planes:
        level = int(plane.get("upgrade_level", 0))
        if level <= 0:
            continue
        result[str(plane["id"])] = get_plane_upgrade_keys_up_to(plane["plane_type_id"], level)
    return result

def get_upgraded_yield(base_yield, plane_type_id, upgrade_level, init_data, effect_type):
    """Add % bonuses from upgrades to a base value"""

    base_yield = int(base_yield)
    # If upgrade_level <= 0, there are no upgrades, so just return base_yield
    if upgrade_level <= 0:
        return base_yield

    total = base_yield

    # key (int) = plane upgrade bracket id (1, 3, 4, 7...)
    for key in get_plane_upgrade_keys_up_to(plane_type_id, upgrade_level):
        # effect = list[dict] = [{"type": "xp", "percent": 10}]
        for effect in init_data["planeUpgradeTypes"][str(key)]["effects"]:
            if effect["type"] == effect_type:
                total += math.ceil(base_yield * float(effect["percent"]) / 100)
    return total

def subtract_resources(json_data, rpcResult, air_coins = None, air_cash = None, event_currency = None):
    player_data = json_data["playerData"]

    for name, amount in (("air_coins", air_coins), ("air_cash", air_cash), ("event_currency", event_currency)):
        if amount is None:
            continue
        if (isinstance(amount, bool)
				or not isinstance(amount, (int, float))
				or not math.isfinite(amount)
				or amount < 0):
            rpcResult["i"] = -1
            report_issue("warning", f"utils: Invalid {name} cost for user {player_data['account_id']}: {amount!r} (must be a non-negative number)")
            return

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