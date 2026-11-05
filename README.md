# tupala-redes

Generador del **reel diario de ofertas** de TuPala para Instagram, Facebook y TikTok.

- `diario.sh`: lo ejecuta la tarea programada cada mañana. Deja `out/reel.mp4` y `out/hoy.json`.
- `ofertas.py`: lee las «Ofertas destacadas» de la portada de tupala.es y descarga la foto de cada pala.
- `recorte.py`: quita el fondo blanco de la foto de la tienda (garganta, correa y puños blancos incluidos).
- `render.py`: monta el vídeo 1080×1920 en plano continuo y escribe los textos de cada red.
- `pagina/index.html`: la página «Reel del día» (artifact de claude.ai) que lee `hoy.json` y `reel.mp4`.
- `assets/`: logo, pala TuPala en 3D y grano.

Diseño: zonas seguras de TikTok (las más restrictivas), así que el mismo vídeo vale para las tres redes.
Las cifras se copian tal cual de la web: no se recalcula ni se redondea nada.
Requisitos: Python 3 con Playwright (Chromium), Pillow, NumPy, SciPy, y ffmpeg.
