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

VERIFIED |= {"foot-locker", "rebel", "general-pants", "country-road", "glue-store"}

EXTRA["rebel"] = {
    "sale": SALE2("EARLY_ACCESS", "https://www.rebelsport.com.au/help-centre/promotions", "Black Friday Early Deal - 30% Off Selected Nike Running Shoes",
                  name="Black Friday Early Deal", discount_text="30% off selected Nike running shoes", discount_max_pct=30, discount_kind="flat",
                  scope="SELECTED", confidence="medium", conditions="Listed on Rebel's promotions page; end date not shown. Other Christmas deals run 29 Oct to 26 Nov."),
    "policy": P2("sourced", "30-day change-of-mind returns; free returns on online orders under 10kg (conditions apply). Free delivery over $150 on tagged items.",
                 R("YES", "CONDITIONAL", "CONDITIONAL", days=30, src="https://www.rebelsport.com.au/help-centre/refunds-and-returns",
                   ev="30 day change of mind returns", cond="Free returns for online orders under 10kg via ParcelPoint and Australia Post (details not fully verified)."),
                 S("CONDITIONAL", 150, restr="Only items tagged 'Free Delivery over $150'; bulky/boxed items excluded.",
                   src="https://www.rebelsport.com.au/help-centre/shipping-and-delivery", ev="Free Delivery over $150'. This offer excludes bulky items")),
}
EXTRA["jd-sports"] = {
    "sale": SALE2("UPCOMING", "https://www.jd-sports.com.au/collections/offers-the-north-face", "Black Friday 2026 Coming Soon", confidence="medium"),
    "policy": P2("sourced", "30-day refunds; you pay postage for change-of-mind returns by post. In-store returns accepted. Free delivery over $150.",
                 R("YES", "CONDITIONAL", "NO", instore="YES", label="CONDITIONAL", days=30, sale_ex="CONDITIONAL", refund="Original payment method",
                   cond="Swimwear, underwear and jewellery excluded. Free label only for faulty items.",
                   src="https://www.jd-sports.com.au/pages/terms-and-conditions",
                   ev="Unless the Goods are faulty or incorrectly supplied, You are responsible for the risk and cost of returning the Goods to Us"),
                 S("CONDITIONAL", 150, src="https://www.jd-sports.com.au/", ev="FREE DELIVERY ON ALL ORDERS OVER $150")),
}
EXTRA["foot-locker"] = {
    "sale": SALE2("UPCOMING", "https://www.footlocker.com.au/en/blackfriday.html",
                  "Black Friday Sale YOU'RE IN Keep an eye on your inbox for first access and exclusive FLX Rewards offers. Black Friday alerts first with SMS or the app",
                  name="Black Friday Sale 2026", early_access="FLX Rewards members get first access"),
    "policy": P2("sourced", "Returns in any Foot Locker store or by mail; window and fees not verified. Free standard delivery over $150.",
                 R("YES", "CONDITIONAL", "UNKNOWN", instore="YES", src="https://help.footlocker.com.au/hc/en-gb/articles/34438200648219-Returns-Exchanges",
                   ev="Take the item(s) you wish to return to any Foot Locker store ... along with the original card used for the purchase"),
                 S("CONDITIONAL", 150, src="https://www.footlocker.com.au/en/terms/terms.html", ev="Free standard delivery is eligable on all orders over $150 AUD within Australia.")),
}
EXTRA["platypus"] = {
    "sale": SALE2("UPCOMING", "https://www.platypusshoes.com.au/post/the-platypus-guide-to-black-friday-and-cyber-monday.html",
                  "Platypus has published a 2026 Black Friday and Cyber Monday guide (per research pass).", confidence="low",
                  expected_note="The guide quotes the industry dates (27 to 30 Nov); Platypus hasn't confirmed its own sale dates",
                  conditions="Could not be re-checked directly (page needs JavaScript)."),
    "policy": P2("sourced", "60-day change-of-mind returns including sale items. Postal label costs $10; free in store. Free express shipping over $150.",
                 R("YES", "CONDITIONAL", "NO", instore="YES", label="NO", days=60, sale_ex="NO", cost="$10 return label", refund="Original payment method",
                   src="https://help.platypusshoes.com.au/hc/en-us/articles/360045681613-WHAT-IS-YOUR-CHANGE-OF-MIND-RETURNS-POLICY",
                   ev="you can return any unwanted products, including sale items ... purchase and print your $10 return shipping label."),
                 S("CONDITIONAL", 150, src="https://www.platypusshoes.com.au/", ev="Free Express Shipping On All Orders Over $150")),
}
EXTRA["the-north-face"] = {
    "sale": SALE2("UPCOMING", "https://thenorthface.com.au/black-friday-sale.html", "Black Friday and Cyber Monday 2026 will feature some of our lowest prices of the year.",
                  confidence="low", conditions="Evergreen information page; no dates or discounts published."),
    "policy": P2("sourced", "30-day returns including sale items. Free standard shipping Australia-wide.",
                 R("YES", "UNKNOWN", "UNKNOWN", days=30, sale_ex="NO", refund="Exchange or refund", src="https://thenorthface.com.au/black-friday-sale.html",
                   ev="sale items can be returned. Simply return any unused item within 30 days for an exchange or refund."),
                 S("YES", None, 0, restr="Express $15 flat.", src="https://thenorthface.com.au/",
                   ev="We offer free standard shipping on all orders Australia-wide.")),
}
EXTRA["represent"] = {
    "sale": SALE2("UPCOMING", "https://row.representclo.com/pages/black-friday-faqs", "The Vault is opening. BLACK FRIDAY 2026 is imminent.", confidence="medium"),
    "policy": P2("sourced", "14 days to send items back for a refund. Shipping to AU $20, free over $420.",
                 R("YES", "UNKNOWN", "UNKNOWN", instore="NA", days=14, refund="Full refund", cond="Unused, unaltered condition.",
                   src="https://row.representclo.com/pages/shipping-returns-product-page", ev="you've got 14 days to send back your items for a full refund"),
                 S("CONDITIONAL", 420, 20, restr="Ships from the UK.", src="https://row.representclo.com/pages/shipping-returns-product-page",
                   ev="Australia $20 AUD (FREE on orders over $420 AUD)")),
}
EXTRA["stussy"] = {
    "sale": SALE2("NOT_ANNOUNCED", "https://stussy.com.au/", "No Black Friday announcement; Stussy says it does not offer codes online.", confidence="medium"),
    "policy": P2("sourced", "Return requests must be emailed within 3 days of delivery. Standard shipping $12, no free-shipping threshold found.",
                 R("CONDITIONAL", "UNKNOWN", "UNKNOWN", instore="NA", days=3, cond="Email online@stussy.com.au within 3 days. Some items final sale.",
                   src="https://stussy.com.au/pages/shipping-returns", ev="To request a return / exchange please email online@stussy.com.au within 3 days of receiving your order."),
                 S("NO", None, 12, src="https://stussy.com.au/pages/shipping-returns", ev="Standard - $12")),
}
EXTRA["glue-store"] = {
    "sale": SALE2("NOT_ANNOUNCED", "https://www.gluestore.com.au/",
                  "Glue Store single media Launching November. Sign up and receive 15% off your first order when we launch",
                  confidence="high", conditions="Online store is closed (password page) and relaunching in November. 15% off first order for sign-ups at launch."),
    "policy": P2("unverified", "Online store closed for relaunch; current returns and delivery terms not available.",
                 R("UNKNOWN", "UNKNOWN", "UNKNOWN"), S("UNKNOWN", au="UNKNOWN")),
}
EXTRA["general-pants"] = {
    "sale": SALE2("LIVE", "https://www.generalpants.com/", "EXTRA 50% OFF SALE*",
                  name="Extra 50% off sale (not labelled Black Friday)", discount_text="Extra 50% off sale items", discount_max_pct=50, discount_kind="flat",
                  scope="SELECTED", conditions="Applies to items already on sale. Research pass saw it marked 'EXTENDED'; no end date."),
    "policy": P2("sourced", "Full-price items: 30-day returns by Refundid portal or in store. Final Sale not returnable. Free shipping over $145.",
                 R("CONDITIONAL", "CONDITIONAL", "UNKNOWN", instore="CONDITIONAL", days=30, sale_ex="CONDITIONAL", refund="Original payment method",
                   cond="Returns only for full-price items; FINAL SALE excluded.", src="https://www.generalpants.com/pages/returns",
                   ev="We accept returns and exchanges for full-price items purchased online within 30 days of delivery"),
                 S("CONDITIONAL", 145, 10, restr="Express $15 flat.", src="https://www.generalpants.com/pages/delivery",
                   ev="STANDARD | Up to 5 Business Days | FREE For Orders Over $145; $10 For Orders Under $145")),
}
EXTRA["universal-store"] = {
    "sale": SALE2("NOT_ANNOUNCED", "https://www.universalstore.com/", "Regular sale section only; no Black Friday announcement seen.", confidence="medium"),
    "policy": P2("sourced", "40-day returns and Universal Store pays return shipping. Free express over $145; standard $10.",
                 R("YES", "YES", "YES", days=40, refund="Original payment method",
                   cond="Unworn with tags; hygiene stickers on swimwear and underwear. Original shipping not refunded.",
                   src="https://www.universalstore.com/pages/all-returns", ev="we'll help you with an exchange or refund within 40 days from purchase. ... we will cover the expense of your return shipment to us"),
                 S("CONDITIONAL", 145, 10, restr="$145 threshold gives free Express; Standard is $10 on all orders.",
                   src="https://www.universalstore.com/pages/shipping", ev="FREE For orders over $145 / $15 For orders under $145 ... $10 for all orders")),
}
EXTRA["levis"] = {
    "sale": SALE2("NOT_ANNOUNCED", "https://levis.com.au/pages/promotions-terms", "Latest dated promotion was a Mid-Season Sale that ended 20 Sep 2026; no Black Friday offer yet.", confidence="medium"),
    "policy": P2("sourced", "30 days from shipping confirmation to return. Free delivery on all orders.",
                 R("CONDITIONAL", "UNKNOWN", "UNKNOWN", days=30, src="https://levis.com.au/policies/refund-policy",
                   ev="You can, within 30 calendar days from shipping confirmation, subject to the terms of our Returns Policy"),
                 S("YES", restr="Australia only (not Norfolk Island).", src="https://levis.com.au/policies/shipping-policy",
                   ev="Delivery is currently FREE for all purchases from levis.com.au.")),
}
EXTRA["country-road"] = {
    "sale": SALE2("LIVE", "https://www.countryroad.com.au/", "25% off Bags and shoes * Shop woman Shop man *Excludes Child",
                  name="25% off bags and shoes (not labelled Black Friday)", discount_text="25% off bags and shoes", discount_max_pct=25, discount_kind="flat",
                  scope="SELECTED", conditions="Full-priced only, excludes Child, can't combine with other offers."),
    "policy": P2("sourced", "30-day returns: free in store, $9.95 by post. Free standard delivery over $100.",
                 R("CONDITIONAL", "YES", "NO", instore="YES", days=30, cost="$9.95 by post", src="https://www.countryroad.com.au/pages/returns",
                   ev="Return or exchange your online purchase at any Country Road store free of charge. ... can be returned by post for a fee of $9.95 (AUD)"),
                 S("CONDITIONAL", 100, src="https://www.countryroad.com.au/pages/delivery", ev="Enjoy fast and free standard delivery* for all online purchases over $100.")),
}
