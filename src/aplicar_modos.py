"""Inserta en web/index.html el sistema de hora del día (día / atardecer / noche). Se ejecuta una sola vez."""
p = 'web/index.html'
s = open(p, encoding='utf-8').read()
if 'elegirModo' in s: raise SystemExit('ya aplicado')

def R(a, b):
    global s
    if a not in s: raise SystemExit('falta: ' + a[:70])
    s = s.replace(a, b, 1)

block = r'''// ---------- hora del día: la escena se tiñe según el reloj del navegador ----------
function elegirModo() {
  const q = new URLSearchParams(location.search).get('modo');
  if (q === 'dia' || q === 'atardecer' || q === 'noche') return q;
  const d = new Date(), h = d.getHours() + d.getMinutes() / 60;
  if (h >= 7.5 && h < 17.5) return 'dia';
  if ((h >= 17.5 && h < 20) || (h >= 6 && h < 7.5)) return 'atardecer';
  return 'noche';
}
const MODO = elegirModo();
const TEMAS = {
  dia: null,
  atardecer: {
    cielo: [[0, [46, 56, 134]], [.38, [96, 78, 168]], [.66, [214, 112, 118]], [.88, [250, 160, 104]], [1, [255, 204, 128]]],
    suelo: {mul: [1, .72, .56], add: [26, 4, -10]}, calido: [46, 20, -8],
    nube: {mul: [1, .66, .56], add: [44, 8, -16], alpha: 1}, tren: {mul: [1, .82, .7], add: [10, 0, -6]},
    humo: {mul: [1, .78, .66], add: [24, 4, -8]}, vineta: .62, brillo: 1.35
  },
  noche: {
    cielo: [[0, [3, 5, 18]], [.45, [9, 15, 44]], [.8, [20, 33, 78]], [1, [38, 54, 112]]],
    suelo: {mul: [.2, .27, .46], add: [3, 6, 20]}, calido: [0, 0, 0],
    nube: {mul: [.3, .35, .56], add: [4, 7, 16], alpha: .88}, tren: {mul: [.34, .38, .56], add: [2, 4, 12]},
    humo: {mul: [.4, .45, .62], add: [4, 6, 14]}, vineta: .8, brillo: 2.3
  }
};
const TEMA = TEMAS[MODO];
function tinte(origen, fn) {                                                  // copia el recurso en un lienzo y le aplica fn(datos, i, x, y)
  const c = document.createElement('canvas'); c.width = origen.width; c.height = origen.height;
  const g = c.getContext('2d', {willReadFrequently: true}); g.drawImage(origen, 0, 0);
  const im = g.getImageData(0, 0, c.width, c.height), d = im.data, w = c.width;
  for (let i = 0; i < d.length; i += 4) fn(d, i, (i >> 2) % w, ((i >> 2) / w) | 0);
  g.putImageData(im, 0, 0); return c;
}
const cl = v => v < 0 ? 0 : v > 255 ? 255 : v;
function degradado(stops, t) {
  let i = 0; while (i < stops.length - 2 && t > stops[i + 1][0]) i++;
  const a = stops[i], b = stops[i + 1], k = clamp((t - a[0]) / (b[0] - a[0]));
  return [0, 1, 2].map(c => lerp(a[1][c], b[1][c], k));
}
let estrellas = [];
function aplicarModo() {
  if (!TEMA) return;
  document.body.dataset.modo = MODO;
  const T = TEMA, suelo = (d, i, extra) => {
    for (let c = 0; c < 3; c++) d[i + c] = cl(d[i + c] * T.suelo.mul[c] + T.suelo.add[c] + (extra ? extra[c] : 0));
  };
  // cielo: las filas de cielo despejado se repintan con un degradado; el resto (cordillera, mar, ladera) se tiñe
  const FILAS = Math.round(cielo.height * 232 / 512), media = new Array(FILAS).fill(0).map(() => [0, 0, 0]);
  const tmp = document.createElement('canvas'); tmp.width = cielo.width; tmp.height = cielo.height;
  const tg = tmp.getContext('2d', {willReadFrequently: true}); tg.drawImage(cielo, 0, 0);
  const td = tg.getImageData(0, 0, cielo.width, FILAS).data;
  for (let y = 0; y < FILAS; y++) {
    for (let x = 0; x < cielo.width; x++) for (let c = 0; c < 3; c++) media[y][c] += td[(y * cielo.width + x) * 4 + c];
    for (let c = 0; c < 3; c++) media[y][c] /= cielo.width;
  }
  const solX = cielo.width * .77, solY = FILAS * 1.0, solR = cielo.width * .042;
  const cielo2 = tinte(cielo, (d, i, x, y) => {
    if (y < FILAS) {
      const g = degradado(T.cielo, y / FILAS);
      for (let c = 0; c < 3; c++) d[i + c] = cl(g[c] + (d[i + c] - media[y][c]) * .8);
      if (MODO === 'atardecer') {                                              // sol bajo, medio oculto por la cordillera
        const dd = Math.hypot(x - solX, y - solY);
        if (dd < solR) { d[i] = 255; d[i + 1] = 236; d[i + 2] = 170; }
        else if (dd < solR * 3.2) {
          const a = Math.max(0, 1 - (dd - solR) / (solR * 2.2)) * .55;
          d[i] = cl(d[i] + (255 - d[i]) * a); d[i + 1] = cl(d[i + 1] + (200 - d[i + 1]) * a); d[i + 2] = cl(d[i + 2] + (120 - d[i + 2]) * a);
        }
      }
    } else suelo(d, i, MODO === 'atardecer' ? T.calido.map(v => v * Math.max(0, 1 - (y - FILAS) / (cielo.height * .12))) : null);
  });
  if (MODO === 'noche') {                                                      // luna y estrellas
    const g = cielo2.getContext('2d'), u = cielo.width / 1024, r = 34 * u, mx = 790 * u, my = 150 * u;
    estrellas = [];
    let rnd = 7; const r01 = () => (rnd = (rnd * 16807) % 2147483647) / 2147483647;
    for (let k = 0; k < 150; k++) {
      const e = [r01() * cielo.width, r01() * FILAS * .86, r01() < .2 ? 2 : 1];
      if (Math.hypot(e[0] - mx, e[1] - my) > r * 1.8) estrellas.push(e);
    }
    g.fillStyle = 'rgba(180,200,255,.10)'; for (const k of [3, 2.2, 1.6]) { g.beginPath(); g.arc(mx, my, r * k, 0, 7); g.fill(); }
    g.fillStyle = '#eef0dc'; g.beginPath(); g.arc(mx, my, r, 0, 7); g.fill();
    g.fillStyle = '#c9ccb4';
    for (const [dx, dy, rr] of [[-.3, -.2, .22], [.25, .15, .28], [-.1, .45, .14], [.35, -.35, .12]]) { g.beginPath(); g.arc(mx + dx * r, my + dy * r, rr * r, 0, 7); g.fill(); }
    g.fillStyle = '#fff'; for (const e of estrellas) g.fillRect(Math.round(e[0]), Math.round(e[1]), e[2] * u * 2, e[2] * u * 2);
  }
  cielo = cielo2;
  nubes = tinte(nubes, (d, i) => { for (let c = 0; c < 3; c++) d[i + c] = cl(d[i + c] * T.nube.mul[c] + T.nube.add[c]); d[i + 3] *= T.nube.alpha; });
  primer = tinte(primer, (d, i) => suelo(d, i, null));
  tren = tinte(tren, (d, i) => {
    if (d[i] > 205 && d[i + 1] > 140 && d[i + 2] < 200 && d[i] - d[i + 2] > 40) return;            // el faro conserva su luz
    for (let c = 0; c < 3; c++) d[i + c] = cl(d[i + c] * T.tren.mul[c] + T.tren.add[c]);
  });
  humo = tinte(humo, (d, i) => { for (let c = 0; c < 3; c++) d[i + c] = cl(d[i + c] * T.humo.mul[c] + T.humo.add[c]); });
}

'''
R("Promise.all([img('cielo.png')", block + "Promise.all([img('cielo.png')")
R("cielo = a; nubes = n; primer = pp; tren = b; humo = c; idleLoop();", "cielo = a; nubes = n; primer = pp; tren = b; humo = c; aplicarModo(); idleLoop();")
R("  ctx.drawImage(primer, 0, 0, WW, WH);                                   // copas",
  "  if (estrellas.length) {                                                // parpadeo de algunas estrellas\n"
  "    const u = WW / cielo.width; ctx.fillStyle = '#fff'; ctx.globalAlpha = .8;\n"
  "    estrellas.forEach((e, k) => { if ((Math.floor(ms / 700) + k) % 7 === 0) ctx.fillRect(e[0] * u - .4, e[1] * u - .4, e[2] * u * 2.4, e[2] * u * 2.4); });\n"
  "    ctx.globalAlpha = 1;\n  }\n"
  "  ctx.drawImage(primer, 0, 0, WW, WH);                                   // copas")
