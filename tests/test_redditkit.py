import datetime as dt
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import redditkit as rk  # noqa: E402

NOW = dt.datetime(2026, 9, 30, 12, tzinfo=dt.timezone.utc)


def entry(kind, days_ago=0, site=None):
    return {"time": (NOW - dt.timedelta(days=days_ago)).isoformat(), "kind": kind, "sub": "mac", "site": site}


class RatioTests(unittest.TestCase):
    def test_no_promo_until_nine_helpful(self):
        r = rk.ratio_status([entry("helpful")] * 8, "freemac", 7, NOW)
        self.assertEqual(r["promo_allowed_now"], 0)
        r = rk.ratio_status([entry("helpful")] * 9, "freemac", 7, NOW)
        self.assertEqual(r["promo_allowed_now"], 1)

    def test_promo_uses_budget_per_site(self):
        log = [entry("helpful")] * 9 + [entry("promo", site="freemac")]
        self.assertEqual(rk.ratio_status(log, "freemac", 7, NOW)["promo_allowed_now"], 0)
        self.assertEqual(rk.ratio_status(log, "other", 7, NOW)["promo_allowed_now"], 1)

    def test_old_entries_ignored(self):
        r = rk.ratio_status([entry("helpful", days_ago=10)] * 20, None, 7, NOW)
        self.assertEqual(r["helpful"], 0)

    def test_format_says_how_many_more(self):
        text = rk.format_ratio({"days": 7, "helpful": 3, "promo": 0, "promo_allowed_now": 0}, None)
        self.assertIn("about 6 more helpful", text)


class ParseTests(unittest.TestCase):
    def test_thread_json_url(self):
        self.assertEqual(
            rk.thread_json_url("https://old.reddit.com/r/mac/comments/abc/some_title/?utm=x"),
            "https://www.reddit.com/r/mac/comments/abc/some_title.json?limit=10&sort=top",
        )

    def test_parse_thread_skips_deleted_and_more(self):
        data = [
            {"data": {"children": [{"data": {"subreddit": "mac", "title": "System Data 90GB??",
                                             "selftext": "help", "score": 4, "permalink": "/r/mac/comments/abc/x/"}}]}},
            {"data": {"children": [
                {"kind": "t1", "data": {"author": "a", "score": 3, "body": "[deleted]"}},
                {"kind": "t1", "data": {"author": "b", "score": 5, "body": "Time Machine snapshots"}},
                {"kind": "more", "data": {}},
            ]}},
        ]
        t = rk.parse_thread(data)
        self.assertEqual(t["sub"], "mac")
        self.assertEqual([c["body"] for c in t["comments"]], ["Time Machine snapshots"])
        self.assertIn("System Data 90GB??", rk.format_thread(t))

    def test_parse_rules(self):
        rules = rk.parse_rules({"rules": [{"short_name": "No self-promo", "description": "Mods approve dev posts."}]})
        self.assertIn("1. No self-promo", rk.format_rules("macapps", rules))

    def test_parse_listing(self):
        data = {"data": {"children": [{"data": {"id": "x", "subreddit": "mac", "title": "t",
                                                "permalink": "/r/mac/comments/x/t/", "num_comments": 2}}]}}
        self.assertEqual(rk.parse_listing(data)[0]["url"], "https://www.reddit.com/r/mac/comments/x/t/")


class PromptTests(unittest.TestCase):
    def test_prompt_contains_skill_site_and_thread(self):
        site = {"key": "freemac", "name": "Free Mac", "url": "https://free-mac.online/",
                "facts": ["Free"], "pages": [{"title": "Guide", "url": "https://free-mac.online/g"}]}
        p = rk.build_prompt("reply", site, thread="Title: disk full", ratio="No links for now")
        for needle in ("Hard rules", "Voice: sound like a person", "https://free-mac.online/g",
                       "Title: disk full", "No links for now", "Task: reply"):
            self.assertIn(needle, p)

    def test_example_config_parses(self):
        cfg = rk.load_config(Path(__file__).resolve().parent.parent / "sites.example.toml")
        site = rk.get_site(cfg, "freemac")
        self.assertTrue(site["subreddits"] and site["keywords"])


if __name__ == "__main__":
    unittest.main()
