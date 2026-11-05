# Batch 2 (added 2026-11-05 evening): brands the user asked to add plus suggested additions.
# Executed by build_research.py with R, S, P, SALE, T in scope. VERIFIED = sale records checked directly.
T2 = "2026-11-05T10:00:00+00:00"
VERIFIED = {"evdnce"}
EXTRA = {}

EXTRA["evdnce"] = {
    "sale": {**SALE("LIVE", "https://evdnce.com/", "UP TO 50% OFF SITEWIDE LIVE NOW",
                    name="Sitewide sale (not labelled Black Friday)", discount_text="Up to 50% off sitewide", discount_max_pct=50,
                    discount_kind="up_to", scope="SITEWIDE",
                    conditions="'Up to' 50%: discounts vary by item. The banner doesn't say Black Friday or give an end date."),
             "verified_at": T2},
}
