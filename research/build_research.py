"""Builds data/research.json from hand-curated entries (initial research pass 2026-11-05).

verification: "verified" = checked directly against the cited retailer page during research.
              "sourced"  = from an automated research pass (Firecrawl agent) with source URL + quote, not double-checked.
Edit this file (or research/extra.py), then run: python research/build_research.py
"""
import json
from pathlib import Path

T = "2026-11-05T09:00:00+00:00"  # research pass time (UTC) = 8pm Sydney


def R(cm, fr, frp, instore="UNKNOWN", label="UNKNOWN", days=None, sale_ex="UNKNOWN", refund=None, cond=None, src=None, ev=None, cost=None, note=None):
    d = dict(change_of_mind=cm, free_returns=fr, free_return_postage=frp, free_instore_returns=instore, prepaid_label=label,
             window_days=days, window_note=note, sale_items_excluded=sale_ex, refund_type=refund, postage_cost=cost,
             conditions=cond, source_url=src, evidence=ev)
    return {k: v for k, v in d.items() if v is not None}


def S(free, thr=None, std=None, au="YES", restr=None, src=None, ev=None):
    d = dict(free_shipping=free, free_threshold_aud=thr, standard_aud=std, ships_to_au=au, restrictions=restr, source_url=src, evidence=ev)
    return {k: v for k, v in d.items() if v is not None}


def P(verif, summary, returns, shipping):
    return {"verification": verif, "verified_at": T, "summary": summary, "returns": returns, "shipping": shipping}


def SALE(status, src, ev, **kw):
    # sale_type: "black_friday" (default for announced/live promos) or "regular" (a normal sale, not Black Friday branded)
    kw.setdefault("sale_type", "black_friday" if status in ("LIVE", "EARLY_ACCESS", "UPCOMING") else None)
    return {"status": status, "source_url": src, "evidence": ev, "verified_at": T, "confidence": kw.pop("confidence", "high"), **kw}


B = {}

