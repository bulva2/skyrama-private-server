import os
import orjson
from pathlib import Path

_CVS_CACHE = None
_CVS_PATH = os.path.join(Path(__file__).parents[1], "data", "getCv.json.def")

BACKGROUND_TYPES_BY_ID = {}
PLANE_UPGRADE_LEVEL_KEYS = {}

def initialize_cache(init_data):
    _initialize_background_types_cache(init_data["backgroundTypes"])
    _initialize_plane_upgrade_keys_cache(init_data["planeUpgradeTypes"])
    get_cvs_data()

# getCv
def get_cvs_data():
    global _CVS_CACHE
    if _CVS_CACHE is None:
        with open(_CVS_PATH, "rb") as f:
            _CVS_CACHE = orjson.loads(f.read())

    return _CVS_CACHE    

# Background Types
def _initialize_background_types_cache(background_types_list):
    global BACKGROUND_TYPES_BY_ID
    BACKGROUND_TYPES_BY_ID = {int(bg["id"]): bg for bg in background_types_list}

def get_background_type_by_id(bg_id):
    return BACKGROUND_TYPES_BY_ID.get(int(bg_id))

# Plane upgrade brackets: {plane_type_id: [key_for_level_1, key_for_level_2, ...]},
# sorted by level and gap-free from 1. A plane's bracket sequence depends only
# on its type, so build_plane_upgrades can slice this list by upgrade_level
# instead of doing a lookup per level - matters at scale (whale accounts
# reportedly have 20k+ planes; see src/utils.py).
def _initialize_plane_upgrade_keys_cache(plane_upgrade_types):
    global PLANE_UPGRADE_LEVEL_KEYS
    
    by_plane = {}
    for key, spec in plane_upgrade_types.items():
        level = spec["level"]
        for plane_type_id in spec["attachableTo"]:
            by_plane.setdefault(int(plane_type_id), {})[level] = int(key)

    index = {}
    for plane_type_id, levels in by_plane.items():
        ordered = []
        for lvl in range(1, max(levels) + 1):
            if lvl not in levels:
                break  # gap: stop rather than emit a wrong key for a higher level
            ordered.append(levels[lvl])
        index[plane_type_id] = ordered
    PLANE_UPGRADE_LEVEL_KEYS = index

def get_plane_upgrade_keys_up_to(plane_type_id, level):
    return PLANE_UPGRADE_LEVEL_KEYS.get(int(plane_type_id), [])[:level]