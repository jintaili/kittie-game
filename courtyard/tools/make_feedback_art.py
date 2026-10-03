"""Native bell motion, raised gates and wool-only table clearance."""
from pathlib import Path
from PIL import Image, ImageDraw
import copy
import hashlib
import json
import uuid

ROOT = Path(__file__).resolve().parents[1]
T, L, M, D = '#65ff00', '#e0f8cf', '#86c06c', '#071821'
uid = lambda name: str(uuid.uuid5(uuid.NAMESPACE_URL, 'kittie-feedback-' + name))


def table_clearance(draw, x, y, r, b):
    """Show the low apron and its exact 14px passage, without fake solid legs."""
    draw.rectangle((x, b-3, r-1, b-1), fill=D)
    for xx in range(x+3, r-3, 8):
        draw.line((xx, y+5, xx, b-4), fill='#306850')
    draw.rectangle((x, b, r-1, 126), fill='#306850')
    draw.line((x, 127, r-1, 127), fill=L)


def build():
    template = json.loads((ROOT/'assets/sprites/gate.png.gbsres').read_text())
    for name, height, count in [('gate', 80, 4), ('bell', 16, 4)]:
        sheet = Image.new('RGB', (16*count, height), T)
        frames = []
        for frame in range(count):
            im = Image.new('RGB', (16, height), T)
            d = ImageDraw.Draw(im)
            if name == 'gate':
                bottom = [79, 47, 23, 7][frame]
                for x in [2, 6, 9]:
                    d.rectangle((x, 0, x+1, bottom), fill=D)
                for y in [2, bottom//2, bottom-2]:
                    d.rectangle((2, y, 10, y+1), fill=M)
                d.line((2, 0, 10, 0), fill=L)
                if frame == 3:
                    # A persistent green check marks the open passage.
                    d.line([(3, 14), (6, 17), (12, 11)], fill=D, width=3)
                    d.line([(3, 13), (6, 16), (12, 10)], fill=L)
            else:
                shift = [0, -2, 2, 0][frame]
                d.line((8, 0, 8+shift, 3), fill=D)
                d.polygon([(5+shift, 3), (10+shift, 3),
                           (13+shift, 11), (2+shift, 11)], fill=M, outline=D)
                d.line((5+shift, 5, 5+shift, 8), fill=L)
                d.line((2+shift, 12, 13+shift, 12), fill=D)
                d.point((8+shift, 14), fill=L if frame == 3 else D)
                if frame in (1, 2):
                    x = 14 if frame == 1 else 1
                    d.line((x, 3, x, 6), fill=L)
                    d.point((x, 9), fill=L)
            sheet.paste(im, (frame*16, 0))
            frames.append(im)
        dest = ROOT/f'assets/sprites/{name}.png'
        sheet.save(dest)
        meta = copy.deepcopy(template)
        meta.update(id=template['id'] if name == 'gate' else uid('bell'),
                    name=name, filename=name+'.png', symbol='sprite_'+name,
                    width=64, height=height, canvasWidth=16, canvasHeight=height,
                    numTiles=2*(height//8)*count,
                    checksum=hashlib.sha1(dest.read_bytes()).hexdigest())
        for a, anim in enumerate(meta['states'][0]['animations']):
            anim['id'] = uid(f'{name}-anim-{a}')
            anim['frames'] = []
            for f, im in enumerate(frames):
                tiles = []
                for y in range(0, height, 16):
                    for x in range(0, 16, 8):
                        if set(im.crop((x,y,x+8,y+16)).getdata()) == {(101,255,0)}:
                            continue
                        tiles.append(dict(id=uid(f'{name}-{a}-{f}-{x}-{y}'),
                            x=x, y=-y, sliceX=f*16+x, sliceY=y,
                            flipX=False, flipY=False, palette=0,
                            paletteIndex=(5 if f == 3 else (3 if name == 'bell' else 0)),
                            objPalette='OBP0', priority=False))
                anim['frames'].append(dict(id=uid(f'{name}-{a}-{f}'), tiles=tiles))
        meta['states'][0]['id'] = uid(name+'-state')
        dest.with_suffix('.png.gbsres').write_text(json.dumps(meta, indent=2)+'\n')
        print(name, meta['id'])


if __name__ == '__main__':
    build()
