# Square seven-segment digits as a BDF font: 5x9 cells, 1 px strokes, plus "-". Every glyph has advance 6
# (tabular); "1" is drawn in the middle column so it doesn't leave a hole on its left.
# --bold: 6-wide cells with 2 px vertical segments (advance 7), to sit beside the bold text font.
# --height=8: 8 rows (middle bar on row 3), as tall as the text font's capitals.
# Usage: python3 tools/seg7bdf.py [--bold] [--height=8] fonts/seg7-5x9.bdf
import sys

BOLD = "--bold" in sys.argv
DST = [a for a in sys.argv[1:] if not a.startswith("--")][0]
H = next((int(a.split("=")[1]) for a in sys.argv if a.startswith("--height=")), 9)
W, MID = (6 if BOLD else 5), (H - 1) // 2
SW = 2 if BOLD else 1  # vertical stroke width
SEG = {
    "a": [(x, 0) for x in range(W)],
    "b": [(x, y) for y in range(MID + 1) for x in range(W - SW, W)],
    "c": [(x, y) for y in range(MID, H) for x in range(W - SW, W)],
    "d": [(x, H - 1) for x in range(W)],
    "e": [(x, y) for y in range(MID, H) for x in range(SW)],
    "f": [(x, y) for y in range(MID + 1) for x in range(SW)],
    "g": [(x, MID) for x in range(W)],
}
DIGITS = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd", "6": "afgedc",
          "7": "abc", "8": "abcdefg", "9": "abcdfg", "-": "g"}

out = ["STARTFONT 2.1", "FONT -Local-Seg7-Medium-R-Normal--9-90-75-75-P-60-ISO10646-1", f"SIZE {H} 75 75",
       f"FONTBOUNDINGBOX {W} {H} 0 0", "STARTPROPERTIES 3", f"FONT_ASCENT {H}", "FONT_DESCENT 0",
       'SPACING "P"', "ENDPROPERTIES", f"CHARS {len(DIGITS)}"]
for ch, segs in DIGITS.items():
    px = {p for s in segs for p in SEG[s]}
    w = W
    if ch == "1":
        px = {(x, y) for (_, y) in px for x in range((W - SW) // 2, (W - SW) // 2 + SW)}
    out += [f"STARTCHAR {ch}", f"ENCODING {ord(ch)}", f"SWIDTH {(w + 1) * 1000 // H} 0", f"DWIDTH {w + 1} 0",
            f"BBX {w} {H} 0 0", "BITMAP"]
    for y in range(H):
        v = sum(1 << (7 - x) for x in range(w) if (x, y) in px)
        out.append(f"{v:02X}")
    out.append("ENDCHAR")
out.append("ENDFONT")
open(DST, "w").write("\n".join(out) + "\n")
