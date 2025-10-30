import json
import os
import time
import subprocess
from typing import Dict, List, Tuple, Optional

from PIL import Image, ImageDraw, ImageFont

from app.config import load_config, ensure_output_dir, get_platform_font_path, OUTPUT_DIR

LAST_JOB_PATH = os.path.join(OUTPUT_DIR, "last_job.json")


def _measure_text(text: str, font: ImageFont.FreeTypeFont) -> Tuple[int, int]:
    # Pillow 6.x supports getsize; newer has getbbox/getlength. Use getsize for compatibility.
    return font.getsize(text)


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int, max_lines: int = 2) -> List[str]:
    # Greedy char-based wrap to avoid word-measure complexity on older Pillow
    lines: List[str] = []
    current = ""
    for ch in text:
        w, _ = _measure_text(current + ch, font)
        if w <= max_width:
            current += ch
        else:
            lines.append(current)
            current = ch
            if len(lines) >= max_lines:
                break
    if len(lines) < max_lines and current:
        lines.append(current)
    # Ellipsis if overflow
    if len(lines) > max_lines:
        lines = lines[:max_lines]
    # If original text didn't fit in allocated lines, ensure last line ends with ellipsis within width
    joined = "".join(lines)
    if len(joined) < len(text):
        last = lines[-1]
        # trim and add ellipsis
        while last and _measure_text(last + "…", font)[0] > max_width:
            last = last[:-1]
        lines[-1] = (last + "…") if last else "…"
    return lines


def render_label(text: str, size_preset: str = "large") -> Tuple[str, Dict]:
    cfg = load_config()
    ensure_output_dir()

    square = int(cfg["canvas"]["square"])  # e.g., 1050
    label_h = int(cfg["canvas"]["label_height"])  # e.g., 338
    max_width = square  # before rotate; we write as if wide, then rotate and crop

    font_size = int(cfg["size_presets"].get(size_preset, cfg["size_presets"]["large"]))
    font_path = get_platform_font_path(cfg)
    try:
        font = ImageFont.truetype(font_path, font_size)
    except Exception:
        font = ImageFont.load_default()

    # Wrap text
    lines = wrap_text(text, font, max_width=max_width, max_lines=2)

    # Create square canvas, draw, rotate, and crop to label height
    img = Image.new('1', (square, square), 255)
    draw = ImageDraw.Draw(img)

    # Compute vertical placement: top-left baseline, simple stacked lines
    y = 0
    line_height = _measure_text("Ag", font)[1]
    for ln in lines:
        draw.text((0, y), ln, font=font)
        y += line_height

    rotated = img.rotate(270)
    cropped = rotated.crop((square - label_h, 0, square, square))

    ts = int(time.time())
    img_path = os.path.join(OUTPUT_DIR, f"label_{ts}.png")
    cropped.save(img_path)

    meta = {
        "text": text,
        "lines": lines,
        "size": size_preset,
        "image_path": img_path,
        "timestamp": ts
    }
    with open(LAST_JOB_PATH, "w") as f:
        json.dump(meta, f, indent=2)

    return img_path, meta


def _run_lpr(image_path: str, copies: int, media: Optional[str]) -> None:
    cfg = load_config()
    printer = cfg.get("printer_name")
    dpi = cfg.get("dpi", 300)

    cmd: List[str] = [
        "lpr",
        "-P", printer,
        "-o", f"ppi={dpi}",
    ]
    if media:
        cmd += ["-o", f"media={media}"]
    if copies and copies > 1:
        cmd += ["-#", str(copies)]
    cmd.append(image_path)

    # Use subprocess to capture errors
    subprocess.run(cmd, check=True)


def print_label(image_path: str, copies: int = 1, media: Optional[str] = None) -> None:
    _run_lpr(image_path, copies=copies, media=media)


def load_last_job() -> Optional[Dict]:
    if not os.path.exists(LAST_JOB_PATH):
        return None
    with open(LAST_JOB_PATH, "r") as f:
        return json.load(f)
