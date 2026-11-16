"""Pinta encima de los fotogramas las zonas que tapan Instagram Reels y TikTok (valores típicos en 1080×1920).
«TikTok iPhone»: en pantallas altas TikTok recorta ~50 px por lado y la columna de botones se mide desde el borde visible."""
import sys, glob
from PIL import Image, ImageDraw, ImageFont
F=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',34)
Z={'Instagram':dict(top=211,bottom=461,right=173,rtop=900,lado=0,izq=65),
   'TikTok':dict(top=240,bottom=440,right=160,rtop=840,lado=0,izq=60),
   'TikTok-iPhone':dict(top=280,bottom=440,right=160,rtop=840,lado=50,izq=60)}
def tapa(src,red):
    z=Z[red]; im=Image.open(src).convert('RGBA'); ov=Image.new('RGBA',im.size,(0,0,0,0)); d=ImageDraw.Draw(ov); c=(255,0,80,110)
    L=z['lado']; R=1080-z['lado']
    if L: d.rectangle([0,0,L,1920],fill=(0,0,0,255)); d.rectangle([R,0,1080,1920],fill=(0,0,0,255))
    d.rectangle([L,0,R,z['top']],fill=c); d.rectangle([L,1920-z['bottom'],R,1920],fill=c)
    d.rectangle([R-z['right'],z['rtop'],R,1920-z['bottom']],fill=c)
    d.rectangle([L,z['top'],L+z['izq'],1920-z['bottom']],fill=(255,160,0,90))
    d.text((L+20,40),red,fill=(255,255,255,255),font=F)
    return Image.alpha_composite(im,ov).convert('RGB')
fs=sorted(glob.glob(sys.argv[1])); W,H=360,640
for red in Z:
    S=Image.new('RGB',(len(fs)*(W+10),H),'white')
    for k,f in enumerate(fs): S.paste(tapa(f,red).resize((W,H)),(k*(W+10),0))
    S.save(f'work/sim-{red}.png')
