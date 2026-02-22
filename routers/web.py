from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from typing import Optional
from bundle import TEMPLATES_DIR, STUB_DIR
from state import state

from src.validator import validate_registration_form
from src.debug import user_registered_webhook

import uuid
import hashlib
import os

import src.user_manager as user_manager

router = APIRouter()
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@router.get("/")
async def homepage(request: Request, locale: Optional[str] = None):
    session = request.session
    lang = locale if locale else session.get("lang", "en")
    session["lang"] = lang
    langUpper = lang.upper()
    
    return templates.TemplateResponse("home.html", {
        "request": request,
        "SERVERIP": state.server_ip,
        "playerCount": user_manager.get_player_count(),
        "langstrings": state.langstrings.get(lang, {}),
        "lang": lang,
        "langUpper": langUpper
    })

@router.get("/error")
async def error(request: Request):
    session = request.session
    mode = session.get("error_mode", "error")
    if mode == "unimplemented":
        session["error_mode"] = "error"
        return templates.TemplateResponse("unimplemented.html", {"request": request})
    else:
        return templates.TemplateResponse("error.html", {"request": request})

@router.get("/crossdomain.xml")
async def crossdomain():
    return HTMLResponse(content=open(os.path.join(STUB_DIR, "crossdomain.xml")).read(), media_type="application/xml")

@router.get("/play")
async def play(request: Request, locale: Optional[str] = None):
    session = request.session
    if "username" not in session:
        return RedirectResponse(url="/")
        
    session["error_mode"] = "error"
    
    lang = locale if locale else session.get("lang", "en")
    session["lang"] = lang
    
    return templates.TemplateResponse("play.html", {
        "request": request,
        "username": session["username"],
        "userid": session["userid"],
        "token": session["token"],
        "lang": lang,
        "SERVERIP": state.server_ip,
        "langstrings": state.langstrings.get(lang, {})
    })

@router.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...), locale: Optional[str] = None):
    session = request.session
    lang = locale if locale else session.get("lang", "en")
    langUpper = lang.upper()
    
    pwd_hash = hashlib.sha512(password.encode('utf-8')).hexdigest()
    
    json_data = user_manager.load_save_by_name(username)
    
    msg = ''
    if json_data == -1:
        msg = 'bgc.error.login_invalidCredentials'
    elif json_data["playerData"]["password"] == pwd_hash:
        json_data["playerData"]["token"] = str(uuid.uuid1())
        user_id = json_data["playerData"]["account_id"]

        user_manager.modify_save_by_id(user_id, json_data, set_last_login=True)

        session["username"] = username
        session["userid"] = user_id
        session["token"] = json_data["playerData"]["token"]
        return RedirectResponse(url='/play', status_code=303)
    else:
        msg = 'bgc.error.login_invalidCredentials'
        
    return templates.TemplateResponse("home.html", {
        "request": request,
        "SERVERIP": state.server_ip,
        "playerCount": user_manager.get_player_count(),
        "langstrings": state.langstrings.get(lang, {}),
        "lang": lang,
        "langUpper": langUpper,
        "msg": msg
    })

@router.post("/register")
async def register(request: Request, RegUsername: str = Form(...), RegPassword: str = Form(...), RegEmail: str = Form(...), locale: Optional[str] = None):
    session = request.session
    lang = locale if locale else session.get("lang", "en")
    langUpper = lang.upper()
    
    pwd_hash = hashlib.sha512(RegPassword.encode('utf-8')).hexdigest()
    msg = validate_registration_form(RegUsername, RegPassword, RegEmail, user_manager.user_name_exists)
    
    if not msg:
        token = str(uuid.uuid1())
        uid = user_manager.create_new_account(RegUsername, pwd_hash, token)
        
        session["username"] = RegUsername
        session["userid"] = uid
        session["token"] = token
        
        user_registered_webhook(uid, RegUsername)
        return RedirectResponse(url='/play', status_code=303)
            
    return templates.TemplateResponse("home.html", {
        "request": request,
        "SERVERIP": state.server_ip,
        "playerCount": user_manager.get_player_count(),
        "langstrings": state.langstrings.get(lang, {}),
        "lang": lang,
        "langUpper": langUpper,
        "msg": msg
    })

@router.get("/logout")
async def logout(request: Request, locale: Optional[str] = None):
    session = request.session
    session.clear()

    lang = locale if locale else session.get("lang", "en")
    session["lang"] = lang
    langUpper = lang.upper()
    return templates.TemplateResponse("logout.html", {
        "request": request,
        "lang": lang,
        "langUpper": langUpper,
        "langstrings": state.langstrings.get(lang, {}),
        "playerCount": user_manager.get_player_count()
    })