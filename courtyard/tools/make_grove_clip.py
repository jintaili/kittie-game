"""Caption retained native game frames; leave gameplay pixels unchanged."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
RECORDING = ROOT / 'artifacts/playtests/session-27ef71bc-5a4f-4eda-aa9b-72bbab5171b3'
SEGMENTS = [
    (1330, 1510, 'INTO THE OLIVE GROVE'),
    (1720, 1869, 'STONE STEPS AND CHANNELS'),
    (1869, 2002, 'LOWER PATH: GOON + GAP'),
    (3810, 3962, 'UPPER PATH: OPTIONAL BALL'),
    (2100, 2251, 'WIDER TERRACE GAPS'),
    (2330, 2430, 'THROW, CATCH, KEEP GOING'),
    (3188, 3290, 'FALL: RESTART THIS LEVEL'),
    (4530, 4601, 'EMPTY? LOCAL BALL AHEAD'),
    (4601, 4819, 'LAST BELL AND GROVE CLEAR'),
]
events = [json.loads(line) for line in (RECORDING / 'events.jsonl').read_text().splitlines()]
records = {e['frame']: e for e in events if e['kind'] == 'frame'}
font = ImageFont.load_default(size=8)
frames, durations, stills = [], [], []
for start, end, caption in SEGMENTS:
    numbers = sorted(n for n in records if start <= n <= end)
    assert numbers, caption
    for i, n in enumerate(numbers):
        canvas = Image.new('RGB', (160, 160), '#f5edd8')
        ImageDraw.Draw(canvas).text((3, 3), caption, font=font, fill='#403b3d')
        canvas.paste(Image.open(RECORDING / records[n]['file']).convert('RGB'), (0, 16))
        frames.append(canvas.resize((480, 480), Image.Resampling.NEAREST))
        elapsed = numbers[i + 1] - n if i + 1 < len(numbers) else 28
        durations.append(max(20, round(elapsed * 1000 / 59.7275)))
        if i == len(numbers) // 2:
            stills.append(canvas.resize((320, 320), Image.Resampling.NEAREST))
frames[0].save(ROOT / 'artifacts/grove-playthrough.gif', save_all=True,
               append_images=frames[1:], duration=durations, loop=0, disposal=2)
sheet = Image.new('RGB', (960, 960), '#f5edd8')
for i, still in enumerate(stills):
    sheet.paste(still, ((i % 3) * 320, (i // 3) * 320))
sheet.save(ROOT / 'artifacts/grove-contact.png')
print(f'{len(frames)} genuine frames; {sum(durations) / 1000:.1f} seconds')
