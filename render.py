"""Historias diarias «Ofertas de hoy» · 1080x1920 · 30 fps · una historia por pantalla (portada, una por oferta, cierre).
Estética de tupala.es (azul noche, menta para el ahorro, lima de acento) en clave premium: profundidad,
vidrio, palas recortadas flotando, tipografía cinética y la gráfica de precio real de cada tarjeta."""
import json, os, re, sys, subprocess, datetime, html as H_
from playwright.sync_api import sync_playwright
HERE=os.path.dirname(os.path.abspath(__file__))
A=lambda p: 'file://'+os.path.join(HERE,'assets',p)
DIAS=['lunes','martes','miércoles','jueves','viernes','sábado','domingo']
MESES=['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']
HOOK=1.7; BEAT=2.8; CLOSE=2.8; FPS=30   # ~15 s: la franja de 7–15 s es la que más se termina de ver
UTM='?utm_source=instagram&utm_medium=historia&utm_campaign=ofertas-dia'
L=96; W=800                                   # columna x 96–896; vertical: arriba >270 (barra y avatar de la historia), 1490–1720 libre para el sticker
e=lambda s: H_.escape(str(s or ''))
nb=lambda s: e(s).replace(' ','&nbsp;')
def num(s): return float(re.sub(r'[^\d,]','',s or '0').replace(',','.') or 0)
def hab_de(o):
    m=re.search(r'habitual de ([\d.]+)',(o.get('vs') or '').replace(' ',' '))
    return int(m.group(1).replace('.','')) if m else None
def curva(d,tdy):
    """La gráfica de la web acaba en el último día con histórico y pinta el precio de hoy como un punto suelto;
    en el vídeo la línea baja hasta ese punto. Los huecos sin datos (varias M) se unen con una línea discontinua."""
    if not d:   # sin histórico: solo sabemos el precio habitual (línea p50, y≈13) y el de hoy
        return '', f'M0,13 C60,13 70,{tdy} 100,{tdy} L100,100 L0,100 Z', f'M0,13 C60,13 70,{tdy} 100,{tdy}'
    num=r'(-?[\d.]+),(-?[\d.]+)'
    trozos=[t for t in re.split(r'(?=M)',d) if t.strip()]
    gaps=''; prev=None
    for t in trozos:
        pts=re.findall(num,t)
        if prev and pts: gaps+=f'M{prev[0]},{prev[1]} L{pts[0][0]},{pts[0][1]} '
        if pts: prev=pts[-1]
    xl,yl=float(prev[0]),float(prev[1])
    linea=d
    if xl<99.5:
        m=xl+(100-xl)*.5
        linea+=f' C{m:.2f},{yl:.2f} {m:.2f},{tdy:.2f} 100,{tdy:.2f}'
    unida=trozos[0]+''.join('L'+t[1:] for t in trozos[1:])
    if xl<99.5: unida+=f' C{m:.2f},{yl:.2f} {m:.2f},{tdy:.2f} 100,{tdy:.2f}'
    return linea, unida+' L100,100 L0,100 Z', gaps.strip()
