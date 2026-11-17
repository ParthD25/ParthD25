#!/usr/bin/env python3
"""Lay the README cards out like GitHub and screenshot them with headless Chrome.

STATIC=1 should be set before rendering the cards so this captures the end frame.
Pass --animated to load the animated SVGs instead (for a GIF).
"""
from __future__ import annotations

import argparse
import os
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREVIEW = ROOT / "preview"
CARDS = ROOT / "cards"
CHROME = os.environ.get("CHROME", "google-chrome")


def write_html(out: Path, animated: bool) -> Path:
    cache = "" if animated else "?v=static"
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>Parth Dave — README preview</title>
  <style>
    html, body {{ margin: 0; background: #ffffff; }}
    .col {{
      max-width: 888px;
      margin: 28px auto 48px;
      padding: 0 24px;
    }}
    p {{ margin: 0; line-height: 0; font-size: 0; }}
    img {{ border: 0; vertical-align: top; }}
  </style>
</head>
<body>
  <div class="col">
    <p><img src="../cards/hero.svg{cache}" width="100%" alt=""/></p>
    <p>
      <img src="../cards/work.svg{cache}" width="32.5%" alt=""/>
      <img src="../cards/code.svg{cache}" width="32.5%" alt=""/>
      <img src="../cards/seek.svg{cache}" width="32.5%" alt=""/>
    </p>
    <p><img src="../cards/heatmap.svg{cache}" width="100%" alt=""/></p>
    <p><img src="../cards/activity.svg{cache}" width="100%" alt=""/></p>
    <p><img src="../cards/title-repos.svg{cache}" width="100%" alt=""/></p>
    <p>
      <img src="../cards/repo-simplywins.svg{cache}" width="49%" alt=""/>
      <img src="../cards/repo-raceshift.svg{cache}" width="49%" alt=""/>
    </p>
    <p>
      <img src="../cards/repo-plattr.svg{cache}" width="49%" alt=""/>
      <img src="../cards/repo-pawpulse.svg{cache}" width="49%" alt=""/>
    </p>
  </div>
</body>
</html>
"""
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    return out


def chrome_shot(html: Path, png: Path, *, width=936, height=2100, delay_ms=1200):
    png.parent.mkdir(parents=True, exist_ok=True)
    url = html.resolve().as_uri()
    cmd = [
        CHROME,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--hide-scrollbars",
        f"--user-data-dir=/tmp/chrome-readme-{os.getpid()}",
        "--force-device-scale-factor=2",
        f"--window-size={width},{height}",
        "--default-background-color=ffffffff",
        f"--screenshot={png}",
        url,
    ]
    try:
        subprocess.run(cmd, check=False, cwd=ROOT, timeout=25)
    except subprocess.TimeoutExpired:
        pass
    if not png.exists():
        raise SystemExit(f"chrome did not write {png}")
    _trim_whitespace(png)
    print(f"wrote {png}")


def _trim_whitespace(png: Path, pad=28):
    try:
        from PIL import Image
    except ImportError:
        return
    im = Image.open(png).convert("RGB")
    bg = im.getpixel((0, 0))
    w, h = im.size
    pixels = im.load()
    top = 0
    bottom = h - 1
    for y in range(h):
        if any(pixels[x, y] != bg for x in range(0, w, 4)):
            top = y
            break
    for y in range(h - 1, -1, -1):
        if any(pixels[x, y] != bg for x in range(0, w, 4)):
            bottom = y
            break
    box = (0, max(0, top - pad), w, min(h, bottom + pad + 1))
    im.crop(box).save(png, "PNG", optimize=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--animated", action="store_true")
    parser.add_argument("--out", default=str(PREVIEW / "readme_static.png"))
    args = parser.parse_args()
    html = write_html(
        PREVIEW / ("readme_animated.html" if args.animated else "readme_static.html"),
        animated=args.animated,
    )
    chrome_shot(Path(html), Path(args.out), delay_ms=4000 if args.animated else 1500)


if __name__ == "__main__":
    main()
