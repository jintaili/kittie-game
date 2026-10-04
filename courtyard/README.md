# Kittie Has Other Plans

A native Game Boy Color game for ModRetro Chromatic. The published v1.0.0 has
28 screens; its [play guide](../design/version-1.html) remains tied to that release.

The working source has 39 screens: 8 courtyard, 11 olive grove,
8 Villa Terraces, 3 Head Goon, and 9 wedding banquet. See the
[Head Goon guide](../design/head-goon-preview.html) and
[encounter brief](../design/head-goon-brief.html). Independent boss review and
the connected native run passed, along with cold boots, save migration and
focused boss checks. See the [final verification](../design/head-goon-hop-verification.html).
Each stage has a separate score and best. The shared character uses approved C1
legs; Villa introduces moving service lifts, which return in the banquet.
The earlier [four-stage guide](../design/four-stage-preview.html) retains that build.

Open `project.gbsproj` in GB Studio 4.3.2. Custom scene types `kittie`, `grove`,
`villa`, `head_goon`, `banquet` and `kittie_title` live in `plugins/kittie/engine`; no engine was ejected.
Gameplay shares signed 12.4 physics, a three-ball inventory and three hearts.
The four traversal stages have three physical wool balls; Head Goon has one. Start retries the current stage; Select returns to
the cover. Water and zero hearts reset the current stage. There are no checkpoints,
automatic ball returns or jump boosts. Balls only ring bells and defeat goons.
Living goons patrol at 12 fixed-point units per update, or 0.75 px, and reflect
at their endpoints without pauses or charges. The Head Goon shares that walking
speed between aimed hops. His marked landing target locks before takeoff.
At full health one hop leads to a tray-down opening; after the first hit, two
separately signaled hops precede the opening. Guarded throws from either side
rebound without damage. His arena has a flat floor without a playable lift.

## Geometry and art

`tools/level.json`, `grove.json`, `villa.json`, `head_goon.json` and `banquet.json` own geometry and pickup placement.
`tools/make_level_data.py` generates `kittie_levels.h`; the old `kittie_level.h`
is unused. Rectangles must be sorted by both left and right edges for collision
scanning. Keep each stage at most 2,000 pixels wide for signed 12.4 coordinates.
`grove.c`, `villa.c`, `head_goon.c` and `banquet.c` start stages 1, 2, 3 and 4 through shared Kittie code.
Moving decks stay separate from the sorted static-solid cache.

`tools/make_level.py` generates the courtyard. `tools/make_world_art.py` contains grove generation and legacy paths for
other backgrounds. Its banquet entry now dispatches to `tools/make_banquet.py`, which owns the approved
art and moving-lift rails. Its main entry preserves the approved v10 title. `tools/make_grove.py` is a compatibility
entry point. Repaint native attributes using `palette_paint` after geometry changes.
Grove and banquet paint regions are in `tools/grove-palettes.json` and
`tools/banquet-palettes.json`.

`tools/make_water_motion.py` generates four phases for the courtyard's two
water tiles in `kittie_water.h`. Regenerate it after changing courtyard water
pixels. Runtime code reads the compiled tile IDs, banks and flips. Before
shipping scenery edits, check that those tile identities occur only in water
cells, including any compiler flip deduplication. Keep the banks and surface
edge fixed and inspect a complete native loop.

`tools/make_world_motion.py` adds four-phase leaf tips to the grove and bunting
to the banquet, then writes `kittie_world_motion.h`. Apply it after regenerating
those backgrounds. Like the water animation, it respects compiled tile banks
and flips; animated tile identities must not be shared with unrelated scenery.

Every sprite change must reference the owner's original Kittie assets. Read the
root `AGENTS.md` and `source-art/character-reference/reference.json`. The original
front and side photos define his identity; he is male. `tools/make_kittie.py`
generates a 40x32 character with 16 frames. All frames share identical face pixels.
Body and paw contours use one-pixel strokes; front paws share the torso taupe.
Frames 14 and 15 use a pleased body bob and tucked-paw recoil. They do not change
the embroidered eyes or grin. Back carry and idle cuddle remain; the beige front
shape is a paw. The title uses device-oriented cover v10; the ending uses the exact gameplay sprite.
`tools/make_cover.py` preserves the full-size source and converts it into native
160x144 pixels, 302 source tiles, and seven palettes. Palette assignments are in
`tools/cover-palettes.json` and the background sidecar. The eighth palette stays
reserved for UI. The generator also corrects the native whisker cells: Kittie’s
right cheek (viewer left) curls inward. The full-size v10 source stays untouched.
A or Start opens the four-row scrolling stage selector overlay; B closes it.

`tools/make_carry_assets.py` generates wool, HUD and the court shutter. Do not run
older `tools/make_art.py` over current assets. Source colors are import indices,
not the final game palette. Wool uses blank padding above its visible pixels and
a compensating tile offset, avoiding deck overlap without moving the drawing.

`tools/make_feedback_art.py` owns four bell and gate frames. Successful hits swing
the bell for 48 updates, raise the gate, then leave a green bell and open marker.
The camera holds the court during the reaction. Skip pose work for offscreen
bells and gates: updating those distant actors caused missed native frames in
the grove. Low tables have a shaded 14px wool passage. The courtyard table
caption and all grove and banquet world captions have been removed.

## Runtime and progression