def build(data,fecha,fotos,reel=True):
    of=data['ofertas'][:4]; n=len(of); total=data.get('total')
    pcts=[int(re.sub(r'\D','',o['pct']) or 0) for o in of]; top=max(pcts) if pcts else 0
    hoy=f'{DIAS[fecha.weekday()]} {fecha.day} de {MESES[fecha.month-1]}'
    pills=''.join(f'<span class="pill" id="pl{i}">{nb(o["rango"])}</span>' for i,o in enumerate(of))
    fan=''.join(f'<img class="it fan" id="fn{i}" data-x="{250+i*150}" data-y="1150" src="file://{fotos[i]}">' for i in range(n))
    offers=''
    for i,o in enumerate(of):
        c=o.get('chart') or {}; hab=hab_de(o); p50=c.get('p50'); tdy=c.get('today') or 83
        d,area,gaps=curva(c.get('d',''),tdy)
        tag=o.get('tag') or ''
        tagh=f'<div class="it chip {"day" if o.get("dia") else "seal"}" id="tg{i}" data-x="{L+150}" data-y="988">{e(tag)}</div>' if tag else ''
        x0,x1=(c.get('x') or ['',''])[0],(c.get('x') or ['',''])[-1]
        offers+=f'''<div class="sw" id="w{i+1}">
<div class="it glow" id="gw{i}" data-x="700" data-y="820"></div>
<img class="it pad" id="pd{i}" data-x="700" data-y="840" src="file://{fotos[i]}">
<div class="it" id="rg{i}" data-x="{L+W/2}" data-y="395"><div class="rng" style="width:{W}px"><span class="rk">Presupuesto</span><b>{nb(o["rango"])}</b></div></div>
<div class="it stk" id="sk{i}" data-x="{L+160}" data-y="730"><div class="stk-in"><small>ahorras</small><span>−<em id="pv{i}">0</em>%</span></div></div>
<div class="it glass" id="gl{i}" data-x="{L+W/2}" data-y="1238">
 <div class="g-name">{e(o["nombre"])}</div>
 <div class="g-attr">{" · ".join(e(a) for a in o.get("attrs",[]))} · en <b>{e(o["tienda"])}</b></div>
 <div class="g-price"><span class="now" id="nw{i}">{nb(o["precio"])}</span>{f'<span class="old">{hab}&nbsp;€</span>' if hab else ''}</div>
 <div class="g-chart">
  <svg viewBox="0 0 100 100" preserveAspectRatio="none"><defs>
   <linearGradient id="ga{i}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8FE3C4" stop-opacity=".45"/><stop offset="1" stop-color="#8FE3C4" stop-opacity="0"/></linearGradient>
   <clipPath id="cp{i}"><rect id="cr{i}" x="-2" y="-20" width="0" height="140"/></clipPath></defs>
   {f'<line class="p50" x1="0" y1="{p50}" x2="100" y2="{p50}" vector-effect="non-scaling-stroke"/>' if p50 is not None else ''}
   <g clip-path="url(#cp{i})"><path d="{e(area)}" fill="url(#ga{i})"/><path class="ln" d="{e(d)}" vector-effect="non-scaling-stroke"/>{f'<path class="gap" d="{e(gaps)}" vector-effect="non-scaling-stroke"/>' if gaps else ''}</g></svg>
  <span class="ring" id="rn{i}" style="top:{tdy}%"></span><span class="dot" id="dt{i}" style="top:{tdy}%"></span>
  <div class="xl"><span>{e(x0)}</span><span class="lg">- - - precio habitual</span><span>Hoy</span></div>
 </div>
</div>{tagh}</div>'''
    tiles=''
    for i,o in enumerate(of):
        tiles+=f'''<div class="it row" id="tl{i}" data-x="{L+W/2}" data-y="{688+i*158}"><div class="r-n">{i+1}</div><div class="r-im"><img src="file://{fotos[i]}"></div><div class="r-tx"><div class="r-nm">{e(o["nombre"])}</div><div class="r-mt">{nb(o["rango"])} · <b>{nb(o["precio"])}</b></div></div><div class="r-p">{e(o["pct"])}</div></div>'''
    css=f'''<style>
*{{box-sizing:border-box}}body{{margin:0}}
.art{{position:relative;width:1080px;height:1920px;overflow:hidden;background:#071a30;font-family:Inter,system-ui,sans-serif;color:#fff}}
.bg{{position:absolute;inset:-200px;background:radial-gradient(700px 700px at 75% 38%,rgba(26,111,191,.75),transparent 62%),radial-gradient(650px 650px at 15% 85%,rgba(17,88,158,.55),transparent 60%),linear-gradient(170deg,#06182C 0%,#0B2E52 55%,#0F4F8A 100%)}}
.grid{{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.035) 1px,transparent 1px);background-size:60px 60px;mask-image:radial-gradient(800px 900px at 50% 45%,#000,transparent 75%)}}
.grain{{position:absolute;inset:0;background:url({A("grain.png")});opacity:.10;mix-blend-mode:overlay;pointer-events:none}}
.it{{position:absolute;left:0;top:0;transform-origin:50% 50%;will-change:transform,opacity}}
.mono{{font-family:'JetBrains Mono',monospace;font-weight:700;letter-spacing:.16em;text-transform:uppercase}}
.prog{{display:flex;gap:10px;width:{W}px}}.seg{{flex:1;height:8px;border-radius:9px;background:rgba(255,255,255,.18);overflow:hidden}}.seg i{{display:block;height:100%;width:0;background:#E4FB6A;border-radius:9px}}
.h-k{{font-size:26px;color:#E4FB6A}}
.h-t{{font:900 112px/.92 Inter;letter-spacing:-.045em}}
.h-n{{display:inline-block;white-space:nowrap;padding:0 14px 10px 0;font:900 250px/.86 Inter;letter-spacing:-.06em;background:linear-gradient(180deg,#E4FB6A 0%,#8FE3C4 100%);-webkit-background-clip:text;background-clip:text;color:transparent;filter:drop-shadow(0 20px 50px rgba(143,227,196,.35))}}
.h-s{{font:600 38px/1.3 Inter;color:#DCEAF8}}
.pills{{display:flex;flex-wrap:wrap;gap:12px}}.pills{{flex-wrap:nowrap!important;gap:10px!important}}.pill{{display:inline-block;font:800 22px Inter;padding:11px 16px;border-radius:99px;background:rgba(255,255,255,.1);border:1.5px solid rgba(255,255,255,.25);color:#fff;white-space:nowrap}}
.fan{{height:440px;filter:drop-shadow(0 30px 40px rgba(0,0,0,.55))}}
.rng{{display:flex;flex-direction:column;gap:10px}}.rng .rk{{font:700 24px 'JetBrains Mono',monospace;letter-spacing:.16em;text-transform:uppercase;color:#8FA3BC}}
.rng b{{font:900 104px/.9 Inter;letter-spacing:-.045em;color:#fff}}
.glow{{width:760px;height:760px;border-radius:50%;background:radial-gradient(closest-side,rgba(143,227,196,.38),rgba(26,111,191,.18) 55%,transparent 72%)}}
.pad{{height:800px;filter:drop-shadow(0 50px 50px rgba(0,0,0,.6)) drop-shadow(0 0 1px rgba(255,255,255,.4))}}
.stk{{width:285px;height:285px;border-radius:50%;background:#E4FB6A;color:#10243B;display:flex;align-items:center;justify-content:center;box-shadow:0 24px 60px -18px rgba(228,251,106,.55),inset 0 -10px 0 rgba(0,0,0,.08)}}
.stk-in{{text-align:center;line-height:1}}.stk small{{display:block;font:800 22px 'JetBrains Mono',monospace;letter-spacing:.14em;text-transform:uppercase;margin-bottom:4px}}
.stk span{{font:900 84px/1 Inter;letter-spacing:-.05em;white-space:nowrap}}.stk em{{font-style:normal}}
.glass{{width:{W}px;height:430px;border-radius:36px;padding:34px 38px 30px;background:linear-gradient(160deg,rgba(255,255,255,.16),rgba(255,255,255,.05));border:1.5px solid rgba(255,255,255,.22);backdrop-filter:blur(26px) saturate(140%);-webkit-backdrop-filter:blur(26px) saturate(140%);box-shadow:0 40px 80px -30px rgba(0,0,0,.6),inset 0 1px 0 rgba(255,255,255,.25);display:flex;flex-direction:column}}
.g-name{{font:800 44px/1.05 Inter;letter-spacing:-.02em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.g-attr{{margin-top:8px;font:500 25px Inter;color:#DCEAF8}}.g-attr b{{color:#fff}}
.g-price{{margin-top:14px;display:flex;align-items:baseline;gap:18px}}
.now{{font:900 86px/1 Inter;letter-spacing:-.04em;color:#8FE3C4}}
.old{{font:600 34px Inter;color:#8FA3BC;text-decoration:line-through;text-decoration-thickness:3px}}
.g-chart{{position:relative;flex:1;margin:22px 4px 26px}}
.g-chart svg{{position:absolute;inset:0;width:100%;height:100%;overflow:visible}}
.p50{{stroke:rgba(255,255,255,.45);stroke-width:2.5;stroke-dasharray:8 8}}
.gap{{fill:none;stroke:rgba(255,255,255,.4);stroke-width:5;stroke-linecap:round;stroke-linejoin:round}}
.ln{{fill:none;stroke:#fff;stroke-width:5;stroke-linecap:round;stroke-linejoin:round;filter:drop-shadow(0 0 6px rgba(143,227,196,.7))}}
.hl{{position:absolute;left:0;transform:translateY(-135%);font:700 18px 'JetBrains Mono',monospace;letter-spacing:.1em;text-transform:uppercase;color:rgba(255,255,255,.65)}}
.dot{{position:absolute;left:100%;width:26px;height:26px;margin:-13px 0 0 -13px;border-radius:50%;background:#8FE3C4;box-shadow:0 0 0 5px rgba(7,26,48,.9),0 0 24px #8FE3C4}}
.ring{{position:absolute;left:100%;width:26px;height:26px;margin:-13px 0 0 -13px;border-radius:50%;border:3px solid #8FE3C4}}
.today{{position:absolute;left:100%;transform:translate(-120%,-240%);font:800 20px 'JetBrains Mono',monospace;letter-spacing:.1em;text-transform:uppercase;color:#8FE3C4}}
.xl{{position:absolute;left:0;right:0;bottom:-30px;display:flex;justify-content:space-between;font:600 19px Inter;color:#8FA3BC}}.xl .lg{{font:700 16px 'JetBrains Mono',monospace;letter-spacing:.08em;text-transform:uppercase;color:rgba(255,255,255,.5)}}.xl span:last-child{{color:#8FE3C4;font-weight:800}}
.chip{{font:800 22px/1 'JetBrains Mono',monospace;letter-spacing:.12em;text-transform:uppercase;padding:13px 22px;border-radius:99px;white-space:nowrap}}
.chip.day{{background:#E4FB6A;color:#2A3A00;box-shadow:0 10px 30px -8px rgba(228,251,106,.6)}}
.chip.seal{{background:#10243B;color:#8FE3C4;border:2px solid #8FE3C4}}
.row{{width:{W}px;height:148px;border-radius:26px;display:flex;align-items:center;gap:20px;padding:0 26px 0 18px;background:linear-gradient(160deg,rgba(255,255,255,.15),rgba(255,255,255,.05));border:1.5px solid rgba(255,255,255,.2);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px)}}
.r-n{{flex:none;width:58px;height:58px;border-radius:50%;background:#E4FB6A;color:#10243B;font:900 32px/58px Inter;text-align:center}}
.r-im{{flex:none;width:86px;height:130px;display:flex;align-items:center;justify-content:center}}.r-im img{{max-height:126px;max-width:86px;filter:drop-shadow(0 10px 12px rgba(0,0,0,.5))}}
.r-tx{{flex:1;min-width:0}}.r-nm{{font:800 30px/1.1 Inter;letter-spacing:-.01em;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}}.r-mt{{margin-top:6px;font:500 23px Inter;color:#DCEAF8}}.r-mt b{{color:#fff}}
.r-p{{flex:none;font:900 58px/1 Inter;color:#8FE3C4;letter-spacing:-.04em}}
.tile{{width:390px;height:270px;border-radius:28px;background:linear-gradient(160deg,rgba(255,255,255,.15),rgba(255,255,255,.05));border:1.5px solid rgba(255,255,255,.2);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);overflow:hidden}}
.tile img{{position:absolute;left:18px;top:20px;height:230px;filter:drop-shadow(0 16px 20px rgba(0,0,0,.5))}}
.t-n{{position:absolute;right:22px;top:16px;font:900 64px/1 Inter;color:rgba(255,255,255,.16);letter-spacing:-.04em}}
.t-r{{position:absolute;left:180px;bottom:30px;display:flex;flex-direction:column;gap:6px}}
.t-p{{font:900 64px/1 Inter;color:#8FE3C4;letter-spacing:-.04em}}.t-g{{font:700 21px Inter;color:#fff}}.t-e{{font:600 21px Inter;color:#DCEAF8}}
.cta{{display:inline-flex;align-items:center;gap:16px;background:#fff;color:#10243B;border-radius:99px;padding:22px 40px 22px 30px;font:800 40px Inter;box-shadow:0 18px 40px -16px rgba(0,0,0,.6)}}.cta i{{font-style:normal;color:#5f6674;font-weight:600}}
.sw{{position:absolute;inset:0;display:none}}
</style>'''
    body=f'''<div class="art"><div class="bg" id="bg"></div><div class="grid"></div>
<img class="it" id="lg" data-x="196" data-y="282" src="{A("logo-blanco.svg")}" style="width:200px">
<div class="sw" id="w0">
<div class="it" id="h0" data-x="{L+W/2}" data-y="372"><div class="mono h-k" style="width:{W}px">{e(hoy.capitalize())}</div></div>
<div class="it" id="h1" data-x="{L+W/2}" data-y="474"><div class="h-t" style="width:{W}px;font-size:110px;white-space:nowrap">Ofertas de hoy</div></div>
<div class="it" id="h2" data-x="{L+W/2}" data-y="650"><div style="width:{W}px"><div class="h-n" style="font-size:112px;line-height:.95">para todos<br>los bolsillos.</div></div></div>
{fan}
<div class="it" id="h3" data-x="{L+W/2}" data-y="830"><div class="pills" style="width:{W}px">{pills}</div></div>
</div>
{offers}
<div class="sw" id="w{n+1}">
<div class="it" id="c0" data-x="{L+W/2}" data-y="372"><div class="mono h-k" style="width:{W}px">Tu turno</div></div>
<div class="it" id="c1" data-x="{L+W/2}" data-y="472"><div class="h-t" style="width:{W}px;font-size:98px;white-space:nowrap">¿Cuál te <span style="color:#E4FB6A">llevas?</span></div></div>
{tiles}
<div class="it" id="c4" data-x="{L+W/2}" data-y="560"><div class="h-s" style="width:{W}px;white-space:nowrap;font-size:32px">{f"Y {total-n} ofertas más en tupala.es" if total and total>n else "Todas las ofertas en tupala.es"}</div></div>
{'<div class="it" id="c2" data-x="'+str(L+W/2)+'" data-y="1300"><div class="h-s" style="width:'+str(W)+'px;white-space:nowrap;font-size:33px"><b style="color:#E4FB6A">Comenta su número.</b> Descubre más ofertas en:</div></div><div class="it" id="c3" data-x="'+str(L+300)+'" data-y="1392"><div class="cta">tupala.es<i>/precios/ofertas</i></div></div>' if reel else '<div class="it" id="c2" data-x="'+str(L+W/2)+'" data-y="1372"><div class="h-s" style="width:'+str(W)+'px;white-space:nowrap;font-size:36px"><b style="color:#E4FB6A">Vota tu favorita aquí abajo&nbsp;↓</b></div></div>'}
</div><div class="grain"></div></div>'''
    tl=[dict(pct=pcts[i],now=num(o['precio']),hab=hab_de(o) or num(o['precio']),now_s=o['precio'].replace(' ',' ')) for i,o in enumerate(of)]
    END=HOOK+n*BEAT+CLOSE
    js=r'''<script>
const E={o:x=>x,expo:x=>x>=1?1:1-Math.pow(2,-10*x),io:x=>x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2,out:x=>1-Math.pow(1-x,3),
 qin:x=>x*x*x*x, back:x=>{const c=1.7;return 1+(c+1)*Math.pow(x-1,3)+c*Math.pow(x-1,2)}};
const D={o:1,x:0,y:0,s:1,r:0,b:0};
function K(id,t,fr){const el=document.getElementById(id); if(!el) return null; let v={...D,...fr[0][1]};
 for(let i=0;i<fr.length-1;i++){const [t0,a]=fr[i],[t1,b,ease]=fr[i+1]; if(t>=t1){v={...v,...b};continue}
  if(t>t0){const k=(E[ease||'expo'])((t-t0)/(t1-t0)); const A={...v},B={...v,...b}; for(const p in B){v[p]=A[p]+(B[p]-A[p])*k}} break;}
 el.style.opacity=Math.max(0,Math.min(1,v.o));
 el.style.transform=`translate(${+el.dataset.x+v.x}px,${+el.dataset.y+v.y}px) translate(-50%,-50%) rotate(${v.r}deg) scale(${v.s})`;
 el.style.filter=v.b>.3?`blur(${v.b.toFixed(1)}px)`:''; return v;}
const cl=v=>Math.max(0,Math.min(1,v));
const TL=__TL__,HOOK=__HOOK__,BEAT=__BEAT__,END=__END__,TOP=__TOP__,CLOSE=__CLOSE__,N=TL.length;
window.render=function(t){
 const C=HOOK+N*BEAT;
 const seg=t<HOOK?0:(t<C?1+Math.floor((t-HOOK)/BEAT):N+1);
 for(let k=0;k<=N+1;k++) document.getElementById('w'+k).style.display=k===seg?'block':'none';
 document.getElementById('bg').style.transform=`translate(${Math.sin(t*.35)*40}px,${Math.cos(t*.28)*50}px) scale(${1.05+.03*Math.sin(t*.5)})`;
 K('lg',t,[[0,{o:0,y:-20}],[.4,{o:1,y:0}]]);
 // PORTADA (sin salida: la historia corta sola)
 K('h0',t,[[.0,{o:0,y:30}],[.3,{o:1,y:0}]]);
 K('h1',t,[[.05,{o:0,y:90,b:12}],[.4,{o:1,y:0,b:0}]]);
 K('h2',t,[[.2,{o:0,y:90,s:.9,b:12}],[.6,{o:1,y:0,s:1,b:0},'out']]);
 K('h3',t,[[.45,{o:1}]]);
 for(let i=0;i<N;i++) K('pl'+i,t,[[.45+i*.07,{o:0,y:30}],[.72+i*.07,{o:1,y:0},'out']]);
 for(let i=0;i<N;i++){const sp=(i-(N-1)/2);
  K('fn'+i,t,[[.45+i*.07,{o:0,y:500,r:sp*16}],[.95+i*.07,{o:1,y:Math.abs(sp)*30,r:sp*12,x:0},'expo']]);}
 // UNA HISTORIA POR OFERTA: entra, dibuja la bajada y se queda quieta para leerla
 for(let i=0;i<N;i++){const s=TL[i],T=HOOK+i*BEAT;
  const v=K('pd'+i,t,[[T,{o:0,x:900,r:24,b:30}],[T+.45,{o:1,x:0,r:9,b:0},'expo'],[T+BEAT,{x:-20,r:8},'o']]);
  if(v&&t>T){const el=document.getElementById('pd'+i); el.style.transform+=` translateY(${Math.sin((t-T)*1.6)*14}px)`;}
  K('gw'+i,t,[[T,{o:0,s:.6}],[T+.45,{o:1,s:1}],[T+BEAT,{s:1.06},'o']]);
  K('rg'+i,t,[[T+.03,{o:0,x:120,b:14}],[T+.33,{o:1,x:0,b:0}]]);
  K('sk'+i,t,[[T+.28,{o:0,s:.6,r:-30}],[T+.58,{o:1,s:1,r:-8},'out']]);
  document.getElementById('pv'+i).textContent=Math.round(s.pct*E.out(cl((t-(T+.32))/.6)));
  K('gl'+i,t,[[T+.06,{o:0,y:160}],[T+.4,{o:1,y:0}]]);
  K('tg'+i,t,[[T+.42,{o:0,s:.6,r:-10}],[T+.7,{o:1,s:1,r:-4},'out']]);
  const kn=E.out(cl((t-(T+.4))/.75)); document.getElementById('nw'+i).textContent=kn>=1?s.now_s:Math.round(s.hab+(s.now-s.hab)*kn)+' €';
  document.getElementById('cr'+i).setAttribute('width',(104*E.io(cl((t-(T+.5))/.95))).toFixed(2));
  const dk=E.out(cl((t-(T+1.42))/.25)); const dt=document.getElementById('dt'+i); dt.style.opacity=dk; dt.style.scale=String(Math.max(.01,dk));
  const rn=document.getElementById('rn'+i), ru=((t-(T+1.55))%1.0+1.0)%1.0/1.0; rn.style.opacity=t>T+1.55?(1-ru)*.8:0; rn.style.scale=String(1+ru*2);
 }
 // CIERRE: lista numerada y hueco para la encuesta
 K('c0',t,[[C+.05,{o:0,y:30}],[C+.4,{o:1,y:0}]]);
 K('c1',t,[[C+.1,{o:0,y:90,b:12}],[C+.55,{o:1,y:0,b:0}]]);
 K('c4',t,[[C+.3,{o:0,y:20}],[C+.6,{o:1,y:0}]]);
 for(let i=0;i<N;i++) K('tl'+i,t,[[C+.3+i*.1,{o:0,x:220,b:14}],[C+.65+i*.1,{o:1,x:0,b:0},'expo']]);
 K('c2',t,[[C+.9,{o:0,y:30}],[C+1.2,{o:1,y:0}]]);
 K('c3',t,[[C+1.1,{o:0,y:40,s:.9}],[C+1.45,{o:1,y:0,s:1},'out']]);
};
window.render(0);
</script>'''
    for k,v in {'__TL__':json.dumps(tl,ensure_ascii=False),'__HOOK__':str(HOOK),'__BEAT__':str(BEAT),'__END__':str(END),'__TOP__':str(top),'__CLOSE__':str(CLOSE)}.items(): js=js.replace(k,v)
    fonts='<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700;800;900&family=JetBrains+Mono:wght@600;700;800&display=swap">'
    return f'<!doctype html><html><head><meta charset="utf-8">{fonts}{css}</head><body>{body}{js}</body></html>',END
