import os
from typing import Dict, Any

import toml

def load_config(PROJECT_DIR=None) -> Dict[str, Any]:
    if not PROJECT_DIR:
        PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(PROJECT_DIR, "config.toml")
    with open(filepath, "r") as f:
        return toml.load(f)
