import os

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.cors import CORSMiddleware

import src.config_handler as config_handler

from bundle import STYLES_DIR, ASSETS_DIR
from routers import game_api, web, management, public_api
from src.startup import lifespan

config_handler.run()
config = config_handler.get_config()

app = FastAPI(lifespan=lifespan, default_response_class=ORJSONResponse)

app.add_middleware(
    SessionMiddleware, 
    secret_key=os.environ.get("SESSION_SECRET", "Epic-Secret-Key-Change-This")
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")
app.mount("/templates/styles", StaticFiles(directory=STYLES_DIR), name="styles")

app.include_router(game_api.router)
app.include_router(web.router)
app.include_router(management.router)
app.include_router(public_api.router)
     
if __name__ == "__main__":
    import uvicorn
    host = config.get("ServerSettings", "host", fallback="127.0.0.1")
    port = int(config.get("ServerSettings", "port", fallback="3800"))
    uvicorn.run("server:app", host=host, port=port, reload=True)
