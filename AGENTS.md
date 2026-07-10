# Repository Instructions

## Project Shape
- Ubuntu 26.04 LTS/GNOME Files target; Nautilus support is the only file-manager integration for now.
- Keep `nautilus/file_converter_nautilus.py` thin: it should read the JSON menu cache, filter selected files, and spawn the CLI only.
- Core conversion logic lives under `src/nautilus_file_convert/`; preserve the CLI boundary so the engine can be rewritten in Rust later.
- Presets are Linux-native TOML in `src/nautilus_file_convert/presets/defaults.toml`; user overrides load from `~/.config/nautilus-file-convert/presets.toml`.

## Commands
- Install in the repo venv: `./venv/bin/python -m pip install -e .`.
- Run tests: `./venv/bin/python -m unittest discover -s tests`.
- List presets: `./venv/bin/python -m nautilus_file_convert presets list --json`.
- Rebuild Nautilus menu cache: `./venv/bin/python -m nautilus_file_convert presets rebuild-cache`.
- Dry-run conversion planning: `./venv/bin/python -m nautilus_file_convert convert --preset-id to-mp4 --dry-run sample.mov`.

## Design Constraints
- The Nautilus extension must never run conversions, probe dependencies, or parse large config; right-click menus must stay fast.
- Conversion subprocesses run outside Nautilus and should stay quiet except optional desktop notifications.
- Current scope is media/images/PDF via `ffmpeg`, ImageMagick, and Ghostscript; defer office-document conversion.
- Use XDG paths from `paths.py` for user config, cache, and logs.
