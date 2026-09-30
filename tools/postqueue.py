"""Weekly post queue: parse and check your planned posts before you schedule them.

Queue files are Markdown you can read and edit by hand:

    ### 2026-10-05 09:00 | x | draft
    Your Mac's "System Data" jumped 60GB overnight?
    ---
    Full guide (my site): https://free-mac.online/

Header: local date and time | platform (x or threads) | status.
Status is draft, approved, skip or posted (you mark it after posting).
Parts are separated by a line containing only ---. The first part is the post,
and each later part goes in as a reply to your own previous part (a thread).

Nothing here posts. You copy approved posts into X's or Threads' own scheduler.
"""

from __future__ import annotations

import datetime as dt
import re
import urllib.parse
from dataclasses import dataclass
from pathlib import Path

LIMITS = {"x": 280, "threads": 500}
STATUSES = ("draft", "approved", "skip", "posted")
URL_RE = re.compile(r"https?://\S+")
X_URL_LEN = 23  # X counts every link as 23 characters
MAX_PROMO_PER_WEEK = 1  # posts linking your sites, per platform per week
DEFAULT_MAX_PER_DAY = 2
DEFAULT_POSTS_PER_WEEK = 3


@dataclass
class Entry:
    when: dt.datetime
    platform: str
    status: str
    parts: list[str]
    line: int  # 0-based index of the header line in the file


# ------------------------------------------------------------------ parse ---

def parse_queue(text: str) -> list[Entry]:
    lines = text.splitlines()
    heads = [i for i, l in enumerate(lines) if l.startswith("### ")]
    entries = []
    for n, i in enumerate(heads):
        fields = [f.strip() for f in lines[i][4:].split("|")]
        if len(fields) != 3:
            raise ValueError(f"line {i + 1}: header must be '### <date time> | <platform> | <status>'")
        when_s, platform, status = fields
        try:
            when = dt.datetime.strptime(when_s, "%Y-%m-%d %H:%M")
        except ValueError:
            raise ValueError(f"line {i + 1}: time must look like 2026-10-05 09:00") from None
        platform = platform.lower()
        if platform not in LIMITS:
            raise ValueError(f"line {i + 1}: platform must be x or threads")
        if status.startswith("posted"):
            status = "posted"
        elif status not in STATUSES:
            raise ValueError(f"line {i + 1}: status must be draft, approved, skip or posted")
        end = heads[n + 1] if n + 1 < len(heads) else len(lines)
        body = "\n".join(lines[i + 1:end])
        parts = [p.strip() for p in re.split(r"(?m)^---\s*$", body) if p.strip()]
        entries.append(Entry(when, platform, status, parts, i))
    return entries


# ------------------------------------------------------------------ check ---

def x_length(text: str) -> int:
    return len(URL_RE.sub("x" * X_URL_LEN, text))


def part_length(platform: str, text: str) -> int:
    return x_length(text) if platform == "x" else len(text)


def check_queue(entries: list[Entry], site_urls: list[str], now: dt.datetime | None = None,
                max_per_day: int = DEFAULT_MAX_PER_DAY,
                posts_per_week: int = DEFAULT_POSTS_PER_WEEK) -> tuple[list[str], list[str]]:
    """Return (errors, warnings). Errors block publishing."""
    now = now or dt.datetime.now()
    errors, warnings = [], []
    live = [e for e in entries if e.status in ("draft", "approved", "posted")]
    hosts = [urllib.parse.urlsplit(u).netloc.lower() for u in site_urls if u]

    def links_site(text: str) -> bool:
        return any(h and h in text.lower() for h in hosts)

    for e in live:
        where = f"line {e.line + 1} ({e.platform} {e.when:%a %H:%M})"
        if not e.parts:
            errors.append(f"{where}: empty post")
            continue
        for k, part in enumerate(e.parts, 1):
            n = part_length(e.platform, part)
            if n > LIMITS[e.platform]:
                errors.append(f"{where}: part {k} is {n} chars, limit {LIMITS[e.platform]}")
        if URL_RE.search(e.parts[0]):
            warnings.append(f"{where}: link in the main post cuts reach; move it to a later part")
        if e.status == "approved" and e.when < now - dt.timedelta(hours=12):
            warnings.append(f"{where}: approved but its time passed over 12h ago; reschedule or mark skip")

    promo_weeks: dict[tuple[str, int, int], int] = {}
    for e in live:
        if any(links_site(p) for p in e.parts):
            key = (e.platform, *e.when.isocalendar()[:2])
            promo_weeks[key] = promo_weeks.get(key, 0) + 1
    for (platform, _, week), count in sorted(promo_weeks.items()):
        if count > MAX_PROMO_PER_WEEK:
            errors.append(f"{count} {platform} posts in week {week} link your sites; keep it to "
                          f"{MAX_PROMO_PER_WEEK} so the feed stays useful and doesn't read as spam")

    per_day: dict[tuple[str, dt.date], int] = {}
    for e in live:
        key = (e.platform, e.when.date())
        per_day[key] = per_day.get(key, 0) + 1
    for (platform, day), count in sorted(per_day.items()):
        if count > max_per_day:
            errors.append(f"{count} {platform} posts on {day}; max is {max_per_day} per day")

    per_week: dict[tuple[str, int, int], int] = {}
    for e in live:
        key = (e.platform, *e.when.isocalendar()[:2])
        per_week[key] = per_week.get(key, 0) + 1
    for (platform, year, week), count in sorted(per_week.items()):
        if count > posts_per_week:
            warnings.append(f"{count} {platform} posts in week {week}; your plan is {posts_per_week}. "
                            "Put the extra energy into comments instead")

    seen: dict[str, Entry] = {}
    for e in live:
        key = re.sub(r"\W+", " ", e.parts[0].lower()).strip() if e.parts else ""
        if key in seen:
            warnings.append(f"line {e.line + 1}: same text as line {seen[key].line + 1}; rewrite it "
                            "for each platform")
        else:
            seen[key] = e
    return errors, warnings
