# Render a 64x32 layout with the fonts ESPHome downloaded, to check pixel positions before flashing.
# Usage (after one compile, so .esphome/font exists):
#   <python with freetype-py> -I tools/sim.py tools/layout.py
import freetype, sys, os
F=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','.esphome','font')+'/'
class Font:
    def __init__(s, f, size):
        s.face=freetype.Face(F+f); s.face.set_pixel_sizes(size,0)
    def glyph(s,ch):
        s.face.load_char(ch, freetype.FT_LOAD_RENDER|freetype.FT_LOAD_TARGET_MONO)
        g=s.face.glyph; b=g.bitmap; rows=[]
        for r in range(b.rows):
            row=[]
            for c in range(b.width):
                byte=b.buffer[r*b.pitch+c//8]; row.append((byte>>(7-c%8))&1)
            rows.append(row)
        return g.bitmap_left, g.bitmap_top, g.advance.x>>6, rows
    def width(s,t): return sum(s.glyph(c)[2] for c in t)
    def ink(s,t):  # (top above baseline, bottom below baseline, ink x0, ink x1)
        x=0; top=-99; bot=99; x0=99; x1=-99
        for c in t:
            l,tp,adv,rows=s.glyph(c)
            if rows and any(map(any,rows)):
                top=max(top,tp); bot=min(bot,tp-len(rows)); x0=min(x0,x+l); x1=max(x1,x+l+len(rows[0])-1)
            x+=adv
        return top,bot,x0,x1
W,H=64,32
scr=[[' ']*W for _ in range(H)]
def draw(font,x,y_base,t,ch,align='L'):
    if align=='R': x-=font.width(t)
    if align=='C': x-=font.width(t)//2
    for c in t:
        l,tp,adv,rows=font.glyph(c)
        for r,row in enumerate(rows):
            for cc,v in enumerate(row):
                X,Y=x+l+cc,y_base-tp+r
                if v and 0<=X<W and 0<=Y<H: scr[Y][X]=ch
        x+=adv
exec(open(sys.argv[1]).read())
print('   '+''.join(str(i%10) for i in range(W)))
for i,r in enumerate(scr): print(f'{i:2d} '+''.join(r))
