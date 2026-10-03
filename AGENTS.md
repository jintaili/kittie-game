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

User-facing plans and guides use HTML. The current guide is `design/version-1.html`.

# Whole-level development

The user approved the agent workflow in `design/agent-workflow.html`. Work on a
complete level per human review, with broad role prompts and independent judgment.
Difficulty may lean slightly high; do not assume the current game is too hard.
Use the agreed designer, builder and independent review roles. Keep build and
emulator ownership serialized. Routine findings should be resolved within the
team before presenting the complete level to the user.
