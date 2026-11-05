"""Reel diario «Ofertas de hoy» (1080x1920, plano continuo) a partir de ofertas.json + textos para redes."""
import json, os, re, sys, glob, subprocess, datetime
from playwright.sync_api import sync_playwright
H=os.path.dirname(os.path.abspath(__file__))
A=lambda p: 'file://'+os.path.join(H,'assets',p)
NAVY='#10243B'; LIME='#E4FB6A'; MINT='#8FE3C4'
BG='radial-gradient(900px 700px at 85% 35%,#1A6FBF 0%,transparent 60%),linear-gradient(170deg,#08213D 0%,#0D3F72 65%,#11589E 100%)'
FONTS='<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anton&family=Caveat+Brush&family=Instrument+Serif:ital@0;1&family=Inter+Tight:wght@500;600;700;800;900&family=JetBrains+Mono:wght@500;700&display=swap">'
DIAS=['lunes','martes','miércoles','jueves','viernes','sábado','domingo']
MESES=['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']
CX=470            # centro del área útil: a la derecha van los iconos de TikTok e Instagram
BEAT=3.6; HOOK=2.6; CLOSE=3.2
def eur2num(s): return float(re.sub(r'[^\d,]','',s).replace(',','.'))
def urlbar(path,size=40):
    lock=f'<svg width="{size*.62:.0f}" height="{size*.62:.0f}" viewBox="0 0 24 24" fill="none" stroke="#6b7686" stroke-width="2.4" stroke-linecap="round"><rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/></svg>'
    return f'<span style="display:inline-flex;align-items:center;gap:16px;background:#fff;color:{NAVY};border-radius:99px;padding:{size*.36:.0f}px {size*.8:.0f}px {size*.36:.0f}px {size*.55:.0f}px;transform:rotate(-2deg);box-shadow:0 16px 30px -14px rgba(0,0,0,.5);white-space:nowrap">{lock}<span style="font:800 {size}px Inter Tight,sans-serif;letter-spacing:-.5px">tupala.es<span style="color:#6b7686;font-weight:600">{path}</span></span></span>'
