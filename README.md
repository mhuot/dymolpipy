# dymolpipy

Python utilities to render and print labels to a DYMO label printer (or any CUPS printer) using `lpr`. Originally built in 2019 as an Amazon Alexa skill backend; today it also works as a simple local web service and via a few small command-line scripts.

Note: The Alexa integration included here is likely obsolete due to changes in the Alexa Skills platform since 2019. The Lambda code remains in this repo for reference but isn’t maintained.

## What’s inside

- Web service (Flask) that exposes simple HTTP endpoints to print labels via `lpr`.
- Command-line scripts experimenting with 1–3 line labels and media testing.
- Sample utilities to test CUPS media options.
- Legacy Alexa Skill (Lambda) code that called the web service through an ngrok URL.

## Requirements

- macOS or Linux with CUPS installed (so `lpr` works)
- A label printer supported by CUPS (e.g., DYMO LabelWriter)
- Python 3.7+ (project was created on Python 3.7/3.8; newer versions should work but dependencies are pinned old)
- Pillow (installed via `requirements.txt`)
- A monospaced font available on your system. The code references:
  - Linux: `/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf`
  - macOS examples in some scripts: `/System/Library/Fonts/Supplemental/Tahoma.ttf`
  Adjust font paths as needed for your OS.

Tip: Create an `output/` directory in the project root to view generated images that are sent to the printer.

## Installation

1) Create and activate a virtual environment, then install dependencies:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2) Ensure an `output` directory exists:

```
mkdir -p output
```

3) Make sure your printer is available to CUPS and `lpr` works:

- On macOS, verify the printer in System Settings and try a test page.
- On Linux, confirm the DYMO CUPS driver is installed and `lpstat -p` shows the printer.

## Web service usage (Flask)

The Flask app is in `app/` with routes defined in `app/routes.py`.

Endpoints:

- GET `/` or `/index` — health check (“Hello, World!”)
- GET `/print/<labelContent>` — render `<labelContent>` into a 1-bit PNG and send to printer via `lpr -o ppi=300`
  - Also saves `output/rotated.png` for debugging/preview
- GET `/reprint/<labelContent>/<number>` — currently returns a message but does not loop printing yet

Run locally (example):

```
export FLASK_APP=web-label.py
export FLASK_ENV=development
flask run
```

Then in another shell or browser:

```
curl "http://127.0.0.1:5000/print/Hello%20World"
```

Notes/limitations for the web endpoint:

- Font size is fixed large (300) and text is not wrapped; long strings may clip.
- Image is constructed square and rotated then cropped to an approximately 1051×331 logical area (variables `length` and `width` in code). Adjust as needed for your media.
- `lpr` is invoked without a specific `-P` printer name; your system default printer will be used unless you customize the command in `app/routes.py`.

## Command-line scripts

These scripts were used to experiment with font sizing, wrapping, and media. They all generate images in `output/` and some invoke `lpr`.

- `1linelabel.py` — one-line label demo. Supports `--dry`/`-d` to skip printing. Currently prints a sample string; edit the script to set your content.
- `2linelabel.py`, `3linelabel.py` — examples for multi-line layout with fixed fonts and sizes.
- `fulllabel.py` — early work on wrapping a long string into up to three lines; tweak to suit your needs.
- `testmedia.py`, `2testmedia.py` — iterate over media types from `media.txt` and send test prints using `lpr -o media=... -o ppi=300` (helpful to confirm driver options).

Because these are experiments, expect to adjust font file paths, sizes, and dimensions for your specific printer and label stock.

## Legacy Alexa Skill (likely obsolete)

The `Skill Code/lambda/` folder contains Lambda code built with `ask-sdk-core` that, in 2019, called the web service via an ngrok URL (see `lambda_function.py`). This integration is not maintained and may no longer function due to platform changes:

- Interaction model and intents may need updates.
- ngrok endpoint is hard-coded and stale.
- Dependencies and AWS runtime versions have evolved.

If you want voice control now, consider wiring the web endpoint into a platform like:

- Apple Shortcuts (HTTP Get)
- Home Assistant (REST Command)
- IFTTT / Make.com (Webhooks)
- Slack slash commands (serverless function → call `/print/...`)

## Customizing printing

- Printer selection: add `-P <printer_name>` to the `lpr` command in the code or set a system default printer.
- DPI/quality: the code uses `-o ppi=300`; check your driver for supported options (e.g., `-o PrintQuality=Graphics`).
- Media: pass `-o media=<name>` if your CUPS driver supports media presets. See `testmedia.py` and `media.txt`.
- Fonts: update font file paths to installed fonts on your system; monospaced fonts can help with predictable layout.

## Troubleshooting

- Nothing prints: ensure `lpr` works outside of Python and the printer is the system default or explicitly specified.
- “Cannot open resource” from Pillow: the font path is incorrect; switch to a font present on your machine.
- The image saves but is rotated/cropped wrong: adjust `length`, `width`, and font size in the scripts or `app/routes.py`.
- Permission errors on macOS: if running a web server, macOS privacy controls may require granting Terminal/VS Code access to the printer.

## Development notes

- Dependencies in `requirements.txt` are pinned to older versions that matched the 2019 runtime (Flask 1.1.x, Pillow 6.x). You may upgrade them for modern Python, but test image rendering and printing options after any upgrade.
- This repo does not include a full production server setup. The Flask debug server is fine for local printing; for remote use, put it behind auth and TLS.
