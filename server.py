from commands import *
from bundle import TEMPLATES_DIR, STUB_DIR, STYLES_DIR, ASSETS_DIR
from flask import Flask, render_template, send_from_directory, request, redirect, session, url_for
import re
import random
import uuid
import time
import hashlib
from pathlib import Path
import json
import os
print(" [+] Loading basics...")
if os.name == 'nt':
    os.system("color")

os.system("title Skyrama Server")

print(" [+] Loading server...")

for module in os.listdir(os.path.join(os.path.dirname(__file__), "commands")):
    if module == '__init__.py' or module[-3:] != '.py':
        continue
    __import__(module[:-3], locals(), globals())
del module


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
    "general.getBuddyInitState": handle_getBuddyInitState
}

print(" [+] Loading init data...")

p = Path(__file__).parents[0]

f = open(os.path.join(p, "data", "global_init_data.json"), "r")
init_data = json.loads(str(f.read()))
f.close()

f = open(os.path.join(p, "data", "obj.json"), "r")
obj_data = json.loads(str(f.read()))
f.close()

# GLITCH
# host = '0.0.0.0'
# port = 8080
# server_ip = "http://skyrama.glitch.me"
# assets_ip = "https://cdn.jsdelivr.net/gh/Mima2370/skyrama-private-server/"

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
    if "username" not in session:
        return redirect("/")
    session["error_mode"] = "error"
    if not request.args.get('locale'):
        if "lang" in session:
            lang = session["lang"]
        else:
            lang = "en"
    else:
        lang = request.args.get('locale')
    session["lang"] = lang
    f = open(os.path.join("templates", "languages",
             lang + ".json"), "r", encoding="utf-8")
    langstrings = json.loads(str(f.read()))
    f.close()
    return render_template("play.html", username=session["username"], userid=session["userid"], token=session["token"], lang=lang, SERVERIP=server_ip, ASSETSIP=assets_ip, langstrings=langstrings)


