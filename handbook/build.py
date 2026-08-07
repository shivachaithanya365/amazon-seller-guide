#!/usr/bin/env python3
"""Assemble handbook parts into one HTML file and render to PDF.

WeasyPrint is imported lazily so that the HTML assembly step still works when it
is not installed - previously a missing WeasyPrint made the whole script fail at
import time, before writing any output. Install it with: pip install weasyprint
"""
import pathlib, re, sys

HERE = pathlib.Path(__file__).parent
PARTS = [f"part{i}.html" for i in range(1, 9)]
OUT_HTML = HERE / "handbook_full.html"
OUT_PDF = HERE / "Amazon_India_Seller_Handbook_2026.pdf"

chunks = []
for i, name in enumerate(PARTS):
    p = HERE / name
    if not p.exists():
        sys.exit(f"MISSING: {name}")
    txt = p.read_text(encoding="utf-8")
    if i == 0:
        # keep head, strip the closing tags so we can append
        txt = re.sub(r"</body>\s*</html>\s*$", "", txt.strip())
    chunks.append(txt)

full = "\n".join(chunks)

# sanity: exactly one <html> and one </html>
assert full.count("<html") == 1, f"html tag count = {full.count('<html')}"
assert full.count("</html>") == 1, f"/html count = {full.count('</html>')}"

OUT_HTML.write_text(full, encoding="utf-8")
print(f"HTML assembled: {OUT_HTML.name}  ({len(full):,} chars)")

try:
    from weasyprint import HTML
except ImportError:
    sys.exit(f"{OUT_HTML.name} written, but PDF skipped: WeasyPrint is not installed.\n"
             f"Install it with 'pip install weasyprint', then re-run to refresh "
             f"{OUT_PDF.name}.")

HTML(filename=str(OUT_HTML)).write_pdf(str(OUT_PDF))
print(f"PDF written:    {OUT_PDF.name}  ({OUT_PDF.stat().st_size:,} bytes)")
