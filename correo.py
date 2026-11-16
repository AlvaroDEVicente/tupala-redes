"""Genera el correo diario (out/correo.html, out/correo.txt, out/correo.json) a partir de work/ofertas.json y work/textos.json.
Lleva: el reel comprimido, su portada, los textos de Instagram y TikTok y las 4 imágenes de historias con sus enlaces.
Uso: python3 correo.py work out"""
import json, os, sys, html, datetime, subprocess
from zoneinfo import ZoneInfo
d, out = sys.argv[1], sys.argv[2]
of = json.load(open(os.path.join(d, 'ofertas.json'))); tx = json.load(open(os.path.join(d, 'textos.json')))
U = '?utm_source=instagram&utm_medium=historia&utm_campaign=ofertas-dia'
MESES = ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']
hoy = datetime.datetime.now(ZoneInfo('Europe/Madrid')).date()
fecha = f'{hoy.day} de {MESES[hoy.month-1]}'
e = html.escape
# Vídeo para el correo: el conector admite ~3 MB por envío en total, así que el vídeo va por debajo de 2,2 MB
src = os.path.join(out, 'historia-completa.mp4'); vid = os.path.join(out, f'reel-tupala-{hoy.isoformat()}.mp4')
for crf in (28, 30, 32, 34):
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-c:v', 'libx264', '-crf', str(crf), '-preset', 'slow',
                    '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-an', vid], check=True)
    if os.path.getsize(vid) < 2_200_000: break
reel_url = 'https://tupala.es/' + U + '#ofertas'
caja = 'style="white-space:pre-line;background:#F2F5F8;padding:12px;border-radius:8px"'
h = ['<div style="font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.5;color:#10243B;max-width:600px">',
     f'<p><b>Contenido de hoy, {e(fecha)}.</b> Adjuntos: el reel ({e(os.path.basename(vid))}), su portada (portada.jpg) y las 4 imágenes de historias.</p>',
     '<h3 style="margin:18px 0 6px">1 · Reel en Instagram</h3>',
     '<p>Sube el vídeo como reel, añade una canción en tendencia, pon portada.jpg como portada y activa «Compartir también en Facebook». Texto:</p>',
     f'<p {caja}>{e(tx["reel_instagram"])}</p>',
     '<h3 style="margin:18px 0 6px">2 · TikTok</h3>',
     '<p>Mismo vídeo con un sonido en tendencia y portada.jpg como portada. Texto:</p>',
     f'<p {caja}>{e(tx["tiktok"])}</p>',
     '<h3 style="margin:18px 0 6px">3 · Historias de Instagram</h3>',
     '<p><b>Historia 1 · el reel</b>: comparte el reel publicado y añade el sticker de enlace (texto <i>Ver las ofertas</i>):<br>'
     f'<a href="{e(reel_url)}">{e(reel_url)}</a></p>']
t = [f'Contenido de hoy, {fecha}.', '', '1 · REEL EN INSTAGRAM', tx['reel_instagram'], '', '2 · TIKTOK', tx['tiktok'], '',
     '3 · HISTORIAS', f'Historia 1 · reel compartido · {reel_url}']
for i, o in enumerate(of['ofertas'][:4]):
    url = (o.get('url') or 'https://tupala.es/precios/ofertas/') + U
    h.append(f'<p><b>Historia {i+2} · oferta-{i+1}.jpg</b> · {e(o["nombre"])} · {e(o["precio"])} ({e(o["pct"])})<br><a href="{e(url)}">{e(url)}</a></p>')
    t.append(f'Historia {i+2} · oferta-{i+1}.jpg · {o["nombre"]} · {o["precio"]} ({o["pct"]}) · {url}')
h += ['<p>En cada historia de producto, pon el sticker de enlace en el hueco de abajo, con el texto <i>Ver oferta</i>.</p>', '</div>']
open(os.path.join(out, 'correo.html'), 'w').write('\n'.join(h))
open(os.path.join(out, 'correo.txt'), 'w').write('\n'.join(t))
adj = [os.path.abspath(vid), os.path.abspath(os.path.join(out, 'portada.jpg'))] + \
      [os.path.abspath(os.path.join(out, 'historias', f'oferta-{i+1}.jpg')) for i in range(len(of['ofertas'][:4]))]
tam = sum(os.path.getsize(a) for a in adj)
json.dump({'asunto': f'TuPala · Reel e historias del {fecha}', 'para': ['begarciam7@gmail.com'], 'cc': ['adevicentegomez@gmail.com'],
           'adjuntos': adj, 'bytes_adjuntos': tam}, open(os.path.join(out, 'correo.json'), 'w'), ensure_ascii=False, indent=1)
if tam > 3_000_000: sys.exit(f'Adjuntos demasiado grandes: {tam} bytes')
print(os.path.join(out, 'correo.html'), tam, 'bytes')
