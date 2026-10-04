# Kittie Has Other Plans

A native Game Boy Color game for ModRetro Chromatic. Kittie crosses the wedding
grounds to reach the photoshoot. The published release has three stages; the
working five-stage version adds Villa Terraces and the Head Goon encounter
between the grove and banquet.

## Play v1.0.0

[Download the ROM](https://github.com/jintaili/kittie-game/releases/download/v1.0.0/kittie-has-other-plans-v1.0.0.gbc)
or open the [release page](https://github.com/jintaili/kittie-game/releases/tag/v1.0.0)
for its checksum. The [HTML play guide](design/version-1.html) contains controls,
current maps and screenshots. Open the guide locally after cloning or downloading
the source.

Each v1.0.0 stage has three physical wool balls. Collect, carry, throw and retrieve
them to defeat goons and ring bells. Water and zero hearts reset the stage.
Cleared stages stay unlocked.

The published v1.0.0 cartridge passed a full-game emulator run and soft-restart
save recovery. The owner reported a successful Chromatic playtest on October 2,
2026. See the [release manifest](release/manifest.json) and
[retained verification](release/verification.json).

## Develop

The working source has five stages and 39 screens: Courtyard, Olive Grove,
Villa Terraces, Head Goon, then Banquet and the photoshoot. Villa introduces
moving service lifts; the Head Goon is a short encounter using one recoverable
wool ball. Its aimed hops require a dodge before each counterattack opening.
The iteration also adds per-stage scoring and bests, C1 character
legs, scenery motion, a four-row scrolling selector, and corrected cover whiskers.

The header uses heart and wool icons at the same height as the numeric score,
with a one-pixel top margin. The latest Head Goon tuning gives 72 frames to
counterattack and 54 frames between attack sequences.
The [Head Goon guide](design/head-goon-preview.html) links the current local
cartridge and review evidence. Independent boss gameplay review and a complete
native run have passed, along with cold boots, save migration and focused boss
checks on the earlier boss build. The latest timing adjustment received a
build and HUD smoke check; see the [current manifest](release/five-stage/manifest.json). The
[four-stage guide](design/four-stage-preview.html) preserves the previous build.
This work is separate from the published release. New Chromatic testing remains
with the owner.

Open [courtyard/project.gbsproj](courtyard/project.gbsproj) in GB Studio 4.3.2.
The authored project includes current game assets and custom engine code.
See [development notes](courtyard/README.md) and the
[whole-level workflow](design/agent-workflow.html).

Build folders, emulator save states and large recordings remain local.
Historical design reviews may link to those local artifacts. The current release
guide and its images are included in the repository.

## License

The project retains its existing [MIT license](LICENSE). Retain the
[GB Studio copyright notice](courtyard/LICENSE) when redistributing the included
font and UI assets.
