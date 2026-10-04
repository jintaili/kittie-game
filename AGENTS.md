# Kittie character reference

The confirmed game title is **Kittie Has Other Plans**, with no subtitle. Use
"KITTIE" large and "HAS OTHER PLANS" below as the rest of the same title.

The user requires every Kittie sprite or portrait change to reference the original
assets in `/Users/jintaili/Downloads/Kittie Codex Skill/assets/`. This is a character
reference folder, not a skill to install. The original front and side photographs
are authoritative for his face and body. Untouched project copies and source
hashes are in `courtyard/source-art/character-reference/`.

Kittie is male. Preserve his low horizontal oval face, dark crown marking,
closed embroidered eyes, pale nose, wide stitched grin, low body and short legs.
Reactions use his body and paws while the face embroidery stays fixed. The beige
shape beneath his face is a paw; visible wool is pink. Preserve the approved
back carry and idle cuddle. Do not use an earlier generated sprite as the sole
reference for a later revision.

Paws use the torso's taupe fill with small highlights, and body/paw contours use
consistent one-pixel strokes. Avoid a large pale front paw that resembles a ball.

The opening screen uses the final native 160x144 portrait cover, version 10.
Its full-size source is `courtyard/source-art/approved-cover/cover-v10.png`;
`courtyard/tools/make_cover.py` produces the native background and palette map.
Intermediate cover versions were removed at the user request.
Keep the full cover visible until A or Start opens the stage selector overlay.
B closes that overlay. Preserve saved stage unlocks.

For cover revisions, keep both front paws resting on the flat ledge. Hide only
the torso sides that spill around the cheeks. The top of the head should be a
shallow, smooth oval arc without an upward tip. The dark cap's downward forehead
marking is separate from that silhouette. Preserve a substantial rounded area
of fur below the smile; do not flatten the underside into the paws or ledge.
Whiskers are naturally uneven threads, never mirrored cartoon pairs.

Design the cover for final native palette and tile constraints from the start.
Use coherent curved highlights and shadows to describe volume, not photographic
speckling. Sky teal must not leak onto the fur. Keep the chin, cast shadow and
stone ledge distinct in value. Avoid noisy texture, large undifferentiated blue shadows, a peaked head, or
removal of the paws and ledge. Preserve approved composition and original assets.

User-facing plans and guides use HTML. The published release guide is
`design/version-1.html`; the current four-stage build guide is
`design/four-stage-preview.html`.

# Whole-level development

The user approved the agent workflow in `design/agent-workflow.html`. Work on a
complete level per human review, with broad role prompts and independent judgment.
Difficulty may lean slightly high; do not assume the current game is too hard.
Use the agreed designer, builder and independent review roles. Keep build and
emulator ownership serialized. Routine findings should be resolved within the
team before presenting the complete level to the user.

# Next version direction

The user approved implementing a courtyard pilot on October 3, 2026. The
decision log is `design/next-version.html`. Add scoring for enemy defeats and
wool retained at completion, a distinctive courtyard moment, and livelier
presentation. A rival or boss is on hold. No shop or upgrade economy is approved.
Wool keeps its two gameplay uses, bells and enemies. Work on one whole level
per review and use independent critic and verification roles.

Environmental life is part of the approved direction. Swaying leaves, rippling
irrigation water, fluttering bunting and expressive enemy reactions are examples;
a coherent selection per level is enough. Keep terrain and landing edges clear.

Revise Kittie's rounded-rectangle feet into clearer short legs, using the
original photo references. A slight body lowering is acceptable if needed for
the silhouette. Preserve his approved face, back carry and idle cuddle.
Preserve the published v1.0.0 release while developing the pilot.

The October 3 pilot feedback requires a continuously visible top score during
courtyard play. Show earned goon points live and add the retained-wool bonus at
completion, preserving the scoring rules. Kittie's legs should be short and
straighter, with restrained walking motion. Fill the large gap between the
forelegs with connected taupe chest/body volume or slightly thicker limbs.
Do not substitute thin skeletal sticks or enlarge the pale paw highlight.
An independent character critic must consult the original Kittie reference
folder and the user's current requirements when reviewing the refinement.

