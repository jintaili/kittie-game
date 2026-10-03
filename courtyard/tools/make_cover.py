"""Reconstruct the device-oriented v10 cover using seven native tile palettes.

The original artwork stays untouched in source-art/approved-cover. Palette maps
are imported with palette_paint; source PNG pixels are GB Studio's four indices.
"""
from pathlib import Path
import hashlib
import json

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'source-art/approved-cover/cover-v10.png'
INDEX_COLORS = ['#e0f8cf', '#86c06c', '#306850', '#071821']
# Fur palettes share their value ramps so an 8x8 boundary cannot change the
# apparent material. Sky and foliage colors are restricted to matching source
# regions, including in tiles that cross Kittie's silhouette.
PALETTES = [
    ['fff7c6', 'f7d65a', '00b5bd', '312119'],
    ['fff7c6', 'b5bd52', '426b29', '213921'],
    ['00b5bd', 'c58c52', '734229', '312119'],
    ['fff7c6', 'deae73', 'ad734a', '312119'],
    ['deae73', 'ad734a', '8c5a39', '312119'],
    ['fff7c6', 'e6a55a', 'b56331', '312119'],
    ['00b5bd', '9cad39', '426b29', '213921'],
]

def build():
    # Sample whole native cells from the deliberately coarse source. There is
    # no photographic texture enhancement or error-diffusion dithering.
    source = Image.open(SOURCE).convert('RGB').resize((160, 144), Image.Resampling.BOX)
    # A tiny 3x5 native prompt occupies only the strip beneath the approved title.
    glyphs = {'A':['010','101','111','101','101'], 'S':['111','100','111','001','111'],
              'T':['111','010','010','010','010'], 'R':['110','101','110','101','101'],
              '/':['001','001','010','100','100'], ' ':['000']*5}
    draw = ImageDraw.Draw(source)
    draw.rectangle((0, 136, 159, 143), fill='#312119')
    for i, ch in enumerate('A / START'):
        for y, row in enumerate(glyphs[ch]):
            for x, bit in enumerate(row):
                if bit == '1':
                    draw.point((62+i*4+x, 138+y), fill='#fff7c6')
    rgb = np.asarray(source, dtype=np.float32)
    palettes = np.array([[tuple(bytes.fromhex(c)) for c in p] for p in PALETTES], dtype=np.float32)
    # RGB555 values, expanded exactly as GBC display colors.
    palettes = np.rint(palettes * 31 / 255) * 255 / 31
    palettes = np.rint(palettes).astype(np.uint8)
    indices = np.empty((144,160), dtype=np.uint8)
    rendered = np.empty((144,160,3), dtype=np.uint8)
    edits = []
    for ty in range(18):
        for tx in range(20):
            tile = rgb[ty*8:ty*8+8,tx*8:tx*8+8]
            # Keep silhouette colors out of the warm plush even within a tile
            # that needs both a sky swatch and a fur swatch.
            delta = tile[None,:,:,None,:] - palettes[:,None,None,:,:]
            distance = (delta**2 * np.array([0.30,0.50,0.20])).sum(axis=-1)
            sky = (tile[:,:,1] > tile[:,:,0]+25) & (tile[:,:,2] > tile[:,:,0]+15)
            foliage = (tile[:,:,1] > tile[:,:,0]+8) & (tile[:,:,1] > tile[:,:,2]+8)
            for pi, palette in enumerate(palettes.astype(float)):
                for ci, color in enumerate(palette):
                    if color[1] > color[0]+25 and color[2] > color[0]+15:
                        distance[pi,:,:,ci][~sky] = float('inf')
                    elif color[1] > color[0]+8 and color[1] > color[2]+8:
                        distance[pi,:,:,ci][~foliage] = float('inf')
            nearest = distance.argmin(axis=-1)
            error = distance.min(axis=-1).sum(axis=(1,2))
            # The title uses the ledge's own palette; the dark footer uses the
            # same cream and espresso. Neither can become a blue shadow field.
            if (3 <= tx <= 16 and 13 <= ty <= 16) or ty == 17:
                error[:] = float('inf')
                error[5] = 0
            slot = int(error.argmin())
            selected = nearest[slot].astype(np.uint8)
            indices[ty*8:ty*8+8,tx*8:tx*8+8] = selected
            rendered[ty*8:ty*8+8,tx*8:tx*8+8] = palettes[slot][selected]
            edits.append({'x':tx,'y':ty,'slot':slot})
    source_palette = np.array([tuple(bytes.fromhex(c[1:])) for c in INDEX_COLORS],dtype=np.uint8)
    Image.fromarray(source_palette[indices]).save(ROOT/'assets/backgrounds/title.png')
    preview = Image.fromarray(rendered)
    preview.save(ROOT/'source-art/approved-cover/native-color.png')
    preview.resize((640,576),Image.Resampling.NEAREST).save(ROOT/'source-art/approved-cover/native-color-4x.png')
    native_sky = (rendered[:,:,1].astype(int) > rendered[:,:,0].astype(int)+25) & (rendered[:,:,2].astype(int) > rendered[:,:,0].astype(int)+15)
    source_sky = (rgb[:,:,1] > rgb[:,:,0]+25) & (rgb[:,:,2] > rgb[:,:,0]+15)
    sky_leaks = int(np.count_nonzero(native_sky & ~source_sky))
    if sky_leaks:
        raise ValueError(f'{sky_leaks} sky-colored pixels escaped the sky region')
    result = {
        'source':str(SOURCE.relative_to(ROOT)),
        'sourceSha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'size':[160,144],
        'palettes':[[''.join(f'{v:02x}' for v in c) for c in p] for p in palettes],
        'edits':edits,
        'uniqueTiles':len({indices[y:y+8,x:x+8].tobytes() for y in range(0,144,8) for x in range(0,160,8)}),
        'colorRules':'Sky teal and foliage green may only map to source regions of that hue; fur uses a shared cream/tan/copper/espresso ramp.',
        'skyPixelsOutsideSourceSky':sky_leaks,
        'maxColorsPerTile':max(len(np.unique(rendered[y:y+8,x:x+8].reshape(-1,3),axis=0)) for y in range(0,144,8) for x in range(0,160,8)),
    }
    (ROOT/'tools/cover-palettes.json').write_text(json.dumps(result,indent=2)+'\n')
    print(f"Cover: 160x144, {result['uniqueTiles']} tiles, 7 palettes; UI palette 7 preserved")

if __name__ == '__main__':
    build()