B["gymshark"] = {
    "sale": SALE("UPCOMING", "https://au.gymshark.com/pages/black-friday",
                 "The sale isn't live just yet (we know, brutal timing)... You didn't think we'd reveal the start date and time that easily did you?",
                 name="Gymshark Black Friday & Cyber Monday Sale 2026",
                 expected_note="Gymshark says it offered up to 50% off last Black Friday",
                 early_access="App users and loyalty members get first notice; no 2026 member discount disclosed"),
    "policy": P("verified", "Free returns in Australia via the returns portal, 30 days. Free standard shipping over $100.",
                R("YES", "YES", "YES", days=30, sale_ex="NO", refund="Original payment method",
                  cond="Register returns through the Gymshark portal. Items unworn with tags. Last year's Black Friday purchases got an extended window to 31 Jan; a 2026 extension is not yet stated.",
                  src="https://au.gymshark.com/pages/black-friday",
                  ev="Returns for Gymshark products are free in most regions, including: the UK, US, Canada, Australia, New Zealand..."),
                S("CONDITIONAL", 100, src="https://au.gymshark.com/pages/black-friday", ev="Free standard shipping on orders over $100")),
}
B["salomon"] = {
    "sale": SALE("NOT_ANNOUNCED", "https://salomon.com.au/collections/womens-black-friday",
                 "Women's and Men's Black Friday collections show 'Black Friday sale now live!' but contain 'No products'. Home page has no sale.",
                 confidence="high",
                 conditions="Corrected 5 Nov: the Black Friday pages are empty placeholders. Salomon's standing outlet has about a third of products marked down; that is not a sale event."),
    "policy": P("sourced", "30-day change-of-mind returns. Free returns only for S/PLUS members, and not on sale items. Free standard delivery for S/PLUS members.",
                R("YES", "CONDITIONAL", "CONDITIONAL", days=30, sale_ex="CONDITIONAL", refund="Original payment method, no online exchanges",
                  cond="S/PLUS (free membership) members get free returns except Sale/Outlet items and winter hardgoods. Outlet items excluded from change-of-mind returns.",
                  src="https://salomon.com.au/pages/returns-2",
                  ev="All S/PLUS members get free returns on their orders excluding Sale Items & Winter Hardgoods."),
                S("CONDITIONAL", 99.95, restr="Free shipping is for S/PLUS members (over $99.95). Express 1-2 days $10.",
                  src="https://salomon.com.au/pages/shipping", ev="Free shipping over $99.95 for S/PLUS members.")),
}
B["lskd"] = {
    "sale": SALE("NOT_ANNOUNCED", "https://www.lskd.co/",
                 "lskd.co/pages/black-friday redirects to the home page; no Black Friday 2026 sale wording found on 5 Nov.", confidence="medium"),
    "policy": P("sourced", "30 days for a refund, 60 days for exchange or store credit. Return postage free only in some cases.",
                R("YES", "CONDITIONAL", "CONDITIONAL", label="YES", days=30, note="30 days refund, 60 days exchange/credit", sale_ex="NO",
                  refund="Refund within 30 days; exchange or store credit within 60 days",
                  cond="Unworn, unwashed, tags on. Hygiene items (underwear, socks, towels, bottles) excluded.",
                  src="https://lskd-au.gorgias.help/en-US/returns-policy-info-92275",
                  ev="You have up to 30 days to return your gear for a refund and 60 days for an exchange or store credit!"),
                S("YES", restr="Site banner advertises free shipping on all orders.", src="https://www.lskd.co/", ev="FREE SHIPPING ON ALL ORDERS")),
}
B["myprotein"] = {
    "sale": SALE("LIVE", "https://au.myprotein.com/c/black-friday/",
                 "HOW DO YOU BLACK FRIDAY? 40% OFF EVERYTHING | DISCOUNT APPLIED. APP EXCLUSIVE | EXTRA 5% OFF | AUTO APPLIES",
                 name="Black Friday 2026 (early)", discount_text="40% off everything", discount_max_pct=40, discount_kind="flat", scope="SITEWIDE",
                 code_required="NO", early_access="Extra 5% off in the app (auto-applies)",
                 expected_note="Myprotein says its Black Friday sale runs through to Cyber Monday (30 Nov); no end date given for the current 40% offer",
                 conditions="Product tiles say the discount is applied automatically. One banner also mentions code 'blackfriday'; check at checkout."),
    "policy": P("verified", "30-day returns for a refund (no exchanges). Free delivery over $150, otherwise from $9.95.",
                R("YES", "UNKNOWN", "UNKNOWN", instore="NA", days=30, sale_ex="NO", refund="Refund only; no exchanges",
                  cond="Clothing unworn and unwashed with tags; hygiene items and opened nutrition excluded. Purchases 1 Nov to 31 Dec can be returned until 30 Jan.",
                  src="https://au.myprotein.com/c/customer-services/returns-policy/",
                  ev="You have 30 days from the date of receiving your item to start a return."),
                S("CONDITIONAL", 150, 9.95, restr="Express is a flat $14.99. Regional areas take longer.",
                  src="https://au.myprotein.com/c/customer-services/delivery-information/", ev="Free shipping over $150")),
}
B["ryderwear"] = {
    "sale": {**SALE("LIVE", "https://au.ryderwear.com/pages/black-friday",
                    "Black Friday Sale is live. Sale starts in: 00 Days 00 Hours 00 Minutes 00 Seconds. Tuesday 3 November 2026 Perth 5am ... 50% off for the first 4 hours",
                    name="Ryderwear Black Friday Sale 2026", discount_text="50% off everything (first 4 hours); sale continuing",
                    discount_max_pct=50, discount_kind="flat", scope="SITEWIDE", code_required="NO",
                    start="2026-11-03T08:00:00+11:00", dates_confirmed=True,
                    conditions="Went live 8am Sydney time, Tue 3 Nov (5am Perth). The store's own prices show every product discounted, up to 80%. End date not stated."),
             "verified_at": "2026-11-05T11:45:00+00:00"},
    "policy": P("sourced", "Black Friday orders: 60 days for store credit or exchange, not refunds. Outlet not returnable. Free shipping over $120.",
                R("YES", "UNKNOWN", "CONDITIONAL", label="NO", days=60, sale_ex="CONDITIONAL", refund="Store credit or exchange for Black Friday orders",
                  cond="Unworn with tags. Outlet items cannot be returned unless faulty. No underwear, socks, towels or gift cards.",
                  src="https://www.ryderwear.com/pages/returns",
                  ev="Black Friday orders can be returned within 60 days of delivery, for store credit or an exchange. Outlet items can't be returned unless faulty."),
                S("CONDITIONAL", 120, restr="Ships from an Australian fulfilment centre.", src="https://www.ryderwear.com/pages/returns",
                  ev="FREE STANDARD SHIPPING OVER $120")),
}
B["echt"] = {
    "sale": SALE("LIVE", "https://echt.com.au/collections/black-friday-2026-up-to-70-off-selected-items",
                 "Black Friday 2026 - Up to 70% Off Selected Items",
                 name="Black Friday 2026", discount_text="Up to 70% off selected items", discount_max_pct=70, discount_kind="up_to", scope="SELECTED",
                 conditions="Collection is live. Extra promotions seen (extra 15% off $135+, free gift over $100) were on ECHT's US storefront and may not apply in Australia."),
    "policy": P("sourced", "40 days for exchange or credit, refunds only within 14 days. You pay return postage unless you bought the free-returns option. Standard AU shipping free.",
                R("YES", "CONDITIONAL", "CONDITIONAL", label="CONDITIONAL", days=40, note="Refund within 14 days; exchange/credit within 40", sale_ex="CONDITIONAL",
                  refund="Refund within 14 days, otherwise store credit",
                  cond="Change-of-mind return postage is the customer's cost; a label is supplied only if free returns were purchased at checkout. Clearance/final sale excluded.",
                  src="https://echt.gorgias.help/en-US/how-do-i-return--exchange-an-item-430440",
                  ev="Return postage for change of mind/incorrect fit is non-refundable and customer's responsibility."),
                S("YES", None, 0, restr="Express $7, free over $100.", src="https://echt.com.au/pages/shipping-info",
                  ev="Australia ... Standard ... Free ... Express ... $7 AUD ... Free on orders over $100 AUD")),
}
B["muscle-nation"] = {
    "sale": SALE("UPCOMING", "https://musclenation.org/pages/black-friday-browse",
                 "Black Friday 50% off everything, 4 hrs only. LAUNCHING TUE 10 NOV, 8AM AEST",
                 name="Black Friday", discount_text="50% off everything", discount_max_pct=50, discount_kind="flat", scope="SITEWIDE",
                 start="2026-11-10T09:00:00+11:00", end="2026-11-10T13:00:00+11:00", dates_confirmed=True,
                 conditions="4 hours only from 8am AEST / 9am AEDT (Sydney). End time is 4 hours after the stated launch."),
    "policy": P("sourced", "15 days to lodge a return. Return postage free only if you chose Checkout Plus. Free AU shipping over $130.",
                R("YES", "CONDITIONAL", "CONDITIONAL", label="CONDITIONAL", days=15, sale_ex="CONDITIONAL", refund="Original payment method or store credit",
                  cond="Lodge via the returns portal within 15 days; unworn and resaleable. Peak sale periods may have a 30-day window. Undergarments, socks and opened supplements excluded.",
                  src="https://musclenation.org/pages/returns-policy",
                  ev="For Australian orders: If you selected Checkout Plus, your return shipping is covered; if you did not select Checkout Plus, you will pay the applicable return shipping fee"),
                S("CONDITIONAL", 130, 9.99, restr="Same-day delivery unavailable during sale events.", src="https://musclenation.org/policies/shipping-policy",
                  ev="Australian Standard | 2-5 Business Days | A$9.99 for orders under A$130")),
}
B["youngla"] = {
    "policy": P("sourced", "60-day returns. Exchanges and store credit get a free label; refunds have a label fee. Free AU shipping over $100.",
                R("YES", "CONDITIONAL", "CONDITIONAL", instore="NO", label="CONDITIONAL", days=60, refund="Original payment, less label fee",
                  cond="Unworn, unwashed, tags on. Original shipping not refunded.",
                  src="https://au.youngla.com/pages/returns-and-exchanges", ev="Returns and exchanges accepted within 60 days of delivery"),
                S("CONDITIONAL", 100, src="https://au.youngla.com/", ev="Free shipping for AU orders over $100 AUD")),
}
B["alphalete"] = {
    "policy": P("sourced", "30-day returns but you pay return postage; no prepaid label or exchanges for international orders. Final Sale excluded.",
                R("YES", "NO", "NO", label="NO", days=30, sale_ex="YES", refund="Original payment method or store credit",
                  cond="International customers self-ship returns and cannot exchange. Customs fees may apply.",
                  src="https://alphaleteathletics.com/pages/faq",
                  ev="Alphalete does not cover the cost of return shipping at this time. ... For international customers (US site), we do not offer exchanges or pre-paid labels"),
                S("UNKNOWN", restr="Ships from the US. Rates shown at checkout; duties/taxes may apply.", src="https://alphaleteathletics.com/pages/faq",
                  ev="Our US site currently ships internationally to: ... Australia")),
}
B["oner-active"] = {
    "policy": P("sourced", "Free 30-day returns with a prepaid label, but discounted and outlet items cannot be returned. Free shipping over $150.",
                R("YES", "YES", "YES", instore="NA", label="YES", days=30, sale_ex="YES", refund="Original card",
                  cond="Discounted or Outlet items are non-returnable (statutory rights still apply), so Black Friday purchases are likely final.",
                  src="https://au.oneractive.com/pages/help-center/returns",
                  ev="Discounted or Outlet items are non-returnable and non-refundable (subject to your statutory rights). ... You won't be charged return fees."),
                S("CONDITIONAL", 150, restr="Free express over $250.", src="https://au.oneractive.com/pages/shipping-policy", ev="Free standard shipping over $150 AUD")),
}
B["hallensteins"] = {
    "policy": P("sourced", "30-day returns at your cost to the AU warehouse. In-store returns only in Queensland. Free shipping over $110.",
                R("YES", "CONDITIONAL", "NO", instore="CONDITIONAL", label="NO", days=30, sale_ex="YES", refund="Refund for warehouse returns",
                  cond="Final Sale items excluded. Queensland stores accept returns and exchanges.",
                  src="https://www.hallensteins.com/au/faqs/shipping", ev="Returns are at the cost of the purchaser"),
                S("CONDITIONAL", 110, 9.99, restr="Express DHL $24.99. No PO Boxes.", src="https://www.hallensteins.com/au/faqs/shipping",
                  ev="Australia: Standard Delivery (3-8 days) - $9.99 or free on orders over $110.")),
}
B["maniere-de-voir"] = {
    "policy": P("sourced", "14-day returns with an A$28.65 return label. Sale items: e-gift card only. Free shipping over A$400.",
                R("YES", "NO", "NO", label="YES", days=14, sale_ex="CONDITIONAL", refund="Full price: original payment. Sale: e-gift card only",
                  cost="A$28.65 via returns portal", src="https://au.manieredevoir.com/pages/delivery-returns",
                  ev="Sale or discounted items are valid for a return to e-gift card only. ... Return via our returns portal for 28.65 AUD"),
                S("CONDITIONAL", 400, 15, restr="Express A$28. Sale periods may have minimum order rules.", src="https://au.manieredevoir.com/pages/delivery-returns",
                  ev="Standard Delivery - A$15 - Free for orders over A$400.")),
}
B["culture-kings"] = {
    "policy": P("sourced", "30 days for exchange or store credit. Online refunds cost an $8.95 handling fee. Free in-store returns.",
                R("YES", "CONDITIONAL", "CONDITIONAL", instore="YES", label="CONDITIONAL", days=30, sale_ex="CONDITIONAL",
                  refund="Exchange or store credit for change of mind; refunds carry a fee", cost="$8.95 handling fee on online refunds",
                  cond="Free return shipping only for full-price footwear over A$100 returned for credit or exchange. Final Sale and hygiene items not returnable.",
                  src="https://www.culturekings.com.au/pages/shipping-returns",
                  ev="You can return your purchase for an exchange or store credit within 30 days if you change your mind"),
                S("CONDITIONAL", 75, 9.95, src="https://www.culturekings.com.au/pages/shipping-returns", ev="AUS Standard | $9.95 AUD or Free over $75 AUD | 3-5 business days")),
}
B["cotton-on"] = {
    "sale": SALE("UPCOMING", "https://cottonon.com/AU/black-friday-cyber-monday/",
                 "Black Friday and Cyber Monday are almost here... The sale you've been waiting for all year is about to kick off. ... What time do the events start online? Telling you now would be cheating.",
                 name="Black Friday & Cyber Monday",
                 early_access="Cotton On & Co Perks members and app users get a VIP head start",
                 expected_note="Cotton On's page cites the industry Black Friday date (Fri 27 Nov) but has not published its own start time"),
    "policy": P("verified", "Change-of-mind returns any time with proof of purchase. Free online returns within Australia, or return in store.",
                R("YES", "YES", "YES", instore="YES", note="No time limit", sale_ex="NO", refund="Original payment method; exchanges in store only",
                  cond="Unworn with tags. Excludes underwear, earrings, cosmetics, third-party brands, gift cards. Original delivery fee not refunded.",
                  src="https://cottonon.com/AU/information-about-returns.html",
                  ev="Products purchased from any Cotton On Group retail or online store can be returned at any time by the customer with proof of purchase"),
                S("CONDITIONAL", 75, 7.95, restr="Perks members: free delivery on first order over $30.", src="https://cottonon.com/AU/delivery-methods.html",
                  ev="Standard - $7.95 or FREE on $75+")),
}
B["abercrombie"] = {
    "sale": SALE("UPCOMING", "https://www.abercrombie.com/shop/wd/black-friday",
                 "Sign up for myAbercrombie and be first to find out about the sale you've been waiting for.",
                 confidence="low", conditions="Seen on the global Black Friday page; Australian dates and discount not stated."),
    "policy": P("sourced", "Australian return and delivery terms could not be verified; the pages served were US-region content.",
                R("UNKNOWN", "UNKNOWN", "UNKNOWN", cond="Official pages fetched were US-store policies.",
                  src="https://www.abercrombie.com/shop/wd/help/online-return-exchange-policy"),
                S("UNKNOWN", au="UNKNOWN", restr="Rates vary by destination; select Australia on the site.",
                  src="https://www.abercrombie.com/shop/wd/help/shipping-handling")),
}

