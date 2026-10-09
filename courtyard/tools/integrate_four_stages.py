"""Apply deterministic four-stage resources while preserving existing resource IDs."""
from pathlib import Path
import copy, json, uuid
ROOT=Path(__file__).resolve().parents[1]
if (ROOT/'project/scenes/head_goon').exists():
    raise SystemExit('Use integrate_head_goon.py for the five-stage project.')
def load(p): return json.loads((ROOT/p).read_text())
def save(p,data):
    p=ROOT/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(data,indent=2)+'\n')
def uid(s): return str(uuid.uuid5(uuid.NAMESPACE_URL,'kittie-four-stage/'+s))
def ev(key,command,args=None,children=None):
    d=dict(id=uid(key),command=command,args=args or {})
    if children is not None:d['children']=children
    return d
def value(key,var,v,kind='number'):return ev(key,'EVENT_SET_VALUE',dict(variable=var,value=dict(type=kind,value=v)))
def cond(key,var,op,n,yes,no=None):return ev(key,'EVENT_IF_VALUE',dict(variable=var,operator=op,comparator=n),dict(true=yes,false=no or []))
def switch(key,sid):return ev(key,'EVENT_SWITCH_SCENE',dict(sceneId=sid,x=dict(type='number',value=4),y=dict(type='number',value=15),direction='right',fadeSpeed='1'))
names=['start','the_olive_grove','villa_terraces','the_wedding_banquet']
ids=[load(f'project/scenes/{n}/scene.gbsres')['id'] if n!='villa_terraces' else uid('villa-scene') for n in names]
titleid=load('project/scenes/kittie_title/scene.gbsres')['id']
photoid=load('project/scenes/the_wedding_photo/scene.gbsres')['id']
v=load('project/variables.gbsres')
new=[('108','Grove personal best','var_grove_best'),('109','Villa personal best','var_villa_best'),('110','Banquet personal best','var_banquet_best'),('111','Four-stage save schema','var_save_schema'),('112','Save family KH','var_save_family_kh'),('113','Save family OP','var_save_family_op')]
for i,n,s in new:
    if not any(x['id']==i for x in v['variables']):v['variables'].append(dict(id=i,name=n,symbol=s))
v['variables'][2]['name']='Attempt goon points';v['variables'][3]['name']='Attempt retained ball points';v['variables'][3]['symbol']='var_courtyard_ball_points';v['variables'][4]['name']='Completed attempt score'
save('project/variables.gbsres',v)

# Clone only the new Villa's native resources; existing scenes retain identities.
vp='project/scenes/villa_terraces'
if not (ROOT/vp/'scene.gbsres').exists():
    scene=load('project/scenes/the_olive_grove/scene.gbsres')
    scene.update(id=ids[2],name='Villa Terraces',symbol='scene_villa_terraces',type='villa',width=160,backgroundId=uid('villa-background'),x=3300,_index=2)
    scene['script']=[ev('villa-select','EVENT_SET_INPUT_SCRIPT',dict(input=['select'],override=True),dict(true=[switch('villa-cover',titleid)]))]
    save(vp+'/scene.gbsres',scene)
    for p in (ROOT/'project/scenes/the_olive_grove/actors').glob('*.gbsres'):
        a=json.loads(p.read_text());a['id']=uid('villa-actor-'+p.stem);a['symbol']='actor_villa_'+p.stem.replace('_wool','_ball')
        save(vp+'/actors/'+p.name,a)
    bg=load('assets/backgrounds/olive_grove.png.gbsres');bg.update(id=uid('villa-background'),name='Villa Terraces',symbol='bg_villa',filename='villa.png',width=160,imageWidth=1280,tileColors='')
    save('assets/backgrounds/villa.png.gbsres',bg)
