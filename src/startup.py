import os
import orjson
import logging
import pyfiglet
import hashlib
import dotenv

from contextlib import asynccontextmanager
from fastapi import FastAPI

import src.user_manager as user_manager
import src.config_handler as config_handler
from src.database import init_database
from src.cache_manager import initialize_cache
from src.chat_moderation import load_profanity_list
from state import state

config = config_handler.get_config()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(pyfiglet.figlet_format("Skyrama Private Server", font="slant", width=200))
    logging.info("Loading the server, please wait..")
    
    dotenv.load_dotenv()
    conn_str = os.environ.get("DB_CONNECTION_STRING", "")
    if not conn_str:
        logging.critical("DB_CONNECTION_STRING not found in .env file. Make sure that you renamed .env-example to .env and that you set the DB_CONNECTION_STRING variable to your connection string!")
        exit(2)

    db_manager = init_database(conn_str)
    db_manager.create_tables()
    
    # Load Init Data
    logging.info("Loading init data...")
    
    with open(state.data_path / "global_init_data.json.def", "rb") as f:
        state.init_data = orjson.loads(f.read())

    # Load global cache
    initialize_cache(state.init_data)

    with open(state.data_path / "obj.json.def", "rb") as f:
        state.obj_data = orjson.loads(f.read())
        
    user_manager.save_players_by_location_id()

    langstrings = {}
    
    # Load language files
    for filename in os.listdir(state.root_path / "templates" / "languages"):
        with open(state.root_path / "templates" / "languages" / filename, "rb") as f:
            langstrings[filename[0:-5]] = orjson.loads(f.read())
        
    state.langstrings = langstrings
    
    # Load profanity list
    load_profanity_list()
    
    # URL setup
    #
    # This becomes SERVERIP in the templates, which the Flash client uses as an
    # absolute origin for /SkyApi.php and for the login/register form actions.
    # It therefore has to be the address the *player's browser* can reach, which
    # is not the address the server binds to when it sits behind a reverse proxy
    # (Docker: bind 0.0.0.0:3800, but players connect to nginx on :80/:443).
    # PUBLIC_URL wins when set; otherwise fall back to host:port from config.cfg.
    public_url = os.environ.get("PUBLIC_URL", "").strip().rstrip("/")
    if public_url:
        state.server_ip = public_url
    else:
        host = config.get("ServerSettings", "host", fallback="127.0.0.1").replace("http://", "").replace("https://", "")
        port = int(config.get("ServerSettings", "port", fallback="3800"))
        use_https = config.getboolean("ServerSettings", "use_https", fallback=False)
        protocol = "https" if use_https else "http"
        state.server_ip = f"{protocol}://{host}:{port}"

    swf_path = state.root_path / "assets" / "airville.swf"
    if swf_path.exists():
        with open(swf_path, "rb") as f:
            state.airville_cv = hashlib.md5(f.read()).hexdigest()
    else:
        state.airville_cv = "devcv"

    logging.info(f"Server initialized on {state.server_ip}")
    yield
    
    # Shutdown logic
    logging.info("Server is shutting down, have a great day! ^^")