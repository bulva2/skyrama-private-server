import os
import json
import random
import logging
from typing import Dict
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager

from src.database import Player, get_db_session

# In-memory cache
__player_cache: Dict[int, dict] = {}
__world_map_players = {}

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

with open(os.path.join(PROJECT_ROOT, "data", "new_player.json.def"), "r", encoding="utf-8") as file:
    NEW_ACCOUNT_DATA = json.load(file)

@contextmanager
def db_session_scope():
    session = get_db_session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logging.error(f"Database error: {e}")
        raise
    finally:
        session.close()

# Convert Player object to json_data
def _player_to_dict(player: Player) -> dict:
    return {
        "playerData": player.player_data,
        "accountData": player.account_data,
        "goals": player.goals_data,
        "backgrounds": player.backgrounds,
        "landmarks": player.landmarks,
        "planes": player.planes,
        "consumables": player.consumables,
        "buddyStuff": player.buddy_stuff,
        "bays": player.bays,
        "runways": player.runways,
        "terminals": player.terminals,
        "hangars": player.hangars,
        "landsideBuildings": player.landside_buildings,
        "cargoShops": player.cargo_shops,
        "cargo": player.cargo,
        "warehouses": player.warehouses,
        "souvenirCollections": player.souvenir_collections,
        "lucky_luggage_data": player.lucky_luggage_data,
        "crafting_data": player.crafting_data,
        "expeditionstatus": player.expedition_status,
        "savedSequenceNum": player.saved_sequence_num,
        "locations": player.locations,
        "specialBuildings": player.special_buildings,
        "news": player.news,
        "eventMaterials": player.event_materials,
        "materials": player.materials,
        "userRecyclingSlots": player.user_recycling_slots,
        "userCraftingSlots": player.user_crafting_slots,
        "userCurrentCraftings": player.user_current_craftings,
        "isUserBeingLogTraced": player.is_user_being_log_traced
    }

def _dict_to_player(json_data: dict, user_id: int, username: str, password: str) -> Player:
    player_data = json_data.get("playerData", {})
    
    return Player(
        user_id = user_id,
        username = username,
        password = password,

        token = player_data.get("token", ""),
        air_coins = player_data.get("air_coins", 0),
        air_cash = player_data.get("air_cash", 0),
        event_currency = player_data.get("event_currency", 0),
        xp = player_data.get("xp", 0),
        super_fuel = player_data.get("super_fuel", 0),
        passengers = player_data.get("passengers", 0),
        location_id = player_data.get("location_id", -1),
        last_buddyping_time = player_data.get("last_buddyping_time", 0),

        saved_sequence_num = json_data.get("savedSequenceNum", -1),
        is_user_being_log_traced = json_data.get("isUserBeingLogTraced", False),
        player_data = player_data,
        account_data = json_data.get("accountData", {}),
        goals_data = json_data.get("goals", {}),
        backgrounds = json_data.get("backgrounds", []),
        landmarks = json_data.get("landmarks", []),
        planes = json_data.get("planes", []),
        consumables = json_data.get("consumables", []),
        runways = json_data.get("runways", []),
        terminals = json_data.get("terminals", []),
        hangars = json_data.get("hangars", []),
        landside_buildings = json_data.get("landsideBuildings", []),
        cargo_shops = json_data.get("cargoShops", []),
        cargo = json_data.get("cargo", []),
        warehouses = json_data.get("warehouses", []),
        bays = json_data.get("bays", []),
        buddy_stuff = json_data.get("buddyStuff", {}),
        souvenir_collections = json_data.get("souvenirCollections", []),
        lucky_luggage_data = json_data.get("lucky_luggage_data", {}),
        crafting_data = json_data.get("crafting_data", {}),
        expedition_status = json_data.get("expeditionstatus", {}),
        locations = json_data.get("locations", []),
        special_buildings = json_data.get("specialBuildings", []),
        news = json_data.get("news"),
        event_materials = json_data.get("eventMaterials", []),
        materials = json_data.get("materials", {}),
        user_recycling_slots = json_data.get("userRecyclingSlots", []),
        user_crafting_slots = json_data.get("userCraftingSlots", []),
        user_current_craftings = json_data.get("userCurrentCraftings", [])
    )

