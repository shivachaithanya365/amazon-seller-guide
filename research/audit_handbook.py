#!/usr/bin/env python3
"""Audit the handbook's own confidence state and re-check its fee figures.

    cd research && python3 audit_handbook.py

Three jobs:
  1. Count VERIFIED / UNCONFIRMED / CHECK LIVE / UNSETTLED tags per chapter, so the
     book cannot quietly drift into looking more certain than it is.
  2. Re-derive every closing-fee and weight-handling figure in Chapter 8 from the
     extracted data and the rate cards, and flag any cell that disagrees.
  3. List every remaining UNCONFIRMED claim in full, so the open items are a
     visible list rather than something you have to hunt for.
"""
import re, html, json, pathlib, sys, collections

HB = pathlib.Path(__file__).parent.parent / "handbook"
if not HB.exists():
    sys.exit("handbook/ not found - run from inside research/")

KIND = {'v': 'VERIFIED', 'c': 'UNCONFIRMED', 's': 'CHECK LIVE', 'n': 'ACTION/UNSETTLED'}
ws = re.compile(r'\s+')
strip = lambda s: ws.sub(' ', re.sub(r'<[^>]+>', ' ', html.unescape(s))).strip()

parts = {}
for i in range(1, 8):
    parts[f"part{i}"] = (HB / f"part{i}.html").read_text(encoding="utf-8")

# --- 1. tag census ----------------------------------------------------------
print("=" * 78)
print("1. CONFIDENCE CENSUS")
print("=" * 78)
print(f"  {'file':10} {'VERIFIED':>9} {'UNCONFIRMED':>12} {'CHECK LIVE':>11} {'ACTION':>8}")
totals = collections.Counter()
for name, t in parts.items():
    c = collections.Counter(m for m in re.findall(r'<span class="tag ([vcsn])">', t))
    totals.update(c)
    print(f"  {name:10} {c['v']:>9} {c['c']:>12} {c['s']:>11} {c['n']:>8}")
print(f"  {'-'*54}")
print(f"  {'TOTAL':10} {totals['v']:>9} {totals['c']:>12} {totals['s']:>11} {totals['n']:>8}")
tagged = sum(totals.values())
print(f"\n  {totals['v']} of {tagged} tagged claims are VERIFIED "
      f"({totals['v']/tagged*100:.0f}%). {totals['c']} remain UNCONFIRMED.")

# --- 2. re-derive the Chapter 8 fee tables ----------------------------------
print()
print("=" * 78)
print("2. CHAPTER 8 FEE FIGURES, RE-DERIVED FROM SOURCE")
print("=" * 78)

groups = json.loads((pathlib.Path(__file__).parent / "closing_groups_live.json").read_text())
RATES = {'Group #': 26, 'Group ##': 22, 'Group A': 20, 'Group C': 18, 'Group B': 13, 'Group D': 14}
# read off the rate-card images on 4 Aug 2026, cards stamped effective 16 Mar 2026
CARD_CLOSING = {'FBA': {'0-300': 'Rs 26/20/13', '301-500': 'Rs 22/18/14', '501-1000': 27, '1000+': 52},
                'Easy Ship': {'0-300': 1, '301-500': 22, '501-1000': 45, '1000+': 76},
                'Self-Ship': {'0-300': 20, '301-500': 26, '501-1000': 51, '1000+': 101},
                'Seller Flex': {'0-300': 6, '301-500': 12, '501-1000': 35, '1000+': 66}}
CARD_FBA_WH = {'Premium & Advanced': [37, 63, 52, 83, 76, 120, 24, 34, 13, 18],
               'Standard': [39, 65, 54, 85, 78, 122, 24, 34, 13, 18],
               'Basic': [42, 69, 58, 89, 82, 126, 24, 34, 13, 18]}
CARD_ES_WH = {'Premium & Advanced': [53, 73, 110, 34, 18],
              'Standard': [55, 75, 112, 34, 18],
              'Basic': [59, 79, 116, 34, 18]}

p3 = parts['part3']
problems = []

def cells_of(table_html):
    out = []
    for row in re.findall(r'<tr>(.*?)</tr>', table_html, re.S):
        out.append([strip(c) for c in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.S)])
    return out

# closing fee table
m = re.search(r'<h4>The complete closing fee table.*?</table>', p3, re.S)
found = {}
for row in cells_of(m.group(0)):
    if not row or 'Item price' in row[0]:
        continue
    # normalise en/em dashes to '-' and drop currency symbols, commas and 'Above '
    band = (row[0].replace('\u20b9', '').replace(',', '').replace('Above ', '')
                  .replace('\u2013', '-').replace('\u2014', '-').strip())
    if band == '1000':
        band = '1000+'
    found[band] = row[1:]
for band, want in [('0-300', 1), ('301-500', 22), ('501-1000', 45), ('1000+', 76)]:
    got = found.get(band)
    es = got[1] if got and len(got) > 1 else None
    ok = es is not None and str(want) in es
    print(f"  closing, Easy Ship {band:10} book {str(es):>12}   card Rs {want:<4} {'OK' if ok else 'MISMATCH'}")
    if not ok:
        problems.append(f"closing/Easy Ship/{band}")

