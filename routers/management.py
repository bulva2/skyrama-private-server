from fastapi import APIRouter, Request, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.database import get_db_session, Player
from bundle import TEMPLATES_DIR

import math

router = APIRouter(prefix="/management", tags=["management"])
templates = Jinja2Templates(directory=TEMPLATES_DIR)

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
        
    return templates.TemplateResponse("management/player_detail.html", {
        "request": request,
        "player": player,
        "admin_user": admin_user,
        "flash_message": flash_message
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