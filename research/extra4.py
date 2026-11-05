# Batch 4 (2026-11-05 night): Elite Eleven + tech & electronics. Executed by build_research.py.
T4 = "2026-11-05T11:30:00+00:00"
VERIFIED = {"samsung", "asus", "lenovo", "dyson", "jb-hifi", "elite-eleven"}
EXTRA = {}


def SALE4(*a, **kw):
    return {**SALE(*a, **kw), "verified_at": T4}


def P4(*a):
    return {**P(*a), "verified_at": T4}


EXTRA["elite-eleven"] = {
    "sale": SALE4("NOT_ANNOUNCED", "https://eliteelevensporting.com/", "No Black Friday 2026 announcement yet; only the regular Outlet (e.g. 'Save 50%').",
                  confidence="medium", conditions="Watching for Elite Eleven's Black Friday announcement."),
    "policy": P4("sourced", "Free returns for Australian customers within 30 days (store credit, or refund less a fee). Sale-period returns: store credit only.",
                 R("YES", "YES", "YES", days=30, sale_ex="CONDITIONAL", refund="Store credit; refunds carry a shipping/handling fee",
                   cond="During sale periods returns are store credit only. Final sale not returnable.", src="https://eliteelevensporting.com/pages/faqs",
                   ev="We offer free returns for store credit or refunds within 30 days of receiving your order."),
                 S("UNKNOWN", restr="Standard 2-5 business days to major cities.", src="https://eliteelevensporting.com/pages/faqs")),
}
EXTRA["jb-hifi"] = {
    "sale": SALE4("UPCOMING", "https://www.jbhifi.com.au/pages/black-friday-sale",
                  "Black Friday Sale is the one JB plans for all year, and the countdown is officially on",
                  name="JB Hi-Fi Black Friday Sale 2026", early_access="Sign up to be first to know when it begins",
                  expected_note="JB's page cites the industry date (Fri 27 Nov) but hasn't announced its own start"),
    "policy": P4("sourced", "30-day change-of-mind refunds for unused, unopened products; category exclusions apply.",
                 R("YES", "CONDITIONAL", "UNKNOWN", instore="YES", days=30, sale_ex="CONDITIONAL", refund="100% refund if unused and unopened",
                   cond="Opened products, PC games/software and commercial sales excluded.",
                   src="https://www.jbhifi.com.au/pages/help-and-support/refunds-and-warranties-guide",
                   ev="Unused & Unopened, packaging in good condition (product not faulty) - eg change of mind. | 100% Refund | 30 Days"),
                 S("UNKNOWN", restr="Delivery cost depends on item and postcode.", src="https://www.jbhifi.com.au/pages/help-and-support/delivery-and-collection")),
}
EXTRA["harvey-norman"] = {
    "sale": SALE4("UPCOMING", "https://www.harveynorman.com.au/black-friday", "The countdown to Black Friday is on ... with huge deals ... coming soon!", confidence="medium"),
    "policy": P4("sourced", "No change-of-mind refunds on online orders. Statutory rights for faulty goods still apply.",
                 R("NO", "NO", "NO", src="https://www.harveynorman.com.au/customer-service/refund-policy",
                   ev="Until further notice, Harvey Norman Online will not provide a refund where you have changed your mind"),
                 S("UNKNOWN", restr="Delivery cost shown at checkout.")),
}
EXTRA["the-good-guys"] = {
    "sale": SALE4("UPCOMING", "https://www.thegoodguys.com.au/deals/black-friday-freezers", "The Black Friday freezer sale 2026 is on its way ...", confidence="medium"),
    "policy": P4("sourced", "Unopened change-of-mind returns only; delivery fee not refunded; opened goods may cost a 20% restocking fee.",
                 R("CONDITIONAL", "CONDITIONAL", "NO", instore="CONDITIONAL", cond="20% restocking fee may apply to unpacked goods; you pay pickup if not returned to a store.",
                   src="https://www.thegoodguys.com.au/terms-and-conditions", ev="we will not refund any delivery fee, and, if you cannot return the Goods to a store, you must pay for us to pick up the Goods."),
                 S("UNKNOWN", restr="Depends on goods and postcode.")),
}
EXTRA["officeworks"] = {
    "sale": SALE4("UPCOMING", "https://www.officeworks.com.au/campaigns/black-friday", "Get ready for Black Friday 2026 with unbeatable deals at Officeworks.", confidence="medium"),
    "policy": P4("sourced", "30-day refunds or exchanges in store (365 days with OnePass). Free metro delivery over $65.",
                 R("YES", "CONDITIONAL", "NO", instore="YES", days=30, sale_ex="CONDITIONAL", refund="Refund or exchange in store",
                   src="https://www.officeworks.com.au/information/policies/return-policy", ev="Return the item within 30 days of purchase"),
                 S("CONDITIONAL", 65, restr="Metro areas.", src="https://www.officeworks.com.au/information/policies/delivery-offer", ev="Free metro delivery over $65")),
}
EXTRA["bing-lee"] = {
    "sale": SALE4("EARLY_ACCESS", "https://www.binglee.com.au/categories/promotions/black-friday-sale", "Early Black Friday Deals", confidence="medium",
                  name="Early Black Friday Deals", early_access="Early deals open to everyone (no membership stated)"),
    "policy": P4("sourced", "14-day change-of-mind returns for unopened goods; postage deducted from online refunds.",
                 R("YES", "NO", "NO", instore="CONDITIONAL", days=14, sale_ex="CONDITIONAL", refund="Original payment method",
                   cond="Opened goods may incur a 20% restocking fee. Delivery mainly Sydney, Melbourne, Brisbane metro.",
                   src="https://www.binglee.com.au/articles/help/returns-refunds-warranties-and-repairs/returns-policy",
                   ev="the customer changes their mind within 14 days ... Goods are unopened, unused"),
                 S("CONDITIONAL", restr="Priced by location and weight.", src="https://www.binglee.com.au/articles/help/delivery-services")),
}
EXTRA["dell"] = {
    "sale": SALE4("NOT_ANNOUNCED", "https://www.dell.com/en-au/shop/lp/black-friday-deals",
                  "Current offer is a Dell Rewards bonus ending 12 Nov 2026; no Black Friday sale yet.", confidence="medium",
                  conditions="Earn $75 Dell Rewards on eligible purchases of $2500+, ends 12 Nov (not a Black Friday sale)."),
    "policy": P4("sourced", "Purchases 1 Nov to 29 Dec returnable until 15 Jan 2027. Free delivery, no minimum.",
                 R("YES", "CONDITIONAL", "CONDITIONAL", instore="NA", days=30, note="1 Nov-29 Dec purchases: until 15 Jan 2027",
                   cond="Shipping or restocking fees may reduce refunds for change of mind.", src="https://www.dell.com/en-au/shop/lp/return-policy",
                   ev="Purchases made ... from 1 November to 29 December 2026 at Dell.com.au can be returned until 15 January 2027"),
                 S("YES", None, 0, src="https://www.dell.com/en-au/shop/dell-experience/lp/shipping-and-delivery", ev="Free delivery, no minimum purchase")),
}
EXTRA["hp"] = {
    "sale": SALE4("EARLY_ACCESS", "https://www.hp.com/au-en/shop/sale-offers.html", "We've gathered our top Early Black Friday offers in one place.",
                  name="Early Black Friday offers", discount_text="Extra 10% off with code EBF", discount_max_pct=10, discount_kind="flat",
                  scope="SELECTED", code_required="YES", code="EBF", confidence="medium",
                  conditions="Reported by the research pass; not re-confirmed directly."),
    "policy": P4("sourced", "14-day change of mind; you pay return costs. Free delivery over $50.",
                 R("YES", "NO", "NO", instore="NA", days=14, sale_ex="CONDITIONAL", refund="Original payment method",
                   src="https://www.hp.com/au-en/shop/faqs-content#returns", ev="You are responsible for all costs of returning a product back to HP"),
                 S("CONDITIONAL", 50, 7.95, src="https://www.hp.com/au-en/shop/faqs-content", ev="HP Online Store delivers free of charge on all orders over $50.")),
}
EXTRA["lenovo"] = {
    "sale": SALE4("EARLY_ACCESS", "https://www.lenovo.com/au/en/deals/black-friday-sale/",
                  "Black Friday Early Access Sale. SHOP AHEAD OF THE CROWDS. Your early access to the biggest savings this year.",
                  name="Black Friday Early Access Sale", early_access="Open to everyone; extra member savings promoted"),
    "policy": P4("sourced", "7-day returns for PCs only with a 20% restocking fee; clearance and accessories excluded. Free shipping.",
                 R("CONDITIONAL", "NO", "CONDITIONAL", instore="NA", days=7, sale_ex="YES", refund="Refund less 20% restocking fee",
                   src="https://www.lenovo.com/au/en/shopping-faqs/", ev="within 7 calendar days of delivery. A restocking fee of 20% ... will apply."),
                 S("YES", None, 0, src="https://www.lenovo.com/au/en/shopping-faqs/", ev="Lenovo offers free standard shipping to addresses within Australia.")),
}
EXTRA["asus"] = {
    "sale": SALE4("LIVE", "https://www.asus.com/au/deals/black-friday/", "Black Friday Deals ... Savings of up to $1500 on selected ASUS devices",
                  name="ASUS Black Friday Deals", discount_text="Up to $1,500 off selected devices", discount_kind="up_to", scope="SELECTED"),
    "policy": P4("sourced", "Only 3 days for change-of-mind returns; restocking fees may apply. Free delivery.",
                 R("CONDITIONAL", "CONDITIONAL", "CONDITIONAL", instore="NA", days=3, sale_ex="CONDITIONAL", refund="Original payment, less fees",
                   src="https://au.store.asus.com/rog/shopping-faqs", ev="You have three (3) days from receiving your order to request a Change of Mind return"),
                 S("YES", None, 0, src="https://au.store.asus.com/terms-conditions", ev="Free standard delivery for all items.")),
}
EXTRA["samsung"] = {
    "sale": SALE4("LIVE", "https://www.samsung.com/au/offer/black-friday-sale/",
                  "Samsung Black Friday Sale 2026 & Deals ... Black Friday Hot Deals (TV & AV, Appliances, Audio, Wearables)",
                  name="Samsung Black Friday Sale 2026", discount_text="Up to $2,500 off selected TVs", discount_kind="up_to", scope="SELECTED",
                  conditions="Research pass quoted 'Black Friday On Now! Save up to $2,500 on selected TVs'."),
    "policy": P4("sourced", "Change-of-mind returns only for unopened mobile devices within 14 days. Free delivery on mobile products only.",
                 R("CONDITIONAL", "UNKNOWN", "UNKNOWN", instore="NA", days=14, sale_ex="YES",
                   cond="Change of mind covers phones, tablets, wearables and accessories only, sealed and unused.",
                   src="https://www.samsung.com/au/shop-faq/returns-and-cancellations/", ev="Eligible consumers can request an exchange or refund of their Mobile Product if they change their mind"),
                 S("CONDITIONAL", restr="Free for mobile/tablet/wearables; big items charged by postcode.",
                   src="https://www.samsung.com/au/shop-faq/delivery-and-installations/delivery-costs/",
                   ev="Free delivery in Australia is available for mobile, tablet, and wearable products only.")),
}
EXTRA["apple"] = {
    "sale": SALE4("NOT_ANNOUNCED", "https://www.apple.com/au/", "No Black Friday shopping event announced yet.", confidence="medium"),
    "policy": P4("sourced", "14-day returns, free by post or in store. Free delivery.",
                 R("YES", "YES", "YES", instore="YES", days=14, src="https://www.apple.com/au/shop/help/returns_refund",
                   ev="you have up to 14 calendar days from the time you receive your item(s) to initiate a return"),
                 S("YES", None, 0, src="https://www.apple.com/au/shop/help/shipping_delivery", ev="Standard delivery is free for all online orders.")),
}
EXTRA["sony"] = {
    "sale": SALE4("NOT_ANNOUNCED", "https://store.sony.com.au/", "No Black Friday 2026 announcement found.", confidence="medium"),
    "policy": P4("sourced", "30-day money-back for My Sony members on eligible products. Free shipping over $200.",
                 R("CONDITIONAL", "CONDITIONAL", "CONDITIONAL", instore="NA", days=30, cond="My Sony members, eligible products; TVs may have a $150 restocking fee.",
                   src="https://store.sony.com.au/30day-faq.html", ev="You have 30 days from the invoice date to start the returns process... This is at Sony's cost"),
                 S("CONDITIONAL", 200, src="https://store.sony.com.au/delivery-returns.html", ev="Get free shipping on all eligible products over $200.00.")),
}
EXTRA["dyson"] = {
    "sale": SALE4("UPCOMING", "https://www.dyson.com.au/", "Black Friday is almost here. Sign up now for exclusive access to Dyson Black Friday 2026 deals",
                  name="Dyson Black Friday 2026", early_access="Sign up for exclusive access"),
    "policy": P4("sourced", "45-day change-of-mind returns with free return delivery; 1 Nov to 17 Dec purchases until 31 Jan 2027. Free delivery over $89.",
                 R("YES", "YES", "YES", instore="NA", days=45, note="45 days; 1 Nov-17 Dec purchases until 31 Jan 2027", sale_ex="CONDITIONAL",
                   src="https://www.dyson.com.au/footer-primary-links/delivery-details", ev="you can cancel within 45 days of receiving your machine(s)... [Dyson] will arrange free return delivery."),
                 S("CONDITIONAL", 89, 10, src="https://www.dyson.com.au/footer-primary-links/delivery-details", ev="Standard delivery | Over $89 Free | Under $89 $10")),
}
EXTRA["logitech"] = {
    "sale": SALE4("NOT_ANNOUNCED", "https://www.logitech.com/en-au/shop/deals", "Only regular deals page; no Black Friday announcement.", confidence="medium"),
    "policy": P4("sourced", "30-day money-back guarantee. Free shipping over $80.",
                 R("YES", "UNKNOWN", "UNKNOWN", instore="NA", days=30, src="https://www.logitech.com/en-au",
                   ev="Shop risk-free with our easy returns and 30-day money back guarantee."),
                 S("CONDITIONAL", 80, src="https://www.logitech.com/en-au", ev="Enjoy free standard shipping on all orders over $80.00")),
}
EXTRA["garmin"] = {
    "sale": SALE4("LIVE", "https://www.garmin.com/en-AU/c/promotions/", "BLACK FRIDAY SALE. Limited time savings on gifts for everyone on your list.",
                  name="Garmin Black Friday Sale", scope="SELECTED", confidence="medium",
                  conditions="Reported by the research pass; the promotions page shows a Black Friday Sale section. Discounts vary by product."),
    "policy": P4("sourced", "30-day returns with free return shipping. Free shipping over $49.",
                 R("YES", "YES", "YES", instore="NA", days=30, src="https://www.garmin.com/en-AU/shop/shipping/",
                   ev="Merchandise in its original condition may be returned for a refund within 30 days ... We offer free shipping on all returns."),
                 S("CONDITIONAL", 49, src="https://www.garmin.com/en-AU/", ev="FREE SHIPPING ON ORDERS $49 AUD")),
}
