"""Study-only one-pixel refinements of the user's selected pose C."""
from pathlib import Path
import ast
import hashlib
import json
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent
# Load drawing definitions without generating or replacing the first study.
tree = ast.parse((OUT/'make_sketches.py').read_text())
nodes=[]
for node in tree.body:
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='specs' for t in node.targets): break
    nodes.append(node)
ns={'__file__':str(OUT/'make_sketches.py')}
exec(compile(ast.Module(body=nodes,type_ignores=[]),'study-definitions','exec'),ns)
pose=ns['pose']; palette={tuple(bytes.fromhex(k[1:])):tuple(bytes.fromhex(v[1:])) for k,v in ns['ns']['PALETTE'].items()}
baseline=pose(2,-2,1,-1)
assert baseline.tobytes()==Image.open(OUT/'C-native.png').convert('RGB').tobytes()
specs=[
    ('C','Approved angle',False,False,'Your selected stance, unchanged.'),
    ('C1','Fuller legs',True,False,'One pixel wider; same length and angle.'),
    ('C2','More visible ears',False,True,'One extra row at the soft ear tips.'),
    ('C3','Both together',True,True,'Fuller legs and slightly clearer ears.'),
]
def font(size,bold=False):
    p=Path('/System/Library/Fonts/Supplemental')/('Arial Bold.ttf' if bold else 'Arial.ttf')
    return ImageFont.truetype(str(p),size)
board=Image.new('RGB',(1024,784),'#f4eedf');d=ImageDraw.Draw(board)
d.text((32,22),'Kittie: small refinements to C',fill='#392b26',font=font(30,True))
d.text((32,65),'One-pixel changes. Same low body, face embroidery and relaxed leg angle.',fill='#665648',font=font(18))
changes=[]
for n,(key,title,fuller,ears,caption) in enumerate(specs):
    native=pose(2,-2,1,-1,fuller=fuller,ears=ears)
    delta=[(x,y) for y in range(32) for x in range(40) if native.getpixel((x,y))!=baseline.getpixel((x,y))]
    assert all(y>=25 or (ears and (x,y) in [(19,10),(20,10),(18,11),(20,11),(35,10),(36,10),(37,11)]) for x,y in delta)
    native.save(OUT/f'refined-{key}-native.png')
    colored=native.copy();colored.putdata([palette[p] for p in native.get_flattened_data()]);colored.save(OUT/f'refined-{key}.png')
    x=32+(n%2)*496;y=109+(n//2)*328
    d.rounded_rectangle((x,y,x+464,y+306),radius=12,fill='#e9ddc7',outline='#c8b493',width=1)
    d.text((x+18,y+15),f'{key}  {title}',fill='#392b26',font=font(23,True))
    d.text((x+18,y+47),'Relaxed outward stance',fill='#705d49',font=font(16))
    board.paste(colored.crop((0,9,40,32)).resize((320,184),Image.Resampling.NEAREST),(x+70,y+75))
    d.line((x+46,y+259,x+418,y+259),fill='#ac9779',width=2)
    d.text((x+18,y+275),caption,fill='#554636',font=font(16))
    changes.append({'id':key,'changedPixels':len(delta),'coordinates':delta})
board.save(OUT/'comparison-refined.png')
assert hashlib.sha256(ns['game_asset'].read_bytes()).hexdigest()==ns['before']
(OUT/'refinement-manifest.json').write_text(json.dumps({'reference':'Original reference-current-front.png consulted; C chosen by user.','gameSpriteSha256':ns['before'],'gameChanged':False,'changes':changes},indent=2)+'\n')
