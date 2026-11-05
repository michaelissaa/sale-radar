"""Turn scan changes and upcoming launch times into subscriber alerts and hand them to the email backend.

Black Friday first: sale.status only describes the Black Friday sale; regular (non Black Friday) sales are
tracked separately via sale.regular_active and are opt-in alerts.

The backend (notify/apps-script/Code.gs, a Google Apps Script web app) owns the private subscriber list
and sends the emails. This script only decides WHAT is worth an alert and posts it.

Env: NOTIFY_URL, NOTIFY_SECRET (GitHub Secrets). Missing -> prints the alerts and exits 0.
Usage: python scanner/notify.py [--dry-run] [--reminders]
  --reminders  clock-based alerts only (hourly job): "goes live in under 24h" and "live now"
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
SYD = ZoneInfo("Australia/Sydney")
ACTIVE = {"LIVE", "EARLY_ACCESS"}
# The same alert for the same brand isn't repeated within this window (protects against status flicker).
COOLDOWN = {"bf_announced": timedelta(days=14), "bf_dates": timedelta(days=1), "bf_live": timedelta(days=3),
            "bf_reminder": timedelta(days=2), "bf_ended": timedelta(days=3),
            "sale_live": timedelta(days=3), "sale_ended": timedelta(days=3), "discount": timedelta(days=1)}
REMIND_BEFORE = timedelta(hours=24)  # "goes live tomorrow" heads-up
LIVE_WINDOW = timedelta(hours=2)     # hourly job announces a confirmed launch once it has started
KIND_TITLE = {
    "bf_announced": "Black Friday sale announced",
    "bf_dates": "Black Friday dates confirmed",
    "bf_reminder": "Black Friday sale goes live soon",
    "bf_live": "Black Friday sale is live",
    "bf_ended": "Black Friday sale ended",
    "sale_live": "Regular sale started (not Black Friday)",
    "sale_ended": "Regular sale ended",
    "discount": "Black Friday discount changed",
}


def load(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default


def start_dt(v: str) -> datetime:
    """Confirmed start as an aware datetime. Date-only values mean midnight Sydney time."""
    if "T" in v:
        return datetime.fromisoformat(v)
    return datetime.fromisoformat(v[:10]).replace(tzinfo=SYD)


def fmt_date(v: str | None) -> str | None:
    if not v:
        return None
    if "T" in v:
        dt = datetime.fromisoformat(v).astimezone(SYD)
        return dt.strftime("%a %d %b, %I:%M%p").replace(" 0", " ").replace("AM", "am").replace("PM", "pm")
    return datetime.fromisoformat(v[:10]).strftime("%a %d %b").replace(" 0", " ")


def classify(brand: dict, changes: list[dict]) -> list[str]:
    """Which alert kinds one brand's changes in a scan add up to."""
    by = {c["field"]: c for c in changes}
    sale = brand["sale"]
    kinds = []
    st = by.get("sale.status")
    if st:
        old, new = st["old"], st["new"]
        if new in ACTIVE and old not in ACTIVE:
            kinds.append("bf_live")
        elif new == "UPCOMING" and old not in ACTIVE | {"UPCOMING"}:
            kinds.append("bf_announced")
        elif old in ACTIVE and new == "ENDED":  # LIVE -> NOT_ANNOUNCED is a correction, not an ending
            kinds.append("bf_ended")
    if ("sale.start" in by or "sale.end" in by) and sale.get("date_basis") == "confirmed" and (sale.get("start") or sale.get("end")):
        if "bf_live" not in kinds:  # going live already tells them
            kinds.append("bf_dates")
    if "sale.discount_text" in by and sale["status"] in ACTIVE and sale.get("discount_text") and not kinds:
        kinds.append("discount")
    reg = by.get("sale.regular_active")
    if reg and reg["new"] is True and reg["old"] is not True:
        kinds.append("sale_live")
    elif reg and reg["old"] is True and reg["new"] is False:  # missing -> False (new field) is not an ending
        kinds.append("sale_ended")
    return list(dict.fromkeys(kinds))


def timed(brand: dict, now: datetime) -> list[str]:
    """Clock-based alerts for retailer-confirmed launch times. No fetching, so it can run hourly."""
    s = brand["sale"]
    if s.get("date_basis") != "confirmed" or not s.get("start"):
        return []
    until = start_dt(s["start"]) - now
    if timedelta(hours=1) < until <= REMIND_BEFORE:
        return ["bf_reminder"]
    if timedelta(0) <= -until <= LIVE_WINDOW:
        return ["bf_live"]
    return []


