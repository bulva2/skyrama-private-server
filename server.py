from pathlib import Path
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse, Response
from fastapi.responses import ORJSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.cors import CORSMiddleware

from bundle import TEMPLATES_DIR, STUB_DIR, STYLES_DIR, ASSETS_DIR
from src.utils import get_level_from_xp
from src.database import init_database
from src.cache_manager import initialize_cache
import src.debug as debug
import src.user_manager as user_manager
import src.config_handler as config_handler
import src.validator as validator

from commands import *
from state import state

import asyncio
import time
import orjson
import logging
import pyfiglet
import uuid
import hashlib
import os

# Config
config_handler.run()
config = config_handler.get_config()

# Global state
maintenance = {"maintenance": False, "startTime": 0}
langstrings = {}

# Request Locking to prevent race conditions
_user_locks = {}

def get_user_lock(user_id: int) -> asyncio.Lock:
    if user_id not in _user_locks:
        _user_locks[user_id] = asyncio.Lock()
    return _user_locks[user_id]

@asynccontextmanager
async def lifespan(app: FastAPI):
    global langstrings

    print(pyfiglet.figlet_format("Skyrama Private Server", font="slant", width=200))
    logging.info("Loading the server, please wait..")
    
    raw_conn_str = config.get("Database", "connection_string")
    db_password = os.environ.get("DB_PASSWORD")

    if db_password == "Your-Database-Password-Here":
        logging.critical("You haven't changed the database password from the .env-example!")
        logging.critical("Please change the DB_PASSWORD variable in the .env file to your database password before running the server!\n")
        exit(1)

    if db_password:
        conn_str = raw_conn_str.replace("${DB_PASSWORD}", db_password)
        init_database(conn_str)
    else:
        logging.critical("Database password not found in .env file. Make sure that you renamed .env-example to .env and that you set the DB_PASSWORD variable to your password!")
        exit(2)
    
    # Load Init Data
    p = Path(__file__).parent
    logging.info("Loading init data...")
    
    with open(state.data_path / "global_init_data.json.def", "rb") as f:
        state.init_data = orjson.loads(f.read())

    # Load global cache
    initialize_cache(state.init_data)

    with open(state.data_path / "obj.json.def", "rb") as f:
        state.obj_data = orjson.loads(f.read())
        
    user_manager.save_players_by_location_id()
    
    # Load language files
    for filename in os.listdir(os.path.join(p, "templates", "languages")):
        with open(os.path.join(p, "templates", "languages", filename), "rb") as f:
            langstrings[filename[0:-5]] = orjson.loads(f.read())

    # Load admins
    state.admins = [int(x.strip()) for x in config.get("AdminUsers", "admin_ids", fallback="-1").split(",")]
    
    # URL setup
    host = config.get("ServerSettings", "host", fallback="127.0.0.1").replace("http://", "").replace("https://", "")
    port = int(config.get("ServerSettings", "port", fallback="3800"))
    use_https = config.getboolean("ServerSettings", "use_https", fallback=False)
    protocol = "https" if use_https else "http"
    state.server_ip = f"{protocol}://{host}:{port}"

    if config.get("Webhooks", "error_webhook", fallback="") == "":
        logging.warning("No error webhook configured, errors will not be sent to Discord!")

    if config.get("Webhooks", "registration_webhook", fallback="") == "":
        logging.warning("No registration webhook configured, registrations will not be sent to Discord!")

    logging.info(f"Server initialized on {state.server_ip}")
    yield
    
    # Shutdown logic
    logging.info("Server is shutting down, have a great day! ^^")

app = FastAPI(lifespan=lifespan, default_response_class=ORJSONResponse)

# Middleware
app.add_middleware(SessionMiddleware, secret_key="ChangeThisSecretKeyToSmtRandom")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")
app.mount("/templates/styles", StaticFiles(directory=STYLES_DIR), name="styles")

templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Available Commands Map
available_commands = {
    "account.getLatest": handle_accountGetLatest,
    "backgrounds.buy": handle_backgroundsBuy,
    "backgrounds.makeCurrent": handle_backgroundsMakeCurrent,
    "bays.buy": handle_baysBuy,
    "bays.sell": handle_sell,
    "buddy.accept": handle_buddyAccept,
    "buddy.collectPassenger": handle_buddyCollectPassenger,
    "buddy.decline": handle_buddyDecline,
    "buddy.endRelationship": handle_buddyEndRelationship,
    "buddy.getAll": handle_buddyGetAll,
    "buddy.invite": handle_buddyInvite,
    "buddy.receivePassengers": handle_buddyReceivePassengers,
    "buddy.search": handle_buddySearch,
    "cargoshops.buy": handle_cargoshopsBuy,
    "cargoshops.buyCapacity": handle_cargoshopsBuyCapacity,
    "cargoshops.buyCargo": handle_cargoshopsBuyCargo,
    "cargoshops.collectSalesRevenue": handle_cargoshopsCollectSalesRevenue,
    "cargoshops.fillShop": handle_cargoshopsFillShop,
    "crafting.buyMaterials": handle_craftingBuyMaterials,
    "crafting.buySlot": handle_craftingBuySlot,
    "crafting.collect": handle_craftingCollect,
    "crafting.instant": handle_craftingInstant,
    "crafting.processCraftingStep": handle_craftingProcessCraftingStep,
    "crafting.start": handle_craftingStart,
    "evoucher.book": handle_evoucherBook,
    "flashCookies.set": handle_flashcookiesSet,
    "general.getBuddyInitState": handle_getBuddyInitState,
    "general.getConfig": handle_getConfig,
    "general.getCv": handle_getCv,
    "general.getInitState": handle_getInitState,
    "general.soundIsOn": handle_soundIsOn,
    "general.trackFlashError": handle_trackFlashError,
    "goals.buyTask": handle_goalsBuyTask,
    "hangars.buy": handle_hangarsBuy,
    "hangars.upgrade": handle_hangarsUpgrade,
    "landmarks.buy": handle_landmarksBuy,
    "landmarks.makeCurrent": handle_landmarksMakeCurrent,
    "landside_buildings.buy": handle_landsideBuildingsBuy,
    "landside_buildings.harvest": handle_landside_buildingsHarvest,
    "landside_buildings.sell": handle_sell,
    "lucky_luggage.spin": handle_luckyLuggageSpin,
    "map_extensions.buy": handle_mapExpansionsBuy,        
    "packages.buy": handle_packagesBuy,
    "placeable.place": handle_placeablePlace,
    "placeable.setInStorage": handle_placeableSetInStorage,
    "planes.buy": handle_planesBuy,
    "planes.createFlyBy": handle_planesCreateFlyBy,
    "planes.get": handle_planesGet,
    "planes.miss": handle_planesMiss,
    "planes.onStartCargoTutorial": handle_planesOnStartCargoTutorial,
    "planes.removeFlyByPlane": handle_planesRemoveFlyByPlane,
    "planes.scrap": handle_planesScrap,
    "planes.send": handle_planesSend,
    "planes.sendback": handle_planesSendback,
    "planes.sendbackflyby": handle_planesSendBackFlyBy,
    "planes.setState": handle_planesSetState,
    "planes.takeMeans": handle_planesTakeMeans,
    "planes.upgrade": handle_planesUpgrade,
    "playerdata.deleteBuddypingTime": handle_deleteBuddypingTime,
    "playerdata.setbooster": handle_setbooster,
    "playerdata.setLocation": handle_setLocation,
    "playerdata.updateBuddypingTime": handle_updateBuddypingTime,
    "playerdata.updateLevel": handle_playerdataUpdateLevel,
    "playerdata.updateSettings": handle_updateSettings,
    "recycling.collect": handle_recyclingCollect,
    "recycling.instant": handle_recyclingInstant,
    "recycling.start": handle_recyclingStart,
    "resource_items.buy": handle_resourceItemsBuy,
    "runways.buy": handle_runwaysBuy,
    "runways.sell": handle_sell,
    "souvenirs.takeReward": handle_souvenirsTakeReward,
    "special_buildings.buy": handle_specialBuildingsBuy,
    "terminals.buy": handle_terminalsBuy,
    "terminals.sell": handle_sell,
}

