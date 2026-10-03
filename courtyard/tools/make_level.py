"""Native courtyard scenery and its tile-aligned material assignments."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json

from make_feedback_art import table_clearance

ROOT = Path(__file__).resolve().parents[1]
level = json.loads((ROOT / 'tools/level.json').read_text())
C = ['#e0f8cf', '#86c06c', '#306850', '#071821']
width = level['width']
im = Image.new('RGB', (width, 144), C[0])
d = ImageDraw.Draw(im)
font = ImageFont.load_default(size=8)
paint = [dict(x=0, y=0, width=width//8, height=18, slot=0)]


def region(x, y, right, bottom, slot):
    paint.append(dict(x=x//8, y=y//8,
                      width=(right+7)//8-x//8,
                      height=(bottom+7)//8-y//8, slot=slot))


def caption(x, y, text):
    for i, char in enumerate(text):
        tile = Image.new('RGB', (8, 8), C[0])
        td = ImageDraw.Draw(tile)
        td.fontmode = '1'
        td.text((1, -1), char, fill=C[3], font=font)
        im.paste(tile, (x+i*8, y))


def shutter(x, y):
    # Recesses stay softer than the outline of a walkable stone surface.
    d.rectangle((x, y, x+31, y+39), fill=C[1])
    d.rectangle((x+3, y+3, x+28, y+36), fill=C[2])
    for xx in range(x+5, x+29, 8):
        d.line((xx, y+5, xx, y+34), fill=C[1])
    d.line((x+4, y+19, x+27, y+19), fill=C[1])
    d.rectangle((x-3, y+40, x+34, y+42), fill=C[1])


def olive(x):
    d.rectangle((x+29, 86, x+33, 127), fill=C[2])
    d.line((x+31, 108, x+20, 82), fill=C[2], width=2)
    d.line((x+31, 96, x+47, 76), fill=C[2], width=2)
    for dx, dy in ((0, 56), (16, 40), (32, 48), (16, 64)):
        d.ellipse((x+dx, dy, x+dx+31, dy+31), fill=C[1])
        # Broad leaf clusters are identical, keeping the native tile family small.
        d.line((x+dx+6, dy+12, x+dx+12, dy+9), fill=C[0])
        d.line((x+dx+15, dy+22, x+dx+22, dy+19), fill=C[2])
    region(x, 40, x+64, 128, 2)


# One continuous garden wall, with quiet plaster behind moving objects.
d.rectangle((0, 56, width-1, 127), fill=C[0])
d.rectangle((0, 54, width-1, 57), fill=C[1])
d.line((0, 54, width-1, 54), fill=C[0])
for x in range(0, width, 64):
    d.line((x+8, 104, x+15, 104), fill=C[1])
    d.line((x+40, 80, x+47, 80), fill=C[1])
    d.line((x+16, 120, x+31, 120), fill=C[1])

# Arrival villa: one broad roof, then a long wall and a shuttered window.
d.rectangle((0, 40, 87, 127), fill=C[0])
d.polygon(((0, 40), (16, 24), (72, 24), (88, 40)), fill=C[1])
d.line((0, 40, 87, 40), fill=C[2])
for x in range(8, 80, 16):
    d.line((x, 32, x+7, 32), fill=C[2])
region(0, 24, 88, 48, 1)
shutter(16, 56)
shutter(208, 56)
# Sparse climbing leaves sit above the planter, outside its landing space.
for x, y in ((248, 58), (256, 66), (248, 74), (256, 82)):
    d.line((252, y, 252, y+8), fill=C[1])
    d.ellipse((x, y, x+6, y+3), fill=C[1])
region(248, 56, 264, 88, 2)

# Garden landmark. Its trunk is behind the entry, clear of the first patrol.
olive(480)
# Recessed panel distinguishes the route heights without a hard platform edge.
d.rectangle((672, 64, 831, 120), fill=C[1])
d.rectangle((680, 72, 823, 120), fill=C[0])
for x in (688, 816):
    d.line((x, 72, x, 120), fill=C[1])
# Open garden between the raised route and the service court.
olive(856)

# A broad service recess and matching pale jambs frame the closing shutter.
d.rounded_rectangle((984, 48, 1063, 127), radius=24, fill=C[1])
d.rounded_rectangle((992, 56, 1055, 127), radius=20, fill=C[0])
d.rectangle((984, 88, 991, 127), fill=C[1])
d.rectangle((1056, 88, 1063, 127), fill=C[1])

# Paving uses one repeated limestone joint, with strong edges only at collisions.
d.rectangle((0, 128, width-1, 143), fill=C[1])
d.line((0, 128, width-1, 128), fill=C[3])
for x in range(0, width, 16):
    d.line((x, 136, x+14, 136), fill=C[2])
    d.line((x+8, 129, x+8, 135), fill=C[2])
    d.line((x+4, 139, x+7, 139), fill=C[0])
region(0, 128, width, 144, 3)

for i, (left, top, right, bottom) in enumerate(level['solids']):
    if i in level['gate_indices'] or i == level['door_index']:
        continue
    table = bottom == 114 and right-left > 48
    d.rectangle((left, top, right-1, bottom-1), fill=C[1], outline=C[2])
    d.line((left, top, right-1, top), fill=C[3])
    d.line((left+1, top+2, right-2, top+2), fill=C[0])
    if table:
        for x in range(left+8, right-4, 16):
            d.ellipse((x, top-5, x+7, top-2), fill=C[0], outline=C[2])
        table_clearance(d, left, top, right, bottom)
        region(left, top-8, right, 128, 0)
    else:
        for y in range(top+8, bottom, 8):
            d.line((left+1, y, right-2, y), fill=C[2])
            for x in range(left+8, right-1, 16):
                d.line((x, y-7, x, y-1), fill=C[2])
        region(left, top, right, bottom, 3)
        if i < 3:
            for x in range(left+4, right-3, 8):
                d.line((x, top-5, x, top-1), fill=C[2])
                d.rectangle((x-2, top-7, x+2, top-5), fill=C[1])
            region(left, top-8, right, top, 2)

for court in level['courts']:
    x, y, gate = court['bell_x'], court['bell_y'], court['gate']
    d.line(((x, y-6), (x, y-16), (gate+3, y-16), (gate+3, 54)), fill=C[2])
    d.rectangle((gate-3, 40, gate-1, 127), fill=C[2])
    d.rectangle((gate+9, 40, gate+11, 127), fill=C[2])
    d.rectangle((gate-5, 36, gate+13, 40), fill=C[1], outline=C[2])
    region(gate-8, 32, gate+16, 128, 3)
    region(x-8, y-8, x+8, y+8, 5)

for left, right, floor in level['gaps']:
    d.rectangle((left, 128, right-1, 143), fill=C[1])
    d.line((left, 128, right-1, 128), fill=C[0])
    for x in range(left, right, 8):
        d.line((x+1, 132, x+5, 132), fill=C[0])
        d.line((x+3, 139, x+7, 139), fill=C[2])
    d.line((left-1, 128, left-1, 143), fill=C[3])
    d.line((right, 128, right, 143), fill=C[3])
    region(left, 128, right, 144, 4)

# Orchard entrance keeps the approved bunting and a single framing bough.
for x in range(1200, 1272, 16):
    d.line((x, 48, x+16, 48), fill=C[2])
    d.polygon(((x+2, 49), (x+10, 49), (x+6, 56)), fill=C[1])
region(1200, 48, 1280, 64, 5)
olive(1216)
caption(8, 40, 'A JUMP B THROW')
caption(344, 24, 'UP+B LOB')

asset = ROOT / 'assets/backgrounds/courtyard.png'
im.save(asset)
im.save(ROOT / 'source-art/courtyard-long.png')
meta = json.loads(asset.with_suffix('.png.gbsres').read_text())
meta.update(name='Tuscan wedding courtyard', width=width//8, height=18,
            imageWidth=width, imageHeight=144)
asset.with_suffix('.png.gbsres').write_text(json.dumps(meta, indent=2)+'\n')
(ROOT / 'tools/courtyard-palettes.json').write_text(json.dumps(paint, indent=2)+'\n')
tiles = {im.crop((x,y,x+8,y+8)).tobytes()
         for y in range(0,144,8) for x in range(0,width,8)}
print(f'Background {width}x144, {len(tiles)} unique source tiles')