def textos(data,fecha):
    """Lo que necesita quien publica: el enlace de cada historia, la encuesta y el texto del vídeo completo para TikTok."""
    of=data['ofertas'][:4]; n=len(of)
    pcts=[int(re.sub(r'\D','',o['pct']) or 0) for o in of]; top=max(pcts) if pcts else 0
    enl=[{'historia':i+2,'nombre':o['nombre'],'url':(o.get('url') or 'https://tupala.es/precios/ofertas/')+UTM,'texto_sticker':'Ver oferta'} for i,o in enumerate(of)]
    enc={'historia':n+2,'pregunta':'¿Cuál te llevas?','opciones':[str(i+1) for i in range(n)]}
    tt=(f'Palas de pádel hasta −{top} % hoy, una por presupuesto y comparadas con lo que cuestan normalmente. '
        '¿Cuál te llevas? Comenta su número. Todas en tupala.es 🎾\n\n#padel #padeltok #padelespaña #palasdepadel #ofertaspadel')
    lis='\n'.join(f'{i+1}. {o["nombre"]} · {o["precio"]} ({o["pct"]})' for i,o in enumerate(of))
    total=data.get('total')
    ig=(f'Ofertas de hoy para todos los bolsillos 🎾\n\n{lis}\n\n'
        'Comparadas con lo que cada pala cuesta normalmente, no con el precio tachado.\n\n'
        '¿Cuál te llevas? Comenta su número 👇\n\n'
        f'{"Las 4 del vídeo y "+str(total-len(of))+" ofertas más" if total and total>len(of) else "Las ofertas del vídeo"}: link en la bio.\n\n'
        '#padel #padeltok #padelespaña #palasdepadel #ofertaspadel #tupala')
    return {'reel_instagram':ig,'tiktok':tt,'enlaces':enl,'encuesta':enc}
