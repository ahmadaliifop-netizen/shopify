#!/usr/bin/env python3
"""dump_events.py — the comp's window.__events() → events.json, so the score follows the picture."""
import json, pathlib, sys
from playwright.sync_api import sync_playwright
here = pathlib.Path(__file__).resolve().parent
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1920, "height": 1080})
    pg.goto((here / "comp.html").as_uri()); pg.evaluate("window.__ready")
    ev = pg.evaluate("window.__events()"); b.close()
(here / "events.json").write_text(json.dumps(ev, indent=1))
print(f"events.json: {len(ev['events'])} events")
