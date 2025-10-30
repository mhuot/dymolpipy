from app import app
from flask import request, jsonify
from PIL import Image, ImageDraw, ImageFont
import os
import sys
from typing import Optional

from app.config import load_or_create_token, load_config, ensure_media_configured
from app.label_utils import render_label, print_label, load_last_job

# --- Legacy demo print helper (kept for back-compat) ---

def printit(mytext):
    output = "./output"
    length = 986
    width = 331
    fontsize = 300
    img = Image.new('1', (length,length), 255) # Length is 1051 so we make a square of it and then we can rotate into a rectangle that is 1051x331

    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", fontsize) # System font so easy to deal with

    d = ImageDraw.Draw(img)
    d.text((0,0), mytext, font=font)
    rotated = img.rotate(270)
    rotated = rotated.crop( (length-width, 0, length, length) ) # Getting to the 1051x331 rectangle

    os.makedirs(output, exist_ok=True)
    rotated.save(f"{output}/rotated.png")
    os.system(f"lpr -o ppi=300 {output}/rotated.png")

# --- Basic pages ---

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"

# --- Legacy GET endpoints (dev convenience) ---

@app.route('/print/<string:labelContent>', methods=['GET'])
def printLabel(labelContent):
    printit(labelContent)
    return f"Printing a label that says {labelContent}"

@app.route('/reprint/<string:labelContent>/<int:number>', methods=['GET'])
def reprintLabel(labelContent,number):
    return f"Printing label with the text '{labelContent}'' {number} times"

# --- Token helper ---

def _require_token() -> Optional[str]:
    token = request.headers.get('X-Label-Token') or request.args.get('token')
    expected = load_or_create_token()
    if not token or token != expected:
        return None
    return token

# --- API v1 ---

@app.route('/api/health', methods=['GET'])
def api_health():
    return jsonify({"status": "ok"})

@app.route('/api/config', methods=['GET'])
def api_config():
    cfg = load_config()
    # Do not include any secrets (token is stored separately anyway)
    return jsonify({
        "printer_name": cfg.get("printer_name"),
        "dpi": cfg.get("dpi"),
        "media": cfg.get("media"),
        "size_presets": cfg.get("size_presets"),
        "canvas": cfg.get("canvas"),
        "font_paths": cfg.get("font_paths")
    })

@app.route('/api/print', methods=['POST'])
def api_print():
    if _require_token() is None:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    text = data.get('text')
    if not isinstance(text, str) or len(text.strip()) == 0 or len(text) > 80:
        return jsonify({"error": "invalid text"}), 400
    copies = data.get('copies', 1)
    try:
        copies = int(copies)
    except Exception:
        return jsonify({"error": "invalid copies"}), 400
    if copies < 1 or copies > 20:
        return jsonify({"error": "copies out of range (1..20)"}), 400
    size = data.get('size', 'large')
    if size not in ('small', 'large'):
        return jsonify({"error": "invalid size"}), 400
    media = data.get('media')
    if media is not None and not isinstance(media, str):
        return jsonify({"error": "invalid media"}), 400

    img_path, meta = render_label(text.strip(), size_preset=size)
    try:
        cfg = load_config()
        effective_media = media if media else (cfg.get('media') or ensure_media_configured())
        print_label(img_path, copies=copies, media=effective_media)
    except Exception as e:
        return jsonify({"error": "print failed", "detail": str(e)}), 409

    job_id = str(meta.get('timestamp'))
    return jsonify({"jobId": job_id, "text": meta.get('text'), "copies": copies})

@app.route('/api/reprint', methods=['POST'])
def api_reprint():
    if _require_token() is None:
        return jsonify({"error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    copies = data.get('copies', 1)
    try:
        copies = int(copies)
    except Exception:
        return jsonify({"error": "invalid copies"}), 400
    if copies < 1 or copies > 20:
        return jsonify({"error": "copies out of range (1..20)"}), 400

    job_id = data.get('jobId')
    last = load_last_job()
    if not last:
        return jsonify({"error": "no last job"}), 404

    last_id = str(last.get('timestamp'))
    if job_id and str(job_id) != last_id:
        return jsonify({"error": "job not found"}), 404

    try:
        cfg = load_config()
        effective_media = cfg.get('media') or ensure_media_configured()
        print_label(last['image_path'], copies=copies, media=effective_media)
    except Exception as e:
        return jsonify({"error": "print failed", "detail": str(e)}), 409

    return jsonify({"jobId": last_id, "reprinted": copies})
