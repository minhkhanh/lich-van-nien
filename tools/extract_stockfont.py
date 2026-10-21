#!/usr/bin/python3
"""Extract the LongSmart Lich Van Nien stock scrolling-text font from app1.elf.

Engine (stock firmware): FUN_400e2a90 drawString(utf8, x, y, color) ->
FUN_400e27c0 (UTF-8 bytes packed big-endian, linear search in a 232-entry u32
code table) -> FUN_400e29c0 drawGlyph. Font struct {bitmaps, u16 offsets[232]}.
Glyph at bitmaps+off: header bytes at -4..-1 = width, height, stride(bytes/row),
ybias; rows MSB-first, row-major. Top row = y + (ybias-4) + max(0, bitmaps[0]-height).
Advance = width + 1.
"""
import struct, sys, os
ELF = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'analysis', 'app1.elf')
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.abspath(__file__))
D = open(ELF, 'rb').read()
phoff = struct.unpack_from('<I', D, 28)[0]; phnum = struct.unpack_from('<H', D, 44)[0]
SEG = []
for i in range(phnum):
    t, off, va, pa, fs, ms, fl, al = struct.unpack_from('<8I', D, phoff + 32 * i)
    SEG.append((va, off, fs))
def rd(a, n):
    for va, off, fs in SEG:
        if va <= a < va + fs: return D[off + a - va: off + a - va + n]
    raise ValueError(hex(a))
u32 = lambda a: struct.unpack('<I', rd(a, 4))[0]

FONT = u32(0x400d0c0c)            # literal: &font struct (DRAM 0x3ffbdc28)
BMP, OFFS = u32(FONT), u32(FONT + 4)
CODES = u32(0x400d0c10)           # literal: code table (0x3f4149a8)
N = 232
codes = [u32(CODES + 4 * i) for i in range(N)]
offs = struct.unpack('<%dH' % N, rd(OFFS, 2 * N))
maxh = rd(BMP, 1)[0]
BASE = 11                          # baseline row below the draw y (caps/x-height sit on row 10)

def cp(code):
    b = code.to_bytes(4, 'big').lstrip(b'\0') or b' '
    return ord(b.decode('utf-8'))

glyphs = {}
for i, c in enumerate(codes):
    u = cp(c)
    if u in glyphs: continue       # index 0 and 32 are both space
    g = BMP + offs[i]
    w, h, s, yb = rd(g - 4, 4)
    top = (yb - 4) + max(0, maxh - h)
    rows = []
    for r in range(h):
        row = rd(g + s * r, s)
        rows.append([(row[x >> 3] >> (7 - (x & 7))) & 1 for x in range(w)])
    glyphs[u] = dict(idx=i, w=w, h=h, top=top, rows=rows)

asc = max(BASE - g['top'] for u, g in glyphs.items() if u != 0x5C)  # '\\' has a bogus ybias (top=-3) in the stock data
desc = max(g['top'] + g['h'] - BASE for g in glyphs.values())
with open(os.path.join(OUT, 'lvn_stock_text.bdf'), 'w') as f:
    f.write('STARTFONT 2.1\nFONT -LongSmart-LVNText-Medium-R-Normal--%d-%d-75-75-P-60-ISO10646-1\n' % (asc + desc, (asc + desc) * 10))
    f.write('SIZE %d 75 75\nFONTBOUNDINGBOX %d %d 0 %d\n' % (asc + desc, max(g['w'] for g in glyphs.values()), asc + desc, -desc))
    f.write('STARTPROPERTIES 3\nFONT_ASCENT %d\nFONT_DESCENT %d\nDEFAULT_CHAR 32\nENDPROPERTIES\n' % (asc, desc))
    f.write('CHARS %d\n' % len(glyphs))
    for u in sorted(glyphs):
        g = glyphs[u]
        f.write('STARTCHAR uni%04X\nENCODING %d\nSWIDTH %d 0\nDWIDTH %d 0\n' % (u, u, (g['w'] + 1) * 1000 // (asc + desc), g['w'] + 1))
        f.write('BBX %d %d 0 %d\nBITMAP\n' % (g['w'], g['h'], BASE - g['top'] - g['h']))
        nb = (g['w'] + 7) // 8
        for r in g['rows']:
            v = 0
            for x, bit in enumerate(r): v |= bit << (nb * 8 - 1 - x)
            f.write('%0*X\n' % (nb * 2, v))
        f.write('ENDCHAR\n')
    f.write('ENDFONT\n')

sample = 'AaHhgy\\ÀàẢẠĂẮẶÂẦĐđÉỆềÍịÔỒỘƠỚỢƯỪỰÝỹỵ°❤‘'
with open(os.path.join(OUT, 'glyphs_preview.txt'), 'w') as f:
    f.write('maxh=%d ascent=%d descent=%d; baseline marked with ^ (row %d); advance = width+1\n\n' % (maxh, asc, desc, BASE))
    for ch in sample:
        g = glyphs[ord(ch)]
        f.write("U+%04X '%s' idx=%d w=%d h=%d top=%d\n" % (ord(ch), ch, g['idx'], g['w'], g['h'], g['top']))
        for y in range(BASE - asc, BASE + desc):
            r = y - g['top']
            line = ''.join('#' if b else '.' for b in g['rows'][r]) if 0 <= r < g['h'] else '.' * g['w']
            f.write('%s%s\n' % (line, ' ^' if y == BASE - 1 else ''))
        f.write('\n')
print('glyphs', len(glyphs), 'asc', asc, 'desc', desc, 'widths', sorted(set(g['w'] for g in glyphs.values())))
