import json
import os
import random
import threading
import time
import queue
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Set
import shutil
from datetime import datetime

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

'''
Store all save files in memory with asynchronous save queue system.
'''

__saves = {}
__world_map_players = {}
__playerCount = {"count": len(os.listdir(os.path.join(PROJECT_ROOT, "data", "users"))) - 1}

# Save queue system
__save_queue = queue.Queue()
__dirty_users: Set[str] = set()  # Track which users have unsaved changes
__saving_users: Set[str] = set()  # Track users currently being saved
__save_lock = threading.RLock()  # Reentrant lock for thread safety
__file_locks = {}  # Per-file locks to prevent concurrent file access
__save_thread = None
__shutdown_event = threading.Event()
__emergency_save_active = threading.Event()  # Prevent multiple emergency saves
__save_system_shutdown = False  # Track if save system has been shutdown

# Configuration (To-do: Move this to a config file)
SAVE_BATCH_INTERVAL = 2.0  # Save every 2 seconds
SAVE_BATCH_SIZE = 50       # Maximum users to save per batch
EMERGENCY_SAVE_THRESHOLD = 100  # Force save if this many users are dirty
MAX_CONCURRENT_SAVES = 5   # Maximum concurrent file write operations

# Backup configuration
BACKUP_ENABLED = True
BACKUP_INTERVAL_HOURS = 6
BACKUP_KEEP_COUNT = 24  # Keep 24 backups (4 days worth if backing up every 6 hours)
__last_backup_time = 0

n = open(os.path.join(PROJECT_ROOT, "data", "new_player.json.def"), "r", encoding="utf-8")
NEW_ACCOUNT_DATA = json.loads(n.read())
n.close()

def store_save_by_id(user_id : int) -> bool:
    """Load user profile from the disk."""
    user_id_str = str(user_id)
    
    # Get or create file lock for this user
    if user_id_str not in __file_locks:
        __file_locks[user_id_str] = threading.RLock()
    
    file_lock = __file_locks[user_id_str]
    
    with file_lock:  # Prevent concurrent file access
        try:
            file_path = os.path.join(PROJECT_ROOT, "data", "users", f"{user_id_str}.json")
            
            with open(file_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)
            
            with __save_lock:
                __saves[user_id_str] = json_data
            
            return True
        except FileNotFoundError:
            return False
        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"Failed to load user {user_id_str}: {e}")
            return False

def load_save_by_id(user_id : int) -> dict | int:
    if not str(user_id) in __saves:
        if store_save_by_id(user_id) == False:
            return -1
    return __saves[str(user_id)]

def load_save_by_name(user_name : str) -> dict | int:
    user_id = get_id_from_name(user_name)
    if user_id == -1:
        return -1
    else:
        return load_save_by_id(user_id)


def modify_save_by_id(user_id : int, json_data : dict) -> None:
    """
    Update user profile in memory and mark for asynchronous save.
    """
    user_id_str = str(user_id)
    
    with __save_lock:
        __saves[user_id_str] = json.loads(json.dumps(json_data))
        __dirty_users.add(user_id_str)
        
        dirty_count = len(__dirty_users)
        
    # Emergency save check outside the lock to prevent deadlock
    if (dirty_count >= EMERGENCY_SAVE_THRESHOLD and 
        not __emergency_save_active.is_set() and 
        not __shutdown_event.is_set()):
        
        __emergency_save_active.set()
        try:
            logging.warning(f"Emergency save triggered: {dirty_count} dirty users")
            _force_save_batch()
        finally:
            __emergency_save_active.clear()

def _force_save_batch():
    """Force immediate save of current dirty users (used for emergency saves)."""
    if not __dirty_users:
        return
        
    batch_to_save = list(__dirty_users)[:SAVE_BATCH_SIZE]
    _save_users_batch(batch_to_save)