# Routes

@app.get("/crossdomain.xml")
async def crossdomain():
    return HTMLResponse(content=open(os.path.join(STUB_DIR, "crossdomain.xml")).read(), media_type="application/xml")

@app.get("/play")
async def play(request: Request, locale: Optional[str] = None):
    if maintenance["maintenance"]:
        return RedirectResponse(url='/maintenance')
    
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
        "langstrings": langstrings.get(lang, {})
    })

@app.get("/")
async def homepage(request: Request, locale: Optional[str] = None):
    if maintenance["maintenance"]:
        return RedirectResponse(url='/maintenance')
    
    session = request.session
    lang = locale if locale else session.get("lang", "en")
    session["lang"] = lang
    langUpper = lang.upper()
    
    return templates.TemplateResponse("home.html", {
        "request": request,
        "SERVERIP": state.server_ip,
        "playerCount": user_manager.get_player_count(),
        "langstrings": langstrings.get(lang, {}),
        "lang": lang,
        "langUpper": langUpper
    })

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...), locale: Optional[str] = None):
    if maintenance["maintenance"]:
        return RedirectResponse(url='/maintenance')
        
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
        "langstrings": langstrings.get(lang, {}),
        "lang": lang,
        "langUpper": langUpper,
        "msg": msg
    })

@app.post("/register")
async def register(request: Request, RegUsername: str = Form(...), RegPassword: str = Form(...), RegEmail: str = Form(...), locale: Optional[str] = None):
    if maintenance["maintenance"]:
        return RedirectResponse(url='/maintenance')

    session = request.session
    lang = locale if locale else session.get("lang", "en")
    langUpper = lang.upper()
    
    pwd_hash = hashlib.sha512(RegPassword.encode('utf-8')).hexdigest()
    msg = validator.validate_registration_form(RegUsername, RegPassword, RegEmail, user_manager.user_name_exists)
    
    if not msg:
        token = str(uuid.uuid1())
        uid = user_manager.create_new_account(RegUsername, pwd_hash, token)
        
        session["username"] = RegUsername
        session["userid"] = uid
        session["token"] = token
        
        debug.user_registered_webhook(uid, RegUsername)
        return RedirectResponse(url='/play', status_code=303)
            
    return templates.TemplateResponse("home.html", {
        "request": request,
        "SERVERIP": state.server_ip,
        "playerCount": user_manager.get_player_count(),
        "langstrings": langstrings.get(lang, {}),
        "lang": lang,
        "langUpper": langUpper,
        "msg": msg
    })

# Admin Routes
@app.get("/set-maintenance/on")
async def setMaintenanceOn(request: Request):
    session = request.session
    if "userid" in session and session["userid"] in state.admins:
        maintenance["maintenance"] = True
        maintenance["startTime"] = int(time.time())
        return "Success!"
    return "good try lmao"

@app.get("/set-maintenance/off")
async def setMaintenanceOff(request: Request):
    session = request.session
    if "userid" in session and session["userid"] in state.admins:
        maintenance["maintenance"] = False
        maintenance["startTime"] = 0
        return "Success!"
    return "good try lmao"

@app.get("/maintenance")
async def maintenanceWork(request: Request):
    return templates.TemplateResponse("maintenance.html", {"request": request})

@app.get("/error")
async def error(request: Request):
    session = request.session
    mode = session.get("error_mode", "error")
    if mode == "unimplemented":
        session["error_mode"] = "error"
        return templates.TemplateResponse("unimplemented.html", {"request": request})
    elif mode == "maintenance":
        session["error_mode"] = "error"
        return templates.TemplateResponse("maintenance.html", {"request": request})
    else:
        return templates.TemplateResponse("error.html", {"request": request})

