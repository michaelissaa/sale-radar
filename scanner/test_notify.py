import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent))
import notify  # noqa: E402

NOW = datetime(2026, 11, 6, 9, tzinfo=timezone.utc)
RUN = "20261106T090000Z"


def brand(bid, status, **sale):
    return {"id": bid, "name": bid.title(), "category": "gymwear", "links": {"home": f"https://{bid}.example/"},
            "sale": {"status": status, "sale_type": "black_friday" if status in ("LIVE", "EARLY_ACCESS", "UPCOMING") else None,
                     "basis": "verified", "date_basis": "unknown", **sale}}


def ev(bid, field, old, new, run=RUN):
    return {"id": f"{bid}{field}{run}", "brand": bid, "field": field, "old": old, "new": new, "run": run}


def syd(s):
    return datetime.fromisoformat(s + "+11:00")


class ClassifyTests(unittest.TestCase):
    def kinds(self, b, *changes):
        return notify.classify(b, list(changes))

    def test_black_friday_vs_regular(self):
        self.assertEqual(self.kinds(brand("a", "LIVE"), ev("a", "sale.status", "UPCOMING", "LIVE")), ["bf_live"])
        self.assertEqual(self.kinds(brand("a", "NOT_ANNOUNCED"), ev("a", "sale.regular_active", False, True)), ["sale_live"])
        self.assertEqual(self.kinds(brand("a", "NOT_ANNOUNCED"), ev("a", "sale.regular_active", True, False)), ["sale_ended"])

    def test_announcement_and_dates(self):
        b = brand("a", "UPCOMING", start="2026-11-13", date_basis="confirmed")
        k = self.kinds(b, ev("a", "sale.status", "NOT_ANNOUNCED", "UPCOMING"), ev("a", "sale.start", None, "2026-11-13"))
        self.assertEqual(k, ["bf_announced", "bf_dates"])

    def test_dates_alone(self):
        b = brand("a", "UPCOMING", start="2026-11-20", date_basis="confirmed")
        self.assertEqual(self.kinds(b, ev("a", "sale.start", None, "2026-11-20")), ["bf_dates"])

    def test_no_alert_for_noise(self):
        self.assertEqual(self.kinds(brand("a", "NEEDS_CHECKING"), ev("a", "scan.ok", True, False)), [])
        self.assertEqual(self.kinds(brand("a", "NOT_ANNOUNCED"), ev("a", "sale.status", "UPCOMING", "NOT_ANNOUNCED")), [])

    def test_ended(self):
        self.assertEqual(self.kinds(brand("a", "ENDED"), ev("a", "sale.status", "LIVE", "ENDED")), ["bf_ended"])


