"""Three clipped 8x16 score objects. Only the bottom eight pixels are visible.

Their upper blank halves sit above the display, so the score adds three OAM
objects on rows0..7 without competing with high-route Kittie below that band.
"""
from pathlib import Path
from PIL import Image
import json,uuid,hashlib

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'source-art'
T,D='#65ff00','#071821'
digits=['11111/10001/10011/10101/11001/10001/11111',
        '00100/01100/00100/00100/00100/00100/01110',
        '11111/00001/00001/11111/10000/10000/11111',
        '11111/00001/00001/01111/00001/00001/11111',
        '10001/10001/10001/11111/00001/00001/00001',
        '11111/10000/10000/11111/00001/00001/11111',
        '11111/10000/10000/11111/10001/10001/11111',
        '11111/00001/00010/00100/01000/01000/01000',
        '11111/10001/10001/11111/10001/10001/11111',
        '11111/10001/10001/11111/00001/00001/11111']
im=Image.new('RGB',(80,16),T)
for n,glyph in enumerate(digits):
    for y,row in enumerate(glyph.split('/')):
        for x,pixel in enumerate(row):
            if pixel=='1':im.putpixel((n*8+x+1,y+9),tuple(bytes.fromhex(D[1:])))
source=SOURCE/'score-digits.png';im.save(source)
sid=str(uuid.uuid5(uuid.NAMESPACE_URL,'kittie-courtyard-score-digits-v1'))
uid=lambda name:str(uuid.uuid5(uuid.UUID(sid),name))
meta=json.loads((ROOT/'assets/sprites/inventory.png.gbsres').read_text())
meta.update(id=sid,name='Courtyard score digits',symbol='sprite_score_digits',filename='score_digits.png',
            width=80,height=16,canvasWidth=8,canvasHeight=16,canvasOriginX=0,canvasOriginY=0,
            checksum=hashlib.sha1(source.read_bytes()).hexdigest(),numTiles=10,animSpeed=255)
state=meta['states'][0];state.update(id=uid('state'),animationType='fixed',flipLeft=False)
for n,animation in enumerate(state['animations']):
    animation['id']=uid(f'animation-{n}')
    animation['frames']=[dict(id=uid(f'frame-{n}-{f}'),tiles=[dict(id=uid(f'tile-{n}-{f}'),x=0,y=8,
        sliceX=f*8,sliceY=0,flipX=False,flipY=False,palette=0,paletteIndex=4,objPalette='OBP0',priority=False)]) for f in range(10)]
path=SOURCE/'score-digits.gbsres';path.write_text(json.dumps(meta,indent=2)+'\n')
print(json.dumps(dict(id=sid,sourceSha256=hashlib.sha256(source.read_bytes()).hexdigest(),metadataSha256=hashlib.sha256(path.read_bytes()).hexdigest())))
