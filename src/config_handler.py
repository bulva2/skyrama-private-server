from dotenv import load_dotenv
from pathlib import Path
from colorama import init, Fore, Style
import configparser
import logging
import orjson
import os
import sys

# Singleton, so we don't load the config multiple times
_config = None

# Mby move this to startup.py
def run():
    os.system('cls' if os.name == 'nt' else 'clear')
    setup_logging()

def load_config(file_path: Path) -> configparser.ConfigParser:
    global _config
    if _config is None:
        load_dotenv()

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

_RECORD_KEYS = set(logging.LogRecord("", 0, "", 0, "", None, None).__dict__) | {"message", "asctime", "taskName"}

class JsonFormatter(logging.Formatter):
    """One JSON object per line, with any `extra` fields included."""

    def format(self, record: logging.LogRecord) -> str:
        out = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname.lower(),
            "logger": record.name,
            "msg": record.getMessage(),
        }
        for key, value in record.__dict__.items():
            if key not in _RECORD_KEYS and not key.startswith("_"):
                out[key] = value
        if record.exc_info:
            out["exception"] = self.formatException(record.exc_info)
        return orjson.dumps(out, default=str).decode()

QUIET_ACCESS_PATHS = ("/chat/messages", "/crossdomain.xml")

class QuietPollingFilter(logging.Filter):
    """Drop successful access-log lines for polled endpoints, keep failures."""

    def filter(self, record: logging.LogRecord) -> bool:
        args = record.args
        if not isinstance(args, tuple) or len(args) < 5:
            return True

        path, status = args[2], args[4]
        if not isinstance(path, str):
            return True

        try:
            status = int(status)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return True

        if status >= 400:
            return True

        return not any(path.startswith(p) for p in QUIET_ACCESS_PATHS)

def setup_logging():
    config = get_config()

    # Initialize Colorama
    init(autoreset=True)

    log_level_str = config.get("Debugging", "logging_level", fallback="INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    
    logging.root.handlers = []
    
    # Create a colored formatter
    if sys.stderr.isatty():
        formatter = ColoredFormatter(fmt='%(levelname)s %(asctime)s: %(message)s', datefmt='%H:%M:%S')
    else:
        formatter = JsonFormatter()
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

    logging.getLogger("uvicorn.access").addFilter(QuietPollingFilter())


