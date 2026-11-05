"""Sale Radar scanner.

Reads config/brands.json + data/research.json (human-verified facts), fetches each
brand's public pages politely, detects sale signals, merges with verified data,
diffs against the previous run and writes data/dashboard.json + data/changes.json.

Stdlib only so GitHub Actions needs no installs.
Usage: python scanner/scan.py [--only gymshark,lskd] [--offline FIXTURE_DIR]
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
import time
import urllib.error
import urllib.request
import urllib.robotparser
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).parent))
from extract import classify, detect_signals, discover_campaign_links, parse_html  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SYD = ZoneInfo("Australia/Sydney")
UA = "SaleRadarBot/1.0 (+https://github.com/michaelissaa/sale-radar; personal sale tracker, few requests per 6h)"
TIMEOUT = 20
PER_HOST_DELAY = 2.0
POLICY_RECHECK = timedelta(hours=24)
STALE_AFTER = timedelta(hours=18)  # ~3 missed 6-hourly scans
VERIFIED_SALE_TTL = timedelta(days=3)  # verified sale status trusted this long without re-verification
MAX_CHANGES = 1000
ACTIVE = {"LIVE", "EARLY_ACCESS"}


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def iso(dt: datetime | None) -> str | None:
    return dt.astimezone(timezone.utc).isoformat(timespec="seconds") if dt else None


def parse_iso(s: str | None) -> datetime | None:
    if not s:
        return None
    dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)  # atomic: a crash never leaves half-written data


# ---------------------------------------------------------------- fetching
class Fetcher:
    """Polite fetcher: robots.txt, per-host delay, conditional GET, never retries blocks."""

    def __init__(self, cache: dict, offline_dir: Path | None = None):
        self.cache = cache  # url -> {etag, last_modified}
        self.robots: dict[str, urllib.robotparser.RobotFileParser | None] = {}
        self.last_hit: dict[str, float] = {}
        self.offline_dir = offline_dir

    def _robots_ok(self, url: str) -> bool:
        host = urlparse(url).netloc
        if host not in self.robots:
            rp = urllib.robotparser.RobotFileParser()
            try:
                req = urllib.request.Request(f"https://{host}/robots.txt", headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                    rp.parse(r.read().decode("utf-8", "replace").splitlines())
            except urllib.error.HTTPError as e:
                # 4xx (not 401/403) = no robots file = allowed; 401/403/5xx = treat as disallowed
                rp.parse([] if 400 <= e.code < 500 and e.code not in (401, 403) else ["User-agent: *", "Disallow: /"])
            except Exception:
                rp = None  # unreachable; let the page fetch itself fail and be recorded
            self.robots[host] = rp
        rp = self.robots[host]
        return True if rp is None else rp.can_fetch(UA, url)

    def get(self, url: str) -> dict:
        if self.offline_dir is not None:
            return self._offline(url)
        if not self._robots_ok(url):
            return {"ok": False, "url": url, "error": "disallowed by robots.txt"}
        host = urlparse(url).netloc
        wait = PER_HOST_DELAY - (time.monotonic() - self.last_hit.get(host, 0))
        if wait > 0:
            time.sleep(wait)
        self.last_hit[host] = time.monotonic()
        headers = {"User-Agent": UA, "Accept": "text/html,application/xhtml+xml", "Accept-Language": "en-AU,en;q=0.9", "Accept-Encoding": "gzip"}
        c = self.cache.get(url, {})
        if c.get("etag"):
            headers["If-None-Match"] = c["etag"]
        if c.get("last_modified"):
            headers["If-Modified-Since"] = c["last_modified"]
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=TIMEOUT) as r:
                body = r.read(3_000_000)
                if r.headers.get("Content-Encoding") == "gzip":
                    body = gzip.decompress(body)
                self.cache[url] = {"etag": r.headers.get("ETag"), "last_modified": r.headers.get("Last-Modified")}
                return {"ok": True, "url": url, "final_url": r.geturl(), "status": r.status, "html": body.decode("utf-8", "replace")}
        except urllib.error.HTTPError as e:
            if e.code == 304:
                return {"ok": True, "url": url, "status": 304, "not_modified": True}
            hint = " (likely bot protection)" if e.code in (401, 403, 429) else ""
            return {"ok": False, "url": url, "status": e.code, "error": f"HTTP {e.code}{hint}"}
        except Exception as e:  # timeouts, DNS, TLS, decode
            return {"ok": False, "url": url, "error": f"{type(e).__name__}: {e}"[:200]}

    def _offline(self, url: str) -> dict:
        name = hashlib.sha1(url.encode()).hexdigest()[:12] + ".html"
        index = load_json(self.offline_dir / "index.json", {})
        if url in index:
            spec = index[url]
            if "error" in spec:
                return {"ok": False, "url": url, "status": spec.get("status"), "error": spec["error"]}
            name = spec["file"]
        p = self.offline_dir / name
        if not p.exists():
            return {"ok": False, "url": url, "error": "fixture missing"}
        return {"ok": True, "url": url, "status": 200, "html": p.read_text(encoding="utf-8")}


# ---------------------------------------------------------------- sale logic
def sydney_day_bounds(date_str: str) -> tuple[datetime, datetime]:
    """'2026-11-27' -> whole Sydney day. A full ISO datetime ('2026-11-10T09:00:00+11:00') is exact."""
    if "T" in date_str:
        dt = datetime.fromisoformat(date_str)
        dt = dt if dt.tzinfo else dt.replace(tzinfo=SYD)
        return dt, dt
    d = datetime.fromisoformat(date_str[:10]).replace(tzinfo=SYD)
    return d, d + timedelta(days=1) - timedelta(seconds=1)


def resolve_sale(verified: dict | None, auto: dict | None, prev: dict | None, scan_ok: bool, now: datetime) -> dict:
    """Combine human-verified data, this run's page signals and the previous result.

    Priority: retailer-confirmed dates > fresh verified status > fresh auto signals > previous (stale).
    Dates are only ever copied from verified data with dates_confirmed=true.
    """
    v = verified or {}
    out = {
        "status": "NOT_ANNOUNCED", "basis": "none", "confidence": "low",
        "name": v.get("name"), "discount_text": v.get("discount_text"), "discount_max_pct": v.get("discount_max_pct"),
        "discount_kind": v.get("discount_kind"), "scope": v.get("scope", "UNKNOWN"),
        "start": v.get("start") if v.get("dates_confirmed") else None,
        "end": v.get("end") if v.get("dates_confirmed") else None,
        "date_basis": "confirmed" if v.get("dates_confirmed") and (v.get("start") or v.get("end")) else "unknown",
        "expected_note": v.get("expected_note"),  # historical pattern, never shown as confirmed
        "code_required": v.get("code_required", "UNKNOWN"), "code": v.get("code"),
        "early_access": v.get("early_access"), "conditions": v.get("conditions"),
        "evidence": v.get("evidence"), "source_url": v.get("source_url"), "verified_at": v.get("verified_at"),
        "verification": v.get("verification"),
        "auto": auto,
    }
    verified_at = parse_iso(v.get("verified_at"))

    # 1. Retailer-confirmed dates are authoritative.
    if out["start"] or out["end"]:
        start = sydney_day_bounds(out["start"])[0] if out["start"] else None
        end = sydney_day_bounds(out["end"])[1] if out["end"] else None
        if end and now > end:
            return {**out, "status": "ENDED", "basis": "verified", "confidence": "high"}
        if start and now < start:
            status = "EARLY_ACCESS" if v.get("status") == "EARLY_ACCESS" else "UPCOMING"
            return {**out, "status": status, "basis": "verified", "confidence": "high"}
        if start and now >= start:
            return {**out, "status": "LIVE", "basis": "verified", "confidence": "high"}

    # 2. Recently verified status (no dates) stays trusted for a few days.
    if v.get("status") and verified_at and now - verified_at <= VERIFIED_SALE_TTL:
        return {**out, "status": v["status"], "basis": "verified", "confidence": v.get("confidence", "high")}

    # 3. Fresh automatic detection.
    if scan_ok and auto:
        status, conf = auto["status"], auto["confidence"]
        if status == "NOT_ANNOUNCED" and prev and prev.get("status") in ACTIVE:
            status, conf = "ENDED", "low"  # was active, wording now gone
        merged = {**out, "status": status, "basis": "auto", "confidence": conf}
        # Discounts on "coming soon" pages are often last year's ("Last time we offered up to 50%"),
        # so only attach a detected discount when the sale is active.
        if status in ACTIVE and auto.get("discount_text"):
            merged.update(
                discount_text=auto["discount_text"], discount_max_pct=auto["discount_max_pct"],
                discount_kind=auto["discount_kind"], evidence=auto.get("evidence"), source_url=auto.get("url"),
                scope="SITEWIDE" if auto.get("sitewide_hint") else out["scope"],
            )
            if auto.get("code"):
                merged.update(code=auto["code"], code_required="YES")
        if status == "UPCOMING" and not out["discount_text"]:
            merged.update(evidence=auto.get("evidence"), source_url=auto.get("url"))
        if status == "NOT_ANNOUNCED":
            # don't keep a stale verified discount next to a "not announced" status
            merged.update(discount_text=None, discount_max_pct=None, discount_kind=None, evidence=auto.get("evidence"))
        return merged

    # 4. Scan failed: keep the previous answer but say it is stale.
    if prev:
        return {**prev, "auto": auto, "basis": "stale", "confidence": "low",
                "status": prev.get("status") if prev.get("status") != "NOT_ANNOUNCED" else "NEEDS_CHECKING"}
    return {**out, "status": "NEEDS_CHECKING", "basis": "none"}


def policy_fingerprint(text: str) -> str:
    keep = [s for s in text.split(". ") if any(k in s.lower() for k in ("return", "refund", "deliver", "shipping", "days", "$"))]
    return hashlib.sha1(" ".join(keep).encode()).hexdigest()[:16]


# ---------------------------------------------------------------- per brand
def scan_brand(brand: dict, fetcher: Fetcher, prev_scan: dict, now: datetime) -> tuple[dict, dict]:
    """Return (scan_record, best_auto_signals)."""
    urls = brand.get("urls", {})
    sale_urls = [urls.get("home")] + list(urls.get("sale", [])) + list(prev_scan.get("discovered", []))[:3]
    sale_urls = list(dict.fromkeys(u for u in sale_urls if u))
    errors, best, discovered, pages_ok = [], None, [], 0
    prev_signals = prev_scan.get("signals_by_url", {})
    signals_by_url = {}
    rank = {"LIVE": 4, "EARLY_ACCESS": 3, "UPCOMING": 2, "NEEDS_CHECKING": 1, "NOT_ANNOUNCED": 0}

    for url in sale_urls:
        r = fetcher.get(url)
        if not r["ok"]:
            errors.append({"url": url, "error": r["error"]})
            continue
        pages_ok += 1
        if r.get("not_modified") and url in prev_signals:
            sig = prev_signals[url]
        else:
            page = parse_html(r.get("html", ""), r.get("final_url", url))
            sig = detect_signals(page["text"])
            status, conf = classify(sig)
            sig.update(status=status, confidence=conf, url=r.get("final_url", url), title=page["title"][:120])
            if url == urls.get("home"):
                discovered = discover_campaign_links(page["links"], r.get("final_url", url))
        signals_by_url[url] = sig
        if best is None or rank[sig["status"]] > rank[best["status"]]:
            best = sig

    # policy pages: at most once per POLICY_RECHECK
    policy = dict(prev_scan.get("policy", {}))
    last_policy = parse_iso(policy.get("checked_at"))
    if not last_policy or now - last_policy >= POLICY_RECHECK:
        fps, perrs = {}, []
        for key in ("returns", "shipping"):
            u = urls.get(key)
            if not u:
                continue
            r = fetcher.get(u)
            if r["ok"] and r.get("not_modified"):
                fps[key] = policy.get("fingerprints", {}).get(key)
            elif r["ok"]:
                text = parse_html(r["html"], u)["text"]
                fps[key] = policy_fingerprint(text)
                hint = detect_signals(text)["free_shipping_threshold_hint"]
                if key == "shipping" and hint:
                    policy["free_shipping_threshold_hint"] = hint
            else:
                perrs.append({"url": u, "error": r["error"]})
        policy.update(checked_at=iso(now), errors=perrs, ok=not perrs and bool(fps))
        if fps:
            policy["fingerprints"] = {**policy.get("fingerprints", {}), **fps}
            policy.setdefault("baseline_fingerprints", policy["fingerprints"])
        if policy.get("ok"):
            policy["last_success"] = iso(now)

    ok = pages_ok > 0
    rec = {
        "last_attempt": iso(now),
        "last_success": iso(now) if ok else prev_scan.get("last_success"),
        "ok": ok,
        "pages_ok": pages_ok,
        "pages_tried": len(sale_urls),
        "errors": errors,
        "consecutive_failures": 0 if ok else prev_scan.get("consecutive_failures", 0) + 1,
        "discovered": discovered or prev_scan.get("discovered", []),
        "signals_by_url": signals_by_url or prev_signals,
        "policy": policy,
    }
    return rec, best


def build_policy(verified: dict | None, scan_policy: dict) -> dict:
    v = verified or {}
    base, cur = scan_policy.get("baseline_fingerprints", {}), scan_policy.get("fingerprints", {})
    changed = [k for k in cur if k in base and cur[k] != base[k]]
    return {
        "returns": v.get("returns", {}),
        "shipping": v.get("shipping", {}),
        "summary": v.get("summary"),
        "verified_at": v.get("verified_at"),
        "verification": v.get("verification", "unverified"),
        "page_checked_at": scan_policy.get("checked_at"),
        "page_ok": scan_policy.get("ok"),
        "page_changed_since_verified": changed,
        "free_shipping_threshold_hint": scan_policy.get("free_shipping_threshold_hint"),
    }


# ---------------------------------------------------------------- diffing
WATCH = [
    ("sale.status", "Sale status"), ("sale.discount_text", "Discount"), ("sale.start", "Start date"),
    ("sale.end", "End date"), ("sale.code", "Code"), ("policy.returns.free_return_postage", "Free return postage"),
    ("policy.returns.change_of_mind", "Change-of-mind returns"), ("policy.returns.window_days", "Returns window"),
    ("policy.shipping.free_threshold_aud", "Free shipping threshold"), ("scan.ok", "Scan health"),
]


def dig(d: dict, path: str):
    for k in path.split("."):
        if not isinstance(d, dict):
            return None
        d = d.get(k)
    return d


def diff(prev: dict | None, cur: dict, run_id: str, at: str) -> list[dict]:
    if prev is None:
        return [{"id": hashlib.sha1(f"{cur['id']}|added".encode()).hexdigest()[:12], "brand": cur["id"], "field": "brand",
                 "label": "Now tracking", "old": None, "new": cur["name"], "at": at, "run": run_id}]
    out = []
    for path, label in WATCH:
        a, b = dig(prev, path), dig(cur, path)
        if a != b:
            eid = hashlib.sha1(f"{cur['id']}|{path}|{a}|{b}|{run_id}".encode()).hexdigest()[:12]
            out.append({"id": eid, "brand": cur["id"], "field": path, "label": label, "old": a, "new": b, "at": at, "run": run_id})
    return out


# ---------------------------------------------------------------- main
def run(only: set[str] | None = None, offline: Path | None = None, data_dir: Path = ROOT / "data",
        config: Path = ROOT / "config" / "brands.json", now: datetime | None = None) -> dict:
    now = now or now_utc()
    run_id = now.strftime("%Y%m%dT%H%M%SZ")
    cfg = load_json(config, {"brands": []})
    research = load_json(data_dir / "research.json", {"brands": {}})["brands"]
    state = load_json(data_dir / "state.json", {"brands": {}, "http_cache": {}})
    prev_dash = load_json(data_dir / "dashboard.json", {"brands": []})
    prev_by_id = {b["id"]: b for b in prev_dash.get("brands", [])}
    changes = load_json(data_dir / "changes.json", {"events": []})
    seen_ids = {e["id"] for e in changes["events"]}
    fetcher = Fetcher(state.setdefault("http_cache", {}), offline)

    brands_out, new_events = [], []
    for brand in sorted(cfg["brands"], key=lambda b: (b.get("priority", 3), b["name"].lower())):
        if not brand.get("enabled", True):
            continue
        bid = brand["id"]
        prev_scan = state["brands"].get(bid, {})
        prev = prev_by_id.get(bid)
        if only and bid not in only:
            if prev:
                brands_out.append(prev)
            continue
        try:
            scan_rec, auto = scan_brand(brand, fetcher, prev_scan, now)
        except Exception as e:  # one broken brand must never stop the run
            scan_rec = {**prev_scan, "last_attempt": iso(now), "ok": False,
                        "errors": [{"url": None, "error": f"scanner crash: {type(e).__name__}: {e}"[:200]}],
                        "consecutive_failures": prev_scan.get("consecutive_failures", 0) + 1}
            auto = None
        state["brands"][bid] = scan_rec
        r = research.get(bid, {})
        last_ok = parse_iso(scan_rec.get("last_success"))
        stale = not last_ok or now - last_ok > STALE_AFTER
        sale = resolve_sale(r.get("sale"), auto, (prev or {}).get("sale"), scan_rec["ok"], now)
        if stale and sale["basis"] not in ("verified",):
            sale["status"] = "NEEDS_CHECKING" if sale["status"] in ("NOT_ANNOUNCED",) else sale["status"]
        rec = {
            "id": bid, "name": brand["name"], "category": brand["category"], "priority": brand.get("priority", 3),
            "storefront": brand.get("storefront"), "notes": brand.get("notes"),
            "links": {"home": brand["urls"].get("home"), "sale": (sale.get("source_url") or (brand["urls"].get("sale") or [None])[0]),
                      "returns": brand["urls"].get("returns"), "shipping": brand["urls"].get("shipping")},
            "sale": sale,
            "policy": build_policy(r.get("policy"), scan_rec.get("policy", {})),
            "scan": {k: scan_rec.get(k) for k in ("last_attempt", "last_success", "ok", "pages_ok", "pages_tried", "errors", "consecutive_failures", "discovered")}
                    | {"stale": stale, "policy_errors": scan_rec.get("policy", {}).get("errors", [])},
        }
        for ev in diff(prev, rec, run_id, iso(now)):
            if ev["id"] not in seen_ids:
                new_events.append(ev)
                seen_ids.add(ev["id"])
        brands_out.append(rec)
        status_line = f"{bid:22} {sale['status']:15} basis={sale['basis']:8} pages={scan_rec.get('pages_ok')}/{scan_rec.get('pages_tried')}"
        print(status_line + (f"  errors={len(scan_rec['errors'])}" if scan_rec.get("errors") else ""), flush=True)
        if scan_rec.get("errors") and offline is None:  # fixture runs (tests) shouldn't annotate the Actions log
            for e in scan_rec["errors"]:
                print(f"::warning title={bid}::{e['url']} -> {e['error']}", flush=True)

    changes["events"] = (new_events + changes["events"])[:MAX_CHANGES]
    for b in brands_out:
        b["recent_changes"] = [e for e in changes["events"] if e["brand"] == b["id"]][:8]
        b["changed_this_run"] = any(e["run"] == run_id and e["field"] != "brand" for e in b["recent_changes"])
    ok_count = sum(1 for b in brands_out if b["scan"]["ok"])
    meta = {
        "generated_at": iso(now), "run_id": run_id, "timezone": "Australia/Sydney", "currency": "AUD",
        "black_friday": "2026-11-27", "cyber_monday": "2026-11-30",
        "brands_total": len(brands_out), "scan_ok": ok_count, "scan_failed": len(brands_out) - ok_count,
        "last_successful_scan": iso(now) if ok_count else prev_dash.get("meta", {}).get("last_successful_scan"),
        "counts": {s: sum(1 for b in brands_out if b["sale"]["status"] == s)
                   for s in ("LIVE", "UPCOMING", "EARLY_ACCESS", "NOT_ANNOUNCED", "ENDED", "NEEDS_CHECKING")},
        "new_events": len(new_events),
    }
    dash = {"meta": meta, "brands": brands_out}
    save_json(data_dir / "dashboard.json", dash)
    save_json(data_dir / "changes.json", changes)
    save_json(data_dir / "state.json", state)
    print(f"done: {ok_count}/{len(brands_out)} brands reachable, {len(new_events)} new change events", flush=True)
    return dash


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="comma-separated brand ids")
    ap.add_argument("--offline", help="fixture dir instead of network")
    a = ap.parse_args()
    run(set(a.only.split(",")) if a.only else None, Path(a.offline) if a.offline else None)
