import logging

_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}

_RESERVED = set(logging.LogRecord("", 0, "", 0, "", None, None).__dict__) | {"message", "asctime"}

def report_issue(severity: str, msg: str, **fields) -> None:
    """Log an issue. Extra keyword args become queryable fields in Loki."""
    extra = {k: v for k, v in fields.items() if k not in _RESERVED}
    logging.log(_LEVELS.get(severity.lower(), logging.WARNING), msg, extra=extra)
