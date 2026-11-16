#!/usr/bin/env bash
# Pieza diaria: lee las ofertas de la portada de tupala.es, recorta las palas, renderiza el reel (~15 s),
# la portada (out/portada.jpg), las 4 imágenes de historias (out/historias/)
# y el correo diario con vídeo, textos e historias (out/correo.html, out/correo.txt, out/correo.json).
set -euo pipefail
cd "$(dirname "$0")"
rm -rf work out && mkdir -p work out
python3 ofertas.py work
python3 render.py work out stills >/dev/null        # fotogramas de control en work/still*.png
python3 render.py work out video reel
python3 hoy_json.py work out/hoy.json
python3 correo.py work out
cat out/correo.json
