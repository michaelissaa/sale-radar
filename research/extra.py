# Executed by build_research.py with R, S, P, SALE, T in scope. Second batch of the 2026-11-05 research pass.
EXTRA = {}

EXTRA["the-iconic"] = {
    "sale": SALE("UPCOMING", "https://www.theiconic.com.au/black-friday/",
                 "When does THE ICONIC's Black Friday sale start and end? Check back for updates to be the first to know when THE ICONIC Black Friday 2026 starts.",
                 name="THE ICONIC Black Friday 2026", confidence="medium",
                 early_access="THE ICONIC Front Row (free loyalty program) members get early access",
                 expected_note="Page cites the industry dates (Fri 27 Nov to Cyber Monday 30 Nov); THE ICONIC has not published its own start",
                 conditions="Page mentions deals of up to 50% off ICONIC Exclusives but does not say when they start."),
    "policy": P("sourced", "Free change-of-mind returns within 30 days. Sale items returnable unless marked Final Sale.",
                R("YES", "YES", "YES", instore="NA", days=30, sale_ex="CONDITIONAL", refund="Refund or FAST store credit",
                  cond="Unworn, original packaging, lodged through your account. Final Sale and hygiene items excluded. Some pickup drop-off options may charge a fee.",
                  src="https://theiconicsupport.zendesk.com/hc/en-us/articles/4418133900697-What-is-THE-ICONIC-s-returns-policy",
                  ev="We offer free change of mind returns within 30 days of purchase"),
                S("UNKNOWN", restr="Delivery price depends on postcode; $1 express to parcel lockers with minimum spend.",
                  src="https://www.theiconic.com.au/shipping-policy/", ev="$1 Express delivery to 24/7 Parcel Lockers. ... Minimum spend and T&Cs apply.")),
}
EXTRA["hm"] = {
    "sale": SALE("NEEDS_CHECKING", "https://www2.hm.com/en_au/seasonal/black-friday.html",
                 "An automated research pass reported the page heading 'Black Friday sale 2026 is on!', but on re-check the page redirected to a generic seasonal page.",
                 confidence="low", conditions="Unconfirmed. H&M's robots.txt blocks the automatic scanner, so check the site directly."),
    "policy": P("sourced", "30-day returns by post with a prepaid label; non-members pay $10.95. Online orders can't be returned in store. Free shipping over $75 for members.",
                R("YES", "CONDITIONAL", "CONDITIONAL", instore="NO", label="YES", days=30, refund="Original payment method",
                  cost="$10.95 deducted for non-members", cond="Membership is free. Delivery fee refunded only if the whole order is returned.",
                  src="https://www2.hm.com/en_au/customer-service/returns.html",
                  ev="H&M will deduct $10.95 from your refund for the use of our returns label if you are not an H&M member. ... Purchases made online cannot be returned or exchanged in stores."),
                S("CONDITIONAL", 75, 8.95, restr="Free over $75 for (free) members; Plus members free on all orders.",
                  src="https://www2.hm.com/en_au/customer-service/shippinganddelivery.html",
                  ev="Standard Delivery (1-10 Business days /$8.95) ... Free for members on orders over $75")),
}
EXTRA["uniqlo"] = {
    "policy": P("sourced", "30-day returns. Posting a return costs $8; exchanges can be done free in an Australian store. Sale items covered. Free shipping over $75.",
                R("YES", "CONDITIONAL", "NO", instore="CONDITIONAL", days=30, sale_ex="NO", refund="Original payment method",
                  cost="$8.00 via the Australia Post return portal", cond="In-store option is for exchanges; refunds of online orders are by post.",
                  src="https://faq-au.uniqlo.com/pkb_Home?id=kA0Ie000000TOR7",
                  ev="An $8.00 return postage fee applies for online order change of mind returns via post where the Australia Post return portal is used."),
                S("CONDITIONAL", 75, 7.95, src="https://www.uniqlo.com/au/en/", ev="Standard delivery is $7.95, or free if you spend over $75.")),
}
EXTRA["asos"] = {
    "policy": P("sourced", "28-day returns for a refund, $8.99 return fee deducted. No exchanges. Free shipping over $120 or with Premier.",
                R("YES", "NO", "NO", instore="NA", days=28, sale_ex="CONDITIONAL", refund="Original payment method", cost="$8.99 deducted from refund",
                  src="https://www.asos.com/au/customer-care/returns-refunds/what-is-your-returns-policy/",
                  ev="we accept returns for a change of mind ... Returns cost $8.99 (AUD) ... You have 28 days"),
                S("CONDITIONAL", 120, 22.99, restr="Ships from the UK; rural areas up to 14 business days.",
                  src="https://www.asos.com/au/customer-care/delivery/how-does-your-delivery-service-to-australia-work/",
                  ev="Standard Shipping - Cost: $22.99; FREE on orders over $120 or with ASOS Premier.")),
}

