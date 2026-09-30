# Reddit Assistant

A free, open-source kit for growing on Reddit **as yourself**: find questions you can
answer, get human-sounding drafts from any AI, post them by hand, and keep your
self-promotion honest.

It has two parts:

- **`skill/reddit-assistant/`**: an AI skill (instructions and references) that works with
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

**As a native skill:** copy `skill/reddit-assistant/` into your agent's skills folder
(for example `~/.claude/skills/` for Claude Code) or upload it as a Claude skill.
In a ChatGPT custom GPT or a Gemini Gem, paste `SKILL.md` into the instructions and add the
three `references/*.md` files as knowledge.

## What makes the drafts sound human

`skill/reddit-assistant/references/voice.md` tells the AI to open on the problem, use
real specifics, show a bit of honest feeling, vary sentence rhythm, and avoid marketing
and AI clichés. It is also told **not to invent experiences**. Where a personal touch
would help and you haven't given one, it leaves a `[slot]` for you. Fill those in with
the truth; they're what make a reply feel real.

## Tests

```bash
python -m unittest discover -s tests
```
