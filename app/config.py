import json
import os
import platform
import secrets
import subprocess
import re
from typing import Any, Dict, Optional

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


def detect_media_for_30252(printer_name: Optional[str] = None) -> Optional[str]:
    """Best-effort detection of CUPS media/page size value for DYMO 30252 labels.
    Parses lpoptions -l output and searches for tokens containing 30252.
    Returns the media token (string) or None if not found.
    """
    cfg = load_config()
    printer = printer_name or cfg.get("printer_name")
    if not printer:
        return None
    try:
        proc = subprocess.run(
            ["lpoptions", "-p", printer, "-l"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except Exception:
        return None
    out = proc.stdout or ""
    candidates: list[str] = []
    for line in out.splitlines():
        if re.search(r"(?i)media|pagesize", line):
            # Format: OptionName/Label: *val1 val2 val3
            parts = line.split(":", 1)
            if len(parts) != 2:
                continue
            values = parts[1].strip()
            # values like: *LW_30252Address LW_30321 LW_99012
            tokens = values.replace("*", "").split()
            for t in tokens:
                if re.search(r"30252", t, re.IGNORECASE):
                    candidates.append(t)
            # fallback: anything with 'Address'
            for t in tokens:
                if not candidates and re.search(r"address", t, re.IGNORECASE):
                    candidates.append(t)
    return candidates[0] if candidates else None


def ensure_media_configured() -> Optional[str]:
    cfg = load_config()
    if cfg.get("media"):
        return cfg["media"]
    media = detect_media_for_30252(cfg.get("printer_name"))
    if media:
        cfg["media"] = media
        save_config(cfg)
        return media
    return None
