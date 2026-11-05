"""Reel diario «Ofertas de hoy»: 1080x1920, 30 fps, plano continuo con la estética de las tarjetas de tupala.es.
Una tarjeta por rango de precio (hasta 4), con su gráfica de precio real tal como la pinta la web."""
import json, os, re, sys, subprocess, datetime, html as H_
from playwright.sync_api import sync_playwright
HERE=os.path.dirname(os.path.abspath(__file__))
A=lambda p: 'file://'+os.path.join(HERE,'assets',p)
DIAS=['lunes','martes','miércoles','jueves','viernes','sábado','domingo']
MESES=['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']
HOOK=2.6; BEAT=4.4; CLOSE=3.4; FPS=30
CX=470; CW=800                                  # tarjeta centrada en el área útil (a la derecha van los iconos de las apps)
e=lambda s: H_.escape(str(s or ''))
def num(s): return float(re.sub(r'[^\d,]','',s or '0').replace(',','.') or 0)
def build(data,fecha):
    of=data['ofertas'][:4]; n=len(of); total=data.get('total')
    pcts=[int(re.sub(r'\D','',o['pct']) or 0) for o in of]; top=max(pcts) if pcts else 0
    hoy=f'{DIAS[fecha.weekday()]} {fecha.day} de {MESES[fecha.month-1]}'
    tabs=''.join(f'<div class="tab" id="tab{i}" style="font-size:{24 if n<4 else 21}px">{e(o["rango"])}</div>' for i,o in enumerate(of))
    cards=''
    for i,o in enumerate(of):
        c=o.get('chart') or {}
        hab=re.search(r'habitual de ([\d.]+)',(o.get('vs') or '').replace(' ',' '))
        hab=int(hab.group(1).replace('.','')) if hab else None
        band=f'<rect class="band" x="0" y="{c["band"]["y"]}" width="100" height="{c["band"]["h"]}"/>' if c.get('band') else ''
        p50=c.get('p50'); tdy=c.get('today') or 83
        tagc='day' if o.get('dia') else ('seal' if o.get('tag') else '')
        tag=f'<div class="tag {tagc}" id="tg{i}">{e(o["tag"])}</div>' if o.get('tag') else ''
        habl=f'<div class="habl" style="top:{p50}%">habitual {hab} €</div>' if (p50 is not None and hab) else ''
        cards+=f'''<div class="card" id="cd{i}">
 <div class="stage"><img id="im{i}" src="{e("file://"+o["foto_abs"]) if o.get("foto_abs") else e(o["img"])}"></div>{tag}
 <div class="body">
  <div class="name" id="nm{i}">{e(o["nombre"])}</div>
  <div class="attrs" id="at{i}">{' · '.join(e(a) for a in o.get('attrs',[]))}</div>
  <div class="rule"></div>
  <div class="pct" id="pc{i}">−<span id="pv{i}">0</span> %</div>
  <div class="vs" id="vs{i}">{e(o["vs"])}</div>
  <div class="price" id="pr{i}"><span class="now" id="nw{i}">{e(o["precio"])}</span><span class="store">en <b>{e(o["tienda"])}</b></span></div>
  <div class="chart" id="ch{i}">
   <svg viewBox="0 0 100 100" preserveAspectRatio="none"><defs><clipPath id="rv{i}"><rect id="rr{i}" x="0" y="-10" width="0" height="120"/></clipPath></defs>
    {band}{f'<line class="p50" x1="0" y1="{p50}" x2="100" y2="{p50}" vector-effect="non-scaling-stroke"/>' if p50 is not None else ''}
    <path class="ln" d="{e(c.get("d",""))}" clip-path="url(#rv{i})" vector-effect="non-scaling-stroke"/></svg>
   {habl}<span class="dot" id="dt{i}" style="top:{tdy}%"></span><span class="ring" id="rg{i}" style="top:{tdy}%"></span>
   <div class="xl"><span>{e((c.get("x") or ["",""])[0])}</span><span>{e((c.get("x") or ["",""])[-1])}</span></div>
  </div>
 </div>
</div>'''
    css=f'''<style>
:root{{--page:#F6F8FA;--night:#10243B;--night2:#0F4F8A;--mint:#8FE3C4;--lime:#E4FB6A;--limeink:#2A3A00;--onDark:#DCEAF8;--muted:#8FA3BC;--brand:#1378C4;--green:#117a5b}}
*{{box-sizing:border-box}}body{{margin:0}}
.art{{position:relative;width:1080px;height:1920px;overflow:hidden;background:radial-gradient(900px 600px at 80% 20%,#E7F1FB 0%,transparent 60%),var(--page);font-family:Inter,'Inter Tight',system-ui,sans-serif;color:var(--night)}}
.it{{position:absolute;left:0;top:0;transform-origin:50% 50%}}
.kick{{font:800 26px/1 'JetBrains Mono',monospace;letter-spacing:.14em;text-transform:uppercase}}
.tabs{{display:flex;gap:10px;width:{CW}px}}
.tab{{flex:1;text-align:center;font:800 24px/1 Inter;padding:16px 6px;border-radius:14px 14px 0 0;background:#fff;color:var(--night);border:2px solid #D5DEE8;border-bottom:0;white-space:nowrap}}
.tab.on{{background:var(--night);color:#fff;border-color:var(--night)}}
.card{{width:{CW}px;height:1050px;border-radius:0 0 34px 34px;overflow:visible;box-shadow:0 2px 4px rgba(16,36,59,.06),0 40px 80px -40px rgba(16,36,59,.55)}}
.stage{{height:420px;background:#fff;border:2px solid var(--night);border-bottom:0;display:flex;align-items:center;justify-content:center;overflow:hidden}}
.stage img{{height:380px;max-width:92%;object-fit:contain;transform-origin:50% 60%}}
.tag{{position:absolute;left:30px;top:396px;font:800 22px/1 'JetBrains Mono',monospace;letter-spacing:.12em;padding:12px 20px;border-radius:99px;z-index:3}}
.tag.day{{background:var(--lime);color:var(--limeink);border:3px solid var(--night)}}
.tag.seal{{background:var(--night);color:var(--mint);border:3px solid #fff;box-shadow:0 0 0 2px var(--night)}}
.body{{height:630px;background:var(--night);border-radius:0 0 34px 34px;padding:46px 44px 34px;color:#fff;position:relative;display:flex;flex-direction:column}}
.card.day .body{{background:#0E3F6E}}
.name{{font:800 44px/1.08 Inter;letter-spacing:-.01em}}
.attrs{{margin-top:12px;font:600 26px Inter;color:var(--onDark)}}
.rule{{height:2px;background:rgba(255,255,255,.18);margin:18px 0 10px;flex:none}}
.pct{{font:900 118px/1 Inter;color:var(--mint);letter-spacing:-.03em;transform-origin:0 60%}}
.vs{{margin-top:6px;font:500 27px/1.3 Inter;color:var(--onDark)}}
.price{{margin-top:8px;display:flex;align-items:baseline;gap:14px}}
.now{{font:900 64px/1 Inter;color:#fff;letter-spacing:-.02em}}
.store{{font:500 26px Inter;color:var(--onDark)}}.store b{{color:#fff}}
.chart{{position:relative;flex:1;min-height:110px;margin:30px 0 40px}}
.chart svg{{position:absolute;inset:0;width:100%;height:100%;overflow:visible}}
.band{{fill:rgba(255,255,255,.10)}}
.p50{{stroke:rgba(255,255,255,.55);stroke-width:3;stroke-dasharray:9 8}}
.ln{{fill:none;stroke:#fff;stroke-width:6;stroke-linecap:round;stroke-linejoin:round}}
.dot{{position:absolute;left:100%;width:30px;height:30px;margin:-15px 0 0 -15px;border-radius:50%;background:var(--mint);box-shadow:0 0 0 5px var(--night)}}
.ring{{position:absolute;left:100%;width:30px;height:30px;margin:-15px 0 0 -15px;border-radius:50%;border:4px solid var(--mint)}}
.habl{{position:absolute;left:0;transform:translateY(40%);font:700 20px 'JetBrains Mono',monospace;letter-spacing:.06em;color:rgba(255,255,255,.7);text-transform:uppercase}}
.xl{{position:absolute;left:0;right:0;bottom:-44px;display:flex;justify-content:space-between;font:600 22px Inter;color:var(--muted)}}
.hero{{width:{CW}px}}
.big{{font:900 230px/0.9 Inter;letter-spacing:-.04em}}
.cta{{display:inline-flex;align-items:center;gap:16px;background:#fff;color:var(--night);border-radius:99px;padding:22px 40px 22px 30px;font:800 42px Inter;box-shadow:0 18px 34px -16px rgba(0,0,0,.5)}}
.cta i{{font-style:normal;color:#5f6674;font-weight:600}}
.rc{{width:180px;text-align:center}}.rci{{height:200px;background:#fff;border-radius:18px;display:flex;align-items:center;justify-content:center;overflow:hidden}}.rci img{{height:180px;max-width:90%;object-fit:contain}}.rcp{{margin-top:12px;font:900 44px/1 Inter;color:var(--mint)}}.rcr{{margin-top:6px;font:700 20px Inter;color:var(--onDark);white-space:nowrap}}
.dark{{position:absolute;inset:0;background:radial-gradient(900px 700px at 85% 35%,#1A6FBF 0%,transparent 60%),linear-gradient(170deg,#08213D 0%,#0D3F72 65%,#11589E 100%)}}
</style>'''
    body=f'''<div class="art">
<div class="dark" id="dk"></div>
<img class="it" id="lg" data-x="196" data-y="330" src="{A("logo-navy.svg")}" style="width:200px">
<img class="it" id="lgw" data-x="196" data-y="330" src="{A("logo-blanco.svg")}" style="width:200px">
<div class="it" id="h0" data-x="{CX+30}" data-y="470"><div class="kick" style="width:{CW}px;color:var(--brand)">Ofertas de hoy · {e(hoy)}</div></div>
<div class="it" id="h1" data-x="{CX+30}" data-y="590"><div style="width:{CW}px;font:900 92px/1 Inter;letter-spacing:-.02em">¿Buscas pala?</div></div>
<div class="it" id="h2" data-x="{CX+30}" data-y="700"><div style="width:{CW}px;font:900 92px/1 Inter;letter-spacing:-.02em;color:var(--green)">Hoy, hasta</div></div>
<div class="it" id="h3" data-x="{CX}" data-y="940"><div style="background:var(--night);border-radius:40px;padding:30px 54px 40px;box-shadow:0 40px 80px -40px rgba(16,36,59,.7)"><div class="big" style="color:var(--mint)">−<span id="hv">0</span> %</div></div></div>
<div class="it" id="h4" data-x="{CX+30}" data-y="1180"><div style="width:{CW}px;font:600 38px/1.3 Inter;color:#374151">{n} palas, una por presupuesto. Comparadas con su propio historial, no con el precio tachado.</div></div>
<div class="it" id="tb" data-x="{CX}" data-y="372"><div class="tabs">{tabs}</div></div>
{''.join(f'<div class="it" id="cw{i}" data-x="{CX}" data-y="{405+550}">'+cards.split('<div class="card" id="cd')[i+1].join(['<div class="card'+(' day' if of[i].get('dia') else '')+'" id="cd',''])+'</div>' for i in range(n)) if False else ''}
'''
    # tarjetas envueltas para animarlas
    parts=cards.split('<div class="card" id="cd')[1:]
    for i,pt in enumerate(parts):
        body+=f'<div class="it" id="cw{i}" data-x="{CX}" data-y="930"><div class="card{" day" if of[i].get("dia") else ""}" id="cd{pt}</div>'
    body+=f'''
<div class="it" id="c1" data-x="{CX+30}" data-y="600"><div style="width:{CW}px;font:900 130px/0.95 Inter;letter-spacing:-.03em;color:#fff">¿Cuál te<br><span style="color:var(--lime)">llevas?</span></div></div>
<div class="it" id="c2" data-x="{CX+30}" data-y="860"><div style="width:{CW}px;font:600 40px/1.3 Inter;color:var(--onDark)">Dínoslo en comentarios.{f" Hoy hay {total} palas por debajo de su precio habitual." if total else ""}</div></div>
<div class="it" id="c4" data-x="{CX}" data-y="1150"><div style="display:flex;gap:14px;width:{CW}px;justify-content:center">{''.join(f'<div class="rc" id="rc{i}"><div class="rci"><img src="{e("file://"+o["foto_abs"]) if o.get("foto_abs") else e(o["img"])}"></div><div class="rcp">{e(o["pct"])}</div><div class="rcr">{e(o["rango"])}</div></div>' for i,o in enumerate(of))}</div></div>
<div class="it" id="c3" data-x="{CX-20}" data-y="1400"><div class="cta"><svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#6b7686" stroke-width="2.4" stroke-linecap="round"><rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/></svg>tupala.es<i>/precios/ofertas</i></div></div>
</div>'''
    tl=[]
    for i,o in enumerate(of):
        hab=re.search(r'habitual de ([\d.]+)',(o.get('vs') or '').replace(' ',' '))
        tl.append(dict(pct=pcts[i],now=num(o['precio']),hab=int(hab.group(1).replace('.','')) if hab else num(o['precio']),now_s=o['precio']))
    END=HOOK+n*BEAT+CLOSE
    js=r'''<script>
const E={o:x=>x,expo:x=>x>=1?1:1-Math.pow(2,-10*x),io:x=>x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2,out:x=>1-Math.pow(1-x,3),
 back:x=>{const c=1.7;return 1+(c+1)*Math.pow(x-1,3)+c*Math.pow(x-1,2)}};
const D={o:1,x:0,y:0,s:1,r:0,b:0};
function K(id,t,fr){const el=document.getElementById(id); if(!el) return; let v={...D,...fr[0][1]};
 for(let i=0;i<fr.length-1;i++){const [t0,a]=fr[i],[t1,b,ease]=fr[i+1]; if(t>=t1){v={...v,...b};continue}
  if(t>t0){const k=(E[ease||'expo'])((t-t0)/(t1-t0)); const A={...v},B={...v,...b}; for(const p in B){v[p]=A[p]+(B[p]-A[p])*k}} break;}
 el.style.opacity=Math.max(0,Math.min(1,v.o));
 const bx=el.dataset.x!==undefined?+el.dataset.x:0, by=el.dataset.y!==undefined?+el.dataset.y:0, ctr=el.dataset.x!==undefined;
 el.style.transform=(ctr?`translate(${bx+v.x}px,${by+v.y}px) translate(-50%,-50%) `:`translate(${v.x}px,${v.y}px) `)+`rotate(${v.r}deg) scale(${v.s})`;
 el.style.filter=v.b>.2?`blur(${v.b}px)`:'none';}
const cl=v=>Math.max(0,Math.min(1,v));
function pop(t,T,a){const u=t-T; if(u<0||u>1) return 1; return 1+a*Math.sin(Math.min(u*14,Math.PI))*Math.exp(-u*6)}
const TL=__TL__,HOOK=__HOOK__,BEAT=__BEAT__,END=__END__,TOP=__TOP__,N=TL.length;
const eur=v=>v.toFixed(2).replace('.',',')+' €';
window.render=function(t){
 let sh=0;
 // GANCHO
 const ho=HOOK-.3;
 K('lg',t,[[0,{o:0}],[.3,{o:1}],[ho,{}],[ho+.3,{o:0}]]);
 K('h0',t,[[.05,{o:0,y:30}],[.4,{o:1,y:0}],[ho,{}],[ho+.3,{o:0,y:-80},'io']]);
 K('h1',t,[[.15,{o:0,y:60}],[.55,{o:1,y:0}],[ho,{}],[ho+.3,{o:0,y:-80},'io']]);
 K('h2',t,[[.35,{o:0,y:60}],[.75,{o:1,y:0}],[ho,{}],[ho+.3,{o:0,y:-80},'io']]);
 K('h3',t,[[.55,{o:0,s:.4,r:-6}],[.95,{o:1,s:1,r:-2},'back'],[ho,{}],[ho+.35,{o:0,s:.7,y:-200},'io']]);
 document.getElementById('hv').textContent=Math.round(TOP*E.out(cl((t-.6)/.9)));
 { const u=t-1.5; if(u>0&&u<.4) sh=Math.max(sh,Math.exp(-u*9)); }
 K('h4',t,[[1.0,{o:0,y:30}],[1.4,{o:1,y:0}],[ho,{}],[ho+.3,{o:0,y:-60},'io']]);
 // PESTAÑAS (progreso por rango)
 K('tb',t,[[1.3,{o:0,y:1000}],[1.7,{o:1,y:960}],[HOOK-.3,{}],[HOOK+.15,{y:0},'io'],[END-__CLOSE__,{}],[END-__CLOSE__+.3,{o:0,y:-40},'io']]);
 const act=Math.floor((t-HOOK)/BEAT);
 for(let i=0;i<N;i++){const tb=document.getElementById('tab'+i); if(tb) tb.classList.toggle('on',t>=HOOK-.05&&i===Math.max(0,Math.min(N-1,act)));}
 // TARJETAS
 for(let i=0;i<N;i++){const s=TL[i],T=HOOK+i*BEAT,X=T+BEAT-.4,last=i===N-1;
  const ent=i===0?{o:0,y:500}:{o:0,x:900,r:8};
  const ex=last?{s:1.04,o:0}:{o:0,x:-900,r:-8};
  K('cw'+i,t,[[T-.45,ent],[T+.05,{o:1,x:0,y:0,r:0}],[X,{}],[X+.4,ex,'io']]);
  K('im'+i,t,[[T,{s:.86}],[T+BEAT,{s:1.0},'o']]);
  K('nm'+i,t,[[T+.05,{o:0,y:24}],[T+.4,{o:1,y:0}]]);
  K('at'+i,t,[[T+.15,{o:0,y:20}],[T+.5,{o:1,y:0}]]);
  K('tg'+i,t,[[T+.35,{o:0,s:.3,r:-12}],[T+.65,{o:1,s:1,r:-3},'back']]);
  K('pc'+i,t,[[T+.3,{o:0,y:30}],[T+.6,{o:1,y:0}]]);
  const kp=E.out(cl((t-(T+.35))/.9)); document.getElementById('pv'+i).textContent=Math.round(s.pct*kp);
  document.getElementById('pc'+i).style.scale=String(pop(t,T+1.25,.18));
  { const u=t-(T+1.25); if(u>0&&u<.35) sh=Math.max(sh,Math.exp(-u*10)*.8); }
  K('vs'+i,t,[[T+.5,{o:0,y:20}],[T+.85,{o:1,y:0}]]);
  K('pr'+i,t,[[T+.6,{o:0,y:20}],[T+.95,{o:1,y:0}]]);
  const kn=E.out(cl((t-(T+.65))/1.0)); document.getElementById('nw'+i).textContent= kn>=1?s.now_s.replace(/\s/g,' '):Math.round(s.hab+(s.now-s.hab)*kn)+' €';
  K('ch'+i,t,[[T+.7,{o:0}],[T+.95,{o:1}]]);
  const rr=document.getElementById('rr'+i); rr.setAttribute('width',(100*E.io(cl((t-(T+.9))/1.4))).toFixed(2));
  const dk=cl((t-(T+2.25))/.35); const dt=document.getElementById('dt'+i); dt.style.opacity=dk; dt.style.scale=String(E.back(dk)||0.001);
  const rg=document.getElementById('rg'+i); const ru=((t-(T+2.4))%1.1+1.1)%1.1; const rOn=t>T+2.4;
  rg.style.opacity=rOn?(1-ru/1.1)*.9:0; rg.style.scale=String(1+ru*1.6);
 }
 // CIERRE: fondo oscuro de la web
 const C=END-__CLOSE__;
 K('dk',t,[[C-.15,{o:0}],[C+.35,{o:1}]]);
 K('lgw',t,[[C+.1,{o:0}],[C+.4,{o:1}]]);
 K('c1',t,[[C+.2,{o:0,y:70}],[C+.65,{o:1,y:0}]]);
 K('c2',t,[[C+.6,{o:0,y:30}],[C+1.0,{o:1,y:0}]]);
 K('c3',t,[[C+1.3,{o:0,y:40,s:.9}],[C+1.7,{o:1,y:0,s:1},'back']]);
 K('c4',t,[[C+.5,{o:1}]]); for(let i=0;i<N;i++) K('rc'+i,t,[[C+.55+i*.12,{o:0,y:60,s:.8}],[C+.9+i*.12,{o:1,y:0,s:1},'back']]);
 document.querySelector('.art').style.translate=sh>.03?`${(Math.sin(t*95)*12*sh).toFixed(1)}px ${(Math.cos(t*80)*7*sh).toFixed(1)}px`:'0 0';
};
window.render(0);
</script>'''
    for k,v in {'__TL__':json.dumps(tl,ensure_ascii=False),'__HOOK__':str(HOOK),'__BEAT__':str(BEAT),'__END__':str(END),'__TOP__':str(top),'__CLOSE__':str(CLOSE)}.items(): js=js.replace(k,v)
    fonts='<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@500;600;700;800;900&family=JetBrains+Mono:wght@600;700;800&display=swap">'
    return f'<!doctype html><html><head><meta charset="utf-8">{fonts}{css}</head><body>{body}{js}</body></html>',END
