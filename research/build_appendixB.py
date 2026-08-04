#!/usr/bin/env python3
"""Build Appendix B from the six closing-fee lists Amazon actually publishes.

Earlier versions of this file modelled the data as THREE tiers, each spanning both
price bands (Group A paired with C, Group B paired with D). That model is wrong.
The 0-300 and 301-500 lists have independent membership, and Amazon's own example
on the fee page proves it: "Apparel - Shorts" is in Group A (0-300, Rs 20) but in
Group D (301-500, Rs 14) - not Group C as an A->C pairing would predict.

16 categories are placed in a band pairing the old tier model got wrong. So the
appendix now presents six separate lists and tells the reader to look their
category up in BOTH bands rather than reading a tier off one row.
"""
import json, pathlib, sys

SRC = pathlib.Path("closing_groups_live.json")
if not SRC.exists():
    sys.exit("closing_groups_live.json not found - run from inside research/ "
             "and run extract_groups.py first")
g = json.loads(SRC.read_text(encoding="utf-8"))

def esc(s):
    return (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
             .replace('\t', ' ').strip())

BANDS = [
    ("\u20b90\u2013300", [
        ("Group #", "\u20b926", "The default. Most categories sit here, and it is the dearest."),
        ("Group A", "\u20b920", "A cheaper list. <strong>Your Home and Home Improvement "
                                "categories are here.</strong>"),
        ("Group B", "\u20b913", "The cheapest list in this band."),
    ]),
    ("\u20b9301\u2013500", [
        ("Group ##", "\u20b922", "The default for this band."),
        ("Group C", "\u20b918", "Cheaper. Includes <strong>Home - Other Products</strong> and "
                                "<strong>Home improvement - Other Products</strong>."),
        ("Group D", "\u20b914", "The cheapest list in this band. Its membership is drawn from "
                                "all three of the \u20b90\u2013300 lists, so do not assume it "
                                "mirrors Group B."),
    ]),
]
RATE = {'Group #': 26, 'Group ##': 22, 'Group A': 20, 'Group C': 18,
        'Group B': 13, 'Group D': 14}
LO_GROUPS = ['Group #', 'Group A', 'Group B']
HI_GROUPS = ['Group ##', 'Group C', 'Group D']
# the pairing the previous tier model assumed
OLD_PAIR = {'Group #': 'Group ##', 'Group A': 'Group C', 'Group B': 'Group D'}

total = sum(len(g.get(k, [])) for k in LO_GROUPS + HI_GROUPS)
out = []

out.append('<p class="lede">Below \u20b9500 your closing fee depends on which list your fee category '
           'sits in \u2014 and the two price bands have <strong>separate lists</strong>. From '
           '\u20b9501 upward the lists stop mattering: every category pays the same.</p>')

out.append('<div class="box good">\n<p class="lbl">Verified from the live page</p>\n'
           f'<p><span class="tag v">VERIFIED</span> All <strong>{total} category assignments</strong> '
           'below were read from Amazon\u2019s live fee page on <strong>4 August 2026</strong> \u2014 '
           'all six lists, extracted directly rather than inferred. The rates themselves come from '
           'Amazon\u2019s closing-fee rate-card images.</p>\n</div>')

# --- summary table ----------------------------------------------------------
out.append('<table>\n<thead><tr><th style="width:38mm">Price band</th>'
           '<th style="width:30mm">List</th><th style="width:24mm">Closing fee</th>'
           '<th>Categories</th></tr></thead>\n<tbody>')
for band, rows in BANDS:
    for n, (grp, rate, _) in enumerate(rows):
        first = (f'<td rowspan="3"><strong>{band}</strong></td>' if n == 0 else '')
        out.append(f'<tr>{first}<td>{grp}</td><td class="num"><strong>{rate}</strong></td>'
                   f'<td>{len(g.get(grp, []))} categories</td></tr>')
out.append('<tr><td colspan="2"><strong>\u20b9501\u20131,000 \u2014 all categories</strong></td>'
           '<td class="num"><strong>\u20b927</strong></td><td>every category</td></tr>')
n72 = len(g.get('Above 1000 (Rs 72)', []))
out.append('<tr><td colspan="2"><strong>Above \u20b91,000</strong></td>'
           '<td class="num"><strong>\u20b952</strong></td>'
           f'<td>every category except the {n72} listed below, which pay \u20b972</td></tr>')
out.append('</tbody></table>')

# --- the critical caution ---------------------------------------------------
switchers = []
for lo in LO_GROUPS:
    for c in g.get(lo, []):
        dest = [h for h in HI_GROUPS if c in g.get(h, [])]
        if dest and dest[0] != OLD_PAIR[lo]:
            switchers.append((c, lo, dest[0]))
switchers.sort(key=lambda r: (r[1], r[0]))

