import re

BLACKLIST = set()

def load_profanity_list():
    global BLACKLIST
    try:
        with open("data/blocked_words.txt", "r") as f:
            BLACKLIST = {word.strip().lower() for word in f.readlines()}
    except FileNotFoundError:
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

