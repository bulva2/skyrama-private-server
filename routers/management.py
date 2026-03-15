import uuid

from fastapi import APIRouter, Request, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from src.database import get_db_session, Player
from bundle import TEMPLATES_DIR
from state import state

import math

router = APIRouter(prefix="/management", tags=["management"])
templates = Jinja2Templates(directory=TEMPLATES_DIR)

def _get_quest_info(player: Player) -> dict:
    """Return current/prev/next seq_num info for 'main' and 'pilot' quests."""
    goals_data = player.goals_data or {}
    goals = goals_data.get("goals", {})
    goal_types = state.init_data.get("goalTypes", [])

    result = {}
    for quest_type in ["main", "pilot"]:
        current = goals.get(quest_type, {})
        current_seq_num = int(current.get("seq_num", -1))

        # Collect all unique seq_nums for this quest type without -1
        seq_nums = sorted(
            set(int(gt["seq_num"]) 
                for gt in goal_types
                    if gt.get("seq_type") == quest_type and int(gt["seq_num"]) >= 0
        ))

        prev_seq_num = None
        next_seq_num = None

        if current_seq_num == -1:
            # Quest type fully finished, so only allow going
            prev_seq_num = seq_nums[-1] if seq_nums else None
        else:
            lower = [s for s in seq_nums if s < current_seq_num]
            if lower:
                prev_seq_num = lower[-1]
            higher = [s for s in seq_nums if s > current_seq_num]
            if higher:
                next_seq_num = higher[0]

        result[quest_type] = {
            "current_seq_num": current_seq_num,
            "goal_types_id": current.get("goal_types_id", -1),
            "prev_seq_num": prev_seq_num,
            "next_seq_num": next_seq_num,
        }

    return result

def get_db():
    session = get_db_session()
    try:
        yield session
    finally:
        session.close()

def is_player_admin(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("userid")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT, 
            headers={"Location": "/"}
        )
    
    player = db.query(Player).filter(Player.user_id == user_id).first()
    if not player or not player.is_admin:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT, 
            headers={"Location": "/"}
        )
    return player

@router.get("/")
async def admin_dashboard(
    request: Request, 
    page: int = Query(1, ge=1), 
    search: str = Query("", max_length=50), 
    admin_user: Player = Depends(is_player_admin), 
    db: Session = Depends(get_db)
):
    per_page = 10
    query = db.query(Player)

    if search:
        query = query.filter(Player.username.ilike(f"%{search}%"))

    total_players = query.count()
    total_pages = math.ceil(total_players / per_page)

    players = query.order_by(Player.user_id).offset((page - 1) * per_page).limit(per_page).all()

    return templates.TemplateResponse("management/dashboard.html", {
        "request": request,
        "admin_user": admin_user,
        "players": players,
        "page": page,
        "total_pages": total_pages,
        "search": search
    })

@router.get("/player/{user_id}")
async def admin_player_detail(
    request: Request, 
    user_id: int,
    admin_user: Player = Depends(is_player_admin), # Protects the route
    db: Session = Depends(get_db)
):
    player = db.query(Player).filter(Player.user_id == user_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    flash_message = request.session.pop("flash_message", None)
        
    quest_info = _get_quest_info(player)

    return templates.TemplateResponse("management/player_detail.html", {
        "request": request,
        "player": player,
        "admin_user": admin_user,
        "flash_message": flash_message,
        "quest_info": quest_info
    })

@router.post("/player/{user_id}/ban", dependencies=[Depends(is_player_admin)])
async def admin_ban_player(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db)
):
    player = db.query(Player).filter(Player.user_id == user_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    player.is_banned = True
    player.player_data["token"] = str(uuid.uuid1()) # Rotate token to force a disconnect if the player is online
    flag_modified(player, "player_data")
    db.commit()

    request.session["flash_message"] = f"Player {player.username} has been banned!"

    return RedirectResponse(
        url=f"/management/player/{user_id}", 
        status_code=status.HTTP_302_FOUND
    )

@router.post("/player/{user_id}/unban", dependencies=[Depends(is_player_admin)])
async def admin_unban_player(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db)
):
    player = db.query(Player).filter(Player.user_id == user_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    player.is_banned = False
    db.commit()

    request.session["flash_message"] = f"Player {player.username} has been unbanned!"

    return RedirectResponse(
        url=f"/management/player/{user_id}", 
        status_code=status.HTTP_302_FOUND
    )

@router.post("/player/{user_id}/quest/{quest_type}/{direction}", dependencies=[Depends(is_player_admin)])
async def admin_quest_navigate(
    request: Request,
    user_id: int,
    quest_type: str,
    direction: str,
    db: Session = Depends(get_db)
):
    if quest_type not in ["main", "pilot"]:
        raise HTTPException(status_code=400, detail="Invalid quest type")
    if direction not in ["prev", "next"]:
        raise HTTPException(status_code=400, detail="Invalid direction")

    player = db.query(Player).filter(Player.user_id == user_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    goal_types = state.init_data.get("goalTypes", [])
    task_types = state.init_data.get("taskTypes", [])
    goals_data = dict(player.goals_data or {})
    goals = goals_data.setdefault("goals", {})
    current = goals.get(quest_type, {})
    current_seq_num = int(current.get("seq_num", -1))

    # Collect all unique seq_nums for this quest type, sorted ascending
    seq_nums = sorted(set(
        int(gt["seq_num"]) for gt in goal_types
        if gt.get("seq_type") == quest_type and int(gt["seq_num"]) >= 0
    ))

    target_seq_num = None
    if direction == "prev":
        if current_seq_num == -1:
            target_seq_num = seq_nums[-1] if seq_nums else None
        else:
            lower = [s for s in seq_nums if s < current_seq_num]
            target_seq_num = lower[-1] if lower else None
    else:  # next
        if current_seq_num != -1:
            higher = [s for s in seq_nums if s > current_seq_num]
            target_seq_num = higher[0] if higher else None

    if target_seq_num is None:
        dir_label = "previous" if direction == "prev" else "next"
        request.session["flash_message"] = f"No {dir_label} quest available for '{quest_type}'."
        return RedirectResponse(url=f"/management/player/{user_id}", status_code=status.HTTP_302_FOUND)

    # Find the matching goalType definition
    target_goal = next(
        (gt for gt in goal_types
         if gt.get("seq_type") == quest_type and int(gt["seq_num"]) == target_seq_num),
        None
    )

    if target_goal is None:
        request.session["flash_message"] = f"Could not find goal definition for {quest_type} seq_num {target_seq_num}."
        return RedirectResponse(url=f"/management/player/{user_id}", status_code=status.HTTP_302_FOUND)

    # Build task list with num_completed reset to 0
    new_tasks = []
    for task in task_types:
        if int(task.get("goal_types_id", -1)) == int(target_goal["id"]):
            new_task = dict(task)
            new_task["num_completed"] = 0
            new_tasks.append(new_task)

    goals[quest_type] = {
        "goal_types_id": target_goal["id"],
        "seq_num": target_seq_num,
        "tasks": new_tasks
    }
    player.goals_data = goals_data
    flag_modified(player, "goals_data")
    db.commit()

    dir_label = "previous" if direction == "prev" else "next"
    request.session["flash_message"] = f"Quest '{quest_type}' moved to {dir_label} quest (seq_num: {target_seq_num})."
    return RedirectResponse(url=f"/management/player/{user_id}", status_code=status.HTTP_302_FOUND)