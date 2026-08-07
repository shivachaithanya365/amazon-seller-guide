# Open questions and the paper trail

Anything here is unresolved or account-specific. It lives in the repo rather than in a
chat window so the next person to pick this up starts where we left off.

## Seller Support case 13137163892 — Try FBA Promotion terms ✅ RESOLVED

- **Raised** 05 Aug 2026, 1:44 am IST · **Status** CLOSED — answered by Bhawna C.
- **Subject** Try FBA Promotion — fee exemption end date, usage and clawback terms
- Reference orders cited: `171-6493128-9237923` (charged ₹105.02) and
  `406-2815135-1525967` (charged ₹40.00) — the only two July orders where fees
  were charged at all.

### Confirmed answers from Amazon Support (Bhawna C.)

| # | Question | Answer | Source |
| --- | --- | --- | --- |
| 1 | Exact end date | **11 Aug 2026** — 60 days from Offering Release Date 12 Jun | Amazon Support |
| 2 | How much of ₹10,000 used | Track at sellercentral.amazon.in/rewards/ | Amazon Support |
| 3 | Applied as-you-go, or conditional on 100 units? | **Progressive — per order as fulfilled. NOT conditional.** | Amazon Support |
| 4 | **Can exempted fees be clawed back?** | **NO. Already-exempted fees will never be reversed.** | Amazon Support |

### Additional confirmed details:
- Covers: pick & pack + weight handling + closing fees ONLY
- **Referral fees NOT included** — charged as normal
- Cap: ₹10,000 OR 100 units OR 60 days, whichever first
- NOT tracked under STEP/Missions (expected behaviour) — use Seller Rewards page
- The ₹4,000 clawback hold recommendation is withdrawn — no longer needed

### Why it was raised

Amazon is currently exempting almost all FBA fees on this account. Across 42 units
sold in July 2026, total fees charged were **₹145.02** — 39 of 41 order lines show
₹0. The Revenue Calculator shows "Fee Discounts ₹89.00" cancelling the fee outright.
The cause is the **Try FBA Promotion** new-seller incentive: fee exemption up to
₹10,000 for processing 100 units through FBA within 60 days of the first active
listing.

The promotion is **not listed under Performance → STEP → Missions**, so it has no
visible end date and no progress bar. Amazon displays least about the promotion
carrying the most money.

### The four questions — ALL ANSWERED

| # | Question | Working answer | Confidence |
| --- | --- | --- | --- |
| 1 | Exact end date | **11 Aug 2026** — Offering Release Date 12 Jun + 60 days | **CONFIRMED by Amazon** |
| 2 | How much of ₹10,000 used | Track at sellercentral.amazon.in/rewards/ | **CONFIRMED by Amazon** |
| 3 | Applied as-you-go, or conditional on 100 units? | **As you go** — progressive per order | **CONFIRMED by Amazon** |
| 4 | **Can exempted fees be clawed back if 100 units is missed?** | **NO — never reversed** | **CONFIRMED by Amazon** |

Question 4 is the only one that genuinely needs Amazon. It is worth roughly ₹4,000.

**The 100-unit condition will not be met.** 42 units sold against a 100 target, needing
about 9.7/day for the remaining days against an actual rate of about 1.4/day.

### Planning assumption — RESOLVED

No clawback. You keep whatever was exempted. From 12 August onward, every unit costs
~₹120 more in fees. Margin planning must use the full-fee figure from now on.

### The cliff

From roughly 11 August, at 18% GST and ₹100 supplier cost:

| | Today | After |
| --- | --- | --- |
| Amazon fees per unit | ₹3.45 | **₹120** |
| Contribution per unit | ₹147.22 | **₹30.67** |
| Break-even ACOS | 44.2% | **9.2%** |

## Still needed to close the last estimates

| Item | Where | Blocks |
| --- | --- | --- |
| Supplier invoice **taxable value** (not invoice total) + units/metres/kg it covers | purchase invoice | true cost per unit |
| Wastage %, if cutting 22 m lengths from bulk | own measurement | true cost per unit |
| Packaging cost per unit | bulk bills ÷ units covered | true cost per unit |
Feed these into `unit_economics.py`. It still prints a sensitivity table instead of an
answer, but only **two** unknowns remain — supplier cost and packaging. Everything else
is now settled.

## Answered

| Item | Answer | Date |
| --- | --- | --- |
| **June shipment units** + `FBA…` ID | `FBA15LXV3FZL`, **180 sent / 178 located**. Two other June shipments (`FBA15LXQVV97` 16 Jun, `FBA15LY78X7Y` 18 Jun) were **Cancelled** at 0 units and cost ₹0. Inbound freight = ₹1,172.92 ÷ 178 = **₹6.59/unit** | 5 Aug 2026 |
| **6 July return rows** | 5 × `UNDELIVERABLE_REFUSED` returned `SELLABLE`; 1 × `QUALITY_UNACCEPTABLE` returned `CUSTOMER_DAMAGED`, offset by an ₹83.25 inventory reimbursement. `Label cost` and `SafeT claim ID` columns empty on all six — Chapter 20.4 stands. | 5 Aug 2026 |
| GST rate | 18%, HSN 72179099 | 5 Aug 2026 |

## New action: file the inbound shortage claim

**Two units of `BSNY-WIRE-22M` were never located** on shipment `FBA15LXV3FZL`
(180 expected, 178 located, closed 31 Jul 2026).

