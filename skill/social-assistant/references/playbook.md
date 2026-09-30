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

## Profile link: traffic without promo comments

Set this up on day 1. It's the biggest traffic source that costs no promo budget.

1. **Bio**: one line with the link, e.g. "I make free Mac utilities → free-mac.online".
2. **Pinned profile post**: a short, honest "what I build and why" post with links to
   each site. Pin it to your profile (not to a subreddit).
3. Then write replies that answer everything with **no link**. People who find an
   answer useful click your username, see the bio, and visit. Every good answer
   works as an ad, and none of them count against the 9:1 ratio.

## Google: making threads and answers rank

Reddit threads rank very well on Google (often in the top 3 and in "Discussions and
forums"), so a good answer can bring visitors for months. Reddit links are `nofollow`,
so they don't pass SEO authority to your site. The value is the **referral traffic from
the thread itself** ranking. To help an answer get found and chosen:

- **Use the words people search.** Name the problem the way a searcher types it:
  "System Data taking up space", "Mac storage full", "what is taking up space on my Mac",
  plus the macOS version (Sequoia, Sonoma) and model (MacBook Air M2) when known.
  Work them in naturally once or twice. Never stuff keywords.
- **Answer in the first two lines.** Google snippets and skimming readers both take
  the opening. Put the key fact or the command there.
- **Make it self-contained and step-by-step.** Numbered steps, exact commands in
  `code`, exact settings paths. Complete answers get upvoted to the top, and
  top comments are what Google shows.
- **Explain the "why" in one sentence.** For example: "the Storage screen lumps
  caches, snapshots and logs into System Data and doesn't break it down."
  People searching usually want to understand, not just fix.
- **Post early in the thread's life.** The first good answer tends to stay on top.
- **For launch posts:** the title is the page title Google indexes. Make it
  descriptive ("Free Mac tool to see what's taking up storage (System Data included)"),
  not clever.
- **Your own site ranks separately.** Linking a specific guide page that exactly matches
  the thread's question sends better-qualified visitors than the homepage, and those
  visits and engagement help your site more than the link itself.

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
