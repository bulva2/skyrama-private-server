from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy import func
from src.database import session_scope, ChatMessage, Player
from src.dependencies import get_current_user
from src.chat_moderation import moderate_msg
from datetime import datetime, timedelta

router = APIRouter(prefix="/chat", tags=["chat_api"])

# Rate limiting: store last message time per user {user_id: timestamp}
_user_last_message_time = {}

@router.get("/messages")
async def load_last_messages(user_id: int = Depends(get_current_user)):
    """Fetch last 50 chat messages (requires authentication)"""
    try:
        with session_scope() as session:
            total_count = session.query(func.count(ChatMessage.id)).scalar()
            offset = max(0, total_count - 50)
            messages = session.query(ChatMessage).order_by(ChatMessage.created_at.asc()).offset(offset).all()
            
            result = []
            for msg in messages:  # Already oldest to newest
                day = msg.created_at.day
                month = msg.created_at.month
                time_str = msg.created_at.strftime("%H:%M")
                timestamp = f"{day}.{month}. {time_str}"
                
                result.append({
                    "user": msg.user.username if msg.user_id != user_id else "You",  # Safe: from DB
                    "text": msg.message,         # Safe: stored as-is, JS renders with textContent (prevents XSS)
                    "created_at": timestamp
                })
            
            return {"messages": result}
    except Exception as e:
        print(f"Error loading messages: {e}")
        return {"messages": []}
    
@router.post("/send")
async def send_message(request: Request, user_id: int = Depends(get_current_user)):
    """Send a chat message (requires authentication)"""
    try:
        # Rate limiting: max 1 message per 2 seconds
        now = datetime.now()
        last_time = _user_last_message_time.get(user_id)
        if last_time and (now - last_time).total_seconds() < 5:
            raise HTTPException(status_code=429, detail="You're sending messages too fast. Wait a moment.")
        
        body = await request.json()
        message_text = body.get("message", "").strip()
        
        # Validation
        if not message_text:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        if len(message_text) > 200:
            raise HTTPException(status_code=400, detail="Message too long (max 200 chars)")
        
        message_text = moderate_msg(message_text)
        
        # Save to database (parameterized query prevents SQL injection)
        with session_scope() as session:
            # Verify user still exists (prevents ID spoofing)
            user = session.query(Player).filter(Player.user_id == user_id).first()
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
            
            chat_msg = ChatMessage(
                user_id=user_id,
                message=message_text  # Stored as plain text, no HTML parsing
            )
            session.add(chat_msg)
            session.commit()
        
        # Update rate limit tracking
        _user_last_message_time[user_id] = now
        
        return {"status": "success", "message": "Message sent"}
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail="Failed to send message")

