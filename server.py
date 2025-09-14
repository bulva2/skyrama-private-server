if __name__ == '__main__':
      
    #######################
    # Import server stuff #
    #######################
    from commands import *
    from bundle import TEMPLATES_DIR, STUB_DIR, STYLES_DIR, ASSETS_DIR
    import userManager
    
    ##########################
    # Import 3rd party stuff #
    ##########################
    print(" [+] Importing libraries...")
    from flask import Flask, render_template, send_from_directory, request, redirect, session, url_for
    import re
    import random
    import uuid
    import hashlib
    from pathlib import Path
    import json
    import os

def main():
    print(" [+] Loading server...")
    
    for module in os.listdir(os.path.join(os.path.dirname(__file__), "commands")):
        if module == '__init__.py' or module[-3:] != '.py':
            continue
        __import__(module[:-3], locals(), globals())
    del module
    
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
        "map_extensions.buy": handle_mapExpansionsBuy
    }
    
    #########################
    # Load global game data #
    #########################
    print(" [+] Loading init data...")
    
    p = Path(__file__).parents[0]
    
    f = open(os.path.join(p, "data", "global_init_data.json.def"), "r", encoding="utf-8")
    init_data = json.loads(str(f.read()))
    f.close()
    
    f = open(os.path.join(p, "data", "obj.json.def"), "r", encoding="utf-8")
    obj_data = json.loads(str(f.read()))
    f.close()
    
    ################################
    # Sort accounts by location id #
    ################################
    
    userManager.save_players_by_location_id()
    
    ##########################
    # Load site translations #
    ##########################
    langstrings = {}
    for filename in os.listdir(os.path.join("templates", "languages")):
        f = open(os.path.join("templates", "languages",
                 filename), "r", encoding="utf-8")
        langstrings[filename[0:-5]] = json.loads(str(f.read()))
        f.close()
    
    ########################################
    # Get total amount of created accounts #
    ########################################
    
    '''
    # GLITCH
    host = '0.0.0.0'
    port = 8080
    server_ip = "http://skyrama.glitch.me"
    assets_ip = "https://cdn.jsdelivr.net/gh/Mima2370/skyrama-private-server/"
    '''
    
    # LOCAL
    host = '127.0.0.1'
    port = 5050
    server_ip = "http://" + str(host) + ":" + str(port)
    assets_ip = "http://" + str(host) + ":" + str(port)
    
    app = Flask(__name__, template_folder=TEMPLATES_DIR)
    
    print(" [+] Configuring server routes...")
    
    ##########
    # ROUTES #
    ##########
    
    @app.route("/play")
    def play():
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
    
    ###############
    # GAME STATIC #
    ###############
    
    @app.route("/assets/<path:path>")
    def static_assets_loader(path):
        return send_from_directory(ASSETS_DIR, path)
    
    
    @app.route("/templates/styles/<path:path>")
    def styles(path):
        return send_from_directory(STYLES_DIR, path)
    
    
    @app.route("/error/")
    def error():
        if session["error_mode"] == "unimplemented":
            session["error_mode"] = "error"
            return render_template('unimplemented.html')
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
    
    ################
    # GAME DYNAMIC #
    ################
    
    def get_level_from_xp(xp, level_caps):
        level = 100  # Handle the edge case when you're at the last level
        j = 0
        for i in level_caps:
            if int(i) > xp:
                level = j
                break
            j = j + 1
        return level
    
    
    @app.route("/SkyApi.php", methods=['POST'])
    def handle_request():
        print(request.form)
    
        json_data = userManager.load_save_by_id(str(request.form["userId"]))
    
        if json_data["playerData"]["token"] == request.form["t"]:
            command_data = json.loads(request.form["d"])
            total_response = {"rpcResults": []}
    
            # Check start level based on xp
            start_level = get_level_from_xp(
                json_data["playerData"]["xp"], init_data["playerData"]["xp_level_caps"])
    
            # Add this data to the Object, allowing for live updating in the game
            total_items_to_add_to_obj = []
            for command in command_data:
                if command["m"] in available_commands:
                    print("Command " + command["m"] + " handled")
    
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
                        print(f"User with id {request.form['userId']} has been disconnected")
                        return "Could not get Sky_Instance_Plane object with unique id 1435_12297741"
    
                    total_response["rpcResults"].append(rpcResult)
                    total_items_to_add_to_obj = total_items_to_add_to_obj + items_to_add_to_obj
    
                    # Check goal completion
                    handle_goal(command, request.form["userId"], "main", items_to_add_to_obj, json_data, init_data)
                    handle_goal(command, request.form["userId"], "pilot", items_to_add_to_obj, json_data, init_data)
    
                else:
                    print("Command " + command["m"] + " not handled")
                    session["error_mode"] = "unimplemented"
                    return "Could not get Sky_Instance_Plane object with unique id 1435_12297741"
    
            # Check start level based on xp
            end_level = get_level_from_xp(
                json_data["playerData"]["xp"], init_data["playerData"]["xp_level_caps"])
    
            if start_level != end_level:  # Check level-up
                for i in range(end_level - start_level):
                    json_data["playerData"]["air_coins"] = int(
                        json_data["playerData"]["air_coins"]) + 850
                    json_data["playerData"]["air_cash"] = int(
                        json_data["playerData"]["air_cash"]) + 2  # YAY WE CAN BUY 0.2 HANGAR SLOTS!!!
    
            # Create command object
            obj = {}
            print(total_items_to_add_to_obj)
            handle_addObj(
                command, request.form["userId"], obj, total_items_to_add_to_obj, json_data, init_data, obj_data)
            total_response["obj"] = obj
    
            userManager.modify_save_by_id(str(request.form["userId"]), json_data)
    
            return total_response
        else:
            print("User " + str(request.form["userId"]
                                ) + " has used an invalid token.")
            return "token_error"
    
    
    ########
    # MAIN #
    ########
    
    print(" [+] Running server...")

    app.secret_key = 'SECRET_KEY'
    app.run(host=host, port=port, debug=True)

if __name__ == '__main__':
    main()
