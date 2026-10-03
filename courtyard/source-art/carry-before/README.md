# Kittie, come back!

An eight-screen, single-level Game Boy Color prototype for ModRetro Chromatic.
See [prototype notes and controls](README.html).

Open `project.gbsproj` in GB Studio 4.3.2. The custom `kittie` scene type is in
`plugins/kittie/engine`; it supplies the ball and platform movement. No engine
was ejected. The level uses native backgrounds, actors, a finish trigger, and
a detailed 40x32 Kittie with ten authored animation frames. Level geometry is
in `tools/level.json`; `tools/make_level.py` generates the background and
`plugins/kittie/engine/include/states/kittie_level.h`. `tools/make_kittie.py`
generates the character frames and their native metadata. `tools/make_goons.py` generates the four enemy poses and ribbon. Background palette indices are authored with `palette_paint` and retained in the background sidecar; repaint them when changing geometry. Sprite palette indices are 0 Kittie/gates, 1 wool, 2 goons, 3 ribbon. Do not rerun the older
`tools/make_art.py` over the current assets.

Build with the managed ModRetro `rom_build` and `web_preview` tools. The compiled
cartridge is `build/kittie-courtyard.gbc`. The official web export is `build/web`.
GB Studio's CLI equivalents are `make:rom project.gbsproj build/kittie-courtyard.gbc`
and `make:web project.gbsproj build/web`.

Retained emulator input history and frames live in `artifacts/playtests`.
The default font and UI came from the ModRetro blank project. Preserve LICENSE.
The external Kittie reference folder was read only and its skill was not installed.

Final action build: `8094fa68972644ddd0a4d81157c149911e86b4161440eeb3e94f8c757856568d`.
Final lower route: `artifacts/playtests/session-65782275-51c3-42c5-a3c7-864cd5d6e1d9`.
Final upper route: `artifacts/playtests/session-66897853-ebac-4b87-88c0-71b61a4ab693`.
