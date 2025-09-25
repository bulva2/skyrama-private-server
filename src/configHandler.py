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
       
        record.levelname = f"{color}[ {levelname} ]{Style.RESET_ALL}"
        return super().format(record)

def setup_logging():
    config = get_config()

    # Initialize Colorama
    init(autoreset=True)

    log_level_str = config.get("Debugging", "logging_level", fallback="INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    
    # Reset all loggers to prevent duplication & other issues
    logging.root.handlers = []
    
    # Create a colored formatter
    formatter = ColoredFormatter(fmt='%(levelname)s %(asctime)s: %(message)s', datefmt='%H:%M:%S')
    
    # Configure the root logger
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    
    # Set up the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(handler)

def get_flask_debug():
    config = get_config()
    return config.getboolean("Debugging", "flask_debug", fallback=True)
