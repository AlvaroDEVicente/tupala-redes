"""Lee las «Ofertas destacadas» de la portada de tupala.es y descarga la foto grande de cada pala."""
import json, re, sys, os, subprocess
from playwright.sync_api import sync_playwright
JS=r"""()=>{const s=document.querySelector('#ofertas'); if(!s) return [];
return [...s.querySelectorAll('article.deal-card')].map(a=>{const q=c=>a.querySelector(c);
 const img=q('.deal-stage img'); let src=img?img.getAttribute('src'):''; const ss=img?img.getAttribute('srcset')||'':'';
 const m=[...ss.matchAll(/(\S+)\s+\d+w/g)].map(x=>x[1]); const big=m.length?m[m.length-1]:src;
 const col=a.closest('.deal-col'); const tab=col?col.querySelector('.deal-tab'):null;
 return {nombre:q('.deal-name')?.innerText.trim(), url:'https://tupala.es'+(q('.deal-name a')?.getAttribute('href')||''),
  attrs:[...a.querySelectorAll('.deal-attr')].map(x=>x.innerText.trim()), pct:q('.deal-pct')?.innerText.replace(/\s+/g,' ').trim(),
  vs:q('.deal-vs')?.innerText.replace(/\s+/g,' ').trim(), precio:q('.deal-now')?.innerText.replace(/\s+/g,' ').trim(),
  tienda:q('.deal-store b')?.innerText.trim(), dia:/oferta del d/i.test(a.innerText), rango:tab?tab.innerText.replace(/\s+/g,' ').trim():'', img:big, tag:q('.deal-tag')?.innerText.trim()||'', chart:(()=>{const sv=q('.tsc-svg'); if(!sv) return null; const band=sv.querySelector('.tsc-band'), p50=sv.querySelector('.tsc-p50'), ln=sv.querySelector('.tsc-line'), td=q('.tsc-today'); const top=td?parseFloat((td.getAttribute('style').match(/top:([\d.]+)%/)||[])[1]):null; return {d:ln?ln.getAttribute('d'):'', p50:p50?+p50.getAttribute('y1'):null, band:band?{y:+band.getAttribute('y'),h:+band.getAttribute('height')}:null, today:top, x:[...q('.tsc-x').querySelectorAll('span')].map(e=>e.innerText.trim())}})()}})}"""
def leer():
    with sync_playwright() as p:
        b=p.chromium.launch(); pg=b.new_page(viewport={'width':1280,'height':900})
        pg.goto('https://tupala.es/',wait_until='networkidle'); pg.wait_for_timeout(800)
        d=pg.evaluate(JS)
        tot=pg.evaluate("(document.querySelector('#ofertas .hub-sec-link')||{}).innerText||''")
        b.close()
        m=re.search(r'(\d+)',tot or '')
        return d,(int(m.group(1)) if m else None)
def imagen_grande(u):
    # las tiendas sirven la misma foto a más resolución quitando el tamaño de la URL
    if 'padelnuestro' in u: u=re.sub(r'\?.*$','',u)
    u=u.replace('home_default','large_default')
    if 'cdn.shopify.com' in u: u=re.sub(r'width=\d+','width=1500',u)
    return u
if __name__=='__main__':
    out=sys.argv[1]; os.makedirs(out,exist_ok=True)
    d,total=leer()
    if not d: sys.exit('No hay ofertas en la portada')
    for i,o in enumerate(d):
        o['img']=imagen_grande(o['img']); f=f'{out}/o{i}.jpg'
        r=subprocess.run(['curl','-sS','--max-time','25','-o',f,'-w','%{http_code}',o['img']],capture_output=True,text=True)
        o['foto']=f if r.stdout.strip()=='200' else None
        if o['foto']:
            try:   # recorta el margen blanco de la foto de la tienda para que la pala llene el escaparate
                from PIL import Image, ImageChops
                im=Image.open(f).convert('RGB'); bg=Image.new('RGB',im.size,(255,255,255))
                bb=ImageChops.difference(im,bg).convert('L').point(lambda v:255 if v>18 else 0).getbbox()
                if bb:
                    pad=int(max(im.size)*.02); bb=(max(0,bb[0]-pad),max(0,bb[1]-pad),min(im.width,bb[2]+pad),min(im.height,bb[3]+pad))
                    im.crop(bb).save(f,quality=94)
                o['foto_abs']=os.path.abspath(f)
            except Exception: o['foto_abs']=os.path.abspath(f)
    json.dump({'total':total,'ofertas':d},open(f'{out}/ofertas.json','w'),ensure_ascii=False,indent=1)
    for o in d: print(o['dia'],o['nombre'],o['pct'],o['precio'],o['tienda'],o['rango'],bool(o['foto']))
