import time
import logging
import hashlib
import bcrypt
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.database import get_db_session, Player, Plane
from src.utils import get_level_from_xp
from state import state
import src.user_manager as user_manager

router = APIRouter(prefix="/public_api", tags=["public_api"])

# ── Cache stores: {user_id: (fetched_at_monotonic, data_dict)} ──────────────
_PROFILE_TTL = 5        # seconds
_TRAFFIC_TTL = 120      # 2 minutes

_profile_cache: dict[int, tuple[float, dict]] = {}
_traffic_cache: dict[int, tuple[float, dict]] = {}

# ── /profile ─────────────────────────────────────────────────────────────────

@router.get("/profile")
async def get_profile(user_id: int = Query(..., description="Player user ID")):
    t_start = time.perf_counter()
    now = time.monotonic()

    cached = _profile_cache.get(user_id)
    if cached and (now - cached[0]) < _PROFILE_TTL:
        elapsed = (time.perf_counter() - t_start) * 1000
        logging.debug(f"[public_api] /profile user={user_id} cache_hit {elapsed:.2f}ms")
        return JSONResponse(content=cached[1], headers={"X-Response-Time": f"{elapsed:.2f}ms", "X-Cache": "HIT"})

    session = get_db_session()
    try:
        player: Optional[Player] = (
            session.query(Player).filter(Player.user_id == user_id).first()
        )
    except Exception as e:
        logging.error(f"[public_api] /profile DB error for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    finally:
        session.close()

    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")

    xp = player.player_data.get("xp", 0) if player.player_data else 0
    level = get_level_from_xp(xp, state.init_data["playerData"]["xp_level_caps"])

    data = {
        "user_id": player.user_id,
        "username": player.username,
        "level": level,
        "location_id": player.location_id,
        "last_login": player.last_login.isoformat() if player.last_login else None,
    }

    _profile_cache[user_id] = (now, data)
    elapsed = (time.perf_counter() - t_start) * 1000
    logging.debug(f"[public_api] /profile user={user_id} db_fetch {elapsed:.2f}ms")
    return JSONResponse(content=data, headers={"X-Response-Time": f"{elapsed:.2f}ms", "X-Cache": "MISS"})


# ── /traffic ─────────────────────────────────────────────────────────────────

@router.get("/traffic")
async def get_traffic(user_id: int = Query(..., description="Player user ID")):
    t_start = time.perf_counter()
    now = time.monotonic()

    cached = _traffic_cache.get(user_id)
    if cached and (now - cached[0]) < _TRAFFIC_TTL:
        elapsed = (time.perf_counter() - t_start) * 1000
        logging.debug(f"[public_api] /traffic user={user_id} cache_hit {elapsed:.2f}ms")
        return JSONResponse(content=cached[1], headers={"X-Response-Time": f"{elapsed:.2f}ms", "X-Cache": "HIT"})

    session = get_db_session()
    try:
        # Verify player exists
        exists = session.query(Player.user_id).filter(Player.user_id == user_id).first()
        if exists is None:
            raise HTTPException(status_code=404, detail="Player not found")

        planes = (
            session.query(Plane.owner_id, Plane.to_player_id, Plane.flight_status)
            .filter(
                (Plane.owner_id == user_id) | (Plane.to_player_id == user_id)
            )
            .all()
        )
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"[public_api] /traffic DB error for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    finally:
        session.close()

    outbound = 0
    inbound = 0

    for owner_id, to_player_id, flight_status in planes:
        # Only count planes that are actually in flight (flight_status != HANGAR/HOME)
        if owner_id == user_id and to_player_id not in (-1, user_id) and flight_status != 0:
            outbound += 1
        elif owner_id != user_id and to_player_id == user_id and flight_status != 0:
            inbound += 1

    data = {
        "user_id": user_id,
        "inbound": inbound,
        "outbound": outbound,
        "cached_until": int(time.time()) + _TRAFFIC_TTL,
    }

    _traffic_cache[user_id] = (now, data)
    elapsed = (time.perf_counter() - t_start) * 1000
    logging.debug(f"[public_api] /traffic user={user_id} db_fetch {elapsed:.2f}ms")
    return JSONResponse(content=data, headers={"X-Response-Time": f"{elapsed:.2f}ms", "X-Cache": "MISS"})


# ── /verify_login ────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/verify_login")
async def verify_login(request: LoginRequest):
    """
    Verify login credentials for an external app.
    
    Returns:
      - 200 OK with success=true and user_id if credentials are valid
      - 401 Unauthorized if credentials are invalid or user is banned
      - 500 if database error occurs
    """
    t_start = time.perf_counter()
    
    logging.debug(f"[public_api] /verify_login request.username={repr(request.username)} request.password={repr(request.password)}")
    
    stored_hash = user_manager.fetch_pwd_hash_by_name(request.username)
    
    if not stored_hash:
        elapsed = (time.perf_counter() - t_start) * 1000
        logging.debug(f"[public_api] /verify_login user={request.username} invalid_user {elapsed:.2f}ms")
        raise HTTPException(status_code=401, detail="Invalid username or password")

    hashed_pwd = hashlib.sha256(request.password.encode('utf-8')).hexdigest().encode('utf-8')
    
    logging.debug(f"[public_api] /verify_login user={request.username} stored_hash={stored_hash} hashed_pwd={hashed_pwd}")

    if not bcrypt.checkpw(hashed_pwd, stored_hash):
        elapsed = (time.perf_counter() - t_start) * 1000
        logging.debug(f"[public_api] /verify_login user={request.username} invalid_password {elapsed:.2f}ms")
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    try:
        json_data = user_manager.load_save_by_name(request.username)
        
        if isinstance(json_data, int) or "playerData" not in json_data:
            logging.error(f"[public_api] /verify_login user={request.username} corrupted data")
            raise HTTPException(status_code=500, detail="Failed to load user data")
        
        user_id = json_data["playerData"]["account_id"]
        
        # Check if user is banned
        if user_manager.is_user_banned(username=request.username):
            elapsed = (time.perf_counter() - t_start) * 1000
            logging.debug(f"[public_api] /verify_login user={request.username} user_id={user_id} banned {elapsed:.2f}ms")
            raise HTTPException(status_code=401, detail="User account is banned")
        
        elapsed = (time.perf_counter() - t_start) * 1000
        logging.debug(f"[public_api] /verify_login user={request.username} user_id={user_id} success {elapsed:.2f}ms")
        
        return JSONResponse(
            content={
                "success": True,
                "user_id": user_id,
                "username": request.username,
            },
            headers={"X-Response-Time": f"{elapsed:.2f}ms"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"[public_api] /verify_login user={request.username} error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
