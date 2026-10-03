"""Native tiles and sparse texture for the grove, banquet and front end."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
C = ['#e0f8cf', '#86c06c', '#306850', '#071821']
FONT = ImageFont.load_default(size=8)

def caption(im, x, y, text):
    for i, char in enumerate(text):
        tile = Image.new('RGB', (8, 8), C[0])
        d = ImageDraw.Draw(tile); d.fontmode = '1'
        d.text((1,-1), char, fill=C[3], font=FONT)
        im.paste(tile, (x+i*8,y))

def build(name):
    level = json.loads((ROOT/f'tools/{name}.json').read_text())
    w = level['width']; grove = name == 'grove'
    im = Image.new('RGB', (w,144), C[0]); d = ImageDraw.Draw(im)
    paint = [dict(x=0,y=0,width=w//8,height=18,slot=0)]
    def region(x,y,r,b,slot):
        paint.append(dict(x=x//8,y=y//8,width=(r+7)//8-x//8,height=(b+7)//8-y//8,slot=slot))
    if grove:
        # Widely spaced trunks and layered canopies leave the jump arc readable.
        for x in range(16,w-64,160):
            d.rectangle((x+30,72,x+35,127),fill=C[2])
            d.line((x+32,104,x+12,78),fill=C[2],width=3)
            for dx,dy in [(0,56),(16,40),(32,48),(48,56),(16,64),(32,64)]:
                d.ellipse((x+dx,dy,x+dx+31,dy+23),fill=C[1])
                for xx,yy in [(8,8),(18,12),(12,18)]:
                    d.line((x+dx+xx,dy+yy,x+dx+xx+3,dy+yy-1),fill=C[2])
            region(x,40,x+80,128,2)
    else:
        # Banquet walls, tall windows, garlands and warm hanging lanterns.
        for x in range(0,w,80):
            d.rectangle((x+8,40,x+55,111),fill=C[1])
            d.rounded_rectangle((x+16,48,x+47,95),radius=14,fill=C[2])
            d.rectangle((x+19,64,x+44,92),fill=C[0])
            d.line((x+31,52,x+31,92),fill=C[1],width=2)
            d.line((x+18,72,x+45,72),fill=C[1],width=2)
            d.line((x+8,104,x+55,104),fill=C[0])
            region(x+8,40,x+56,112,1)
        d.line((0,24,w-1,24),fill=C[2])
        for x in range(8,w,24):
            d.polygon([(x,25),(x+12,25),(x+6,33)],fill=C[1])
            d.point((x+6,30),fill=C[2])
        region(0,24,w,40,5)
    # Eight-pixel patterns repeat instead of random noise, preserving tile space.
    d.rectangle((0,128,w-1,143),fill=C[2]);d.line((0,128,w-1,128),fill=C[3])
    for x in range(0,w,16):
        d.line((x,136,x+14,136),fill=C[1]);d.line((x+8,129,x+8,135),fill=C[1])
        d.point((x+3,131),fill=C[0]);d.point((x+11,140),fill=C[1])
    region(0,128,w,144,2 if grove else 3)
    for i,(x,y,r,b) in enumerate(level['solids']):
        if i in level['gate_indices'] or i==level['door_index']: continue
        table = not grove and b-y<=18 and r-x>48
        d.rectangle((x,y,r-1,b-1),fill=C[1],outline=C[2])
        d.line((x,y,r-1,y),fill=C[3]);d.line((x+1,y+2,r-2,y+2),fill=C[0])
        if table:
            for xx in range(x+8,r-8,24):
                d.ellipse((xx,y-4,xx+9,y-2),fill=C[0],outline=C[2])
                d.line((xx+4,y-8,xx+4,y-5),fill=C[2])
                d.point((xx+4,y-9),fill=C[1])
            # Cloth border; supporting legs are background decoration only.
            for xx in range(x+2,r-2,8): d.line((xx,b-3,xx+3,b-3),fill=C[2])
            region(x,y-16,r,b,0)
        else:
            for yy in range(y+8,b,8):
                d.line((x+1,yy,r-2,yy),fill=C[2])
                for xx in range(x+8+(8 if (yy//8)&1 else 0),r,16):
                    d.line((xx,yy-7,xx,yy-1),fill=C[2]);d.point((xx-4,yy-3),fill=C[0])
            region(x,y,r,b,3)
    for x,r,_ in level['gaps']:
        d.rectangle((x,128,r-1,143),fill=C[1])
        d.line((x,128,r-1,128),fill=C[0])
        for xx in range(x,r,8):
            d.line((xx+1,132,xx+5,132),fill=C[0]);d.line((xx+3,139,xx+7,139),fill=C[2])
        d.line((x-1,128,x-1,143),fill=C[3]);d.line((r,128,r,143),fill=C[3])
        region(x,128,r,144,4)
    for i,court in enumerate(level['courts']):
        if level.get('initial_gate',0)&(1<<i): continue
        x,y,g=court['bell_x'],court['bell_y'],court['gate']
        d.line([(x,y-7),(x,y-16),(g+3,y-16),(g+3,48)],fill=C[2])
        d.polygon([(x-3,y-5),(x+3,y-5),(x+6,y+3),(x-6,y+3)],fill=C[3])
        d.rectangle((x-3,y-3,x+2,y),fill=C[1]);d.line((x-6,y+4,x+6,y+4),fill=C[3])
        d.rectangle((g-3,40,g-1,127),fill=C[2]);d.rectangle((g+9,40,g+11,127),fill=C[2])
        d.rectangle((g-5,36,g+13,40),fill=C[1],outline=C[2])
        region(x-8,y-8,x+8,y+8,5)
    if grove:
        caption(im,8,24,'OLIVE GROVE')
        caption(im,696,24,'WOOL ABOVE')
        caption(im,1512,24,'ONE LAST LOB')
        # Orchard baskets beneath the trees.
        for x in (40,1336,1680):
            d.rectangle((x,116,x+15,127),fill=C[1],outline=C[2])
            d.line((x+1,121,x+14,121),fill=C[2])
    else:
        caption(im,8,40,'THE BANQUET')
        caption(im,144,40,'B LOW THROW')
        caption(im,808,40,'TABLE HOP')
        caption(im,1160,40,'LAST BELL')
        # Wedding arch and two guests frame the final spot.
        d.rounded_rectangle((1344,48,1431,127),radius=32,outline=C[2],width=3)
        d.rectangle((1347,96,1428,130),fill=C[0])
        for x in (1344,1428):
            d.rectangle((x,72,x+3,127),fill=C[2])
            for y in range(72,124,16): d.ellipse((x-3,y,x+5,y+5),fill=C[1])
        caption(im,1352,40,'PHOTO')
        region(1344,48,1440,128,5)
    dest='olive_grove' if grove else 'banquet'
    im.save(ROOT/f'assets/backgrounds/{dest}.png')
    (ROOT/f'tools/{name}-palettes.json').write_text(json.dumps(paint)+'\n')
    tiles={im.crop((x,y,x+8,y+8)).tobytes() for y in range(0,144,8) for x in range(0,w,8)}
    print(name,w,'pixels;',len(tiles),'source tiles')

def front_end(name):
    im=Image.new('RGB',(160,144),C[0]);d=ImageDraw.Draw(im)
    # Native pixel portrait: the head is an oval, with closed eyes and a smile.
    d.ellipse((32,46,92,88),fill=C[2]);d.ellipse((34,47,91,85),fill=C[1])
    d.polygon([(34,70),(16,57),(8,58),(7,62),(30,79)],fill=C[2])
    for x,y in [(12,59),(21,64)]:d.line((x,y,x+1,y+5),fill=C[3],width=3)
    d.rounded_rectangle((43,80,62,91),radius=4,fill=C[2]);d.rounded_rectangle((46,81,61,89),radius=4,fill=C[1])
    d.rounded_rectangle((94,80,111,91),radius=4,fill=C[2]);d.rounded_rectangle((95,81,110,89),radius=3,fill=C[1])
    d.ellipse((72,42,126,82),fill=C[3]);d.ellipse((73,43,125,81),fill=C[1])
    d.polygon([(74,58),(72,40),(77,36),(89,46),(86,52)],fill=C[3])
    d.polygon([(108,44),(119,37),(124,40),(123,54)],fill=C[3])
    d.polygon([(84,44),(91,42),(100,44),(94,49),(87,49)],fill=C[3])
    d.polygon([(105,44),(114,43),(116,49),(111,49)],fill=C[3])
    d.line([(83,58),(86,55),(91,55),(94,58)],fill=C[3],width=2)
    d.line([(106,58),(109,55),(114,55),(117,58)],fill=C[3],width=2)
    d.polygon([(97,60),(103,60),(100,64)],fill=C[0])
    d.line([(100,64),(100,68),(96,71),(92,69),(90,66)],fill=C[3])
    d.line([(100,68),(104,71),(108,69),(111,65)],fill=C[3])
    d.line((78,64,87,65),fill=C[2]);d.line((114,65,122,63),fill=C[2])
    d.ellipse((54,55,69,70),fill=C[3]);d.ellipse((55,56,68,69),fill=C[1])
    d.arc((55,57,69,69),20,240,fill=C[2]);d.line((58,57,65,68),fill=C[2])
    if name=='title':
        caption(im,40,8,'KITTIE!');caption(im,16,24,'A TUSCAN WEDDING')
    else:
        caption(im,24,8,'JUST MARRIED!');caption(im,16,24,'KITTIE MADE IT')
        for x in (8,140):
            d.ellipse((x,52,x+10,62),fill=C[2]);d.rectangle((x+1,65,x+9,84),fill=C[2])
            d.line((x+2,84,x+2,95),fill=C[3]);d.line((x+8,84,x+8,95),fill=C[3])
    im.save(ROOT/f'assets/backgrounds/{name}.png')

if __name__ == '__main__':
    build('grove');build('banquet');front_end('title');front_end('ending')
