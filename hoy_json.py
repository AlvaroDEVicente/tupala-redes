"""Une ofertas.json y textos.json en el hoy.json que lee la página «Historias del día»."""
import json, sys, os, datetime
d=sys.argv[1]; out=sys.argv[2]
of=json.load(open(os.path.join(d,'ofertas.json')))
tx=json.load(open(os.path.join(d,'textos.json')))
fecha=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=1))).date().isoformat()
json.dump({'fecha':fecha,'total':of.get('total'),'ofertas':[{k:o[k] for k in ('nombre','precio','tienda','pct','vs','dia','url','rango')} for o in of['ofertas'][:4]],'historias':sorted(f for f in os.listdir(os.path.dirname(out) or '.') if f.startswith('historia-') and f.endswith('.mp4')),'textos':tx},open(out,'w'),ensure_ascii=False,indent=1)
print(out)
