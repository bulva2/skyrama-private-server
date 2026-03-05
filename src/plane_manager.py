from src.enums import PlaneState

def add_plane(json_data: dict, plane_type_id: int, user_id: int, init_data: dict) -> None:
    for plane_type in init_data["planeTypes"]:
        if int(plane_type["id"]) == plane_type_id:
            container_id = _get_hangar_id_from_plane(plane_type, json_data, init_data)

            plane = {
                "souvenir_types_id": -1,
                "active_count": 1,
                "id": json_data["playerData"]["next_object_id"],
                "plane_type_id": plane_type_id,
                "container_id": container_id,
                "subcontainer_id": 1,
                "to_player_id": -1,
                "departure_time": -1,
                "arrival_time": -1,
                "kerosene_boost_flag": 0,
                "flight_status": PlaneState.HANGAR.value, # (0)
                "buddy_points": plane_type["buddy_points_yield"],
                "contents_count": plane_type["capacity"],
                "air_coins": plane_type["air_coins_yield"],
                "xp": plane_type["xp_yield"],
                "wares_revenue": plane_type["wares_revenue_capacity"],
                "banner_id": -1,
                "start_service_time": 0,
                "last_state_change_time": 0,
                "drop_consumable_id": 0,
                "drop_consumable_amount": 0,
                "instantland": 0,
                "player_id": user_id,
                "from_location_id": -1,
                "from_user_name": "",
                "upgrade_level": 0
            }
            json_data["planes"].append(plane)
            json_data["playerData"]["next_object_id"] += 1
            break

def _get_hangar_id_from_plane(plane: dict ,json_data: dict, init_data: dict) -> int:
    hangar_type_id = _get_hangar_type_id_from_plane(plane, init_data)

    for hangar in json_data["hangars"]:
        if int(hangar["hangar_types_id"]) == hangar_type_id:
            return hangar["id"]
    
    return -1
        
def _get_hangar_type_id_from_plane(plane: dict , init_data: dict) -> int:
    planeSize = plane["size"]
    planeType = plane["type"]

    for hangarType in init_data["hangarTypes"]:
        if hangarType["sml"] == planeSize and hangarType["aircraft_type"] == planeType:
            return hangarType["id"]
    
    return -1