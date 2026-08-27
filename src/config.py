# src/config.py
import json

DEFAULT_CONFIG = {
    "language": "zh",
    "gui_default": False,
    "log_level": "info",
    "prefix_style": {
        "warning": "[WARNING] ",
        "error": "[ERROR] ",
        "success": "[SUCCESS] ",
        "debug": "[DEBUG] "
    }
}

_config = DEFAULT_CONFIG.copy()

def load_config(path="config.json"):
    global _config
    try:
        with open(path, 'r', encoding='utf-8') as f:
            _config.update(json.load(f))
    except FileNotFoundError:
        pass
    return _config

def get_config():
    return _config