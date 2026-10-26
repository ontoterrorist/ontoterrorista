"""Capas del fondo generado con PixelLab Pro (src/fondos/pro.png, 512x512):
cielo.png (cielo limpio), nubes.png (capa de nubes con alfa), primer-plano.png (pinos, van por delante de las nubes),
bg.png (escena entera, fondo de la bio). Las capas salen a 1024 px (x2, vecino más cercano)."""
import numpy as np, os
from PIL import Image, ImageFilter
here = os.path.dirname(os.path.abspath(__file__))
out_dir = f"{here}/../web/" if os.path.isdir(f"{here}/../web") else f"{here}/../"
ref = Image.open(f"{here}/fondos/pro.png").convert("RGB"); W, H = ref.size
a = np.array(ref).astype(int)
SKY_ROWS = 232                                                  # por debajo: cordillera, bruma del horizonte y suelo (fijos)
valid = (a[:, :, 0] < 140) & (a[:, :, 2] > a[:, :, 1] + 10) & (a[:, :, 1] > 105) & (a[:, :, 2] > 165)
xs = np.arange(W)
coef = np.full((SKY_ROWS, 3, 2), np.nan)
for y in range(SKY_ROWS):
    m = valid[y]
    if m.sum() >= 25:
        for c in range(3): coef[y, c] = np.polyfit(xs[m], a[y, m, c], 1)[::-1]
rows = np.arange(SKY_ROWS)
for c in range(3):
    for k in range(2):
        col = coef[:, c, k]; ok = ~np.isnan(col)
        col = np.interp(rows, rows[ok], col[ok])
        coef[:, c, k] = np.convolve(np.pad(col, 6, mode="edge"), np.ones(13) / 13, mode="valid")
skymap = np.zeros((H, W, 3))
for y in range(SKY_ROWS): skymap[y] = coef[y, :, 0][None, :] + coef[y, :, 1][None, :] * xs[:, None]
def mf(m, n): return np.array(Image.fromarray((m * 255).astype("uint8")).filter(ImageFilter.MaxFilter(n))) > 0
def nf(m, n): return np.array(Image.fromarray((m * 255).astype("uint8")).filter(ImageFilter.MinFilter(n))) > 0
cloud = np.zeros((H, W), bool); cloud[:SKY_ROWS] = a[:SKY_ROWS, :, 0] >= 140
cloud = mf(cloud, 3); cloud[SKY_ROWS:] = False
prot = np.zeros((H, W), bool); prot[:SKY_ROWS, :135] = a[:SKY_ROWS, :135].sum(2) < 400         # pinos de la ladera
cloud &= ~prot
# restos sueltos de nube (menos de 25 px)
seen = np.zeros((H, W), bool)
for y0 in range(SKY_ROWS):
    for x0 in np.where(cloud[y0] & ~seen[y0])[0]:
        if seen[y0, x0]: continue
        comp, st = [], [(y0, x0)]; seen[y0, x0] = True
        while st:
            y, x = st.pop(); comp.append((y, x))
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < H and 0 <= xx < W and cloud[yy, xx] and not seen[yy, xx]: seen[yy, xx] = True; st.append((yy, xx))
        if len(comp) < 25:
            for y, x in comp: cloud[y, x] = False
sky = a.copy()
sky[cloud] = skymap[cloud]
layer = np.zeros((H, W, 4), np.uint8); layer[:, :, :3] = a
# la nube pasa por detrás de los pinos: se rellena el hueco que dejan, con color de nube lejos de su contorno
closed = nf(mf(cloud, 13), 13)
protd = mf(prot, 7)
fill = protd & closed & ~cloud
def boxsum(m, r):
    c = np.pad(m, ((r + 1, r), (r + 1, r))).cumsum(0).cumsum(1)
    return c[2 * r + 1:, 2 * r + 1:] - c[:-2 * r - 1, 2 * r + 1:] - c[2 * r + 1:, :-2 * r - 1] + c[:-2 * r - 1, :-2 * r - 1]
src = cloud & ~protd
done = np.zeros((H, W), bool)
for r in (6, 16, 37):
    cw = boxsum(src.astype(float), r)
    todo = protd & (cloud | fill) & (cw > 0) & ~done
    for c in range(3): layer[:, :, c] = np.where(todo, boxsum(a[:, :, c] * src, r) / np.maximum(cw, 1), layer[:, :, c])
    done |= todo
layer[:, :, 3] = (cloud | fill) * 255
fg = np.zeros((H, W, 4), np.uint8); fg[:, :, :3] = a; fg[:, :, 3] = prot * 255
up = lambda arr, mode: Image.fromarray(arr.astype("uint8"), mode).resize((W * 2, H * 2), Image.NEAREST)
up(sky, "RGB").save(f"{out_dir}cielo.png"); up(layer, "RGBA").save(f"{out_dir}nubes.png"); up(fg, "RGBA").save(f"{out_dir}primer-plano.png")
ref.save(f"{out_dir}bg.png")
print("ok", W * 2)