def P(id,html,x,y): return f'<div id="{id}" class="it" data-x="{x}" data-y="{y}">{html}</div>'
def build(data,fotos_dir,fecha):
    of=data['ofertas'][:4]; total=data.get('total')
    hoy=f'{DIAS[fecha.weekday()].capitalize()} {fecha.day} de {MESES[fecha.month-1]}'
    els=[]
    els.append(P('h0',f'<div class="kick" style="width:800px;font-size:30px;color:{LIME}">{hoy}</div>',496,430))
    els.append(P('h1','<div class="big" style="width:800px;font-size:150px;color:#fff">Las ofertas</div>',496,560))
    els.append(P('h2',f'<div class="big" style="width:800px;font-size:150px;color:{LIME}">de hoy.</div>',496,705))
    els.append(P('h3',f'<div class="ser" style="width:800px;font-size:52px;line-height:1.08;color:#DCEAF8">Comparadas con su propio historial,<br>no con el precio tachado.</div>',496,880))
    els.append(P('hp',f'<img class="pad" src="{A("tupala-pala-3d.png")}" style="height:520px;display:block">',CX+200,1270))
    tl=[]; T=HOOK
    for i,o in enumerate(of):
        hab=re.search(r'habitual de ([\d.]+)',o['vs'].replace(' ',' '))
        hab=float(hab.group(1).replace('.','')) if hab else None
        kick='Oferta del día' if o['dia'] else (o['rango'] or 'Oferta')
        foto=os.path.join(fotos_dir,f'c{data["ofertas"].index(o)}.png')
        attrs=' · '.join(o['attrs'])
        els.append(P(f'k{i}',f'<div class="kick" style="width:800px;font-size:30px;color:{LIME}">{kick}</div>',496,430))
        els.append(P(f'p{i}',f'<img class="pad" src="file://{foto}" style="height:560px;display:block">',CX+150,770))
        els.append(P(f'b{i}',f'<div class="badge"><span>{o["pct"]}</span></div>',CX-200,680))
        els.append(P(f'n{i}',f'<div style="width:800px"><div style="font:800 46px/1.1 Inter Tight;color:#fff">{o["nombre"]}</div><div class="kick" style="margin-top:8px;font-size:22px;color:rgba(255,255,255,.65)">{attrs}</div></div>',496,1120))
        els.append(P(f'v{i}',f'<div style="width:800px;display:flex;align-items:baseline;gap:22px"><span class="big" style="font-size:150px;color:{MINT}"><span id="c{i}">{o["precio"]}</span></span>'+(f'<span class="kick" style="font-size:30px;color:rgba(255,255,255,.6);text-decoration:line-through">{int(hab)} €</span>' if hab else '')+'</div>',496,1275))
        els.append(P(f's{i}',f'<div style="width:800px;font:600 28px/1.3 Inter Tight;color:#DCEAF8">en <b style="color:#fff">{o["tienda"]}</b> · {o["vs"]}</div>',496,1380))
        tl.append(dict(i=i,T=T,hab=hab or eur2num(o['precio']),now=eur2num(o['precio'])))
        T+=BEAT
    els.append(P('e1','<div class="big" style="width:800px;font-size:132px;color:#fff">Compara</div>',496,470))
    els.append(P('e2','<div class="big" style="width:800px;font-size:132px;color:#fff">antes de</div>',496,595))
    els.append(P('e5',f'<div class="big" style="width:800px;font-size:132px;color:{LIME}">comprar.</div>',496,720))
    msg=f'Hoy hay {total} palas por debajo de su precio habitual.' if total else 'Cada día, las palas por debajo de su precio habitual.'
    els.append(P('e3',f'<div style="width:800px;font:600 40px/1.3 Inter Tight;color:#DCEAF8">{msg}</div>',496,890))
    els.append(P('e4',urlbar('/precios/ofertas'),CX-30,1060))
    els.append(P('ep',f'<img class="pad" src="{A("tupala-pala-3d.png")}" style="height:360px;display:block">',CX+270,1290))
    els.append(P('ft',f'<div class="kick" style="width:800px;font-size:20px;color:rgba(255,255,255,.55)">Precios del {fecha.day} de {MESES[fecha.month-1]} · cambian a diario</div>',496,1460))
    END=T+CLOSE
    css=f'''<style>*{{box-sizing:border-box}}body{{margin:0}}
.art{{position:relative;width:1080px;height:1920px;overflow:hidden;background:{BG};color:#fff;font-family:'Inter Tight',sans-serif}}
.it{{position:absolute;left:0;top:0;transform-origin:50% 50%}}
.big{{font-family:Anton,sans-serif;text-transform:uppercase;line-height:.96}}
.kick{{font-family:'JetBrains Mono',monospace;font-weight:700;letter-spacing:2px;text-transform:uppercase}}
.ser{{font-family:'Instrument Serif',serif;font-style:italic}}
.pad{{filter:drop-shadow(18px 34px 30px rgba(0,0,0,.5))}}
.badge{{width:230px;height:230px;border-radius:50%;background:{LIME};color:{NAVY};display:flex;align-items:center;justify-content:center;transform:rotate(-10deg);box-shadow:0 18px 40px -12px rgba(0,0,0,.55)}}
.badge span{{font-family:Anton,sans-serif;font-size:84px;line-height:1;white-space:nowrap}}
.grain{{position:absolute;inset:0;background:url({A("grain.png")});opacity:.09;mix-blend-mode:overlay;pointer-events:none}}
</style>'''
    js=r'''<script>
const E={o:x=>x,expo:x=>x>=1?1:1-Math.pow(2,-10*x),io:x=>x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2,out:x=>1-Math.pow(1-x,3),
 back:x=>{const c=1.7;return 1+(c+1)*Math.pow(x-1,3)+c*Math.pow(x-1,2)}};
const D={o:1,x:0,y:0,s:1,r:0,b:0};
function K(id,t,fr){const el=document.getElementById(id); if(!el) return; let v={...D,...fr[0][1]};
 for(let i=0;i<fr.length-1;i++){const [t0,a]=fr[i],[t1,b,ease]=fr[i+1]; if(t>=t1){v={...v,...b};continue}
  if(t>t0){const k=(E[ease||'expo'])((t-t0)/(t1-t0)); const A={...v},B={...v,...b}; for(const p in B){v[p]=A[p]+(B[p]-A[p])*k}} break;}
 el.style.opacity=Math.max(0,Math.min(1,v.o));
 el.style.transform=`translate(${+el.dataset.x+v.x}px,${+el.dataset.y+v.y}px) translate(-50%,-50%) rotate(${v.r}deg) scale(${v.s})`;
 el.style.filter=v.b>.2?`blur(${v.b}px)`:'none';}
const TL=__TL__, HOOK=__HOOK__, BEAT=__BEAT__, END=__END__;
const fmt=v=>v.toFixed(2).replace('.',',')+' €';
window.render=function(t){
 const out=HOOK-.35;
 K('h0',t,[[.1,{o:0,y:40}],[.5,{o:1,y:0}],[out,{}],[out+.35,{o:0,x:-500},'io']]);
 K('h1',t,[[.25,{o:0,y:80}],[.7,{o:1,y:0}],[out,{}],[out+.35,{o:0,x:-500},'io']]);
 K('h2',t,[[.45,{o:0,y:80}],[.9,{o:1,y:0}],[out,{}],[out+.35,{o:0,x:-500},'io']]);
 K('h3',t,[[.8,{o:0,y:30}],[1.2,{o:1,y:0}],[out,{}],[out+.35,{o:0,x:-500},'io']]);
 K('hp',t,[[0,{o:0,y:400,r:-20}],[.9,{o:1,y:0,r:-8}],[out,{}],[out+.35,{o:0,x:-600,r:-20},'io']]);
 let sh=0;
 for(const s of TL){const i=s.i,T=s.T,X=T+BEAT-.35, last=i===TL.length-1;
  const ex=last?{o:0,y:-60}:{o:0,x:-560}; const exr=last?{o:0,y:-60}:{o:0,x:-600,r:-16};
  K('k'+i,t,[[T-.1,{o:0,y:30}],[T+.25,{o:1,y:0}],[X,{}],[X+.35,ex,'io']]);
  K('p'+i,t,[[T-.35,{o:0,x:600,r:16}],[T+.2,{o:1,x:0,r:4}],[X,{}],[X+.35,exr,'io']]);
  K('b'+i,t,[[T+.45,{o:0,s:.2,r:-30}],[T+.8,{o:1,s:1,r:0},'back'],[X,{}],[X+.35,ex,'io']]);
  K('n'+i,t,[[T+.1,{o:0,y:40}],[T+.5,{o:1,y:0}],[X,{}],[X+.35,ex,'io']]);
  K('v'+i,t,[[T+.2,{o:0,y:40}],[T+.6,{o:1,y:0}],[X,{}],[X+.35,ex,'io']]);
  K('s'+i,t,[[T+.35,{o:0,y:30}],[T+.75,{o:1,y:0}],[X,{}],[X+.35,ex,'io']]);
  const k=Math.max(0,Math.min(1,(t-(T+.5))/1.1)); const v=s.hab+(s.now-s.hab)*E.out(k);
  const c=document.getElementById('c'+i); if(c) c.textContent= k>=1?fmt(s.now): Math.round(v)+' €';
  const u=t-(T+.8); if(u>0&&u<.4) sh=Math.max(sh,Math.exp(-u*9));}
 const C=END-__CLOSE__;
 K('e1',t,[[C,{o:0,y:70}],[C+.45,{o:1,y:0}]]); K('e2',t,[[C+.12,{o:0,y:70}],[C+.57,{o:1,y:0}]]); K('e5',t,[[C+.24,{o:0,y:70}],[C+.69,{o:1,y:0}]]);
 K('e3',t,[[C+.6,{o:0,y:30}],[C+1.0,{o:1,y:0}]]); K('e4',t,[[C+.95,{o:0,y:40,s:.9}],[C+1.35,{o:1,y:0,s:1},'back']]);
 K('ep',t,[[C+.2,{o:0,x:400,r:30}],[C+.9,{o:1,x:0,r:-10}]]);
 K('ft',t,[[HOOK-.2,{o:0}],[HOOK+.2,{o:1}],[C,{}],[C+.3,{o:0}]]);
 document.querySelector('.art').style.translate=sh>.03?`${(Math.sin(t*95)*12*sh).toFixed(1)}px ${(Math.cos(t*80)*7*sh).toFixed(1)}px`:'0 0';
};
window.render(0);
</script>'''.replace('__TL__',json.dumps(tl)).replace('__HOOK__',str(HOOK)).replace('__BEAT__',str(BEAT)).replace('__END__',str(END)).replace('__CLOSE__',str(CLOSE))
    logo=f'<img src="{A("logo.svg")}" style="position:absolute;left:96px;top:300px;width:200px">'
    html=f'<!doctype html><html><head><meta charset="utf-8">{FONTS}{css}</head><body><div class="art">{logo}{"".join(els)}<div class="grain"></div></div>{js}</body></html>'
    return html,END
