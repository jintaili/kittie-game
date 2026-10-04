"""Native 40x32 Kittie pixels. The fixed face is shared by every local motion.

Frames: 0 rest, 1 breath/tail lift, 2 tail settle, 3-6 walk, 7 paw reach,
8 swat follow-through, 9 airborne, 10-13 idle cuddle, 14 pleased bob, 15 recoil.
Reference photos: source-art/character-reference/reference-current-front.png
and reference-current-side.png, copied unchanged from the owner's Kittie folder.
Keep the photographed crown, closed eyes and stitched crescent grin in every pose.
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
# Preserve the approved cuddle hand shapes and an explicit pilot before image.
BEFORE = SOURCE / 'kittie-pilot-before.png'
if not BEFORE.exists():
    BEFORE.write_bytes(ASSET.read_bytes())
approved_sheet = Image.open(BEFORE).convert('RGB')
# Each anatomy revision reads the owner's original photographs, not just sprites.
reference = json.loads((SOURCE/'character-reference/reference.json').read_text())
for asset in reference['assets']:
    assert hashlib.sha256(Path(asset['source']).read_bytes()).hexdigest() == asset['sha256']
T, L, M, D = '#65ff00', '#e0f8cf', '#86c06c', '#071821'
PALETTE = {T:'#efe5d3', L:'#dcc6a3', M:'#aa8e6d', D:'#392b26'}
NAMES = ['rest','breath','tail-settle','walk-a','walk-b','walk-c','walk-d','paw-reach','paw-follow','air-tuck','cuddle-reach','cuddle-open','cuddle-squeeze','cuddle-release','happy','ouch']

def layer():
    return Image.new('RGBA', SIZE, (0,0,0,0))

def paw(draw, box, radius=2):
    # One-pixel contour and the same taupe fill as the torso and hind paws.
    draw.rounded_rectangle(box, radius=radius, fill=M, outline=D, width=1)

def leg_tilt(points, anchor, floor, dx):
    """The selected C1 study's outward stance, on the same native grid."""
    return [(x + round(dx * max(0, y-anchor) / (floor-anchor)), y)
            for x, y in points]

def leg_step(points, lift=0, toe=0):
    # Keep the sewn attachments fixed; motion stays at the short foot ends.
    return [(x + (toe if y >= 30 else 0), y - (lift if y >= 29 else 0))
            for x, y in points]

# The owner's plush has a low oval head and a broad stitched crescent grin.
face = layer()
d = ImageDraw.Draw(face)
d.polygon([(22,12),(29,11),(35,12),(38,14),(39,17),(39,21),
           (36,24),(31,25),(24,25),(20,23),(17,20),(17,16),(19,14)],fill=D)
d.polygon([(22,13),(29,12),(35,13),(37,15),(38,17),(38,21),
           (35,23),(31,24),(24,24),(20,22),(18,20),(18,16),(20,14)],fill=M)
d.polygon([(23,14),(29,13),(34,14),(37,16),(38,19),(36,22),
           (31,24),(24,23),(20,21),(19,18),(20,16)],fill=L)
# Small rounded ears droop into the cheeks. The cap has a central pointed lobe.
d.polygon([(18,15),(18,12),(19,11),(21,12),(23,14),(21,17),(20,18)],fill=D)
d.polygon([(33,12),(35,11),(36,11),(37,12),(37,15),(35,16)],fill=D)
d.polygon([(21,13),(24,12),(28,12),(30,13),(31,15),(27,14),(24,15),(22,15)],fill=D)
d.polygon([(31,12),(34,12),(35,14),(33,14)],fill=D)
# Eyes are two clean arches, separated from cap, nose and mouth.
d.line([(22,18),(23,17),(25,17),(26,18)],fill=D)
d.line([(31,18),(32,17),(34,17),(35,18)],fill=D)
# Pale raised nose on a small shaded muzzle, then the photographed wide grin.
d.line((28,19,30,19),fill=M);d.point((29,19),fill=L)
d.line([(23,20),(24,22),(26,23),(31,23),(34,22),(35,20)],fill=D)
d.line((29,20,29,23),fill=D)
d.point((26,22),fill=D);d.point((32,22),fill=D)
d.line((19,20,22,20),fill=M)
d.line((36,20,38,19),fill=M)