@app.route('/')
def homepage():
    # Get total amount of created accounts
    playerCount = len(os.listdir("data")) - 4
    if not request.args.get('locale'):
        if "lang" in session:
            lang = session["lang"]
        else:
            lang = "en"
    else:
        lang = request.args.get('locale')
    session["lang"] = lang
    langUpper = lang.upper()
    f = open(os.path.join("templates", "languages",
             lang + ".json"), "r", encoding="utf-8")
    langstrings = json.loads(str(f.read()))
    f.close()
    return render_template("home.html", SERVERIP=server_ip, ASSETSIP=assets_ip, playerCount=playerCount, langstrings=langstrings, lang=lang, langUpper=langUpper)


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''

    # Get total amount of created accounts
    playerCount = len(os.listdir("data")) - 4
    if not request.args.get('locale'):
        if "lang" in session:
            lang = session["lang"]
        else:
            lang = "en"
    else:
        lang = request.args.get('locale')
    langUpper = lang.upper()
    f = open(os.path.join("templates", "languages", lang + ".json"), "r")
    langstrings = json.loads(str(f.read()))
    f.close()

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        password = hashlib.sha512(password.encode('utf-8')).hexdigest()
        for i in os.listdir("data"):
            if i[8:len(i)-5] == username:
                f = open(os.path.join("data", i), "r")
                json_data = json.loads(str(f.read()))
                f.close()
                if json_data["playerData"]["password"] == password:
                    json_data["playerData"]["token"] = str(uuid.uuid1())
                    msg = 'Logged in successfully!'
                    f = open(os.path.join("data", i), "w")
                    f.write(json.dumps(json_data))
                    f.close()

                    session["username"] = username
                    session["userid"] = json_data["playerData"]["account_id"]
                    session["token"] = json_data["playerData"]["token"]
                    return redirect('play')
                else:
                    msg = 'bgc.error.login_invalidCredentials'
                    return render_template("home.html", SERVERIP=server_ip, ASSETSIP=assets_ip, playerCount=playerCount, langstrings=langstrings, lang=lang, langUpper=langUpper, msg=msg)
        msg = 'bgc.error.login_invalidCredentials'
        return render_template("home.html", SERVERIP=server_ip, ASSETSIP=assets_ip, playerCount=playerCount, langstrings=langstrings, lang=lang, langUpper=langUpper, msg=msg)

    else:
        return render_template("home.html", SERVERIP=server_ip, ASSETSIP=assets_ip, playerCount=playerCount, langstrings=langstrings, lang=lang, langUpper=langUpper, msg='')


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        username = request.form['RegUsername']
        password = request.form['RegPassword']
        password = hashlib.sha512(password.encode('utf-8')).hexdigest()
        email = request.form['RegEmail']

        # Get total amount of created accounts
        playerCount = len(os.listdir("data")) - 4
        if not request.args.get('locale'):
            lang = "en"
        else:
            lang = request.args.get('locale')
        langUpper = lang.upper()
        f = open(os.path.join("templates", "languages", lang + ".json"), "r")
        langstrings = json.loads(str(f.read()))
        f.close()

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
            accountExists = 0
            files = os.listdir(os.path.join(Path(__file__).parents[0], "data"))
            for g in files:
                if g[8:len(g) - 5] == username:
                    accountExists = 1
                    break
            if accountExists == 0:
                uid = random.randint(10000000, 99999999)
                n = open(os.path.join("data", "new_player.json"), "r")
                json_data = json.loads(str(n.read()))
                f = open(os.path.join("data", str(uid) +
                         str(username) + ".json"), "w+")
                json_data["playerData"]["account_id"] = uid
                json_data["playerData"]["user_name"] = username
                json_data["playerData"]["password"] = password

                # Change user-id everywhere [WHY :-( ]
                json_data["goals"]["player_id"] = uid
                json_data["backgrounds"][0]["player_id"] = uid
                json_data["planes"][0]["to_player_id"] = uid
                json_data["runways"][0]["player_id"] = uid
                json_data["hangars"][0]["player_id"] = uid
                # json_data["bays"][0]["player_id"] = uid
                j = 0
                for i in json_data["landsideBuildings"]:
                    json_data["landsideBuildings"][j]["player_id"] = uid
                    j = j + 1
                json_data["accountData"]["id"] = uid
                json_data["accountData"]["user_name"] = username

                json_data["expeditionstatus"]["player_id"] = uid

                json_data["playerData"]["token"] = str(uuid.uuid1())

                f.write(json.dumps(json_data))
                f.close()

                session["username"] = username
                session["userid"] = json_data["playerData"]["account_id"]
                session["token"] = json_data["playerData"]["token"]
                return redirect('play')
            else:
                msg = 'bgc.error.account_exists'
    return render_template("home.html", SERVERIP=server_ip, ASSETSIP=assets_ip, playerCount=playerCount, langstrings=langstrings, lang=lang, langUpper=langUpper, msg=msg)


@app.route("/crossdomain.xml")
def crossdomain():
    return send_from_directory(STUB_DIR, "crossdomain.xml")

# GAME STATIC


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
    return render_template('logout.html')

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
    for file in os.listdir(os.path.join(p, "data")):
        if file[0:8] == str(request.form["userId"]):
            player_file = file
            break

    f = open(os.path.join(p, "data", player_file), "r")
    json_data = json.loads(str(f.read()))
    f.close()   

    if json_data["playerData"]["token"] == request.form["t"]:
        command_data = json.loads(request.form["d"])
        total_response = {"rpcResults": []}

        # Check start level based on xp
        start_level = get_level_from_xp(
            json_data["playerData"]["xp"], json_data["playerData"]["xp_level_caps"])

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
            json_data["playerData"]["xp"], json_data["playerData"]["xp_level_caps"])

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

        f = open(os.path.join(p, "data", player_file), "w")
        f.write(json.dumps(json_data))
        f.close()

        return total_response
    else:
        print("User " + str(request.form["userId"]
                            ) + " has used an invalid token.")
        return "token_error"


########
# MAIN #
########

print(" [+] Running server...")

if __name__ == '__main__':
    app.secret_key = 'SECRET_KEY'
    app.run(host=host, port=port, debug=True)
