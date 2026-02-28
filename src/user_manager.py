import os
import orjson
import random
import logging
from datetime import datetime
from typing import Any, Dict
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager

from src.database import Player, Plane, get_db_session

# Columns that need to be synced from playerData for query purposes
PLAYER_INDEXED_FIELDS = [
    ("location_id", "location_id"),
]

PLAYER_JSON_FIELDS = [
    ("saved_sequence_num", "savedSequenceNum"),
    ("is_user_being_log_traced", "isUserBeingLogTraced"),
    ("player_data", "playerData"),
    ("account_data", "accountData"),
    ("goals_data", "goals"),
    ("backgrounds", "backgrounds"),
    ("landmarks", "landmarks"),
    ("consumables", "consumables"),
    ("runways", "runways"),
    ("terminals", "terminals"),
    ("hangars", "hangars"),
    ("landside_buildings", "landsideBuildings"),
    ("cargo_shops", "cargoShops"),
    ("cargo", "cargo"),
    ("warehouses", "warehouses"),
    ("bays", "bays"),
    ("buddy_stuff", "buddyStuff"),
    ("souvenir_collections", "souvenirCollections"),
    ("lucky_luggage_data", "lucky_luggage_data"),
    ("crafting_data", "crafting_data"),
    ("expedition_status", "expeditionstatus"),
    ("locations", "locations"),
    ("special_buildings", "specialBuildings"),
    ("news", "news"),
    ("event_materials", "eventMaterials"),
    ("materials", "materials"),
    ("user_recycling_slots", "userRecyclingSlots"),
    ("user_crafting_slots", "userCraftingSlots"),
    ("user_current_craftings", "userCurrentCraftings"),
]

# (db_attribute, json_key, default_for_new)
PLANE_FIELD_MAPPINGS = [
    ("plane_type_id", "plane_type_id", 0),
    ("container_id", "container_id", -1),
    ("subcontainer_id", "subcontainer_id", -1),
    ("flight_status", "flight_status", 77),
    ("departure_time", "departure_time", 0),
    ("arrival_time", "arrival_time", 0),
    ("start_service_time", "start_service_time", 0),
    ("last_state_change_time", "last_state_change_time", 0),
    ("from_player_id", "player_id", 0),  # Note: JSON key differs
    ("from_user_object_id", "fromUser_objectId", -1),
    ("to_player_id", "to_player_id", -1),
    ("from_location_id", "from_location_id", -1),
    ("to_location_id", "to_location_id", -1),
    ("from_user_name", "from_user_name", ""),
    ("to_user_name", "to_user_name", ""),
    ("active_count", "active_count", 1),
    ("contents_count", "contents_count", 0),
    ("wares_revenue", "wares_revenue", 0),
    ("buddy_points", "buddy_points", 0),
    ("xp", "xp", 0),
    ("air_coins", "air_coins", 0),
    ("kerosene_boost_flag", "kerosene_boost_flag", 0),
    ("instantland", "instantland", 0),
    ("upgrade_level", "upgrade_level", 0),
    ("souvenir_types_id", "souvenir_types_id", -1),
    ("drop_consumable_id", "drop_consumable_id", 0),
    ("drop_consumable_amount", "drop_consumable_amount", 0),
    ("drop_material", "drop_material", 0),
    ("drop_material_amount", "drop_material_amount", 0),
    ("banner_id", "banner_id", -1),
    ("banner_text", "banner_text", ""),
]

def _safe_update(obj, attr: str, data: dict, key: str) -> None:
    if key in data:
        setattr(obj, attr, data[key])

# Probably remove this soon, inconsistent
CACHE_ENABLED = False
__player_cache: Dict[int, dict] = {}

__world_map_players = {}

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