# Remaining brands live in research/extra.py (EXTRA dict) so this file stays readable.
for extra in sorted(Path(__file__).parent.glob("extra*.py")):  # extra.py, extra2.py, ... (later batches win)
    ns = {"R": R, "S": S, "P": P, "SALE": SALE, "T": T}
    exec(extra.read_text(encoding="utf-8"), ns)
    for bid, rec in ns["EXTRA"].items():
        B.setdefault(bid, {}).update(rec)
    VERIFIED_EXTRA = ns.get("VERIFIED", set())
    globals().setdefault("_verified_extra", set()).update(VERIFIED_EXTRA)

# Sale records re-checked directly against the retailer page on 5 Nov (others came from the research agent).
VERIFIED_SALES = {"gymshark", "salomon", "lskd", "myprotein", "ryderwear", "echt", "muscle-nation", "cotton-on",
                  "the-iconic", "hm", "new-balance", "reebok", "under-armour"} | globals().get("_verified_extra", set())
for bid, rec in B.items():
    if "sale" in rec:
        rec["sale"]["verification"] = "verified" if bid in VERIFIED_SALES else "sourced"

out = Path(__file__).resolve().parent.parent / "data" / "research.json"
out.write_text(json.dumps({"generated": T, "brands": B}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"wrote {len(B)} brands to {out}")
