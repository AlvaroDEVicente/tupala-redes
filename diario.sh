#!/usr/bin/env bash
# Genera las historias del día: lee las ofertas de la portada de tupala.es, recorta las palas, renderiza
# una historia por pantalla (portada, una por oferta, cierre) y la versión completa, y deja en out/ lo que
# publica la página «Historias del día» (historia-*.mp4 y hoy.json).
set -euo pipefail
cd "$(dirname "$0")"
rm -rf work out && mkdir -p work out
python3 ofertas.py work
python3 render.py work out
python3 hoy_json.py work out/hoy.json
python3 render.py work out stills >/dev/null   # fotogramas de control en work/still*.png
for f in out/historia-*.mp4; do printf '%s %ss\n' "$(basename "$f")" "$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")"; done
