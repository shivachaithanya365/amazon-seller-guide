#!/usr/bin/env python3
"""Compute the real unit economics from the Seller Central exports.

    cd research/account && python3 analyse_account.py

Everything Chapter 3 and Chapter 9 of the handbook assert about this seller's
position should be reproducible from here. Where a figure in the book disagrees
with this script, the script wins - it reads the account exports directly.
"""
import csv, collections, datetime, pathlib, sys

HERE = pathlib.Path(__file__).parent
TX = HERE / "transactions_60d.csv"
FP = HERE / "fee_preview_50051020669.csv"
for p in (TX, FP):
    if not p.exists():
        sys.exit(f"{p.name} not found - run this script from inside research/account/")

def num(s):
    s = (s or "").strip().replace(",", "")
    try:
        return float(s)
    except ValueError:
        return 0.0

rows = list(csv.DictReader(TX.open(encoding="utf-8-sig")))
for r in rows:
    d, m, y = r["Date"].split("/")
    r["_d"] = datetime.date(int(y), int(m), int(d))
    r["_charges"] = num(r["Total product charges"])
    r["_fees"] = num(r["Amazon fees"])
    r["_total"] = num(r["Total (INR)"])

UNIT_PRICE = 333.0
JULY = lambda r: r["_d"].month == 7 and r["_d"].year == 2026

# --- units -------------------------------------------------------------------
orders = [r for r in rows if r["Transaction type"] == "Order Payment"]
refunds = [r for r in rows if r["Transaction type"] == "Refund"]
j_orders = [r for r in orders if JULY(r)]
j_refunds = [r for r in refunds if JULY(r)]

# a 666 line is two units at 333
units = lambda rs: int(round(sum(abs(r["_charges"]) for r in rs) / UNIT_PRICE))
j_units_gross = units(j_orders)
j_units_refunded = units(j_refunds)
j_units_net = j_units_gross - j_units_refunded

# --- advertising -------------------------------------------------------------
ads = [r for r in rows if "advertising" in r["Product Details"].lower()]
j_ads = [r for r in ads if JULY(r)]
ads_total = sum(-r["_fees"] for r in ads)
j_ads_total = sum(-r["_fees"] for r in j_ads)

# --- fee preview: Amazon's own per-unit fee for this SKU ---------------------
fp = next(csv.DictReader(FP.open(encoding="utf-8-sig")))
f_ref = num(fp["estimated-referral-fee-per-unit"])
f_close = num(fp["estimated-fixed-closing-fee"])
f_pick = num(fp["estimated-pick-pack-fee-per-unit"])
f_wh = num(fp["estimated-weight-handling-fee-per-unit"])
f_total = num(fp["estimated-fee-total"])
pkg_g = num(fp["item-package-weight"])

print("=" * 74)
print("FEE PREVIEW - Amazon's own numbers for", fp["sku"])
print("=" * 74)
print(f"  price                       Rs {num(fp['your-price']):>8.2f}")
print(f"  referral fee                Rs {f_ref:>8.2f}   <- 0 confirms a HOME category, not Wires")
print(f"  closing fee                 Rs {f_close:>8.2f}   <- Group C, 301-500 band")
print(f"  pick & pack                 Rs {f_pick:>8.2f}")
print(f"  weight handling             Rs {f_wh:>8.2f}   <- see note below")
print(f"  {'-'*46}")
print(f"  fee total                   Rs {f_total:>8.2f}   (parts sum to {f_ref+f_close+f_pick+f_wh:.2f})")
print(f"  + GST at 18%                Rs {f_total*0.18:>8.2f}")
print(f"  = Amazon's cut per unit     Rs {f_total*1.18:>8.2f}   ({f_total*1.18/UNIT_PRICE*100:.1f}% of {UNIT_PRICE:.0f})")
print()
print(f"  package weight {pkg_g:.2f} g - under 500 g, so the first-500g rate should apply.")
print(f"  Rs {f_wh:.0f} is the 500g-1kg NATIONAL rate at Standard STEP, not the first-500g rate")
print(f"  (Rs 65). Amazon is billing one weight band higher than the raw product weight")
print(f"  implies - most likely because outbound packaging pushes it past 500 g.")

print()
print("=" * 74)
print("JULY 2026 - actuals from the transaction export")
print("=" * 74)
print(f"  units sold (gross)          {j_units_gross:>6}")
print(f"  units refunded              {j_units_refunded:>6}   ({j_units_refunded/j_units_gross*100:.1f}% of gross)")
print(f"  units net                   {j_units_net:>6}")
print(f"  gross revenue               Rs {j_units_gross*UNIT_PRICE:>9,.2f}")
print(f"  net revenue                 Rs {j_units_net*UNIT_PRICE:>9,.2f}")
print()
print(f"  advertising charges in July  {len(j_ads):>5} charges")
for r in sorted(j_ads, key=lambda r: r["_d"]):
    print(f"     {r['_d']}   Rs {-r['_fees']:>9,.2f}")
print(f"  {'-'*46}")
print(f"  July advertising            Rs {j_ads_total:>9,.2f}")
print(f"  advertising in the file     Rs {ads_total:>9,.2f}  (28 Jun - 2 Aug)")
print()
print(f"  ad cost per NET unit        Rs {j_ads_total/j_units_net:>9,.2f}")
print(f"  ad cost per gross unit      Rs {j_ads_total/j_units_gross:>9,.2f}")
print(f"  TACOS on net revenue        {j_ads_total/(j_units_net*UNIT_PRICE)*100:>9.1f}%")

# --- other charges -----------------------------------------------------------
storage = sum(-r["_fees"] for r in rows if "storage" in r["Product Details"].lower())
inbound = sum(-r["_total"] for r in rows if "inbound transportation" in r["Product Details"].lower())
reimb = sum(r["_total"] for r in rows if "reimbursement" in r["Product Details"].lower())

print()
print("=" * 74)
print("PER-UNIT P&L, using Amazon's own fee figures and actual July ad spend")
print("=" * 74)
amazon = f_total * 1.18
ad_unit = j_ads_total / j_units_net
storage_unit = storage / j_units_net
lines = [("selling price", UNIT_PRICE),
         ("Amazon fees incl. GST", -amazon),
         ("advertising", -ad_unit),
         ("storage", -storage_unit)]
run = 0.0
for label, v in lines:
    run += v
    print(f"  {label:<28} Rs {v:>10,.2f}")
print(f"  {'-'*46}")
print(f"  {'before cost of goods':<28} Rs {run:>10,.2f}")
print()
print(f"  Every unit sold loses about Rs {abs(run):,.0f} BEFORE paying for the wire,")
print(f"  the packaging or the inbound freight. Selling more makes it worse.")
print()
print(f"  For contrast, the handbook's Chapter 3 stated a loss of Rs 39.94 per unit,")
print(f"  built from a 7-day ad figure projected to 30 days (Rs 7,963) and divided by")
print(f"  32 units. Actual July spend was Rs {j_ads_total:,.0f} over {j_units_net} net units.")

print()
print("=" * 74)
print("OTHER CHARGES IN THE PERIOD")
print("=" * 74)
print(f"  FBA storage fee             Rs {storage:>9,.2f}")
print(f"  inbound transportation      Rs {inbound:>9,.2f}")
print(f"  FBA inventory reimbursement Rs {reimb:>9,.2f}  (credit - Amazon repaid a lost/damaged unit)")
print()
print("  Cross-account debt adjustments appear in pairs that net to zero")
print("  (-666/+666, -999/+999, -416.25/+416.25) - they move money between the COD")
print("  and electronic ledgers and are not a cost. Do not count them.")