R("const k = smooth(.15, 1, u); if (k <= 0 || tr.hid) return;",
  "const k = Math.min(1.6, smooth(.15, 1, u) * (TEMA ? TEMA.brillo : 1)); if (k <= 0 || tr.hid) return;")
R("  ctx.globalCompositeOperation = 'lighter';\n  [[1.7, .10]",
  "  ctx.globalCompositeOperation = 'lighter';\n"
  "  if (MODO === 'noche') {                                                // el faro alumbra la vía\n"
  "    const gy = tr.y + 6 * tr.s, g2 = ctx.createRadialGradient(tr.x, gy, 4, tr.x, gy, 85 * tr.s);\n"
  "    g2.addColorStop(0, 'rgba(255,225,150,.30)'); g2.addColorStop(1, 'rgba(255,225,150,0)');\n"
  "    ctx.fillStyle = g2; ctx.beginPath(); ctx.arc(tr.x, gy, 85 * tr.s, 0, 7); ctx.fill();\n  }\n"
  "  [[1.7, .10]")
R("g.addColorStop(1, 'rgba(0,0,0,.55)');", "g.addColorStop(1, `rgba(0,0,0,${TEMA ? TEMA.vineta : .55})`);")
R("#bio .wrap{",
  "body[data-modo=atardecer] #bio{background:linear-gradient(rgba(44,16,44,.9),rgba(40,14,34,.95)),url(bg.png) center/cover fixed}\n"
  "body[data-modo=noche] #bio{background:linear-gradient(rgba(3,5,18,.94),rgba(3,5,16,.97)),url(bg.png) center/cover fixed}\n"
  "#bio .wrap{")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
