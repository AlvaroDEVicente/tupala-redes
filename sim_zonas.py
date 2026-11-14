"""Pinta encima de los fotogramas las zonas que tapan Instagram Reels y TikTok (valores típicos en 1080×1920)."""
import sys, glob
from PIL import Image, ImageDraw, ImageFont
F=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',34)
Z={'Instagram':dict(top=210,bottom=460,right=173,rtop=900),'TikTok':dict(top=240,bottom=440,right=160,rtop=840)}
def tapa(src,red):
    z=Z[red]; im=Image.open(src).convert('RGBA'); ov=Image.new('RGBA',im.size,(0,0,0,0)); d=ImageDraw.Draw(ov); c=(0,0,0,150)
    d.rectangle([0,0,1080,z['top']],fill=c); d.rectangle([0,1920-z['bottom'],1080,1920],fill=c)
    d.rectangle([1080-z['right'],z['rtop'],1080,1920-z['bottom']],fill=c)
    d.text((40,40),red,fill=(255,255,255,255),font=F)
    return Image.alpha_composite(im,ov).convert('RGB')
fs=sorted(glob.glob(sys.argv[1])); W,H=360,640
for red in Z:
    S=Image.new('RGB',(len(fs)*(W+10),H),'white')
    for k,f in enumerate(fs): S.paste(tapa(f,red).resize((W,H)),(k*(W+10),0))
    S.save(f'work/sim-{red}.png')
