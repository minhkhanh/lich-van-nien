T=Font('Roboto Condensed@700@False@v1.ttf',22); s=Font('Silkscreen@400@False@v1.ttf',8)
tw=T.width('09:02'); sw=s.width('17'); x0=(64-(tw+1+sw))//2
draw(T,x0,16,'09:02','#'); draw(s,x0+tw+1,16,'17','s')
draw(s,1,23,'T3 20/10','d'); draw(s,64,23,'28°','t','R')
draw(s,32,31,'Binh Ngo','l','C')
print(x0,tw,sw)
