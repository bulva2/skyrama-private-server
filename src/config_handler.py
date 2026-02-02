from pathlib import Path
from colorama import init, Fore, Style
import configparser
import logging
import os

# Singleton, so we don't load the config multiple times
_config = None

def run():
    os.system('cls' if os.name == 'nt' else 'clear')
    setup_logging()

def load_config(file_path: str) -> configparser.ConfigParser:
    global _config
    if _config is None:
        _config = configparser.ConfigParser()
        _config.read(file_path)
    return _config

def get_config():
    global _config
    if _config is None:
        return load_config(Path(__file__).parents[1] / "config.cfg")
    return _config


class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT
    }

    def format(self, record):
        levelname = record.levelname
        color = self.COLORS.get(levelname, Fore.WHITE)
       
        record.levelname = f"{color}{levelname}{Style.RESET_ALL}"
        return super().format(record)

def setup_logging():
    config = get_config()

    # Initialize Colorama
    init(autoreset=True)

    log_level_str = config.get("Debugging", "logging_level", fallback="INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    
    logging.root.handlers = []
    
    # Create a colored formatter
    formatter = ColoredFormatter(fmt='%(levelname)s %(asctime)s: %(message)s', datefmt='%H:%M:%S')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(handler)

    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("multipart").setLevel(logging.ERROR)
    logging.getLogger("multipart.multipart").setLevel(logging.ERROR)

    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access", "uvicorn.asgi"):
        ulogger = logging.getLogger(logger_name)
        ulogger.handlers = []
        ulogger.addHandler(handler)
        ulogger.propagate = False


