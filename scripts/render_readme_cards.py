#!/usr/bin/env python3
"""
Render the profile README's cards as animated SVGs into cards/.

Design matches parthdave.me: navy ground (#070d1a), bone type, chrome silver,
Space Grotesk / Inter / JetBrains Mono.

Every card is a standalone SVG shown through <img>, so it can only use what
GitHub allows there: inline CSS keyframes, SMIL, and fonts embedded as data
URIs (no JS, no external requests). Fonts are subset WOFFs in fonts/ (SIL OFL).

Live numbers come from data/contributions.json (scripts/fetch_contributions.py).
Project copy is taken from public repos and parthdave.me — nothing invented.

Run by .github/workflows/update-profile-art.yml after fetch_contributions.py.

STATIC=1 renders the final frame (for screenshots).
"""
from __future__ import annotations

import base64
import datetime
import json
import os
import re
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
DATA = os.path.join(ROOT, "data", "contributions.json")
OUT = os.path.join(ROOT, "cards")
FONTS = os.path.join(ROOT, "fonts")
PORTRAIT = os.path.join(ROOT, "assets", "portrait.jpg")

# ---- brand tokens (parthdave.me :root) --------------------------------------
BG = "#070d1a"
DEEP = "#0d1628"
ELEVATED = "#14203a"
BONE = "#e8ecf3"
SOFT = "#c9d1de"
MUTED = "#9aa6ba"
LINE = "#22304d"
SILVER = "#c9d1de"
CHROME = "#e6ebf2"
CHROME_FROM = "#8c97a8"
PAPER = "#f3efe6"
W = 880  # full card width, GitHub's README column at 100%

DISPLAY = "'Space Grotesk', system-ui, sans-serif"
SANS = "Inter, system-ui, -apple-system, sans-serif"
MONO = "'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace"

FONT_FILES = {
    "display": ("Space Grotesk", "normal", 700, "spacegrotesk-700.woff"),
    "display-m": ("Space Grotesk", "normal", 500, "spacegrotesk-500.woff"),
    "sans": ("Inter", "normal", 400, "inter-400.woff"),
    "sans-b": ("Inter", "normal", 600, "inter-600.woff"),
    "mono": ("JetBrains Mono", "normal", 400, "jetbrainsmono-400.woff"),
}

# Ten named projects on parthdave.me (About → Projects).
PORTFOLIO_BUILDS = 10
# Internship tracks named in the README brief: ML/AI, software, solutions.
INTERNSHIP_TRACKS = 3

# Featured public repos — descriptions from the portfolio / those READMEs.
REPOS = [
    {
        "name": "SimplyWins",
        "desc": "Does this job actually need AI? Tests rules, classic ML and LLMs, then recommends the simplest one that clears the bar.",
        "lang": "Python · FastAPI · scikit-learn",
        "href": "https://github.com/ParthD25/SimplyWins",
        "accent": CHROME,
    },
    {
        "name": "RaceShift",
        "desc": "Forecasts an F1 driver's next lap with a network trained one layer at a time, without backpropagation.",
        "lang": "Python · NumPy · FastAPI · React",
        "href": "https://github.com/ParthD25/RaceShift",
        "accent": SILVER,
    },
    {
        "name": "Plattr",
        "desc": "Scan a barcode, see where food came from and how well each claim is backed. Scored A+ to F.",
        "lang": "React · TypeScript · Vite",
        "href": "https://github.com/ParthD25/Plattr",
        "accent": CHROME_FROM,
    },
    {
        "name": "PawPulse",
        "desc": "Vet-clinic platform where AI agents handle intake triage and scheduling.",
        "lang": "Next.js · IBM watsonx · SQLite",
        "href": "https://github.com/ParthD25/PawPulse",
        "accent": BONE,
    },
]

