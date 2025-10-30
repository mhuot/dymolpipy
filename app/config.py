import json
import os
import platform
import secrets
from typing import Any, Dict

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
CONFIG_PATH = os.path.join(ROOT_DIR, "config.json")
TOKEN_PATH = os.path.join(ROOT_DIR, ".label_token")
OUTPUT_DIR = os.path.join(ROOT_DIR, "output")

DEFAULT_CONFIG: Dict[str, Any] = {
    "printer_name": "DYMO LabelWriter 450",
    "dpi": 300,
    "media": None,  # set to a CUPS media option string if known, else None
    "size_presets": {
        "large": 300,
        "small": 200
    },
    "canvas": {
        "square": 1050,
        "label_height": 338
    },
    "font_paths": {
        "Darwin": "/System/Library/Fonts/Supplemental/Tahoma.ttf",
        "Linux": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
    }
}


def load_config() -> Dict[str, Any]:
    if not os.path.exists(CONFIG_PATH):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    with open(CONFIG_PATH, "r") as f:
        data = json.load(f)
    # merge with defaults to ensure new keys exist
    merged = DEFAULT_CONFIG.copy()
    for k, v in DEFAULT_CONFIG.items():
        if isinstance(v, dict):
            mv = data.get(k, {})
            nv = v.copy()
            nv.update(mv)
            merged[k] = nv
        else:
            merged[k] = data.get(k, v)
    return merged


def save_config(cfg: Dict[str, Any]) -> None:
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)


def ensure_output_dir() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def get_platform_font_path(cfg: Dict[str, Any]) -> str:
    sysname = platform.system()
    paths = cfg.get("font_paths", {})
    return paths.get(sysname) or paths.get("Linux") or paths.get("Darwin") or ""


def load_or_create_token() -> str:
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "r") as f:
            return f.read().strip()
    token = secrets.token_hex(16)
    with open(TOKEN_PATH, "w") as f:
        f.write(token)
    try:
        os.chmod(TOKEN_PATH, 0o600)
    except Exception:
        pass
    return token
