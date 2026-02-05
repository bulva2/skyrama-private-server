import time
import json
import logging
import uuid
import hashlib
import os
from pathlib import Path
from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.cors import CORSMiddleware

from commands import *
from bundle import TEMPLATES_DIR, STUB_DIR, STYLES_DIR, ASSETS_DIR
from src.utils import get_level_from_xp
from src.database import init_database
import src.debug as debug
import src.user_manager as user_manager
import src.config_handler as config_handler
import src.validator as validator

# Config
config_handler.run()
config = config_handler.get_config()

# Global state
maintenance = {"maintenance": False, "startTime": 0}
init_data = {}
obj_data = {}
langstrings = {}
ADMINS = []
server_ip = ""
assets_ip = ""

# Request Locking to prevent race conditions
_user_locks = {}

def get_user_lock(user_id: int) -> asyncio.Lock:
    if user_id not in _user_locks:
        _user_locks[user_id] = asyncio.Lock()
    return _user_locks[user_id]

@asynccontextmanager
async def lifespan(app: FastAPI):
    global init_data, obj_data, langstrings, ADMINS, server_ip, assets_ip
    logging.info("Loading the server, please wait..")
    
    # Init DB
    init_database(config.get("Database", "connection_string"))
    
    # Load Init Data
    p = Path(__file__).parent
    logging.info("Loading init data...")
    
    with open(os.path.join(p, "data", "global_init_data.json.def"), "r", encoding="utf-8") as f:
        init_data = json.loads(f.read())

    with open(os.path.join(p, "data", "obj.json.def"), "r", encoding="utf-8") as f:
        obj_data = json.loads(f.read())
        
    user_manager.save_players_by_location_id()
    
    # Load language files
    for filename in os.listdir(os.path.join(p, "templates", "languages")):
        with open(os.path.join(p, "templates", "languages", filename), "r", encoding="utf-8") as f:
            langstrings[filename[0:-5]] = json.loads(f.read())

    # Load admins
    ADMINS = [int(x.strip()) for x in config.get("AdminUsers", "admin_ids", fallback="-1").split(",")]
    
    # URL setup
    host = config.get("ServerSettings", "host", fallback="127.0.0.1").replace("http://", "").replace("https://", "")
    port = int(config.get("ServerSettings", "port", fallback="3800"))
    use_https = config.getboolean("ServerSettings", "use_https", fallback=False)
    protocol = "https" if use_https else "http"
    server_ip = f"{protocol}://{host}:{port}"
    assets_ip = server_ip

    logging.info(f"Server initialized on {server_ip}")
    
    yield
    
    # Shutdown logic
    logging.info("Server is shutting down, have a great day! ^^")

app = FastAPI(lifespan=lifespan)

