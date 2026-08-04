# Open questions and the paper trail

Anything here is unresolved or account-specific. It lives in the repo rather than in a
chat window so the next person to pick this up starts where we left off.

## Seller Support case 13137163892 — Try FBA Promotion terms

- **Raised** 05 Aug 2026, 1:44 am IST · **Status** Work in progress
- **Subject** Try FBA Promotion — fee exemption end date, usage and clawback terms
- Reference orders cited: `171-6493128-9237923` (charged ₹105.02) and
  `406-2815135-1525967` (charged ₹40.00) — the only two July orders where fees
  were charged at all.

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

### The four questions, and our working answers

| # | Question | Working answer | Confidence |
| --- | --- | --- | --- |
| 1 | Exact end date | **~11 Aug 2026** — Offering Release Date 12 Jun + 60 days | derived, not confirmed |
| 2 | How much of ₹10,000 used | **~₹3,600–4,900** — 42 units × ₹89–120 expected, less ₹145.02 charged | derived |
| 3 | Applied as-you-go, or conditional on 100 units? | **As you go** — 39 of 41 lines are already at ₹0 | strong inference |
| 4 | **Can exempted fees be clawed back if 100 units is missed?** | **UNKNOWN** | needs Amazon |

Question 4 is the only one that genuinely needs Amazon. It is worth roughly ₹4,000.

**The 100-unit condition will not be met.** 42 units sold against a 100 target, needing
about 9.7/day for the remaining days against an actual rate of about 1.4/day.

### Planning assumption until answered

Assume fees **can** be reversed. Keep about ₹4,000 unspent. If a reversal lands and it
affects a disbursement, that *does* meet Amazon's "Urgent Help Needed" criteria — the
original case was deliberately not flagged urgent, since it met none of them.

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
| **June shipment units** + `FBA…` shipment ID | Inventory → Manage FBA Shipments, 16–17 Jun | inbound freight per unit (₹1,172.92 total) |
| **6 July return rows** — reason, resolution, in-policy | Reports → Fulfilment → Customer Returns | the 14.3% refund rate |

Feed the first four into `unit_economics.py`. It currently prints a sensitivity table
instead of an answer because they are unknown.

Two columns in the returns report worth checking when pulling those rows:
`Label cost` / `Label to be paid by` (an uncounted per-return cost if Amazon billed the
labels to us), and `SafeT claim ID` / `SafeT claim state` — if any are populated on an
FBA order, that contradicts Chapter 20.4 and the book needs correcting.

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

Advertising ran at about **₹500/day** through July — ₹15,554 against ₹11,988 of net
revenue, with **₹0 attributed sales**. Without ads the unit clears about ₹190 before
cost of goods. The product works; the advertising does not. Pausing it is the single
highest-value action available and requires no reply from Amazon.