BASE_CSS = """
@keyframes rise{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@keyframes pop{0%{opacity:0;transform:scale(.3)}70%{opacity:1;transform:scale(1.15)}100%{opacity:1;transform:none}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.28}}
@keyframes nudge{0%,100%{transform:none}50%{transform:translateX(4px)}}
@keyframes nudgeup{0%,100%{transform:none}50%{transform:translate(3px,-3px)}}
.r{opacity:0;animation:rise .8s cubic-bezier(.16,1,.3,1) both;transform-box:fill-box}
.f{opacity:0;animation:fade .9s ease-out both}
.g{transform-box:fill-box;transform-origin:bottom;transform:scaleY(0);animation:grow .8s cubic-bezier(.16,1,.3,1) both}
.p{opacity:0;transform-box:fill-box;transform-origin:center;animation:pop .4s ease-out both}
.live{animation:pulse 1.6s ease-in-out infinite}
.n{transform-box:fill-box;animation:nudge 1.8s ease-in-out infinite}
.nu{transform-box:fill-box;animation:nudgeup 1.8s ease-in-out infinite}
@keyframes tilein{0%{opacity:0;transform:translateY(90px) scale(.6) rotate(-9deg)}55%{opacity:1;transform:translateY(-10px) scale(1.05) rotate(2deg)}75%{transform:translateY(3px) scale(.98) rotate(-.8deg)}90%{transform:translateY(-1px) scale(1.01) rotate(.2deg)}100%{opacity:1;transform:none}}
@keyframes slidein{from{opacity:0;transform:translateX(-26px)}to{opacity:1;transform:none}}
@keyframes arrowin{0%{opacity:0;transform:translateX(-30px)}60%{opacity:1;transform:translateX(6px)}100%{opacity:1;transform:none}}
@keyframes roll{from{transform:translateY(60px)}to{transform:none}}
@keyframes sheen{0%{transform:translateX(-260px) skewX(-20deg)}22%,100%{transform:translateX(420px) skewX(-20deg)}}
@keyframes ring{0%{opacity:.7;transform:scale(.2)}100%{opacity:0;transform:scale(2.4)}}
.ti{opacity:0;transform-box:fill-box;transform-origin:50% 60%;animation:tilein 1.1s cubic-bezier(.16,1,.3,1) both}
.sl{opacity:0;transform-box:fill-box;animation:slidein .6s cubic-bezier(.16,1,.3,1) both}
.ai{opacity:0;transform-box:fill-box;animation:arrowin .7s cubic-bezier(.16,1,.3,1) both}
.ro{transform-box:fill-box;animation:roll .8s cubic-bezier(.15,.8,.2,1) both}
.sh{animation:sheen 5s ease-in-out infinite}
.rg{opacity:0;transform-box:fill-box;transform-origin:center;animation:ring 1s ease-out both}
@media (prefers-reduced-motion: reduce){
  .r,.f,.g,.p,.live,.n,.nu,.ti,.sl,.ai,.ro,.rg{animation:none!important;opacity:1!important;transform:none!important}
  .sh,.rg{display:none}
}
"""

STATIC = bool(os.environ.get("STATIC"))
GAP = 12
BOTTOM = 12
COL = W / 3


def font_face(keys):
    out = []
    for k in keys:
        fam, style, weight, fn = FONT_FILES[k]
        b64 = base64.b64encode(open(os.path.join(FONTS, fn), "rb").read()).decode()
        out.append(
            f"@font-face{{font-family:'{fam}';font-style:{style};font-weight:{weight};"
            f"src:url(data:font/woff;base64,{b64}) format('woff')}}"
        )
    return "".join(out)


def svg(w, h, body, fonts, label, extra_css="", left=0, right=0, bottom=BOTTOM):
    if left:
        body = f'<g transform="translate({left:.3f} 0)">{body}</g>'
    w, h = w + left + right, h + bottom
    css = font_face(fonts) + BASE_CSS + extra_css
    if STATIC:
        css += (
            ".r,.f,.g,.p,.live,.n,.nu,.ti,.sl,.ai,.ro{animation:none!important;"
            "opacity:1!important;transform:none!important}.sh,.rg{display:none}"
        )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.3f}" height="{h}" '
        f'viewBox="0 0 {w:.3f} {h}" role="img" aria-label="{escape(label)}">'
        f"<title>{escape(label)}</title><style>{css}</style>{body}</svg>"
    )


