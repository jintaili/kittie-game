"""Standalone native-cell pose sketches. Does not write game resources."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import ast
import hashlib
import json

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
SOURCE = ROOT / 'courtyard/tools/make_kittie.py'
game_asset = ROOT / 'courtyard/assets/sprites/kittie.png'
before = hashlib.sha256(game_asset.read_bytes()).hexdigest()
# Read the authored face and helpers without executing the generator's writes.
tree = ast.parse(SOURCE.read_text())
nodes = []
for node in tree.body:
    if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'frames' for t in node.targets):
        break
    if isinstance(node, ast.If):
        continue  # The optional legacy before-image creation is not a sketch action.
    nodes.append(node)
ns = {'__file__': str(SOURCE)}
exec(compile(ast.Module(body=nodes, type_ignores=[]), str(SOURCE), 'exec'), ns)
T, L, M, D = [ns[k] for k in ('T', 'L', 'M', 'D')]
face = ns['face']

def tilt(points, anchor, floor, dx):
    return [(x + round(dx * max(0, y-anchor) / (floor-anchor)), y) for x,y in points]

def pose(front, rear, far_front, far_rear, fuller=False, ears=False):
    im = Image.new('RGB', (40,32), T)
    d = ImageDraw.Draw(im)
    # Existing authored tail and torso, unchanged from rest frame.
    d.polygon([(1,14),(4,13),(8,15),(13,17),(17,20),(16,24),(12,22),(8,20),(4,18),(1,17)],fill=M,outline=D,width=1)
    d.polygon([(1,14),(3,14),(3,17),(1,17)],fill=D)
    d.line([(6,15),(6,18)],fill=D,width=2)
    d.line([(10,17),(9,20)],fill=D,width=2)
    d.point((4,15),fill=L);d.point((8,17),fill=L)
    w = int(fuller)
    d.polygon(tilt([(18,26),(21+w,26),(21+w,29),(20+w,30),(18,30),(17,29)],26,30,far_rear),fill=M,outline=D)
    d.polygon([(9,24),(11,22),(16,20),(21,20),(25,22),(28,25),(26,28),(22,29),(13,29),(9,27)],fill=M,outline=D,width=1)
    d.line([(13,24),(17,22),(20,22)],fill=L)
    d.line([(17,27),(21,27)],fill=L)
    d.polygon(tilt([(12,25),(15+w,25),(15+w,29),(15+w,30),(15+w,31),(12,31),(11,30),(12,28)],25,31,rear),fill=M,outline=D,width=1)
    d.line((12,25,15+w,25),fill=M)
    d.point(tilt([(13,28)],25,31,rear)[0],fill=L)
    # Preserve the approved filled chest; the paw tips alone move laterally.
    d.polygon([(24,24),(37,24),(38,26),(38,28),(29,29),(25,27)],fill=M,outline=D,width=1)
    d.rectangle((27,25,37,27),fill=M)
    d.polygon(tilt([(35-w,25),(38,25),(38,29),(37,30),(35-w,30)],25,30,far_front),fill=M,outline=D,width=1)
    d.polygon(tilt([(28-w,25),(31,25),(31,29),(31,30),(31,31),(28-w,31),(28-w,29)],25,31,front),fill=M,outline=D,width=1)
    d.line((28-w,25,31,25),fill=M)
    d.point(tilt([(29,28)],25,31,front)[0],fill=L)
    im.paste(face, mask=face.getchannel('A'))
    if ears:
        # Tiny rounded extensions of the photographed dark ears, not the crown.
        d = ImageDraw.Draw(im)
        d.point([(19,10),(20,10),(18,11),(20,11),(35,10),(36,10),(37,11)],fill=D)
    return im

specs = [
    ('A', 'Current', 'Vertical legs', (0,0,0,0), 'The existing upright stance.'),
    ('B', 'Gentle splay', 'About 10 degrees outward', (1,-1,0,0), 'A subtle lean, still very compact.'),
    ('C', 'Relaxed splay', 'About 20 degrees outward', (2,-2,1,-1), 'A broader stance with less rigid legs.'),
    ('D', 'Forward-set paws', 'Front 20 degrees / rear 10 degrees', (2,1,1,0), 'Both near paws sit ahead of their roots.'),
]
palette = {tuple(bytes.fromhex(k[1:])):tuple(bytes.fromhex(v[1:])) for k,v in ns['PALETTE'].items()}
frames = []
baseline = ns['draw_frame'](0)
for letter,title,angle,values,description in specs:
    native = pose(*values)
    if letter == 'A':
        assert native.tobytes() == baseline.tobytes(), 'Comparison baseline must match current source.'
    assert native.crop((0,0,40,25)).tobytes() == baseline.crop((0,0,40,25)).tobytes()
    for y in range(32):
        for x in range(40):
            f = face.getpixel((x,y))
            if f[3]: assert native.getpixel((x,y)) == f[:3]
    native.save(OUT/f'{letter}-native.png')
    colored = native.copy();colored.putdata([palette[p] for p in native.getdata()])
    colored.save(OUT/f'{letter}.png')
    frames.append(colored)

def font(size, bold=False):
    paths = ['/System/Library/Fonts/Supplemental/Arial Bold.ttf' if bold else '/System/Library/Fonts/Supplemental/Arial.ttf', '/System/Library/Fonts/Helvetica.ttc']
    for p in paths:
        if Path(p).exists(): return ImageFont.truetype(p,size)
    return ImageFont.load_default(size=size)

board = Image.new('RGB',(1024,766),'#f4eedf')
d = ImageDraw.Draw(board)
d.text((32,22),'Kittie: leg-angle sketches',fill='#392b26',font=font(30,True))
d.text((32,65),'Same face, body height and filled chest. Native pixels, enlarged 8x.',fill='#665648',font=font(18))
for n,(spec,frame) in enumerate(zip(specs,frames)):
    letter,title,angle,values,description = spec
    x=32+(n%2)*496;y=109+(n//2)*320
    d.rounded_rectangle((x,y,x+464,y+296),radius=12,fill='#e9ddc7',outline='#c8b493',width=1)
    d.text((x+18,y+14),f'{letter}  {title}',fill='#392b26',font=font(23,True))
    d.text((x+18,y+46),angle,fill='#705d49',font=font(16))
    board.paste(frame.crop((0,10,40,32)).resize((320,176),Image.Resampling.NEAREST),(x+70,y+75))
    d.line((x+46,y+251,x+418,y+251),fill='#ac9779',width=2)
    d.text((x+18,y+266),description,fill='#554636',font=font(16))
board.save(OUT/'comparison.png')
assert hashlib.sha256(game_asset.read_bytes()).hexdigest() == before
(OUT/'manifest.json').write_text(json.dumps({'gameSpriteSha256':before,'method':'Authored native-cell sketches from the existing generator, original side photo consulted. No game resources changed.','angleNote':'Approximate near-leg centerline angles from vertical, quantized to 1 or 2 pixels. Far legs use shorter shifts to stay within the fixed canvas.','variants':[{'id':s[0],'title':s[1],'footOffsets':s[3]} for s in specs]},indent=2)+'\n')