def build(dash: dict, events: list[dict], run_id: str, sent: dict, now: datetime, site_url: str,
          reminders: bool = False) -> list[dict]:
    brands = {b["id"]: b for b in dash["brands"]}
    per_brand: dict[str, list] = {}
    if reminders:
        per_brand = {bid: [] for bid in brands}
    else:
        for e in events:
            if e["run"] == run_id and e["field"] != "brand" and e["brand"] in brands:
                per_brand.setdefault(e["brand"], []).append(e)
    out = []
    for bid, ch in per_brand.items():
        b = brands[bid]
        s = b["sale"]
        if s.get("basis") == "stale":  # never alert on values we couldn't re-check
            continue
        for kind in (timed(b, now) if reminders else classify(b, ch)):
            key = f"{bid}:{kind}"
            if kind in ("bf_reminder", "bf_live") and s.get("start"):
                key += f":{s['start']}"  # once per announced launch time, shared by the hourly job and the scan
            last = sent.get(key)
            if last and now - datetime.fromisoformat(last) < COOLDOWN[kind]:
                continue
            reg = s.get("regular") or {}
            when = " to ".join(x for x in (fmt_date(s.get("start")), fmt_date(s.get("end"))) if x)
            regular_kind = kind in ("sale_live", "sale_ended")
            detail = "; ".join(x for x in (
                reg.get("discount_text") if regular_kind else s.get("discount_text"),
                f"Goes live: {when} (Sydney time, confirmed by retailer)" if when and not regular_kind and s.get("date_basis") == "confirmed" else None,
                None if regular_kind else (s.get("early_access") and f"Early access: {s['early_access']}"),
                reg.get("conditions") if regular_kind else s.get("conditions"),
            ) if x)
            out.append({
                "id": f"{run_id}:{key}", "key": key, "brand": bid, "brand_name": b["name"], "category": b["category"],
                "kind": kind, "detail": detail,
                "title": f"{b['name']}: " + ("Black Friday early access is live" if kind == "bf_live" and s["status"] == "EARLY_ACCESS" else KIND_TITLE[kind]),
                "status": s["status"], "start": s.get("start"),
                "url": (reg.get("source_url") if regular_kind else s.get("source_url")) or b["links"].get("sale") or b["links"].get("home"),
                "site_url": f"{site_url}#{bid}", "at": now.isoformat(timespec="seconds"),
            })
    return out


def post(url: str, payload: dict) -> dict:
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "text/plain;charset=utf-8"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:  # Apps Script answers via a redirect; urllib follows it
        body = r.read().decode("utf-8", "replace")
    try:
        return json.loads(body)
    except ValueError:
        return {"ok": False, "error": f"unexpected response: {body[:200]}"}


def main(dry_run: bool = False, data_dir: Path = ROOT / "data", now: datetime | None = None, reminders: bool = False) -> list[dict]:
    now = now or datetime.now(timezone.utc)
    dash = load(data_dir / "dashboard.json", None)
    if not dash:
        print("notify: no dashboard.json yet")
        return []
    site = load(ROOT / "config" / "site.json", {})
    changes = load(data_dir / "changes.json", {"events": []})["events"]
    state_path = data_dir / "notified.json"
    state = load(state_path, {"sent": {}})
    alerts = build(dash, changes, dash["meta"]["run_id"], state["sent"], now, site.get("site_url", ""), reminders)
    print(f"notify{' (reminders)' if reminders else ''}: {len(alerts)} alert(s)")
    for a in alerts:
        print(f"  - {a['title']} | {a['detail'][:110]}")
    url, secret = os.environ.get("NOTIFY_URL"), os.environ.get("NOTIFY_SECRET")
    if dry_run or not alerts:
        return alerts
    if not url or not secret:
        print("notify: NOTIFY_URL / NOTIFY_SECRET not set, so no emails sent (see notify/README.md)")
        return alerts
    try:
        res = post(url, {"action": "notify", "secret": secret, "alerts": alerts, "site_url": site.get("site_url", "")})
    except Exception as e:  # never fail the scan because email had a problem
        print(f"::warning title=notify::backend unreachable: {type(e).__name__}: {e}")
        return alerts
    if not res.get("ok"):
        print(f"::warning title=notify::backend error: {res.get('error')}")
        return alerts
    print(f"notify: backend sent {res.get('emails', 0)} email(s) to {res.get('recipients', 0)} subscriber(s)")
    for a in alerts:
        state["sent"][a["key"]] = now.isoformat(timespec="seconds")
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    return alerts


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--reminders", action="store_true", help="clock-based alerts only (hourly job)")
    a = ap.parse_args()
    main(a.dry_run, reminders=a.reminders)
    sys.exit(0)