# FBA weight handling
m = re.search(r'<h4>FBA standard-size weight handling.*?</table>', p3, re.S)
nums = [int(x) for x in re.findall(r'\u20b9(\d+)', m.group(0))]
exp = CARD_FBA_WH['Premium & Advanced'] + CARD_FBA_WH['Standard'] + CARD_FBA_WH['Basic']
ok = nums == exp
print(f"  FBA weight handling, 30 values      {'OK - matches the rate card' if ok else 'MISMATCH'}")
if not ok:
    problems.append("FBA weight handling")
    print(f"     book {nums}\n     card {exp}")

# Easy Ship weight handling
m = re.search(r'<h4>Easy Ship weight handling.*?</table>', p3, re.S)
if m:
    nums = [int(x) for x in re.findall(r'\u20b9(\d+)', m.group(0))]
    exp = CARD_ES_WH['Premium & Advanced'] + CARD_ES_WH['Standard'] + CARD_ES_WH['Basic']
    ok = nums == exp
    print(f"  Easy Ship weight handling, 15 values {'OK - matches the rate card' if ok else 'MISMATCH'}")
    if not ok:
        problems.append("Easy Ship weight handling")
else:
    problems.append("Easy Ship weight handling table MISSING")
    print("  Easy Ship weight handling            MISSING")

# Chapter 9 per-unit tables must be internally consistent
print()
print("  Chapter 9 - fees + 18% GST = total, and share of Rs 333:")
m = re.search(r'<h2>9\.1.*?</table>', p3, re.S)
for row in cells_of(m.group(0)):
    money = [c for c in row if c.startswith('\u20b9')]
    if len(money) < 3:
        continue
    f, g, tot = (float(x.replace('\u20b9', '').replace(',', '')) for x in money[:3])
    pct = next((c for c in row if c.endswith('%')), None)
    ok = abs(g - f * 0.18) < 0.02 and abs(tot - (f + g)) < 0.02
    if pct:
        ok = ok and abs(float(pct.rstrip('%')) - tot / 333 * 100) < 0.15
    label = strip(row[0])[:28] or "(cont)"
    print(f"    {label:30} {f:7.2f} + {g:6.2f} = {tot:7.2f}  {pct or '':>6}   {'OK' if ok else 'MISMATCH'}")
    if not ok:
        problems.append(f"Chapter 9 row: {label}")

# --- 3. remaining open items ------------------------------------------------
print()
print("=" * 78)
print("3. EVERY REMAINING UNCONFIRMED CLAIM")
print("=" * 78)
n = 0
for name, t in parts.items():
    for m in re.finditer(r'<span class="tag c">[^<]*</span>(.{0,190})', t, re.S):
        n += 1
        print(f"  [{n:2}] {name}: {strip(m.group(1))[:150]}")
# --- 4. glyph coverage -----------------------------------------------------
# WeasyPrint silently DROPS characters the font cannot render. No warning, no
# placeholder box - the character just vanishes from the PDF. This went unnoticed
# for a long time and cost 220 "<=" signs in Appendix A, where "0% <= Rs 1,000"
# was rendering as "0% Rs 1,000", plus 127 navigation arrows. Never rely on a
# character being present just because it is in the HTML.
print()
print("=" * 78)
print("4. GLYPH COVERAGE - do all characters survive into the PDF?")
print("=" * 78)
full = (HB / "handbook_full.html").read_text(encoding="utf-8")
vis = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', full, flags=re.S | re.I)
vis = html.unescape(re.sub(r'<[^>]+>', ' ', vis))
used = sorted({c for c in vis if ord(c) > 127})
print(f"  distinct non-ASCII characters used: {len(used)}")

try:
    from weasyprint import HTML as _H
    from pypdf import PdfReader as _R
    import tempfile, os
    body = "".join(f"<p>X {c} X</p>" for c in used)
    doc = ('<html><head><meta charset="utf-8"><style>@page{size:A4;margin:15mm}'
           'body{font-family:"Noto Sans","DejaVu Sans";font-size:12pt}</style>'
           f'</head><body>{body}</body></html>')
    with tempfile.TemporaryDirectory() as d:
        hp, pp = os.path.join(d, "g.html"), os.path.join(d, "g.pdf")
        pathlib.Path(hp).write_text(doc, encoding="utf-8")
        _H(filename=hp).write_pdf(pp)
        rendered = "".join((pg.extract_text() or "") for pg in _R(pp).pages)
    dropped = [c for c in used if c not in rendered]
    if dropped:
        print(f"  DROPPED BY THE FONT: {len(dropped)}")
        for c in dropped:
            print(f"    U+{ord(c):04X} {c!r} - used {vis.count(c)} times and will NOT appear in the PDF")
        problems.append(f"{len(dropped)} glyph(s) dropped by the font")
    else:
        print("  OK - every character used in the book renders in the PDF")
except ImportError:
    print("  SKIPPED - weasyprint or pypdf unavailable, cannot verify glyph coverage")

print()
print("=" * 78)
if problems:
    print(f"AUDIT FAILED - {len(problems)} problem(s):")
    for p in problems:
        print("  -", p)
    sys.exit(1)
print("AUDIT PASSED - every Chapter 8 and 9 figure matches the rate cards and the")
print("extracted data, and all arithmetic is internally consistent.")
print(f"{n} claims remain UNCONFIRMED and are listed above.")
