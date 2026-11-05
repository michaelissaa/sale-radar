"""Run: python -m unittest discover -s scanner -v"""
import json
import shutil
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import scan  # noqa: E402
from extract import classify, detect_signals, discover_campaign_links, parse_html  # noqa: E402

FIX = Path(__file__).parent / "fixtures"
ROOT = Path(__file__).parent.parent
ENUM = {"YES", "NO", "CONDITIONAL", "UNKNOWN", "NA"}


class ExtractTests(unittest.TestCase):
    def test_up_to_vs_flat(self):
        s = detect_signals("Black Friday is here. Up to 50% off selected styles.")
        self.assertEqual((s["discount_kind"], s["discount_max_pct"]), ("up_to", 50))
        s = detect_signals("Black Friday: 30% off sitewide, no code needed.")
        self.assertEqual((s["discount_kind"], s["discount_max_pct"]), ("flat", 30))
        self.assertTrue(s["sitewide_hint"])

    def test_classify(self):
        self.assertEqual(classify(detect_signals("New arrivals. Shop shorts."))[0], "NOT_ANNOUNCED")
        self.assertEqual(classify(detect_signals("Black Friday is coming soon. Sign up to be the first to know."))[0], "UPCOMING")
        self.assertEqual(classify(detect_signals("Black Friday sale: 40% off everything"))[0], "LIVE")
        self.assertEqual(classify(detect_signals("Black Friday early access for members: 30% off"))[0], "EARLY_ACCESS")

    def test_real_page_regressions(self):
        # Myprotein AU 2026-11-05: new-customer banner precedes the BF banner
        s = detect_signals("Extra 10% off + FREE shaker for new customers HOW DO YOU BLACK FRIDAY? 40% OFF EVERYTHING | DISCOUNT APPLIED")
        self.assertEqual(s["discount_text"].upper(), "40% OFF")
        # Oner Active 2026-11-05: nav label next to a login link is not an announcement
        s = detect_signals("Menu Black Friday Shop About Us Log In / Sign Up Loyalty Club Contact us")
        self.assertEqual(classify(s)[0], "NEEDS_CHECKING")
        # Gymshark AU 2026-11-05: explicit not-live wording
        s = detect_signals("The Gymshark Black Friday Sale 2026. The sale isn't live just yet. Last time, we offered up to 50% everything")
        self.assertEqual(classify(s)[0], "UPCOMING")

    def test_discovery_follows_redirect_host(self):
        page = parse_html('<a href="https://musclenation.org/collections/black-friday">Black Friday</a>', "https://musclenation.org/")
        self.assertEqual(discover_campaign_links(page["links"], "https://musclenation.org/"), ["https://musclenation.org/collections/black-friday"])

    def test_code_extraction(self):
        s = detect_signals("Black Friday 25% off with code BF25 at checkout")
        self.assertEqual(s["code"], "BF25")

    def test_discovery_same_site_only(self):
        page = parse_html('<a href="/pages/black-friday">BF</a><a href="https://evil.com/black-friday">x</a><a href="/collections/sale">Early Access</a>', "https://shop.com/")
        self.assertEqual(discover_campaign_links(page["links"], "https://shop.com/"),
                         ["https://shop.com/pages/black-friday", "https://shop.com/collections/sale"])

    def test_scripts_ignored(self):
        page = parse_html("<script>var x='Black Friday 90% off'</script><p>Hello</p>", "https://a.com/")
        self.assertNotIn("Black Friday", page["text"])


def syd(y, m, d, h=0, mi=0):
    return datetime(y, m, d, h, mi, tzinfo=scan.SYD).astimezone(timezone.utc)


class ResolveTests(unittest.TestCase):
    V = {"status": "UPCOMING", "start": "2026-11-27", "end": "2026-11-30", "dates_confirmed": True,
         "verified_at": "2026-11-05T00:00:00+00:00", "discount_text": "Up to 50% off"}

    def test_sydney_boundaries(self):
        # 23:59 on 26 Nov Sydney is still upcoming, 00:01 on 27 Nov Sydney is live (UTC is 13:01 on 26 Nov)
        self.assertEqual(scan.resolve_sale(self.V, None, None, True, syd(2026, 11, 26, 23, 59))["status"], "UPCOMING")
        live = scan.resolve_sale(self.V, None, None, True, syd(2026, 11, 27, 0, 1))
        self.assertEqual(live["status"], "LIVE")
        self.assertEqual(live["basis"], "verified")
        self.assertEqual(scan.resolve_sale(self.V, None, None, True, syd(2026, 11, 30, 23, 59))["status"], "LIVE")
        self.assertEqual(scan.resolve_sale(self.V, None, None, True, syd(2026, 12, 1, 0, 1))["status"], "ENDED")

    def test_exact_times(self):
        v = {"status": "UPCOMING", "start": "2026-11-10T09:00:00+11:00", "end": "2026-11-10T13:00:00+11:00", "dates_confirmed": True}
        self.assertEqual(scan.resolve_sale(v, None, None, True, syd(2026, 11, 10, 8, 59))["status"], "UPCOMING")
        self.assertEqual(scan.resolve_sale(v, None, None, True, syd(2026, 11, 10, 9, 0))["status"], "LIVE")
        self.assertEqual(scan.resolve_sale(v, None, None, True, syd(2026, 11, 10, 13, 1))["status"], "ENDED")

    def test_no_invented_dates(self):
        v = {"status": "UPCOMING", "start": "2026-11-27", "dates_confirmed": False, "verified_at": "2026-11-05T00:00:00+00:00",
             "expected_note": "Started 21 Nov in 2025"}
        r = scan.resolve_sale(v, None, None, True, syd(2026, 11, 6))
        self.assertIsNone(r["start"])
        self.assertEqual(r["date_basis"], "unknown")
        self.assertEqual(r["expected_note"], "Started 21 Nov in 2025")

    def test_verified_expires_to_auto(self):
        v = {"status": "LIVE", "verified_at": "2026-11-01T00:00:00+00:00"}
        auto = {"status": "NOT_ANNOUNCED", "confidence": "low"}
        r = scan.resolve_sale(v, auto, {"status": "LIVE"}, True, syd(2026, 11, 10))
        self.assertEqual((r["status"], r["basis"]), ("ENDED", "auto"))

    def test_failed_scan_keeps_previous_marked_stale(self):
        prev = {"status": "LIVE", "discount_text": "30% off"}
        r = scan.resolve_sale(None, None, prev, False, syd(2026, 11, 28))
        self.assertEqual((r["status"], r["basis"], r["discount_text"]), ("LIVE", "stale", "30% off"))


