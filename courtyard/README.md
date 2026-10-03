# Kittie Has Other Plans

A native Game Boy Color game for ModRetro Chromatic with 28 screens:
8 courtyard, 11 olive grove, 9 wedding banquet. See [the play guide](../design/version-1.html)
for controls, maps, screenshots and verified release hashes.

Open `project.gbsproj` in GB Studio 4.3.2. Custom scene types `kittie`, `grove`,
`banquet` and `kittie_title` live in `plugins/kittie/engine`; no engine was ejected.
Gameplay shares signed 12.4 physics, a three-ball inventory and three hearts.
Each stage has three physical wool balls. Start retries the current stage; Select returns to
the cover. Water and zero hearts reset the current stage. There are no checkpoints,
automatic ball returns or jump boosts. Balls only ring bells and defeat goons.
Living goons patrol at 12 fixed-point units per update, or 0.75 px, and reflect
at their endpoints without pauses or charges.

## Geometry and art

`tools/level.json`, `grove.json` and `banquet.json` own geometry and pickup placement.
`tools/make_level_data.py` generates `kittie_levels.h`; the old `kittie_level.h`
is unused. Rectangles must be sorted by both left and right edges for collision
scanning. Keep each stage at most 2,000 pixels wide for signed 12.4 coordinates.
`grove.c` and `banquet.c` start stages 1 and 2 through shared Kittie code.

`tools/make_level.py` generates the courtyard. `tools/make_world_art.py` contains grove generation and legacy paths for
other backgrounds. Its legacy banquet path does not reproduce the approved
banquet art: do not run its whole entry point over current assets. `tools/make_grove.py` is a compatibility
entry point. Repaint native attributes using `palette_paint` after geometry changes.
Grove and banquet paint regions are in `tools/grove-palettes.json` and
`tools/banquet-palettes.json`.

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
reserved for UI. A or Start opens the stage selector overlay, B closes it.

`tools/make_carry_assets.py` generates wool, HUD and the court shutter. Do not run
older `tools/make_art.py` over current assets. Source colors are import indices,
not the final game palette.

`tools/make_feedback_art.py` owns four bell and gate frames. Successful hits swing
the bell for 48 updates, raise the gate, then leave a green bell and open marker.
The camera holds the court during the reaction. Skip pose work for offscreen
bells and gates: updating those distant actors caused missed native frames in
the grove. Low tables have a shaded 14px wool passage. The courtyard table
caption and all grove and banquet world captions have been removed.

## Runtime and progression

Actor indices in each gameplay scene: player 0; balls 1,8,9,10,11,12; gates 2,3;
goons 4,5,6; shutter 7; hearts 13; inventory 14; bells 15,16. Sprite palette slots
are Kittie/gates 0, wool 1, goons 2, resting bells 3, HUD 4, and rung bells/open
gates 5. Per-goon ground heights come from the stage JSON. A door index of 255 means
that stage has no entry shutter. The shared engine guards collision, rendering
and closure logic for this case; the grove and banquet use it to allow backtracking.

Native scene scripts connect courtyard, grove, banquet and the wedding ending.
Variable 100 is the highest unlock: 0 fresh, 1 grove, 2 banquet, 3 completed.
Variable 101 is the menu choice. Clearing a stage raises variable 100 and uses
`EVENT_SAVE_DATA` slot 0. The title uses `EVENT_PEEK_DATA` to recover the unlock.
This saves stage access, not mid-stage position. Earlier clears never reduce it.

`kittie_music.c` has three original 32-note themes and a bass accompaniment.
Pulse channel 2 carries melody; wave carries bass; sound effects use pulse 1.
Title and ending are quiet. The user reported a successful Chromatic test on October 2, 2026.

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
a historical build folder.

Old builds, recordings, backups and user save states remain preserved locally.
The release package is staged under the ignored ../dist/v1.0.0/ directory;
GitHub release assets hold the published ROM and checksum.
Preserve this project's font/UI license. The external character reference
folder is reference material only and was never installed as a skill.
