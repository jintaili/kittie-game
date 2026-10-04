"""Banquet-only native art, following the editable collision geometry."""
from pathlib import Path
import json
from PIL import Image, ImageDraw
from make_feedback_art import table_clearance

ROOT = Path(__file__).resolve().parents[1]
C = ['#e0f8cf', '#86c06c', '#306850', '#071821']


def build():
    level = json.loads((ROOT / 'tools/banquet.json').read_text())
    w = level['width']
    im = Image.new('RGB', (w, 144), C[0])
    d = ImageDraw.Draw(im)
    paint = [dict(x=0, y=0, width=w//8, height=18, slot=0)]

    def region(x, y, r, b, slot):
        paint.append(dict(x=x//8, y=y//8, width=(r+7)//8-x//8,
                          height=(b+7)//8-y//8, slot=slot))

    # Wide plaster bays; paired recessed windows only in the dining room.
    d.line((0, 56, w-1, 56), fill=C[1])
    for x in (24, 344, 712):
        for xx in (x, x+40):
            d.rounded_rectangle((xx, 40, xx+31, 88), radius=14, fill=C[1])
            d.rounded_rectangle((xx+4, 44, xx+27, 84), radius=10, fill=C[0])
            d.line((xx+15, 46, xx+15, 83), fill=C[1])
            d.line((xx+5, 64, xx+26, 64), fill=C[1])
        region(x, 40, x+72, 96, 1)
    for x in (8, 312, 648, 816, 1112):
        d.rectangle((x, 24, x+7, 127), fill=C[1])
        d.line((x, 24, x+7, 24), fill=C[2])
    # Celebration stays above the flight paths and the fixed HUD.
    for left, right in ((8, 136), (336, 800), (872, 1024)):
        d.line((left, 24, right-1, 24), fill=C[1])
        for x in range(left+8, right-12, 24):
            d.polygon([(x,25),(x+12,25),(x+6,32)], fill=C[1])
        region(left, 24, right, 40, 5)
    d.rectangle((0,128,w-1,143), fill=C[1])
    d.line((0,128,w-1,128), fill=C[3])
    for x in range(0,w,16):
        d.line((x,136,x+14,136), fill=C[2])
        d.line((x+8,129,x+8,135), fill=C[2])
    region(0,128,w,144,3)
    for i,(x,y,r,b) in enumerate(level['solids']):
        if i in level['gate_indices']:
            continue
        table = b-y <= 18 and r-x > 48
        d.rectangle((x,y,r-1,b-1), fill=C[1])
        d.line((x,y,r-1,y), fill=C[3])
        d.line((x+1,y+2,r-2,y+2), fill=C[0])
        if table:
            d.rectangle((x+1,y+4,r-2,b-2), fill=C[0])
            for xx in range(x+3,r-3,8):
                d.line((xx,b-4,xx+3,b-4), fill=C[1])
            # Settings belong to the feast; landing and wool areas stay empty.
            if 320 < x < 800:
                for xx in range(x+16,r-12,32):
                    if abs(xx-576) < 20 or 664 <= xx < 704:
                        continue
                    d.ellipse((xx,y-4,xx+9,y-2), fill=C[0], outline=C[1])
                    d.line((xx+4,y-10,xx+4,y-5), fill=C[2])
                    d.point((xx+4,y-11), fill=C[1])
            if b == 114:
                table_clearance(d,x,y,r,b)
                region(x,b,r,128,0)
            region(x,y-16,r,b,0)
        else:
            d.rectangle((x+2,y+5,r-3,b-2), fill=C[2])
            d.line((x+4,y+6,x+4,b-3), fill=C[1])
            region(x,y,r,b,3)
    for x in level.get('lifts',[]):
        # Same service machinery as the villa, within the quiet approach bay.
        d.rectangle((x+8,56,x+31,127),fill=C[0])
        for rail in (x+10,x+29):
            d.line((rail,56,rail,127),fill=C[2])
            d.line((rail+1,56,rail+1,127),fill=C[1])
        d.line((x+8,56,x+31,56),fill=C[2]);region(x+8,56,x+32,128,3)
    for x,r,_ in level['gaps']:
        d.rectangle((x,128,r-1,143), fill=C[1])
        d.line((x,128,r-1,128), fill=C[0])
        for xx in range(x,r,8):
            d.line((xx+1,132,xx+5,132), fill=C[0])
            d.line((xx+3,139,xx+7,139), fill=C[2])
        d.line((x-1,128,x-1,143), fill=C[3])
        d.line((r,128,r,143), fill=C[3])
        region(x,128,r,144,4)
    for court in level['courts']:
        x,y,g = court['bell_x'],court['bell_y'],court['gate']
        d.line([(x,y-8),(x,y-16),(g+3,y-16),(g+3,48)], fill=C[1])
        d.rectangle((g-3,40,g-1,127), fill=C[2])
        d.rectangle((g+9,40,g+11,127), fill=C[2])
        d.rectangle((g-5,36,g+13,40), fill=C[1], outline=C[2])
        region(x-8,y-8,x+8,y+8,5)
    # Photo recess has no rear window. Flowers and a short pale runner mark it.
    d.rounded_rectangle((1344,48,1431,127), radius=32, outline=C[1], width=3)
    d.rectangle((1347,96,1428,127), fill=C[0])
    for x in (1344,1428):
        d.rectangle((x,72,x+3,127), fill=C[2])
        for y in range(72,124,16):
            d.ellipse((x-3,y,x+5,y+5), fill=C[1])
            d.point((x+1,y+2), fill=C[0])
    region(1344,48,1440,128,5)
    d.rectangle((1352,128,1423,135), fill=C[0])
    d.line((1352,135,1423,135), fill=C[1])
    region(1352,128,1424,136,0)
    im.save(ROOT / 'assets/backgrounds/banquet.png')
    (ROOT / 'tools/banquet-palettes.json').write_text(json.dumps(paint)+'\n')
    tiles = {im.crop((x,y,x+8,y+8)).tobytes() for y in range(0,144,8) for x in range(0,w,8)}
    print('Banquet:',len(tiles),'source tiles')


if __name__ == '__main__':
    build()
