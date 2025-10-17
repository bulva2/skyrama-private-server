import json
import time
import requests
import logging
from pathlib import Path
from src.configHandler import get_config

_FLASH_ERRORS_PATH = Path(__file__).parents[1] / "flasherrors.json"
_CONFIG = get_config()
_ERROR_WEBHOOK_URL = _CONFIG.get("Webhooks", "error_webhook", fallback=None)

def save_error(user_id: int, request_payload: dict) -> None:
    if _FLASH_ERRORS_PATH.exists():
        try:
            with _FLASH_ERRORS_PATH.open("r", encoding="utf-8") as src:
                existing = json.load(src)
            if not isinstance(existing, list):
                existing = []
        except (json.JSONDecodeError, OSError):
            existing = []
    else:
        existing = []

    entry = {
        "timestamp": int(time.time()),
        "userId": user_id,
        "payload": request_payload,
    }
    existing.append(entry)

    with _FLASH_ERRORS_PATH.open("w", encoding="utf-8") as dst:
        json.dump(existing, dst, ensure_ascii=False, indent=2)

# https://discord.com/developers/docs/resources/message#embed-object
def send_webhook(json_data: dict, user_id: int, request_payload: dict, url: str = _ERROR_WEBHOOK_URL, additional_data: dict = None) -> None:
    if url is None or url.strip() == "":
        logging.warning("No valid webhook URL provided in the config file. Skipping error webhook.")
        return

    data = {
        #"content" : "idk",
        "username" : "Skyrama Private Server - Error Logger",
    }

    fields = [
        {
            "name": "The failing payload:",
            "value": f"```json\n{json.dumps(request_payload, indent=2)}```",
            "inline": False,
        }
    ]

    if additional_data:
        try:
            pretty_additional = json.dumps(additional_data, indent=2)
        except (TypeError, ValueError):
            pretty_additional = str(additional_data)

        fields.append(
            {
                "name": "Additional information:",
                "value": f"```json\n{pretty_additional}```",
                "inline": False,
            }
        )

    data["embeds"] = [
        {
            "description" : "An error has occurred while handling the request!",
            "title" : f"Failing command: {request_payload.get("m", "Unspecified command")}",
            "footer": {
                "text": "Skyrama Private Server - https://github.com/Michielvde1253/skyrama-private-server",
                #"icon_url": "https://example.com/icon.png"
            },
            "color" : 16711680,
            "fields": fields,
            "author": {
                "name": f"{json_data['playerData']['user_name']} (ID: {user_id})",
                #"url": "https://example.com",
                #"icon_url": "https://example.com/icon.png"
            },
        }
    ]

    try:
        result = requests.post(url, json=data, timeout=5)
        result.raise_for_status()
    except requests.exceptions.RequestException as err:
        logging.error(f"Error sending webhook: {err}")