for i,n in enumerate(names):
    p=f'project/scenes/{n}/scene.gbsres';s=load(p);s['_index']=i
    if i==3:s['x']=4700
    save(p,s)
    for p in (ROOT/'project/scenes/start/actors').glob('score_*.gbsres'):
        if i==0:continue
        a=json.loads(p.read_text());a['id']=uid(n+'/'+p.stem);a['symbol']='actor_'+n+'_'+p.stem
        save(f'project/scenes/{n}/actors/{p.name}',a)
for n,index in [('kittie_title',4),('the_wedding_photo',5)]:
    p=f'project/scenes/{n}/scene.gbsres';s=load(p);s['_index']=index;save(p,s)
settings=load('project/settings.gbsres');settings['defaultPlayerSprites']['villa']=settings['defaultPlayerSprites']['grove'];save('project/settings.gbsres',settings)
engine=load('plugins/kittie/engine/engine.json')
if not any(s['key']=='villa' for s in engine['sceneTypes']):engine['sceneTypes'].insert(2,dict(key='villa',label='Kittie Villa Terraces',files=['include/states/villa.h','src/states/villa.c']))
save('plugins/kittie/engine/engine.json',engine)
(ROOT/'plugins/kittie/engine/include/states/villa.h').write_text('#ifndef VILLA_STATE_H\n#define VILLA_STATE_H\n#include <gbdk/platform.h>\nvoid villa_init(void) BANKED;\nvoid villa_update(void) BANKED;\n#endif\n')
(ROOT/'plugins/kittie/engine/src/states/villa.c').write_text('#pragma bank 255\n#include "states/villa.h"\n#include "states/kittie.h"\nvoid villa_init(void) BANKED { kittie_start_stage(2); }\nvoid villa_update(void) BANKED { kittie_update(); }\n')
p=ROOT/'plugins/kittie/engine/src/states/banquet.c';p.write_text(p.read_text().replace('kittie_start_stage(2)','kittie_start_stage(3)'))

# Same result accounting for each stage, with separate best slots.
best=['105','108','109','110'];labels=['COURTYARD','GROVE','VILLA','BANQUET']
base=load('project/scenes/start/triggers/photo_finish.gbsres')
for i,n in enumerate(names):
    old=list((ROOT/f'project/scenes/{n}/triggers').glob('*.gbsres'))
    trigger=load(str(old[0].relative_to(ROOT))) if old else copy.deepcopy(base)
    if not old:trigger.update(id=uid(n+'/finish'),symbol='trigger_villa_clear',name='Villa clear')
    trigger['x']=[154,214,154,174][i]
    k=n+'/result';changed=lambda suffix:value(k+suffix,'107',1)
    trigger['script']=[value(k+'/family-kh','112',0x4b48),value(k+'/family-op','113',0x4f50),value(k+'/reset','107',0),cond(k+'/unlock','100','<',i+1,[value(k+'/unlock-set','100',i+1),changed('/unlocked')]),
        ev(k+'/best','EVENT_IF_VALUE_COMPARE',dict(vectorX='104',operator='>',vectorY=best[i]),dict(true=[value(k+'/best-set',best[i],'104','variable'),changed('/improved')],false=[])),
        cond(k+'/save','107','==',1,[ev(k+'/save-write','EVENT_SAVE_DATA',dict(saveSlot=0),dict(true=[],load=[]))]),
        ev(k+'/text','EVENT_TEXT',dict(text=f'{labels[i]} CLEAR\nGOONS $102$ BALL $103$\nSCORE $104$ BEST ${best[i]}$\nA CONTINUE',minHeight=6,maxHeight=6,textHeight=4,position='top')),
        switch(k+'/next',ids[i+1] if i<3 else photoid)]
    save(str(old[0].relative_to(ROOT)) if old else f'project/scenes/{n}/triggers/villa_clear.gbsres',trigger)
