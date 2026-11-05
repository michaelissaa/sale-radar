# Batch 2 (added 2026-11-05 evening): brands the user asked to add plus suggested additions.
# Executed by build_research.py with R, S, P, SALE, T in scope. VERIFIED = sale records checked directly.
T2 = "2026-11-05T10:00:00+00:00"
VERIFIED = {"evdnce", "pe-nation", "nimble", "lorna-jane", "bo-tee", "2xu"}
EXTRA = {}


def SALE2(*a, **kw):
    return {**SALE(*a, **kw), "verified_at": T2}


def P2(*a):
    return {**P(*a), "verified_at": T2}


EXTRA["evdnce"] = {
    "sale": SALE2("LIVE", "https://evdnce.com/", "UP TO 50% OFF SITEWIDE LIVE NOW",
                  name="Sitewide sale (not labelled Black Friday)", discount_text="Up to 50% off sitewide", discount_max_pct=50,
                  discount_kind="up_to", scope="SITEWIDE", code_required="NO",
                  conditions="'Up to' 50%: discounts vary by item. The banner doesn't say Black Friday or give an end date."),
    "policy": P2("sourced", "14-day returns via the Loop portal; $9.95 handling and return postage deducted from refunds. Free shipping over AU$250.",
                 R("YES", "CONDITIONAL", "CONDITIONAL", instore="NA", label="YES", days=14, sale_ex="CONDITIONAL", refund="Refund, exchange or store credit",
                   cost="$9.95 deducted from refunds", cond="Final sale, underwear, socks and headwear excluded. Unworn with tags.",
                   src="https://evdnce.com/pages/help-center",
                   ev="A handling and return postage fee of $9.95 is deducted from your refund"),
                 S("CONDITIONAL", 250, src="https://evdnce.com/", ev="Free shipping on orders over AU$250")),
}
EXTRA["aybl"] = {
    "sale": SALE2("UPCOMING", "https://www.aybl.com/pages/black-friday-2026",
                  "Black Friday is coming. Sign up for Early Access and shop up to 60% off sitewide 1 hour before everyone else.",
                  name="AYBL Black Friday 2026", discount_text="Up to 60% off sitewide", discount_max_pct=60, discount_kind="up_to", scope="SITEWIDE",
                  early_access="Sign up to shop 1 hour before everyone else",
                  conditions="Announced, no start date yet. AYBL serves one global store (UK-based)."),
    "policy": P2("sourced", "30-day returns but return postage is deducted for Australia (free returns only UK/US/EU). Final Sale excluded. Free shipping over $90.",
                 R("YES", "NO", "NO", instore="NA", label="YES", days=30, sale_ex="YES", refund="Original payment method; no exchanges",
                   cond="Free returns only in the UK, USA, NL, DE and FR; for Australia the portal shows the cost and deducts it.",
                   src="https://www.aybl.com/pages/returns", ev="We currently only offer free returns in the UK, USA, NL, DE & FR... Any costs will be deducted from the final refund"),
                 S("CONDITIONAL", 90, 8, restr="Ships from the UK. Express $30, free over $250.", src="https://www.aybl.com/pages/shipping",
                   ev="AUSTRALIA ... Standard | 3-5 working days | $8 | $90")),
}
EXTRA["stax"] = {
    "sale": SALE2("NOT_ANNOUNCED", "https://stax.com.au/",
                  "Store is behind a password page for a new collection launch (public access opens 6 Nov, 9am AEDT). No Black Friday announcement seen.",
                  confidence="medium"),
    "policy": P2("sourced", "Free returns only if you pay the returns option at checkout; otherwise a handling fee applies. Full policy not visible while the store is locked.",
                 R("UNKNOWN", "CONDITIONAL", "CONDITIONAL", src="https://stax.com.au/policies/refund-policy",
                   ev="By paying now on your order, you will qualify for a return at no extra cost... If you don't opt to pay the fee now... you will be responsible for the cost of the handling fee."),
                 S("UNKNOWN", src="https://stax.com.au/")),
}
EXTRA["bo-tee"] = {
    "sale": SALE2("EARLY_ACCESS", "https://boandtee.com/pages/30-off", "early access is now live sign up below to be emailed the exclusive link",
                  name="30% off event (not labelled Black Friday)", discount_text="30% off", discount_max_pct=30, discount_kind="flat",
                  early_access="Email sign-up gives an exclusive early-access link",
                  conditions="Page is titled '30% Off'; scope and end date not stated."),
    "policy": P2("sourced", "14 days for refund or exchange (28 for store credit). First return free in some cases; customs may apply from the UK.",
                 R("YES", "CONDITIONAL", "CONDITIONAL", instore="NA", label="YES", days=14, note="14 days refund/exchange, 28 days store credit",
                   refund="Refund, exchange or store credit", src="https://boandtee.com/pages/returns-information",
                   ev="Orders must be returned within 14 days of delivery for a full refund or exchange extended to 28 days for store credit"),
                 S("UNKNOWN", restr="Ships from the UK; customs and duties may be payable on arrival.", src="https://boandtee.com/pages/delivery",
                   ev="For countries outside of Europe, customs and duties may be payable on arrival.")),
}
EXTRA["pe-nation"] = {
    "sale": SALE2("UPCOMING", "https://www.pe-nation.com/pages/black-friday-faqs",
                  "The P.E Nation Black Friday sale begins Wednesday 11 November 2026 and runs through Cyber Monday on Monday 30 November... Styles are up to 70% off for the full Black Friday event.",
                  name="P.E Nation Black Friday 2026", discount_text="Up to 70% off selected styles", discount_max_pct=70, discount_kind="up_to",
                  scope="SELECTED", start="2026-11-11", end="2026-11-30", dates_confirmed=True, code_required="NO",
                  early_access="Mailing list early access; SMS list gets VIP perks"),
    "policy": P2("sourced", "30-day free returns, but sale and Black Friday items are store credit or in-store exchange only; final sale not returnable. Free shipping over $150.",
                 R("YES", "YES", "YES", instore="CONDITIONAL", label="YES", days=30, sale_ex="CONDITIONAL",
                   refund="Full price: refund. Sale: store credit (12 months) or in-store exchange",
                   cond="Final Sale items cannot be returned unless faulty.", src="https://www.pe-nation.com/pages/returns",
                   ev="Sale items... Store credit (valid for 12 months) or Exchange (in-store only)... Final Sale items are final"),
                 S("CONDITIONAL", 150, 7.95, src="https://www.pe-nation.com/pages/shipping",
                   ev="$7.95 AUD for orders under $150.00 AUD; FREE for orders over $150.00 AUD")),
}
EXTRA["nimble"] = {
    "sale": SALE2("UPCOMING", "https://nimbleactivewear.com/pages/black-friday-sale", "50% OFF* Tuesday 10th November ... we'll be launching sale on Tuesday 10th November",
                  name="Black Friday Sale", discount_text="50% off*", discount_max_pct=50, discount_kind="flat", scope="SELECTED",
                  start="2026-11-10", dates_confirmed=True, code_required="NO",
                  conditions="Asterisk: conditions apply. Launch time not yet published; sign up to be told."),
    "policy": P2("sourced", "30-day returns; refunds cost $10, exchanges and store credit free. Promo items: store credit only. Free shipping over $175.",
                 R("YES", "CONDITIONAL", "CONDITIONAL", instore="CONDITIONAL", days=30, sale_ex="CONDITIONAL", refund="Refund less $10, or free exchange/credit",
                   cost="$10 on refunds", cond="Promotional items: store credit. Final sale not returnable. No exchanges on sale styles.",
                   src="https://nimbleactivewear.com/pages/what-is-your-returns-policy", ev="$10 return fee applies to refunds; Exchanges and store credit are free"),
                 S("CONDITIONAL", 175, 11.95, src="https://nimbleactivewear.com/pages/shipping", ev="Standard Post ... $11.95 (free over $175)")),
}
EXTRA["lorna-jane"] = {
    "sale": SALE2("LIVE", "https://www.lornajane.com.au/collections/black-friday-event",
                  "Black Friday | 20% Off* ... Offer T&Cs: Black Friday - Up To 40% Off Selected Styles",
                  name="Black Friday", discount_text="Up to 40% off selected styles", discount_max_pct=40, discount_kind="up_to", scope="SELECTED",
                  conditions="Collection headline says 20% off; T&Cs say up to 40% off selected styles."),
    "policy": P2("sourced", "Sale styles: exchange or gift card only (30 days), no refunds. Free in-store returns. Free shipping over $160.",
                 R("CONDITIONAL", "CONDITIONAL", "NO", instore="YES", label="NO", days=30, note="30 days; 1 Nov-25 Dec purchases until 31 Jan 2027",
                   sale_ex="CONDITIONAL", refund="Full price: refund. Sale: exchange or gift card",
                   cond="Final-sale tagged items have no change-of-mind return.", src="https://www.lornajane.com.au/pages/returns-exchanges",
                   ev="we offer an Exchange or Gift Card (3-year expiry) on all purchases of Sale styles"),
                 S("CONDITIONAL", 160, 12.95, src="https://www.lornajane.com.au/pages/shipping-information", ev="Pay $12.95 or spend $160 to receive complimentary shipping.")),
}
EXTRA["2xu"] = {
    "sale": SALE2("UPCOMING", "https://2xu.com/pages/black-friday-early-access", "Sign up for Black Friday early access now",
                  name="Black Friday", early_access="Sign up for early access"),
    "policy": P2("sourced", "30-day change-of-mind refunds for full-price and outlet items. Free shipping over $80.",
                 R("YES", "UNKNOWN", "UNKNOWN", days=30, sale_ex="CONDITIONAL", refund="Original payment method",
                   cond="Full-priced and/or outlet items; underwear and socks excluded.", src="https://2xu.com/pages/terms-and-conditions",
                   ev="We will allow a change of mind return for refund, provided that the item in question is: A full priced and/or outlet item; returned within 30 days"),
                 S("CONDITIONAL", 80, 8.5, restr="Express $12.50, free over $150.", src="https://2xu.com/pages/shipping-and-tracking",
                   ev="Standard shipping is $8.50 or free on orders over $80.")),
}
EXTRA["vuori"] = {
    "sale": SALE2("NOT_ANNOUNCED", "https://vuoriclothing.com.au/", "Regular sale sections only; no Black Friday announcement seen.", confidence="medium"),
    "policy": P2("sourced", "Free express shipping and free returns on all orders (AU store). Returns window not stated.",
                 R("YES", "YES", "YES", src="https://vuoriclothing.com.au/", ev="Free Express Shipping and Free Returns on All Orders"),
                 S("YES", restr="Ships from San Diego by DHL (3-4 business days).", src="https://vuoriclothing.com.au/",
                   ev="Free Express Shipping and Free Returns on All Orders")),
}
EXTRA["on-running"] = {
    "sale": SALE2("UPCOMING", "https://www.on.com/en-au/collection/black-friday",
                  "Sign up for Black Friday and Cyber Monday, limited drops, new arrivals and more. Straight to your inbox.",
                  confidence="low", conditions="Only an email sign-up for Black Friday news; no sale details."),
    "policy": P2("sourced", "Free returns; purchases 21 Oct to 31 Dec get 90 days. Free standard shipping including customs.",
                 R("YES", "YES", "YES", instore="YES", label="YES", days=90, note="90 days for 21 Oct-31 Dec 2026 purchases", sale_ex="CONDITIONAL",
                   refund="Original payment method", cond="Limited editions and last-season items: refund only, no exchange.",
                   src="https://www.on.com/en-au/faq/returns-and-exchanges",
                   ev="Any product purchased between October 21 and December 31, 2026 ... Australia ... will benefit from extended 90 day returns"),
                 S("YES", src="https://www.on.com/en-au/faq/shipping",
                   ev="We cover shipping costs and any relevant customs charges in most countries (for standard-level shipping).")),
}
EXTRA["hoka"] = {
    "sale": SALE2("NOT_ANNOUNCED", "https://au.hoka.com/", "Regular promotions only; no Black Friday announcement seen.", confidence="medium"),
    "policy": P2("sourced", "60-day returns for 5 Nov to 31 Dec purchases, sale items included. Postal return label costs $10; free in store. Free shipping over $200.",
                 R("YES", "CONDITIONAL", "NO", instore="YES", label="NO", days=60, note="60 days for 5 Nov-31 Dec purchases, otherwise 30", sale_ex="NO",
                   cost="$10 postal label", refund="Original payment method",
                   src="https://help.au.hoka.com/hc/en-us/articles/4899736773657-WHAT-IS-YOUR-CHANGE-OF-MIND-RETURNS-POLICY",
                   ev="you can return any unwanted products, including sale items ... purchases made between November 5 and December 31 come with an extended 60-day return window."),
                 S("CONDITIONAL", 200, src="https://au.hoka.com/", ev="Free Shipping on all orders $200+")),
}