def write(name, content):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    with open(path, "w") as f:
        f.write(content)
    print(f"wrote cards/{name} ({len(content) // 1024} KB)")


def d(s):
    return f'style="animation-delay:{s:.2f}s"'


def wrap(text, n):
    lines, line = [], ""
    for word in text.split():
        if line and len(line) + 1 + len(word) > n:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    return lines + [line] if line else lines


def text_lines(x, y, lines, lh, attrs):
    return "".join(
        f'<text x="{x}" y="{y + i * lh}" {attrs}>{escape(l)}</text>' for i, l in enumerate(lines)
    )


def portrait_svg():
    """Navy/silver duotone of the public headshot on parthdave.me."""
    try:
        from io import BytesIO
        from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps
    except ImportError:
        print("Pillow missing; skipping portrait")
        return None
    if not os.path.exists(PORTRAIT):
        print(f"no portrait at {PORTRAIT}; skipping")
        return None

    im = Image.open(PORTRAIT).convert("RGB")
    w, h = im.size
    box = (int(w * 0.10), int(h * 0.00), int(w * 0.90), int(h * 0.82))
    im = im.crop(box)
    size = 280
    im = im.resize((size, size), Image.Resampling.LANCZOS)
    im = ImageEnhance.Contrast(im).enhance(1.15)
    im = im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=90, threshold=2))
    gray = ImageOps.grayscale(im)

    navy, hi = (7, 13, 26), (201, 209, 222)
    duo = Image.new("RGBA", (size, size))
    gp, dp = gray.load(), duo.load()
    for y in range(size):
        for x in range(size):
            t = (gp[x, y] / 255.0) ** 0.92
            dp[x, y] = (
                int(navy[0] + t * (hi[0] - navy[0])),
                int(navy[1] + t * (hi[1] - navy[1])),
                int(navy[2] + t * (hi[2] - navy[2])),
                255,
            )
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((2, 2, size - 3, size - 3), fill=255)
    duo.putalpha(mask)

    buf = BytesIO()
    duo.save(buf, format="PNG", optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return b64, size


# ---- 1 · hero ---------------------------------------------------------------
def hero():
    h = 430
    portrait = portrait_svg()
    portrait_markup = ""
    if portrait:
        b64, size = portrait
        dw = 318
        tx, ty = 528, 48
        portrait_markup = f"""
<g class="f" {d(0.35)}>
  <circle cx="{tx + dw / 2:.1f}" cy="{ty + dw / 2:.1f}" r="{dw / 2 + 6:.1f}" fill="none" stroke="{LINE}" stroke-width="1"/>
  <image href="data:image/png;base64,{b64}" x="{tx}" y="{ty}" width="{dw}" height="{dw}"/>
</g>
"""

    shine_anim = ""
    if not STATIC:
        shine_anim = (
            '<animateTransform attributeName="gradientTransform" type="translate" '
            'values="-640 0;640 0;640 0" keyTimes="0;.42;1" dur="7s" begin="1.5s" '
            'repeatCount="indefinite"/>'
        )

    line = wrap(
        "CMU M.S. student, graduating Dec 2027. Looking for Summer 2027 internships in ML/AI, software, and solutions engineering.",
        48,
    )
    body = f"""
<defs>
  <linearGradient id="shine" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="640" y2="0">
    <stop offset="0" stop-color="{BONE}"/>
    <stop offset=".42" stop-color="{BONE}"/>
    <stop offset=".5" stop-color="{CHROME}"/>
    <stop offset=".58" stop-color="{BONE}"/>
    <stop offset="1" stop-color="{BONE}"/>
    {shine_anim}
  </linearGradient>
  <linearGradient id="cardbg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{DEEP}"/>
    <stop offset="1" stop-color="{BG}"/>
  </linearGradient>
</defs>
<rect width="{W}" height="{h}" rx="16" fill="url(#cardbg)"/>
<rect x="0.75" y="0.75" width="{W - 1.5}" height="{h - 1.5}" rx="15.2" fill="none" stroke="{LINE}" stroke-width="1"/>
<g class="f" {d(0)}>
  <rect x="44" y="36" width="36" height="36" rx="10" fill="none" stroke="{SILVER}" stroke-width="1.2"/>
  <text x="62" y="59" text-anchor="middle" font-family="{DISPLAY}" font-weight="700" font-size="13" fill="{SILVER}">PD</text>
  <circle class="live" cx="102" cy="54" r="4" fill="{SILVER}"/>
  <text x="114" y="59" font-family="{SANS}" font-size="12" letter-spacing="0" fill="{MUTED}">CMU M.S. · DEC 2027</text>
</g>
<text class="r" {d(0.12)} x="44" y="168" font-family="{DISPLAY}" font-weight="700" font-size="86" letter-spacing="-3.2" fill="{BONE}">Parth</text>
<text class="r" {d(0.28)} x="44" y="254" font-family="{DISPLAY}" font-weight="700" font-size="86" letter-spacing="-3.2" fill="url(#shine)">Dave</text>
<g class="r" {d(0.5)}>
  {text_lines(44, 304, line, 22, f'font-family="{SANS}" font-size="15" fill="{SOFT}"')}
</g>
<g class="f" {d(0.75)}>
  <text x="44" y="392" font-family="{MONO}" font-size="12" fill="{BONE}">parthdave.me</text>
  <g class="nu" transform="translate(158 384)">
    <path d="M0 8 L8 0 M8 0 L8 6 M8 0 L2 0" fill="none" stroke="{SILVER}" stroke-width="1.4" stroke-linecap="round"/>
  </g>
</g>
{portrait_markup}
"""
    write(
        "hero.svg",
        svg(
            W,
            h,
            body,
            ["display", "sans", "mono"],
            "Parth Dave. CMU M.S. student, graduating Dec 2027. Looking for Summer 2027 internships in ML/AI, software, and solutions engineering.",
        ),
    )


# ---- 2 · tiles --------------------------------------------------------------
TILE_W, TILE_H = 880 / 3 - 8, 222


def count_up(num, word, x, y, attrs, begin, dur=1.1, frames=18):
    m = re.match(r"([\d.]+)(.*)", str(num))
    val, suf = float(m.group(1)), m.group(2)
    dec = len(m.group(1).split(".")[1]) if "." in m.group(1) else 0
    tail = f' <tspan font-weight="500">{escape(word)}</tspan>'
    if STATIC:
        return f'<text x="{x}" y="{y}" {attrs}>{escape(str(num))}{tail}</text>'
    out = []
    for i in range(frames + 1):
        e = 1 - (1 - i / frames) ** 3
        txt = str(num) if i == frames else f"{val * e:.{dec}f}{suf}"
        on = begin + dur * i / frames
        off = (
            ""
            if i == frames
            else f'<set attributeName="opacity" to="0" begin="{begin + dur * (i + 1) / frames:.3f}s"/>'
        )
        out.append(
            f'<text x="{x}" y="{y}" {attrs} opacity="0">{escape(txt)}{tail}'
            f'<set attributeName="opacity" to="1" begin="{on:.3f}s"/>{off}</text>'
        )
    return "".join(out)


def tile(name, label, fill, on, num, word, blurb, delay, pos, big=None):
    lines = wrap(blurb, 30)
    blurb_svg = "".join(
        f'<text class="r" {d(delay + 0.75 + i * 0.1)} x="22" y="{154 + i * 18}" '
        f'font-family="{SANS}" font-size="13" fill="{on}" fill-opacity=".92">{escape(l)}</text>'
        for i, l in enumerate(lines)
    )
    if big is not None:
        headline = (
            f'<text x="22" y="112" font-family="{DISPLAY}" font-weight="700" '
            f'font-size="44" fill="{on}">{escape(big)}'
            f'<tspan font-weight="500" font-size="28"> {escape(word)}</tspan></text>'
        )
    else:
        headline = count_up(
            num,
            word,
            22,
            112,
            f'font-family="{DISPLAY}" font-weight="700" font-size="44" fill="{on}"',
            delay + 0.45,
        )
    body = f"""
<defs>
  <clipPath id="card"><rect width="{TILE_W}" height="{TILE_H}" rx="16"/></clipPath>
  <clipPath id="slot"><rect x="0" y="62" width="{TILE_W}" height="62"/></clipPath>
  <linearGradient id="gl" x1="0" x2="1">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/>
    <stop offset=".5" stop-color="#fff" stop-opacity=".28"/>
    <stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="chrome" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{CHROME}"/>
    <stop offset=".48" stop-color="{SILVER}"/>
    <stop offset="1" stop-color="{CHROME_FROM}"/>
  </linearGradient>
</defs>
<g class="ti" {d(delay)}>
  <g clip-path="url(#card)">
    <rect width="{TILE_W}" height="{TILE_H}" fill="{fill}"/>
    <circle class="rg" {d(delay + 0.5)} cx="{TILE_W - 36}" cy="{TILE_H - 36}" r="54" fill="none" stroke="{on}" stroke-opacity=".4" stroke-width="1.5"/>
    <rect class="sh" style="animation-delay:{delay + 1.4:.2f}s" x="0" y="-20" width="80" height="{TILE_H + 40}" fill="url(#gl)" transform="translate(-260 0)"/>
  </g>
  <text class="sl" {d(delay + 0.35)} x="22" y="38" font-family="{MONO}" font-size="11" fill="{on}">{label}</text>
  <g class="ai" {d(delay + 0.5)}>
    <g class="n" style="animation-delay:{delay + 1.3:.2f}s" transform="translate({TILE_W - 34:.1f} 30)">
      <path d="M0 4 L8 4 M5 1 L8 4 L5 7" fill="none" stroke="{on}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </g>
  </g>
  <g clip-path="url(#slot)"><g class="ro" {d(delay + 0.45)}>{headline}</g></g>
  {blurb_svg}
</g>
"""
    write(
        f"{name}.svg",
        svg(
            TILE_W,
            TILE_H,
            body,
            ["display", "display-m", "sans", "mono"],
            f"{label}: {num or big} {word}. {blurb}",
            left=4 * pos,
            right=8 - 4 * pos,
        ),
    )


# ---- 3 · activity -----------------------------------------------------------
def activity(data):
    h = 348
    monthly = data["monthly"][-12:]
    best = max(monthly[:-1] or monthly, key=lambda m: m["total"])
    top = max(best["total"], 1)
    x0, x1, base, maxh, gap = 40, 600, 300, 148, 10
    bw = (x1 - x0 - gap * (len(monthly) - 1)) / max(len(monthly), 1)
    bars = []
    for i, m in enumerate(monthly):
        partial = i == len(monthly) - 1
        is_best = m is best
        bh = max(4, round(m["total"] / top * maxh))
        x = x0 + i * (bw + gap)
        fill = CHROME if is_best else (LINE if partial else SOFT)
        label = datetime.date.fromisoformat(m["month"] + "-01").strftime("%b")
        bars.append(
            f'<rect class="g" style="animation-delay:{2.4 + i * 0.07:.2f}s" x="{x:.1f}" y="{base - bh}" '
            f'width="{bw:.1f}" height="{bh}" rx="4" fill="{fill}">'
            f'<title>{label}: {m["total"]:,}</title></rect>'
            f'<text class="f" style="animation-delay:{2.4 + i * 0.07:.2f}s" x="{x + bw / 2:.1f}" y="{base + 22}" '
            f'text-anchor="middle" font-family="{MONO}" font-size="11" fill="{MUTED}">{label}</text>'
        )
        if is_best:
            bars.append(
                f'<text class="p" style="animation-delay:3.4s" x="{x + bw / 2:.1f}" y="{base - bh - 10}" '
                f'text-anchor="middle" font-family="{MONO}" font-size="11" fill="{CHROME}">{m["total"]:,}</text>'
            )

    cs = data["current_streak"]["length"]
    ls = data["longest_streak"]["length"]
    streak_note = "current streak, and the longest" if cs >= ls else f"current streak, longest {ls}"
    total_days = len(data["days"])
    best_label = datetime.date.fromisoformat(data["best_day"]["date"]).strftime("%b %-d")
    stats = [
        (f'{cs} <tspan font-weight="500">days</tspan>', streak_note),
        (f'{data["active_days"]}<tspan fill="{MUTED}"> / {total_days}</tspan>', "days with a commit"),
        (f'{data["best_day"]["count"]}', f"busiest day · {best_label}"),
    ]
    side = []
    for i, (big, small) in enumerate(stats):
        y = 108 + i * 90
        side.append(
            f'<g class="r" {d(2.8 + i * 0.15)}>'
            f'<text x="646" y="{y}" font-family="{DISPLAY}" font-weight="700" font-size="36" fill="{BONE}">{big}</text>'
            f'<text x="646" y="{y + 22}" font-family="{SANS}" font-size="13" fill="{MUTED}">{escape(small)}</text></g>'
        )
        if i < 2:
            side.append(
                f'<rect class="f" {d(2.8)} x="646" y="{y + 42}" width="190" height="1" fill="{LINE}"/>'
            )

    body = f"""
<rect width="{W}" height="{h}" rx="16" fill="{BG}"/>
<rect x="0.75" y="0.75" width="{W - 1.5}" height="{h - 1.5}" rx="15.2" fill="none" stroke="{LINE}"/>
<text class="f" {d(2.1)} x="40" y="48" font-family="{MONO}" font-size="11" fill="{MUTED}">THE LAST 12 MONTHS ON GITHUB</text>
<text class="r" {d(2.2)} x="38" y="102" font-family="{DISPLAY}" font-weight="700" font-size="42" fill="{BONE}">{data["total_contributions"]:,} <tspan font-weight="500" font-size="28" fill="{SOFT}">contributions</tspan></text>
{''.join(bars)}
{''.join(side)}
"""
    write(
        "activity.svg",
        svg(
            W,
            h,
            body,
            ["display", "display-m", "sans", "mono"],
            f'{data["total_contributions"]:,} contributions in the last year, {cs}-day streak',
        ),
    )


# ---- 4 · repo cards ---------------------------------------------------------
REPO_W, REPO_H = 880 / 2 - 8, 168


def repo_card(i, repo):
    delay = 4.5 + i * 0.1
    col = i % 2
    name, desc, lang, accent = repo["name"], repo["desc"], repo["lang"], repo["accent"]
    body = f"""
<rect width="{REPO_W}" height="{REPO_H}" rx="16" fill="{BG}"/>
<rect x="0.75" y="0.75" width="{REPO_W - 1.5}" height="{REPO_H - 1.5}" rx="15.2" fill="none" stroke="{LINE}"/>
<g class="r" {d(delay)}>
  <rect x="22" y="28" width="8" height="8" rx="2" fill="{accent}"/>
  <text x="38" y="37" font-family="{SANS}" font-weight="600" font-size="18" fill="{BONE}">{escape(name)}</text>
  {text_lines(22, 68, wrap(desc, 46), 20, f'font-family="{SANS}" font-size="14" fill="{SOFT}"')}
  <text x="22" y="{REPO_H - 26}" font-family="{MONO}" font-size="11" fill="{MUTED}">{escape(lang)}</text>
</g>
"""
    write(
        f"repo-{name.lower()}.svg",
        svg(
            REPO_W,
            REPO_H,
            body,
            ["sans", "sans-b", "mono"],
            f"{name}: {desc}",
            left=4 * col,
            right=8 - 4 * col,
        ),
    )


# ---- 5 · contribution graph -------------------------------------------------
HEAT = ["#152036", "#27476d", "#4d6f96", "#8c9bb0", SILVER, CHROME]


def level_for(c, level=None):
    if c == 0:
        return 0
    return 1 if c <= 3 else 2 if c <= 8 else 3 if c <= 20 else 4 if c <= 50 else 5


def heatmap(data):
    days = data["days"]
    first = datetime.date.fromisoformat(days[0]["date"])
    lead = (first.weekday() + 1) % 7  # sunday = 0
    cell, step, gx, gy = 12, 15, 44, 96
    cells, months, seen = [], [], set()
    for i, day in enumerate(days):
        k = i + lead
        col, row = divmod(k, 7)
        date = datetime.date.fromisoformat(day["date"])
        if date.day <= 7 and (date.year, date.month) not in seen and row == 0:
            seen.add((date.year, date.month))
            months.append((col, date.strftime("%b")))
        c = day["count"]
        delay = 1.8 + col * 0.028 + row * 0.016
        fill = HEAT[level_for(c, day.get("level"))]
        cells.append(
            f'<rect class="p" style="animation-delay:{delay:.2f}s" x="{gx + col * step}" y="{gy + row * step}" '
            f'width="{cell}" height="{cell}" rx="3" fill="{fill}">'
            f'<title>{day["date"]}: {c} contribution{"s" if c != 1 else ""}</title></rect>'
        )
    ncols = (len(days) + lead + 6) // 7
    right = gx + ncols * step - 3
    labels = "".join(
        f'<text x="{gx + col * step}" y="{gy + 7 * step + 16}" font-family="{MONO}" font-size="11" fill="{MUTED}">{m}</text>'
        for col, m in months
        if col < ncols - 8
    )
    legend_x = right - len(HEAT) * 14
    legend = "".join(
        f'<rect x="{legend_x + i * 14}" y="{gy + 7 * step + 6}" width="11" height="11" rx="2.5" fill="{c}"/>'
        for i, c in enumerate(HEAT)
    )
    h = gy + 7 * step + 44
    body = f"""
<rect width="{W}" height="{h}" rx="16" fill="{BG}"/>
<rect x="0.75" y="0.75" width="{W - 1.5}" height="{h - 1.5}" rx="15.2" fill="none" stroke="{LINE}"/>
<text class="r" {d(1.6)} x="42" y="58" font-family="{DISPLAY}" font-weight="700" font-size="30" fill="{BONE}">Every day, <tspan fill="{CHROME}">in silver</tspan></text>
<text class="f" {d(1.6)} x="{right}" y="56" text-anchor="end" font-family="{MONO}" font-size="11" fill="{MUTED}">REFRESHED DAILY</text>
{''.join(cells)}
<g class="f" {d(3.0)}>{labels}
<text x="{legend_x - 8}" y="{gy + 7 * step + 16}" text-anchor="end" font-family="{MONO}" font-size="11" fill="{MUTED}">less</text>
{legend}
<text x="{legend_x + len(HEAT) * 14 + 2}" y="{gy + 7 * step + 16}" font-family="{MONO}" font-size="11" fill="{MUTED}">more</text></g>
"""
    write(
        "heatmap.svg",
        svg(
            W,
            h,
            body,
            ["display", "mono"],
            f'Contribution graph: {data["total_contributions"]:,} contributions in the last year',
        ),
    )


def title_building():
    h = 64
    body = f"""
<rect width="{W}" height="{h}" rx="16" fill="{BG}"/>
<rect x="0.75" y="0.75" width="{W - 1.5}" height="{h - 1.5}" rx="15.2" fill="none" stroke="{LINE}"/>
<text class="r" {d(4.3)} x="28" y="42" font-family="{DISPLAY}" font-weight="700" font-size="26" fill="{BONE}">Featured <tspan font-weight="500" fill="{SOFT}">repos</tspan></text>
"""
    write("title-repos.svg", svg(W, h, body, ["display", "display-m"], "Featured repos", bottom=8))


if __name__ == "__main__":
    data = json.load(open(DATA))
    hero()
    tile(
        "work",
        "WORK",
        "url(#chrome)",
        BG,
        str(PORTFOLIO_BUILDS),
        "builds",
        "Applied AI, AI security, and product systems on parthdave.me.",
        1.05,
        0,
    )
    tile(
        "code",
        "CODE",
        ELEVATED,
        BONE,
        None,
        "GitHub",
        "Public repos including SimplyWins, RaceShift, Plattr, PawPulse.",
        1.28,
        1,
        big="PD",
    )
    tile(
        "seek",
        "SEEK",
        DEEP,
        CHROME,
        str(INTERNSHIP_TRACKS),
        "tracks",
        "Summer 2027 internships in ML/AI, software, and solutions engineering.",
        1.5,
        2,
    )
    heatmap(data)
    activity(data)
    title_building()
    for i, repo in enumerate(REPOS):
        repo_card(i, repo)
