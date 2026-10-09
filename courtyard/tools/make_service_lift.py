"""A four-object, 40px slatted deck. Small gaps are narrower than a physical wool ball."""
from pathlib import Path
import json,uuid,hashlib
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
uid=lambda s:str(uuid.uuid5(uuid.NAMESPACE_URL,'kittie-service-lift/'+s))
im=Image.new('RGB',(40,16),'#65ff00');d=ImageDraw.Draw(im)
slats=(0,10,22,32)
for x in slats:
    d.rectangle((x,0,x+7,7),fill='#86c06c',outline='#071821')
    d.line((x+1,1,x+6,1),fill='#e0f8cf');d.line((x+2,5,x+5,5),fill='#071821')
    d.point((x+4,3),fill='#e0f8cf')
p=ROOT/'assets/sprites/service_lift.png';im.save(p)
m=json.loads((ROOT/'assets/sprites/ball.png.gbsres').read_text())
m.update(id=uid('sprite'),name='Service lift',symbol='sprite_service_lift',filename=p.name,width=40,height=16,canvasWidth=40,canvasHeight=16,numTiles=4,checksum=hashlib.sha1(p.read_bytes()).hexdigest(),animSpeed=255)
state=m['states'][0];state.update(id=uid('state'),animationType='fixed',flipLeft=False)
for i,a in enumerate(state['animations']):
    a['id']=uid(f'anim-{i}');a['frames']=[dict(id=uid(f'frame-{i}'),tiles=[dict(id=uid(f'tile-{i}-{x}'),x=x-12,y=0,sliceX=x,sliceY=0,flipX=False,flipY=False,palette=0,paletteIndex=3,objPalette='OBP0',priority=False) for x in slats])]
p.with_suffix('.png.gbsres').write_text(json.dumps(m,indent=2)+'\n')
template=json.loads((ROOT/'project/scenes/start/actors/score_hundreds.gbsres').read_text())
for scene,positions in [('villa_terraces',[176,528,936]),('the_wedding_banquet',[952])]:
    # The shafts are more than two screens apart; one actor renders the local deck.
    for i,x in enumerate(positions[:1]):
        a=dict(template);a.update(id=uid(f'{scene}-{i}'),_index=19+i,symbol=f'actor_{scene}_lift_{i}',name=f'Service lift {i+1}',spriteSheetId=m['id'],isPinned=False,x=x//8,y=15)
        (ROOT/f'project/scenes/{scene}/actors/service_lift_{i}.gbsres').write_text(json.dumps(a,indent=2)+'\n')
im.resize((160,64),Image.Resampling.NEAREST).save(ROOT/'source-art/service-lift-4x.png')