def _update_player_from_dict(player: Player, json_data: dict) -> None:
    player_data = json_data.get("playerData", {})

    player.token = player_data.get("token", "")
    player.air_coins = player_data.get("air_coins", 0)
    player.air_cash = player_data.get("air_cash", 0)
    player.event_currency = player_data.get("event_currency", 0)
    player.xp = player_data.get("xp", 0)
    player.super_fuel = player_data.get("super_fuel", 0)
    player.passengers = player_data.get("passengers", 0)
    player.location_id = player_data.get("location_id", -1)
    player.last_buddyping_time = player_data.get("last_buddyping_time", 0)

    player.saved_sequence_num = json_data.get("savedSequenceNum", -1)
    player.is_user_being_log_traced = json_data.get("isUserBeingLogTraced", False)
    player.player_data = player_data
    player.account_data = json_data.get("accountData", {})
    player.goals_data = json_data.get("goals", {})
    player.backgrounds = json_data.get("backgrounds", [])
    player.landmarks = json_data.get("landmarks", [])
    player.planes = json_data.get("planes", [])
    player.consumables = json_data.get("consumables", [])
    player.runways = json_data.get("runways", [])
    player.terminals = json_data.get("terminals", [])
    player.hangars = json_data.get("hangars", [])
    player.landside_buildings = json_data.get("landsideBuildings", [])
    player.cargo_shops = json_data.get("cargoShops", [])
    player.cargo = json_data.get("cargo", [])
    player.warehouses = json_data.get("warehouses", [])
    player.bays = json_data.get("bays", [])
    player.buddy_stuff = json_data.get("buddyStuff", {})
    player.souvenir_collections = json_data.get("souvenirCollections", [])
    player.lucky_luggage_data = json_data.get("lucky_luggage_data", {})
    player.crafting_data = json_data.get("crafting_data", {})
    player.expedition_status = json_data.get("expeditionstatus", {})
    player.locations = json_data.get("locations", [])
    player.special_buildings = json_data.get("specialBuildings", [])
    player.news = json_data.get("news")
    player.event_materials = json_data.get("eventMaterials", [])
    player.materials = json_data.get("materials", {})
    player.user_recycling_slots = json_data.get("userRecyclingSlots", [])
    player.user_crafting_slots = json_data.get("userCraftingSlots", [])
    player.user_current_craftings = json_data.get("userCurrentCraftings", [])
        
def load_save_by_name(username: str) -> dict | int:
    """Load player data by username"""
    try:
        with db_session_scope() as session:
            player = session.query(Player).filter_by(username=username).first()
            
            if not player:
                return -1
            
            json_data = _player_to_dict(player)
            __player_cache[player.user_id] = json_data
            return json_data
            
    except SQLAlchemyError as e:
        logging.error(f"Failed to load user {username}: {e}")
        return -1

def load_save_by_id(user_id: int) -> dict | int:
    try:
        # Ensure user_id is an integer
        user_id = int(user_id)
        
        # Check cache first (optional optimization)
        if user_id in __player_cache:
            return __player_cache[user_id]
        
        with db_session_scope() as session:
            player = session.query(Player).filter_by(user_id=user_id).first()
            
            if not player:
                logging.error(f"User ID {user_id} not found in database! Returning -1")
                return -1
            
            json_data = _player_to_dict(player)
            __player_cache[user_id] = json_data
            return json_data
            
    except SQLAlchemyError as e:
        logging.error(f"Failed to load user {user_id}: {e}")
        return -1


def modify_save_by_id(user_id: int, json_data: dict) -> None:
    try:
        # Ensure user_id is an integer
        user_id = int(user_id)
        with db_session_scope() as session:
            player = session.query(Player).filter_by(user_id=user_id).first()
            
            if not player:
                logging.error(f"Cannot modify non-existent user {user_id}")
                return
            
            # Update player object directly from JSON
            _update_player_from_dict(player, json_data)
            
            # Update cache
            __player_cache[user_id] = json_data
            
            # Commit happens automatically via context manager
            logging.debug(f"Updated user {user_id}")
            
    except SQLAlchemyError as e:
        logging.error(f"Failed to modify user {user_id}: {e}")
        raise