def _save_users_batch(user_ids: list):
    """Save a batch of users to disk."""
    if not user_ids:
        return
        
    # Mark users as being saved to prevent concurrent save attempts
    with __save_lock:
        # Filter out users already being saved
        users_to_save = [uid for uid in user_ids if uid not in __saving_users]
        
        # Mark as being saved
        for user_id_str in users_to_save:
            __saving_users.add(user_id_str)
    
    if not users_to_save:
        return
    
    saved_count = 0
    failed_saves = []
    
    # Use ThreadPoolExecutor for concurrent saves with limit
    with ThreadPoolExecutor(max_workers=min(MAX_CONCURRENT_SAVES, len(users_to_save))) as executor:
        futures = {}
        
        for user_id_str in users_to_save:
            future = executor.submit(_save_single_user, user_id_str)
            futures[future] = user_id_str
        
        # Wait for all saves to complete
        for future in futures:
            user_id_str = futures[future]
            try:
                if future.result():
                    saved_count += 1
                else:
                    failed_saves.append(user_id_str)
            except Exception as e:
                logging.error(f"Failed to save user {user_id_str}: {e}")
                failed_saves.append(user_id_str)
    
    # Update tracking sets
    with __save_lock:
        for user_id_str in users_to_save:
            __saving_users.discard(user_id_str)
            if user_id_str not in failed_saves:
                __dirty_users.discard(user_id_str)
    
    if saved_count > 0:
        logging.info(f"Batch saved {saved_count} users to disk")
    
    if failed_saves:
        logging.error(f"Failed to save {len(failed_saves)} users: {failed_saves}")

def _save_single_user(user_id_str: str) -> bool:
    """Save a single user profile."""
    # Get or create file lock for this user
    if user_id_str not in __file_locks:
        with __save_lock:
            if user_id_str not in __file_locks:
                __file_locks[user_id_str] = threading.RLock()
    
    file_lock = __file_locks[user_id_str]
    
    with file_lock:  # Prevent concurrent file access for this user
        try:
            # Get a snapshot of the data while holding the lock
            with __save_lock:
                if user_id_str not in __saves:
                    return False
                
                # Create a deep copy to prevent modification during save
                user_data = json.loads(json.dumps(__saves[user_id_str]))
            
            file_path = os.path.join(PROJECT_ROOT, "data", "users", f"{user_id_str}.json")
            temp_path = f"{file_path}.tmp.{threading.current_thread().ident}"
            
            # Write to unique temporary file
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(user_data, f, separators=(',', ':'))
            
            os.replace(temp_path, file_path)
            return True
            
        except Exception as e:
            # Clean up temp file if it exists
            try:
                if 'temp_path' in locals():
                    os.unlink(temp_path)
            except:
                pass
            logging.error(f"Failed to save user {user_id_str}: {e}")
            return False

def _save_worker():
    """Background thread that periodically saves dirty users."""
    logging.info("Save worker thread started")
    
    while not __shutdown_event.is_set():
        try:
            # Wait for the interval or shutdown event
            if __shutdown_event.wait(SAVE_BATCH_INTERVAL):
                break  # Shutdown requested
            
            # Get batch of users to save (atomic snapshot)
            with __save_lock:
                if not __dirty_users:
                    continue
                
                # Get users not currently being saved
                available_dirty = __dirty_users - __saving_users
                batch_to_save = list(available_dirty)[:SAVE_BATCH_SIZE]
            
            if batch_to_save:
                _save_users_batch(batch_to_save)
                
            # Check if it's time to create a backup (not during shutdown)
            if not __shutdown_event.is_set() and _should_backup():
                _create_backup()
                
        except Exception as e:
            logging.error(f"Error in save worker: {e}")
            # Continue working even if there's an error
    
    # Final save on shutdown - ensure all data is saved
    logging.info("Save worker shutting down, performing final save...")
    
    # Give time for any ongoing saves to complete
    time.sleep(0.5)
    
    # Force save any remaining dirty users
    final_attempts = 0
    while final_attempts < 3:  # Maximum 3 attempts
        with __save_lock:
            remaining_dirty = list(__dirty_users - __saving_users)
        
        if not remaining_dirty:
            break
            
        logging.info(f"Final save attempt {final_attempts + 1}: {len(remaining_dirty)} users")
        _save_users_batch(remaining_dirty)
        final_attempts += 1
        
        if final_attempts < 3:
            time.sleep(1)  # Brief pause between attempts
    
    # Log any users that couldn't be saved
    with __save_lock:
        if __dirty_users:
            logging.error(f"WARNING: {len(__dirty_users)} users could not be saved on shutdown: {list(__dirty_users)}")
        else:
            logging.info("All user data successfully saved on shutdown")
    
    logging.info("Save worker thread stopped")

def _should_backup():
    """Check if it's time to create a backup."""
    if not BACKUP_ENABLED:
        return False
    
    current_time = time.time()
    return (current_time - __last_backup_time) > (BACKUP_INTERVAL_HOURS * 3600)