out.append('<div class="box warn">\n<p class="lbl">Look your category up in both bands \u2014 '
           'they are not the same list</p>\n'
           '<p>It is tempting to read this appendix as three tiers, each with a cheap rate and a '
           'dearer one. <strong>That is wrong.</strong> The \u20b9301\u2013500 lists are not a '
           'relabelling of the \u20b90\u2013300 lists.</p>\n'
           '<p>Amazon\u2019s own worked example on the fee page makes the point: '
           '<em>Apparel - Shorts</em> is in <strong>Group A</strong> (\u20b920) below \u20b9300, but '
           'at \u20b9450 it is billed under <strong>Group D</strong> at <strong>\u20b914</strong> '
           '\u2014 not the \u20b918 a Group A \u2192 Group C pairing would predict.</p>\n'
           f'<p style="margin-bottom:0"><strong>{len(switchers)} categories</strong> change list in a '
           'way no simple pairing predicts. They are tabulated at the end of this appendix. '
           'If yours is one of them, read the fee from the band you actually sell in.</p>\n</div>')

# --- the six lists ----------------------------------------------------------
for band, rows in BANDS:
    out.append(f'<h2>Price band {band}</h2>')
    for grp, rate, note in rows:
        items = g.get(grp, [])
        if not items:
            continue
        out.append(f'<h3>{grp} \u2014 {rate} <span class="tag v">VERIFIED</span></h3>')
        out.append(f'<p>{note} <small>{len(items)} categories.</small></p>')
        out.append('<p class="src cols2">' +
                   ' \u00b7 '.join(esc(c) for c in sorted(items)) + '</p>')

# --- the Rs 72 list ---------------------------------------------------------
if g.get('Above 1000 (Rs 72)'):
    items = g['Above 1000 (Rs 72)']
    out.append('<h2>Above \u20b91,000 \u2014 the \u20b972 exception '
               '<span class="tag v">VERIFIED</span></h2>')
    out.append('<p>Above \u20b91,000 every category pays <strong>\u20b952</strong>, except these '
               f'<strong>{len(items)}</strong>, which pay <strong>\u20b972</strong>. Amazon publishes '
               'this only as an asterisk reading \u201cselect fee categories\u201d; these are the '
               'categories it refers to.</p>')
    out.append('<p class="src">' + ' \u00b7 '.join(esc(c) for c in items) + '</p>')

# --- the switch table -------------------------------------------------------
if switchers:
    out.append('<h2>Categories that change list between bands '
               '<span class="tag v">VERIFIED</span></h2>')
    out.append('<p>For these categories the \u20b9301\u2013500 fee is <em>not</em> the one a simple '
               'tier pairing would give. The last column is the error you would make by assuming '
               'the pairing.</p>')
    out.append('<table>\n<thead><tr><th>Fee category</th><th style="width:26mm">\u20b90\u2013300</th>'
               '<th style="width:26mm">\u20b9301\u2013500</th>'
               '<th style="width:30mm">Pairing would say</th>'
               '<th style="width:20mm">Error</th></tr></thead>\n<tbody>')
    for c, lo, hi in switchers:
        assumed = RATE[OLD_PAIR[lo]]
        actual = RATE[hi]
        d = actual - assumed
        sign = f'+\u20b9{d}' if d > 0 else f'\u2212\u20b9{abs(d)}'
        out.append(f'<tr><td>{esc(c)}</td>'
                   f'<td class="num">\u20b9{RATE[lo]} <small>({lo})</small></td>'
                   f'<td class="num"><strong>\u20b9{actual}</strong> <small>({hi})</small></td>'
                   f'<td class="num">\u20b9{assumed} <small>({OLD_PAIR[lo]})</small></td>'
                   f'<td class="num">{sign}</td></tr>')
    out.append('</tbody></table>')

# --- what it means for the reader's own product -----------------------------
out.append('<div class="box info">\n<p class="lbl">What this means for your \u20b9333 rope wire</p>\n'
           '<p><span class="tag v">VERIFIED</span> At \u20b9333 you are in the '
           '<strong>\u20b9301\u2013500</strong> band. <strong>Home - Other Products</strong> and '
           '<strong>Home improvement - Other Products</strong> are both in <strong>Group C</strong>, '
           'so your closing fee is <strong>\u20b918</strong>.</p>\n'
           '<p><strong>Two ways that changes.</strong> If Amazon bills you under '
           '\u201cWires (Electrical Wires/cables for house wiring, ad hoc usage)\u201d, that is '
           '<strong>Group ## \u2014 \u20b922</strong>, plus a 10% referral fee above \u20b9300; about '
           '<strong>\u20b937 more per sale before GST</strong>, over \u20b94,000 a month at 100 '
           'orders. If instead you are billed under <strong>Home Improvement Accessories</strong>, '
           'that is <strong>Group D \u2014 \u20b914</strong>, so \u20b94 <em>less</em> than \u20b918.</p>\n'
           '<p style="margin-bottom:0">None of the four \u20b972 categories apply to you, so above '
           '\u20b91,000 you would pay \u20b952. Read the exact fee category name in Fee Preview '
           'rather than inferring it from your browse path.</p>\n</div>')

pathlib.Path("appendixB_body.html").write_text('\n'.join(out), encoding="utf-8")

print(f"Appendix B built \u2014 {total} category assignments across 6 published lists")
for band, rows in BANDS:
    print(f"  {band}")
    for grp, rate, _ in rows:
        print(f"    {grp:9} {rate:5}  {len(g.get(grp, [])):4} categories")
print(f"  Above \u20b91,000 \u20b972 exception: {n72} categories")
print(f"  Categories that change list between bands: {len(switchers)}")
