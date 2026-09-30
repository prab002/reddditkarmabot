#!/usr/bin/env python3
"""redditkit: a read-only Reddit helper for the reddit-assistant skill.

It finds threads, reads subreddit rules, builds prompts for any AI, and keeps
a local log of your helpful vs. promotional activity. It never logs in, posts,
comments, votes or sends messages. You do that part yourself.

Python 3.11+, standard library only.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import tomllib
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT / "skill" / "reddit-assistant"
DEFAULT_CONFIG = ROOT / "sites.toml"
DEFAULT_LOG = ROOT / "data" / "activity.jsonl"
DEFAULT_MEMORY = ROOT / "memory" / "LEARNINGS.md"
MEMORY_SECTIONS = {"pref": "Preferences", "sub": "Subreddits", "worked": "What worked",
                   "didnt": "What didn't", "env": "Environment"}
USER_AGENT = "redditkit/0.1 (read-only helper; personal use)"
TASKS = ("reply", "post", "mod-message", "pick-subs", "review")
PROMO_RATIO = 9  # helpful actions per promotional one


# ---------------------------------------------------------------- config ---

def load_config(path: Path) -> dict:
    if not path.exists():
        sys.exit(f"Config not found: {path}\nCopy sites.example.toml to sites.toml and edit it.")
    with path.open("rb") as f:
        return tomllib.load(f)


def get_site(config: dict, name: str | None) -> dict:
    sites = config.get("site", {})
    if not sites:
        sys.exit("No [site.*] entries in config.")
    if name is None:
        if len(sites) == 1:
            name = next(iter(sites))
        else:
            sys.exit(f"Pick a site with --site. Available: {', '.join(sites)}")
    if name not in sites:
        sys.exit(f"Unknown site '{name}'. Available: {', '.join(sites)}")
    return {"key": name, **sites[name]}


# ---------------------------------------------------------------- reddit ---

def fetch_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        if e.code == 429:
            sys.exit("Reddit rate-limited this request (429). Wait a minute and try again.")
        if e.code in (403, 404):
            sys.exit(f"Reddit returned {e.code} for {url} (private, banned, or blocked).")
        raise
    except urllib.error.URLError as e:
        sys.exit(f"Could not reach Reddit: {e.reason}")


def parse_rules(data: dict) -> list[dict]:
    return [
        {"name": r.get("short_name", ""), "description": (r.get("description") or "").strip()}
        for r in data.get("rules", [])
    ]


def get_rules(sub: str) -> list[dict]:
    return parse_rules(fetch_json(f"https://www.reddit.com/r/{sub}/about/rules.json"))


def format_rules(sub: str, rules: list[dict]) -> str:
    if not rules:
        return f"r/{sub}: no rules listed (check the sidebar and wiki anyway)."
    lines = [f"r/{sub} rules:"]
    for i, r in enumerate(rules, 1):
        lines.append(f"{i}. {r['name']}")
        if r["description"]:
            lines.extend(f"   {line}" for line in r["description"].splitlines() if line.strip())
    return "\n".join(lines)


def parse_listing(data: dict) -> list[dict]:
    posts = []
    for child in data.get("data", {}).get("children", []):
        p = child.get("data", {})
        posts.append({
            "id": p.get("id"),
            "sub": p.get("subreddit"),
            "title": p.get("title", ""),
            "score": p.get("score", 0),
            "comments": p.get("num_comments", 0),
            "created": p.get("created_utc", 0),
            "url": "https://www.reddit.com" + p.get("permalink", ""),
            "locked": p.get("locked", False),
            "archived": p.get("archived", False),
        })
    return posts


def search_sub(sub: str, query: str, limit: int) -> list[dict]:
    qs = urllib.parse.urlencode({
        "q": query, "restrict_sr": 1, "sort": "new", "t": "week", "limit": limit,
    })
    return parse_listing(fetch_json(f"https://www.reddit.com/r/{sub}/search.json?{qs}"))


def thread_json_url(url: str) -> str:
    parts = urllib.parse.urlsplit(url.strip())
    path = parts.path.rstrip("/")
    if not path.endswith(".json"):
        path += ".json"
    return urllib.parse.urlunsplit(("https", "www.reddit.com", path, "limit=10&sort=top", ""))


def parse_thread(data: list, max_comments: int = 8) -> dict:
    post = data[0]["data"]["children"][0]["data"]
    comments = []
    for c in data[1]["data"]["children"]:
        if c.get("kind") != "t1":
            continue
        d = c["data"]
        body = (d.get("body") or "").strip()
        if body and body not in ("[deleted]", "[removed]"):
            comments.append({"author": d.get("author"), "score": d.get("score", 0), "body": body})
        if len(comments) >= max_comments:
            break
    return {
        "sub": post.get("subreddit"),
        "title": post.get("title", ""),
        "body": (post.get("selftext") or "").strip(),
        "score": post.get("score", 0),
        "url": "https://www.reddit.com" + post.get("permalink", ""),
        "comments": comments,
    }


def format_thread(t: dict) -> str:
    out = [f"Subreddit: r/{t['sub']}", f"URL: {t['url']}", f"Title: {t['title']}", ""]
    out.append(t["body"] or "(no body text)")
    if t["comments"]:
        out += ["", "Top comments so far:"]
        for c in t["comments"]:
            out.append(f"- [{c['score']} pts] {c['body'][:600]}")
    else:
        out += ["", "No comments yet."]
    return "\n".join(out)


# ------------------------------------------------------------------- log ---

def read_log(path: Path) -> list[dict]:
    if not path.exists():
        return []
    entries = []
    for line in path.read_text().splitlines():
        if line.strip():
            entries.append(json.loads(line))
    return entries


def append_log(path: Path, entry: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(entry) + "\n")


def ratio_status(entries: list[dict], site: str | None, days: int, now: dt.datetime | None = None) -> dict:
    now = now or dt.datetime.now(dt.timezone.utc)
    cutoff = now - dt.timedelta(days=days)
    helpful = promo = 0
    for e in entries:
        if dt.datetime.fromisoformat(e["time"]) < cutoff:
            continue
        # Helpful comments build your reputation for every site; promos count per site.
        if e["kind"] == "helpful":
            helpful += 1
        elif e["kind"] == "promo" and (site is None or e.get("site") == site):
            promo += 1
    allowed = helpful // PROMO_RATIO - promo
    return {"days": days, "helpful": helpful, "promo": promo, "promo_allowed_now": max(allowed, 0)}


def format_ratio(r: dict, site: str | None) -> str:
    scope = f"site '{site}'" if site else "all sites"
    lines = [
        f"Last {r['days']} days ({scope}): {r['helpful']} helpful, {r['promo']} promo.",
    ]
    if r["promo_allowed_now"] > 0:
        lines.append(f"OK to include your link {r['promo_allowed_now']} more time(s), where it truly fits.")
    else:
        needed = (r["promo"] + 1) * PROMO_RATIO - r["helpful"]
        lines.append(f"No links for now: about {needed} more helpful replies before the next one.")
    return "\n".join(lines)


# ---------------------------------------------------------------- prompt ---

def read_skill(memory: Path | None = DEFAULT_MEMORY) -> str:
    parts = [(SKILL_DIR / "SKILL.md").read_text()]
    for name in ("voice.md", "playbook.md", "templates.md"):
        p = SKILL_DIR / "references" / name
        parts.append(f"\n\n===== references/{name} =====\n\n{p.read_text()}")
    if memory and memory.exists():
        parts.append(f"\n\n===== memory/LEARNINGS.md =====\n\n{memory.read_text()}")
    return "".join(parts)


def add_learning(path: Path, section: str, text: str, today: dt.date | None = None) -> None:
    """Append a dated bullet at the end of a '## <section>' block, creating it if needed."""
    heading = f"## {MEMORY_SECTIONS[section]}"
    bullet = f"- {(today or dt.date.today()).isoformat()}: {text.strip()}"
    lines = path.read_text().splitlines() if path.exists() else ["# Learnings", ""]
    if heading not in lines:
        lines += ["", heading, "", bullet]
    else:
        start = lines.index(heading) + 1
        end = next((i for i in range(start, len(lines)) if lines[i].startswith("## ")), len(lines))
        insert_at = end
        while insert_at > start + 1 and not lines[insert_at - 1].strip():
            insert_at -= 1
        lines.insert(insert_at, bullet)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def format_site(site: dict) -> str:
    lines = [f"Name: {site.get('name', site['key'])}", f"URL: {site.get('url', '')}"]
    for key, label in (("what", "What it is"), ("audience", "Who it's for"),
                       ("my_story", "My real story with it (safe to use)"),
                       ("facts", "Facts I can back up")):
        val = site.get(key)
        if isinstance(val, list):
            val = "\n".join(f"- {v}" for v in val)
        if val:
            lines.append(f"{label}:\n{val}")
    if site.get("pages"):
        lines.append("Pages I can link when they directly answer a question:")
        for page in site["pages"]:
            lines.append(f"- {page.get('title', '')}: {page.get('url', '')}")
    return "\n".join(lines)


def build_prompt(task: str, site: dict, *, thread: str | None = None, rules: str | None = None,
                 ratio: str | None = None, extra: str | None = None, persona: str | None = None,
                 length: str = "auto", memory: Path | None = DEFAULT_MEMORY) -> str:
    sections = [
        "You are using the following skill. Follow it exactly.\n\n" + read_skill(memory),
        "\n\n===== CONTEXT =====",
        f"\nTask: {task}",
    ]
    if length != "auto":
        sections.append(f"Length: {length} (short = 2-4 sentences; long = full steps, see 'Length' in the skill)")
    if persona:
        sections.append(f"\nAbout me (the person posting):\n{persona}")
    sections.append(f"\nMy site:\n{format_site(site)}")
    if ratio:
        sections.append(f"\nMy self-promotion ratio:\n{ratio}")
    if rules:
        sections.append(f"\n{rules}")
    if thread:
        sections.append(f"\nThread:\n{thread}")
    if extra:
        sections.append(f"\nExtra notes from me:\n{extra}")
    sections.append("\nWrite the draft now, in the output format from the skill.")
    return "\n".join(sections)


def call_ai(prompt: str) -> str:
    """Send the prompt to any OpenAI-compatible chat endpoint (OpenAI, Ollama,
    OpenRouter, Groq, LM Studio, Anthropic's compatibility endpoint, ...)."""
    base = os.environ.get("AI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.environ.get("AI_MODEL")
    if not model:
        sys.exit("Set AI_MODEL (and AI_BASE_URL / AI_API_KEY) to use --send. See README.")
    headers = {"Content-Type": "application/json"}
    if key := os.environ.get("AI_API_KEY"):
        headers["Authorization"] = f"Bearer {key}"
    body = json.dumps({"model": model, "messages": [{"role": "user", "content": prompt}]}).encode()
    req = urllib.request.Request(f"{base}/chat/completions", data=body, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as e:
        sys.exit(f"AI request failed ({e.code}): {e.read().decode(errors='replace')[:500]}")
    except urllib.error.URLError as e:
        sys.exit(f"Could not reach AI endpoint {base}: {e.reason}")
    return data["choices"][0]["message"]["content"]


# -------------------------------------------------------------- commands ---

def cmd_rules(args):
    print(format_rules(args.sub, get_rules(args.sub)))


def cmd_threads(args):
    config = load_config(args.config)
    site = get_site(config, args.site)
    subs = args.subs or site.get("subreddits", [])
    keywords = args.keywords or site.get("keywords", [])
    if not subs or not keywords:
        sys.exit("Need subreddits and keywords (in sites.toml or via --subs/--keywords).")
    seen, found = set(), []
    for sub in subs:
        for kw in keywords:
            for p in search_sub(sub, kw, args.limit):
                if p["id"] in seen or p["locked"] or p["archived"]:
                    continue
                seen.add(p["id"])
                found.append(p)
    # Fewer comments = more chance your answer gets seen and is still needed.
    found.sort(key=lambda p: (p["comments"] > 15, -p["created"]))
    if not found:
        print("No matching threads this week. Try broader keywords.")
        return
    now = dt.datetime.now(dt.timezone.utc).timestamp()
    for p in found[: args.max]:
        age_h = int((now - p["created"]) / 3600)
        print(f"r/{p['sub']:<14} {age_h:>4}h  {p['comments']:>3}c  {p['score']:>4}pts  {p['title'][:90]}")
        print(f"{'':16}{p['url']}")


def cmd_prompt(args):
    config = load_config(args.config)
    site = get_site(config, args.site)
    thread_text = rules_text = None
    sub = args.sub
    if args.thread:
        t = parse_thread(fetch_json(thread_json_url(args.thread)))
        thread_text, sub = format_thread(t), sub or t["sub"]
    elif args.thread_file:
        thread_text = Path(args.thread_file).read_text()
    if sub and not args.no_rules:
        rules_text = format_rules(sub, get_rules(sub))
    ratio = format_ratio(ratio_status(read_log(args.log), site["key"], 7), site["key"])
    prompt = build_prompt(args.task, site, thread=thread_text, rules=rules_text, ratio=ratio,
                          extra=args.notes, persona=config.get("me", {}).get("about"),
                          length=args.length, memory=args.memory)
    if args.send:
        print(call_ai(prompt))
    elif args.out:
        Path(args.out).write_text(prompt)
        print(f"Prompt written to {args.out}. Paste it into any AI chat.")
    else:
        print(prompt)


def cmd_log(args):
    entry = {
        "time": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "kind": args.kind, "sub": args.sub.removeprefix("r/"), "site": args.site, "note": args.note,
    }
    if args.kind == "promo" and not args.site:
        sys.exit("Promo entries need --site so the ratio is tracked per site.")
    append_log(args.log, entry)
    print(f"Logged {args.kind} in r/{entry['sub']}.")
    print(format_ratio(ratio_status(read_log(args.log), args.site, 7), args.site))


def cmd_learn(args):
    add_learning(args.memory, args.section, args.text)
    print(f"Added to {MEMORY_SECTIONS[args.section]} in {args.memory}.")
    print("Commit and push it so the next session picks it up.")


def cmd_ratio(args):
    print(format_ratio(ratio_status(read_log(args.log), args.site, args.days), args.site))


def main(argv=None):
    ap = argparse.ArgumentParser(prog="redditkit", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    ap.add_argument("--log", type=Path, default=DEFAULT_LOG)
    ap.add_argument("--memory", type=Path, default=DEFAULT_MEMORY)
    sp = ap.add_subparsers(dest="cmd", required=True)

    p = sp.add_parser("rules", help="show a subreddit's rules")
    p.add_argument("sub")
    p.set_defaults(func=cmd_rules)

    p = sp.add_parser("threads", help="find fresh threads matching a site's topics")
    p.add_argument("--site")
    p.add_argument("--subs", nargs="+")
    p.add_argument("--keywords", nargs="+")
    p.add_argument("--limit", type=int, default=10, help="results per search")
    p.add_argument("--max", type=int, default=25, help="threads to show")
    p.set_defaults(func=cmd_threads)

    p = sp.add_parser("prompt", help="build a ready-to-paste prompt for any AI")
    p.add_argument("task", choices=TASKS)
    p.add_argument("--site")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--thread", help="Reddit thread URL")
    g.add_argument("--thread-file", help="text file with a pasted thread")
    p.add_argument("--sub", help="target subreddit (for post / mod-message)")
    p.add_argument("--notes", help="extra context for the AI")
    p.add_argument("--no-rules", action="store_true", help="skip fetching subreddit rules")
    p.add_argument("--length", choices=("auto", "short", "long"), default="auto",
                   help="short = 2-4 sentences (default for karma); auto lets the skill decide")
    p.add_argument("--out", help="write the prompt to a file instead of stdout")
    p.add_argument("--send", action="store_true",
                   help="send to an OpenAI-compatible API (AI_BASE_URL, AI_MODEL, AI_API_KEY)")
    p.set_defaults(func=cmd_prompt)

    p = sp.add_parser("log", help="record something you posted")
    p.add_argument("kind", choices=("helpful", "promo"))
    p.add_argument("sub")
    p.add_argument("note", nargs="?", default="")
    p.add_argument("--site")
    p.set_defaults(func=cmd_log)

    p = sp.add_parser("learn", help="save a learning to memory/LEARNINGS.md")
    p.add_argument("text")
    p.add_argument("--section", choices=tuple(MEMORY_SECTIONS), default="worked",
                   help="pref, sub, worked (default), didnt, env")
    p.set_defaults(func=cmd_learn)

    p = sp.add_parser("ratio", help="show your helpful vs. promo balance")
    p.add_argument("--site")
    p.add_argument("--days", type=int, default=7)
    p.set_defaults(func=cmd_ratio)

    args = ap.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
