#!/usr/bin/env python3
"""Turn the 219 live referral-fee rows into a clean, fully-verified Appendix A."""
import re, json, pathlib

rows = json.loads(pathlib.Path("referral_fees_live.json").read_text(encoding="utf-8"))

def pct(p):
    p = p.rstrip('%').strip()
    f = float(p)
    return (f"{f:.2f}".rstrip('0').rstrip('.')) + '%'

def rupee(n):
    return '₹' + n.strip()

def fmt(fee):
    """Compact readable form, preserving the order of dated rule-sets."""
    parts = [s.strip() for s in fee.split('|') if s.strip()]
    segments, out = [], []          # segments = list of (rules_str, note)
    for p in parts:
        if not re.search(r'item price', p, re.I):
            note = p.strip('() ').strip()
            if note:
                segments.append((' · '.join(out), note)); out = []
            continue
        m = re.match(r'([\d.]+\s*%)\s*for item price\s*(.*)$', p, re.I)
        if not m:
            continue
        rate, cond = pct(m.group(1)), m.group(2).strip()
        c = None
        mm = re.match(r'<=\s*([\d,]+)$', cond)
        if mm: c = f"up to {rupee(mm.group(1))}"
        if c is None:
            mm = re.match(r'>\s*([\d,]+)\s*and\s*<=\s*([\d,]+)$', cond)
            if mm: c = f"{rupee(mm.group(1))}–{mm.group(2)}"
        if c is None:
            mm = re.match(r'>\s*([\d,]+)$', cond)
            if mm: c = f"above {rupee(mm.group(1))}"
        if c is None:
            c = cond
        out.append(f"{rate} {c}")
    if out:
        segments.append((' · '.join(out), None))

    if len(segments) == 1 and segments[0][1] is None:
        return segments[0][0]

    # dated rule-sets: mark which one is in force today (4 Aug 2026)
    pieces = []
    for rules, note in segments:
        if not rules:
            continue
        if note and re.search(r'until', note, re.I):
            pieces.append(f'<s>{rules}</s> <small>({note} &mdash; expired)</small>')
        elif note and re.search(r'from', note, re.I):
            pieces.append(f'<strong>{rules}</strong> <small>({note} &mdash; in force now)</small>')
        elif note:
            pieces.append(f'{rules} <small>({note})</small>')
        else:
            pieces.append(rules)
    return '<br>'.join(pieces)

def esc(s):
    return (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
             .replace('–', '&ndash;'))

# lightweight family grouping, following Amazon's own document order
FAMILIES = [
    ("Automotive, Car &amp; Accessories",      r'^(automotive|vehicle|oils|car )'),
    ("Baby, Toys &amp; Education",             r'^(toys|baby|breast pump|diaper bag)'),
    ("Books, Music, Movies &amp; Video Games", r'^(books|school textbook|video games|movies|music|musical)'),
    ("Industrial, Medical, Scientific &amp; Office", r'^(masks|3d printer|business|power &|stethoscop|packing material|office)'),
    ("Clothing, Fashion, Jewellery, Luggage &amp; Shoes", r'^(apparel|pants|backpack|eyewear|fashion jewel|fine jewel|silver|handbag|luggage|flip flop|kids shoe|shoes|wallet|watch)'),
    ("Electronics, Cameras, Mobile &amp; PC",  r'^(camera|cases|accessories|electronic device|gps|hard disk|headset|keyboard|kindle|laptop|desktop|monitor|mobile|tablet|scanner|memory|speaker|power bank|smart watch|pc component|entertainment collect|software|cables|television|modem|usb|landline|projector)'),
    ("Grocery, Food &amp; Pet Supplies",       r'^(grocery|pet)'),
    ("Health, Beauty &amp; Personal Care",     r'^(beauty|luxury beauty|face wash|moisturi|sunscreen|deodor|facial|personal care|health|feminine|body support|otc|pharmacy)'),
    ("Home, D&eacute;cor, Home Improvement, Furniture, Garden", r'^(bean bag|rugs|mattress|clocks|wall|home|office furniture|tiles|wires|craft|water|sanitary|inverter|cleaning and home|ladder|indoor lighting|doors|led|cushion|curtain|slipcover|safes|lawn|shelf|shelves|netting|large furniture|furniture)'),
    ("Kitchen &amp; Appliances",               r'^(kitchen|containers|cookware|major appliance|chimney|refrigerator|small appliance|fans)'),
    ("Sports &amp; Gym",                       r'^(bicycles|gym|sports)'),
]

buckets = {name: [] for name, _ in FAMILIES}
buckets["Other categories"] = []
for r in rows:
    cat = r["category"]
    placed = False
    for name, pat in FAMILIES:
        if re.match(pat, cat, re.I):
            buckets[name].append(r); placed = True; break
    if not placed:
        buckets["Other categories"].append(r)

html_out = []
total = 0
for name in [n for n, _ in FAMILIES] + ["Other categories"]:
    items = buckets[name]
    if not items: continue
    total += len(items)
    html_out.append(f'<h2>{name} <span class="tag v">VERIFIED</span></h2>')
    html_out.append('<table class="tight fixed">')
    html_out.append('<thead><tr><th style="width:82mm">Category</th>'
                    '<th style="width:96mm">Referral fee</th></tr></thead>\n<tbody>')
    for r in items:
        html_out.append(f'<tr><td>{esc(r["category"])}</td><td>{fmt(r["fee"])}</td></tr>')
    html_out.append('</tbody></table>')

pathlib.Path("appendixA_body.html").write_text('\n'.join(html_out), encoding="utf-8")
print(f"rows written: {total} of {len(rows)}")
for name in [n for n,_ in FAMILIES] + ["Other categories"]:
    if buckets[name]: print(f"  {len(buckets[name]):3}  {re.sub('&[a-z]+;','&',name)}")
