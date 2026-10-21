# Make a proportional BDF from a monospace one: each glyph's advance becomes its ink width + 1,
# the space becomes 2 px wide (--space=N). Digits keep their monospace cell so numbers don't shift as they change.
# Printable ASCII and ° are kept; --vi adds the Vietnamese letters, --bold doubles every stroke sideways.
# Usage: python3 tools/propbdf.py [--vi] [--bold] SRC.bdf DST.bdf   (e.g. X11 misc-fixed, public domain)
#   tools/propbdf.py 5x8.bdf fonts/5x8-prop.bdf
#   tools/propbdf.py --vi --bold --space=4 fonts/lvn-stock.bdf fonts/lvn-stock-bold.bdf
import re
import sys

args = [a for a in sys.argv[1:] if not a.startswith("--")]
src, dst = args
bold = "--bold" in sys.argv
space = next((int(a.split("=")[1]) for a in sys.argv if a.startswith("--space=")), 2)
keep = set(range(32, 127)) | {0xB0}
if "--vi" in sys.argv:
    keep |= set(range(0xC0, 0x1B1)) | set(range(0x1EA0, 0x1EFA))
lines = open(src, encoding="latin-1").read().split("\n")
header, glyphs, i = [], [], 0
while not lines[i].startswith("STARTCHAR"):
    if not lines[i].startswith("CHARS "):
        header.append(lines[i])
    i += 1
while i < len(lines) and lines[i].startswith("STARTCHAR"):
    g = {"name": lines[i]}
    i += 1
    while not lines[i].startswith("BITMAP"):
        k, _, v = lines[i].partition(" ")
        g[k] = v
        i += 1
    i += 1
    rows = []
    while lines[i] != "ENDCHAR":
        rows.append(int(lines[i], 16))
        i += 1
    i += 1
    g["rows"] = rows
    if int(g["ENCODING"]) in keep:
        glyphs.append(g)

# Charcell spacing would make renderers use a fixed advance
out = [re.sub(r"-C-(\d+)-", "-P-\\1-", l).replace('SPACING "C"', 'SPACING "P"') for l in header]
out.append(f"CHARS {len(glyphs)}")
for g in glyphs:
    w, h, xo, yo = map(int, g["BBX"].split())
    nbytes = (w + 7) // 8
    bits = [[(r >> (nbytes * 8 - 1 - c)) & 1 for c in range(w)] for r in g["rows"]]
    if bold:
        bits = [[row[c] if c < w else 0 for c in range(w + 1)] for row in bits]
        bits = [[row[c] | (row[c - 1] if c else 0) for c in range(w + 1)] for row in bits]
        w += 1
    cols = [c for c in range(w) if any(row[c] for row in bits)]
    if 0x30 <= int(g["ENCODING"]) <= 0x39:
        nw, adv = w, w
    elif not cols:  # space
        bits, nw, adv = [[0] for _ in bits], 1, space
    else:
        c0, c1 = cols[0], cols[-1]
        bits = [row[c0:c1 + 1] for row in bits]
        nw, adv = c1 - c0 + 1, c1 - c0 + 2
    out += [g["name"], f"ENCODING {g['ENCODING']}", f"SWIDTH {adv * 1000 // 8} 0", f"DWIDTH {adv} 0",
            f"BBX {nw} {h} 0 {yo}", "BITMAP"]
    for row in bits:
        v = 0
        for b in row:
            v = (v << 1) | b
        nb = (nw + 7) // 8
        out.append(f"{v << (nb * 8 - nw):0{nb * 2}X}")
    out.append("ENDCHAR")
out.append("ENDFONT")
open(dst, "w", encoding="latin-1").write("\n".join(out) + "\n")
