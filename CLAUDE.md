# Reddit Assistant repo

A human-in-the-loop kit for growing on Reddit as yourself. The AI drafts, the user posts by hand.

## Start of every session

1. Read `memory/LEARNINGS.md`. It holds the user's preferences and what has worked so far,
   and it overrides the skill's defaults.
2. For any Reddit drafting, follow `skill/reddit-assistant/SKILL.md` and its `references/`.

## During the session

- When the user pastes a thread or screenshot, draft with the skill (short comment by default).
- Never post, vote or message on Reddit for the user, and never present their own site as
  something they found. See the hard rules in `SKILL.md`.

## End of session (or when something new is learned)

- Add new learnings to `memory/LEARNINGS.md` under the right section, dated, one line each.
  Good learnings: a preference the user stated, a comment that got good karma, a removal
  and why, a subreddit rule or quirk.
- Commit and push so the next session sees them.

## Code

- `tools/redditkit.py`: stdlib-only CLI. `threads`, `rules`, `prompt`, `log`, `ratio`, `learn`.
- Tests: `python -m unittest discover -s tests`
