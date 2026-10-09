"""Caption retained native emulator frames without changing gameplay pixels."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
UPPER = ROOT / 'artifacts/playtests/session-a657f376-d1b6-4a36-8c78-a8020bf6ad6c'
CHECKS = ROOT / 'artifacts/playtests/session-9a1a8100-0fec-4e26-a8a8-d7cccf764319'
SEGMENTS = [
    (UPPER, 160, 230, 'COLLECT AND CARRY'),
    (UPPER, 400, 510, 'LOB, THEN RETRIEVE'),
    (UPPER, 530, 580, 'THROW AT A GOON'),
    (UPPER, 674, 834, 'UPPER ROUTE BALL'),
    (CHECKS, 980, 1083, 'LOWER ROUTE COMBAT'),
    (CHECKS, 3948, 4000, 'CONTACT COSTS A HEART'),
    (CHECKS, 3490, 3582, 'FALL: WHOLE LEVEL RESET'),
    (UPPER, 980, 1052, 'LOW THROW UNDER TABLE'),
    (CHECKS, 1450, 1513, 'MAKE THE WEDDING PHOTO'),
]
font = ImageFont.load_default(size=8)
frames, durations = [], []
for root, start, end, caption in SEGMENTS:
    events = [json.loads(line) for line in (root / 'events.jsonl').read_text().splitlines()]
    records = {e['frame']: e for e in events if e['kind'] == 'frame' and start <= e['frame'] <= end}
    numbers = sorted(records)
    for i, n in enumerate(numbers):
        canvas = Image.new('RGB', (160, 160), '#f5edd8')
        ImageDraw.Draw(canvas).text((4, 3), caption, font=font, fill='#403b3d')
        canvas.paste(Image.open(root / records[n]['file']).convert('RGB'), (0, 16))
        frames.append(canvas.resize((480, 480), Image.Resampling.NEAREST))
        elapsed = numbers[i + 1] - n if i + 1 < len(numbers) else 28
        durations.append(max(20, round(elapsed * 1000 / 59.7275)))
frames[0].save(ROOT / 'artifacts/carry-playthrough.gif', save_all=True,
               append_images=frames[1:], duration=durations, loop=0, disposal=2)
frames[12].save(ROOT / 'artifacts/carry-still.png')
print(f'{len(frames)} genuine frames; {sum(durations) / 1000:.1f} seconds')