# Four-stage expansion

The user authorized C1 sprite integration, whole-grove and whole-banquet upgrades,
and a new harder Villa Terraces stage on October 3, 2026. He explicitly approved
predictable moving service lifts as the new mechanic. Order: Courtyard (8 screens),
Olive Grove (11), Villa Terraces (8), Banquet (9), then the photoshoot. Keep the
banquet ending. Preserve old saves' banquet access when inserting the new stage.
The selected C1 study uses relaxed outward legs, one pixel fuller, with ORIGINAL
ears. Keep the face, chest connection, quiet walk, carry and cuddle.
Use design/next-iteration-plan.html and the active whole-level briefs.

Native Villa testing required a compact top HUD of four hardware objects and a
four-slat lift spanning the same 40-pixel collision surface. Preserve the visible
score during high jumps. `tools/make_compact_hud.py` owns the current HUD and must
follow older carry/score generators when those are rerun. Banquet art comes from
`tools/make_banquet.py`; do not restore the removed world tutorial captions or
replace the approved v10 cover through a legacy world-art entrypoint.

Four-stage progress uses schema 19538 and stable family words 0x4b48/0x4f50
in globals 12/13, with bounded block, unlock and score checks. Keep legacy
release/pilot signature migration separate. Compiler save IDs change across
exports and must not be used as a circular native/web whitelist.

# Head Goon iteration

The user approved building the Head Goon as a short separate stage after Villa
and before Banquet. He must be larger than ordinary goons, with richer readable
service-uniform/tray details and animated reactions. Keep the fixed patrol
speed and physical recoverable wool. Build and independently review the complete
encounter before human review; preserve the four-stage cartridge and old saves.
The title selector must occupy only three or four rows and scroll additional
stages. Four visible rows are the current implementation choice. Preserve the
full cover until A/Start opens it and B closes it.

The owner corrected the cover whiskers: his right cheek (viewer left) has
threads curling inward toward his nose; the other side sweeps outward. Original
reference-current-front.png and reference-head-on-own-paws-front.png establish
this direction. make_cover.py applies an exact native-cell correction while
keeping cover-v10.png untouched. Preserve this asymmetric correction on rebuild.

Polar bears are two quiet, cute plushie friends contrasted with mischievous
Kittie. They may support a later friendly challenge; no bear encounter is in
this build. Photographer remains a possible later prototype. Economy is on hold
while bosses are developed; do not add currency, shops or upgrades this round.

The first Head Goon drawing was rejected as too human-like. He must be a
larger, somewhat cute member of the regular goon family: round cloth body,
triangular ear tufts, pale eyes, small mouth and stubby feet. Preserve that
family resemblance; the tray and small accessories show rank. Avoid the human
coat/cap/long-legged silhouette.

The October 4 owner playtest rejected the stationary winning strategy. The
approved replacement is in `design/head-goon-hop-brief.html`: a flat arena with
no playable lift or plinth, aimed committed hops, then a distinct tray-down
counterattack opening. Full health uses one hop; after the first hit, two
separately telegraphed hops precede recovery. Lock each destination during its
wind-up, never retarget in flight. Keep three hits, one physical wool, constant
walking speed, the approved cloth-goon art family and existing saves. Guarded
rear shots and automatic endpoint openings must no longer give free hits.
Independent gameplay review must try camping and repetitive input strategies.


# Icon header

The October 4 header revision replaces numeric health and wool counts with
three filled/outline icon slots each, at the same seven-pixel height as the
numeric score. `tools/make_compact_hud.py` now generates native window tile data
for `kittie_hud.c`; the one-row header uses no OAM objects. This supersedes the
older four-object sprite HUD. Keep the header at the top, preserve score
visibility during high jumps, and restore the normal UI window and palette
before completion dialogs or the title screen. Validate the reserved VRAM tiles
when changing asset allocation. Legacy heart/count and inventory/count sprite
assets must not be made visible again.

The October 4 follow-up restores one blank pixel above the seven-pixel HUD glyphs.
Head Goon tray-down recovery is 72 updates and patrol between sequences is 54;
windup remains 28, with the existing one-then-two hop pattern and three hits.