# Middleware
app.add_middleware(SessionMiddleware, secret_key="SECRET_KEY")

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
    "general.getCv": handle_getCv,
    "general.soundIsOn": handle_soundIsOn,
    "general.getConfig": handle_getConfig,
    "general.getInitState": handle_getInitState,
    "playerdata.setbooster": handle_setbooster,
    "playerdata.setLocation": handle_setLocation,
    "buddy.getAll": handle_buddyGetAll,
    "planes.get": handle_planesGet,
    "planes.setState": handle_planesSetState,
    "placeable.place": handle_placeablePlace,
    "planes.takeMeans": handle_planesTakeMeans,
    "planes.sendback": handle_planesSendback,
    "planes.buy": handle_planesBuy,
    "account.getLatest": handle_accountGetLatest,
    "planes.send": handle_planesSend,
    "terminals.buy": handle_terminalsBuy,
    "landside_buildings.harvest": handle_landside_buildingsHarvest,
    "flashCookies.set": handle_flashcookiesSet,
    "buddy.search": handle_buddySearch,
    "buddy.invite": handle_buddyInvite,
    "buddy.accept": handle_buddyAccept,
    "playerdata.updateSettings": handle_updateSettings,
    "planes.miss": handle_planesMiss,
    "buddy.endRelationship": handle_buddyEndRelationship,
    "buddy.decline": handle_buddyDecline,
    "bays.buy": handle_baysBuy,
    "runways.buy": handle_runwaysBuy,
    "special_buildings.buy": handle_specialBuildingsBuy,
    "placeable.setInStorage": handle_placeableSetInStorage,
    "lucky_luggage.spin": handle_luckyLuggageSpin,
    "landside_buildings.buy": handle_landsideBuildingsBuy,
    "packages.buy": handle_packagesBuy,
    "planes.upgrade": handle_planesUpgrade,
    "planes.scrap": handle_planesScrap,
    "goals.buyTask": handle_goalsBuyTask,
    "playerdata.updateLevel": handle_playerdataUpdateLevel,
    "planes.createFlyBy": handle_planesCreateFlyBy,
    "planes.sendbackflyby": handle_planesSendBackFlyBy,
    "planes.removeFlyByPlane": handle_planesRemoveFlyByPlane,
    "planes.onStartCargoTutorial": handle_planesOnStartCargoTutorial,
    "cargoshops.fillShop": handle_cargoshopsFillShop,
    "cargoshops.collectSalesRevenue": handle_cargoshopsCollectSalesRevenue,
    "general.getBuddyInitState": handle_getBuddyInitState,
    "resource_items.buy": handle_resourceItemsBuy,
    "playerdata.updateBuddypingTime": handle_updateBuddypingTime,
    "playerdata.deleteBuddypingTime": handle_deleteBuddypingTime,
    "cargoshops.buy": handle_cargoshopsBuy,
    "cargoshops.buyCargo": handle_cargoshopsBuyCargo,
    "cargoshops.buyCapacity": handle_cargoshopsBuyCapacity,
    "bays.sell": handle_sell,
    "landside_buildings.sell": handle_sell,
    "runways.sell": handle_sell,
    "terminals.sell": handle_sell,
    "backgrounds.buy": handle_backgroundsBuy,
    "backgrounds.makeCurrent": handle_backgroundsMakeCurrent,
    "landmarks.buy": handle_landmarksBuy,
    "landmarks.makeCurrent": handle_landmarksMakeCurrent,
    "hangars.upgrade": handle_hangarsUpgrade,
    "map_extensions.buy": handle_mapExpansionsBuy,        
    "hangars.buy": handle_hangarsBuy,
    "buddy.collectPassenger": handle_buddyCollectPassenger,
    "crafting.buySlot": handle_craftingBuySlot,
    "evoucher.book": handle_evoucherBook,
    "souvenirs.takeReward": handle_souvenirsTakeReward,
    "crafting.buyMaterials": handle_craftingBuyMaterials,
    "crafting.processCraftingStep": handle_craftingProcessCraftingStep,
    "crafting.start": handle_craftingStart,
    "crafting.instant": handle_craftingInstant,
    "general.trackFlashError": handle_trackFlashError,
    "crafting.collect": handle_craftingCollect
}

# Disabled for testing purposes, keep disabled for now -bulva2
REORDER_COMMANDS = False
def resolve_command_dependencies(command_data):
    if not REORDER_COMMANDS:
        return command_data
    
    plane_setState_commands = []
    plane_send_commands = []
    plane_takeMeans_commands = []
    other_commands = []
    
    for command in command_data:
        if command["m"] == "planes.setState" and "id" in command.get("p", {}):
            plane_setState_commands.append(command)
        elif (command["m"] == "planes.send" or command["m"] == "planes.sendback") and "id" in command.get("p", {}):
            plane_send_commands.append(command)
        elif command["m"] == "planes.takeMeans" and "plane_id" in command.get("p", {}):
            plane_takeMeans_commands.append(command)
        else:
            other_commands.append(command)
    
    ordered_commands = []
    ordered_commands.extend(other_commands)
    ordered_commands.extend(plane_setState_commands)
    ordered_commands.extend(plane_send_commands)
    ordered_commands.extend(plane_takeMeans_commands)
    
    return ordered_commands

# Routes

@app.get("/crossdomain.xml")
async def crossdomain():
    return HTMLResponse(content=open(os.path.join(STUB_DIR, "crossdomain.xml")).read(), media_type="application/xml")

@app.get("/play")
async def play(request: Request, locale: str = None):
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
        "SERVERIP": server_ip,
        "ASSETSIP": assets_ip,
        "langstrings": langstrings.get(lang, {})
    })

@app.get("/")
async def homepage(request: Request, locale: str = None):
    if maintenance["maintenance"]:
        return RedirectResponse(url='/maintenance')
    
    session = request.session
    lang = locale if locale else session.get("lang", "en")
    session["lang"] = lang
    langUpper = lang.upper()
    
    return templates.TemplateResponse("home.html", {
        "request": request,
        "SERVERIP": server_ip,
        "ASSETSIP": assets_ip,
        "playerCount": user_manager.get_player_count(),
        "langstrings": langstrings.get(lang, {}),
        "lang": lang,
        "langUpper": langUpper
    })

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...), locale: str = None):
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
        "SERVERIP": server_ip,
        "ASSETSIP": assets_ip,
        "playerCount": user_manager.get_player_count(),
        "langstrings": langstrings.get(lang, {}),
        "lang": lang,
        "langUpper": langUpper,
        "msg": msg
    })

