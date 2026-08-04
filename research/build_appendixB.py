#!/usr/bin/env python3
"""Build Appendix B as a usable lookup table, not six blocks of prose.

Earlier versions printed each of the six closing-fee groups as a paragraph of
category names separated by middots. That is 465 assignments as running text: to
answer "what is my closing fee?" you had to scan one wall of prose for your
category, then scan a second wall for the other price band. Nobody does that.

This builds ONE alphabetical table of all 251 distinct category names with BOTH
price bands side by side, so a lookup is a single row. Rows where the 301-500
band does not follow the obvious pairing are flagged, because those are where a
seller loses money by assuming.

The six lists remain the underlying data in closing_groups_live.json; this is
purely about presentation.
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

LO = [('Group #', 26), ('Group A', 20), ('Group B', 13)]      # INR 0-300
HI = [('Group ##', 22), ('Group C', 18), ('Group D', 14)]      # INR 301-500
PAIR = {'Group #': 'Group ##', 'Group A': 'Group C', 'Group B': 'Group D'}
RATE = dict(LO + HI)

def band_of(name, groups):
    for grp, rate in groups:
        if name in g.get(grp, []):
            return grp, rate
    return None, None

names = sorted({n for grp, _ in LO + HI for n in g.get(grp, [])},
               key=lambda s: s.lower())

out = []
total = sum(len(g.get(k, [])) for k, _ in LO + HI)

out.append('<p class="lede">Below \u20b9500 your closing fee depends on which list your fee category '
           'sits in \u2014 and the two price bands have <strong>separate lists</strong>. From '
           '\u20b9501 upward the lists stop mattering: every category pays the same.</p>')

out.append('<div class="box good">\n<p class="lbl">How to use this appendix</p>\n'
           '<p><strong>Find your fee category in the table below and read across.</strong> One row '
           'gives you both price bands. You do not need to know which group you are in \u2014 that is '
           'what the table is for.</p>\n'
           f'<p style="margin-bottom:0"><span class="tag v">VERIFIED</span> All <strong>{total} '
           f'category assignments</strong> across <strong>{len(names)} distinct categories</strong> '
           'were read from Amazon\u2019s live fee page on <strong>4 August 2026</strong>, and the rates '
           'from Amazon\u2019s own closing-fee rate cards, stamped effective 16 March 2026.</p>\n</div>')

# --- summary of the rates ---------------------------------------------------
out.append('<h2>The rates</h2>')
out.append('<table>\n<thead><tr><th style="width:38mm">Price band</th>'
           '<th style="width:30mm">List</th><th style="width:24mm">Closing fee</th>'
           '<th>Categories</th></tr></thead>\n<tbody>')
for band, rows in (('\u20b90\u2013300', LO), ('\u20b9301\u2013500', HI)):
    for n, (grp, rate) in enumerate(rows):
        first = (f'<td rowspan="3"><strong>{band}</strong></td>' if n == 0 else '')
        out.append(f'<tr>{first}<td>{grp}</td><td class="num"><strong>\u20b9{rate}</strong></td>'
                   f'<td>{len(g.get(grp, []))} categories</td></tr>')
n72 = len(g.get('Above 1000 (Rs 72)', []))
out.append('<tr><td colspan="2"><strong>\u20b9501\u20131,000 \u2014 all categories</strong></td>'
           '<td class="num"><strong>\u20b927</strong></td><td>every category</td></tr>')
out.append('<tr><td colspan="2"><strong>Above \u20b91,000</strong></td>'
           '<td class="num"><strong>\u20b952</strong></td>'
           f'<td>every category except the {n72} listed at the end, which pay \u20b972</td></tr>')
out.append('</tbody></table>')

# --- the caution ------------------------------------------------------------
switchers = [(n, lo, hi) for n in names
             for lo, hi in [(band_of(n, LO)[0], band_of(n, HI)[0])]
             if lo and hi and hi != PAIR[lo]]
out.append('<div class="box warn">\n<p class="lbl">Why both columns exist</p>\n'
           '<p>It is tempting to assume the \u20b9301\u2013500 list is just the \u20b90\u2013300 list at a '
           'different price. <strong>It is not.</strong> Amazon\u2019s own example proves it: '
           '<em>Apparel - Shorts</em> is in Group A (\u20b920) below \u20b9300, but at \u20b9450 it is billed '
           'under Group D at <strong>\u20b914</strong> \u2014 not the \u20b918 a Group A \u2192 C pairing '
           'would predict.</p>\n'
           f'<p style="margin-bottom:0"><strong>{len(switchers)} categories</strong> behave this way. '
           'They are marked <strong>\u25b2</strong> in the table below, and listed with the size of the '
           'error at the end of this appendix.</p>\n</div>')

# --- THE LOOKUP TABLE -------------------------------------------------------
out.append('<h2>Closing fee by category, both price bands '
           '<span class="tag v">VERIFIED</span></h2>')
out.append('<p><small><strong>\u25b2</strong> marks a category whose \u20b9301\u2013500 fee does not follow '
           'the obvious pairing. A dash means Amazon does not list that category in that band \u2014 often '
           'because it spells the name differently there, so check the other spelling before assuming '
           'the fee does not apply.</small></p>')
out.append('<table class="tight">\n<thead><tr><th>Fee category</th>'
           '<th style="width:27mm">\u20b90\u2013300</th><th style="width:27mm">\u20b9301\u2013500</th>'
           '<th style="width:7mm"></th></tr></thead>\n<tbody>')
for name in names:
    lo_g, lo_r = band_of(name, LO)
    hi_g, hi_r = band_of(name, HI)
    lo_cell = (f'\u20b9{lo_r} <small>({lo_g.replace("Group ", "")})</small>'
               if lo_g else '<small>\u2014</small>')
    hi_cell = (f'\u20b9{hi_r} <small>({hi_g.replace("Group ", "")})</small>'
               if hi_g else '<small>\u2014</small>')
    flag = ''
    if lo_g and hi_g and hi_g != PAIR[lo_g]:
        flag = '<strong>\u25b2</strong>'
        hi_cell = f'<strong>\u20b9{hi_r}</strong> <small>({hi_g.replace("Group ", "")})</small>'
    out.append(f'<tr><td>{esc(name)}</td><td class="num">{lo_cell}</td>'
               f'<td class="num">{hi_cell}</td><td class="num">{flag}</td></tr>')
out.append('</tbody></table>')

# --- the Rs 72 list ---------------------------------------------------------
if g.get('Above 1000 (Rs 72)'):
    items = g['Above 1000 (Rs 72)']
    out.append('<h2>Above \u20b91,000 \u2014 the \u20b972 exception '
               '<span class="tag v">VERIFIED</span></h2>')
    out.append('<p>Above \u20b91,000 every category pays <strong>\u20b952</strong>, except these '
               f'<strong>{len(items)}</strong>, which pay <strong>\u20b972</strong>. Amazon publishes '
               'this only as an asterisk reading \u201cselect fee categories\u201d; these are the '
               'categories it means.</p>')
    out.append('<table>\n<thead><tr><th>Category</th><th style="width:30mm">Above \u20b91,000</th>'
               '</tr></thead>\n<tbody>')
    for c in items:
        out.append(f'<tr><td>{esc(c)}</td><td class="num"><strong>\u20b972</strong></td></tr>')
    out.append('</tbody></table>')

# --- the switch table -------------------------------------------------------
if switchers:
    out.append('<h2>The \u25b2 categories, and what assuming would cost you '
               '<span class="tag v">VERIFIED</span></h2>')
    out.append('<table class="tight">\n<thead><tr><th>Fee category</th>'
               '<th style="width:24mm">\u20b90\u2013300</th><th style="width:24mm">\u20b9301\u2013500</th>'
               '<th style="width:28mm">Pairing would say</th><th style="width:18mm">Error</th>'
               '</tr></thead>\n<tbody>')
    for name, lo_g, hi_g in sorted(switchers, key=lambda r: (r[1], r[0].lower())):
        assumed = RATE[PAIR[lo_g]]
        actual = RATE[hi_g]
        d = actual - assumed
        sign = f'+\u20b9{d}' if d > 0 else f'\u2212\u20b9{abs(d)}'
        out.append(f'<tr><td>{esc(name)}</td>'
                   f'<td class="num">\u20b9{RATE[lo_g]} <small>({lo_g.replace("Group ", "")})</small></td>'
                   f'<td class="num"><strong>\u20b9{actual}</strong> <small>({hi_g.replace("Group ", "")})</small></td>'
                   f'<td class="num">\u20b9{assumed} <small>({PAIR[lo_g].replace("Group ", "")})</small></td>'
                   f'<td class="num">{sign}</td></tr>')
    out.append('</tbody></table>')

# --- what it means for this seller -----------------------------------------
out.append('<div class="box info">\n<p class="lbl">What this means for your \u20b9333 rope wire</p>\n'
           '<p><span class="tag v">VERIFIED</span> At \u20b9333 you are in the '
           '<strong>\u20b9301\u2013500</strong> band, and your Fee Preview confirms a closing fee of '
           '<strong>\u20b918</strong> \u2014 Group C, matching <em>Home - Other Products</em> and '
           '<em>Home improvement - Other Products</em> in the table above.</p>\n'
           '<p style="margin-bottom:0">Two ways that changes. Billed as \u201cWires (Electrical\u2026)\u201d '
           'it is <strong>Group ## \u2014 \u20b922</strong> plus a 10% referral fee above \u20b9300. Billed as '
           '<strong>Home Improvement Accessories</strong> it is <strong>Group D \u2014 \u20b914</strong>, one '
           'of the \u25b2 rows. None of the four \u20b972 categories apply to you, so above \u20b91,000 you '
           'would pay \u20b952.</p>\n</div>')

pathlib.Path("appendixB_body.html").write_text('\n'.join(out), encoding="utf-8")

print(f"Appendix B built \u2014 one lookup table of {len(names)} categories, both bands")
print(f"  underlying assignments      {total}")
print(f"  in both price bands         {sum(1 for n in names if band_of(n, LO)[0] and band_of(n, HI)[0])}")
print(f"  \u20b90\u2013300 only               {sum(1 for n in names if band_of(n, LO)[0] and not band_of(n, HI)[0])}")
print(f"  \u20b9301\u2013500 only             {sum(1 for n in names if not band_of(n, LO)[0] and band_of(n, HI)[0])}")
print(f"  flagged \u25b2 (broken pairing)  {len(switchers)}")
print(f"  \u20b972 above 1,000            {n72}")
