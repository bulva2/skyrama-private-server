import os
import sys

# Static asset roots.
#
# These are resolved against the project root rather than the process working
# directory. With the previous "." base, `uvicorn server:app` or `gunicorn`
# started from anywhere except the repo root made StaticFiles(directory=...)
# raise at import time, and Jinja2Templates silently found no templates.
# When frozen by PyInstaller the data lives in the _MEIPASS temp dir instead.
if getattr(sys, "frozen", False):
    BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ASSETS_DIR = os.path.join(BASE_DIR, "assets")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STUB_DIR = os.path.join(BASE_DIR, "stub")
STYLES_DIR = os.path.join(BASE_DIR, "templates", "styles")
