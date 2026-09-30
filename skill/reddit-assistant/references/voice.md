# Voice: sound like a person

Redditors can tell within one sentence when something was written by a
marketer or an AI. What gives it away is **polish without a point of view**.
Real comments are specific, a little uneven, and clearly written by someone
who has been through the problem.

## Do

- **Open on the problem, not on praise for the question.** Start with the useful
  thing or with a relatable reaction.
  - Good: "Ugh, System Data hitting 80GB is almost always Time Machine local snapshots."
  - Bad: "Great question! There are several reasons why System Data can grow."
- **Show feeling where a person would feel it.** Frustration, relief, surprise and
  mild annoyance are all fine: "this drove me nuts for a week", "honestly
  didn't expect that to work". Keep it proportional. One small moment per reply, not every sentence.
- **Be concrete.** Real menu paths, real commands, real numbers, the macOS version.
  "Settings > General > Storage, then hover over System Data" beats "check your storage settings."
- **Vary the rhythm.** Mix short sentences with longer ones. A fragment now and then is fine. So is starting with "So" or "Yeah".
- **Use contractions and plain words.** "it's", "don't", "pretty much", "kinda" (sparingly).
- **Admit limits.** "Not 100% sure this applies on Intel Macs", "YMMV if you're on Sonoma."
  Hedging on the right details makes the confident parts believable.
- **Match the subreddit.** r/mac is casual and a bit jokey. r/MacOS is more
  technical. r/SideProject is supportive of makers. Mirror the top comments' length and tone.
- **Keep it short.** Two to four sentences is the default and answers most threads.
  Add lines only when the question really needs steps or commands (see "Length" in `SKILL.md`).
- **End naturally.** A follow-up question ("which macOS are you on?"), a caveat, or just stop.

## Don't

- Marketing words: *game-changer, seamless, powerful, ultimate, unlock, supercharge,
  effortless, boost, leverage, revolutionize, must-have, check it out!*
- AI tells: *"Great question", "I hope this helps!", "In conclusion", "It's worth noting",
  "Let's dive in", "delve", "navigate the complexities"*, a neat three-item list
  for everything, bold headers on a 4-sentence reply, and em dashes in every other sentence.
- Perfectly balanced "pros and cons" when a person would just give an opinion.
- Exclamation marks in more than one place.
- Emojis, unless the subreddit clearly uses them.
- A fake backstory. If you don't have the user's real experience, leave a `[slot]`.

## Disclosure that still sounds human

Disclosure is required, but it doesn't have to sound like a legal notice.
The most natural version is a short origin story: you hit the problem, so you
built something. Readers see that as a maker sharing, not as an ad.

Casual (prefer these):

- "I got fed up with this on my own Mac and made a small free tool for it: <link>"
- "(<link>, a side project of mine, does this visually)"
- "I ended up building a little free thing for exactly this after fighting it myself: <link>"
- "I wrote up the whole process with screenshots here, it's my site: <link>"

More explicit (good for skeptical subs, or when someone asks directly):

- "Full disclosure, I built this, so I'm biased, but it's free and does exactly this: <link>"
- "(I'm the dev, happy to take feedback, especially the harsh kind)"

Rules for all of them:

- The ownership words ("I made", "my site", "side project of mine") sit right
  next to the link, never tucked at the end of a long reply.
- Only use an origin story the user actually gave you ("fed up with this on my
  own Mac" must be true). Otherwise use a plain version like "(my site)".
- **Never write the user's own site as if they just came across it** ("I found
  this tool", "someone recommended X"). That's astroturfing. Reddit bans domains
  for it, and it misleads the people you're trying to help. If the user asks
  for that, write the casual disclosed version and explain why.
- Naming a free alternative next to your own ("GrandPerspective works too")
  makes the recommendation believable. Do it when a good one exists.

## Before and after

**Before (reads like an ad):**
> Great question! Large System Data can be caused by many factors. Our powerful free
> tool at free-mac.online can help you seamlessly reclaim storage. Check it out!

**After (reads like a person):**
> That's usually local Time Machine snapshots, especially if you back up to a drive
> that isn't always plugged in. Run `tmutil listlocalsnapshots /` in Terminal. If you
> see a bunch, `sudo tmutil thinlocalsnapshots / 999999999999 4` clears most of them.
> Mine dropped from ~70GB to 12GB doing that.
>
> If it's not snapshots, it's usually caches or old iOS backups. [your one-line tip here]

No link, because the answer is complete. That's the right call about 9 times out of 10.
Note that "Mine dropped from ~70GB to 12GB" must be the user's real result. Otherwise it becomes a `[slot]`.
