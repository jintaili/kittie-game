"""Small native wool ball, count displays and the banquet's entry shutter."""
from pathlib import Path
from PIL import Image, ImageDraw
import json, copy, uuid, hashlib, sys
ROOT=Path(__file__).resolve().parents[1]
T,L,M,D='#65ff00','#e0f8cf','#86c06c','#071821'
# UUID seeds retain the original asset key so regeneration preserves native IDs.
def uid(s):
 if s=='ball' or s.startswith('ball-'):s='wool'+s[4:]
 return str(uuid.uuid5(uuid.NAMESPACE_URL,'kittie-carry-'+s))
template=json.loads((ROOT/'assets/sprites/ball.png.gbsres').read_text())
for name,w,h,count,slot in [('ball',16,16,1,1),('hearts',24,16,4,4),('inventory',24,16,4,4),('entry_shutter',8,128,1,0)]:
 if sys.argv[1:] and name not in sys.argv[1:]: continue
 sheet=Image.new('RGB',(w*count,h),T)
 for f in range(count):
  im=Image.new('RGB',(w,h),T);d=ImageDraw.Draw(im)
  if name=='ball':
   # Keep the visible ball fixed via metadata y+4. Empty OAM padding belongs
   # above the ball, so a resting ball never consumes its support deck's rows.
   d.ellipse((4,8,11,15),fill=D);d.ellipse((5,9,10,14),fill=M)
   d.line([(5,11),(8,9),(10,11)],fill=L);d.line([(5,13),(8,11),(10,13)],fill=L);d.point((8,14),fill=D)
  elif name=='entry_shutter':
   d.rectangle((2,0,3,127),fill=D);d.rectangle((6,0,7,127),fill=D)
   for y in range(4,128,16):d.line((2,y,7,y),fill=M,width=2)
  else:
   # A dark backing and cream empty outlines stay legible over every backdrop.
   d.rounded_rectangle((0,1,23,12),radius=2,fill=D)
   for n in range(3):
    x=n*8;fill=L if n<f else D;edge=M
    if name=='hearts':
     d.polygon([(x,5),(x+1,3),(x+3,3),(x+4,5),(x+5,3),(x+6,3),(x+7,5),(x+7,7),(x+4,10),(x,7)],fill=fill,outline=edge)
     if n<f:d.line((x+2,5,x+3,5),fill=M)
    else:
     d.ellipse((x,3,x+7,10),fill=fill,outline=edge)
     if n<f:d.line([(x+1,6),(x+4,4),(x+6,6),(x+2,8),(x+5,9)],fill=M)
  sheet.paste(im,(f*w,0))
 dest=ROOT/f'assets/sprites/{name}.png';sheet.save(dest)
 m=copy.deepcopy(template);m.update(id=template['id'] if name=='ball' else uid(name),name='Wool ball' if name=='ball' else name,filename=f'{name}.png',symbol='sprite_'+name,width=w*count,height=h,canvasWidth=w,canvasHeight=h,numTiles=(w//8)*(h//16)*count,checksum=hashlib.sha1(dest.read_bytes()).hexdigest())
 for a,anim in enumerate(m['states'][0]['animations']):
  anim['id']=uid(f'{name}-anim-{a}');anim['frames']=[]
  for f in range(count):
   tiles=[]
   for y in range(0,h,16):
    for x in ([4] if name=='ball' else range(0,w,8)):
     tiles.append(dict(id=uid(f'{name}-{a}-{f}-{x}-{y}'),x=x,y=4 if name=='ball' else -y,sliceX=f*w+x,sliceY=y,flipX=False,flipY=False,palette=0,paletteIndex=slot,objPalette='OBP0',priority=False))
   anim['frames'].append(dict(id=uid(f'{name}-{a}-{f}'),tiles=tiles))
 m['states'][0]['id']=uid(name+'-state')
 dest.with_suffix('.png.gbsres').write_text(json.dumps(m,indent=2)+'\n')
 print(name,m['id'])
