import datetime as dt
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import postqueue as pq  # noqa: E402
import redditkit as rk  # noqa: E402

NOW = dt.datetime(2026, 10, 5, 8, 0)
SITE = ["https://free-mac.online/"]

QUEUE = """# Week 41

### 2026-10-06 09:00 | x | approved
Your Mac's System Data jumped 60GB overnight?
---
Full guide (my site): https://free-mac.online/

### 2026-10-07 19:00 | threads | draft
Drop a screenshot of your storage bar and I'll tell you what's eating it.

### 2026-10-09 09:00 | x | posted
Old iPhone backups are often 20GB+ each.
"""


class ParseTests(unittest.TestCase):
    def test_parse(self):
        e = pq.parse_queue(QUEUE)
        self.assertEqual([x.platform for x in e], ["x", "threads", "x"])
        self.assertEqual([x.status for x in e], ["approved", "draft", "posted"])
        self.assertEqual(len(e[0].parts), 2)
        self.assertEqual(e[0].when, dt.datetime(2026, 10, 6, 9, 0))

    def test_bad_header(self):
        with self.assertRaises(ValueError):
            pq.parse_queue("### tomorrow | x | draft\nhi")
        with self.assertRaises(ValueError):
            pq.parse_queue("### 2026-10-06 09:00 | facebook | draft\nhi")


class CheckTests(unittest.TestCase):
    def test_clean_queue_passes(self):
        errors, warnings = pq.check_queue(pq.parse_queue(QUEUE), SITE, now=NOW)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_x_counts_links_as_23(self):
        self.assertEqual(pq.x_length("see https://free-mac.online/some/very/long/path/here"), 4 + 23)

    def test_too_long_is_error(self):
        q = "### 2026-10-06 09:00 | x | draft\n" + "a" * 281
        errors, _ = pq.check_queue(pq.parse_queue(q), SITE, now=NOW)
        self.assertTrue(any("281 chars" in e for e in errors))

    def test_link_in_main_post_warns(self):
        q = "### 2026-10-06 09:00 | x | draft\nhttps://free-mac.online/ is great"
        q += "\n\n### 2026-10-07 09:00 | x | draft\ntip\n\n### 2026-10-08 09:00 | x | draft\ntip2"
        q += "\n\n### 2026-10-06 19:00 | threads | draft\ntip3"
        _, warnings = pq.check_queue(pq.parse_queue(q), SITE, now=NOW)
        self.assertTrue(any("link in the main post" in w for w in warnings))

    def test_too_much_promo_is_error(self):
        q = "\n\n".join(f"### 2026-10-0{d} 09:00 | x | draft\ntip {d}\n---\nhttps://free-mac.online/"
                        for d in (6, 7))
        errors, _ = pq.check_queue(pq.parse_queue(q), SITE, now=NOW)
        self.assertTrue(any("link your sites" in e for e in errors))

    def test_weekly_and_daily_limits(self):
        q = "\n\n".join(f"### 2026-10-06 {h:02d}:00 | x | draft\ntip number {h}" for h in (8, 12, 18))
        errors, warnings = pq.check_queue(pq.parse_queue(q), SITE, now=NOW, max_per_day=2, posts_per_week=2)
        self.assertTrue(any("max is 2 per day" in e for e in errors))
        self.assertTrue(any("your plan is 2" in w for w in warnings))

    def test_duplicate_text_warns(self):
        q = "### 2026-10-06 09:00 | x | draft\nSame tip!\n\n### 2026-10-06 19:00 | threads | draft\nsame tip"
        _, warnings = pq.check_queue(pq.parse_queue(q), SITE, now=NOW)
        self.assertTrue(any("same text" in w for w in warnings))


class TodayTests(unittest.TestCase):
    def test_counts_by_platform(self):
        now = dt.datetime(2026, 10, 5, 20, 0, tzinfo=dt.timezone.utc)
        log = [{"time": "2026-10-05T10:00:00+00:00", "sub": "x"},
               {"time": "2026-10-05T11:00:00+00:00", "sub": "mac"},
               {"time": "2026-10-04T11:00:00+00:00", "sub": "x"}]
        status = rk.today_status(log, {"reddit": 5, "x": 10, "threads": 5}, now)
        self.assertEqual(status, {"reddit": (1, 5), "x": (1, 10), "threads": (0, 5)})


if __name__ == "__main__":
    unittest.main()