if __name__=='__main__':
    d=sys.argv[1]; out=sys.argv[2]; mode=sys.argv[3] if len(sys.argv)>3 else 'video'; reel=(sys.argv[4] if len(sys.argv)>4 else 'reel')=='reel'
    data=json.load(open(os.path.join(d,'ofertas.json')))
    sys.path.insert(0,HERE); from recorte import recortar
    keep=[]; fotos=[]
    for i,o in enumerate(data['ofertas'][:4]):
        if not o.get('foto'): continue
        c=os.path.abspath(os.path.join(d,f'c{i}.png')); recortar(o['foto'],c); keep.append(o); fotos.append(c)
    if not keep: sys.exit('Sin ofertas con foto')
    data['ofertas']=keep
    fecha=datetime.datetime.now(__import__("zoneinfo").ZoneInfo("Europe/Madrid")).date()
    html,END=build(data,fecha,fotos,reel)
    hp=os.path.join(d,'historias.html'); open(hp,'w').write(html)
    json.dump(textos(data,fecha),open(os.path.join(d,'textos.json'),'w'),ensure_ascii=False,indent=1)
    with sync_playwright() as p:
        b=p.chromium.launch(); pg=b.new_page(viewport={'width':1080,'height':1920})
        pg.goto('file://'+os.path.abspath(hp),wait_until='networkidle'); pg.wait_for_timeout(1500)
        if mode=='stills':
            n=len(keep); ts=[HOOK-.05]+[HOOK+i*BEAT+.9 for i in range(1)]+[HOOK+(i+1)*BEAT-.05 for i in range(n)]+[END-.05]
            for t in ts: pg.evaluate(f'render({t})'); pg.screenshot(path=os.path.join(d,f'still{t:05.2f}.png'))
        else:
            os.makedirs(out,exist_ok=True); n=len(keep); C=HOOK+n*BEAT
            segs=[(0,HOOK)]+[(HOOK+i*BEAT,BEAT) for i in range(n)]+[(C,CLOSE)]
            files=[]
            for k,(s0,du) in enumerate(segs):
                f=os.path.join(out,f'historia-{k+1}.mp4'); tmp=f[:-4]+'.part.mp4'
                ff=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','image2pipe','-framerate',str(FPS),'-c:v','mjpeg','-i','-',
                    '-c:v','libx264','-pix_fmt','yuv420p','-crf','19','-preset','medium','-r',str(FPS),'-movflags','+faststart',tmp],stdin=subprocess.PIPE)
                for j in range(round(du*FPS)):
                    pg.evaluate(f'render({s0+j/FPS+1e-4})'); ff.stdin.write(pg.screenshot(type='jpeg',quality=92))
                ff.stdin.close()
                if ff.wait()!=0: sys.exit('ffmpeg falló')
                os.replace(tmp,f); files.append(f)
            lst=os.path.join(out,'lista.txt'); open(lst,'w').write(''.join(f"file '{os.path.abspath(f)}'\n" for f in files))
            comp=os.path.join(out,'historia-completa.mp4'); tmp=comp[:-4]+'.part.mp4'
            if subprocess.run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i',lst,'-c','copy','-movflags','+faststart',tmp]).returncode!=0: sys.exit('concat falló')
            os.replace(tmp,comp); os.remove(lst); print(len(files),'historias +',comp,round(END,1),'s')
            # Copia para subir: el conector de Drive admite ~3 MB por envío; con gráficos planos no se nota la diferencia.
            web=os.path.join(out,'reel-web.mp4')
            for crf in (24,26,28,30,32,34):
                subprocess.run(['ffmpeg','-y','-loglevel','error','-i',comp,'-c:v','libx264','-crf',str(crf),'-preset','slow',
                    '-pix_fmt','yuv420p','-movflags','+faststart','-an',web],check=True)
                if os.path.getsize(web)<3_000_000: break
            else: sys.exit('reel-web.mp4 no baja de 3 MB')
            print(web,round(os.path.getsize(web)/1e6,2),'MB crf',crf)
        b.close()
