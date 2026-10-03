"""Native olive-grove blockout, with editable geometry and palette regions."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
level = json.loads((ROOT / 'tools/grove.json').read_text())
C = ['#e0f8cf','#86c06c','#306850','#071821']
im = Image.new('RGB',(level['width'],144),C[0]); d = ImageDraw.Draw(im)
font = ImageFont.load_default(size=8)
paint = [dict(x=0,y=16,width=level['width']//8,height=2,slot=2)]

def caption(x,y,text):
    for i,char in enumerate(text):
        tile=Image.new('RGB',(8,8),C[0]); td=ImageDraw.Draw(tile); td.fontmode='1'
        td.text((1,-1),char,fill=C[3],font=font); im.paste(tile,(x+i*8,y))

# Quiet, repeated olive trees. The ground and stone edges remain stronger.
for x in range(16,level['width']-48,96):
    d.rectangle((x+22,88,x+25,127),fill=C[2])
    d.line((x+24,108,x+10,92),fill=C[2],width=2)
    d.line((x+24,100,x+38,86),fill=C[2],width=2)
    for dx,dy in [(0,72),(16,64),(32,72),(8,80),(24,80)]:
        d.ellipse((x+dx,dy,x+dx+23,dy+23),fill=C[1])
        d.line((x+dx+6,dy+8,x+dx+13,dy+8),fill=C[2])
    paint.append(dict(x=x//8,y=8,width=7,height=8,slot=2))
d.rectangle((0,128,level['width']-1,143),fill=C[2])
d.line((0,128,level['width']-1,128),fill=C[3])
for x in range(0,level['width'],16):
    d.line((x+1,136,x+14,136),fill=C[1]);d.line((x+8,130,x+8,134),fill=C[1])
for i,(x,y,r,b) in enumerate(level['solids']):
    if i in level['gate_indices'] or i==level['door_index']:continue
    d.rectangle((x,y,r-1,b-1),fill=C[1],outline=C[2]);d.line((x,y,r-1,y),fill=C[3])
    d.line((x+1,y+3,r-2,y+3),fill=C[0])
    for row in range(y+8,b,8):d.line((x+1,row,r-2,row),fill=C[2])
    paint.append(dict(x=x//8,y=y//8,width=(r-x+7)//8,height=(b-y+7)//8,slot=3))
for x,r,_ in level['gaps']:
    d.rectangle((x,128,r-1,143),fill=C[1]);d.line((x,128,r-1,128),fill=C[0])
    for col in range(x,r,8):
        d.line((col+1,132,col+5,132),fill=C[0]);d.line((col+3,137,col+7,137),fill=C[2])
    d.line((x-1,128,x-1,143),fill=C[3]);d.line((r,128,r,143),fill=C[3])
    paint.append(dict(x=x//8,y=16,width=(r-x)//8,height=2,slot=4))
for court in level['courts']:
    x,y,g=court['bell_x'],court['bell_y'],court['gate']
    d.line([(x,y-6),(x,y-16),(g+3,y-16),(g+3,54)],fill=C[2])
    d.polygon([(x-3,y-5),(x+3,y-5),(x+6,y+3),(x-6,y+3)],fill=C[3])
    d.rectangle((x-3,y-3,x+2,y),fill=C[1]);d.line((x-6,y+4,x+6,y+4),fill=C[3])
    d.rectangle((g-3,40,g-1,127),fill=C[2]);d.rectangle((g+9,40,g+11,127),fill=C[2])
    d.rectangle((g-5,36,g+13,40),fill=C[1],outline=C[2])
    paint.append(dict(x=(x-8)//8,y=(y-8)//8,width=2,height=2,slot=5))
caption(8,24,'OLIVE GROVE')
caption(192,24,'RING THE BELL')
caption(664,24,'WOOL ABOVE')
caption(664,40,'GOON BELOW')
caption(1504,24,'LOW THROW')
caption(1664,24,'GROVE EXIT')
# Two arrows mark the actual fork, instead of relying on a vague caption.
d.line((654,100,654,77),fill=C[3],width=2)
d.line([(650,81),(654,77),(658,81)],fill=C[3],width=2)
d.line((648,120,663,120),fill=C[3],width=2)
d.line([(660,116),(664,120),(660,124)],fill=C[3],width=2)
dest=ROOT/'assets/backgrounds/olive_grove.png';im.save(dest)
im.save(ROOT/'source-art/olive-grove-blockout.png')
(ROOT/'tools/grove-palettes.json').write_text(json.dumps(paint,indent=2)+'\n')
tiles={im.crop((x,y,x+8,y+8)).tobytes() for y in range(0,144,8) for x in range(0,level['width'],8)}
print(f'Olive grove: {im.width}x{im.height}, {len(tiles)} source tiles, {len(paint)} palette regions')
