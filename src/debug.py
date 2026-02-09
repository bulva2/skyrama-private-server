import json
import requests
import logging
from src.config_handler import get_config

_CONFIG = get_config()
_ERROR_WEBHOOK_URL = _CONFIG.get("Webhooks", "error_webhook", fallback="")

def report_issue(severity: str, msg: str):
    severity = severity.lower()

    if severity == "debug":
        logging.debug(msg)
    elif severity == "info":
        logging.info(msg)
    elif severity == "warning":
        logging.warning(msg)
    elif severity == "error":
        logging.error(msg)
    elif severity == "critical":
        logging.critical(msg)
    else:
        logging.warning(msg)

    if severity in ["warning", "error", "critical"] and _ERROR_WEBHOOK_URL:
        send_short_webhook(f"**{severity.upper()}**: {msg}")

def send_short_webhook(content: str, url: str = _ERROR_WEBHOOK_URL) -> None:
    if url is None or url.strip() == "":
        logging.warning("No valid webhook URL provided in the config file. Skipping short webhook.")
        return

    data = {
        "content": content,
        "username": "Skyrama Private Server - Problem Reporter",
    }

    try:
        result = requests.post(url, json=data, timeout=5)
        result.raise_for_status()
    except requests.exceptions.RequestException as err:
        logging.error(f"Error sending short webhook: {err}")

# https://discord.com/developers/docs/resources/message#embed-object
def send_trackflash_webhook(json_data: dict, user_id: int, request_payload: dict, url: str = _ERROR_WEBHOOK_URL, additional_data: dict = None) -> None:
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

def user_registered_webhook(uid: int, username: str) -> None:
    url = _CONFIG.get("Webhooks", "registration_webhook", fallback=None)

    if url is None or url.strip() == "":
        logging.warning("No valid registration webhook URL provided in the config file. Skipping registration webhook.")
        return
    
    data = {
        "username": "New Airport Manager",
    }

    data["embeds"] = [
        {
            "title": f"New player took control of an airport!",
            "description": f"Welcome **{username}** (ID: {uid}) to the server!",
            "color": 3145631,
            "footer": {
                "text": "Skyrama Private Server - https://github.com/Michielvde1253/skyrama-private-server"
            }
        }
    ]

    try:
        result = requests.post(url, json=data, timeout=5)
        result.raise_for_status()
    except requests.exceptions.RequestException as err:
        logging.error(f"Error sending registration webhook: {err}")


