import sys
import os

# Bundled data (extracted to a temp dir)
# Maybe for future use, else remove this in upcoming updates
TMP_BUNDLED_DIR = getattr(sys, '_MEIPASS', ".") if getattr(sys, 'frozen', False) else "."

ASSETS_DIR = os.path.join(TMP_BUNDLED_DIR, "assets")
TEMPLATES_DIR = os.path.join(TMP_BUNDLED_DIR, "templates")
STUB_DIR = os.path.join(TMP_BUNDLED_DIR, "stub")
STYLES_DIR = os.path.join(TMP_BUNDLED_DIR, "templates", "styles")

