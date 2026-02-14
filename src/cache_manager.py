import os
import orjson
from pathlib import Path

_CVS_CACHE = None
_CVS_PATH = os.path.join(Path(__file__).parents[1], "data", "getCv.json.def")

BACKGROUND_TYPES_BY_ID = {}

def initialize_cache(init_data):
    _initialize_background_types_cache(init_data["backgroundTypes"])
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