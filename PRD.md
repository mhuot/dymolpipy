# Voice Label Printer PRD (Apple-first)

This document defines the next steps to create a hands‑free, voice‑triggered label printer using Apple Shortcuts to drive a local Flask service that prints to a DYMO LabelWriter.

## Summary

- Voice platform: Apple Shortcuts (primary), with optional Home Assistant integration later.
- Printer: DYMO LabelWriter 450 (CUPS), invoked via `lpr`.
- Label stock: DYMO 30252 (1‑1/8" x 3‑1/2") Address & Barcode Labels.
- Local-only by default: no cloud dependency; simple token auth.

## Assumptions

- Host OS: macOS or Raspberry Pi (Raspberry Pi OS/Debian) with CUPS installed and `lpr` available.
- Printer name: "DYMO LabelWriter 450" (as shown in macOS/CUPS). If different, we will make this configurable.
- DPI: 300. Label pixel target ≈ 1050 × 338 (3.5" x 1.125" at 300 DPI) which matches existing code’s ~1051×331.
- Media option: the CUPS PPD for DYMO will expose a media/page size for 30252. We now auto-detect this on first use (best-effort) and persist it to `config.json`.

## Host OS notes

- macOS
  - CUPS is present by default; `lpr` is available.
  - Printer appears as "DYMO LabelWriter 450" in System Settings and CUPS.
  - Common font path used in this repo: `/System/Library/Fonts/Supplemental/Tahoma.ttf`.

- Raspberry Pi (Raspberry Pi OS/Debian)
  - Install CUPS and drivers:
    - `sudo apt update && sudo apt install cups printer-driver-dymo`
  - Add your user to lpadmin and enable remote access if needed:
    - `sudo usermod -aG lpadmin $USER`
  - Start/enable CUPS service: `sudo systemctl enable --now cups`
  - Typical monospaced font path: `/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf`.

To discover available media names for the DYMO manually (optional):
```
lpoptions -p "DYMO LabelWriter 450" -l | grep -i media
```

## Goals

- Dictate a label and print in under 3 seconds on the local network.
- Support copies and size preset (small/large) via voice.
- Keep a small history (“last job”) to enable quick reprint.
- Run locally, require a shared token, and avoid exposing the service publicly.

## Non-goals

- Complex layout editing (beyond 1–2 lines and basic presets) in v1.
- Public internet exposure by default.

## User stories

1. As a user, I say "Print label: miniature paints drawer B" and a label prints.
2. As a user, I say "Print label shelf C, 4 copies" and 4 labels print.
3. As a user, I say "Reprint that 3 times" to reprint the last label.
4. As a user, I say "Print label small: screws M3" to pick the small size preset.

## Functional requirements

- Input parameters: text (1–80 chars), copies (1–20, default 1), size preset (small|large, default large), optional media override.
- Render: word-based auto-wrap to max 2 lines with ellipsis on overflow; split overly long words.
- Print: use `lpr` targeting the DYMO LabelWriter 450; pass DPI 300 and media when available (auto-detected if missing).
- History: store last job for reprint.
- Observability: save last N rendered PNGs to `output/`; basic log lines.

## Non-functional requirements

- Performance: p50 job submission < 3s from Shortcut invocation on LAN.
- Reliability: graceful errors when printer unavailable; no crashes on bad input.
- Security: token required; bind to LAN; document not exposing publicly.
- Privacy: no cloud logs in the primary flow.

## Architecture

- Flask app (existing `app/`), extended with new JSON POST endpoints under `/api/*`.
- Rendering via Pillow (existing), with parameterized dimensions and fonts.
- Printing via `lpr`, default printer name set to "DYMO LabelWriter 450" (configurable). If `media` is not set, we attempt to discover the 30252 token via `lpoptions`.
- Apple Shortcut invokes POST /api/print with JSON and a token header.

## API (v1)

Auth: All POST endpoints require `X-Label-Token: <token>` header (or `?token=...`).

- POST /api/print
  - Request JSON:
    - text: string (required, <= 80)
    - copies: integer (optional, 1..20, default 1)
    - size: string enum (optional: "small" | "large", default "large")
    - media: string (optional CUPS media name; if omitted, use configured default or detected value)
  - Response 200:
    - { jobId: string, text: string, copies: number }
  - Response errors: 400 invalid input, 401 unauthorized, 409 printer unavailable, 500 internal

- POST /api/reprint
  - Request JSON:
    - jobId: string (optional; if omitted, reprint last)
    - copies: integer (optional, default 1)
  - Response 200: { jobId: string }
  - Errors: 401, 404 (no last job), 500

- GET /api/health
  - Response 200: { status: "ok" }

Compatibility (existing):
- Keep `GET /print/<labelContent>` for quick testing in development; mark deprecated.

## Rendering details

- Canvas: base square then rotate and crop to ~1050×338, aligning with DYMO 30252 at 300 DPI.
- Fonts:
  - large: 300px monospaced (default)
  - small: 200px monospaced
  - Font path configurable per-OS; default to DejaVuSansMono or macOS Tahoma if available.
- Wrap: word-based to max 2 lines; very long words are split; ellipsis added if overflow.

## Printing details

- Printer name: default `-P "DYMO LabelWriter 450"` (configurable env/ini).
- DPI: `-o ppi=300`.
- Media: uses configured `media` from `config.json` or attempts detection via `lpoptions` (searching for tokens containing `30252`).
- Copies: use `-# <n>` if supported; otherwise loop submits.

## Security

- Generate a random token at first run; store in a local file (e.g., `.label_token`).
- Require token header on POST endpoints.
- Bind to 0.0.0.0 but recommend LAN only; document that public exposure is not supported.

## Apple Shortcut design

- Steps (high level):
  1) Dictate Text → `text`
  2) Ask for Input (Number, optional) → `copies` (default 1)
  3) Choose from Menu (Large/Small) → `size`
  4) Build JSON `{ "text": text, "copies": copies, "size": size }`
  5) Get Contents of URL (POST http://<printer-host>:5000/api/print)
     - Headers: `Content-Type: application/json`, `X-Label-Token: <token>`
  6) Show Result (optional)

- A second Shortcut can call `/api/reprint` with a number prompt for copies.

## Metrics

- Measure time from Shortcut start to 200 OK; log duration in the Flask app.
- Track print success/failure counts in logs.

## Risks & mitigations

- Media option mismatch → Auto-detect on first use; allow manual override.
- Font availability → Provide clear macOS and Raspberry Pi default paths and fallbacks; allow config.
- Printer offline → Return 409 with message; optionally retry once.

## Milestones

- Phase 1: API + Apple Shortcuts (v1) — Implemented
  - `/api/print`, `/api/reprint`, `/api/health`, token auth
  - Rendering presets and 2-line word-based wrapping with ellipsis
  - Media auto-detection on first use; config persisted
  - Example Shortcut guidance in README

- Phase 2: Home Assistant (optional)
  - REST Command and Assist sentences to trigger prints locally.

- Phase 3: Enhancements (optional)
  - Barcode/QR support; media selection by voice; last N job history endpoint; simple UI; rate limiting.

## Open questions

- Will the service run permanently on macOS (sleep considerations) or a small always-on Raspberry Pi?
- Do you prefer a bundled open font for consistency?
- Do you want us to ship a pre-made Apple Shortcut file in the repo?
