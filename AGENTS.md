# Project workflow

User-facing plans and guides use HTML. The current guide is
`design/head-goon-preview.html`; `design/version-1.html` documents published
v1.0.0. Historical plans record decisions, not instructions to repeat completed work.
Preserve published cartridges, prior builds and user saves.

For whole-level development, follow `design/agent-workflow.html`: designer,
builder and independent review roles, broad prompts, one complete level per
human review. Serialize builds and emulator ownership. Resolve routine findings
within the team. Small approved fixes need focused checks; the owner requested
fewer verification-agent rounds for those. Difficulty may lean slightly high.

# Character and cover

The title is **Kittie Has Other Plans**, with no subtitle. On the cover, use
"KITTIE" large and "HAS OTHER PLANS" below as part of the same title.

Every Kittie sprite or portrait change must reference the original photographs
in `/Users/jintaili/Downloads/Kittie Codex Skill/assets/`. This is reference
material, not a skill to install. Untouched project copies and hashes are in
`courtyard/source-art/character-reference/`. Generated art is never the sole
reference; independent character reviews must consult the originals too.

Kittie is male. Preserve his low horizontal oval face, dark crown marking,
closed embroidered eyes, pale nose, wide stitched grin, low body and short legs.
Face embroidery stays fixed; reactions use his body and paws. Preserve the
approved back carry, idle cuddle and C1 legs: relaxed outward angles, one pixel
fuller, original ears, connected chest and restrained walking motion.
Avoid rectangular feet, skeletal limbs or a large gap between the forelegs.
Paws share the torso's taupe fill with small highlights and consistent one-pixel
contours. The beige shape below his face is a paw; wool is pink.

The cover uses native 160x144 portrait v10. Keep
`courtyard/source-art/approved-cover/cover-v10.png` untouched;
`courtyard/tools/make_cover.py` generates the native image and palette map.
Do not restore deleted intermediate covers or overwrite it through legacy art tools.

For cover changes, retain both paws on the flat ledge and hide the torso sides
around the cheeks. Keep a shallow elliptical head outline, with no upward tip,
and substantial rounded chin below the smile. The cap's downward forehead mark
is separate from the head outline. Highlights and shadows should describe curved
volume, without photographic speckling or sky teal on the fur. Keep chin, cast
shadow and ledge distinct. Design within native tile and palette limits.

Whiskers are uneven threads. His right cheek, viewer left, curls inward toward
the nose; the other side sweeps outward. `reference-current-front.png` and
`reference-head-on-own-paws-front.png` establish this. Preserve the generator's
native-cell correction without changing the full-size v10 source.

# Game rules and progression

Stage order is Courtyard (8 screens), Olive Grove (11), Villa Terraces (8),
Head Goon (3), Banquet (9), then the photoshoot. Keep the banquet ending.
Traversal stages have three physical wool balls; Head Goon has one. Wool only
rings bells and hits enemies. Preserve physical retrieval, with no automatic
returns or jump boosts. Water and zero hearts reset the stage.

Keep the numeric score visible at the top. Award points for unique goon defeats
or boss hits during play, then add retained-wool points at completion.
Preserve per-stage bests and saved unlocks. A/Start opens the title selector;
B restores the full cover. Show four rows and scroll additional stages.

Scenery motion should suit each level and leave landing edges clear. Preserve
Villa's predictable service lifts, also used in Banquet. The four visible slats
span the same 40-pixel collision surface. `courtyard/tools/make_banquet.py` owns
banquet art. Do not restore removed world tutorial captions.

Current saves use schema 19539; four-stage imports use 19538. Preserve stable
family words 0x4b48/0x4f50 in globals 12/13 and bounded block, unlock and score
checks. Older saves must retain banquet access. Keep legacy release/pilot
signature migration separate; compiler-generated save IDs change across exports
and are not a whitelist for new native/web pairs. See `courtyard/README.md` for
variable mappings and generator ownership.

# Head Goon

He is a larger, cute member of the ordinary goon family: round cloth body,
triangular ear tufts, pale eyes, small mouth and stubby feet. A tray and small
accessories show rank. Avoid a human coat, cap or long-legged silhouette.

Use the flat arena with no playable lift or plinth. Each windup locks a landing
target; hops never retarget in flight. One hop precedes recovery at full health;
after the first hit, two separately signaled hops precede it. Keep three hits,
constant walking speed and one recoverable ball. Guarded shots from either side
deflect; only tray-down recovery accepts damage. Review substantial fight
changes against camping and repetitive-input strategies.

Current timings are 28 updates of windup, 72 of tray-down recovery and 54 of
patrol between sequences. Contact hurts during recovery and flinching as well
as attacks; defeat is harmless. Flinch contact must run despite its early return.
Preserve Kittie's damage protection. The October 9 contact change leaves ball
physics, rebound, animations and these timings unchanged.

Polar bears are two quiet, cute plushie friends. Bear and photographer encounters
remain future ideas. Currency, shops and upgrades are not approved.

# HUD

Use three filled/outline heart slots, a numeric score and three filled/outline
wool slots. Glyphs are seven pixels tall, with one blank pixel above them.
`courtyard/tools/make_compact_hud.py` generates native window tiles for
`kittie_hud.c`. The one-row window uses no OAM objects; keep legacy HUD actors
hidden. Restore the normal UI window and palette before completion dialogs or
the title screen. Preserve score visibility during high jumps and validate
reserved VRAM tiles when asset allocation changes.
