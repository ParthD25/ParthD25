#!/usr/bin/env python3
"""Refresh data/contributions.json from Parth's public GitHub contribution calendar.

Prefers the GraphQL `contributionsCollection` field when a token is present
(the workflow's default GITHUB_TOKEN is enough for a public profile). Falls
back to scraping the unauthenticated calendar HTML GitHub already serves, so
a local run needs no secrets.
"""
from __future__ import annotations

import datetime
import json
import os
import re
import sys
import urllib.error
import urllib.request

USERNAME = os.environ.get("GH_PROFILE_USER", "ParthD25")
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")
GRAPHQL_URL = "https://api.github.com/graphql"
CALENDAR_URL = f"https://github.com/users/{USERNAME}/contributions"
UA = "ParthD25-profile-readme/1.0"


def _request(url, *, data=None, headers=None, timeout=30):
    req = urllib.request.Request(url, data=data, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def fetch_days_graphql(token):
    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            weeks {
              contributionDays {
                date
                contributionCount
                contributionLevel
              }
            }
          }
        }
      }
    }
    """
    payload = json.dumps({"query": query, "variables": {"login": USERNAME}}).encode()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": UA,
    }
    raw = _request(GRAPHQL_URL, data=payload, headers=headers)
    body = json.loads(raw.decode())
    if body.get("errors"):
        raise RuntimeError(body["errors"])
    user = (body.get("data") or {}).get("user")
    if not user:
        raise RuntimeError("GraphQL returned no user")
    weeks = user["contributionsCollection"]["contributionCalendar"]["weeks"]
    level_map = {
        "NONE": 0,
        "FIRST_QUARTILE": 1,
        "SECOND_QUARTILE": 2,
        "THIRD_QUARTILE": 3,
        "FOURTH_QUARTILE": 4,
    }
    days = []
    for week in weeks:
        for day in week["contributionDays"]:
            days.append(
                {
                    "date": day["date"],
                    "count": int(day["contributionCount"]),
                    "level": level_map.get(day.get("contributionLevel"), 0),
                }
            )
    days.sort(key=lambda d: d["date"])
    if len(days) < 300:
        raise RuntimeError(f"GraphQL calendar too short: {len(days)} days")
    return days


def fetch_days_scrape():
    try:
        from bs4 import BeautifulSoup
    except ImportError as exc:
        raise SystemExit("beautifulsoup4 is required for the HTML fallback") from exc

    raw = _request(CALENDAR_URL, headers={"User-Agent": UA})
    soup = BeautifulSoup(raw, "html.parser")
    cells = soup.select("td.ContributionCalendar-day")
    if not cells:
        raise RuntimeError("no calendar cells found — GitHub markup may have changed")

    days = []
    for td in cells:
        date = td.get("data-date")
        if not date:
            continue
        td_id = td.get("id")
        tooltip_el = soup.find("tool-tip", attrs={"for": td_id}) if td_id else None
        text = tooltip_el.get_text(strip=True) if tooltip_el else ""
        if re.search(r"no contributions", text, re.I):
            count = 0
        else:
            match = re.match(r"(\d+)", text)
            count = int(match.group(1)) if match else 0
        days.append(
            {
                "date": date,
                "count": count,
                "level": int(td.get("data-level") or 0),
            }
        )
    days.sort(key=lambda d: d["date"])
    if len(days) < 300:
        raise RuntimeError(f"scraped calendar too short: {len(days)} days")
    return days


def compute_current_streak(days):
    idx = len(days) - 1
    if days[idx]["count"] == 0:
        idx -= 1
    streak = 0
    end_idx = idx
    while idx >= 0 and days[idx]["count"] > 0:
        streak += 1
        idx -= 1
    start_idx = idx + 1
    if streak == 0:
        return 0, None, None
    return streak, days[start_idx]["date"], days[end_idx]["date"]


def compute_longest_streak(days):
    longest = run = 0
    longest_start = longest_end = None
    run_start_idx = None
    for i, day in enumerate(days):
        if day["count"] > 0:
            if run == 0:
                run_start_idx = i
            run += 1
            if run > longest:
                longest = run
                longest_start = days[run_start_idx]["date"]
                longest_end = days[i]["date"]
        else:
            run = 0
    return longest, longest_start, longest_end


def build_data(days):
    total = sum(d["count"] for d in days)
    active_days = sum(1 for d in days if d["count"] > 0)
    best = max(days, key=lambda d: d["count"])
    cur_len, cur_start, cur_end = compute_current_streak(days)
    long_len, long_start, long_end = compute_longest_streak(days)

    monthly = {}
    for d in days:
        key = d["date"][:7]
        monthly[key] = monthly.get(key, 0) + d["count"]
    monthly_list = [{"month": k, "total": v} for k, v in sorted(monthly.items())]

    return {
        "username": USERNAME,
        "generated_at": datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "range": {"start": days[0]["date"], "end": days[-1]["date"]},
        "total_contributions": total,
        "active_days": active_days,
        "avg_per_active_day": round(total / active_days, 1) if active_days else 0,
        "current_streak": {"length": cur_len, "start": cur_start, "end": cur_end},
        "longest_streak": {"length": long_len, "start": long_start, "end": long_end},
        "best_day": {"date": best["date"], "count": best["count"]},
        "monthly": monthly_list,
        "days": days,
    }


def fetch_days():
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    errors = []
    if token:
        try:
            days = fetch_days_graphql(token)
            print(f"fetched {len(days)} days via GraphQL")
            return days
        except (RuntimeError, urllib.error.URLError, json.JSONDecodeError, KeyError) as exc:
            errors.append(f"graphql: {exc}")
            print(f"GraphQL fetch failed ({exc}); falling back to HTML scrape", file=sys.stderr)
    try:
        days = fetch_days_scrape()
        print(f"fetched {len(days)} days via HTML scrape")
        return days
    except (RuntimeError, urllib.error.URLError) as exc:
        errors.append(f"scrape: {exc}")
        raise SystemExit("could not load contribution calendar: " + " | ".join(errors)) from exc


if __name__ == "__main__":
    days = fetch_days()
    data = build_data(days)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    print(
        f"wrote {OUT_PATH}: {data['total_contributions']} contributions, "
        f"current streak {data['current_streak']['length']}, "
        f"longest streak {data['longest_streak']['length']}"
    )