@app.get("/logout")
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
        "langstrings": langstrings.get(lang, {}),
        "playerCount": user_manager.get_player_count()
    })

@app.post("/SkyApi.php")
async def handle_request(
    request: Request,
    userId: int = Form(...),
    t: str = Form(...),
    d: str = Form(...)
):
    session = request.session
    if maintenance["maintenance"]:
        session["error_mode"] = "maintenance"
        return PlainTextResponse("Maintenance Break! We are deeply sorry for the inconvenience. Grab a coffee and come back later ^^")

    # Acquire lock for this user to prevent race conditions
    async with get_user_lock(userId):
        json_data = user_manager.load_save_by_id(userId)
        if not isinstance(json_data, dict):
            return PlainTextResponse("token_error")

        if json_data.get("playerData", {}).get("token") == t:
            command_data = orjson.loads(d.encode())

            if not isinstance(command_data, list):
                session.clear()
                session["error_mode"] = "error"
                return templates.TemplateResponse("error.html", {"request": request})
            
            total_response: Dict[str, Any] = {"rpcResults": []}

            # Start level check
            start_level = get_level_from_xp(json_data["playerData"]["xp"], state.init_data["playerData"]["xp_level_caps"])
            
            total_items_to_add_to_obj = []
            
            command = {}
            for cmd in command_data:
                command = cmd # Keep track of last command
                if command["m"] in available_commands:
                    logging.info(f"Command {command['m']} handled")
                    command["previous_air_coins"] = json_data["playerData"]["air_coins"]
                    
                    handle_lucky_luggage_live(command, userId, json_data)
                    
                    rpcResult = {}
                    items_to_add_to_obj = []
                    handler = available_commands[command["m"]]
                    
                    # Handlers are sync, so we call them directly
                    handler(command, userId, rpcResult, items_to_add_to_obj, json_data, state.init_data)
                    
                    if rpcResult.get("i") == -1:
                        logging.warning(f"User {userId} disconnected/cheat detected.")
                        return PlainTextResponse("Could not get Sky_Instance_Plane object with unique id 1435_12297741")
                        
                    total_response["rpcResults"].append(rpcResult)
                    
                    handle_goal(command, userId, "main", items_to_add_to_obj, json_data, state.init_data)
                    handle_goal(command, userId, "pilot", items_to_add_to_obj, json_data, state.init_data)
                    handle_goal(command, userId, "daily", items_to_add_to_obj, json_data, state.init_data)
                    
                    total_items_to_add_to_obj += items_to_add_to_obj
                else:
                    logging.error(f"Command {command['m']} isn't implemented!")
                    session["error_mode"] = "unimplemented"
                    return PlainTextResponse("Could not get Sky_Instance_Plane object with unique id 1435_12297741")

            # Level up check
            end_level = get_level_from_xp(json_data["playerData"]["xp"], state.init_data["playerData"]["xp_level_caps"])
            if start_level != end_level:
                for i in range(end_level - start_level):
                    json_data["playerData"]["air_coins"] += 850
                    json_data["playerData"]["air_cash"] += 2
            
            obj = {}
            handle_addObj(command, userId, obj, total_items_to_add_to_obj, json_data, state.init_data, state.obj_data)
            total_response["obj"] = obj
            
            user_manager.modify_save_by_id(userId, json_data)
            return Response(orjson.dumps(total_response))
        else:
            logging.critical(f"Security alert: User {userId} attempted to use an invalid token!")
            return PlainTextResponse("token_error")
        
# Run only if executed directly
if __name__ == "__main__":
    import uvicorn
    host = config.get("ServerSettings", "host", fallback="127.0.0.1")
    port = int(config.get("ServerSettings", "port", fallback="3800"))
    uvicorn.run("server:app", host=host, port=port, reload=True)
