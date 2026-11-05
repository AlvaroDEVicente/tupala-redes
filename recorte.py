# Recorte de fotos de tienda (fondo blanco): quita fondo, hueco de la garganta y correa.
import sys, numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage
def cut(src,dst,thr=236):
    im=Image.open(src).convert('RGB'); a=np.asarray(im).astype(int); mn=a.min(axis=2)
    white=mn>=thr; lab,n=ndimage.label(white)
    border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
    bg=np.isin(lab,list(border))
    body=~bg; ys,_=np.nonzero(body); top,bot=ys.min(),ys.max()
    inner=[i for i in range(1,n+1) if i not in border]
    keep=body.copy(); removed=[]
    if inner:
        sizes=ndimage.sum(white,lab,inner); cys=[c[0] for c in ndimage.center_of_mass(white,lab,inner)]
        med=np.median(sizes)
        for i,sz,cy in zip(inner,sizes,cys):
            if sz>4*med and 0.5<(cy-top)/(bot-top)<0.78: keep&=~(lab==i); removed.append(int(sz))
    keep=ndimage.binary_erosion(keep,iterations=2)   # fuera el halo claro del borde
    alpha=Image.fromarray((keep*255).astype('uint8')).filter(ImageFilter.GaussianBlur(1.1))
    out=im.convert('RGBA'); out.putalpha(alpha)
    out.crop(alpha.point(lambda v:255 if v>20 else 0).getbbox()).save(dst)
    return removed


def strip(p,ref=.80,start=.78,pad=10):
    a=np.array(Image.open(p)); h,w=a.shape[:2]
    op=np.nonzero(a[int(h*ref),:,3]>128)[0]
    # en la fila de referencia puede haber correa: quedarse con el tramo opaco más ancho contiguo al centro de la pala
    runs=np.split(op,np.nonzero(np.diff(op)>1)[0]+1); cx=w/2
    run=min(runs,key=lambda r: abs((r[0]+r[-1])/2-cx))
    x0,x1=run[0]-pad,run[-1]+pad
    a[int(h*start):,:max(x0,0),3]=0; a[int(h*start):,x1+1:,3]=0
    im=Image.fromarray(a); im.crop(im.getchannel('A').point(lambda v:255 if v>20 else 0).getbbox()).save(p)
    return x0,x1


def recortar(src,dst):
    cut(src,dst)
    try: strip(dst)
    except Exception: pass

def rellenar_mango(p, desde=.73):
    """Puños blancos sobre fondo blanco: el mango se pierde con el fondo. Se reconstruye con su anchura
    típica (≈13 % del ancho de la cabeza), centrado en lo que sí se detecta."""
    a=np.array(Image.open(p)); h,w=a.shape[:2]; al=a[:,:,3]>128
    anch=max((np.ptp(np.nonzero(al[r])[0]) for r in range(int(h*.5)) if al[r].any()),default=0)
    esp=int(anch*.135)
    filas=[r for r in range(int(h*desde),h) if al[r].any()]
    if not filas or esp<10: return
    cen=[ (np.nonzero(al[r])[0].min()+np.nonzero(al[r])[0].max())/2 for r in filas]
    if not any(np.ptp(np.nonzero(al[r])[0]) < esp*.8 for r in filas): return
    c=float(np.median(cen)); L=int(c-esp/2); R=int(c+esp/2)
    for r in filas:
        xs=np.nonzero(al[r])[0]
        if np.ptp(xs) > esp*1.4: continue          # todavía es la garganta
        gap=~al[r,L:R+1]; a[r,:,3]=0; a[r,L:R+1,3]=255; a[r,L:R+1,:3][gap]=[238,238,240]
    a[:,:,3]=np.array(Image.fromarray(a[:,:,3]).filter(ImageFilter.GaussianBlur(.8)))
    Image.fromarray(a).save(p)
def recortar(src,dst):
    cut(src,dst)
    try: strip(dst)
    except Exception: pass
    try: rellenar_mango(dst)
    except Exception: pass
