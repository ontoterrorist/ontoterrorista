# ontoterrorista

Página experimental en pixel art: una locomotora de vapor asoma por la cresta y avanza de frente con humo y nubes que derivan, la pantalla se quiebra y aparece una mini descripción de mis intereses filosóficos.

- `index.html`: cinemática en canvas (sin dependencias), sonido procedural con WebAudio.
- `src/build_assets.py`: saca el fondo, el tren y los cuadros del humo de la imagen de referencia (`src/ref2.webp`).
- `src/humo.pxo`: proyecto de Pixelorama con los 8 cuadros del humo; la hoja `humo.png` se exportó con la CLI de Pixelorama.
- Animaciones de la bio ("pixel ferroviario nocturno"): CSS con `steps()` y variables `--paso`/`--entrada`, más `IntersectionObserver` para el revelado al bajar, la categoría activa y las nubes que derivan. Todo queda desactivado con `prefers-reduced-motion`. El plan está en `PROMPT-animaciones.md`.
- Diseño de la bio (taste-skill, dirección "tipografía y nada más"): la primera pantalla son dos campos que se juntan a media altura y el nombre se parte en la costura (onto / terrorista). Sigue una página de texto con una franja de imagen, blogs, FAQ como texto de lectura, animaciones en campo naranja, repositorios en filas y un cierre con el nombre a todo el ancho. Mantiene la paleta y las dos tipografías; sin sombras, degradados ni líneas finas. El análisis con `inspect.mjs` da 0 errores en 1440, 768 y 390 píxeles (se permitieron `mono` por Press Start 2P y `palette-claude` por la paleta propia).
