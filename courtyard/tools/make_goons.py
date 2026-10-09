"""Native 16px garden goon poses and wedding ribbon, kept editable as pixels."""
from pathlib import Path
from PIL import Image, ImageDraw
import json, uuid, hashlib, copy
ROOT=Path(__file__).resolve().parents[1]
T,L,M,D='#65ff00','#e0f8cf','#86c06c','#071821'
uid=lambda s:str(uuid.uuid5(uuid.NAMESPACE_URL,'kittie-'+s))
template=json.loads((ROOT/'assets/sprites/ball.png.gbsres').read_text())
for name,count in [('goon',4),('ribbon',1)]:
    sheet=Image.new('RGB',(16*count,16),T)
    for f in range(count):
        im=Image.new('RGB',(16,16),T); d=ImageDraw.Draw(im)
        if name=='goon':
            # Round cloth garden pest; pale eyes make the charge tell readable.
            y=3 if f==2 else 2
            d.rounded_rectangle((2,y,13,13),radius=4,fill=D)
            d.rounded_rectangle((3,y+1,12,12),radius=3,fill=M)
            d.rectangle((3,13,6,15 if f!=1 else 14),fill=D)
            d.rectangle((9,13,12,14 if f!=1 else 15),fill=D)
            d.rectangle((4,6,6,8),fill=L); d.rectangle((9,6,11,8),fill=L)
            d.point((5,7),fill=D); d.point((10,7),fill=D)
            d.line((6,11,9,11),fill=D)
            d.polygon([(1,3),(3,0),(5,3)],fill=D)
            d.polygon([(10,3),(12,0),(14,3)],fill=D)
            if f==2:
                d.line((3,4,6,5),fill=D);d.line((9,5,12,4),fill=D)
            if f==3:
                d.line((4,6,6,8),fill=D);d.line((6,6,4,8),fill=D)
                d.line((9,6,11,8),fill=D);d.line((11,6,9,8),fill=D)
                d.line((1,1,1,4),fill=L);d.point((15,3),fill=L)
        else:
            d.polygon([(3,2),(8,5),(12,2),(13,8),(9,8),(11,14),(8,12),(5,14),(6,8),(2,8)],fill=D)
            d.polygon([(3,3),(7,6),(3,7)],fill=L); d.polygon([(12,3),(9,6),(12,7)],fill=L)
            d.rectangle((7,5,8,8),fill=M);d.line((7,9,6,12),fill=M);d.line((9,9,10,12),fill=L)
        sheet.paste(im,(16*f,0))
    dest=ROOT/f'assets/sprites/{name}.png';sheet.save(dest)
    m=copy.deepcopy(template);m.update(id=uid(name),name=name,filename=f'{name}.png',symbol=f'sprite_{name}',width=16*count,numTiles=4*count,checksum=hashlib.sha1(dest.read_bytes()).hexdigest())
    st=m['states'][0];st['id']=uid(name+'-state')
    for a,anim in enumerate(st['animations']):
        anim['id']=uid(f'{name}-anim-{a}');anim['frames']=[]
        for f in range(count):
            anim['frames'].append(dict(id=uid(f'{name}-frame-{a}-{f}'),tiles=[dict(id=uid(f'{name}-{a}-{f}-{x}'),x=x,y=0,sliceX=f*16+x,sliceY=0,flipX=False,flipY=False,palette=0,paletteIndex=2 if name=='goon' else 3,objPalette='OBP0',priority=False) for x in [0,8]]))
    dest.with_suffix('.png.gbsres').write_text(json.dumps(m,indent=2)+'\n')
    print(name,m['id'])
