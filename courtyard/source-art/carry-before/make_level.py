"""Native indexed courtyard art; scene palettes provide Tuscan colors."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import hashlib
import json
import uuid

ROOT = Path(__file__).resolve().parents[1]
level = json.loads((ROOT / 'tools/level.json').read_text())
colors = ['#e0f8cf', '#86c06c', '#306850', '#071821']
width = level['width']
im = Image.new('RGB', (width, 144), colors[0])
d = ImageDraw.Draw(im)
font = ImageFont.load_default(size=8)

def caption(x, y, text):
    # Each letter stays inside one 8px tile, so text tiles can be reused.
    for i, char in enumerate(text):
        tile = Image.new('RGB', (8, 8), colors[0])
        td = ImageDraw.Draw(tile)
        td.fontmode = '1'
        td.text((1, -1), char, fill=colors[3], font=font)
        im.paste(tile, (x + i * 8, y))

def tree(x, y=64):
    d.rectangle((x+14,y+32,x+17,127),fill=colors[2])
    d.line((x+16,y+50,x+4,y+39),fill=colors[2],width=2)
    for dx,dy in [(0,8),(16,8),(8,0),(8,24)]:
        d.ellipse((x+dx,y+dy,x+dx+15,y+dy+23),fill=colors[1])
        d.line((x+dx+4,y+dy+7,x+dx+9,y+dy+7),fill=colors[2])

# Repeated distant roof/wall tiles; leave moving objects a quiet backdrop.
for x in range(0,width,64):
    d.polygon([(x,72),(x+24,48),(x+48,72)], fill=colors[1])
    d.rectangle((x+8,72,x+39,119),fill=colors[1])
    d.rectangle((x+16,80,x+23,95),fill=colors[0])
    d.line((x+8,104,x+39,104),fill=colors[0])
for x in [24,480,864,984]:
    tree(x)
# Solid paving.
d.rectangle((0,128,width-1,143),fill=colors[2])
d.line((0,128,width-1,128),fill=colors[3])
for x in range(0,width,16):
    d.line((x,136,x+14,136),fill=colors[1])
    d.line((x+8,129,x+8,134),fill=colors[1])

for i,(left,top,right,bottom) in enumerate(level['solids']):
    if i in level['gate_indices']:
        continue
    if left == 1104:  # Table: leave the entire wool-ball passage visible.
        d.rectangle((left,top,right-1,bottom-1),fill=colors[1],outline=colors[3])
        d.line((left+1,top+3,right-2,top+3),fill=colors[0])
        for x in range(left+8,right-4,16):
            d.ellipse((x,top-5,x+7,top-2),fill=colors[0],outline=colors[2])
        continue
    d.rectangle((left,top,right-1,bottom-1),fill=colors[1],outline=colors[2])
    d.line((left,top,right-1,top),fill=colors[3])
    d.line((left+1,top+3,right-2,top+3),fill=colors[0])
    for y in range(top+8,bottom,8):
        d.line((left+1,y,right-2,y),fill=colors[2])
    if i in [0,1,2]:
        for x in range(left+4,right-3,8):
            d.line((x,top-6,x,top-1),fill=colors[2])
            d.rectangle((x-2,top-8,x+2,top-6),fill=colors[1])

for court in level['courts']:
    x,y,g = court['bell_x'],court['bell_y'],court['gate']
    # The thin cord connects the target to its gate latch.
    d.line([(x,y-6),(x,y-16),(g+3,y-16),(g+3,54)],fill=colors[2])
    d.polygon([(x-3,y-5),(x+3,y-5),(x+6,y+3),(x-6,y+3)],fill=colors[3])
    d.rectangle((x-3,y-3,x+2,y),fill=colors[1])
    d.line((x-6,y+4,x+6,y+4),fill=colors[3])
    d.point((x,y+6),fill=colors[3])
    d.rectangle((g-3,40,g-1,127),fill=colors[2])
    d.rectangle((g+9,40,g+11,127),fill=colors[2])
    d.rectangle((g-5,36,g+13,40),fill=colors[1],outline=colors[2])

# Wedding bunting and a small photo alcove after the final gate.
for x in range(1192,1272,16):
    d.line((x,40,x+16,40),fill=colors[2])
    d.polygon([(x+2,41),(x+10,41),(x+6,48)],fill=colors[1])
d.rectangle((1228,112,1260,127),fill=colors[1],outline=colors[2])
d.line((1228,115,1260,115),fill=colors[0])
for x in [1216,1264]:
    d.ellipse((x-3,84,x+3,90),fill=colors[2])
    d.rectangle((x-3,92,x+3,111),fill=colors[2])
    d.line((x-2,112,x-2,127),fill=colors[2])
    d.line((x+2,112,x+2,127),fill=colors[2])

caption(8,8,'KITTIE COME BACK')
caption(8,24,'A JUMP')
caption(168,8,'GARDEN STEPS')
caption(320,8,'RING THE BELL')
caption(320,24,'UP+B LOB')
caption(320,40,'SELECT RESET')
caption(488,8,'WOOL VS GOONS')
caption(488,24,'B BAT')
caption(616,40,'A JUMP')
caption(680,8,'HIGH OR LOW?')
caption(872,8,'ONE MORE HOP')
caption(1032,8,'UNDER THE TABLE')
caption(1032,24,'B BAT / A JUMP')
caption(1032,40,'SELECT RESET')
caption(1216,8,'PHOTO')

# Irrigation channels: first has a safe shallow bottom; later pools respawn.
for left,right,floor in level['gaps']:
    d.rectangle((left,128,right-1,143),fill=colors[1])
    d.line((left,128,right-1,128),fill=colors[0])
    for x in range(left,right,8):
        d.line((x+1,132,x+5,132),fill=colors[0])
        d.line((x+3,137,x+7,137),fill=colors[2])
    if floor == 140:
        d.rectangle((left,140,right-1,143),fill=colors[3])
    d.line((left-1,128,left-1,143),fill=colors[3])
    d.line((right,128,right,143),fill=colors[3])
# Small flags mark automatic checkpoints at the garden and final crossing.
for x in [496,864]:
    d.line((x,100,x,127),fill=colors[3])
    d.polygon([(x+1,100),(x+13,100),(x+9,105),(x+1,107)],fill=colors[2])

dest=ROOT/'assets/backgrounds/courtyard.png'
old=ROOT/'source-art/courtyard-v1.png'
if not old.exists():
    old.write_bytes(dest.read_bytes())
im.save(dest)
im.save(ROOT/'source-art/courtyard-long.png')
metadata=dest.with_suffix('.png.gbsres')
meta=json.loads(metadata.read_text())
meta.update(name='Tuscan wedding courtyard',width=width//8,height=18,imageWidth=width,imageHeight=144)
metadata.write_text(json.dumps(meta,indent=2)+'\n')
header=ROOT/'plugins/kittie/engine/include/states/kittie_level.h'
rows=',\n '.join('{'+','.join(str(v*16) for v in r)+'}' for r in level['solids'])
header.write_text('/* Generated by tools/make_level.py. Edit tools/level.json. */\n'
    f'#define LEVEL_WIDTH {width}\n#define SOLID_COUNT {len(level["solids"])}\n'
    f'#define FIRST_GATE_SOLID {level["gate_indices"][0]}\n#define LAST_GATE_SOLID {level["gate_indices"][1]}\n'
    f'static const INT16 solids[SOLID_COUNT][4]={{\n {rows}\n}};\n'
    + '#define GAP_COUNT 3\nstatic const INT16 gaps[GAP_COUNT][3]={'
    + ','.join('{'+','.join(str(v*16) for v in r)+'}' for r in level['gaps'])+'};\n'
    + '#define GOON_COUNT 3\nstatic const INT16 goon_limits[GOON_COUNT][2]={'
    + ','.join('{'+','.join(str(v*16) for v in r)+'}' for r in level['goons'])+'};\n')

# Extend the existing gate to cover its full 80px collision height.
gate=Image.new('RGB',(16,80),'#65ff00')
gd=ImageDraw.Draw(gate)
for x in [2,6,9]: gd.rectangle((x,0,x+1,79),fill=colors[3])
for y in [4,38,73]: gd.rectangle((2,y,10,y+2),fill=colors[1])
gp=ROOT/'assets/sprites/gate.png'
if not (ROOT/'source-art/gate-v1.png').exists():
    (ROOT/'source-art/gate-v1.png').write_bytes(gp.read_bytes())
gate.save(gp)
gm=gp.with_suffix('.png.gbsres')
m=json.loads(gm.read_text())
m.update(width=16,height=80,canvasHeight=80,numTiles=20,checksum=hashlib.sha1(gp.read_bytes()).hexdigest())
for a,anim in enumerate(m['states'][0]['animations']):
    frame=anim['frames'][0]
    frame['tiles']=[dict(id=str(uuid.uuid5(uuid.NAMESPACE_URL,f'kittie-gate-{a}-{x}-{y}')),x=x,y=-y,sliceX=x,sliceY=y,flipX=False,flipY=False,palette=0,paletteIndex=0,objPalette='OBP0',priority=False) for y in range(0,80,16) for x in range(0,16,8)]
gm.write_text(json.dumps(m,indent=2)+'\n')
tiles={im.crop((x,y,x+8,y+8)).tobytes() for y in range(0,144,8) for x in range(0,width,8)}
print(f'Background {width}x144, {len(tiles)} unique source tiles')
