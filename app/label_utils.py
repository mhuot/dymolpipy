import json
import os
import time
import subprocess
from typing import Dict, List, Tuple, Optional

from PIL import Image, ImageDraw, ImageFont

from app.config import load_config, ensure_output_dir, get_platform_font_path, OUTPUT_DIR

LAST_JOB_PATH = os.path.join(OUTPUT_DIR, "last_job.json")


def _measure_text(text: str, font: ImageFont.FreeTypeFont) -> Tuple[int, int]:
    return font.getsize(text)


def _wrap_word_fallback(word: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
    # Break a too-long word into chunks that fit max_width
    parts: List[str] = []
    buf = ""
    for ch in word:
        if _measure_text(buf + ch, font)[0] <= max_width:
            buf += ch
        else:
            if buf:
                parts.append(buf)
            buf = ch
    if buf:
        parts.append(buf)
    return parts


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int, max_lines: int = 2) -> List[str]:
    words = text.split()
    if not words:
        return [""]
    lines: List[str] = []
    current = ""
    for w in words:
        candidate = (current + " " + w).strip() if current else w
        if _measure_text(candidate, font)[0] <= max_width:
            current = candidate
        else:
            # word itself too long? break it
            if _measure_text(w, font)[0] > max_width:
                chunks = _wrap_word_fallback(w, font, max_width)
                # place first chunk on current line if possible
                first = chunks[0]
                cand2 = (current + " " + first).strip() if current else first
                if _measure_text(cand2, font)[0] <= max_width:
                    current = cand2
                    chunks = chunks[1:]
                # commit current if full
                if current:
                    lines.append(current)
                    current = ""
                for chnk in chunks:
                    if _measure_text(chnk, font)[0] <= max_width:
                        lines.append(chnk)
                    else:
                        # extreme fallback: char split already ensures fit
                        lines.append(chnk)
                    if len(lines) >= max_lines:
                        break
                if len(lines) >= max_lines:
                    break
            else:
                # commit current line and start new with word
                if current:
                    lines.append(current)
                current = w
                if len(lines) >= max_lines:
                    break
    if len(lines) < max_lines and current:
        lines.append(current)
    # Ellipsis if overflowed overall
    if len(lines) > max_lines:
        lines = lines[:max_lines]
    joined_len_by_chars = len(" ".join(words))
    visible_len_by_chars = sum(len(s) for s in lines)
    if visible_len_by_chars < joined_len_by_chars:
        last = lines[-1]
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
