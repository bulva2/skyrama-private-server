import orjson

from fastapi import APIRouter, Request, Form
from fastapi.responses import Response, PlainTextResponse, RedirectResponse
from typing import Dict, Any

from src.game_service import process_game_commands
from src.dependencies import get_user_lock
from src.debug import report_issue

import src.user_manager as user_manager

router = APIRouter()

@router.post("/SkyApi.php")
async def handle_request(
    request: Request,
    userId: int = Form(...),
    t: str = Form(...),
    d: str = Form(...)
):
    session = request.session

    lock = get_user_lock(userId)
    async with lock:
        json_data = user_manager.load_save_by_id(userId)

        if not isinstance(json_data, dict):
            report_issue("error", f"Failed to load data for user_id {userId} in handle_request")
            return PlainTextResponse("Error loading data for this user. Please try again later or contact us on discord.", status_code=500)
        
        if json_data.get("playerData", {}).get("token") != t:
            report_issue("warning", f"Token mismatch for user_id {userId} in handle_request")
            return RedirectResponse(url='/')
        
        raw_commands = orjson.loads(d)

        response_data: Dict[str, Any] | int = process_game_commands(userId, raw_commands, json_data, session)
        if isinstance(response_data, int) and response_data == -1:
            return PlainTextResponse("An error occured while verifying your data. If you believe this to be a mistake, please contact us on discord.", status_code=400)
        
        user_manager.modify_save_by_id(userId, json_data)
        return Response(orjson.dumps(response_data))
