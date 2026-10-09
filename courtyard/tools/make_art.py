from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import json,uuid,hashlib
P=Path(__file__).resolve().parents[1]
C=['#e0f8cf','#86c06c','#306850','#071821'];T='#65ff00'
font=ImageFont.load_default(size=8)
im=Image.new('RGB',(480,144),C[0]);d=ImageDraw.Draw(im);d.fontmode='1'
# Rough, deliberately sparse blockout. Geometry matches the custom scene's rectangles.
d.rectangle((0,128,479,143),fill=C[2]);d.line((0,128,479,128),fill=C[3])
for x in range(0,480,16): d.line((x,136,x+7,136),fill=C[1])
for x in [14,106,298]:
 d.rectangle((x+3,78,x+5,126),fill=C[2]);d.polygon([(x+4,55),(x-3,94),(x+11,94)],fill=C[2])
d.rectangle((128,116,139,127),fill=C[3]);d.rectangle((126,112,141,117),fill=C[1])
d.rectangle((164,112,177,115),fill=C[2]);d.line((166,115,166,127),fill=C[3]);d.line((175,115,175,127),fill=C[3])
d.rectangle((184,96,263,114),fill=C[1]);d.line((184,96,263,96),fill=C[3]);d.rectangle((187,115,189,127),fill=C[2]);d.rectangle((259,115,261,127),fill=C[2])
# Gaps below the table are ball-only. Decorative legs are not solid.
for x in [199,223,245]: d.ellipse((x,91,x+10,94),outline=C[2])
d.rectangle((271,112,285,115),fill=C[2]);d.line((273,115,273,127),fill=C[3])
d.polygon([(350,127),(366,117),(366,127)],fill=C[2]);d.line((350,127,366,117),fill=C[3])
d.line((394,63,408,63),fill=C[3]);d.line((401,63,401,73),fill=C[3]);d.polygon([(397,74),(405,74),(409,84),(393,84)],fill=C[3]);d.rectangle((396,84,406,86),fill=C[1])
d.rectangle((414,49,417,127),fill=C[2]);d.arc((412,31,467,70),180,360,fill=C[2],width=3);d.rectangle((465,49,468,127),fill=C[2])
d.rectangle((447,118,464,127),fill=C[1]);d.line((447,118,464,118),fill=C[3]);d.line((449,121,462,121),fill=C[2])
for x,txt in [(8,'KITTIE, COME BACK!'),(173,'THE BANQUET TABLE'),(332,'RING THE BELL')]:d.text((x,8),txt,font=font,fill=C[3])
for xy,txt in [((8,24),'A: JUMP   B: BAT'),((8,35),'UP+B: LOB'),((8,46),'SELECT: RECALL'),((177,28),'BALL UNDER.'),((177,39),'KITTIE OVER.'),((332,24),'BAT FROM THE RAMP'),((425,103),'PHOTO')]:d.text(xy,txt,font=font,fill=C[3])
im.save(P/'source-art/courtyard.png')
# Hand-placed placeholder sprite, not final character art.
cat=Image.new('RGB',(32,16),T);d=ImageDraw.Draw(cat)
d.line([(1,8),(4,9),(7,11)],fill=C[1],width=3)
for x,y in [(1,7),(3,8),(6,10)]:d.rectangle((x,y,x+1,y+2),fill=C[3])
d.ellipse((6,7,21,14),fill=C[1]);d.ellipse((8,12,13,15),fill=C[0]);d.ellipse((20,12,25,15),fill=C[0]);d.ellipse((17,3,31,14),fill=C[0]);d.polygon([(18,5),(18,1),(22,3),(27,2),(30,1),(31,6),(25,5),(24,7)],fill=C[3]);d.line([(20,8),(22,7),(23,8)],fill=C[3]);d.line([(27,8),(28,7),(30,8)],fill=C[3]);d.point((25,10),fill=C[1]);d.line([(21,10),(23,12),(28,12),(30,10)],fill=C[3]);cat.save(P/'source-art/kittie.png')
ball=Image.new('RGB',(16,16),T);d=ImageDraw.Draw(ball);d.ellipse((3,3,12,12),fill=C[1],outline=C[3]);d.line([(4,6),(10,4),(12,7),(5,10),(10,11)],fill=C[0]);ball.save(P/'source-art/ball.png')
gate=Image.new('RGB',(16,64),T);d=ImageDraw.Draw(gate)
for x in [2,7,12]:d.line((x,0,x,63),fill=C[3],width=2)
for y in [4,30,57]:d.line((2,y,13,y),fill=C[1],width=2)
gate.save(P/'source-art/gate.png')
def meta(name,w,h,frames,originx=0,originy=0,flip=False):
 uid=lambda:str(uuid.uuid4())
 tiles=[dict(id=uid(),x=x-(8 if w==32 else 0),y=-y,sliceX=x,sliceY=y,flipX=False,flipY=False,palette=0,paletteIndex=0,objPalette='OBP0',priority=False) for x in range(0,w,8) for y in range(0,h,16)]
 animations=[dict(id=uid(),frames=[dict(id=uid(),tiles=[dict(t,id=uid()) for t in tiles])]) for _ in range(8)]
 m=dict(_resourceType='sprite',id=uid(),name=name,symbol='sprite_'+name,filename=name+'.png',width=w,height=h,canvasWidth=w,canvasHeight=h,canvasOriginX=originx,canvasOriginY=originy,boundsX=0,boundsY=-8,boundsWidth=16,boundsHeight=16,checksum=hashlib.sha1((P/'source-art'/f'{name}.png').read_bytes()).hexdigest(),animSpeed=15,numTiles=w*h//64,states=[dict(id=uid(),name='',animationType='multi' if flip else 'fixed',flipLeft=flip,animations=animations)])
 path=P/'source-art'/f'{name}.json';path.write_text(json.dumps(m,indent=2))
 return dict(name=name,id=m['id'],sourceSha256=hashlib.sha256((P/'source-art'/f'{name}.png').read_bytes()).hexdigest(),metadataSha256=hashlib.sha256(path.read_bytes()).hexdigest())
print(json.dumps([meta('kittie',32,16,1,flip=True),meta('ball',16,16,1),meta('gate',16,64,1)]))