def _create_backup():
    """Create a backup of all user data."""
    global __last_backup_time
    
    try:
        backup_dir = os.path.join(PROJECT_ROOT, "data", "backups")
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"users_backup_{timestamp}")
        
        # Copy entire users directory
        users_dir = os.path.join(PROJECT_ROOT, "data", "users")
        shutil.copytree(users_dir, backup_path)
        
        # Clean old backups
        _cleanup_old_backups(backup_dir)
        
        __last_backup_time = time.time()
        logging.info(f"Backup created: {backup_path}")
        
    except Exception as e:
        logging.error(f"Failed to create backup: {e}")

def _cleanup_old_backups(backup_dir):
    """Remove old backups, keeping only the most recent ones."""
    try:
        backups = [d for d in os.listdir(backup_dir) 
                  if d.startswith("users_backup_") and os.path.isdir(os.path.join(backup_dir, d))]
        backups.sort(reverse=True)  # Most recent first
        
        for old_backup in backups[BACKUP_KEEP_COUNT:]:
            old_path = os.path.join(backup_dir, old_backup)
            shutil.rmtree(old_path)
            logging.info(f"Removed old backup: {old_backup}")
            
    except Exception as e:
        logging.error(f"Failed to cleanup old backups: {e}")

def start_save_system():
    """Initialize and start the asynchronous save system."""
    global __save_thread, __save_system_shutdown
    
    if __save_thread and __save_thread.is_alive():
        logging.warning("Save system already running")
        return
    
    __save_system_shutdown = False
    __shutdown_event.clear()
    __save_thread = threading.Thread(target=_save_worker, daemon=False)  # Don't use daemon threads for save system
    __save_thread.start()
    logging.info("Asynchronous save system started")

def shutdown_save_system():
    """Gracefully shutdown the save system and save all pending data."""
    global __save_thread, __save_system_shutdown
    
    # Prevent multiple shutdowns
    if __save_system_shutdown:
        logging.debug("Save system already shutdown")
        return
    
    __save_system_shutdown = True
    logging.info("Shutting down save system...")
    __shutdown_event.set()
    
    if __save_thread and __save_thread.is_alive():
        __save_thread.join(timeout=30)  # Wait up to 30 seconds
        
        if __save_thread.is_alive():
            logging.error("Save thread did not shutdown gracefully")
        else:
            logging.info("Save system shutdown complete")
    else:
        logging.info("Save system shutdown complete")

def is_save_system_shutdown():
    """Check if the save system has been shutdown."""
    return __save_system_shutdown

def force_save_all():
    """Force immediate save of all dirty users (blocking operation)."""
    with __save_lock:
        if not __dirty_users:
            logging.info("No dirty users to save")
            return
        
        users_to_save = list(__dirty_users)
    
    logging.info(f"Force saving {len(users_to_save)} users...")
    
    # Save in batches
    for i in range(0, len(users_to_save), SAVE_BATCH_SIZE):
        batch = users_to_save[i:i + SAVE_BATCH_SIZE]
        _save_users_batch(batch)
    
    logging.info("Force save completed")

def get_save_stats():
    """Get statistics about the save system."""
    with __save_lock:
        return {
            "dirty_users_count": len(__dirty_users),
            "saving_users_count": len(__saving_users),
            "total_users_cached": len(__saves),
            "save_thread_alive": __save_thread.is_alive() if __save_thread else False,
            "emergency_save_active": __emergency_save_active.is_set(),
            "shutdown_in_progress": __shutdown_event.is_set(),
            "file_locks_count": len(__file_locks),
            "dirty_users_sample": list(__dirty_users)[:10],  # First 10 for debugging
            "saving_users_sample": list(__saving_users)[:10]
        }

def verify_data_integrity(user_id: int) -> dict:
    """Verify data integrity for a specific user - useful for debugging."""
    user_id_str = str(user_id)
    
    with __save_lock:
        memory_data = __saves.get(user_id_str)
        is_dirty = user_id_str in __dirty_users
        is_saving = user_id_str in __saving_users
    
    # Read from disk
    try:
        file_path = os.path.join(PROJECT_ROOT, "data", "users", f"{user_id_str}.json")
        with open(file_path, "r", encoding="utf-8") as f:
            disk_data = json.load(f)
    except:
        disk_data = None
    
    return {
        "user_id": user_id,
        "in_memory": memory_data is not None,
        "on_disk": disk_data is not None,
        "is_dirty": is_dirty,
        "is_saving": is_saving,
        "data_matches": memory_data == disk_data if (memory_data and disk_data) else None
    }