with open(os.path.join(PROJECT_ROOT, "data", "new_player.json.def"), "rb") as file:
    NEW_ACCOUNT_DATA = orjson.loads(file.read())

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
    planes_list = [p.to_dict() for p in player.planes]
    
    return {
        "playerData": player.player_data,
        "accountData": player.account_data,
        "goals": player.goals_data,
        "backgrounds": player.backgrounds,
        "landmarks": player.landmarks,
        "planes": planes_list,
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

def _update_player_from_dict(player: Player, json_data: dict, session):
    """Update player model from JSON data. Only updates fields that exist in the incoming data."""
    player_data = json_data.get("playerData", {})

    # Update indexed fields (only location_id) for query purposes
    for db_attr, json_key in PLAYER_INDEXED_FIELDS:
        _safe_update(player, db_attr, player_data, json_key)

    # Update complex/JSON fields from root json_data
    for db_attr, json_key in PLAYER_JSON_FIELDS:
        _safe_update(player, db_attr, json_data, json_key)

    # Sync Planes
    _sync_planes(player, json_data.get("planes", []), session)


def _sync_planes(player: Player, incoming_planes: list, session):
    """
    Synchronize planes between incoming JSON and database.
    - Updates existing planes (only fields present in JSON)
    - Creates new planes with defaults
    - Deletes planes no longer in JSON
    """
    existing_planes = {p.plane_id: p for p in player.planes}
    processed_ids = set()
    
    for p_data in incoming_planes:
        p_id = int(p_data.get("id", 0))
        processed_ids.add(p_id)
        
        if p_id in existing_planes:
            # Update existing - only update fields present in p_data
            plane = existing_planes[p_id]
            for db_attr, json_key, _ in PLANE_FIELD_MAPPINGS:
                _safe_update(plane, db_attr, p_data, json_key)
        else:
            # Create new plane with defaults from mapping
            plane_kwargs = {
                "owner_id": player.user_id,
                "plane_id": p_id,
            }
            for db_attr, json_key, default in PLANE_FIELD_MAPPINGS:
                plane_kwargs[db_attr] = p_data.get(json_key, default)
            
            new_plane = Plane(**plane_kwargs)
            session.add(new_plane)
    
    # Delete planes that are no longer in the incoming data
    for p_id, plane in existing_planes.items():
        if p_id not in processed_ids and p_id != 0:
            session.delete(plane)
        
def load_save_by_name(username: str) -> Any:
    try:
        with db_session_scope() as session:
            player = session.query(Player).filter_by(username=username).first()
            
            if not player:
                return -1
            
            json_data = _player_to_dict(player)
            if CACHE_ENABLED:
                __player_cache[player.user_id] = json_data # type: ignore (pylance)
            return json_data
            
    except SQLAlchemyError as e:
        logging.error(f"Failed to load user {username}: {e}")
        return -1
    
def fetch_pwd_hash_by_name(username: str) -> bytes | None:
    try:
        with db_session_scope() as session:
            player = session.query(Player).filter_by(username=username).first()
            return player.password.encode('utf-8') if player else None
    except SQLAlchemyError as e:
        logging.error(f"Failed to fetch password hash for {username}: {e}")
        return None
    
def is_user_banned(username: str) -> bool:
    try:
        with db_session_scope() as session:
            player = session.query(Player).filter_by(username=username).first()
            return player.is_banned if player else False
    except SQLAlchemyError as e:
        logging.error(f"Failed to check ban status for {username}: {e}")
        return False

def load_save_by_id(user_id: int) -> dict | int:
    try:
        user_id = int(user_id)
        
        if CACHE_ENABLED and user_id in __player_cache:
            return __player_cache[user_id]
        
        with db_session_scope() as session:
            player = session.query(Player).filter_by(user_id=user_id).first()
            
            if not player:
                logging.error(f"User ID {user_id} not found in database! Returning -1")
                return -1
            
            json_data = _player_to_dict(player)
            if CACHE_ENABLED:
                __player_cache[user_id] = json_data
            return json_data
            
    except SQLAlchemyError as e:
        logging.error(f"Failed to load user {user_id}: {e}")
        return -1


def modify_save_by_id(user_id: int, json_data: dict, set_last_login: bool = False) -> None:
    try:
        user_id = int(user_id)
        
        with db_session_scope() as session:
            player = session.query(Player).filter_by(user_id=user_id).first()
            if not player:
                logging.error(f"Cannot modify non-existent user {user_id}")
                return
            
            # Update player object directly from JSON
            _update_player_from_dict(player, json_data, session)
            
            if set_last_login:
                player.last_login = datetime.now() # type: ignore (pylance)

            if CACHE_ENABLED:
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

def user_name_exists(username: str) -> bool:
    try:
        with db_session_scope() as session:
            return session.query(Player).filter_by(username=username).first() is not None
    except SQLAlchemyError:
        return False

def search_users_by_name(pattern: str) -> list[tuple[int, str]]:
    try:
        with db_session_scope() as session:
            return session.query(Player.user_id, Player.username)\
                          .filter(func.lower(Player.username).like(f"{pattern.lower()}%"))\
                          .limit(10).all() # type: ignore (pylance)
    except SQLAlchemyError:
        return []


def create_new_account(username: str, password: str, token: str) -> int:
    try:
        json_data = orjson.loads(orjson.dumps(NEW_ACCOUNT_DATA))
        
        with db_session_scope() as session:
            new_player = Player(
                username=username,
                password=password,
                token=token,
                player_data={},  # Placeholder
                account_data={},  # Placeholder
                goals_data={}  # Placeholder
            )
            session.add(new_player)
            session.flush()
            
            uid = new_player.user_id
        
            json_data["playerData"]["account_id"] = uid
            json_data["playerData"]["user_name"] = username
            json_data["playerData"]["password"] = password
            json_data["playerData"]["token"] = token
            
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
            
            _update_player_from_dict(new_player, json_data, session)
            
        logging.info(f"Created new account: {username} (ID: {uid})")
        return uid # type: ignore (pylance)
        
    except SQLAlchemyError as e:
        logging.error(f"Failed to create account {username}: {e}")
        raise

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