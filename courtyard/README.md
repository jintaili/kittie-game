# Kittie Has Other Plans

A native Game Boy Color game for ModRetro Chromatic with 28 screens:
8 courtyard, 11 olive grove, 9 wedding banquet. See [the play guide](../design/version-1.html)
for controls, maps, screenshots and verified release hashes.

Open `project.gbsproj` in GB Studio 4.3.2. Custom scene types `kittie`, `grove`,
`banquet` and `kittie_title` live in `plugins/kittie/engine`; no engine was ejected.
Gameplay shares signed 12.4 physics, a three-ball inventory and three hearts.
Each current stage candidate has three physical wool balls. Start retries the current stage; Select returns to
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

`tools/make_level.py` generates the courtyard. `tools/make_world_art.py` generates
grove, banquet, title and ending backgrounds. `tools/make_grove.py` is a compatibility
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
Title and ending are quiet. Physical speaker balance remains for the user's test.

## Build and evidence

The current grove revision follows `../design/grove-revision-brief.html`, with
whole-level status at `../design/grove-review.html`. Its shared movement and goon
physics remain unchanged. The geometry uses three high ledges and a 64px late
channel, with an open final bell garden for wool recovery. Final main/practice builds are `build/kittie-grove-review-2.gbc` and
`build/kittie-grove-practice-review-2.gbc`. Independent review passed after a
third-attempt clear with full health; see `artifacts/reviews/grove-gameplay/`.
The exact browser-export replay, banquet transition and soft-restart unlock
check are in `artifacts/grove-final-integration.json`. The browser export lives
at `build/grove-practice-project/build/web`.
The art generator must be invoked for the grove only: its legacy banquet path
does not reproduce the approved banquet background. Preserve those assets.


The current banquet candidate is `build/kittie-banquet-review-2.gbc`. Its
whole-level handoff is `../design/banquet-review.html`. The direct-entry practice
ROM is `build/kittie-banquet-practice-review-2.gbc`. Builder evidence and exact
hashes are in `artifacts/banquet-review-2-verification.json`; the compact main-ROM
route is `artifacts/banquet-review-2-full-game-inputs.json`. Independent review completed on attempt two with three hearts and one wool;
no blocking change was requested. Evidence is under
`artifacts/reviews/banquet-gameplay/`. Browser export and remaining-check status
are recorded in `artifacts/banquet-handoff-status.json`. The final art/text review is `../design/banquet-art-review.html`.

The generated native project in `build/banquet-practice-project/` copies the
canonical authored files and changes only the start scene to the banquet. Keep
editing this directory's canonical `project.gbsproj`, not that generated copy.
The main build retains normal stage unlocks. No physical Chromatic claim is made.


The whole-level courtyard candidate is `build/kittie-courtyard-review-2.gbc`.
Its review page is `../design/courtyard-review.html`; the general agent workflow
is `../design/agent-workflow.html`. `tools/level.json` now has three balls, an
optional early shelf and a later final shutter. `make_level_data.py` pads each
stage to six engine slots and records its active supply separately. Reset marks
inactive slots lost. The revised grove and banquet also use three active balls.
Candidate evidence is in `artifacts/courtyard-review-1-verification.json`.
The previous complete release below remains available for comparison.

Use managed ModRetro `rom_build` and `web_preview` tools. Earlier complete release:
`build/kittie-complete-v1.gbc`. Its official browser export is `build/feedback-web`.
The previous `build/release-web` export and disconnected browser tab remain for
state recovery. The new preview is open separately.
Preserve previous exports, user states and recordings.

Both exact final ROMs completed all three stages and recovered unlock value 3
after a native engine soft restart that clears VM variables. The deterministic
public-emulator route is `tools/complete-route.json`, starting at frame 180 and
ending at frame 4690 with the cover-opening prelude below. Current hashes and replay results are in
`artifacts/version-1-verification.json`; current stills are `artifacts/version-1-*.png`.
The feedback update passed the same route in both exact ROMs. Evidence is in
`artifacts/feedback-native-replay.json` and `artifacts/feedback-web-replay.json`.
Sampled bell/table scenes peaked at nine objects per scanline, below ten.
Contact reduced health from three to two; Start restored three and cleared wool.

The extensive gameplay recording is
`artifacts/playtests/session-5bdd378f-3e5f-4c5b-ac24-e31080ef57ff`. It covers both
grove routes, optional high wool, contact damage, constant patrols, full completion,
and entering both final courts with no carried wool. It predates the final face
and menu correction; its geometry and gameplay match the release.
`artifacts/complete-v1-playthrough.gif` uses that earlier artwork. Its ROM is
`build/kittie-complete-gameplay-tested.gbc`.

Backups remain in `source-art/reference-correction-before` and
`source-art/three-stage-before`. Older recordings retain their original bytes
under `artifacts/playtests` and `artifacts/recording-archives`.

The user handles physical Chromatic testing, including power-cycle save retention,
frame pacing and sound balance. Emulator completion is not a hardware claim.
Preserve the blank project's font/UI license. The external reference folder was
read only; its skill was not installed.

The shipped cover and selector were verified in both final ROMs. Evidence:
`artifacts/cover-v10-native-ui.json`, `artifacts/cover-v10-native-replay.json`, and
`artifacts/cover-v10-web-replay.json`. Each replay first presses A for 60 frames and
releases for one frame, then follows `tools/complete-route.json`. Both reach the
wedding ending and recover unlock value 3 after soft restart. The original
full-size cover is in `source-art/approved-cover/cover-v10.png`.