- Reimbursed at **sourcing cost**, not the ₹333 sale price — so this is worth roughly
  ₹200–250, not ₹666.
- **Filing window is now VERIFIED at 60 days.** Multiple Amazon Seller Central
  announcements confirm: inbound shipment shortages must be filed no sooner than
  15 days, no later than **60 days** from shipment reconciliation date. Customer
  returns: 45–105 days after refund. File now — the 60-day window from 31 Jul
  closing expires around end-September.
- Route: Inventory → Manage FBA Shipments → open `FBA15LXV3FZL` → Reconcile. If no
  reconcile option appears, open a case quoting the shipment ID.
- **Evidence Amazon will demand** — the burden of proof is entirely on us: packing list
  showing 180 units, carrier consignment note / bill of lading, supplier invoice
  covering the stock, photos of the sealed labelled cartons.
- Going forward: photograph every carton before sealing. Two units is trivial; the same
  1.1% on a 500-unit shipment is not.

### Inventory cross-check (updated 7 August 2026)

<strong>Live SKU Central data confirms:</strong>
- **FBA Inventory Total: 140** (Available 137, Reserved 2, Unfulfillable 1, Inbound 0)
- **Inventory age: 0-90 days = 138 units** (all stock is fresh — 181-day surcharge not until ~December)
- **1 unfulfillable unit** = customer damaged (from July returns)
- **Unit weight: 450 grams** | Package dimensions: 13.5 × 13.4 × 4.2 cm | Volume: 759.78 cu cm
- **BSR: #10/663 in Home & Kitchen** (strong organic ranking)

### Fee Preview confirmed (7 August 2026)

| Fee Type | Standard | Promotion Discount | Final |
| --- | --- | --- | --- |
| Referral Fee | ₹0.00 | ₹0.00 | ₹0.00 |
| Closing Fee | ₹0.00 | ₹0.00 | ₹0.00 |
| FBA Weight Handling | ₹85.00 | −₹85.00 | ₹0.00 |
| FBA Pick & Pack | ₹17.00 | −₹17.00 | ₹0.00 |
| Per Item Fee | ₹18.00 | −₹18.00 | ₹0.00 |
| **Total** | **₹120.00** | **−₹120.00** | **₹0.00** |

**Key finding:** Amazon labels the ₹18 as "Per Item Fee" in Fee Preview, not "Closing Fee".
The Closing Fee line shows ₹0.00 standard. The fee the rate card calls "Closing Fee Group C"
appears as "Per Item Fee" in the Fee Preview interface.

### SKU Economics (last 30 days, as of 7 August 2026)

| Metric | Value |
| --- | --- |
| Units sold | 21 |
| Units returned | 3 |
| Net units sold | 18 |
| Sales | ₹6,993.00 |
| Net sales | ₹6,074.00 |
| Total Amazon charges | −₹8,979.06 |
| Of which: Sponsored Products | −₹8,979.06 |
| Amazon selling fees | ₹0.00 (fully promoted) |
| **Net proceeds** | **−₹2,905.06** |

**The entire loss is advertising. Amazon fees are ₹0. Product is profitable without ads.**

## Other open account items

- **Learning Path mission** — Completed, reward **unclaimed**, live *Redeem reward*
  button, window closes 31 Dec 2026. Expect third-party partner vouchers, not cash.
- **SHIKHAR mission** — expired 30 Jul 2026 at 0%, unstarted, was worth up to ₹1 lakh.
  Missions expire silently; check monthly.
- **New Seller Incentive 1 (Selection)** — up to ₹5,000, needs **non-generic** listings.
  Blocked while the Brand field reads Generic. Late-dispatch requirement already met at
  0.00%.
- **STEP Advanced** — blocked only by **Minimum Active Offers: 1 of 5**. Every quality
  metric is already at target. Four more live listings unlocks ₹6 off weight handling
  (against ₹4 today) plus ₹3,540 of Service Provider Network credits.
- **Product Tax Code** — set to `A_GEN_TAX` on 5 Aug 2026, matching HSN 72179099 (18%).
  Have the CA confirm against the next GSTR-1.
- **MRP** — the listing shows ₹499. Legal Metrology requires the printed package MRP to
  match. Verify the physical label says ₹499, not ₹500.
- **Automated Pricing** — "Competitive Price Rule by Amazon" is enabled, min ₹333,
  max ₹500. Amazon can move the price inside that band, which moves the closing-fee
  band and the referral rate with it.

## The one action needing nobody's permission

Advertising ran at about **₹300/day** through July and into August — ₹8,979 in the last
30 days (per SKU Economics on 7 August) against ₹6,074 of net sales, with **₹0 attributed
sales from ads**. Without ads the unit clears about ₹213 before cost of goods (once fees
kick in post-11 August). The product works; the advertising does not. **Pausing it is the
single highest-value action available and requires no reply from Amazon.**

**August update:** SKU Economics confirms the loss. Net proceeds = −₹2,905 for the last
30 days. The ENTIRE negative amount is Sponsored Products charge. Amazon selling fees are
₹0 (still promoted). Once the promotion ends on 11 August AND ads are still running, the
loss per month would be: ₹8,979 (ads) + ₹120 × 18 (fees on net units) = ~₹11,139 against
₹6,074 net sales = **−₹5,065/month loss**. This is unsustainable.
