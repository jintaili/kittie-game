"""Montage of retained, unmodified emulator frame pixels with captions above."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
ROOT=Path(__file__).resolve().parents[1]
upper=ROOT/'artifacts/playtests/session-66897853-ebac-4b87-88c0-71b61a4ab693'
lower=ROOT/'artifacts/playtests/session-65782275-51c3-42c5-a3c7-864cd5d6e1d9'
segments=[(upper,512,564,'BAT THE GOON'),(lower,692,814,'LOW ROAD: BAT + JUMP'),(upper,696,784,'HIGH ROAD: RIBBON'),(lower,956,1059,'CHECKPOINT + CROSSING'),(upper,1200,1277,'MAKE THE WEDDING PHOTO')]
frames=[];duration=[];font=ImageFont.load_default(size=8)
for root,start,end,label in segments:
    events=[json.loads(s) for s in (root/'events.jsonl').read_text().splitlines()]
    records={e['frame']:e for e in events if e['kind']=='frame' and start<=e['frame']<=end}
    chosen=sorted(records)
    for i,n in enumerate(chosen):
        im=Image.new('RGB',(160,160),'#f5edd8');d=ImageDraw.Draw(im);d.text((4,3),label,font=font,fill='#403b3d')
        im.paste(Image.open(root/records[n]['file']).convert('RGB'),(0,16))
        frames.append(im.resize((480,480),Image.Resampling.NEAREST))
        duration.append(max(20,round(((chosen[i+1]-n) if i+1<len(chosen) else 20)*1000/59.7275)))
frames[0].save(ROOT/'artifacts/action-playthrough.gif',save_all=True,append_images=frames[1:],duration=duration,loop=0,disposal=2)
frames[10].save(ROOT/'artifacts/action-still.png')
print(f'{len(frames)} frames, {sum(duration)/1000:.1f} seconds')
