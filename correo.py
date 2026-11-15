"""Genera el correo diario de historias (out/correo.html y out/correo.txt) a partir de work/ofertas.json y work/textos.json.
Uso: python3 correo.py work out [--con-video]"""
import json, os, sys, html, datetime
from zoneinfo import ZoneInfo
d, out = sys.argv[1], sys.argv[2]; con_video = '--con-video' in sys.argv
of = json.load(open(os.path.join(d, 'ofertas.json'))); tx = json.load(open(os.path.join(d, 'textos.json')))
U = '?utm_source=instagram&utm_medium=historia&utm_campaign=ofertas-dia'
MESES = ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']
hoy = datetime.datetime.now(ZoneInfo('Europe/Madrid')).date()
fecha = f'{hoy.day} de {MESES[hoy.month-1]}'
e = html.escape
reel_url = 'https://tupala.es/' + U + '#ofertas'
filas = []
for i, o in enumerate(of['ofertas'][:4]):
    url = (o.get('url') or 'https://tupala.es/precios/ofertas/') + U
    filas.append((i + 2, f'oferta-{i+1}.jpg', o['nombre'], o['precio'], o['pct'], url))
h = ['<div style="font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.5;color:#10243B;max-width:600px">',
     f'<p><b>Historias de hoy, {e(fecha)}.</b> Van adjuntas las 4 imágenes.</p>',
     '<p><b>Historia 1 · el reel</b><br>Comparte el reel publicado en tu historia y añade el sticker de enlace:<br>'
     f'<a href="{e(reel_url)}">{e(reel_url)}</a><br>Texto del sticker: <i>Ver las ofertas</i></p>']
t = [f'Historias de hoy, {fecha}. Adjuntas las 4 imágenes.', '', f'Historia 1 · reel compartido · {reel_url}']
for n, img, nom, pre, pct, url in filas:
    h.append(f'<p><b>Historia {n} · {img}</b> · {e(nom)} · {e(pre)} ({e(pct)})<br><a href="{e(url)}">{e(url)}</a></p>')
    t.append(f'Historia {n} · {img} · {nom} · {pre} ({pct}) · {url}')
h.append('<p>En cada historia de producto, pon el sticker de enlace en el hueco de abajo, con el texto <i>Ver oferta</i>.</p>')
if con_video:
    h += ['<hr style="border:0;border-top:1px solid #DCE3EB">',
          '<p><b>Reel de hoy</b> (adjunto; hoy no ha podido programarse en Metricool). Texto para Instagram y TikTok:</p>',
          f'<p style="white-space:pre-line;background:#F2F5F8;padding:12px;border-radius:8px">{e(tx["reel_instagram"])}</p>']
    t += ['', 'Reel de hoy adjunto. Texto:', tx['reel_instagram']]
h.append('</div>')
open(os.path.join(out, 'correo.html'), 'w').write('\n'.join(h))
open(os.path.join(out, 'correo.txt'), 'w').write('\n'.join(t))
json.dump({'asunto': f'TuPala · Historias del {fecha}', 'para': ['begarciam7@gmail.com'], 'cc': ['adevicentegomez@gmail.com'],
           'adjuntos': [os.path.abspath(os.path.join(out, 'historias', f'oferta-{i+1}.jpg')) for i in range(len(filas))]},
          open(os.path.join(out, 'correo.json'), 'w'), ensure_ascii=False, indent=1)
print(os.path.join(out, 'correo.html'))
