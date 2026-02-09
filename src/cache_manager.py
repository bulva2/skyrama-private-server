BACKGROUND_TYPES_BY_ID = {}

def initialize_cache(init_data):
    _initialize_background_types_cache(init_data["backgroundTypes"])

def _initialize_background_types_cache(background_types_list):
    global BACKGROUND_TYPES_BY_ID
    BACKGROUND_TYPES_BY_ID = {int(bg["id"]): bg for bg in background_types_list}

def get_background_type_by_id(bg_id):
    return BACKGROUND_TYPES_BY_ID.get(int(bg_id))