# Kittie Has Other Plans

A native Game Boy Color game for ModRetro Chromatic. Kittie crosses an eight-screen
courtyard, an eleven-screen olive grove, and a nine-screen wedding banquet.

## Play v1.0.0

[Download the ROM](https://github.com/jintaili/kittie-game/releases/download/v1.0.0/kittie-has-other-plans-v1.0.0.gbc)
or open the [release page](https://github.com/jintaili/kittie-game/releases/tag/v1.0.0)
for its checksum. The [HTML play guide](design/version-1.html) contains controls,
current maps and screenshots. Open the guide locally after cloning or downloading
the source.

Each stage has three physical wool balls. Collect, carry, throw and retrieve
them to defeat goons and ring bells. Water and zero hearts reset the stage.
Cleared stages stay unlocked.

The latest complete cartridge passed a full-game emulator run and soft-restart
save recovery. The owner reported a successful Chromatic playtest on October 2,
2026. See the [release manifest](release/manifest.json) and
[retained verification](release/verification.json).

## Develop

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
