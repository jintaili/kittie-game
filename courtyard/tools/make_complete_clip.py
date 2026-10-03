"""Present genuine retained frames from the complete game's recorded branches."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
REC=ROOT/'artifacts/playtests/session-5bdd378f-3e5f-4c5b-ac24-e31080ef57ff'
segments=[
 ('branch-0001',300,420,'KITTIE: CLEARER FACE'),
 ('branch-0001',1670,1900,'GROVE: RAISED STONE ISLANDS'),
 ('branch-0001',1940,2126,'LOWER ROUTE: PATROL + GAP'),
 ('branch-0002',1860,2046,'UPPER ROUTE: OPTIONAL WOOL'),
 ('branch-0001',3250,3510,'BANQUET: ACROSS THE TABLES'),
 ('branch-0002',3680,3724,'CONTACT COSTS A HEART'),
 ('branch-0003',3776,3862,'EMPTY ENTRY: LOCAL WOOL'),
 ('branch-0003',3862,4162,'LAST BELL, WEDDING PHOTO'),
 ('branch-0003',4460,4496,'RESTART: UNLOCKS REMEMBERED'),
]
events=[json.loads(s) for s in (REC/'events.jsonl').read_text().splitlines()]
font=ImageFont.load_default(size=8)
frames=[]; durations=[]; stills=[]
for branch,start,end,caption in segments:
 records={e['frame']:e for e in events if e['kind']=='frame' and e['branchId']==branch and start<=e['frame']<=end}
 numbers=sorted(records);assert numbers
 for i,n in enumerate(numbers):
  canvas=Image.new('RGB',(160,160),'#f5edd8');d=ImageDraw.Draw(canvas)
  d.text((3,3),caption,font=font,fill='#403b3d')
  canvas.paste(Image.open(REC/records[n]['file']).convert('RGB'),(0,16))
  frames.append(canvas.resize((480,480),Image.Resampling.NEAREST))
  durations.append(max(20,round((numbers[i+1]-n if i+1<len(numbers) else 35)*1000/59.7275)))
  if i==len(numbers)//2: stills.append(canvas.resize((320,320),Image.Resampling.NEAREST))
frames[0].save(ROOT/'artifacts/complete-v1-playthrough.gif',save_all=True,append_images=frames[1:],duration=durations,loop=0,disposal=2)
sheet=Image.new('RGB',(960,960),'#f5edd8')
for i,im in enumerate(stills):sheet.paste(im,((i%3)*320,(i//3)*320))
sheet.save(ROOT/'artifacts/complete-v1-contact.png')
# Faithful previews of the before/after native source pixels.
colors={'#65ff00':'#f5edd8','#e0f8cf':'#cbb79b','#86c06c':'#a59077','#071821':'#453126'}
lookup={tuple(bytes.fromhex(k[1:])):tuple(bytes.fromhex(v[1:])) for k,v in colors.items()}
compare=Image.new('RGB',(400,190),'#f5edd8');d=ImageDraw.Draw(compare)
for i,p in enumerate([ROOT/'source-art/three-stage-before/assets/sprites/kittie.png',ROOT/'assets/sprites/kittie.png']):
 im=Image.open(p).convert('RGB').crop((0,0,40,32));im.putdata([lookup[p] for p in im.getdata()])
 compare.paste(im.resize((200,160),Image.Resampling.NEAREST),(i*200,25))
 d.text((i*200+12,6),['BEFORE','VERSION 1'][i],font=ImageFont.load_default(size=12),fill='#403b3d')
compare.save(ROOT/'artifacts/kittie-face-comparison.png')
print(len(frames),'native frames,',round(sum(durations)/1000,1),'seconds')
