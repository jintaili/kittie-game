"""Native 40x32 Kittie pixels. The fixed face is shared by every local motion.

Frames: 0 rest, 1 breath/tail lift, 2 tail settle, 3-6 walk, 7 paw reach,
8 swat follow-through, 9 airborne, 10-13 idle cuddle. Engine selects offsets.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import hashlib
import json
import uuid

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'source-art'
ASSET = ROOT / 'assets/sprites/kittie.png'
META = ASSET.with_suffix('.png.gbsres')
SIZE = (40, 32)
T, L, M, D = '#65ff00', '#e0f8cf', '#86c06c', '#071821'
PALETTE = {T:'#efe5d3', L:'#dcc6a3', M:'#aa8e6d', D:'#392b26'}
NAMES = ['rest','breath','tail-settle','walk-a','walk-b','walk-c','walk-d','paw-reach','paw-follow','air-tuck','cuddle-reach','cuddle-open','cuddle-squeeze','cuddle-release']

def layer():
    return Image.new('RGBA', SIZE, (0,0,0,0))

# Wide, low oval head. The closed eyes and embroidered smile stay fixed.
face = layer()
d = ImageDraw.Draw(face)
d.polygon([(24,13),(29,12),(34,13),(38,15),(39,18),(39,21),
           (37,24),(33,25),(26,25),(22,23),(20,20),(20,17),(22,15)],fill=D)
d.polygon([(24,14),(29,13),(34,14),(37,16),(38,18),(38,21),
           (36,23),(33,24),(26,24),(23,22),(21,20),(21,17)],fill=M)
d.polygon([(25,15),(29,14),(34,15),(37,17),(38,19),(37,22),
           (34,24),(27,24),(23,22),(22,19),(23,17)],fill=L)
# Small soft ears and cap follow the flattened head rather than adding height.
d.polygon([(20,16),(20,12),(21,11),(24,13),(26,14),(24,17),(22,18)],fill=D)
d.polygon([(33,13),(35,10),(37,11),(37,15),(35,16)],fill=D)
d.polygon([(24,14),(27,12),(31,13),(35,14),(35,16),
           (31,15),(30,17),(28,15),(26,16)],fill=D)
d.point((21,13),fill=M); d.point((35,12),fill=M)
d.line([(24,18),(25,17),(26,17),(27,18)],fill=D)
d.line([(32,18),(33,17),(34,17),(35,18)],fill=D)
d.point((30,19),fill=M)
d.line([(24,20),(25,22),(28,23),(33,23),(36,22),(37,20)],fill=D)
d.point((28,22),fill=D); d.point((32,22),fill=D)
d.line((21,20,23,20),fill=M); d.point((38,20),fill=M)

def draw_frame(index):
    if index >= 10:
        im = draw_frame(0)
        d = ImageDraw.Draw(im)
        # The forepaws leave the ground only during a stationary cuddle.
        # Keep the low belly, hind paws and every face pixel in place.
        d.rectangle((27,26,39,31),fill=T)
        d.line((26,27,28,28),fill=D,width=2)
        if index in (10,13):
            d.rounded_rectangle((29,25,35,28),radius=1,fill=D)
            d.line((30,26,34,26),fill=L)
            d.rounded_rectangle((36,24,39,27),radius=1,fill=D)
            d.line((37,25,38,25),fill=M)
        else:
            squeeze = index == 12
            # Two small paws cup opposite sides of an 8px ball at (35,29).
            d.line((28,27,31,29),fill=D,width=3)
            d.rounded_rectangle((30+squeeze,27,33+squeeze,31),radius=1,fill=D)
            d.line((31+squeeze,28,31+squeeze,30),fill=L)
            d.rounded_rectangle((38-squeeze,26,39,30),radius=1,fill=D)
            d.line((38,27,38,29),fill=M)
        im.paste(face,mask=face.getchannel('A'))
        return im
    im = Image.new('RGB', SIZE, T)
    d = ImageDraw.Draw(im)
    # Long thick tail, two separated dark bands, plus its dark tip.
    ty = [0,-1,1,0,-1,0,1,0,-1,-1][index]
    tail = layer(); q = ImageDraw.Draw(tail)
    q.polygon([(1,14+ty),(4,13+ty),(8,15+ty),(13,17),(17,20),(16,24),(12,22),(8,20+ty),(4,18+ty),(1,17+ty)],fill=D)
    q.polygon([(4,14+ty),(7,15+ty),(12,18),(15,20),(15,22),(12,21),(8,19+ty),(4,17+ty)],fill=M)
    q.line([(6,15+ty),(6,18+ty)],fill=D,width=2)
    q.line([(10,17+ty),(9,20+ty)],fill=D,width=2)
    q.point((4,15+ty),fill=L); q.point((8,17+ty),fill=L)
    # Cover tail root with the rear haunch; root never detaches.
    im.paste(tail,mask=tail.getchannel('A'))
    # The far paws peek out separately; near paws extend below the belly.
    walk = [0,0,0,-1,0,1,0,0,0,0][index]
    air = index == 9
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((17-walk,25,21-walk,29 if air else 30),radius=1,fill=D)
    d.rectangle((18-walk,26,20-walk,28 if air else 29),fill=M)
    # Lower the plush torso two pixels; keep the approved paws and their gait.
    breath = 1 if index == 1 else 0
    d.polygon([(9,24),(11,22),(16,20),(21,20),(25,22),(28,25),
               (26,28+breath),(22,29),(13,29),(9,27)],fill=D)
    d.polygon([(10,24),(12,23),(17,21),(21,21),(24,23),(27,25),
               (25,27+breath),(22,28),(13,28),(10,26)],fill=M)
    d.line([(13,24),(17,22),(20,22)],fill=L)
    d.line([(17,27),(21,27)],fill=L)
    # Near hind leg overlaps the haunch, with a broad rounded paw on the floor.
    hx = 11 + walk
    hy = 25 - (1 if air else 0)
    d.rounded_rectangle((hx,hy,hx+6,29 if air else 31),radius=2,fill=D)
    d.rounded_rectangle((hx+1,hy+1,hx+5,28 if air else 30),radius=1,fill=M)
    d.line((hx+2,hy+2,hx+4,hy+2),fill=L)
    # Two distinct front paws beneath the cheeks, separated by clear background.
    fx = 34 - walk
    d.rounded_rectangle((fx,24, min(39,fx+5),29 if air else 30),radius=2,fill=D)
    d.rounded_rectangle((fx+1,25,min(38,fx+4),28 if air else 29),radius=1,fill=M)
    paw_x = 25 + [0,0,0,1,0,-1,0,5,3,1][index]
    paw_y = 25 + [0,0,0,-1,0,0,-1,-2,-1,-2][index]
    d.rounded_rectangle((paw_x,paw_y,min(39,paw_x+7),min(31,paw_y+6)),radius=2,fill=D)
    d.rounded_rectangle((paw_x+1,paw_y+1,min(38,paw_x+6),min(30,paw_y+5)),radius=1,fill=L)
    d.point((paw_x+5,min(30,paw_y+5)),fill=M)
    im.paste(face,mask=face.getchannel('A'))
    return im

frames = [draw_frame(i) for i in range(len(NAMES))]
# Identity protection: all face pixels are exactly shared, not separately redrawn.
for frame in frames:
    for y in range(32):
        for x in range(40):
            rgba = face.getpixel((x,y))
            if rgba[3]:
                assert frame.getpixel((x,y)) == rgba[:3]
for frame in frames:
    assert set(frame.getdata()) <= {tuple(bytes.fromhex(c[1:])) for c in (T,L,M,D)}

SOURCE.mkdir(exist_ok=True)
(SOURCE/'kittie-frames').mkdir(exist_ok=True)
# Retain the old small blockout as an explicit before image.
if not (SOURCE/'kittie-before.png').exists():
    (SOURCE/'kittie-before.png').write_bytes(ASSET.read_bytes())
sheet = Image.new('RGB',(40*len(frames),32),T)
for i, frame in enumerate(frames):
    sheet.paste(frame,(i*40,0))
    frame.save(SOURCE/'kittie-frames'/f'{i:02d}-{NAMES[i]}.png')
sheet.save(ASSET)
sheet.save(SOURCE/'kittie-sheet.png')

meta = json.loads(META.read_text())
meta.update(width=sheet.width,height=sheet.height,canvasWidth=40,canvasHeight=32,
            canvasOriginX=0,canvasOriginY=0,animSpeed=255,
            checksum=hashlib.sha1(ASSET.read_bytes()).hexdigest())
# All directions share authored right-facing frames. GB Studio compiles mirrored left.
uid = lambda name: str(uuid.uuid5(uuid.UUID(meta['id']),name))
for a, animation in enumerate(meta['states'][0]['animations']):
    old_frame_id=animation['frames'][0]['id']
    animation['frames']=[]
    for f in range(len(NAMES)):
        tiles=[]
        for y in range(0,32,16):
            for x in range(0,40,8):
                if set(frames[f].crop((x,y,x+8,y+16)).getdata()) == {(101,255,0)}:
                    continue
                tiles.append(dict(id=uid(f'{a}-{f}-{x}-{y}'),x=x-12,y=16-y,
                                  sliceX=f*40+x,sliceY=y,flipX=False,flipY=False,
                                  palette=0,paletteIndex=0,objPalette='OBP0',priority=False))
        animation['frames'].append(dict(id=old_frame_id if f==0 else uid(f'frame-{a}-{f}'),tiles=tiles))
# Count unique native 8x16 pairs with flip deduplication, matching source structure.
patterns=set()
for frame in frames:
    for y in range(0,32,16):
        for x in range(0,40,8):
            tile=frame.crop((x,y,x+8,y+16))
            if set(tile.getdata())=={(101,255,0)}: continue
            patterns.add(min(tile.tobytes(),tile.transpose(Image.Transpose.FLIP_LEFT_RIGHT).tobytes(),tile.transpose(Image.Transpose.FLIP_TOP_BOTTOM).tobytes(),tile.transpose(Image.Transpose.ROTATE_180).tobytes()))
meta['numTiles']=len(patterns)
META.write_text(json.dumps(meta,indent=2)+'\n')

# Source previews use intended taupe/chocolate colors, not emulator output.
def colored(frame):
    result=frame.copy()
    rgb={tuple(bytes.fromhex(k[1:])):tuple(bytes.fromhex(v[1:])) for k,v in PALETTE.items()}
    result.putdata([rgb[p] for p in frame.getdata()])
    return result
previews=[colored(f) for f in frames]
contact=Image.new('RGB',(200,132),'#efe5d3')
d=ImageDraw.Draw(contact)
for i,p in enumerate(previews):
    x=(i%5)*40;y=(i//5)*44
    contact.paste(p,(x,y))
    d.text((x+2,y+32),str(i),fill='#392b26')
contact.save(SOURCE/'kittie-contact-native.png')
contact.resize((800,528),Image.Resampling.NEAREST).save(SOURCE/'kittie-contact-4x.png')
# Long idle hold, local breath, then walk/swat/air poses with intentional timing.
sequence=[0,1,0,2,0,3,4,5,6,3,4,5,6,0,7,8,0,9,0]
durations=[700,240,500,180,700,120,120,120,120,120,120,120,120,450,120,160,450,400,700]
for scale in (1,4):
    loop=[previews[i].resize((40*scale,32*scale),Image.Resampling.NEAREST) for i in sequence]
    loop[0].save(SOURCE/f'kittie-motion-{scale}x.gif',save_all=True,append_images=loop[1:],duration=durations,loop=0,disposal=2)
(SOURCE/'kittie-animation.json').write_text(json.dumps(dict(canvas=[40,32],frames=NAMES,sourcePreviewSequence=sequence,sourcePreviewDurationMs=durations,engineSelection='actor_set_dir then actor_set_frame_offset; anim_tick=ANIM_PAUSED',maxSpritesPerScanline=5,unique8x16Pairs=len(patterns)),indent=2)+'\n')
print(json.dumps(dict(frames=len(frames),unique8x16Pairs=len(patterns),sheet=list(sheet.size),maxSpritesPerScanline=5)))
