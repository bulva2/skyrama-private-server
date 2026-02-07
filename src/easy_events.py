import json
import os
import time

_CACHED_EVENTS = []
_CACHED_ACTIVE_EVENTS = []
FIRST_REFRESH_TIME = 0

_CACHED_COIN_MULTIPLIER = None
_CACHED_XP_MULTIPLIER = None
_CACHED_PAX_MULTIPLIER = None

# Easy event types:
# 0: XP
# 1: Wares TO-DO
# 2: Coins
# 3: Passengers
# 4: Plane TO-DO
# 5: Superfuel TO-DO

def _refresh_active_easy_events():
    global _CACHED_EVENTS
    global _CACHED_ACTIVE_EVENTS
    global FIRST_REFRESH_TIME
    global _CACHED_COIN_MULTIPLIER
    global _CACHED_XP_MULTIPLIER
    global _CACHED_PAX_MULTIPLIER

    _CACHED_EVENTS = []
    _CACHED_ACTIVE_EVENTS = []
    FIRST_REFRESH_TIME = None

    _CACHED_COIN_MULTIPLIER = None
    _CACHED_XP_MULTIPLIER = None
    _CACHED_PAX_MULTIPLIER = None
    
    _easy_events_path = os.path.join(os.path.dirname(__file__), "..", "data", "easy_events.json")
    with open(_easy_events_path, "r") as f:
        _CACHED_EVENTS = json.load(f)
        current_time = time.time()
        for event in _CACHED_EVENTS:
            # Check active events
            if current_time >= event["datestart"] and current_time <= event["dateend"]:
                _CACHED_ACTIVE_EVENTS.append(event)
            # Find the timestamp on which the active event list must be reloaded
            if current_time < event["datestart"] and (FIRST_REFRESH_TIME is None or event["datestart"] < FIRST_REFRESH_TIME):
                FIRST_REFRESH_TIME = event["datestart"]
            if current_time < event["dateend"] and (FIRST_REFRESH_TIME is None or event["dateend"] < FIRST_REFRESH_TIME):
                FIRST_REFRESH_TIME = event["dateend"]

    if FIRST_REFRESH_TIME is None:
        # No events, set refresh time to 24h later to avoid reloading the file on every request
        FIRST_REFRESH_TIME = current_time + 24*3600

    return _CACHED_ACTIVE_EVENTS

def get_all_easy_events():
    current_time = time.time()
    if current_time > FIRST_REFRESH_TIME:
        _refresh_active_easy_events()
    return _CACHED_EVENTS

def get_coin_multiplier():
    global _CACHED_COIN_MULTIPLIER

    current_time = time.time()
    if current_time > FIRST_REFRESH_TIME:
        _refresh_active_easy_events()
        return get_coin_multiplier()

    if _CACHED_COIN_MULTIPLIER is not None:
        return _CACHED_COIN_MULTIPLIER
    
    multiplier = 1
    active_events = _CACHED_ACTIVE_EVENTS
    for event in active_events:
        if event["eventType"] == 2:
            multiplier *= event["droprate"]
    _CACHED_COIN_MULTIPLIER = multiplier
    return multiplier

def get_xp_multiplier():
    global _CACHED_XP_MULTIPLIER

    current_time = time.time()
    if current_time > FIRST_REFRESH_TIME:
        _refresh_active_easy_events()
        return get_xp_multiplier()

    if _CACHED_XP_MULTIPLIER is not None:
        return _CACHED_XP_MULTIPLIER
    
    multiplier = 1
    active_events = _CACHED_ACTIVE_EVENTS
    for event in active_events:
        if event["eventType"] == 0:
            multiplier *= event["droprate"]
    _CACHED_XP_MULTIPLIER = multiplier
    return multiplier

def get_pax_multiplier():
    global _CACHED_PAX_MULTIPLIER

    current_time = time.time()
    if current_time > FIRST_REFRESH_TIME:
        _refresh_active_easy_events()
        return get_pax_multiplier()

    if _CACHED_PAX_MULTIPLIER is not None:
        return _CACHED_PAX_MULTIPLIER
    
    multiplier = 1
    active_events = _CACHED_ACTIVE_EVENTS
    for event in active_events:
        if event["eventType"] == 3:
            multiplier *= event["droprate"]
    _CACHED_PAX_MULTIPLIER = multiplier
    return multiplier