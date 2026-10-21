import struct,sys
d=open(sys.argv[1],'rb').read(); n=d[1]; o=24; segs=[]
for i in range(n):
    a,l=struct.unpack('<II',d[o:o+8]); segs.append((a,d[o+8:o+8+l])); o+=8+l
entry=struct.unpack('<I',d[4:8])[0]
# ELF32 LE, EM_XTENSA=94
ph=[];data=b'';off=52+32*len(segs)
for a,b in segs:
    flags=5 if a>=0x40000000 else 6
    ph.append(struct.pack('<IIIIIIII',1,off+len(data),a,a,len(b),len(b),flags,4)); data+=b
hdr=b'\x7fELF\x01\x01\x01'+b'\0'*9+struct.pack('<HHIIIIIHHHHHH',2,94,1,entry,52,0,0,52,32,len(segs),40,0,0)
open(sys.argv[2],'wb').write(hdr+b''.join(ph)+data)
for a,b in segs: print(hex(a),hex(len(b)))
