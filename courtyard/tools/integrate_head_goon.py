"""Insert the Head Goon while preserving all prior stage and actor identities."""
from pathlib import Path
import json,copy,uuid
R=Path(__file__).resolve().parents[1]
def load(p):return json.loads((R/p).read_text())
def save(p,x):
 p=R/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+'\n')
def uid(s):return str(uuid.uuid5(uuid.NAMESPACE_URL,'kittie-head-goon/'+s))
def ev(k,c,a=None,ch=None):
 x=dict(id=uid(k),command=c,args=a or {})
 if ch is not None:x['children']=ch
 return x
def val(k,v,n,t='number'):return ev(k,'EVENT_SET_VALUE',dict(variable=v,value=dict(type=t,value=n)))
def cond(k,v,op,n,yes):return ev(k,'EVENT_IF_VALUE',dict(variable=v,operator=op,comparator=n),dict(true=yes,false=[]))
def switch(k,s):return ev(k,'EVENT_SWITCH_SCENE',dict(sceneId=s,x=dict(type='number',value=4),y=dict(type='number',value=15),direction='right',fadeSpeed='1'))
names=['start','the_olive_grove','villa_terraces','head_goon','the_wedding_banquet']
scene=load('project/scenes/villa_terraces/scene.gbsres');scene.update(id=uid('scene'),name='Head Goon',symbol='scene_head_goon',type='head_goon',width=60,backgroundId=uid('background'),x=4700,_index=3)
save('project/scenes/head_goon/scene.gbsres',scene)
for p in (R/'project/scenes/villa_terraces/actors').glob('*.gbsres'):
 a=json.loads(p.read_text());a.update(id=uid('actor/'+p.stem),symbol='actor_head_goon_'+p.stem.replace('_wool','_ball'),x=min(a['x'],55),y=min(a['y'],15))
 if a['_index']==19:continue
 if a['_index']==4:a.update(name='Hop landing cue',spriteSheetId=uid('target-sprite'))
 if a['_index']==3:a.update(name='Head Goon',spriteSheetId=uid('sprite'),x=34,y=15)
 save('project/scenes/head_goon/actors/'+p.name,a)
bg=load('assets/backgrounds/villa.png.gbsres');bg.update(id=uid('background'),name='Head Goon passage',symbol='bg_head_goon',filename='head_goon.png',width=60,imageWidth=480,tileColors='');save('assets/backgrounds/head_goon.png.gbsres',bg)
for n in ['villa_terraces','head_goon']:
 for p in (R/f'project/scenes/{n}/actors').glob('*.gbsres'):
  a=json.loads(p.read_text());w=160 if n=='villa_terraces' else 60
  a['x']=min(a['x'],w-5);a['y']=min(a['y'],15);p.write_text(json.dumps(a,indent=2)+'\n')
ids=[]
for i,n in enumerate(names):
 p=f'project/scenes/{n}/scene.gbsres';s=load(p);s['_index']=i;save(p,s);ids.append(s['id'])
for n,i in [('kittie_title',5),('the_wedding_photo',6)]:
 p=f'project/scenes/{n}/scene.gbsres';s=load(p);s['_index']=i;save(p,s)
variables=load('project/variables.gbsres')
for id,name,symbol in [('114','Head Goon personal best','var_boss_best'),('115','Title selector enabled','var_title_selector')]:
 if not any(v['id']==id for v in variables['variables']):variables['variables'].append(dict(id=id,name=name,symbol=symbol))
save('project/variables.gbsres',variables)
settings=load('project/settings.gbsres');settings['defaultPlayerSprites']['head_goon']=settings['defaultPlayerSprites']['villa'];save('project/settings.gbsres',settings)
engine=load('plugins/kittie/engine/engine.json')
if not any(s['key']=='head_goon' for s in engine['sceneTypes']):engine['sceneTypes'].insert(3,dict(key='head_goon',label='Kittie Head Goon',files=['include/states/head_goon.h','src/states/head_goon.c']))
save('plugins/kittie/engine/engine.json',engine)
if not (R/'plugins/kittie/engine/include/states/head_goon.h').exists():
 (R/'plugins/kittie/engine/include/states/head_goon.h').write_text('#ifndef HEAD_GOON_H\n#define HEAD_GOON_H\n#include <gbdk/platform.h>\nvoid head_goon_init(void) BANKED;\nvoid head_goon_update(void) BANKED;\n#endif\n')
