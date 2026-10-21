import struct,sys
d=open(sys.argv[1],'rb').read(); n=d[1]; o=24
OUT={0,2,4,5,12,13,14,15,16,17,18,19,21,22,23,25,26,27,32,33}
for i in range(n):
    a,l=struct.unpack('<II',d[o:o+8]); b=d[o+8:o+8+l]; o+=8+l
    if a>=0x40000000: continue
    for w,fmt in ((1,'B'),(4,'<I'),(2,'<H')):
        j=0
        while j+w*10<=len(b):
            k=j; vals=[]
            while k+w<=len(b):
                v=struct.unpack_from(fmt,b,k)[0]
                if v in OUT: vals.append(v); k+=w
                else: break
            if len(vals)>=10 and len(set(vals))>=8:
                print(f'{hex(a+j)} w{w} {vals}'); j=k
            else: j+=w
