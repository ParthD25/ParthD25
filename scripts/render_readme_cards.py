#!/usr/bin/env python3
"""
Render the profile README's cards as animated SVGs into cards/.

Design matches parthdave.me: navy ground (#070d1a), bone type, chrome silver,
Space Grotesk / Inter / JetBrains Mono.

Layout follows builder profile READMEs (one line about what he makes, grouped
tools, projects, then activity): see Avi Vashishta's profile and
docs/copy_research.md. This is a GitHub showcase, not a resume. Clarity over flash.

Every card is a standalone SVG shown through <img>, so it can only use what
GitHub allows there: inline CSS keyframes, SMIL, and fonts embedded as data
URIs (no JS, no external requests). Fonts are subset WOFFs in fonts/ (SIL OFL).

Live numbers come from data/contributions.json (scripts/fetch_contributions.py).
Project copy and skills are taken from public repos and parthdave.me — nothing
invented. Weak vanity stats (build counts, internship-track counts) are omitted.

Run by .github/workflows/update-profile-art.yml after fetch_contributions.py.

STATIC=1 renders the final frame (for screenshots).
"""
from __future__ import annotations

import base64
import datetime
import json
import os
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
DATA = os.path.join(ROOT, "data", "contributions.json")
OUT = os.path.join(ROOT, "cards")
FONTS = os.path.join(ROOT, "fonts")

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

# Skills that actually appear in public repos / parthdave.me project tags.
SKILLS = [
    ("Languages", ["Python", "TypeScript", "JavaScript", "Swift", "C"]),
    ("ML / AI", ["scikit-learn", "NumPy", "pandas", "IBM watsonx", "Groq"]),
    ("Web / backend", ["React", "Next.js", "FastAPI", "Vite", "Express"]),
    ("Cloud / tools", ["Supabase", "Postgres", "SQLite", "Firebase", "Vercel"]),
]

