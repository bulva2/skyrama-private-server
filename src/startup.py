import os
import orjson
import logging
import pyfiglet

from contextlib import asynccontextmanager
from fastapi import FastAPI

import src.user_manager as user_manager
import src.config_handler as config_handler
from src.database import init_database
from src.cache_manager import initialize_cache
from state import state

config = config_handler.get_config()

@asynccontextmanager
async def lifespan(app: FastAPI):
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