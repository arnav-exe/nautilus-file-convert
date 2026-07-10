# nautilus-file-convert

Ubuntu 26.04 LTS-targeted file conversion for GNOME Files/Nautilus. The project is intentionally split into a standalone conversion CLI and a thin Nautilus extension so the engine can be rewritten later without changing the file-manager integration contract.

## Current Scope

- Nautilus/GNOME context-menu integration only.
- Linux-native TOML presets.
- Media conversions through `ffmpeg`.
- Image and PDF-oriented conversions through ImageMagick/Ghostscript.
- No settings GUI yet.
- Office document conversion is intentionally deferred.

## Development

Use the repo-local virtual environment:

```bash
./venv/bin/python -m pip install -e .
./venv/bin/python -m unittest discover -s tests
```

Rebuild the Nautilus menu cache after changing presets:

```bash
./venv/bin/python -m nautilus_file_convert presets rebuild-cache
```

Dry-run a conversion command without touching files:

```bash
./venv/bin/python -m nautilus_file_convert convert --preset-id to-mp4 --dry-run sample.mov
```

## Nautilus Extension Development

Install Nautilus Python support once:

```bash
sudo apt install python3-nautilus
```

Run that apt command by itself; it installs Nautilus' Python extension loader.

Install the development context-menu integration:

```bash
./scripts/install-nautilus-dev.sh
nautilus -q
```

The installer creates `~/.local/bin/nautilus-file-convert`, symlinks `nautilus/file_converter_nautilus.py` into `~/.local/share/nautilus-python/extensions/`, installs the package editable in the repo venv, and rebuilds the menu cache.

To remove the development integration:

```bash
./scripts/uninstall-nautilus-dev.sh
nautilus -q
```

The extension must stay lightweight: it reads only `~/.cache/nautilus-file-convert/menu-cache.json`, filters presets by extension, and spawns the CLI detached from Nautilus.