def textos(data,fecha):
    of=data['ofertas'][:4]; total=data.get('total')
    lis='\n'.join(f'{"🔥" if o["dia"] else "•"} {o["nombre"]}: {o["precio"]} en {o["tienda"]} ({o["pct"]}, {o["vs"]}).' for o in of)
    ig=(f'Las ofertas de hoy, comparadas con su propio historial y no con el precio tachado.\n\n{lis}\n\n'
        f'{"Hoy hay "+str(total)+" palas por debajo de su precio habitual. " if total else ""}Los precios cambian cada día: míralos antes de comprar.\n\n'
        '👉 tupala.es/precios/ofertas (link en la bio)\n\n#padel #padelespaña #palasdepadel #ofertaspadel #tupala')
    tt=(f'Título: Ofertas de palas de pádel de hoy\n\nDescripción: {" · ".join(o["nombre"]+" a "+o["precio"] for o in of)}. '
        'Comparadas con su propio historial. Búscalas en tupala.es 🎾\n\n#padel #padeltok #padelespaña #palasdepadel #ofertaspadel')
    return {'instagram_facebook':ig,'tiktok':tt}
if __name__=='__main__':
    d=sys.argv[1]; out=sys.argv[2] if len(sys.argv)>2 else os.path.join(d,'reel.mp4')
    data=json.load(open(os.path.join(d,'ofertas.json')))
    from recorte import recortar
    sys.path.insert(0,H)
    for i,o in enumerate(data['ofertas'][:4]):
        if o.get('foto'): recortar(o['foto'],os.path.join(d,f'c{i}.png'))
    data['ofertas']=[o for i,o in enumerate(data['ofertas'][:4]) if os.path.exists(os.path.join(d,f'c{i}.png'))] or sys.exit('Sin fotos')
    fecha=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=1))).date()
    html,END=build(data,os.path.abspath(d),fecha)
    hp=os.path.join(d,'reel.html'); open(hp,'w').write(html)
    json.dump(textos(data,fecha),open(os.path.join(d,'textos.json'),'w'),ensure_ascii=False,indent=1)
    fr=os.path.join(d,'frames'); os.makedirs(fr,exist_ok=True)
    for f in glob.glob(fr+'/*.jpg'): os.remove(f)
    mode=sys.argv[3] if len(sys.argv)>3 else 'video'
    with sync_playwright() as p:
        b=p.chromium.launch(); pg=b.new_page(viewport={'width':1080,'height':1920})
        pg.goto('file://'+os.path.abspath(hp),wait_until='networkidle'); pg.wait_for_timeout(1500)
        if mode=='stills':
            for t in [1.4,HOOK+1.4,HOOK+2.8,HOOK+BEAT+1.6,END-0.3]:
                pg.evaluate(f'render({t})'); pg.screenshot(path=os.path.join(d,f'still{t:05.2f}.png'))
        else:
            n=int((END+.3)*30)
            for i in range(n): pg.evaluate(f'render({i/30})'); pg.screenshot(path=f'{fr}/f{i:04d}.jpg',type='jpeg',quality=92)
        b.close()
    if mode!='stills':
        subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','30','-i',f'{fr}/f%04d.jpg','-c:v','libx264','-pix_fmt','yuv420p','-crf','20','-movflags','+faststart',out],check=True)
        print(out,round(END+.3,1),'s')
