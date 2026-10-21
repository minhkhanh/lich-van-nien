#!/usr/bin/python3
"""Extract the LongSmart Lich Van Nien stock clock-digit fonts from app1.elf (stdlib only).

FUN_400d536c(theme, hfont) picks the font pointers; FUN_400d5714 draws themes 0/3 (16-row fonts),
FUN_400d5b38 draws themes 1/2 (22-row fonts). All bitmaps are row-major, LSB = leftmost pixel.
"""
import struct, sys, os
ELF = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'analysis', 'app1.elf')
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.abspath(__file__))
D = open(ELF, 'rb').read()
phoff = struct.unpack_from('<I', D, 28)[0]; phnum = struct.unpack_from('<H', D, 44)[0]
SEG = [struct.unpack_from('<8I', D, phoff + 32 * i)[1:5:] for i in range(phnum)]
SEG = [(va, off, fs) for off, va, pa, fs in SEG]
def rd(a, n):
    for va, off, fs in SEG:
        if va <= a < va + fs: return D[off + a - va: off + a - va + n]
    raise ValueError(hex(a))
u32 = lambda a: struct.unpack('<I', rd(a, 4))[0]
L = lambda lit: u32(lit)   # literal-pool slot -> font address

def rows8(addr, n, w):            # 1 byte per row
    return [[(b >> x) & 1 for x in range(w)] for b in rd(addr, n)]
def rows16(addr, n, w):           # 2 bytes per row, little-endian
    d = rd(addr, 2 * n)
    return [[((d[2*r] | d[2*r+1] << 8) >> x) & 1 for x in range(w)] for r in range(n)]

def trim(rows):
    """Return (rows, top) with empty top/bottom rows removed (keeps at least 1 row)."""
    nz = [i for i, r in enumerate(rows) if any(r)]
    if not nz: return [rows[0]], 0
    return rows[nz[0]:nz[-1] + 1], nz[0]

def glyph16(f, i):   return rows8(f + 18 * i, 16, 8)
def colon22(f, s):   return rows8(f + 0x3f0 + 24 * s, 22, 3)
def glyph22(f, i):   return rows16(f + 48 * i, 21, 13)
def small(f, i):     return rows8(f + 10 * i, 8, 5)
def tiny(f, i):      return rows8(f + 8 * i, 6, 5)

