from pathlib import Path
from typing import Dict, List, Any

ROOT_DIR = Path(__file__).parent.resolve()

class ServerState:
    def __init__(self):
        self.init_data: Dict[str, Any] = {}
        self.obj_data: Dict[str, Any] = {}
        self.admins: List[int] = []
        self.server_ip: str = ""

        self.data_path = ROOT_DIR / "data"
        self.template_path = ROOT_DIR / "templates"

state = ServerState()