import logging
import re

from state import state

BLACKLIST = set()

def load_profanity_list():
    global BLACKLIST
    # Resolved from the project root, not the current working directory - a
    # relative "data/..." path silently disabled the whole filter whenever the
    # server was started from anywhere other than the repo root.
    path = state.data_path / "blocked_words.txt"
    try:
        with open(path, "r", encoding="utf-8") as f:
            BLACKLIST = {word.strip().lower() for word in f if word.strip()}
    except FileNotFoundError:
        logging.warning(f"Profanity list not found at {path}, chat filtering is disabled.")
        BLACKLIST = set()

def moderate_msg(text: str) -> str:
    """Moderate message: remove links, censor profanity"""
    # Remove all links first
    text = _remove_links(text)
    
    # Then censor profanity
    words = text.lower().split()
    if any(word in BLACKLIST for word in words):
        text = _censor_message(text)
    
    return text

def _censor_message(text: str) -> str:
    """Replace blacklisted words with asterisks"""
    words = text.lower().split()
    censored = []
    for word in words:
        if word in BLACKLIST:
            censored.append("*" * len(word))
        else:
            censored.append(word)
    return " ".join(censored)

def _remove_links(text: str) -> str:
    """Remove URLs, domain references, Discord invites, and similar patterns"""
    # Match:
    # - http/https URLs: https://example.com
    # - Domain patterns: seznam.cz, discord.gg, example.com
    # - Discord invites: discord gg, discord.gg/xxxxx
    # - IP patterns: 192.168.1.1
    patterns = [
        r"https?://\S+",           # http/https URLs
        r"(?:www\.)?[\w-]+\.\w{2,}(?:/\S*)?",  # Domain patterns (seznam.cz, example.com)
        r"discord\.gg/\S+",         # discord.gg/invite
        r"discord\s+gg",            # "discord gg"
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"  # IP addresses
    ]
    
    url_pattern = re.compile("|".join(f"({p})" for p in patterns), re.IGNORECASE)
    return url_pattern.sub(lambda m: "*" * len(m.group(0)), text)

