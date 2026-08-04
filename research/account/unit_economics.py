#!/usr/bin/env python3
"""Work out the true profit per unit, once you know your cost of goods.

    cd research/account && python3 unit_economics.py

Fill in the four UNKNOWNs below and it prints your real contribution per unit,
your break-even ACOS, and how many units a month you need to cover advertising.

Two things this handles that a naive margin sheet gets wrong:

1. GST on Amazon's fees is NOT a cost to you. You are GST-registered, so the 18%
   Amazon charges on its fees is input tax credit - you offset it against your own
   GST liability. Treating it as a cost overstates your costs by about Rs 21.60
   a unit. (Confirm the treatment with your CA, but this is the normal position.)

2. Your Rs 333 selling price INCLUDES GST. You have to remit that GST out of the
   Rs 333 - Amazon does not add it on top. So your real revenue is Rs 333 divided
   by (1 + your GST rate), not Rs 333. On an 18% product that is Rs 282.20, not
   Rs 333. Missing this overstates revenue by about Rs 50 a unit.

Those two errors point in opposite directions but do not cancel: the net effect is
that a sheet ignoring both overstates contribution by roughly Rs 29 a unit.
"""

# ---------------------------------------------------------------------------
# KNOWN - from your Fee Preview and transaction export, already verified
# ---------------------------------------------------------------------------
PRICE_INCL_GST   = 333.00   # what the customer pays

# Two fee scenarios, because your fees are currently being WAIVED.
#   Amazon charged Rs 145.02 in fees across 42 units sold in July. At the
#   Fee Preview rate of Rs 120/unit it would have been Rs 5,040. 39 of 41 order
#   lines show Rs 0. The Revenue Calculator shows 'Fee Discounts Rs 89.00'
#   cancelling the whole fee, and the dashboard offers a New Seller Incentive
#   worth Rs 41,000. So today you pay almost nothing in Amazon fees.
#   THAT WILL END. Model both.
FEES_TODAY       = 145.02 / 42          # actual, averaged over July units
FEES_AFTER       = 120.00               # Fee Preview: 0 referral + 18 closing
                                        # + 17 pick&pack + 85 weight handling
AMAZON_FEES      = FEES_AFTER           # switch to FEES_TODAY to see the current position
GST_ON_FEES      = AMAZON_FEES * 0.18          # reclaimable as input credit
STORAGE_MONTH    = 23.02    # FBA storage fee, July
ADS_MONTH        = 15554.00 # advertising charged in July
UNITS_NET_MONTH  = 36       # units sold minus refunds, July
REFUND_RATE      = 6 / 42   # 6 refunded of 42 gross
INBOUND_FREIGHT  = 1172.92  # Inbound Transportation Fee, 17 June

# CONFIRMED 5 Aug 2026 from Inventory > Manage FBA Shipments. Three shipments were
# created 16-18 June; only ONE actually shipped:
#
#   FBA15LXQVV97  created 16 Jun  Cancelled  0 expected / 0 located   fee Rs 0.00
#   FBA15LXV3FZL  created 17 Jun  Closed   180 expected / 178 located fee Rs 1,172.92
#   FBA15LY78X7Y  created 18 Jun  Cancelled  0 expected / 0 located   no fee row
#
# The Rs 1,172.92 dated 17/6 maps to FBA15LXV3FZL exactly. The two cancelled
# shipments cost nothing - verified against the transaction export, which has a
# second Inbound Transportation Fee row dated 16/6 for Rs 0.00 and no row at all
# for 18/6. So the whole inbound charge belongs to one 180-unit shipment.
SHIPMENT_UNITS_SENT     = 180   # units Amazon expected
SHIPMENT_UNITS_RECEIVED = 178   # units Amazon actually located - TWO SHORT

# ---------------------------------------------------------------------------
# UNKNOWN - fill these in. Set to None to see what happens across a range.
# ---------------------------------------------------------------------------
GST_RATE         = 0.18     # CONFIRMED. The listing's HSN code is 72179099 - heading
                            # 7217, wire of iron or non-alloy steel - which attracts 18%
                            # GST. Read from the listing's External Product Information
                            # field on 5 August 2026.
                            # NOTE: the listing's Product Tax Code field is EMPTY, which
                            # is a separate problem - see the handbook, section 8.8.
SUPPLIER_COST    = None     # Rs per unit, EX-GST (the taxable value on the invoice,
                            # not the invoice total - the GST part is input credit)
PACKAGING_COST   = None     # Rs per unit: poly bag + FNSKU label + insert card

# NO LONGER UNKNOWN. Spread over units RECEIVED (178), not units sent (180),
# because the two units Amazon could not locate will never earn revenue - so the
# freight paid to move them has to be carried by the units that did arrive.
#   1172.92 / 178 = Rs 6.59 a unit   <- used
#   1172.92 / 180 = Rs 6.52 a unit   (understates it by 7 paise)
SHIPMENT_UNITS   = SHIPMENT_UNITS_RECEIVED