def textos(data,fecha):
    of=data['ofertas'][:4]; total=data.get('total')
    pcts=[int(re.sub(r'\D','',o['pct']) or 0) for o in of]; top=max(pcts) if pcts else 0
    lis='\n'.join(f'{o["rango"]}: {o["nombre"]}, {o["precio"]} en {o["tienda"]} ({o["pct"]}).' for o in of)
    ig=(f'¿Buscas pala? Hoy hay bajadas de hasta −{top} %.\n\n'
        f'Una por presupuesto, comparada con lo que esa pala cuesta normalmente:\n\n{lis}\n\n'
        f'¿Cuál te llevas? Te leemos en comentarios.\n\n'
        f'{"Hoy hay "+str(total)+" palas por debajo de su precio habitual, y los precios cambian cada día. " if total else "Los precios cambian cada día. "}'
        'Míralas en tupala.es/precios/ofertas (link en la bio).\n\n#padel #padelespaña #palasdepadel #ofertaspadel #tupala')
    tt=(f'Título: Hoy, palas de pádel hasta −{top} %\n\nDescripción: Una oferta por presupuesto, comparada con su propio historial. '
        '¿Cuál te llevas? Búscalas en tupala.es 🎾\n\n#padel #padeltok #padelespaña #palasdepadel #ofertaspadel')
    return {'instagram_facebook':ig,'tiktok':tt}
