# Prompt: animaciones minimalistas y estética propia

Copia todo lo que sigue en una sesión nueva de Claude Code abierta sobre este repositorio. Skills recomendadas: `taste-frontend` (criterio de diseño), `librerias-animacion-web` (con qué animar) y `html-concept-animations` si se quiere una animación conceptual aparte.

---

## Contexto

`index.html` es una página estática sin dependencias ni build (GitHub Pages). Una cinemática en canvas de 3 segundos muestra un tren de frente; luego la pantalla se quiebra y aparece `#bio`: título `ontoterrorista`, una frase de intereses filosóficos, una navegación de categorías (Blogs, FAQ, Animaciones), las tres secciones con esos nombres y una cuadrícula de repositorios de GitHub.

Lo que ya existe y debe respetarse:

- Paleta en variables CSS: `--night #0d1430`, `--panel #16224a`, `--panel2 #1d2d5e`, `--sky #6fa6e8`, `--cream #f3e9d2`, `--orange #e8743b`, `--leaf #8fb85a`, `--ink`, `--mute`.
- Tipografías: `Press Start 2P` (títulos y etiquetas) y `Pixelify Sans` (cuerpo).
- Forma: esquinas rectas (radio 0), bordes de 2px o 4px, sombras duras desplazadas (`4px 4px 0`), nunca difuminadas.
- Pulsar un botón se siente como hundirlo: `transform: translate(3px,3px)` y la sombra se acorta.
- La cinemática ya respeta `prefers-reduced-motion` (no se reproduce).

## Lectura de diseño (declárala antes de escribir código)

Lo leo así: página personal de filosofía para lectores curiosos, con lenguaje pixel art nocturno y minimalista, tirando hacia CSS nativo y JavaScript sin dependencias.

Diales: `VARIACION_DISENO 5`, `INTENSIDAD_MOTION 4`, `DENSIDAD_VISUAL 3`. El movimiento debe acompañar la lectura, no competir con ella.

## Estética propia: "pixel ferroviario nocturno"

Idea central: todo en la página se mueve **a saltos de píxel**, como un tren que avanza por durmientes, y no con curvas suaves.

1. **Movimiento en pasos.** Usa `steps(n)` o `cubic-bezier` casi lineal en cada transición. Nada de rebotes elásticos ni easing blando; el único movimiento suave permitido es el desplazamiento lento de las nubes que ya existe.
2. **Un solo acento.** Naranja `--orange` para todo lo que se mueve o se activa. El verde `--leaf` queda solo para enlaces externos. No introducir colores nuevos.
3. **Vocabulario ferroviario.** Los separadores de sección pueden ser una vía de tren hecha con `repeating-linear-gradient` (durmientes de 4px cada 12px), no una línea lisa. El estado activo de una categoría es una "señal" que cambia de oscuro a `--orange`.
4. **Glifos de texto, no iconos dibujados.** Usa `▌ ▶ ■ ▪` y caracteres del propio tipo de letra. Prohibido dibujar SVG a mano, emojis y raya larga (`—`) o semirraya (`–`) en cualquier texto visible.
5. **Cero tics de plantilla.** Nada de degradados morados, glassmorphism, tarjetas con sombras difuminadas, ni micro textos decorativos sobre los títulos.

## Animaciones a implementar (todas minimalistas, solo `transform` y `opacity`)

1. **Entrada de `#bio` tras el quiebre.** Los bloques (`kicker`, `h1`, `lead`, categorías, secciones) aparecen uno tras otro con `animation-delay` de 80ms, desplazándose 8px hacia arriba en 3 pasos (`steps(3)`) mientras sube la opacidad. Duración total menor a 700ms.
2. **Título.** La sombra naranja de `h1` se "enciende" en dos pasos al terminar la entrada (primero `4px 4px`, luego `8px 8px`). Sin bucle.
3. **Tarjetas de categorías y de repositorios.** En `:hover` y `:focus-visible` se desplazan 2px hacia la izquierda y el borde pasa a `--orange`, en un solo paso. En `:active` conservan el hundimiento actual.
4. **Revelado al bajar.** Cada `section` aparece una vez con `IntersectionObserver` (nunca `window.addEventListener('scroll')`): sube 8px y se hace visible en 3 pasos. Se desuscribe después de revelarse.
5. **FAQ.** Al abrir un `<details>`, el contenido aparece con un fundido corto en pasos. Sin animar `height`.
6. **Separador de vía.** Una vía de tren fina entre secciones cuyo patrón de durmientes se desplaza 12px en bucle muy lento (6s, `linear`, solo en la sección Animaciones y solo mientras es visible).
7. **Botón "Ver llegar el tren".** Parpadeo del texto en dos pasos mientras tiene el foco (reutilizar `@keyframes blink` que ya existe). Al pulsar, reproduce la cinemática de nuevo.
8. **Cursor.** No añadir cursores personalizados ni seguimiento del puntero.

## Cómo implementarlas

- Primera opción: CSS puro con `@keyframes` y `animation-delay`; JavaScript solo para `IntersectionObserver`. No añadas librerías; si alguna animación lo exigiera, justifícalo con `librerias-animacion-web` antes de instalar nada (GSAP solo para una línea de tiempo larga y encadenada, que aquí no hay).
- Define duraciones y pasos como variables CSS (`--paso: 80ms`, `--entrada: 600ms`) para poder ajustar el ritmo en un solo lugar.
- Todo debe estar envuelto en `@media (prefers-reduced-motion: no-preference)`. Con movimiento reducido, el contenido es visible desde el primer momento y sin transiciones.
- No uses `will-change` salvo en el elemento que se anima en ese momento.
- No toques el código de la cinemática de canvas (`trainAt`, `scene`, `frame`) salvo que se pida.
- El texto de los botones debe caber en una línea en escritorio. Contraste mínimo WCAG AA en cada estado.

## Criterios de terminado

- [ ] La página sigue funcionando sin red (excepto las fuentes) y sin dependencias nuevas.
- [ ] Ninguna animación dura más de 700ms, salvo la vía del punto 6.
- [ ] Con `prefers-reduced-motion: reduce` no hay ningún movimiento.
- [ ] No se anima `width`, `height`, `top` ni `left`.
- [ ] En móvil (390px de ancho) no hay scroll horizontal y los hover no dejan estados pegados.
- [ ] Cero rayas largas en el texto visible.
- [ ] Verificado en el navegador (captura en escritorio y en móvil) antes de dar la tarea por terminada.
- [ ] Un commit con mensaje claro y el cambio descrito en `README.md`.
