# Batch 3 (2026-11-05 night): Amazon, department stores, sneakers, more activewear.
# Executed by build_research.py with R, S, P, SALE, T in scope.
T3 = "2026-11-05T11:00:00+00:00"
VERIFIED = {"amazon", "bonds", "converse"}
EXTRA = {}


def SALE3(*a, **kw):
    return {**SALE(*a, **kw), "verified_at": T3}


def P3(*a):
    return {**P(*a), "verified_at": T3}


EXTRA["amazon"] = {
    "sale": SALE3("UPCOMING", "https://www.amazon.com.au/blackfriday", "Black Friday Sale 2026 - 17 Nov - 30 Nov",
                  name="Amazon Black Friday Sale 2026", start="2026-11-17", end="2026-11-30", dates_confirmed=True,
                  early_access="Prime members usually get some deals first; no 2026 Prime early-access date published",
                  conditions="Deals vary by product and seller. Launch time of day not stated (treated as midnight Sydney)."),
    "policy": P3("sourced", "Free returns within 30 days on eligible Amazon-fulfilled fashion (look for 'FREE Returns'). Free delivery on eligible orders over $59.",
                 R("YES", "CONDITIONAL", "CONDITIONAL", instore="NA", label="CONDITIONAL", days=30, refund="Full refund of item price",
                   cond="Free return shipping on eligible clothing, shoes and accessories fulfilled by Amazon AU; third-party sellers vary.",
                   src="https://www.amazon.com.au/b?ie=UTF8&node=10347105051",
                   ev="Amazon AU offers free return shipping on eligible Fashion items (clothing, shoes and accessories)."),
                 S("CONDITIONAL", 59, restr="Eligible items only; Prime gives free delivery on eligible items.",
                   src="https://www.amazon.com.au/gp/help/customer/display.html?nodeId=GZXW7X6AKTHNUP6H",
                   ev="Orders of eligible items with a combined value of AUD $59 or more are eligible for free delivery")),
}
EXTRA["myer"] = {
    "sale": SALE3("UPCOMING", "https://www.myer.com.au/content/black-Friday",
                  "Our 2026 Black Friday sale is returning soon with exciting deals and offers across a wide range of products at Myer.",
                  name="Myer Black Friday 2026", confidence="medium"),
    "policy": P3("sourced", "30-day change-of-mind refunds (online orders: refund, not exchange). Clearance excluded. Free delivery over $99.",
                 R("YES", "CONDITIONAL", "UNKNOWN", instore="YES", days=30, sale_ex="CONDITIONAL", refund="Refund (online orders)",
                   cond="Reduced-to-clear items not accepted for change of mind.", src="https://www.myer.com.au/content/returns-policy",
                   ev="we offer refunds or exchanges on most items within 30 days of purchase"),
                 S("CONDITIONAL", 99, 9.95, src="https://www.myer.com.au/content/payment-and-delivery", ev="We offer free standard delivery on all orders over $99.")),
}
EXTRA["david-jones"] = {
    "sale": SALE3("LIVE", "https://www.davidjones.com/sale", "Selected full-priced women's international designer fashion. 40% OFF",
                  name="Designer sale (not Black Friday)", sale_type="regular", discount_text="40% off selected designer fashion",
                  discount_max_pct=40, discount_kind="flat", scope="SELECTED", confidence="medium",
                  conditions="Black Friday not announced yet."),
    "policy": P3("sourced", "30-day refunds or exchanges; sale items returnable. Free delivery over $100.",
                 R("YES", "CONDITIONAL", "UNKNOWN", instore="YES", days=30, sale_ex="NO", refund="Refund or exchange (post returns: refund only)",
                   src="https://www.davidjones.com/return-options", ev="you can exchange or refund your purchase within 30 days from the date of purchase"),
                 S("CONDITIONAL", 100, 9.95, src="https://www.davidjones.com/delivery-choices", ev="Free for orders over $100. $9.95 fee for orders under $100.")),
}
EXTRA["hype-dc"] = {
    "sale": SALE3("UPCOMING", "https://www.hypedc.com/au/blog/hype-dc-black-friday",
                  "Hype DC has published a Black Friday and Cyber Monday 2026 guide.", confidence="low",
                  expected_note="The guide quotes the industry dates (27 to 30 Nov); Hype DC hasn't confirmed its own sale dates",
                  early_access="Mailing list gets early access"),
    "policy": P3("sourced", "30-day returns; you pay change-of-mind postage. Sale items: in-store exchange or gift card only. Free express over $160.",
                 R("YES", "CONDITIONAL", "NO", instore="CONDITIONAL", label="NO", days=30, sale_ex="CONDITIONAL",
                   refund="Full price: refund. Sale: exchange or gift card", src="https://www.hypedc.com/au/articles/faq/returns-faq",
                   ev="We will not cover the cost of return orders due to change of mind."),
                 S("CONDITIONAL", 160, 10, src="https://www.hypedc.com/au/articles/faq/shipping", ev="Free express shipping is applicable for orders over AU$160.00")),
}
EXTRA["alo-yoga"] = {
    "sale": SALE3("NOT_ANNOUNCED", "https://www.aloyoga.com/en-au", "No Black Friday 2026 announcement found.", confidence="medium"),
    "policy": P3("sourced", "30-day returns with return shipping covered. Free worldwide shipping over US$75.",
                 R("YES", "YES", "YES", days=30, refund="Refund, exchange or store credit", src="https://www.aloyoga.com/pages/returns-exchanges",
                   ev="Alo will gladly accept returns on unworn and unused items within 30 days of purchase for a full refund and will cover the return shipping"),
                 S("CONDITIONAL", restr="Free over US$75; duties may apply.", src="https://www.aloyoga.com/pages/shipping-info",
                   ev="FREE worldwide shipping with orders over $75 USD")),
}
EXTRA["adanola"] = {
    "sale": SALE3("NOT_ANNOUNCED", "https://adanola.com/en-au", "No Black Friday 2026 announcement found.", confidence="medium"),
    "policy": P3("sourced", "30-day returns at your cost. Shipping $15, free over A$230, duties included.",
                 R("YES", "NO", "NO", instore="NA", label="NO", days=30, refund="Original payment method", src="https://adanola.com/en-au/pages/returns",
                   ev="Return shipping costs are the customer's responsibility"),
                 S("CONDITIONAL", 230, 15, restr="Ships from the UK, duties included.", src="https://adanola.com/pages/worldwide-shipping",
                   ev="Australia | $15 AUD | 5 - 10 Days | $230 AUD")),
}
EXTRA["vans"] = {
    "sale": SALE3("NOT_ANNOUNCED", "https://www.vans.com.au/", "Only the regular sale section; no Black Friday announcement.", confidence="medium"),
    "policy": P3("sourced", "60-day returns for 5 Nov to 31 Dec purchases; free in store. Free express over $150.",
                 R("YES", "CONDITIONAL", "NO", instore="YES", label="YES", days=60, note="60 days for 5 Nov-31 Dec 2026 purchases",
                   src="https://www.vans.com.au/create-returns-info", ev="purchases made between 5 November and 31 December 2026 are eligible for an extended 60-day returns policy"),
                 S("CONDITIONAL", 150, src="https://www.vans.com.au/", ev="FREE EXPRESS DELIVERY ON ORDERS OVER $150")),
}
EXTRA["converse"] = {
    "sale": SALE3("NEEDS_CHECKING", "https://www.converse.com.au/black-friday-cyber-monday",
                  "Converse has a Black Friday & Cyber Monday page, but its content loads by script and a live sale couldn't be confirmed.",
                  confidence="low", early_access="Email sign-up promoted for early access"),
    "policy": P3("sourced", "Free 30-day returns with a prepaid label. Free shipping over $100.",
                 R("YES", "YES", "YES", label="YES", days=30, refund="Refund, exchange or store credit", src="https://www.converse.com.au/help/returns-policy",
                   ev="we just ask that the items are returned and received within 30 days of your original order date"),
                 S("CONDITIONAL", 100, 10, src="https://www.converse.com.au/help/shipping-delivery/cost", ev="FREE for orders over $100 AUD | $10 AUD for orders under $100 AUD")),
}
EXTRA["bonds"] = {
    "sale": SALE3("LIVE", "https://www.bonds.com.au/", "40% OFF MEN'S CLOTHING WHEN YOU BUY 2 ... 40% OFF WOMEN'S CLOTHING WHEN YOU BUY 2",
                  name="Multi-buy offers (not Black Friday)", sale_type="regular", discount_text="40% off clothing when you buy 2",
                  discount_max_pct=40, discount_kind="flat", scope="SELECTED",
                  conditions="Black Friday not announced. A 'Cyber Weekend has begun' banner reported by research was not on the page on re-check."),
    "policy": P3("sourced", "120-day returns on purchases from 1 Oct. Free shipping for Bonds Rewards members, otherwise over $59.",
                 R("YES", "UNKNOWN", "UNKNOWN", instore="YES", days=120, note="120 days for purchases from 1 Oct 2026", sale_ex="CONDITIONAL",
                   src="https://www.bonds.com.au/returns-exchanges", ev="Enjoy 120-days of returns on all purchases from 1st October, online and in-store."),
                 S("CONDITIONAL", 59, 8.95, restr="Free on all orders for (free) Bonds Rewards members.", src="https://www.bonds.com.au/shipping-options",
                   ev="FREE standard shipping Australia-wide on orders over $59")),
}