# Featured public repos — descriptions from the portfolio / those READMEs.
REPOS = [
    {
        "name": "SimplyWins",
        "desc": "Does this job actually need AI? Tests rules, classic ML and LLMs, then recommends the simplest one that clears the bar.",
        "lang": "Python · FastAPI · scikit-learn · Groq",
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

# Small footer only (Avi's README: site / linkedin — no email card).
LINKS = [
    {"label": "parthdave.me", "href": "https://www.parthdave.me/"},
    {"label": "LinkedIn", "href": "https://www.linkedin.com/in/parth-dave-a0288221a/"},
]

BASE_CSS = """
@keyframes rise{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@keyframes pop{0%{opacity:0;transform:scale(.3)}70%{opacity:1;transform:scale(1.12)}100%{opacity:1;transform:none}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.28}}
@keyframes nudge{0%,100%{transform:none}50%{transform:translateX(4px)}}
@keyframes nudgeup{0%,100%{transform:none}50%{transform:translate(3px,-3px)}}
.r{opacity:0;animation:rise .7s cubic-bezier(.16,1,.3,1) both;transform-box:fill-box}
.f{opacity:0;animation:fade .8s ease-out both}
.g{transform-box:fill-box;transform-origin:bottom;transform:scaleY(0);animation:grow .8s cubic-bezier(.16,1,.3,1) both}
.p{opacity:0;transform-box:fill-box;transform-origin:center;animation:pop .35s ease-out both}
.live{animation:pulse 1.6s ease-in-out infinite}
.n{transform-box:fill-box;animation:nudge 1.8s ease-in-out infinite}
.nu{transform-box:fill-box;animation:nudgeup 1.8s ease-in-out infinite}
@media (prefers-reduced-motion: reduce){
  .r,.f,.g,.p,.live,.n,.nu{animation:none!important;opacity:1!important;transform:none!important}
}
"""

STATIC = bool(os.environ.get("STATIC"))
BOTTOM = 12


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
            ".r,.f,.g,.p,.live,.n,.nu{animation:none!important;"
            "opacity:1!important;transform:none!important}"
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
    return lines + [line] if line else []


def text_lines(x, y, lines, lh, attrs):
    return "".join(
        f'<text x="{x}" y="{y + i * lh}" {attrs}>{escape(l)}</text>' for i, l in enumerate(lines)
    )


def card_shell(w, h, fill=BG):
    return (
        f'<rect width="{w}" height="{h}" rx="16" fill="{fill}"/>'
        f'<rect x="0.75" y="0.75" width="{w - 1.5}" height="{h - 1.5}" rx="15.2" '
        f'fill="none" stroke="{LINE}" stroke-width="1"/>'
    )


def shine_defs():
    shine_anim = ""
    if not STATIC:
        shine_anim = (
            '<animateTransform attributeName="gradientTransform" type="translate" '
            'values="-640 0;640 0;640 0" keyTimes="0;.42;1" dur="7s" begin="1.2s" '
            'repeatCount="indefinite"/>'
        )
    return f"""
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
"""


# ---- 1 · hero (no portrait) -------------------------------------------------
HERO_INTRO = [
    "I build full-stack AI products people can actually use.",
]
HERO_EYEBROW = "AI DEVELOPER"
HERO_ALT = "Parth Dave. I build full-stack AI products people can actually use."


def hero():
    # One intro line: keep the original name/intro gap, shrink the card so the
    # bottom padding matches the old three-line hero instead of leaving a hole.
    h = 220
    body = f"""
{shine_defs()}
<rect width="{W}" height="{h}" rx="16" fill="url(#cardbg)"/>
<rect x="0.75" y="0.75" width="{W - 1.5}" height="{h - 1.5}" rx="15.2" fill="none" stroke="{LINE}" stroke-width="1"/>
<g class="f" {d(0)}>
  <rect x="36" y="28" width="36" height="36" rx="10" fill="none" stroke="{SILVER}" stroke-width="1.2"/>
  <text x="54" y="51" text-anchor="middle" font-family="{DISPLAY}" font-weight="700" font-size="13" fill="{SILVER}">PD</text>
  <circle class="live" cx="94" cy="46" r="4" fill="{SILVER}"/>
  <text x="106" y="51" font-family="{MONO}" font-size="12" fill="{MUTED}">{HERO_EYEBROW}</text>
</g>
<text class="r" {d(0.12)} x="36" y="128" font-family="{DISPLAY}" font-weight="700" font-size="56" letter-spacing="-1.8" fill="url(#shine)">Parth Dave</text>
<g class="r" {d(0.32)}>
  {text_lines(36, 178, HERO_INTRO, 24, f'font-family="{SANS}" font-size="16" fill="{SOFT}"')}
</g>
"""
    write(
        "hero.svg",
        svg(
            W,
            h,
            body,
            ["display", "sans", "mono"],
            HERO_ALT,
        ),
    )


# ---- 2 · skills -------------------------------------------------------------
def skills():
    h = 250
    cols = 4
    pad_x = 36
    col_w = (W - pad_x * 2) / cols
    groups = []
    for i, (title, items) in enumerate(SKILLS):
        x = pad_x + i * col_w
        rows = [
            f'<text class="f" {d(0.85)} x="{x:.1f}" y="86" font-family="{MONO}" '
            f'font-size="11" fill="{MUTED}">{escape(title.upper())}</text>'
        ]
        for j, item in enumerate(items):
            y = 118 + j * 26
            rows.append(
                f'<g class="r" {d(0.95 + i * 0.05 + j * 0.04)}>'
                f'<rect x="{x:.1f}" y="{y - 9}" width="6" height="6" rx="1.5" fill="{SILVER}" fill-opacity=".7"/>'
                f'<text x="{x + 14:.1f}" y="{y}" font-family="{SANS}" font-size="14" fill="{BONE}">{escape(item)}</text>'
                f"</g>"
            )
        groups.append("".join(rows))
        if i:
            groups.append(
                f'<rect class="f" {d(0.8)} x="{x - 16:.1f}" y="78" width="1" height="148" fill="{LINE}"/>'
            )

    body = f"""
{card_shell(W, h)}
<text class="f" {d(0.7)} x="36" y="42" font-family="{MONO}" font-size="11" fill="{MUTED}">STACK</text>
<text class="r" {d(0.75)} x="36" y="64" font-family="{DISPLAY}" font-weight="700" font-size="22" fill="{BONE}">What I build with</text>
{''.join(groups)}
"""
    write(
        "skills.svg",
        svg(
            W,
            h,
            body,
            ["display", "sans", "mono"],
            "What I build with: languages, ML/AI, web/backend, cloud/tools",
        ),
    )


# ---- 3 · activity -----------------------------------------------------------
def activity(data):
    h = 328
    monthly = data["monthly"][-12:]
    # Highlight the busiest completed month, but scale every bar against the
    # full series so a partial current month cannot overflow the plot area.
    best = max(monthly[:-1] or monthly, key=lambda m: m["total"])
    top = max((m["total"] for m in monthly), default=1) or 1
    x0, x1, base, maxh, gap = 40, 600, 284, 148, 10
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
            f'<rect class="g" style="animation-delay:{2.2 + i * 0.07:.2f}s" x="{x:.1f}" y="{base - bh}" '
            f'width="{bw:.1f}" height="{bh}" rx="4" fill="{fill}">'
            f'<title>{label}: {m["total"]:,}</title></rect>'
            f'<text class="f" style="animation-delay:{2.2 + i * 0.07:.2f}s" x="{x + bw / 2:.1f}" y="{base + 22}" '
            f'text-anchor="middle" font-family="{MONO}" font-size="11" fill="{MUTED}">{label}</text>'
        )
        if is_best:
            bars.append(
                f'<text class="p" style="animation-delay:3.2s" x="{x + bw / 2:.1f}" y="{base - bh - 10}" '
                f'text-anchor="middle" font-family="{MONO}" font-size="11" fill="{CHROME}">{m["total"]:,}</text>'
            )

    cs = data["current_streak"]["length"]
    ls = data["longest_streak"]["length"]
    if cs >= ls:
        streak_note = "current streak"
    else:
        streak_note = f"current streak · longest {ls}"
    total_days = len(data["days"])
    stats = [
        (f'{cs} <tspan font-weight="500">days</tspan>', streak_note),
        (f'{data["active_days"]}<tspan fill="{MUTED}"> / {total_days}</tspan>', "days with a commit"),
    ]
    side = []
    for i, (big, small) in enumerate(stats):
        y = 132 + i * 110
        side.append(
            f'<g class="r" {d(2.6 + i * 0.15)}>'
            f'<text x="646" y="{y}" font-family="{DISPLAY}" font-weight="700" font-size="36" fill="{BONE}">{big}</text>'
            f'<text x="646" y="{y + 22}" font-family="{SANS}" font-size="13" fill="{MUTED}">{escape(small)}</text></g>'
        )
        if i == 0:
            side.append(
                f'<rect class="f" {d(2.6)} x="646" y="{y + 48}" width="190" height="1" fill="{LINE}"/>'
            )

    body = f"""
{card_shell(W, h)}
<text class="f" {d(1.9)} x="40" y="44" font-family="{MONO}" font-size="11" fill="{MUTED}">THE LAST 12 MONTHS ON GITHUB</text>
<text class="r" {d(2.0)} x="38" y="92" font-family="{DISPLAY}" font-weight="700" font-size="38" fill="{BONE}">{data["total_contributions"]:,} <tspan font-weight="500" font-size="24" fill="{SOFT}">contributions</tspan></text>
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
    delay = 1.35 + i * 0.1
    col = i % 2
    name, desc, lang, accent = repo["name"], repo["desc"], repo["lang"], repo["accent"]
    body = f"""
{card_shell(REPO_W, REPO_H)}
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
    cell, step, gx, gy = 12, 15, 44, 88
    cells, months, seen = [], [], set()
    for i, day in enumerate(days):
        k = i + lead
        col, row = divmod(k, 7)
        date = datetime.date.fromisoformat(day["date"])
        if date.day <= 7 and (date.year, date.month) not in seen and row == 0:
            seen.add((date.year, date.month))
            months.append((col, date.strftime("%b")))
        c = day["count"]
        delay = 1.55 + col * 0.028 + row * 0.016
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
{card_shell(W, h)}
<text class="r" {d(1.4)} x="42" y="50" font-family="{DISPLAY}" font-weight="700" font-size="26" fill="{BONE}">Every day on GitHub</text>
<text class="f" {d(1.4)} x="{right}" y="48" text-anchor="end" font-family="{MONO}" font-size="11" fill="{MUTED}">REFRESHED DAILY</text>
{''.join(cells)}
<g class="f" {d(2.8)}>{labels}
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
    h = 56
    body = f"""
{card_shell(W, h)}
<text class="r" {d(1.2)} x="28" y="36" font-family="{DISPLAY}" font-weight="700" font-size="22" fill="{BONE}">What I'm coding</text>
"""
    write("title-repos.svg", svg(W, h, body, ["display"], "What I'm coding", bottom=8))


def write_readme():
    """Keep README.md in lockstep with REPOS / LINKS so links cannot drift."""
    portfolio = LINKS[0]["href"]
    rows = []
    for i in range(0, len(REPOS), 2):
        pair = REPOS[i : i + 2]
        tags = "".join(
            f'<a href="{r["href"]}"><img src="./cards/repo-{r["name"].lower()}.svg" '
            f'width="49%" alt="{escape(r["name"])}: {escape(r["desc"])}" /></a>'
            for r in pair
        )
        rows.append(f'<p align="center">\n{tags}\n</p>')
    footer = " &nbsp;·&nbsp; ".join(
        f'<a href="{link["href"]}">{escape(link["label"])}</a>' for link in LINKS
    )
    md = f"""<!-- Cards are animated SVGs from scripts/render_readme_cards.py, refreshed daily
     by .github/workflows/update-profile-art.yml. Matched to parthdave.me.
     Keep image rows on one line with no spaces between <a>/<img> tags. -->
<p align="center">
<a href="{portfolio}"><img src="./cards/hero.svg" width="100%" alt="{escape(HERO_ALT)}" /></a>
</p>
<p align="center">
<img src="./cards/skills.svg" width="100%" alt="What I build with: languages, ML/AI, web/backend, and cloud/tools" />
</p>
<p align="center">
<img src="./cards/title-repos.svg" width="100%" alt="What I'm coding" />
</p>
{chr(10).join(rows)}
<p align="center">
<img src="./cards/heatmap.svg" width="100%" alt="Parth's GitHub contribution graph, refreshed daily" />
</p>
<p align="center">
<img src="./cards/activity.svg" width="100%" alt="Contributions in the last 12 months, with streak and active days" />
</p>
<p align="center">
{footer}
</p>
"""
    path = os.path.join(ROOT, "README.md")
    with open(path, "w") as f:
        f.write(md)
    print("wrote README.md")


if __name__ == "__main__":
    data = json.load(open(DATA))
    hero()
    skills()
    title_building()
    for i, repo in enumerate(REPOS):
        repo_card(i, repo)
    heatmap(data)
    activity(data)
    write_readme()