Actor indices in each gameplay scene: player 0; balls 1,8,9,10,11,12; gates 2,3;
goons 4,5,6; shutter 7; hearts 13; inventory 14; bells 15,16; score 17–19.
Head Goon uses actor 4 for the boss and actor 5 for the landing cue; unused
ordinary goons remain hidden. The boss stays visible throughout his fixed-camera
arena, including positions beyond the ordinary 110-pixel culling distance.
Villa and banquet use actor 20 for the currently visible lift. Shafts are farther
apart than the viewport; all physical decks continue moving offscreen. Sprite palette slots
are Kittie/gates 0, wool 1, goons 2, resting bells 3, HUD 4, and rung bells/open
gates 5. Per-goon ground heights come from the stage JSON. A door index of 255 means
that stage has no entry shutter. The shared engine guards collision, rendering
and closure logic for this case; the grove and banquet use it to allow backtracking.

Native scene scripts connect courtyard, grove, Villa, Head Goon, banquet and the wedding ending.
Variable 100 is the highest unlock: 0 fresh, 1 grove, 2 Villa, 3 Head Goon,
4 banquet, 5 completed. The bounded progress loader maps four-stage unlocks
3 and 4 to 4 and 5, and legacy three-stage unlocks 2 and 3 to 4 and 5.
Inserting stages preserves earlier banquet access.
Variable 101 is the menu choice. Clearing a stage raises variable 100 and uses
`EVENT_SAVE_DATA` slot 0. This saves stage access, not mid-stage position.
Earlier clears never reduce it.

Variables 102–107 store goon points, wool points, attempt score,
courtyard best, save-format version and a save-needed flag. Variables
108–111 store grove best, Villa best, banquet best and the stage-save schema.
Variables 112–113 hold the stable game-family marker, written by stage clears.
114 stores the Head Goon best; 115 stores selector state. Traversal stages award
100 per unique defeated goon and 200 per held ball at completion. A retry clears
the attempt; only a completed higher score replaces the best. The Head Goon
awards 100 per successful hit and 200 for his one retained wool, at most 500.
Each throw can damage him only once; a guarded hit from either side consumes the throw
without points, leaving the wool physically recoverable. The completion
trigger saves when the best or stage unlock changes.

The header uses three heart slots, a centered numeric score, and three wool
slots. Filled pink icons show the current count; outlines show empty capacity.
The icons and score digits are seven pixels tall. The clipped one-row window
uses no OAM objects, leaving the hardware sprite budget for Kittie and the world.
Legacy HUD actors 13, 14 and 17–19 remain hidden to preserve actor indices.

`tools/make_compact_hud.py` generates `kittie_hud_tiles.h` and the source-art
preview. `kittie_hud.c` owns the clipped window, cached glyph updates and palette
restoration. It releases the header before completion dialogs and title
transitions. The window glyphs use bank-one C0–D8; validate that these remain
outside scene background and actor tile allocations when changing assets.
The older carry/score generators produce historical sprite HUD assets; do not
restore those actors to replace the current window header.

The title uses a bounded progress loader in `kittie_title.c`. Current five-stage
saves use schema 19539; four-stage imports use 19538. Both require the two-word
game-family marker, the expected variables block and valid unlock/score ranges.
Boss best is capped at 500; other stage bests at 900. Four-stage imports start
with boss best zero. This avoids dependence on compiler save IDs
that change between exports. Legacy imports require the exact reviewed pilot native
and web signatures for score/unlock migration, or the published v1.0.0 signature
for unlock-only migration. Legacy pilot signatures are explicitly bounded to the preserved review-2 and
review-3 native and web cartridges. The four-stage schema is distinct from the
three-stage pilot schema, and new bests keep fixed slots. Browser sessions remain separate; this
loader does not transfer browser storage across preview URLs. It reads the saved VM globals without
loading cross-build scene state. Compile-time guards preserve the global
indices, and block validation uses the full `sizeof(script_memory)`, including
VM context stacks. Published v1.0.0 used `EVENT_PEEK_DATA`; its ROM is unchanged.

`kittie_music.c` has four original 32-note themes and a bass accompaniment.
Pulse channel 2 carries melody; wave carries bass; sound effects use pulse 1.
Title and ending are quiet. The user reported a successful Chromatic test of
the published version on October 2, 2026.

## Release and verification

Release v1.0.0 promotes the exact reviewed main cartridge
[build/kittie-grove-review-2.gbc](build/kittie-grove-review-2.gbc) without
recompiling or modifying it. Its published filename is
kittie-has-other-plans-v1.0.0.gbc.
The tracked [release manifest](../release/manifest.json) records the SHA-256,
download URL and scope of hardware feedback. The user reported a successful
Chromatic test; specific hardware subtests and cartridge hash were not enumerated.

The exact release cartridge completed all three stages, returned to the cover
and recovered unlock value 3 after a native soft restart. Full input history and
frame hashes are in [verification.json](../release/verification.json), including
an initial grove route failure and successful explicit retry. Per-level reviews
are linked from the [grove](../design/grove-review.html),
[banquet](../design/banquet-review.html) and
[courtyard](../design/courtyard-review.html) review pages. Those historical
reports retain links to local evidence.

Open the native project in GB Studio 4.3.2 and export a Game Boy Color ROM, or use
the managed ModRetro ROM build tools with this canonical project selected.
Authored PNGs and palette sidecars are the build inputs; regeneration is not
needed to compile the release. Python art tools require Pillow.
Do not edit generated practice copies under build/.

To refresh the release guide and geometry maps after updating the release
manifest or stage data, run python3 tools/write_release_guide.py from this
directory. It uses the tracked release manifest and current stage JSON, not
a historical build folder. Do not run it with the v1.0.0 manifest against pilot
geometry. Keep that published guide tied to its release; use the separate
pilot guide until preparing a new release.

Old builds, recordings, backups and user save states remain preserved locally.
The release package is staged under the ignored ../dist/v1.0.0/ directory;
GitHub release assets hold the published ROM and checksum.
Preserve this project's font/UI license. The external character reference
folder is reference material only and was never installed as a skill.