def economics(gst_rate, supplier, packaging, shipment_units):
    """Return a dict of the real per-unit numbers."""
    net_revenue = PRICE_INCL_GST / (1 + gst_rate)      # ex-GST, what you actually keep
    output_gst = PRICE_INCL_GST - net_revenue
    inbound_unit = INBOUND_FREIGHT / shipment_units
    storage_unit = STORAGE_MONTH / UNITS_NET_MONTH
    cogs = supplier + packaging + inbound_unit
    # GST on fees is reclaimed, so it is not subtracted here
    contribution = net_revenue - AMAZON_FEES - cogs - storage_unit
    # A refund loses the sale but you still paid weight handling + pick & pack.
    # VALIDATED against the July returns report: 5 of 6 returns came back SELLABLE,
    # so Amazon restocks the unit and you do NOT lose the cost of goods - only the
    # fulfilment you already paid. The 6th was CUSTOMER_DAMAGED and Amazon credited
    # an 83.25 inventory reimbursement against the 82.60 refund fee, so it was
    # roughly neutral. Modelling this as fees-only is therefore correct.
    refund_drag = REFUND_RATE * (85.00 + 17.00)
    contribution_after_refunds = contribution - refund_drag
    ad_unit = ADS_MONTH / UNITS_NET_MONTH
    return dict(net_revenue=net_revenue, output_gst=output_gst, inbound_unit=inbound_unit,
                storage_unit=storage_unit, cogs=cogs, contribution=contribution,
                refund_drag=refund_drag, after_refunds=contribution_after_refunds,
                ad_unit=ad_unit, profit_now=contribution_after_refunds - ad_unit,
                breakeven_acos=contribution_after_refunds / PRICE_INCL_GST,
                breakeven_units=ADS_MONTH / contribution_after_refunds
                                 if contribution_after_refunds > 0 else float('inf'))


def show(gst_rate, supplier, packaging, shipment_units):
    e = economics(gst_rate, supplier, packaging, shipment_units)
    print(f"  selling price (incl GST)      Rs {PRICE_INCL_GST:>9.2f}")
    print(f"  less output GST at {gst_rate*100:.0f}%        Rs {-e['output_gst']:>9.2f}   you remit this")
    print(f"  = real revenue                Rs {e['net_revenue']:>9.2f}")
    print(f"  less Amazon fees              Rs {-AMAZON_FEES:>9.2f}   GST on these is reclaimed, not a cost")
    print(f"  less supplier cost (ex-GST)   Rs {-supplier:>9.2f}")
    print(f"  less packaging                 Rs {-packaging:>9.2f}")
    print(f"  less inbound freight          Rs {-e['inbound_unit']:>9.2f}   {INBOUND_FREIGHT:.2f} / {shipment_units} units")
    print(f"  less storage                  Rs {-e['storage_unit']:>9.2f}")
    print(f"  {'-'*52}")
    print(f"  contribution per unit         Rs {e['contribution']:>9.2f}   before advertising")
    print(f"  less refund drag              Rs {-e['refund_drag']:>9.2f}   {REFUND_RATE*100:.1f}% x (weight 85 + pick&pack 17)")
    print(f"  = contribution after refunds  Rs {e['after_refunds']:>9.2f}")
    print()
    print(f"  advertising at July's rate    Rs {-e['ad_unit']:>9.2f}   {ADS_MONTH:,.0f} / {UNITS_NET_MONTH} units")
    print(f"  PROFIT PER UNIT TODAY         Rs {e['profit_now']:>9.2f}")
    print()
    print(f"  break-even ACOS               {e['breakeven_acos']*100:>9.1f}%   spend more than this on ads and you lose money")
    print(f"  units/month to cover ads      {e['breakeven_units']:>9.1f}   at {ADS_MONTH:,.0f} of ad spend")


if None in (GST_RATE, SUPPLIER_COST, PACKAGING_COST, SHIPMENT_UNITS):
    print(__doc__)
    print("=" * 78)
    print("NOT YET FILLED IN - showing a sensitivity range instead")
    print("=" * 78)
    print("""
To fill this in you need four numbers:

  GST_RATE        Your supplier invoice shows an HSN code and a GST rate. Use that
                  rate. Do not guess between 12% and 18% - it is worth about Rs 15
                  a unit.
  SUPPLIER_COST   The TAXABLE VALUE on the invoice divided by units received.
                  Not the invoice total. The GST you paid is input credit.
  PACKAGING_COST  Poly bag + FNSKU label + insert card, per unit. Divide a bulk
                  purchase by the number of units it covers.

Two of the original four are now settled:
  GST_RATE        18%, from HSN 72179099 on the listing.
  SHIPMENT_UNITS  178 received of 180 sent, shipment FBA15LXV3FZL. Inbound
                  freight is therefore Rs 6.59 a unit - small, and not your problem.
""")
    print("=" * 78)
    print("Sensitivity: contribution after refunds, BEFORE advertising")
    print("(rows = supplier cost ex-GST, columns = GST rate; packaging Rs 8,")
    print(f" inbound spread over {SHIPMENT_UNITS} units received = Rs "
          f"{INBOUND_FREIGHT/SHIPMENT_UNITS:.2f}/unit)")
    print("=" * 78)
    rates = [0.05, 0.12, 0.18]
    print("      supplier  " + "".join(f"{r*100:>12.0f}%" for r in rates))
    for supplier in (60, 80, 100, 120, 140, 160):
        cells = []
        for r in rates:
            e = economics(r, supplier, 8.0, SHIPMENT_UNITS)
            cells.append(f"Rs {e['after_refunds']:>8.2f}")
        print(f"      Rs {supplier:>5}   " + "  ".join(cells))
    print()
    print("Read it like this: find your supplier cost on the left and your GST rate")
    print("along the top. That cell is what one unit contributes before you spend")
    print("anything on advertising. Advertising is currently Rs 432.06 per unit, so")
    print("every cell in this table is far below what the ads cost.")
else:
    print("=" * 78)
    print("YOUR REAL UNIT ECONOMICS")
    print("=" * 78)
    show(GST_RATE, SUPPLIER_COST, PACKAGING_COST, SHIPMENT_UNITS)