@app.post("/register")
async def register(request: Request, RegUsername: str = Form(...), RegPassword: str = Form(...), RegEmail: str = Form(...), locale: str = None):
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
        "SERVERIP": server_ip,
        "ASSETSIP": assets_ip,
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
    if "userid" in session and session["userid"] in ADMINS:
        maintenance["maintenance"] = True
        maintenance["startTime"] = int(time.time())
        return "Success!"
    return "good try lmao"

@app.get("/set-maintenance/off")
async def setMaintenanceOff(request: Request):
    session = request.session
    if "userid" in session and session["userid"] in ADMINS:
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
async def logout(request: Request, locale: str = None):
    session = request.session
    if "username" in session:
        del session["username"]
    if "userid" in session:
        del session["userid"]
    if "token" in session:
        del session["token"]

    lang = locale if locale else session.get("lang", "en")
    session["lang"] = lang
    langUpper = lang.upper()
    return templates.TemplateResponse("logout.html", {
        "request": request,
        "lang": lang,
        "langUpper": langUpper,
        "langstrings": langstrings.get(lang, {}),
        "ASSETSIP": assets_ip,
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
        
        if json_data == -1: # User not found or error
            return PlainTextResponse("token_error")

        if json_data["playerData"]["token"] == t:
            command_data = json.loads(d)
            total_response = {"rpcResults": []}
            
            # Start level check
            start_level = get_level_from_xp(json_data["playerData"]["xp"], init_data["playerData"]["xp_level_caps"])
            
            total_items_to_add_to_obj = []
            ordered_command_data = resolve_command_dependencies(command_data)
            
            command = {}
            for cmd in ordered_command_data:
                command = cmd # Keep track of last command
                if command["m"] in available_commands:
                    logging.info(f"Command {command['m']} handled")
                    command["previous_air_coins"] = json_data["playerData"]["air_coins"]
                    
                    handle_lucky_luggage_live(command, userId, json_data)
                    
                    rpcResult = {}
                    items_to_add_to_obj = []
                    handler = available_commands[command["m"]]
                    
                    # Handlers are sync, so we call them directly
                    handler(command, userId, rpcResult, items_to_add_to_obj, json_data, init_data)
                    
                    if rpcResult.get("i") == -1:
                        logging.warning(f"User {userId} disconnected/cheat detected.")
                        return PlainTextResponse("Could not get Sky_Instance_Plane object with unique id 1435_12297741")
                        
                    total_response["rpcResults"].append(rpcResult)
                    
                    handle_goal(command, userId, "main", items_to_add_to_obj, json_data, init_data)
                    handle_goal(command, userId, "pilot", items_to_add_to_obj, json_data, init_data)
                    handle_goal(command, userId, "daily", items_to_add_to_obj, json_data, init_data)
                    
                    total_items_to_add_to_obj += items_to_add_to_obj
                else:
                    logging.error(f"Command {command['m']} not implemented")
                    session["error_mode"] = "unimplemented"
                    return PlainTextResponse("Could not get Sky_Instance_Plane object with unique id 1435_12297741")

            # Level up check
            end_level = get_level_from_xp(json_data["playerData"]["xp"], init_data["playerData"]["xp_level_caps"])
            if start_level != end_level:
                for i in range(end_level - start_level):
                    json_data["playerData"]["air_coins"] += 850
                    json_data["playerData"]["air_cash"] += 2
            
            obj = {}
            handle_addObj(command, userId, obj, total_items_to_add_to_obj, json_data, init_data, obj_data)
            total_response["obj"] = obj
            
            user_manager.modify_save_by_id(userId, json_data)
            return total_response
        else:
            logging.critical(f"Security alert: User {userId} attempted to use an invalid token!")
            return PlainTextResponse("token_error")

# Run only if executed directly
if __name__ == "__main__":
    import uvicorn
    host = config.get("ServerSettings", "host", fallback="127.0.0.1")
    port = int(config.get("ServerSettings", "port", fallback="3800"))
    uvicorn.run("server:app", host=host, port=port, reload=True)
