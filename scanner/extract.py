"""Pure text-extraction helpers. No network. Tested in test_scan.py."""
from __future__ import annotations

import re
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

SKIP_TAGS = {"script", "style", "noscript", "svg", "template", "head"}


class _PageParser(HTMLParser):
    def __init__(self, base_url: str):
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.skip = 0
        self.text: list[str] = []
        self.links: list[tuple[str, str]] = []
        self._href: str | None = None
        self._anchor_text: list[str] = []
        self.title = ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self._in_title = True
        if tag in SKIP_TAGS:
            self.skip += 1
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self._href = urljoin(self.base_url, href)
                self._anchor_text = []

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag in SKIP_TAGS and self.skip:
            self.skip -= 1
        if tag == "a" and self._href:
            self.links.append((self._href, " ".join(self._anchor_text).strip()))
            self._href = None

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self.skip:
            return
        s = data.strip()
        if s:
            self.text.append(s)
            if self._href is not None:
                self._anchor_text.append(s)


def parse_html(html: str, base_url: str) -> dict:
    p = _PageParser(base_url)
    try:
        p.feed(html)
    except Exception:  # malformed HTML must not kill a scan
        pass
    text = re.sub(r"\s+", " ", " ".join(p.text))
    return {"title": p.title.strip(), "text": text, "links": p.links}


CAMPAIGN_RE = re.compile(r"black[-_ ]?friday|cyber[-_ ]?monday|bfcm|cyber[-_ ]?week|early[-_ ]?access|pre[-_ ]?sale|click[-_ ]?frenzy|singles[-_ ]?day", re.I)


def discover_campaign_links(links: list[tuple[str, str]], home_url: str, limit: int = 5) -> list[str]:
    """Same-site links whose URL or anchor text looks like a BF/Cyber campaign page.

    Pass the final (post-redirect) URL as home_url so redirected domains still match.
    """
    host = urlparse(home_url).netloc.removeprefix("www.")
    home_clean = urlparse(home_url)._replace(query="", fragment="").geturl().rstrip("/")
    out: list[str] = []
    for href, label in links:
        u = urlparse(href)
        if u.scheme not in ("http", "https"):
            continue
        if u.netloc.removeprefix("www.") != host:
            continue
        if "/products/" in u.path or "/p/" in u.path:  # product pages inside a BF collection aren't campaign pages
            continue
        if CAMPAIGN_RE.search(u.path) or CAMPAIGN_RE.search(label or ""):
            clean = u._replace(query="", fragment="").geturl()
            if clean.rstrip("/") != home_clean and clean not in out:
                out.append(clean)
        if len(out) >= limit:
            break
    return out


BF_RE = re.compile(r"black\s*friday|cyber\s*monday|cyber\s*week|bfcm", re.I)
UPTO_RE = re.compile(r"up\s*to\s*(\d{1,2})\s*%\s*off", re.I)
FLAT_RE = re.compile(r"(?<!up to )(?<!\d)(\d{1,2})\s*%\s*off", re.I)
SITEWIDE_RE = re.compile(r"\b(sitewide|site-wide|storewide|store-wide|everything|all orders|entire (site|store|range))\b", re.I)
CODE_RE = re.compile(r"(?:use|with|enter|apply)\s+(?:the\s+)?(?:promo\s+|discount\s+)?code[:\s]+[\"'“]?([A-Z0-9]{3,20})\b")
# Bare "sign up" is everywhere in nav bars ("Log In / Sign Up"), so require sale-specific phrasing.
FUTURE_RE = re.compile(r"coming soon|is coming|almost here|not live|isn.t live|starts? (?:on|in|soon)|launch(?:es|ing) (?:on|soon)|sign ?up (?:to|for|now to|below to)|register (?:for|to|your interest)|notify me|get notified|join the (?:wait|vip)|be the first|first to know|countdown|save the date", re.I)
EARLY_RE = re.compile(r"early access|members?[- ]only|vip access|members get first", re.I)
DATE_RE = re.compile(
    r"\b(\d{1,2})(?:st|nd|rd|th)?\s+(nov(?:ember)?|dec(?:ember)?)\b|\b(nov(?:ember)?|dec(?:ember)?)\s+(\d{1,2})(?:st|nd|rd|th)?\b",
    re.I,
)
FREESHIP_RE = re.compile(
    r"free (?:standard |express )?(?:shipping|delivery)[^.$]{0,40}?(?:over|above|orders of|spend(?:ing)?|on orders over)\s*(?:A?U?\$|AUD\s?)(\d{2,4})",
    re.I,
)


def _window(text: str, m: re.Match, size: int = 220) -> str:
    a, b = max(0, m.start() - size // 2), min(len(text), m.end() + size // 2)
    return text[a:b].strip()


def detect_signals(text: str) -> dict:
    """Return sale signals found in page text. Only reports what is literally on the page."""
    bf = BF_RE.search(text)
    sig: dict = {
        "bf_mentioned": bool(bf),
        "discount_text": None,
        "discount_max_pct": None,
        "discount_kind": None,  # "up_to" | "flat"
        "sitewide_hint": False,
        "code": None,
        "future_language": False,
        "early_access": False,
        "dates_seen": [],
        "evidence": None,
        "free_shipping_threshold_hint": None,
    }
    # Prefer discounts that appear near a Black Friday mention.
    region = text
    if bf:
        region = text[max(0, bf.start() - 400): bf.end() + 600]
        sig["evidence"] = _window(text, bf)
    # Prefer discounts after the BF mention (banners read "Black Friday: 40% off"), then the closest before it.
    after = text[bf.start(): bf.end() + 600] if bf else text
    before = text[max(0, bf.start() - 150): bf.start()] if bf else ""
    upto = UPTO_RE.search(after) or UPTO_RE.search(before)
    flat = FLAT_RE.search(after) or (list(FLAT_RE.finditer(before)) or [None])[-1]
    if upto:
        sig.update(discount_text=upto.group(0), discount_max_pct=int(upto.group(1)), discount_kind="up_to")
    elif flat:
        sig.update(discount_text=flat.group(0), discount_max_pct=int(flat.group(1)), discount_kind="flat")
    if sig["discount_text"]:
        m = re.search(re.escape(sig["discount_text"]), region)
        near = region[max(0, m.start() - 80): m.end() + 80] if m else ""
        sig["sitewide_hint"] = bool(SITEWIDE_RE.search(near))
    code = CODE_RE.search(region)
    if code:
        sig["code"] = code.group(1)
    if bf:
        sig["future_language"] = bool(FUTURE_RE.search(region))
        sig["early_access"] = bool(EARLY_RE.search(region))
        sig["dates_seen"] = sorted({m.group(0).strip() for m in DATE_RE.finditer(region)})[:6]
    fs = FREESHIP_RE.search(text)
    if fs:
        sig["free_shipping_threshold_hint"] = int(fs.group(1))
    return sig


def classify(sig: dict) -> tuple[str, str]:
    """Map page signals to (status, confidence). Never infers dates.

    LIVE needs BF wording AND a discount AND no future-tense language.
    """
    if not sig["bf_mentioned"]:
        return "NOT_ANNOUNCED", "low"
    if sig["early_access"] and sig["discount_text"] and not sig["future_language"]:
        return "EARLY_ACCESS", "medium"
    if sig["future_language"] or sig["early_access"]:
        return "UPCOMING", "low"
    if sig["discount_text"]:
        return "LIVE", "medium"
    # BF mentioned with no discount and no future wording: ambiguous (could be a nav label).
    return "NEEDS_CHECKING", "low"
