# ontoterrorista

Página experimental en pixel art: una locomotora de vapor asoma por la cresta y avanza de frente con humo y nubes que derivan, la pantalla se quiebra y aparece una mini descripción de mis intereses filosóficos.

- `index.html`: cinemática en canvas (sin dependencias), sonido procedural con WebAudio.
- `src/build_assets.py`: saca el fondo, el tren y los cuadros del humo de la imagen de referencia (`src/ref2.webp`).
- `src/humo.pxo`: proyecto de Pixelorama con los 8 cuadros del humo; la hoja `humo.png` se exportó con la CLI de Pixelorama.
- Animaciones de la bio ("pixel ferroviario nocturno"): CSS con `steps()` y variables `--paso`/`--entrada`, más `IntersectionObserver` para el revelado al bajar, la categoría activa y la vía de tren. Todo queda desactivado con `prefers-reduced-motion`. El plan está en `PROMPT-animaciones.md`.