def get_id_from_name(username: str) -> int:
    try:
        with db_session_scope() as session:
            player = session.query(Player.user_id).filter_by(username=username).first()
            return player.user_id if player else -1
    except SQLAlchemyError:
        return -1

def user_id_exists(user_id : int) -> bool:
    return load_save_by_id(user_id) != -1

def user_name_exists(username: str) -> bool:
    try:
        with db_session_scope() as session:
            return session.query(Player).filter_by(username=username).first() is not None
    except SQLAlchemyError:
        return False

def create_new_account(uid: int, username: str, password: str, token: str) -> None:
    try:
        json_data = NEW_ACCOUNT_DATA.copy()
        
        # Set user-specific data
        json_data["playerData"]["account_id"] = uid
        json_data["playerData"]["user_name"] = username
        json_data["playerData"]["password"] = password
        json_data["playerData"]["token"] = token
        
        # Update all player_id references
        json_data["goals"]["player_id"] = uid
        json_data["backgrounds"][0]["player_id"] = uid
        json_data["planes"][0]["to_player_id"] = uid
        json_data["runways"][0]["player_id"] = uid
        json_data["hangars"][0]["player_id"] = uid

        for building in json_data["landsideBuildings"]:
            building["player_id"] = uid

        json_data["accountData"]["id"] = uid
        json_data["accountData"]["user_name"] = username
        json_data["expeditionstatus"]["player_id"] = uid
        
        with db_session_scope() as session:
            new_player = _dict_to_player(json_data, uid, username, password)
            session.add(new_player)
            
        logging.info(f"Created new account: {username} (ID: {uid})")
        
    except SQLAlchemyError as e:
        logging.error(f"Failed to create account {username}: {e}")
        raise

def read_location_id(file : str) -> tuple[str, int]:
    with open(os.path.join(PROJECT_ROOT, "data", "users", file), "r", encoding="utf-8") as f:
        json_data = json.load(f)
    return file[0:-5], json_data["playerData"]["location_id"]
    

def save_players_by_location_id():
    global __world_map_players
    
    try:
        with db_session_scope() as session:
            players = session.query(Player.user_id, Player.location_id).all()
            
            for user_id, location_id in players:
                if location_id not in __world_map_players:
                    __world_map_players[location_id] = []
                __world_map_players[location_id].append(user_id)
        
        for i in range(241):
            if i in __world_map_players:
                random.shuffle(__world_map_players[i])
            else:
                __world_map_players[i] = [800]  # NPC player
        
    except SQLAlchemyError as e:
        logging.error(f"Failed to load world map: {e}")

def add_player_to_world_list(user_id: int, location_id: int) -> None:
    # Do NOT add players who have not yet chosen a location
    if location_id == -1:
        return
    
    # Remove NPC when first real player picks the country
    if len(__world_map_players[location_id]) == 1 and __world_map_players[location_id][0] == 800:
        __world_map_players[location_id] = []
    __world_map_players[location_id].insert(0, int(user_id))

def buddyping_enabled(user_id: int, location_id: int) -> None:
    if location_id == -1: # When a player has not yet chosen a location in the tutorial
        return
    
    player_list = __world_map_players[location_id]
    old_index = player_list.index(int(user_id))
    player_list.insert(0, player_list.pop(old_index))

def get_accounts_by_location_id(location_id: int, amount: int, own_user_id: int) -> list[int]:
    player_list = __world_map_players[location_id]
    player_list_cropped = [
        x for x in player_list[0:(amount+1 if int(own_user_id) in player_list else amount)] if x != int(own_user_id)
    ]
    return player_list_cropped if player_list_cropped else [800]

def get_player_count() -> int:
    try:
        with db_session_scope() as session:
            return session.query(Player).count()
    except SQLAlchemyError:
        return 0