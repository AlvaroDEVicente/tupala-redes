#!/usr/bin/env bash
# Genera el reel del día: lee las ofertas de la portada de tupala.es, recorta las palas, renderiza el vídeo
# y deja en out/ los ficheros que publica la página «Reel del día» (reel.mp4 y hoy.json).
set -euo pipefail
cd "$(dirname "$0")"
rm -rf work out && mkdir -p work out
python3 ofertas.py work
python3 render.py work out/reel.mp4
python3 hoy_json.py work out/hoy.json
python3 render.py work out/reel.mp4 stills >/dev/null   # fotogramas de control en work/still*.png
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 out/reel.mp4)
echo "OK reel=${dur}s"