if __name__=='__main__':
    d=sys.argv[1]; out=sys.argv[2]; mode=sys.argv[3] if len(sys.argv)>3 else 'video'
    data=json.load(open(os.path.join(d,'ofertas.json')))
    if not data.get('ofertas'): sys.exit('Sin ofertas')
    fecha=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=1))).date()
    html,END=build(data,fecha)
    hp=os.path.join(d,'reel.html'); open(hp,'w').write(html)
    json.dump(textos(data,fecha),open(os.path.join(d,'textos.json'),'w'),ensure_ascii=False,indent=1)
    with sync_playwright() as p:
        b=p.chromium.launch(); pg=b.new_page(viewport={'width':1080,'height':1920})
        pg.goto('file://'+os.path.abspath(hp),wait_until='networkidle'); pg.wait_for_timeout(1500)
        if mode=='stills':
            ts=[1.7,HOOK+.3]+[HOOK+i*BEAT+t for i in range(len(data['ofertas'][:4])) for t in (1.3,3.2)]+[END-.2]
            for t in ts: pg.evaluate(f'render({t})'); pg.screenshot(path=os.path.join(d,f'still{t:05.2f}.png'))
        else:
            tmp=out[:-4]+'.part.mp4'
            ff=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','image2pipe','-framerate',str(FPS),'-c:v','mjpeg','-i','-',
                '-c:v','libx264','-pix_fmt','yuv420p','-crf','19','-preset','medium','-movflags','+faststart',tmp],stdin=subprocess.PIPE)
            for i in range(int((END+.2)*FPS)):
                pg.evaluate(f'render({i/FPS})'); ff.stdin.write(pg.screenshot(type='jpeg',quality=92))
            ff.stdin.close()
            if ff.wait()!=0: sys.exit('ffmpeg falló')
            os.replace(tmp,out); print(out,round(END+.2,1),'s')
        b.close()