def draw_frame(index):
    if index >= 14:
        # Reactions use the plush body and paws, never redraw his embroidery.
        return draw_frame(1 if index == 14 else 9)
    if index >= 10:
        im = draw_frame(0)
        d = ImageDraw.Draw(im)
        # The forepaws leave the ground only during a stationary cuddle.
        # Keep the low belly, hind paws and every face pixel in place.
        d.rectangle((27,26,39,31),fill=T)
        d.line((26,27,28,28),fill=D,width=1)
        if index in (10,13):
            paw(d,(29,25,35,28),radius=1)
            paw(d,(36,24,39,27),radius=1)
        else:
            squeeze = index == 12
            # Two small paws cup opposite sides of an 8px ball at (35,29).
            d.line((28,27,31,29),fill=D,width=1)
            paw(d,(30+squeeze,27,33+squeeze,31),radius=1)
            paw(d,(38-squeeze,26,39,30),radius=1)
        # Preserve every approved cuddle forepaw pixel and the ball space.
        im.paste(approved_sheet.crop((index*40+25,24,index*40+40,32)), (25,24))
        im.paste(face,mask=face.getchannel('A'))
        return im
    im = Image.new('RGB', SIZE, T)
    d = ImageDraw.Draw(im)
    # Long thick tail, two separated dark bands, plus its dark tip.
    ty = [0,-1,1,0,0,0,0,0,-1,-1][index]
    tail = layer(); q = ImageDraw.Draw(tail)
    q.polygon([(1,14+ty),(4,13+ty),(8,15+ty),(13,17),(17,20),(16,24),(12,22),(8,20+ty),(4,18+ty),(1,17+ty)],fill=M,outline=D,width=1)
    q.polygon([(1,14+ty),(3,14+ty),(3,17+ty),(1,17+ty)],fill=D)
    q.line([(6,15+ty),(6,18+ty)],fill=D,width=2)
    q.line([(10,17+ty),(9,20+ty)],fill=D,width=2)
    q.point((4,15+ty),fill=L); q.point((8,17+ty),fill=L)
    # Cover tail root with the rear haunch; root never detaches.
    im.paste(tail,mask=tail.getchannel('A'))
    # Short legs flow out of the body and end in low toes.
    walk = [0,0,0,-1,0,1,0,0,0,0][index]
    air = index == 9
    front_lift = 1 if index in (4,9) else 0
    hind_lift = 1 if index in (6,9) else 0
    d = ImageDraw.Draw(im)
    # Far toes are partly hidden by the low belly and near legs.
    d.polygon(leg_step(leg_tilt([(18,26),(22,26),(22,29),
               (21,30),(18,30),(17,29)],26,30,-1),hind_lift),fill=M,outline=D)
    breath = 1 if index == 1 else 0
    d.polygon([(9,24),(11,22),(16,20),(21,20),(25,22),(28,25),
               (26,28+breath),(22,29),(13,29),(9,27)],fill=M,outline=D,width=1)
    d.line([(13,24),(17,22),(20,22)],fill=L)
    d.line([(17,27),(21,27)],fill=L)
    # Shoulder stays fixed. Only the last two toe rows shift during a step.
    hx=walk
    lift=hind_lift
    d.polygon(leg_step(leg_tilt([(12,25),(16,25),(16,29),(16,30),
               (16,31),(12,31),(11,30),(12,28)],25,31,-2),lift,hx),
              fill=M,outline=D,width=1)
    d.line((12,25,16,25),fill=M)
    d.point(leg_tilt([(13,28)],25,31,-2)[0],fill=L)
    # Low chest joins the two forelegs; only their bottom tips separate.
    d.polygon([(24,24),(37,24),(38,26),(38,28),(29,29),(25,27)],
              fill=M,outline=D,width=1)
    d.rectangle((27,25,37,27),fill=M)
    d.polygon(leg_step(leg_tilt([(34,25),(38,25),(38,29),
               (37,30),(34,30)],25,30,1),front_lift),
              fill=M,outline=D,width=1)
    # The near foreleg slopes forward into a flattened, clipped toe.
    px=[0,0,0,1,0,-1,0,5,3,1][index]
    py=[0,0,0,0,0,0,0,-2,-1,-2][index]
    lift=front_lift
    if index in (7,8):
        d.polygon([(26+px,24+py),(29+px,25+py),(29+px,27+py),
                   (31+px,28+py),(33+px,29+py-lift),(33+px,30+py-lift),
                   (32+px,31+py-lift),(29+px,31+py-lift),(27+px,30+py-lift),
                   (26+px,28+py),(25+px,26+py)],fill=M,outline=D,width=1)
        d.line([(26+px,25+py),(27+px,26+py),(28+px,26+py)],fill=M)
        d.line((29+px,29+py-lift,30+px,29+py-lift),fill=L)
    else:
        d.polygon(leg_step(leg_tilt([(27,25),(31,25),(31,29),(31,30),
                   (31,31),(27,31),(27,29)],25,31,2),lift,px),
                  fill=M,outline=D,width=1)
        d.line((27,25,31,25),fill=M)
        d.point(leg_tilt([(29,28-lift)],25,31,2)[0],fill=L)
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
contact=Image.new('RGB',(200,176),'#efe5d3')
d=ImageDraw.Draw(contact)
for i,p in enumerate(previews):
    x=(i%5)*40;y=(i//5)*44
    contact.paste(p,(x,y))
    d.text((x+2,y+32),str(i),fill='#392b26')
contact.save(SOURCE/'kittie-contact-native.png')
contact.resize((800,704),Image.Resampling.NEAREST).save(SOURCE/'kittie-contact-4x.png')
# Long idle hold, local breath, then walk/swat/air poses with intentional timing.
sequence=[0,1,0,2,0,3,4,5,6,3,4,5,6,0,7,8,0,9,0]
durations=[700,240,500,180,700,120,120,120,120,120,120,120,120,450,120,160,450,400,700]
for scale in (1,4):
    loop=[previews[i].resize((40*scale,32*scale),Image.Resampling.NEAREST) for i in sequence]
    loop[0].save(SOURCE/f'kittie-motion-{scale}x.gif',save_all=True,append_images=loop[1:],duration=durations,loop=0,disposal=2)
(SOURCE/'kittie-animation.json').write_text(json.dumps(dict(canvas=[40,32],frames=NAMES,sourcePreviewSequence=sequence,sourcePreviewDurationMs=durations,engineSelection='actor_set_dir then actor_set_frame_offset; anim_tick=ANIM_PAUSED',maxSpritesPerScanline=5,unique8x16Pairs=len(patterns)),indent=2)+'\n')
print(json.dumps(dict(frames=len(frames),unique8x16Pairs=len(patterns),sheet=list(sheet.size),maxSpritesPerScanline=5)))