class RunTests(unittest.TestCase):
    """End-to-end offline run with fixtures: one live sale, one upcoming, one blocked (403)."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        (self.tmp / "data").mkdir()
        shutil.copy(FIX / "brands.json", self.tmp / "brands.json")
        shutil.copy(FIX / "research.json", self.tmp / "data" / "research.json")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def go(self, now):
        return scan.run(offline=FIX / "pages", data_dir=self.tmp / "data", config=self.tmp / "brands.json", now=now)

    def test_run_failures_isolated_and_no_duplicate_events(self):
        t0 = syd(2026, 11, 20, 9)
        d = self.go(t0)
        by = {b["id"]: b for b in d["brands"]}
        self.assertEqual(by["livebrand"]["sale"]["status"], "LIVE")
        self.assertEqual(by["livebrand"]["sale"]["discount_kind"], "up_to")
        self.assertEqual(by["soonbrand"]["sale"]["status"], "UPCOMING")
        self.assertIsNone(by["soonbrand"]["sale"]["start"], "auto scan must never invent dates")
        self.assertIsNone(by["soonbrand"]["sale"]["discount_text"], "upcoming pages often quote last year's discount")
        self.assertFalse(by["blocked"]["scan"]["ok"])
        self.assertIn("403", by["blocked"]["scan"]["errors"][0]["error"])
        self.assertEqual(by["blocked"]["sale"]["status"], "NEEDS_CHECKING")
        n1 = len(json.loads((self.tmp / "data" / "changes.json").read_text())["events"])
        # second identical run 6h later: no new events
        d2 = self.go(t0 + timedelta(hours=6))
        n2 = len(json.loads((self.tmp / "data" / "changes.json").read_text())["events"])
        self.assertEqual(n1, n2)
        self.assertEqual(d2["meta"]["new_events"], 0)
        self.assertFalse(any(b["changed_this_run"] for b in d2["brands"]))

    def test_stale_when_previous_success_old(self):
        t0 = syd(2026, 11, 20, 9)
        self.go(t0)
        idx = json.loads((FIX / "pages" / "index.json").read_text())
        broken = self.tmp / "pages"
        shutil.copytree(FIX / "pages", broken)
        for url in ("https://live.example/", "https://live.example/black-friday"):
            idx[url] = {"error": "HTTP 503", "status": 503}
        (broken / "index.json").write_text(json.dumps(idx))
        d = scan.run(offline=broken, data_dir=self.tmp / "data", config=self.tmp / "brands.json", now=t0 + timedelta(hours=24))
        lb = {b["id"]: b for b in d["brands"]}["livebrand"]
        self.assertTrue(lb["scan"]["stale"])
        self.assertEqual(lb["sale"]["basis"], "stale")
        self.assertEqual(lb["sale"]["status"], "LIVE")  # last known value kept, flagged stale
        self.assertTrue(any(e["field"] == "scan.ok" for e in lb["recent_changes"]))


class DataQualityTests(unittest.TestCase):
    """Guards on the real curated dataset."""

    def setUp(self):
        self.cfg = json.loads((ROOT / "config" / "brands.json").read_text(encoding="utf-8"))
        self.res = json.loads((ROOT / "data" / "research.json").read_text(encoding="utf-8"))["brands"]

    def test_config_valid(self):
        ids = [b["id"] for b in self.cfg["brands"]]
        self.assertEqual(len(ids), len(set(ids)))
        for b in self.cfg["brands"]:
            self.assertIn(b["category"], {"gymwear", "sportswear", "fashion"})
            self.assertTrue(b["urls"]["home"].startswith("https://"))

    def test_no_unconfirmed_dates_and_sourced_claims(self):
        for bid, r in self.res.items():
            s = r.get("sale") or {}
            if s.get("start") or s.get("end"):
                self.assertTrue(s.get("dates_confirmed"), f"{bid}: dates without retailer confirmation")
                self.assertTrue(s.get("source_url"), f"{bid}: dated sale without source")
            if s.get("status") in ("LIVE", "UPCOMING", "EARLY_ACCESS"):
                self.assertTrue(s.get("source_url") and s.get("evidence"), f"{bid}: sale claim without source/evidence")

    def test_returns_fields_distinct(self):
        for bid, r in self.res.items():
            ret = (r.get("policy") or {}).get("returns") or {}
            if not ret:
                continue
            for k in ("change_of_mind", "free_return_postage", "free_instore_returns"):
                self.assertIn(ret.get(k, "UNKNOWN"), ENUM, f"{bid}.{k}")
            # "free returns" (no fee to return) must never be derived from postage alone or vice versa
            self.assertIn("free_returns", ret, f"{bid}: free_returns must be explicit")


if __name__ == "__main__":
    unittest.main()
