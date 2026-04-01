"""FastAPI dependencies for authentication and authorization"""

from fastapi import Request, HTTPException, status, Depends
from sqlalchemy.orm import Session
from src.database import get_db_session, Player

def get_current_user(request: Request):
    """Dependency to get the currently authenticated user (requires active session)"""
    user_id = request.session.get("userid")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user_id

def get_db():
    """Dependency to get a database session"""
    session = get_db_session()
    try:
        yield session
    finally:
        session.close()

def is_player_admin(request: Request, db: Session = Depends(get_db)) -> Player:
    """Dependency to verify user is authenticated and is an admin"""
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
