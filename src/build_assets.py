"""Genera el arte de ontoterrorista a partir de la referencia (src/ref2.webp, 1254x1254).
web/cielo.png (cielo sin nubes ni tren), web/nubes.png (capa de nubes con alfa), web/bg.png (escena fija sin tren, para la bio),
web/tren.png (locomotora con alfa) y los cuadros del humo (src/humo/*.png) que Pixelorama convierte en hoja."""
import numpy as np, random, os
from PIL import Image, ImageDraw, ImageFilter
random.seed(7); np.random.seed(7)
here = os.path.dirname(os.path.abspath(__file__)); out_dir = f"{here}/../web/" if os.path.isdir(f"{here}/../web") else f"{here}/../"
ref = Image.open(f"{here}/ref2.webp").convert("RGB"); W, H = ref.size
a = np.array(ref).astype(int)
br = a[:, :, 2] - a[:, :, 0]                                   # azul - rojo: el cielo despejado es muy azul
# cielo despejado: media local (ventana horizontal) de los píxeles muy azules de cada fila
def local_sky(valid, win=140):
    out = np.zeros((H, W, 3))
    for y in range(0, 575):
        v = valid[y].astype(float); cs = np.concatenate([[0], np.cumsum(v)])
        lo = np.clip(np.arange(W) - win, 0, W); hi = np.clip(np.arange(W) + win + 1, 0, W)
        n = cs[hi] - cs[lo]
        for c in range(3):
            cc = np.concatenate([[0], np.cumsum(a[y, :, c] * v)])
            out[y, :, c] = np.where(n > 0, (cc[hi] - cc[lo]) / np.maximum(n, 1), np.nan)
        for c in range(3):                                     # huecos sin vecinos: arrastra el último valor
            col = out[y, :, c]; idx = np.where(~np.isnan(col))[0]
            out[y, :, c] = np.interp(np.arange(W), idx, col[idx]) if len(idx) else 100
    return out
skymap = local_sky((a[:, :, 0] < 140) & (a[:, :, 2] > a[:, :, 1] + 10))
# 1) humo original de la locomotora: todo lo que se aleje del cielo local dentro de la caja del penacho
clean = a.copy()
for y in range(300, 575):
    for x in range(560, 776 if y < 549 else 700):
        if np.abs(a[y, x] - skymap[y, x]).sum() > 16: clean[y, x] = skymap[y, x]
# 2) nubes (solo sobre cielo, por encima de la cordillera)
cloud = np.zeros((H, W), bool)
for y in range(0, 560):
    cloud[y] = a[y, :, 0] >= 140
cloud[300:549, 560:776] = False
cm = Image.fromarray((cloud * 255).astype('uint8')).filter(ImageFilter.MaxFilter(3))
cloud = np.array(cm) > 0
# quita restos sueltos (trozos de nube de menos de 60 px)
seen = np.zeros((H, W), bool)
for y0 in range(H):
    for x0 in np.where(cloud[y0] & ~seen[y0])[0]:
        if seen[y0, x0]: continue
        comp, st = [], [(y0, x0)]; seen[y0, x0] = True
        while st:
            y, x = st.pop(); comp.append((y, x))
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < H and 0 <= xx < W and cloud[yy, xx] and not seen[yy, xx]: seen[yy, xx] = True; st.append((yy, xx))
        if len(comp) < 60:
            for y, x in comp: cloud[y, x] = False; clean[y, x] = skymap[y, x]
clean[360:392, 566:596] = skymap[360:392, 566:596]; cloud[360:392, 566:596] = False   # resto suelto del penacho
sky = clean.copy()
for y in range(0, 560):
    sky[y][cloud[y]] = skymap[y][cloud[y]]
layer = np.zeros((H, W, 4), np.uint8)
layer[:, :, :3] = clean; layer[:, :, 3] = cloud * 255
# 3) locomotora: polígono en coords de la referencia
poly = [(603,543),(644,543),(644,560),(639,560),(639,600),(662,602),(682,612),(692,620),(692,742),(684,750),(674,757),
        (580,757),(566,750),(557,742),(557,620),(566,612),(578,604),(606,600),(606,560),(603,560)]
mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).polygon(poly, fill=255)
md = np.array(mask.filter(ImageFilter.MaxFilter(13))) > 0
def patch(base):                                              # rellena la locomotora uniendo, fila a fila, el fondo de sus dos lados
    b = base.copy(); xl, xr = 546, 704
    for y in range(536, 768):
        for x in range(xl, xr + 1):
            if md[y, x]:
                t = (x - xl) / (xr - xl); b[y, x] = (1 - t) * base[y, xl] + t * base[y, xr]
    return b
sky = patch(sky); clean = patch(clean)
def save(arr, name, mode):
    im = Image.fromarray(arr.astype('uint8'), mode)
    im.resize((W // 2, H // 2), Image.BOX).save(f"{out_dir}{name}")
save(sky, "cielo.png", "RGB"); save(clean, "bg.png", "RGB")
layer = np.array(Image.fromarray(layer).resize((W // 2, H // 2), Image.NEAREST))
Image.fromarray(layer).save(f"{out_dir}nubes.png")
box = (550, 540, 700, 762)
spr = ref.crop(box).convert("RGBA"); spr.putalpha(mask.crop(box).filter(ImageFilter.MinFilter(3)))
spr = spr.resize((spr.width // 2, spr.height // 2), Image.BOX); spr.save(f"{out_dir}tren.png")
print("tren", spr.size, "ancla (centro-base) =", ((624 - 550) / 2, (757 - 540) / 2), "chimenea", ((624-550)/2, (546-540)/2), "faro", ((623-550)/2, (597-540)/2))
# humo: 8 cuadros de 32x32 (celdas de 2 px como los bloques de la referencia), paleta tomada del penacho original
pal = {"luz": (236, 222, 208), "base": (214, 200, 196), "medio": (186, 184, 200), "sombra": (150, 160, 192), "hondo": (122, 134, 176)}
os.makedirs(f"{here}/humo", exist_ok=True)
G = 16                                                          # rejilla de celdas
rng = random.Random(23)
blobs = []
for k in range(9):                                              # cúmulo: bolas repartidas en un disco, las de arriba más chicas
    ang = rng.uniform(0, 6.283); rad = rng.uniform(0, 3.4)
    blobs.append((np.cos(ang) * rad, np.sin(ang) * rad * .8 - .4, rng.uniform(.55, .95)))
blobs.append((0, 0, 1.0))
drop = np.random.RandomState(5).rand(G, G)
def sample(x, y, r0, lift):                                     # (campo, bola dominante)
    best, bi = -9, 0
    for i, (bx, by, bs) in enumerate(blobs):
        d = np.hypot(x - (G / 2 + bx * (.5 + .55 * r0 / 6)), y - (G / 2 + by * (.5 + .55 * r0 / 6) - lift)) / (r0 * bs * .62)
        if 1 - d > best: best, bi = 1 - d, i
    return best, bi
for f in range(8):
    t = f / 7; r0 = 3.8 + 5.2 * t ** .75; lift = 3.0 * t; thr = .05
    img = np.zeros((32, 32, 4), np.uint8)
    for cy in range(G):
        for cx in range(G):
            v, bi = sample(cx, cy, r0, lift)
            if v <= thr: continue
            if t > .55 and drop[cy, cx] < (t - .55) * 1.7 and v < .45: continue      # se deshace en bloques
            bx, by, bs = blobs[bi]
            ox_, oy_ = cx - (G / 2 + bx * (.5 + .55 * r0 / 6)), cy - (G / 2 + by * (.5 + .55 * r0 / 6) - lift)
            n = np.hypot(ox_, oy_) or 1
            L = -(ox_ + oy_) / (n * 1.414) * (1 - .55 * v)                                   # luz desde arriba a la izquierda
            L -= .18 * (cy - G / 2) / (G / 2)                                                # la base del cúmulo, más a la sombra
            c = "luz" if L > .42 else "base" if L > .08 else "medio" if L > -.28 else "sombra" if L > -.6 else "hondo"
            if t > .6 and c == "luz": c = "base"
            img[cy * 2:cy * 2 + 2, cx * 2:cx * 2 + 2] = (*pal[c], 255)
    Image.fromarray(img).save(f"{here}/humo/h{f}.png")
