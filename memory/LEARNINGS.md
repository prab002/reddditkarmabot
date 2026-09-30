# Learnings

What we've learned works (and doesn't) for this user on Reddit. The skill reads this
before drafting, and it overrides the skill's defaults (never the hard rules).

Add entries with `python tools/redditkit.py learn "..."`, or edit by hand. Newest at the bottom
of each section. Commit and push after each session so the next session picks it up.

## Preferences

- 2026-09-30: Current goal is earning comment karma, so default to short comments (2–4 sentences). Extend only when the question needs steps.
- 2026-09-30: Most comments should have no link. Traffic comes from the Reddit bio and the custom feed "Mac Help & Storage Fixes" shown on the profile.
- 2026-09-30: When free-mac.online is linked, use the casual origin-story disclosure, not "full disclosure". Never present it as found on Google.

## Subreddits

- 2026-09-30: Targets: r/mac, r/MacOS, r/applehelp, r/MacSoftware, r/macapps (dev posts need mod approval), r/macbookair, r/macbookpro, r/MacOSBeta.
- 2026-09-30: r/macbookair gets lots of "256GB is full" posts from new M-series owners. Good karma threads.
- 2026-09-30: r/MacOS: sudden overnight storage drops are usually Time Machine local snapshots or a staged macOS update; for Adobe users also check Media Cache (~/Library/Application Support/Adobe/Common)

## What worked

<!-- e.g. "2026-10-02: r/mac 'System Data 90GB' reply, short + tmutil command, +34 karma" -->

## What didn't

- 2026-09-30: Threads a day old with 24+ comments are too late to become the top answer. Aim for threads under 3 hours old with fewer than 10 comments.

## Environment

- 2026-09-30: The Claude Code cloud sandbox blocks reddit.com and free-mac.online, so `threads`, `rules` and `--thread` only work on the user's own machine (or after allowing those hosts in the environment's network settings). In the sandbox, work from screenshots or pasted text.
