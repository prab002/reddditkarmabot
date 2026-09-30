# Social Assistant (Reddit, X, Threads)

A free, open-source kit for growing on Reddit **as yourself**: find questions you can
answer, get human-sounding drafts from any AI, post them by hand, and keep your
self-promotion honest.

It has two parts:

- **`skill/social-assistant/`**: an AI skill (instructions and references) that works with
  Claude, ChatGPT, Gemini, a local model, or anything that reads text.
- **`tools/redditkit.py`**: a small read-only helper that finds threads, pulls subreddit
  rules, builds the prompt for you, and tracks your helpful-to-promo ratio.

**It never posts, comments, votes, or logs into Reddit.** You copy the draft, edit it,
and post it yourself. That's deliberate: automated posting and karma farming get
accounts suspended and domains banned site-wide.

## Setup (2 minutes)

Needs Python 3.11+. No packages to install.

```bash
cp sites.example.toml sites.toml
# edit sites.toml: add each of your sites, your real story, and the facts you can back up
```

## Daily use (15–20 min)

```bash
# 1. Find fresh questions matching your site's topics
python tools/redditkit.py threads --site freemac

# 2. Build a prompt for one of them and paste it into any AI
python tools/redditkit.py prompt reply --site freemac --thread https://www.reddit.com/r/mac/comments/...
#    (add --out draft-prompt.txt to save it to a file instead)

# 3. Edit the draft, fill the [slots], post it yourself, then log it
python tools/redditkit.py log helpful mac "System Data snapshots answer"
python tools/redditkit.py log promo SideProject "launch post" --site freemac

# 4. Check whether you've earned a link
python tools/redditkit.py ratio --site freemac
```

Other tasks:

```bash
python tools/redditkit.py rules macapps                                      # read a sub's rules
python tools/redditkit.py prompt post --site freemac --sub SideProject       # maker/launch post
python tools/redditkit.py prompt mod-message --site freemac --sub macapps    # ask mods to approve
python tools/redditkit.py prompt pick-subs --site freemac --no-rules         # suggest subreddits
python tools/redditkit.py prompt review --site freemac --thread-file my-draft.txt --no-rules
```

## X and Threads

The same skill drafts for X and Instagram Threads. Paste the post you want to reply to
(or your own text to repurpose) into a file and use `--platform`:

```bash
# Turn a Reddit answer that did well into an X post, an X thread and a Threads post
python tools/redditkit.py prompt repurpose --platform x --site freemac --thread-file my-answer.txt

# A how-to thread for X, or a relatable tip for Threads
python tools/redditkit.py prompt thread --platform x --site freemac --notes "System Data snapshots fix"
python tools/redditkit.py prompt post --platform threads --site freemac --notes "256GB Mac full"

# Reply to someone's X post (saved in post.txt)
python tools/redditkit.py prompt reply --platform x --site freemac --thread-file post.txt

python tools/redditkit.py log helpful x "snapshots tip post"
```

Platform guides: `skill/social-assistant/references/platforms/x.md` and `threads.md`.
Key points: links go in a reply to your own post or in your bio, not the main post;
about 4 in 5 posts should be pure tips; replies to bigger accounts grow a small account fastest.
Schedule posts with the apps' own schedulers; nothing here posts for you.

## Your weekly rhythm: 3 posts, lots of comments

Growth on a new account comes mostly from **comments**. Your own posts are 3 a week per platform.

**Daily (15–20 min): comments**
```bash
python tools/redditkit.py today          # progress vs. targets (Reddit 5, X 10, Threads 5)
# paste 5-10 posts you want to reply to into posts.txt, separated by lines of ---
python tools/redditkit.py prompt batch-reply --platform x --site freemac --thread-file posts.txt
# post the replies you like by hand, then log each one
python tools/redditkit.py log helpful x "reply to @someone about snapshots"
```

**Weekly (10 min): plan your 3 posts**
```bash
python tools/redditkit.py prompt week --platform x --site freemac --no-rules --out week-prompt.txt
# paste into any AI, save its answer as queue/2026-w41.md
python tools/redditkit.py check queue/2026-w41.md
```
`check` enforces character limits (X counts links as 23), at most one post per platform
per week linking your sites, no links in the main post, no duplicate text across
platforms, and your daily and weekly limits (`[schedule]` in `sites.toml`). Change `draft` to
`approved` on the posts you like, paste them into X's or Threads' own scheduler, and mark
them `posted`.

Each week includes a **community post** ("drop a screenshot of your storage bar and I'll tell
you what's eating it"). Answer every reply to it; that's how followers turn into a community.

## Comment length

Drafts default to **short comments (2–4 sentences)**, which earn the most karma.
They get longer only when the question needs steps or commands. Force it either way:

```bash
python tools/redditkit.py prompt reply --site freemac --thread <url> --length short
python tools/redditkit.py prompt reply --site freemac --thread <url> --length long
```

## Memory: getting smarter each session

`memory/LEARNINGS.md` records what works for you: your preferences, subreddit quirks,
which comments got karma, and what got removed. Every `prompt` includes it, and
`CLAUDE.md` tells Claude Code to read it at the start of each session and update it at the end.

```bash
python tools/redditkit.py learn "r/macbookair short storage reply got +40" --section worked
python tools/redditkit.py learn "r/MacOS removes posts without flair" --section sub
python tools/redditkit.py learn "prefer no emojis" --section pref
git add memory && git commit -m "Update learnings" && git push
```

Sections: `pref`, `sub`, `worked` (default), `didnt`, `env`.

## Plugging in an AI

**Copy and paste (works with any AI):** run `prompt ...` and paste the output into any chat.

**Straight to an API:** `--send` calls any OpenAI-compatible endpoint and prints the draft:

```bash
# OpenAI
export AI_BASE_URL=https://api.openai.com/v1 AI_API_KEY=sk-... AI_MODEL=gpt-4o
# Local Ollama (free)
export AI_BASE_URL=http://localhost:11434/v1 AI_MODEL=llama3.1
# OpenRouter (Claude, Gemini, etc.)
export AI_BASE_URL=https://openrouter.ai/api/v1 AI_API_KEY=... AI_MODEL=anthropic/claude-sonnet-4.5

python tools/redditkit.py prompt reply --site freemac --thread <url> --send
```

**As a native skill:** copy `skill/social-assistant/` into your agent's skills folder
(for example `~/.claude/skills/` for Claude Code) or upload it as a Claude skill.
In a ChatGPT custom GPT or a Gemini Gem, paste `SKILL.md` into the instructions and add the
three `references/*.md` files as knowledge.

## What makes the drafts sound human

`skill/social-assistant/references/voice.md` tells the AI to open on the problem, use
real specifics, show a bit of honest feeling, vary sentence rhythm, and avoid marketing
and AI clichés. It is also told **not to invent experiences**. Where a personal touch
would help and you haven't given one, it leaves a `[slot]` for you. Fill those in with
the truth; they're what make a reply feel real.

## Tests

```bash
python -m unittest discover -s tests
```
