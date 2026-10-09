# Kittie Has Other Plans

A native Game Boy Color game for ModRetro Chromatic. Kittie crosses a Tuscan
wedding venue to reach the photoshoot, collecting and throwing wool along the way.

## Play

[Download published v1.0.0](https://github.com/jintaili/kittie-game/releases/download/v1.0.0/kittie-has-other-plans-v1.0.0.gbc)
or visit its [release page](https://github.com/jintaili/kittie-game/releases/tag/v1.0.0).
This three-stage release has 28 screens and passed an owner Chromatic playtest.
The [play guide](design/version-1.html) covers controls and maps;
[release metadata](release/manifest.json) records its checksum and validation.
Open HTML guides locally after cloning or downloading the repository.

Collect, carry, throw and retrieve wool to ring bells and defeat goons.
Water and zero hearts reset the stage. Cleared stages stay unlocked.

## Current source

The source has five stages and 39 screens: Courtyard, Olive Grove, Villa Terraces,
Head Goon, then Banquet and the photoshoot. It adds moving service lifts,
per-stage scores and bests, scenery animation, refined character art and an icon
HUD. The Head Goon uses aimed hops and a tray-down counterattack window;
contact with him still hurts during recovery and flinching.

This version is separate from published v1.0.0. The
[current guide](design/head-goon-preview.html) describes the latest build and
validation limits. Earlier five-stage builds passed full-game, save-migration
and independent boss reviews. The latest contact change passed native/web builds
and focused combat-code checks; it has not had a full emulator or hardware run.

## Build

Open [courtyard/project.gbsproj](courtyard/project.gbsproj) in GB Studio 4.3.2
and export a Game Boy Color ROM, or select that project in the ModRetro build
tools. Authored assets and custom engine code are included; art regeneration is
not required. See [development notes](courtyard/README.md) for implementation
and [AGENTS.md](AGENTS.md) for project constraints.

Builds, save states, recordings and separate music experiments stay local.
Historical design reports may link to local artifacts that are not in Git.

## License

The project uses the [MIT license](LICENSE). Retain the
[GB Studio copyright notice](courtyard/LICENSE) when redistributing its included
font and UI assets.