def write_bdf(path, name, height, glyphs):
    """glyphs: list of (codepoint, rows (top..), top_row, xoff, advance). Baseline = bottom of cell."""
    W = max(len(r[0]) for _, r, *_ in glyphs)
    with open(path, 'w') as f:
        f.write('STARTFONT 2.1\nFONT -LongSmart-%s-Medium-R-Normal--%d-%d-75-75-C-%d-ISO10646-1\n' % (name, height, height * 10, W * 10))
        f.write('SIZE %d 75 75\nFONTBOUNDINGBOX %d %d 0 0\n' % (height, W, height))
        f.write('STARTPROPERTIES 2\nFONT_ASCENT %d\nFONT_DESCENT 0\nENDPROPERTIES\nCHARS %d\n' % (height, len(glyphs)))
        for cp, rows, top, xoff, adv in glyphs:
            rows, t2 = trim(rows); top += t2
            w = len(rows[0]); nb = (w + 7) // 8
            f.write('STARTCHAR uni%04X\nENCODING %d\nSWIDTH %d 0\nDWIDTH %d 0\nBBX %d %d %d %d\nBITMAP\n'
                    % (cp, cp, adv * 1000 // height, adv, w, len(rows), xoff, height - top - len(rows)))
            for r in rows:
                v = sum(b << (nb * 8 - 1 - x) for x, b in enumerate(r))
                f.write('%0*X\n' % (nb * 2, v))
            f.write('ENDCHAR\n')
        f.write('ENDFONT\n')

def art(rows):
    return ['' .join('#' if b else '.' for b in r) for r in rows]
dump = []
def add_dump(title, gl):
    dump.append(title)
    cols = [art(r) for r in gl]
    for y in range(max(len(c) for c in cols)):
        dump.append('  '.join(c[y] if y < len(c) else ' ' * len(c[0]) for c in cols))
    dump.append('')

PUA = 0xE000   # colon animation frames: U+E000.. (frame 0 is also ':')
# ---- themes 0/3 ("Giao dien 1/4"): 16-row big digits + 5x8 seconds / AM-PM font -------------
H16 = {1: (0x400d0310, 0x400d0314), 2: (0x400d0318, 0x400d031c),
       3: (0x400d0320, 0x400d0324), 4: (0x400d0328, 0x400d0314)}
for hf, (lb, ls) in H16.items():
    f, s = L(lb), L(ls)
    gl = [(0x30 + d, glyph16(f, d), 0, 0, 10) for d in range(10)]
    gl.append((0x3A, [r[:2] for r in glyph16(f, 22)], 0, 0, 4))
    gl.append((0x2E, [r[:2] for r in glyph16(f, 21)], 0, 0, 4))
    gl += [(PUA + k, [r[:2] for r in glyph16(f, 22 + k)], 0, 0, 4) for k in range(3)]
    write_bdf(os.path.join(OUT, 'lvn_hour%d.bdf' % hf), 'LVNHour%d' % hf, 16, gl)
    sg = [(0x30 + d, small(s, d), 0, 0, 6) for d in range(10)]
    sg += [(ord(c), small(s, i), 0, 0, 6) for c, i in (('A', 24), ('P', 25), ('M', 26), ('.', 22), (':', 23))]
    write_bdf(os.path.join(OUT, 'lvn_hour%d_small.bdf' % hf), 'LVNHour%dSmall' % hf, 8, sg)
    add_dump('=== hour font %d (themes 0/3), 16-row @0x%08x: 0-9 : .   (adv 10, colon/dot adv 4)' % (hf, f),
             [glyph16(f, d) for d in range(10)] + [[r[:2] for r in glyph16(f, 22)], [r[:2] for r in glyph16(f, 21)]])
    add_dump('    small seconds/AM-PM font @0x%08x: 0-9 A P M' % s, [small(s, d) for d in list(range(10)) + [24, 25, 26]])
# ---- themes 1/2 ("Giao dien 2/3"): 22-row big digits (13 wide), 3x3 colon -----------------------
H22 = {('', 1): (0x400d032c, 30), ('', 2): (0x400d0330, 30), ('', 3): (0x400d0334, 30), ('', 4): (0x400d0338, 29),
       ('_12h', 1): (0x400d033c, 30), ('_12h', 4): (0x400d0340, 30)}
for (sfx, hf), (lb, cx) in H22.items():
    f = L(lb)
    gl = [(0x30 + d, glyph22(f, d), 0, 0, 15) for d in range(10)]
    # pen after hours is at x+30 (2 digits x 15); colon drawn at x+cx, minutes start at x+36
    gl.append((0x3A, colon22(f, 0), 0, cx - 30, 6))
    gl += [(PUA + k, colon22(f, k), 0, cx - 30, 6) for k in range(4)]
    write_bdf(os.path.join(OUT, 'lvn_big%d%s.bdf' % (hf, sfx)), 'LVNBig%d%s' % (hf, sfx.upper().strip('_')), 22, gl)
    add_dump('=== big font %d%s (theme %s), 22-row @0x%08x: 0-9 :   (adv 15, colon at +%d)'
             % (hf, sfx, '2' if sfx else '1', f, cx), [glyph22(f, d) for d in range(10)] + [colon22(f, 0)])
# ---- tiny 5x6 font (theme 3 date row, struct +0x30) --------------------------------------------
t = L(0x400d0344)
write_bdf(os.path.join(OUT, 'lvn_tiny.bdf'), 'LVNTiny', 6,
          [(0x30 + d, tiny(t, d), 0, 0, 6) for d in range(10)] + [(0x2D, tiny(t, 10), 0, 0, 6), (0x2E, tiny(t, 11), 0, 0, 6)])
open(os.path.join(OUT, 'hourfonts_preview.txt'), 'w').write('\n'.join(dump) + '\n')
print('ok')