def get_id_from_name(user_name : str) -> int:
    try:
        f = open(os.path.join(PROJECT_ROOT, "data", "users", "nametoid", str(user_name)), "r", encoding="utf-8")
        user_id = int(f.read())
        f.close()
        return user_id
    except FileNotFoundError:
        return -1

def user_id_exists(user_id : int) -> bool:
    return load_save_by_id(user_id) != -1

def user_name_exists(user_name : str) -> bool:
    return load_save_by_name(user_name) != -1

def create_new_account(uid : int, username : str, password : str, token : str) -> None:
    json_data = NEW_ACCOUNT_DATA.copy()
    f = open(os.path.join(PROJECT_ROOT, "data", "users", str(uid) + ".json"), "w+", encoding="utf-8")
    json_data["playerData"]["account_id"] = uid
    json_data["playerData"]["user_name"] = username
    json_data["playerData"]["password"] = password

    #################################################################
    # Change user-id everywhere [WHY :-( ]                          #
    #################################################################
    json_data["goals"]["player_id"] = uid                           #
    json_data["backgrounds"][0]["player_id"] = uid                  #
    json_data["planes"][0]["to_player_id"] = uid                    #
    json_data["runways"][0]["player_id"] = uid                      #
    json_data["hangars"][0]["player_id"] = uid                      #
    j = 0                                                           #
    for i in json_data["landsideBuildings"]:                        #
        json_data["landsideBuildings"][j]["player_id"] = uid        #
        j = j + 1                                                   #
    json_data["accountData"]["id"] = uid                            #
    json_data["accountData"]["user_name"] = username                #
    json_data["expeditionstatus"]["player_id"] = uid                #
    json_data["playerData"]["token"] = token                        #
    #################################################################

    f.write(json.dumps(json_data))
    f.close()


    # Create a nametoid file
    f = open(os.path.join(PROJECT_ROOT, "data", "users", "nametoid", str(username)), "w+", encoding="utf-8")
    f.write(str(uid))
    f.close()

def read_location_id(file : str) -> tuple[str, int]:
    with open(os.path.join(PROJECT_ROOT, "data", "users", file), "r", encoding="utf-8") as f:
        json_data = json.load(f)
    return file[0:-5], json_data["playerData"]["location_id"]
    

def save_players_by_location_id():
    all_files = [x for x in os.listdir(os.path.join(PROJECT_ROOT, "data", "users")) if x.endswith(".json")]
    with ThreadPoolExecutor() as executor:
        for user_id, result in executor.map(read_location_id, all_files):
            if result not in __world_map_players:
                __world_map_players[result] = []
            __world_map_players[result].append(int(user_id))


    for i in range(241):
        # There are 240 countries right now.
        # Not all ids exist, but we don't care as it doesn't hurt
        if i in __world_map_players:
            # The original game uses a completely random order.
            # We'd like to prioritize online users, but instead of checking this on server start
            # we're putting them on the beginning of the list when they enable their buddyping.
            random.shuffle(__world_map_players[i])
        else:
            __world_map_players[i] = [800] # NPC player

def add_player_to_world_list(user_id, location_id):
    if location_id == -1: # Prevent corruption
        return
    if len(__world_map_players[location_id]) == 1 and __world_map_players[location_id][0] == 800:
        # Remove NPC player
        __world_map_players[location_id] = []
    __world_map_players[location_id].insert(0, int(user_id))

def buddyping_enabled(user_id, location_id):
    if location_id == -1: # When a player has not yet chosen a location in the tutorial
        return
    player_list = __world_map_players[location_id]
    old_index = player_list.index(int(user_id))
    player_list.insert(0, player_list.pop(old_index))

def get_accounts_by_location_id(location_id, amount, own_user_id):
    player_list = __world_map_players[location_id]
    player_list_cropped = [ x for x in player_list[0:(amount+1 if int(own_user_id) in player_list else amount)] if x != int(own_user_id) ]

    # Ducktape fix for if you're the only person in your country
    if player_list_cropped == []:
        player_list_cropped = [800]

    return player_list_cropped

def get_player_count() -> int:
    return __playerCount["count"]

def add_to_player_count(amount : int) -> None:
    __playerCount["count"] += amount