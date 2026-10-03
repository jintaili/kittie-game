"""Small native wool, count displays and the banquet's entry shutter."""
from pathlib import Path
from PIL import Image, ImageDraw
import json, copy, uuid, hashlib
ROOT=Path(__file__).resolve().parents[1]
T,L,M,D='#65ff00','#e0f8cf','#86c06c','#071821'
uid=lambda s:str(uuid.uuid5(uuid.NAMESPACE_URL,'kittie-carry-'+s))
template=json.loads((ROOT/'assets/sprites/wool.png.gbsres').read_text())
for name,w,h,count,slot in [('wool',16,16,1,1),('hearts',24,16,4,1),('inventory',24,16,4,1),('entry_shutter',8,128,1,0)]:
 sheet=Image.new('RGB',(w*count,h),T)
 for f in range(count):
  im=Image.new('RGB',(w,h),T);d=ImageDraw.Draw(im)
  if name=='wool':
   d.ellipse((4,4,11,11),fill=D);d.ellipse((5,5,10,10),fill=M)
   d.line([(5,7),(8,5),(10,7)],fill=L);d.line([(5,9),(8,7),(10,9)],fill=L);d.point((8,10),fill=D)
  elif name=='entry_shutter':
   d.rectangle((2,0,3,127),fill=D);d.rectangle((6,0,7,127),fill=D)
   for y in range(4,128,16):d.line((2,y,7,y),fill=M,width=2)
  else:
   for n in range(3):
    x=n*8;fill=L if n<f else T;edge=D if n<f else M
    if name=='hearts':
     d.polygon([(x,5),(x+1,3),(x+3,3),(x+4,5),(x+5,3),(x+6,3),(x+7,5),(x+7,7),(x+4,10),(x,7)],fill=fill,outline=edge)
     if n<f:d.line((x+2,5,x+3,5),fill=M)
    else:
     d.ellipse((x,3,x+7,10),fill=fill,outline=edge)
     if n<f:d.line([(x+1,6),(x+4,4),(x+6,6),(x+2,8),(x+5,9)],fill=M)
  sheet.paste(im,(f*w,0))
 dest=ROOT/f'assets/sprites/{name}.png';sheet.save(dest)
 m=copy.deepcopy(template);m.update(id=template['id'] if name=='wool' else uid(name),name=name,filename=f'{name}.png',symbol='sprite_'+name,width=w*count,height=h,canvasWidth=w,canvasHeight=h,numTiles=(w//8)*(h//16)*count,checksum=hashlib.sha1(dest.read_bytes()).hexdigest())
 for a,anim in enumerate(m['states'][0]['animations']):
  anim['id']=uid(f'{name}-anim-{a}');anim['frames']=[]
  for f in range(count):
   tiles=[]
   for y in range(0,h,16):
    for x in ([4] if name=='wool' else range(0,w,8)):
     tiles.append(dict(id=uid(f'{name}-{a}-{f}-{x}-{y}'),x=x,y=-y,sliceX=f*w+x,sliceY=y,flipX=False,flipY=False,palette=0,paletteIndex=slot,objPalette='OBP0',priority=False))
   anim['frames'].append(dict(id=uid(f'{name}-{a}-{f}'),tiles=tiles))
 m['states'][0]['id']=uid(name+'-state')
 dest.with_suffix('.png.gbsres').write_text(json.dumps(m,indent=2)+'\n')
 print(name,m['id'])