class TimedTests(unittest.TestCase):
    MN = brand("muscle-nation", "UPCOMING", start="2026-11-10T09:00:00+11:00", date_basis="confirmed")

    def test_reminder_window(self):
        self.assertEqual(notify.timed(self.MN, syd("2026-11-09T10:00:00")), ["bf_reminder"])  # 23h before
        self.assertEqual(notify.timed(self.MN, syd("2026-11-09T08:00:00")), [])               # 25h before
        self.assertEqual(notify.timed(self.MN, syd("2026-11-10T08:30:00")), [])               # too close for a reminder

    def test_live_now_window(self):
        self.assertEqual(notify.timed(self.MN, syd("2026-11-10T09:20:00")), ["bf_live"])
        self.assertEqual(notify.timed(self.MN, syd("2026-11-10T12:00:00")), [])

    def test_date_only_start_is_sydney_midnight(self):
        nb = brand("nb", "UPCOMING", start="2026-11-13", date_basis="confirmed")
        self.assertEqual(notify.timed(nb, syd("2026-11-12T08:00:00")), ["bf_reminder"])
        self.assertEqual(notify.timed(nb, syd("2026-11-13T00:30:00")), ["bf_live"])

    def test_unconfirmed_dates_never_timed(self):
        self.assertEqual(notify.timed(brand("x", "UPCOMING", start="2026-11-10"), syd("2026-11-10T00:30:00")), [])

    def test_once_per_launch_and_no_duplicate_from_scan(self):
        dash = {"meta": {"run_id": RUN}, "brands": [self.MN]}
        now = syd("2026-11-10T09:10:00")
        a = notify.build(dash, [], RUN, {}, now, "", reminders=True)
        self.assertEqual([x["kind"] for x in a], ["bf_live"])
        self.assertIn("9:00am", a[0]["detail"])
        sent = {a[0]["key"]: now.isoformat()}
        self.assertEqual(notify.build(dash, [], RUN, sent, now + timedelta(hours=1), "", reminders=True), [])
        live = {**self.MN, "sale": {**self.MN["sale"], "status": "LIVE"}}
        evs = [ev("muscle-nation", "sale.status", "UPCOMING", "LIVE")]
        self.assertEqual(notify.build({"meta": {"run_id": RUN}, "brands": [live]}, evs, RUN, sent, now + timedelta(hours=3), ""), [])


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.dash = {"meta": {"run_id": RUN}, "brands": [brand("gymshark", "LIVE", discount_text="Up to 50% off")]}
        self.events = [ev("gymshark", "sale.status", "UPCOMING", "LIVE"), ev("gymshark", "brand", None, "x")]

    def test_build_and_cooldown(self):
        a = notify.build(self.dash, self.events, RUN, {}, NOW, "https://site/")
        self.assertEqual([x["kind"] for x in a], ["bf_live"])
        self.assertIn("Up to 50% off", a[0]["detail"])
        self.assertEqual(notify.build(self.dash, self.events, RUN, {a[0]["key"]: (NOW - timedelta(hours=6)).isoformat()}, NOW, ""), [])
        self.assertEqual(len(notify.build(self.dash, self.events, RUN, {a[0]["key"]: (NOW - timedelta(days=4)).isoformat()}, NOW, "")), 1)

    def test_old_runs_ignored(self):
        self.assertEqual(notify.build(self.dash, [ev("gymshark", "sale.status", "UPCOMING", "LIVE", run="old")], RUN, {}, NOW, ""), [])

    def test_stale_never_alerts(self):
        self.dash["brands"][0]["sale"]["basis"] = "stale"
        self.assertEqual(notify.build(self.dash, self.events, RUN, {}, NOW, ""), [])

    def _run(self, env, response=None, raises=None):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "dashboard.json").write_text(json.dumps(self.dash))
            (d / "changes.json").write_text(json.dumps({"events": self.events}))
            with mock.patch.dict(notify.os.environ, env, clear=True), \
                 mock.patch.object(notify, "post", side_effect=raises, return_value=response) as p:
                notify.main(data_dir=d, now=NOW)
                state = json.loads((d / "notified.json").read_text()) if (d / "notified.json").exists() else None
            return p, state

    def test_unconfigured_sends_nothing(self):
        p, state = self._run({})
        p.assert_not_called()
        self.assertIsNone(state)

    def test_sent_alerts_recorded_only_on_success(self):
        env = {"NOTIFY_URL": "https://x", "NOTIFY_SECRET": "s"}
        p, state = self._run(env, response={"ok": True, "emails": 1, "recipients": 1})
        self.assertEqual(p.call_args[0][1]["secret"], "s")
        self.assertTrue(any(k.startswith("gymshark:bf_live") for k in state["sent"]))
        _, state = self._run(env, response={"ok": False, "error": "bad secret"})
        self.assertIsNone(state)
        _, state = self._run(env, raises=OSError("down"))
        self.assertIsNone(state)

    def test_date_format(self):
        self.assertEqual(notify.fmt_date("2026-11-10T09:00:00+11:00"), "Tue 10 Nov, 9:00am")
        self.assertEqual(notify.fmt_date("2026-11-01"), "Sun 1 Nov")


if __name__ == "__main__":
    unittest.main()
