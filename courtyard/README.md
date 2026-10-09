# Development notes

Open `project.gbsproj` in GB Studio 4.3.2 and export a Game Boy Color ROM, or use
the ModRetro build tools with this project selected. Authored PNGs, sidecars and
custom engine code are build inputs; regeneration is not needed to compile.
Python art generators require Pillow. Do not edit practice copies under `build/`.

The [root README](../README.md) covers releases and play;
[AGENTS.md](../AGENTS.md) defines character references, approved gameplay and
review requirements. The [current guide](../design/head-goon-preview.html)
records build-specific validation. Historical reviews describe earlier builds.

## Engine and gameplay

Custom scene types live in `plugins/kittie/engine`; no engine was ejected.
`kittie.c` shares signed 12.4 physics across stages. `grove.c`, `villa.c`,
`head_goon.c` and `banquet.c` initialize stages 1 through 4.

Start retries; Select returns to the cover. Water and zero hearts reset the
stage. There are no checkpoints. Traversal stages have three physical wool
balls; Head Goon has one. Balls ring bells and damage enemies, with physical
retrieval and no jump boost or automatic return.

Ordinary goons move at 12 fixed-point units per update, or 0.75 pixels, reflecting
at patrol endpoints. The Head Goon uses that walking speed between committed
hops. His target locks during each 28-update windup. One hop precedes recovery
at full health; two precede it after the first hit. Recovery lasts 72 updates,
with 54 updates of patrol between sequences. Only recovery accepts ball hits.
Contact hurts during recovery and flinching too; defeat is harmless. The flinch
branch calls the shared contact helper before returning. Kittie's existing
60-update damage protection and the ball's rebound are preserved.

## Geometry and generators

`tools/level.json`, `grove.json`, `villa.json`, `head_goon.json` and `banquet.json`
own geometry and pickup placement. `tools/make_level_data.py` generates
`kittie_levels.h`; `kittie_level.h` is unused. Rectangles must be sorted by both
left and right edges for collision scanning. Keep stage width below 2,000 pixels
for signed 12.4 coordinates. Moving decks use a separate collision path.

| Generator | Responsibility |
| --- | --- |
| `tools/make_level.py` | Courtyard background |
| `tools/make_world_art.py` | Grove and legacy world entry points; dispatches Banquet to its dedicated generator and preserves the approved title |
| `tools/make_grove.py` | Grove compatibility entry point |
| `tools/make_banquet.py` | Banquet art and lift rails |
| `tools/make_head_goon.py` | Head Goon family art and encounter assets |
| `tools/make_service_lift.py` | Four-slat lift, matching its 40-pixel collision width |
| `tools/make_kittie.py` | 40×32 character, 16 frames with fixed face pixels |
| `tools/make_cover.py` | Native v10 cover and asymmetric whisker correction |
| `tools/make_carry_assets.py` | Wool, shutter and legacy sprite HUD assets |
| `tools/make_feedback_art.py` | Four-frame bell and gate reactions |
| `tools/make_compact_hud.py` | Current window HUD glyphs and preview |

Do not run older `tools/make_art.py` over current assets. Source colors are import
indices, not final palettes. Repaint native attributes with `palette_paint` after
geometry changes; `tools/*-palettes.json` files hold paint regions.

`tools/make_water_motion.py` generates four phases for the courtyard's two water
tiles in `kittie_water.h`. `tools/make_world_motion.py` generates grove leaf tips
and banquet bunting in `kittie_world_motion.h`. Run them after regenerating their
backgrounds. Runtime motion depends on compiled tile IDs, banks and flips;
verify that those tiles occur only in intended cells, including flipped copies,
and inspect a complete native loop. Keep terrain edges readable.

The cover uses 160×144 pixels, 302 source tiles and seven palettes; the eighth
palette is reserved for UI. `tools/cover-palettes.json` and the background sidecar
own its palette assignments. The full-size v10 source stays untouched. The ending
uses the gameplay sprite. Original character references and hashes are in
`source-art/character-reference/`.

