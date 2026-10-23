"""Genera el arte de ontoterrorista a partir de la referencia.
bg.png (sin tren, 768x512), tren.png (recorte con alfa a resolucion de la referencia, mitad) y
los cuadros del humo (src/humo/*.png) que Pixelorama convierte en hoja."""
import numpy as np, random, os
from PIL import Image, ImageDraw, ImageFilter
random.seed(7); np.random.seed(7)
here = os.path.dirname(os.path.abspath(__file__))
ref = Image.open(f"{here}/ref.webp").convert("RGB")           # 1536x1024
W, H = ref.size
# polígono del tren en coords de la referencia (crop offset 200,300; zoom 3)
poly3 = [(160,200),(250,166),(350,168),(430,193),(560,256),(700,308),(820,338),(820,386),(770,414),
         (600,442),(452,466),(432,505),(300,524),(190,508),(158,440)]
poly = [(200+x/3, 300+y/3) for x,y in poly3]
mask = Image.new("L", (W,H), 0); ImageDraw.Draw(mask).polygon(poly, fill=255)
mask_d = mask.filter(ImageFilter.MaxFilter(9))                 # dilatado para el parche
# fondo sin tren: foliage espejado
bg = ref.copy(); px = bg.load(); src = ref.load(); md = mask_d.load()
x0,x1,y0,y1 = 240,500,335,490
for y in range(y0,y1):
    for x in range(x0,x1):
        if md[x,y]:
            k = (x-x0)%160; sx = 520+k if ((x-x0)//160)%2==0 else 679-k
            sy = 370 + (y-y0)%100
            px[x,y] = src[sx,sy]
bg.resize((768,512), Image.BOX).save(f"{here}/../bg.png")
# sprite del tren (mitad de resolución → 1 px = 2 px de la referencia)
box = (240,335,490,490)
spr = ref.crop(box).convert("RGBA"); m = mask.crop(box)
spr.putalpha(m.filter(ImageFilter.MinFilter(7)))
spr = spr.resize((spr.width//2, spr.height//2), Image.BOX)
spr.save(f"{here}/../tren.png")
print("tren", spr.size, "ancla frente-centro aprox", ((300-240)/2, (472-335)/2))
# humo: 8 cuadros de 32x32
pal = [(0x2f,0x36,0x55),(0x5b,0x63,0x84),(0x9a,0xa1,0xbd),(0xd7,0xda,0xe6),(0xf6,0xf1,0xe6)]
os.makedirs(f"{here}/humo", exist_ok=True)
blobs = [(random.uniform(-5,5),random.uniform(-5,5),random.uniform(.5,1)) for _ in range(9)]
bayer = np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]])/16.0
for f in range(8):
    t = f/7; r0 = 5+9*t**.7; img = np.zeros((32,32,4),np.uint8)
    yy,xx = np.mgrid[0:32,0:32]
    dens = np.zeros((32,32))
    for bx,by,bs in blobs:
        cx,cy = 16+bx*(.5+t), 16+by*(.5+t)-6*t
        d = np.hypot(xx-cx,yy-cy)/(r0*bs*.8)
        dens = np.maximum(dens, 1-d)
    alpha = max(0,1-t**1.6*1.05)
    for y in range(32):
        for x in range(32):
            d = dens[y,x]
            if d <= 0: continue
            lvl = d*(.35+.65*t) + (bayer[y%4,x%4]-.5)*.35    # más claro al envejecer
            lvl = min(max(lvl,0),.999)
            c = pal[int(lvl*len(pal))]
            if bayer[(y+2)%4,(x+1)%4] > alpha*1.25 and d < .45: continue   # borde roto al desvanecer
            img[y,x] = (*c, 255)
    Image.fromarray(img).save(f"{here}/humo/h{f}.png")
