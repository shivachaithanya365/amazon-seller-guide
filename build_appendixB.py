#!/usr/bin/env python3
"""Build a verified Appendix B: three closing-fee tiers, each with two price bands."""
import json, pathlib, re

g = json.loads(pathlib.Path("closing_groups_live.json").read_text(encoding="utf-8"))

def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

TIERS = [
    ("Standard Fee tier", "Group #", "Group #", "Group ##", "₹26", "₹22",
     "The default tier. Most categories sit here, and it is the most expensive."),
    ("Select categories &mdash; tier 1", "Group A", "Group A", "Group C", "₹20", "₹18",
     "A cheaper tier. <strong>Your Home / Home Improvement categories are in this tier.</strong>"),
    ("Select categories &mdash; tier 2", "Group B", "Group B", "Group D", "₹13", "₹14",
     "The cheapest tier at ₹0–300. Note it is the only tier where the ₹301–500 rate is "
     "<em>higher</em> than the ₹0–300 rate."),
]

out = []
out.append('''<table>
<thead><tr><th style="width:52mm">Tier</th><th style="width:30mm">₹0–300</th>
<th style="width:30mm">₹301–500</th><th>Categories</th></tr></thead>
<tbody>''')
for name, key, gl, gh, lo, hi, _ in TIERS:
    n = len(g.get(key, []))
    out.append(f'<tr><td><strong>{name}</strong></td>'
               f'<td>{lo} <small>({gl})</small></td>'
               f'<td>{hi} <small>({gh})</small></td>'
               f'<td>{n} categories</td></tr>')
out.append('''<tr><td colspan="3"><strong>₹501–1,000 — all categories</strong></td><td><strong>₹27</strong></td></tr>
<tr><td colspan="3"><strong>Above ₹1,000 — all categories</strong></td><td><strong>₹52</strong>, or ₹72 for select categories</td></tr>
</tbody></table>''')

for name, key, gl, gh, lo, hi, note in TIERS:
    items = g.get(key, [])
    if not items:
        continue
    out.append(f'<h2>{name} — {lo} at ₹0–300 ({gl}) · {hi} at ₹301–500 ({gh}) '
               f'<span class="tag v">VERIFIED</span></h2>')
    out.append(f'<p>{note} <small>{len(items)} categories.</small></p>')
    out.append('<p class="src cols2">' + ' · '.join(esc(c) for c in sorted(items)) + '</p>')

pathlib.Path("appendixB_body.html").write_text('\n'.join(out), encoding="utf-8")
tot = sum(len(g.get(k, [])) for _, k, *_ in TIERS)
print(f"Appendix B built — {tot} category assignments across 3 tiers")
for name, key, *_ in TIERS:
    print(f"  {len(g.get(key, [])):3}  {re.sub('&[a-z]+;', '-', name)}")
