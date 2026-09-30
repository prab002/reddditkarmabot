# Playbook

## How karma filters actually work

Most "your post was removed" messages come from a subreddit's AutoModerator
config, usually a minimum account age plus a minimum comment karma
(often 10–100). **Comment karma** is what counts almost everywhere, and it's
easiest to earn by answering questions in busy, friendly subreddits.

Fastest honest route: 3–5 genuinely good answers a day in subreddits where you
know the topic. A good answer in an active thread often earns 5–50 karma.

## Daily routine (15–20 minutes)

1. `python tools/redditkit.py threads --site <site>` lists fresh questions matching your topics.
2. Pick 3–5 threads you can really answer. Skip anything already well answered.
3. `python tools/redditkit.py prompt reply --site <site> --thread <url>` builds a prompt. Paste it into any AI.
4. Edit the draft: fill the `[slots]` and cut anything you wouldn't say out loud.
5. Post it by hand. Reply if someone answers you.
6. `python tools/redditkit.py log helpful <sub> "note"`, and log `promo` when you linked your own stuff.
7. Check back once later in the day for replies. Conversations earn more than one-off comments.

## A realistic first week

| Day | Focus |
|-----|-------|
| 1 | Run `rules` on your target subs. Note karma, age and self-promo limits. Answer 3 threads, no links. |
| 2–4 | 3–5 answers a day, no links. Reply to anyone who responds. |
| 5 | Message the mods of your main target sub (see templates): "I'm the dev, what's your policy?" |
| 6 | If your ratio is fine and the rules allow it, make **one** maker post in the most fitting sub (r/SideProject, r/macapps if the mods approved it). |
| 7 | Stay in that post's comments. Take feedback. No second promo post this week. |

Expect somewhere around 50–200 comment karma by the end of week one if the
answers are good. That's enough to clear most filters. Traffic comes from the
occasional well-placed link in a thread where it truly answers the question.
Those links keep sending visitors for months through search.

## Self-promotion rules of thumb

- **9:1**: nine helpful contributions for each one that promotes your stuff.
- **One post, one sub, then wait.** Space promo posts for the same site out by at least a week,
  and rewrite each one for its community.
- **Read the sidebar first.** Many subs have a weekly self-promo thread or a
  "Self-promotion Saturday". Use those instead of fighting the rule.
- **Several sites:** each site gets its own ratio budget. Don't link three of
  your sites in one comment, and don't link a site that isn't the best answer.

## Subreddit ideas by topic

Always check the current rules with `redditkit.py rules <sub>` first.

- **Mac utilities / guides:** r/mac, r/MacOS, r/macapps (dev posts usually need mod approval),
  r/applehelp, r/MacSoftware
- **Maker / launch posts:** r/SideProject, r/alphaandbetausers, r/IMadeThis, r/roastmystartup (for harsh feedback)
- **Web tools in general:** r/InternetIsBeautiful (strict, high bar), r/software, r/productivity

## If a post gets removed

1. Read the removal reason and the rule it cites.
2. Don't repost. Don't try a new account.
3. Send one polite mod message (template in `templates.md`) asking what to change.
4. Wait for the answer, or at least 48 hours.