Wool has blank top padding and a compensating tile offset to avoid deck overlap.
Bell hits animate for 48 updates and leave a green bell and open gate marker;
the courtyard camera holds during the reaction. Skip offscreen bell/gate pose
updates, which previously caused missed native frames. Low tables have a 14-pixel
wool passage. Removed world captions must not return through regeneration.

## Actor and palette allocation

| Actor indices | Use |
| --- | --- |
| 0 | Player |
| 1, 8–12 | Balls |
| 2–3 | Gates |
| 4–6 | Goons; Head Goon uses 4 for himself and 5 for the landing cue |
| 7 | Entry shutter |
| 13–14, 17–19 | Hidden legacy HUD actors; retain indices |
| 15–16 | Bells |
| 20 | Visible lift in Villa and Banquet |

The boss bypasses ordinary 110-pixel culling so he stays visible across the fixed
arena. Lift shafts are farther apart than the viewport; all decks move offscreen.
Sprite palettes are Kittie/gates 0, wool 1, goons 2, resting bells 3, HUD source 4,
and rung bells/open gates 5. Goons' ground heights come from stage JSON.
Door index 255 means no entry shutter; collision, rendering and closure code must
handle it. Grove and Banquet use this to permit backtracking.

The HUD has three heart slots, centered score and three wool slots. Seven-pixel
glyphs have one empty row above them. `kittie_hud.c` manages the clipped window,
cached updates and palette restoration before dialogs or title transitions.
It uses no OAM objects. Bank-one tiles C0–D8 must remain outside scene background
and actor allocations. Do not reactivate the legacy sprite HUD.

## Scores and saves

Native scene scripts connect all five stages and the ending. Authored variable
IDs 100–115 map to compiled global indices 0–15:

| IDs | Values |
| --- | --- |
| 100 | Highest unlock: 0 fresh, 1 Grove, 2 Villa, 3 Head Goon, 4 Banquet, 5 complete |
| 101 | Menu choice |
| 102–107 | Goon points, wool points, attempt score, Courtyard best, legacy save version, save-needed flag |
| 108–111 | Grove best, Villa best, Banquet best, save schema |
| 112–113 | Stable family words 0x4b48 / 0x4f50 |
| 114–115 | Head Goon best, selector state |

Traversal stages award 100 per unique defeated goon and 200 per held ball at
completion, up to 900. Head Goon awards 100 per hit and 200 for retained wool,
up to 500. Each throw can damage him once; guarded hits give no points.
Retries clear attempt scores. A completion updates only higher bests and unlocks,
then saves slot 0 if either changed. Saves record progress, not mid-stage position.

`kittie_title.c` loads bounded progress from VM globals without restoring
cross-build scene state. Schema 19539 is current; 19538 imports four-stage saves.
Both require the family marker, expected block size and valid unlock/score ranges.
Four-stage unlocks 3/4 map to 4/5, with boss best initialized to zero.
Legacy three-stage unlocks 2/3 map to 4/5. Reviewed pilot native/web signatures
allow score and unlock migration; published v1.0.0 allows unlock-only migration.
Keep these legacy checks separate from current schemas, whose compatibility
must not depend on compiler-generated save IDs.

Compile-time guards preserve global indices. Block validation uses the full
`sizeof(script_memory)`, including VM context stacks. Browser storage remains
separate across preview URLs; this loader does not transfer it.

## Audio and release maintenance

`kittie_music.c` uses pulse 2 for melody, wave for bass and pulse 1 for effects.
Title and ending are quiet.

Published v1.0.0 and its guide remain frozen. Its checksum and verification live
in `../release/manifest.json` and `../release/verification.json`. The five-stage
October 4 snapshot is recorded separately under `../release/five-stage/`;
later changes and their validation are documented in the current guide.

`tools/write_release_guide.py` combines a release manifest with current stage JSON.
Do not regenerate the v1.0.0 guide against newer geometry. Local `build/`,
`artifacts/`, save states and `../dist/` are excluded from Git. Retain font/UI
attributions in `LICENSE` when redistributing them.