if not (R/'plugins/kittie/engine/src/states/head_goon.c').exists():
 (R/'plugins/kittie/engine/src/states/head_goon.c').write_text('#pragma bank 255\n#include "states/head_goon.h"\n#include "states/kittie.h"\nvoid head_goon_init(void) BANKED { kittie_start_stage(3); }\nvoid head_goon_update(void) BANKED { kittie_update(); }\n')
p=R/'plugins/kittie/engine/src/states/banquet.c';p.write_text(p.read_text().replace('kittie_start_stage(3)','kittie_start_stage(4)'))
best=['105','108','109','114','110'];labels=['COURTYARD','GROVE','VILLA','HEAD GOON','BANQUET'];photoid=load('project/scenes/the_wedding_photo/scene.gbsres')['id']
base=load('project/scenes/start/triggers/photo_finish.gbsres')
for i,n in enumerate(names):
 paths=list((R/f'project/scenes/{n}/triggers').glob('*.gbsres'));t=load(str(paths[0].relative_to(R))) if paths else copy.deepcopy(base)
 if not paths:t.update(id=uid('finish'),name='Head Goon clear',symbol='trigger_head_goon_clear')
 t['x']=[154,214,154,54,174][i];k=n+'/result';changed=lambda s:val(k+s,'107',1)
 t['script']=[val(k+'/schema','111',19539),val(k+'/family1','112',0x4b48),val(k+'/family2','113',0x4f50),val(k+'/reset','107',0),cond(k+'/unlock','100','<',i+1,[val(k+'/set','100',i+1),changed('/unlockchange')]),ev(k+'/best','EVENT_IF_VALUE_COMPARE',dict(vectorX='104',operator='>',vectorY=best[i]),dict(true=[val(k+'/setbest',best[i],'104','variable'),changed('/bestchange')],false=[])),cond(k+'/save','107','==',1,[ev(k+'/write','EVENT_SAVE_DATA',dict(saveSlot=0),dict(true=[],load=[]))]),ev(k+'/text','EVENT_TEXT',dict(text=f'{labels[i]} CLEAR\n'+('HITS' if i==3 else 'GOONS')+f' $102$ BALL $103$\nSCORE $104$ BEST ${best[i]}$\nA CONTINUE',minHeight=6,maxHeight=6,textHeight=4,position='top')),switch(k+'/next',ids[i+1] if i<4 else photoid)]
 save(str(paths[0].relative_to(R)) if paths else 'project/scenes/head_goon/triggers/head_goon_clear.gbsres',t)
title=load('project/scenes/kittie_title/scene.gbsres')
loop=[cond('title/choice'+str(i),'101','==',i+1,[switch('title/go'+str(i),s)]) for i,s in enumerate(ids)]
loop.append(ev('title/wait','EVENT_WAIT',dict(units='frames',frames=dict(type='number',value=1))))
title['script']=[val('title/pilot','106',19537),val('title/schema','111',19539),val('title/enabled','115',1),ev('title/unlock','EVENT_SCRIPT_UNLOCK'),ev('title/loop','EVENT_LOOP',{},dict(true=loop))];save('project/scenes/kittie_title/scene.gbsres',title)
level=dict(width=480,initial_gate=1,door_index=0,solids=[[160,0,168,128],[320,0,328,128]],gate_indices=[0,1],gaps=[],goons=[[216,280],[0,0],[0,0]],goon_heights=[128,128,128],balls=[[188,124]],courts=[dict(bell_x=0,bell_y=0),dict(bell_x=0,bell_y=0)],camera_entries=[0,184],camera_centers=[80,240],lifts=[]);save('tools/head_goon.json',level)
# The older bulk helper must not silently restore four-stage flow over this version.
p=R/'tools/integrate_four_stages.py';s=p.read_text();guard="if (ROOT/'project/scenes/head_goon').exists():\n    raise SystemExit('Use integrate_head_goon.py for the five-stage project.')\n"
if guard not in s:s=s.replace("ROOT=Path(__file__).resolve().parents[1]\n","ROOT=Path(__file__).resolve().parents[1]\n"+guard);p.write_text(s)
print('Five-stage resources integrated.')