photo=load('project/scenes/the_wedding_photo/scene.gbsres')
# The banquet result commits completion before entering the photograph.
photo['script']=[e for e in photo['script'] if e['command']!='EVENT_IF_VALUE']
save('project/scenes/the_wedding_photo/scene.gbsres',photo)
title=load('project/scenes/kittie_title/scene.gbsres')
menu_labels=['COURTYARD','OLIVE GROVE','VILLA','BANQUET']
def menu(unlock):
    args=dict(variable='101',items=4,layout='dialogue',cancelOnB=True,cancelOnLastOption=False)
    for i in range(4):args['option'+str(i+1)]=f'{menu_labels[i]} ${best[i]}$' if i<=unlock else ['','GROVE LOCKED','VILLA LOCKED','BANQUET LOCKED'][i]
    return ev(f'menu/{unlock}','EVENT_MENU',args)
branch=[menu(0)]
for i in range(1,4):branch=[cond(f'menu/branch/{i}','100','>=',i,[menu(i)],branch)]
loop=[ev('menu/await','EVENT_AWAIT_INPUT',dict(input=['a','start'])),*branch]
for i in range(4):
    entry=[switch(f'menu/stage/{i}',ids[i])]
    if i:entry=[cond(f'menu/locked/{i}','100','>=',i,entry,[ev(f'menu/hint/{i}','EVENT_TEXT',dict(text=f'CLEAR {menu_labels[i-1]}\nTO OPEN {menu_labels[i]}'))])]
    loop.append(cond(f'menu/choice/{i}','101','==',i+1,entry))
title['script']=[value('save/pilot-version','106',19537),value('save/schema','111',19538),ev('menu/loop','EVENT_LOOP',{},dict(true=loop))]
save('project/scenes/kittie_title/scene.gbsres',title)

g=load('tools/grove.json');g['solids']=[s for s in g['solids'] if not 688<=s[0]<968]+[[688,72,744,80],[752,104,776,128],[784,72,880,80],[920,64,968,72]];g['solids'].sort();g['gate_indices']=[next(i for i,s in enumerate(g['solids']) if s[0]==x) for x in (320,1640)];g['goons'][1]=[824,864];g['goon_heights'][1]=72;g['balls'][1]=[808,68];
for solid in g['solids']:
    if solid[0]==1192:solid[0]=1184
for gap in g['gaps']:
    if gap[:2]==[1128,1192]:gap[1]=1184
for section in g['sections']:section['action']=section['action'].replace('64-pixel','56-pixel')
save('tools/grove.json',g)
villa=dict(width=1280,initial_gate=1,door_index=255,solids=[[64,48,72,128],[96,112,128,128],[240,64,368,128],[384,112,408,128],[416,96,480,128],[616,80,728,128],[792,112,816,128],[824,96,888,128],[1024,64,1120,128],[1128,96,1176,128],[1216,48,1224,128]],gate_indices=[0,10],gaps=[[480,616,192],[888,1024,192]],goons=[[304,344],[672,712],[1072,1104]],goon_heights=[64,80,64],balls=[[56,124],[440,92],[856,92]],courts=[dict(entry=0,bell_x=0,bell_y=80,gate=64),dict(entry=1120,bell_x=1168,bell_y=56,gate=1216)],camera_entries=[0,1120],camera_centers=[80,1200],lifts=[176,528,936]);save('tools/villa.json',villa)
b=load('tools/banquet.json');b['courts'][0]['bell_x']=184
b['solids']=[s for s in b['solids'] if s[0] not in (536,544,664,680,952,1056)]+[[544,80,624,96],[680,96,816,112],[1056,64,1136,128]];b['solids'].sort();b['gate_indices']=[next(i for i,s in enumerate(b['solids']) if s[0]==x) for x in (280,1312)]
b.update(gaps=[[504,544,192],[624,680,192],[1008,1056,192]],goons=[[424,472],[728,792],[1096,1120]],goon_heights=[128,96,64],balls=[[56,124],[576,76],[976,108]],lifts=[952]);save('tools/banquet.json',b)
print('Four-stage resources integrated; Villa and Banquet await native validation.')
