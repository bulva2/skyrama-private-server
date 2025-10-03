# Import local stuff
import time
from commands import *
from werkzeug import Request
from bundle import TEMPLATES_DIR, STUB_DIR, STYLES_DIR, ASSETS_DIR
from src.utils import get_level_from_xp
import src.userManager as userManager
import src.configHandler as configHandler

# Import 3rd party stuff
import logging
import re
import random
import uuid
import hashlib
from pathlib import Path
import json
import os

from flask import Flask, render_template, send_from_directory, request, redirect, session
app = Flask(__name__, template_folder=TEMPLATES_DIR)

# Command batch state - shared between related commands in the same request
_command_batch_state = {}

def resolve_command_dependencies(command_data):
    """
    Ensures all necessary commands are executed in the correct order to prevent race conditions.
    """
    
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

def main():
    configHandler.run()
    logging.info("Loading the server, please wait..")
    logging.debug("Debug mode is enabled")
    
    ###############################
    # Setup list of game commands #
    ###############################
    
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
        "souvenirs.takeReward": handle_souvenirsTakeReward
    }
    logging.info("Loading init data...")
    
    p = Path(__file__).parents[0]
    
    with open(os.path.join(p, "data", "global_init_data.json.def"), "r", encoding="utf-8") as f:
        init_data = json.loads(f.read())
    f.close()

    with open(os.path.join(p, "data", "obj.json.def"), "r", encoding="utf-8") as f:
        obj_data = json.loads(f.read())
    f.close()

    # Sort accounts by location id
    userManager.save_players_by_location_id()
    
    # Load language files
    langstrings = {}
    for filename in os.listdir(os.path.join(p, "templates", "languages")):
        with open(os.path.join(p, "templates", "languages",
                 filename), "r", encoding="utf-8") as f:
            langstrings[filename[0:-5]] = json.loads(f.read())
        f.close()
    
    config = configHandler.get_config()

    maintenance = {"maintenance": False, "startTime": 0}

    # List of admin user IDs
    ADMINS = [int(x.strip()) for x in config.get("AdminUsers", "admin_ids", fallback="-1").split(",")]
    host = config.get("ServerSettings", "host", fallback="127.0.0.1").replace("http://", "").replace("https://", "")
    port = int(config.get("ServerSettings", "port", fallback="5050"))
    use_https = config.getboolean("ServerSettings", "use_https", fallback=False)
    protocol = "https" if use_https else "http"
    server_ip = f"{protocol}://{host}:{port}"
    
    use_alt_assets = config.getboolean("AlternativeAssetStore", "alternative_asset_store_enabled", fallback=False)
    if use_alt_assets:
        alt_host = config.get("AlternativeAssetStore", "alternative_asset_store_host", fallback="")
        alt_port = config.get("AlternativeAssetStore", "alternative_asset_store_port", fallback="")
        alt_use_https = config.getboolean("AlternativeAssetStore", "asset_store_use_https", fallback=False)
        alt_protocol = "https" if alt_use_https else "http"
        
        # If we have an alternative host
        if alt_host:
            # Clean the host (remove any protocol)
            alt_host = alt_host.replace("http://", "").replace("https://", "")
            
            if alt_port:
                assets_ip = f"{alt_protocol}://{alt_host}:{alt_port}"
            else:
                assets_ip = f"{alt_protocol}://{alt_host}"
                
            logging.info(f"Using alternative asset store: {assets_ip}")
        else:
            assets_ip = server_ip
    else:
        assets_ip = server_ip

    logging.info("Configuring server routes...")
    
    # Routing    
    @app.route("/play")
    def play():
        if maintenance["maintenance"]:
            return redirect('maintenance')
        
        # If not logged in, redirect to homepage
        if "username" not in session:
            return redirect("/")
        
        # Setup session
        session["error_mode"] = "error"
        if not request.args.get('locale'):
            if "lang" in session:
                lang = session["lang"]
            else:
                lang = "en"
        else:
            lang = request.args.get('locale')
        session["lang"] = lang
        return render_template("play.html", username=session["username"], userid=session["userid"], token=session["token"], lang=lang, SERVERIP=server_ip, ASSETSIP=assets_ip, langstrings=langstrings[lang])
    
    
    @app.route('/')
    def homepage():
        if maintenance["maintenance"]:
            return redirect('maintenance')
        # Setup session
        if not request.args.get('locale'):
            if "lang" in session:
                lang = session["lang"]
            else:
                lang = "en"
        else:
            lang = request.args.get('locale')
        session["lang"] = lang
        langUpper = lang.upper()
        return render_template("home.html", SERVERIP=server_ip, ASSETSIP=assets_ip, playerCount=userManager.get_player_count(), langstrings=langstrings[lang], lang=lang, langUpper=langUpper)
    
    
    @app.route('/login', methods=['POST'])
    def login():
        if maintenance["maintenance"]:
            return redirect('maintenance')
        msg = ''
        # Setup session
        if not request.args.get('locale'):
            if "lang" in session:
                lang = session["lang"]
            else:
                lang = "en"
        else:
            lang = request.args.get('locale')
        langUpper = lang.upper()
    
        if 'username' in request.form and 'password' in request.form:
            username = request.form['username']
            password = request.form['password']
            password = hashlib.sha512(password.encode('utf-8')).hexdigest()
    
            json_data = userManager.load_save_by_name(username)

            # In case there isn't an account with the selected username we return invalid credentials
            if json_data == -1:
                msg = 'bgc.error.login_invalidCredentials'
                return render_template("home.html", SERVERIP=server_ip, ASSETSIP=assets_ip, playerCount=userManager.get_player_count(), langstrings=langstrings[lang], lang=lang, langUpper=langUpper, msg=msg)

            if json_data["playerData"]["password"] == password:
                # Generate random token
                json_data["playerData"]["token"] = str(uuid.uuid1())
                user_id = json_data["playerData"]["account_id"]
                msg = 'Logged in successfully!'
                userManager.modify_save_by_id(user_id, json_data)
                session["username"] = username
                session["userid"] = user_id
                session["token"] = json_data["playerData"]["token"]
                return redirect('play')
            else:
                msg = 'bgc.error.login_invalidCredentials'
                return render_template("home.html", SERVERIP=server_ip, ASSETSIP=assets_ip, playerCount=userManager.get_player_count(), langstrings=langstrings[lang], lang=lang, langUpper=langUpper, msg=msg)
    
        else:
            return render_template("home.html", SERVERIP=server_ip, ASSETSIP=assets_ip, playerCount=userManager.get_player_count(), langstrings=langstrings[lang], lang=lang, langUpper=langUpper, msg='')
    
    
    @app.route('/register', methods=['POST'])
    def register():
        if maintenance["maintenance"]:
            return redirect('maintenance')
        msg = ''
        # Read form data
        username = request.form['RegUsername']
        password = request.form['RegPassword']
        password = hashlib.sha512(password.encode('utf-8')).hexdigest()
        email = request.form['RegEmail']
    
        # Setup session
        if not request.args.get('locale'):
            lang = "en"
        else:
            lang = request.args.get('locale')
        langUpper = lang.upper()
    
        # Check if input data is valid
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'bgc.error.email_invalidAddress'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'bgc.error.username_containsInvalidCharacters'
        elif not username:
            msg = 'bgc.error.username_notGiven'
        elif not password:
            msg = 'bgc.error.password_notGiven'
        elif len(username) < 4:
            msg = 'bgc.error.username_isTooShort'
        elif len(username) > 20:
            msg = 'bgc.error.username_isTooLong'
        # Disabled cuz of hash, needs to be checked on the site itself
        # elif len(password) < 4:
        #    msg = 'bgc.error.password_isTooShort'
        # elif len(password) > 45:
        #    msg = 'bgc.error.password_isTooLong'
        elif not email:
            msg = 'bgc.error.email_notGiven'
        else:
            # Check if account already exists
            if not userManager.user_name_exists(username):
                uid = random.randint(10000000, 99999999)
                # Just in case it might be a double user id
                while userManager.user_id_exists(uid):
                    uid = random.randint(10000000, 99999999)
    
                token = str(uuid.uuid1())
                userManager.create_new_account(uid,username,password,token)
                session["username"] = username
                session["userid"] = uid
                session["token"] = token
                userManager.add_to_player_count(1)
    
                return redirect('play')
            else:
                msg = 'bgc.error.account_exists'
        return render_template("home.html", SERVERIP=server_ip, ASSETSIP=assets_ip, playerCount=userManager.get_player_count(), langstrings=langstrings[lang], lang=lang, langUpper=langUpper, msg=msg)
    
    
    @app.route("/crossdomain.xml")
    def crossdomain():
        return send_from_directory(STUB_DIR, "crossdomain.xml")
    
    # Game static files
    @app.route("/assets/<path:path>")
    def static_assets_loader(path):
        return send_from_directory(ASSETS_DIR, path)
    
    
    @app.route("/templates/styles/<path:path>")
    def styles(path):
        return send_from_directory(STYLES_DIR, path)


    # Be sure to be logged in before using this
    @app.route("/set-maintenance/on")
    def setMaintenanceOn():
        if "userid" in session and session["userid"] in ADMINS:
            maintenance["maintenance"] = True
            maintenance["startTime"] = int(time.time())
            return "Success!"
        else:
            return "good try lmao"
    

    @app.route("/set-maintenance/off")
    def setMaintenanceOff():
        if "userid" in session and session["userid"] in ADMINS:
            maintenance["maintenance"] = False
            maintenance["startTime"] = 0
            return "Success!"
        else:
            return "good try lmao"


    @app.route("/maintenance/")
    def maintenanceWork():
        return render_template('maintenance.html') 


    @app.route("/error/")
    def error():
        if session["error_mode"] == "unimplemented":
            session["error_mode"] = "error"
            return render_template('unimplemented.html')
        elif session["error_mode"] == "maintenance":
            session["error_mode"] = "error"
            return render_template('maintenance.html')
        else:
            return render_template('error.html')
    
    
    @app.route("/logout/")
    def logout():
        # Setup session
        if not request.args.get('locale'):
            if "lang" in session:
                lang = session["lang"]
            else:
                lang = "en"
        else:
            lang = request.args.get('locale')
        session["lang"] = lang
        
        langUpper = lang.upper()
        return render_template('logout.html', lang=lang, langUpper=langUpper, langstrings=langstrings[lang], ASSETSIP=assets_ip, playerCount=userManager.get_player_count())
    
    @app.errorhandler(404)
    def page_not_found(e):
        return homepage()
    
    @app.errorhandler(413)
    def request_entity_too_large(e):
        return f"Flask caught 413, Content-Length={request.content_length}", 413
    
    # Handle all the game commands
    @app.route("/SkyApi.php", methods=['POST'])
    def handle_request():
        # Check for maintenance
        if maintenance["maintenance"]:
            session["error_mode"] = "maintenance"
            return "Maintenance going on, sorry not sorry :)"

        logging.debug(request.form)
    
        json_data = userManager.load_save_by_id(str(request.form["userId"]))
    
        if json_data["playerData"]["token"] == request.form["t"]:
            command_data = json.loads(request.form["d"])
            total_response = {"rpcResults": []}
            
            # Initialize batch state for this request
            global _command_batch_state
            _command_batch_state = {}
    
            # Check start level based on xp
            start_level = get_level_from_xp(
                json_data["playerData"]["xp"], init_data["playerData"]["xp_level_caps"])
    
            # Add this data to the Object, allowing for live updating in the game
            total_items_to_add_to_obj = []
            
            # Resolve command dependencies to prevent race conditions
            ordered_command_data = resolve_command_dependencies(command_data)
            
            for command in ordered_command_data:
                if command["m"] in available_commands:
                    logging.info(f"Command {command['m']} handled")

                    # Add current coins to request in order to simplify the GetAirCoins tasks
                    command["previous_air_coins"] = json_data["playerData"]["air_coins"]
    
                    # Check Lucky Luggage new spins
                    handle_lucky_luggage_live(command, request.form["userId"], json_data)
    
                    # Create command answer
                    rpcResult = {}
                    items_to_add_to_obj = []
                    handler = available_commands[command["m"]]
                    handler(command, request.form["userId"],
                            rpcResult, items_to_add_to_obj, json_data, init_data)
                    
                    if rpcResult["i"] == -1: # Command asked to disconnect user (likely due to possible cheat)
                        logging.warning(f"User with id {request.form['userId']} has been disconnected, possible cheat detected!")
                        return "Could not get Sky_Instance_Plane object with unique id 1435_12297741"
    
                    total_response["rpcResults"].append(rpcResult)
    
                    # Check goal completion
                    handle_goal(command, request.form["userId"], "main", items_to_add_to_obj, json_data, init_data)
                    handle_goal(command, request.form["userId"], "pilot", items_to_add_to_obj, json_data, init_data)
                    
                    total_items_to_add_to_obj += items_to_add_to_obj
    
                else:
                    logging.error(f"Command {command['m']} not implemented")
                    session["error_mode"] = "unimplemented"
                    return "Could not get Sky_Instance_Plane object with unique id 1435_12297741"
    
            # Check start level based on xp
            end_level = get_level_from_xp(
                json_data["playerData"]["xp"], init_data["playerData"]["xp_level_caps"])
    
            if start_level != end_level:  # Check level-up
                for i in range(end_level - start_level):
                    json_data["playerData"]["air_coins"] += 850
                    json_data["playerData"]["air_cash"] += 2  # YAY WE CAN BUY 0.2 HANGAR SLOTS!!!

            # Create command object
            obj = {}
            handle_addObj(
                command, request.form["userId"], obj, total_items_to_add_to_obj, json_data, init_data, obj_data)
            total_response["obj"] = obj
    
            userManager.modify_save_by_id(str(request.form["userId"]), json_data)
            return total_response
        else:
            logging.critical(f"Security alert: User {request.form['userId']} attempted to use an invalid token!")
            return "token_error"

    logging.info(f"Starting server on {host}:{port} (Debug mode: {'On' if configHandler.get_flask_debug() else 'Off'})")
    app.secret_key = 'SECRET_KEY'

    # Increase limits so we avoid 413 errors
    Request.max_form_parts = 50000
    MEGABYTE = (2 ** 10) ** 2
    app.config['MAX_CONTENT_LENGTH'] = None
    app.config['MAX_FORM_MEMORY_SIZE'] = 50 * MEGABYTE

    # Development environment, this won't run in production with a proper web server like nginx or apache
    if __name__ == "__main__":
        app.run(host=host, port=port, debug=configHandler.get_flask_debug())

# Start the server
main()