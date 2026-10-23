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
def local_sky(valid):
    # cielo despejado: por fila, una recta color(x) ajustada a los píxeles válidos; luego suavizada entre filas
    coef = np.full((575, 3, 2), np.nan)
    xs = np.arange(W)
    for y in range(575):
        m = valid[y]
        if m.sum() >= 40:
            for c in range(3): coef[y, c] = np.polyfit(xs[m], a[y, m, c], 1)[::-1]
    rows = np.arange(575)
    for c in range(3):
        for k in range(2):
            col = coef[:, c, k]; ok = ~np.isnan(col)
            col = np.interp(rows, rows[ok], col[ok])
            coef[:, c, k] = np.convolve(np.pad(col, 12, mode="edge"), np.ones(25) / 25, mode="valid")
    out = np.zeros((H, W, 3))
    for y in range(575): out[y] = coef[y, :, 0][None, :] + coef[y, :, 1][None, :] * xs[:, None]
    return np.clip(out, 0, 255)
skymap = local_sky((a[:, :, 0] < 140) & (a[:, :, 2] > a[:, :, 1] + 10) & (a[:, :, 1] > 115) & (a[:, :, 2] > 170))
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
cm = Image.fromarray((cloud * 255).astype('uint8')).filter(ImageFilter.MaxFilter(7))
cloud = np.array(cm) > 0
prot = np.zeros((H, W), bool); prot[:575, :330] = (a[:575, :330].sum(2) < 400)          # los pinos de la ladera no se tocan
cloud &= ~prot
# quita restos sueltos (trozos de nube de menos de 220 px)
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
        if len(comp) < 220:
            for y, x in comp: cloud[y, x] = False; clean[y, x] = skymap[y, x]
clean[350:400, 536:600] = skymap[350:400, 536:600]; cloud[350:400, 536:600] = False   # resto suelto del penacho
sky = clean.copy()
for y in range(0, 560):
    sky[y][cloud[y]] = skymap[y][cloud[y]]
layer = np.zeros((H, W, 4), np.uint8)
layer[:, :, :3] = clean; layer[:, :, 3] = cloud * 255
# la nube pasa por detrás de los pinos: rellena el hueco con forma de árbol que dejan en la capa de nubes
closed = np.array(Image.fromarray((cloud * 255).astype('uint8')).filter(ImageFilter.MaxFilter(31)).filter(ImageFilter.MinFilter(31))) > 0
protd = np.array(Image.fromarray((prot * 255).astype('uint8')).filter(ImageFilter.MaxFilter(15))) > 0
fill = protd & closed & ~cloud
def boxsum(m, r):
    c = np.pad(m, ((r + 1, r), (r + 1, r))).cumsum(0).cumsum(1)
    return c[2 * r + 1:, 2 * r + 1:] - c[:-2 * r - 1, 2 * r + 1:] - c[2 * r + 1:, :-2 * r - 1] + c[:-2 * r - 1, :-2 * r - 1]
cw = boxsum(cloud.astype(float), 14)
for c in range(3):
    mean = boxsum(clean[:, :, c] * cloud, 14) / np.maximum(cw, 1)
    layer[:, :, c] = np.where(fill, mean, layer[:, :, c])
layer[:, :, 3] = (cloud | fill) * 255
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
def save(arr, name, mode, half=False):
    im = Image.fromarray(arr.astype('uint8'), mode)
    if half: im = im.resize((W // 2, H // 2), Image.BOX)
    im.save(f"{out_dir}{name}")
save(sky, "cielo.png", "RGB"); save(clean, "bg.png", "RGB", half=True)             # cielo a resolución completa; bg (fondo de la bio) a la mitad
save(layer, "nubes.png", "RGBA")
# primer plano: las copas de los pinos de la ladera izquierda van por delante de las nubes
fg = np.zeros((H, W, 4), np.uint8)
dark = (a.sum(2) < 400)
fgm = np.zeros((H, W), bool); fgm[:575, :330] = dark[:575, :330]
fgm[575:] = False
fg[:, :, :3] = a; fg[:, :, 3] = fgm * 255
save(fg, "primer-plano.png", "RGBA")
# locomotora a resolución completa, sin el azul del cielo en el borde
box = (550, 540, 700, 762)
rgb = np.array(ref.crop(box)).astype(int); pm = np.array(mask.crop(box)) > 0
h, w = pm.shape
bluish = lambda p: ((p[2] - p[0] > 30) and (p[2] >= p[1] - 6)) or min(p) > 172      # cielo azul o nube blanca
alpha = pm.copy(); stack = []
for y in range(h):
    for x in range(w):
        if pm[y, x] and (x in (0, w - 1) or y in (0, h - 1) or not (pm[y - 1, x] and pm[y + 1, x] and pm[y, x - 1] and pm[y, x + 1])) and bluish(rgb[y, x]):
            alpha[y, x] = False; stack.append((y, x))
while stack:                                                                       # el cielo que toca el exterior, a través de píxeles azulados
    y, x = stack.pop()
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        yy, xx = y + dy, x + dx
        if 0 <= yy < h and 0 <= xx < w and alpha[yy, xx] and bluish(rgb[yy, xx]): alpha[yy, xx] = False; stack.append((yy, xx))
for _ in range(2):                                                                 # franja de mezcla borde/cielo: un píxel más hacia adentro mientras sea azulada
    nxt = alpha.copy()
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            if alpha[y, x] and not (alpha[y - 1, x] and alpha[y + 1, x] and alpha[y, x - 1] and alpha[y, x + 1]) and rgb[y, x][2] - rgb[y, x][0] > 12:
                nxt[y, x] = False
    alpha = nxt
# silueta limpia: simétrica (la locomotora lo es), sin motas, con borde de un píxel oscuro
ys_, xs_ = np.where(alpha); cxm = (xs_.min() + xs_.max()) / 2
mir = np.zeros_like(alpha)
for x in range(w):
    xm = int(round(2 * cxm - x))
    if 0 <= xm < w: mir[:, x] = alpha[:, xm]
alpha = alpha & mir
def morph(m, f): return np.array(Image.fromarray((m * 255).astype('uint8')).filter(f)) > 127
alpha = morph(morph(alpha, ImageFilter.MinFilter(3)), ImageFilter.MaxFilter(3))               # abre: quita motas
alpha = morph(morph(alpha, ImageFilter.MaxFilter(3)), ImageFilter.MinFilter(3))               # cierra: rellena mellas
inner = morph(alpha, ImageFilter.MinFilter(3))
ring = alpha & ~inner
rgb2 = rgb.astype(float); rgb2[ring] = rgb2[ring] * .45 + np.array([18, 22, 40]) * .55         # contorno oscuro de pixel art
rgb = rgb2.astype(int)
spr = np.zeros((h, w, 4), np.uint8); spr[:, :, :3] = rgb; spr[:, :, 3] = alpha * 255
Image.fromarray(spr).save(f"{out_dir}tren.png")
import shutil                                                                      # la locomotora definitiva se regeneró con PixelLab (img2img sobre el recorte anterior)
if os.path.exists(f"{here}/tren_pixellab.png"): shutil.copy(f"{here}/tren_pixellab.png", f"{out_dir}tren.png")
print("tren", (w, h), "ancla (centro-base, unidades de mundo) =", ((624 - 550) / 2, (757 - 540) / 2))
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
