"""Native service-uniform extension of the ordinary goon, six objects per pose."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageOps
import json,copy,hashlib,uuid
R=Path(__file__).resolve().parents[1]
uid=lambda s:str(uuid.uuid5(uuid.NAMESPACE_URL,'kittie-head-goon/'+s))
T,L,M,D='#65ff00','#e0f8cf','#86c06c','#071821'
frames=[]
for hp in [3,2,1]:
 for pose in range(7):
  im=Image.new('RGB',(24,32),T);d=ImageDraw.Draw(im)
  # Enlarge the actual garden goon's cloth body, paired ear points, eyes and feet.
  d.rounded_rectangle((4,4,22,29),radius=7,fill=D)
  d.rounded_rectangle((5,5,21,28),radius=6,fill=M)
  d.polygon([(3,5),(6,0),(9,5)],fill=D)
  d.polygon([(16,5),(20,0),(23,5)],fill=D)
  d.polygon([(5,5),(6,3),(7,5)],fill=M)
  d.polygon([(18,5),(20,3),(21,5)],fill=M)
  d.rectangle((7,28,11,31 if pose!=1 else 30),fill=D)
  d.rectangle((16,28,20,30 if pose!=1 else 31),fill=D)
  d.rectangle((8,9,11,13),fill=L);d.rectangle((16,9,19,13),fill=L)
  if pose==4:
   d.line((8,11,11,12),fill=D);d.line((16,12,19,11),fill=D)
  else:
   d.point((9,11),fill=D);d.point((17,11),fill=D)
  d.line((10,18,17,18),fill=D);d.point((9,17),fill=D);d.point((18,17),fill=D)
  # The small bow and three dimming fasteners distinguish his rank, not a coat.
  d.polygon([(10,21),(13,23),(10,24)],fill=D)
  d.polygon([(17,21),(14,23),(17,24)],fill=D);d.point((13,23),fill=L)
  for j in range(3):d.point((10+j*4,26),fill=L if j<hp else D)
  if pose==3:
   d.rectangle((0,26,9,29),fill=D);d.line((1,26,8,26),fill=L);d.line((4,20,5,25),fill=D)
  elif pose==4:
   d.polygon([(0,17),(3,14),(9,26),(6,29)],fill=D);d.line((2,17,7,26),fill=L)
  else:
   d.rounded_rectangle((0,11,5,28),radius=2,fill=D);d.rectangle((1,13,3,25),fill=L);d.point((2,27),fill=M)
   d.line((5,20,7,20),fill=D)
  if pose==5:
   # A compressed body and upright tray are a wind-up, never an opening.
   im=Image.new('RGB',(24,32),T);d=ImageDraw.Draw(im)
   d.rounded_rectangle((4,9,22,29),radius=6,fill=D);d.rounded_rectangle((5,10,21,28),radius=5,fill=M)
   d.polygon([(3,11),(6,5),(9,11)],fill=D);d.polygon([(16,11),(20,5),(23,11)],fill=D)
   d.rectangle((8,14,11,17),fill=L);d.rectangle((16,14,19,17),fill=L)
   d.point((9,16),fill=D);d.point((17,16),fill=D);d.line((10,22,17,22),fill=D)
   d.rectangle((7,29,11,31),fill=D);d.rectangle((16,29,20,31),fill=D)
   d.rounded_rectangle((0,14,5,28),radius=2,fill=D);d.rectangle((1,16,3,25),fill=L)
   for j in range(3):d.point((10+j*4,26),fill=L if j<hp else D)
  elif pose==6:
   # Tucked feet and the raised tray keep airborne commitment distinct.
   d.rectangle((5,28,22,31),fill=T);d.rectangle((8,28,12,29),fill=D);d.rectangle((16,27,20,28),fill=D)
  frames.append(im)
im=Image.new('RGB',(24,32),T);d=ImageDraw.Draw(im)
d.rounded_rectangle((4,13,22,29),radius=6,fill=D);d.rounded_rectangle((5,14,21,28),radius=5,fill=M)
d.polygon([(3,15),(6,9),(9,15)],fill=D);d.polygon([(16,15),(20,9),(23,15)],fill=D)
d.line((8,19,11,20),fill=D);d.line((16,20,19,19),fill=D);d.line((10,24,17,24),fill=D)
d.rectangle((7,29,11,31),fill=D);d.rectangle((16,29,20,31),fill=D)
d.polygon([(0,21),(3,19),(9,28),(6,30)],fill=D);d.line((2,21,7,28),fill=L)
frames.append(im)
sheet=Image.new('RGB',(24*22,32),T)
for i,im in enumerate(frames):sheet.paste(im,(i*24,0))
p=R/'assets/sprites/head_goon.png';sheet.save(p)
m=json.loads((R/'assets/sprites/goon.png.gbsres').read_text());m.update(id=uid('sprite'),name='Head Goon',symbol='sprite_head_goon',filename=p.name,width=528,height=32,canvasWidth=24,canvasHeight=32,numTiles=264,boundsWidth=24,boundsHeight=32,animSpeed=255,checksum=hashlib.sha1(p.read_bytes()).hexdigest())
state=m['states'][0];state.update(id=uid('state'),animationType='fixed',flipLeft=False)
# Explicit directional frames avoid hidden extra sprite columns during mirroring.
for a,anim in enumerate(state['animations']):
 anim['id']=uid(f'anim{a}');anim['frames']=[]
 for f in range(22):
  anim['frames'].append(dict(id=uid(f'f{a}/{f}'),tiles=[dict(id=uid(f't{a}/{f}/{x}/{y}'),x=x-4,y=16-y,sliceX=f*24+x,sliceY=y,flipX=False,flipY=False,palette=0,paletteIndex=2,objPalette='OBP0',priority=False) for y in (0,16) for x in (0,8,16)]))
# Use engine's left/right mirroring with a left-facing source and a right-facing
# animation derived by tile flip and reversed column coordinates.
state['animationType']='multi';state['flipLeft']=False
# GB Studio source ordering: right, left, up, down, then moving equivalents.
for a in (0,4):
 for f in state['animations'][a]['frames']:
  for t in f['tiles']:t['x']=8-t['x'];t['flipX']=True
p.with_suffix('.png.gbsres').write_text(json.dumps(m,indent=2)+'\n')
(R/'source-art/head-goon-contact.png').parent.mkdir(exist_ok=True)
sheet.resize((2112,128),Image.Resampling.NEAREST).save(R/'source-art/head-goon-contact.png')
# Quiet service passage. The marked rail stays clear of the patrol silhouette.
C=[L,M,'#306850',D];im=Image.new('RGB',(480,144),L);d=ImageDraw.Draw(im)
d.rectangle((0,128,479,143),fill=M);d.line((0,128,479,128),fill=D)
for x in range(0,480,16):d.line((x,136,x+14,136),fill=C[2]);d.line((x+8,129,x+8,135),fill=C[2])
d.line((0,48,479,48),fill=M)
for x in [24,88,352,416]:
 d.rounded_rectangle((x,56,x+31,104),radius=12,fill=M);d.rounded_rectangle((x+3,60,x+28,100),radius=10,fill=L);d.line((x+15,61,x+15,100),fill=M)
for x in [152,328]:d.rectangle((x,24,x+7,127),fill=M);d.line((x+1,24,x+6,24),fill=C[2])
# A single formal doorway frames the arena. No rule text on the world.
d.rectangle((216,40,303,47),fill=M);d.line((220,42,299,42),fill=L)

# Repeated, distinct gate tiles allow independent native tile-data changes.
# Each gate reaches the ceiling so a high lob stays recoverable inside.
for gx,bars in [(160,(1,4)),(320,(1,5))]:
 for y in range(0,128,8):
  d.rectangle((gx,y,gx+7,y+7),fill=L)
  for xx in bars:d.line((gx+xx,y,gx+xx,y+7),fill=D)
  d.line((gx+1,y+3,gx+5,y+3),fill=M)
im.save(R/'assets/backgrounds/head_goon.png')
paint=[dict(x=0,y=0,width=60,height=18,slot=0),dict(x=0,y=16,width=60,height=2,slot=3)]
(R/'tools/head-goon-palettes.json').write_text(json.dumps(paint)+'\n')
# A three-object floor marker remains below the airborne/body/HUD scanlines.
marker=Image.new('RGB',(48,16),T)
for f in range(2):
 q=ImageDraw.Draw(marker);x=f*24
 q.line([(x+2,1),(x+6,4),(x+2,7)],fill=D)
 q.line([(x+21,1),(x+17,4),(x+21,7)],fill=D)
 q.line((x+8,6,x+15,6),fill=L if f else M)
 if f:q.line((x+10,3,x+13,3),fill=D)
p=R/'assets/sprites/head_goon_target.png';marker.save(p)
m=json.loads((R/'assets/sprites/ball.png.gbsres').read_text());m.update(id=uid('target-sprite'),name='Hop landing cue',symbol='sprite_head_goon_target',filename=p.name,width=48,height=16,canvasWidth=24,canvasHeight=16,numTiles=12,checksum=hashlib.sha1(p.read_bytes()).hexdigest(),animSpeed=255)
state=m['states'][0];state.update(id=uid('target-state'),animationType='fixed',flipLeft=False)
for a,anim in enumerate(state['animations']):
 anim['id']=uid(f'target-anim{a}');anim['frames']=[]
 for f in range(2):anim['frames'].append(dict(id=uid(f'target-frame{a}/{f}'),tiles=[dict(id=uid(f'target-tile{a}/{f}/{x}'),x=x-4,y=0,sliceX=f*24+x,sliceY=0,flipX=False,flipY=False,palette=0,paletteIndex=3,objPalette='OBP0',priority=False) for x in (0,8,16)]))
p.with_suffix('.png.gbsres').write_text(json.dumps(m,indent=2)+'\n')
p=R/'project/scenes/head_goon/actors/terrace_goon.gbsres';a=json.loads(p.read_text());a.update(name='Hop landing cue',spriteSheetId=m['id']);p.write_text(json.dumps(a,indent=2)+'\n')
print('Head Goon: 22 poses, flat floor, one landing marker.')