EXTRA["new-balance"] = {
    "sale": SALE("UPCOMING", "https://www.newbalance.com.au/promo/blackfriday/",
                 "The New Balance Black Friday Sale starts on Friday 13 November 2026 and runs until Sunday 29 November 2026. There will be offers running upto 50% off on eligible styles.",
                 name="New Balance Black Friday Sale 2026", discount_text="Up to 50% off eligible styles", discount_max_pct=50, discount_kind="up_to",
                 scope="SELECTED", start="2026-11-13", end="2026-11-29", dates_confirmed=True, code_required="NO"),
    "policy": P("sourced", "Free 60-day returns by post or in store. Final sale excluded. Free shipping over $150, or free for logged-in members.",
                R("YES", "YES", "YES", instore="YES", label="YES", days=60, sale_ex="CONDITIONAL", refund="Original payment method",
                  cond="Most full-price and reduced items. Final-sale items not returnable unless faulty.",
                  src="https://www.newbalance.com.au/returns/", ev="Return postage is free if within an Australian location."),
                S("CONDITIONAL", 150, restr="Free with no minimum when you join or log in. Express $15.",
                  src="https://www.newbalance.com.au/customer-service-shipping.html",
                  ev="Australia Post Standard: Free on all orders over $150*; Free with no minimum spend when you join or login")),
}
EXTRA["reebok"] = {
    "sale": SALE("LIVE", "https://reebok.com.au/collections/black-friday",
                 "Black Friday is here. Take 30% off almost everything across Reebok footwear, apparel and training gear.",
                 name="Black Friday", discount_text="30% off almost everything", discount_max_pct=30, discount_kind="flat", scope="SELECTED",
                 conditions="'Almost everything' means some exclusions apply, so this is not sitewide."),
    "policy": P("sourced", "Free 30-day returns with a prepaid slip, or in store. Final sale excluded. Free shipping over $99.",
                R("YES", "YES", "YES", instore="YES", label="YES", days=30, sale_ex="YES", refund="Original payment method, less shipping paid",
                  cond="Final-sale products not eligible for change-of-mind returns.",
                  src="https://reebok.com.au/pages/returns-1", ev="Australian orders made through reebok.com.au may be returned within 30 days free of charge"),
                S("CONDITIONAL", 99, 12.95, src="https://reebok.com.au/pages/delivery-and-returns", ev="Free shipping on all Australian orders $99 and above.")),
}
EXTRA["under-armour"] = {
    "sale": SALE("UPCOMING", "https://www.underarmour.com.au/en-au/c/black-friday/",
                 "While we can't share our deals just yet, we're warming up for the long-awaited Under Armour 2026 Black Friday event.",
                 name="Under Armour Black Friday Event 2026", confidence="medium",
                 conditions="An earlier 30% off sitewide promotion ended 2 Nov 2026 (per the research pass). Black Friday deals not yet published."),
    "policy": P("sourced", "Free 30-day returns with a prepaid label. Free shipping over $129.",
                R("YES", "YES", "YES", instore="CONDITIONAL", label="YES", days=30, refund="Original payment method",
                  cond="Online orders can be returned in store only if paid by card (not PayPal/Klarna). Undergarments excluded.",
                  src="https://www.underarmour.com.au/en-au/t/returns-and-exchanges.html",
                  ev="you can return it for FREE using our pre-paid return label. All returns are accepted 30 days from date of purchase."),
                S("CONDITIONAL", 129, 9.99, src="https://www.underarmour.com.au/en-au/t/shipping-information.html",
                  ev="Get free standard delivery on all orders over $129AUD, or $9.99 for orders under $129AUD.")),
}
EXTRA["nike"] = {
    "sale": SALE("UPCOMING", "https://www.nike.com/au/w/black-friday-2phlm", "Something is coming... Sign up for early access to our biggest sale of the year",
                 name="Black Friday Sale", confidence="medium", early_access="Sign-up for early access offered"),
    "policy": P("sourced", "30-day returns (60 days for 1 Nov to 25 Dec purchases). Free return postage for Nike Members; guests pay $9.95.",
                R("YES", "CONDITIONAL", "CONDITIONAL", instore="NA", label="YES", days=30, note="30 days; 60 days for 1 Nov-25 Dec 2026 purchases",
                  sale_ex="CONDITIONAL", refund="Original payment method", cost="$9.95 deducted for guests (free for members)",
                  cond="Membership is free. Final-sale items excluded.",
                  src="https://www.nike.com/au/help/a/returns-policy",
                  ev="Return delivery is free for Nike Members. Guests will have a $9.95 return delivery fee deducted from their refund."),
                S("CONDITIONAL", 80, 9.95, restr="$80 threshold is for Nike Members; guests $150.", src="https://www.nike.com/au/help/a/shipping-delivery",
                  ev="Nike Members: free for orders of $80 or more, $9.95 for orders less than $80; Guests: free for orders of $150 or more")),
}
EXTRA["adidas"] = {
    "sale": SALE("UPCOMING", "https://www.adidas.com.au/black_friday", "2026 BLACK FRIDAY SALE COMING SOON. Become an adiClub Member for Black Friday sale updates.",
                 name="2026 Black Friday Sale", confidence="medium", early_access="adiClub members get sale updates"),
    "policy": P("sourced", "30-day returns by post only. Free delivery for adiClub members; guests free over $120.",
                R("YES", "UNKNOWN", "UNKNOWN", instore="NO", days=30, sale_ex="CONDITIONAL", refund="Original payment method",
                  cond="Online orders return by post only. Hype items, swimwear, socks, undergarments and more excluded. Shipping fees not refunded.",
                  src="https://www.adidas.com.au/help/pac-returns-and-refunds/what-is-adidas-returns-policy",
                  ev="Items eligible for return or exchange must be returned or exchanged within 30 days of purchase."),
                S("CONDITIONAL", 120, 10, restr="Free for adiClub members (free to join) on any order.",
                  src="https://www.adidas.com.au/help/pac-delivery/how-long-does-delivery-take",
                  ev="Delivery fee for Guest Order Under $120: $10.00; ... adiclub Members Orders Under $120: FREE")),
}
EXTRA["cos"] = {
    "sale": SALE("UPCOMING", "https://www.cos.com/en-au/black-friday", "The COS Black Friday offer begins in November.", confidence="medium"),
    "policy": P("sourced", "30-day returns with $7.95 deducted. Online orders can't be returned in store. Free shipping over $125.",
                R("YES", "NO", "NO", instore="NO", label="YES", days=30, sale_ex="YES", refund="Original payment, less $7.95", cost="$7.95",
                  cond="FINAL SALE items not returnable for change of mind.",
                  src="https://www.cos.com/en-au/customer-service/returns", ev="with the cost of the return taken out of the original payment ($7.95)"),
                S("CONDITIONAL", 125, 7.95, src="https://www.cos.com/en-au/customer-service/delivery/delivery-methods",
                  ev="Standard Home Delivery ($7.95 AUD / Free over $125 AUD)")),
}
EXTRA["puma"] = {
    "policy": P("sourced", "Free 30-day returns (one free return per order). Free shipping over $150, otherwise $10.",
                R("YES", "YES", "YES", days=30, refund="Original payment method", cond="1 free return per order. No exchanges for online orders.",
                  src="https://au.puma.com/au/en/help/returns", ev="You can return your order free of charge within 30 days of purchase. We offer 1 free return per order."),
                S("CONDITIONAL", 150, 10, restr="Express $15.95.", src="https://au.puma.com/au/en/help/delivery",
                  ev="We offer free standard shipping across Australia for all orders over $150. For all orders under $150, the regular shipping cost is $10.")),
}
EXTRA["asics"] = {
    "sale": SALE("NOT_ANNOUNCED", "https://www.asics.com/au/en-au/asics-black-friday-cyber-monday/c/au80154000/",
                 "ASICS Black Friday & Cyber Weekend Sale has ended. (Left over from last year; no 2026 announcement.)", confidence="medium"),
    "policy": P("sourced", "45-day returns (60 for OneASICS members). Free returns for members, $9.99 for guests. Final Sale excluded. Free shipping over $199.",
                R("YES", "CONDITIONAL", "CONDITIONAL", instore="YES", days=45, note="45 days guests, 60 days OneASICS members", sale_ex="YES", refund="Refund",
                  cost="$9.99 flat for guests", cond="Online purchases can be returned at ASICS brand stores. Final Sale not returnable unless faulty.",
                  src="https://www.asics.com/au/en-au/customer-service/returns/", ev="Free returns for OneASICS Members. Or $9.99 flat postage fee for Guest orders."),
                S("CONDITIONAL", 199, 8.99, restr="Mainland Australia and Tasmania.", src="https://www.asics.com/au/en-au/customer-service/shipping/",
                  ev="FREE* shipping on orders over $199")),
}
EXTRA["lululemon"] = {
    "policy": P("sourced", "Free 30-day returns by post or in store, but sale and We Made Too Much items are excluded. Free shipping when signed in.",
                R("YES", "YES", "YES", instore="YES", label="YES", days=30, sale_ex="YES", refund="Refund, credit or exchange",
                  cond="Sale and marked-down items (incl. We Made Too Much) excluded from change-of-mind returns. Outlets don't accept online returns.",
                  src="https://www.lululemon.com.au/en-au/help/returns-and-refunds", ev="You can return an online purchase to one of our stores or for free via Australia Post."),
                S("CONDITIONAL", restr="Free on all orders when signed in to a (free) lululemon account.",
                  src="https://www.lululemon.com.au/en-au/help/shipping-and-delivery",
                  ev="We offer free shipping on all orders for guests who are signed in to their lululemon account!")),
}
EXTRA["zara"] = {
    "policy": P("sourced", "30-day returns, free in store; drop-point returns cost $3.95. Free shipping over $75 only on full-price items.",
                R("YES", "YES", "NO", instore="YES", label="YES", days=30, cost="$3.95 for drop-point returns",
                  cond="Return within the same market. 30 days from shipping date.",
                  src="https://www.zara.com/au/en/help-center/HowToReturn", ev="You can return your items for free at any of our Zara stores."),
                S("CONDITIONAL", 75, 7.95, restr="Free-shipping threshold excludes discounted items, so sale orders may pay delivery.",
                  src="https://www.zara.com/au/en/help-center/DeliveryMethods", ev="Shipping will be free for orders over $ 75 only for non-discounted items.")),
}

# Research pass found no 2026 Black Friday announcement on these official sites (5 Nov).
_NA = {
    "puma": "https://au.puma.com/au/en/", "lululemon": "https://www.lululemon.com.au/en-au/", "zara": "https://www.zara.com/au/en/",
    "uniqlo": "https://www.uniqlo.com/au/en/", "asos": "https://www.asos.com/au/", "youngla": "https://au.youngla.com/",
    "alphalete": "https://alphaleteathletics.com/", "oner-active": "https://au.oneractive.com/", "hallensteins": "https://www.hallensteins.com/au",
    "maniere-de-voir": "https://au.manieredevoir.com/", "culture-kings": "https://www.culturekings.com.au/",
}
for _id, _url in _NA.items():
    EXTRA.setdefault(_id, {})["sale"] = SALE("NOT_ANNOUNCED", _url, "No Black Friday 2026 announcement found on the official site during the 5 Nov research pass.",
                                              confidence="medium")
