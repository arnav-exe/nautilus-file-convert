#!/usr/bin/env bash
set -euo pipefail

rm -f "$HOME/.local/bin/nautilus-file-convert"
rm -f "$HOME/.local/share/nautilus-python/extensions/file_converter_nautilus.py"

echo "Removed development Nautilus integration."
echo "Restart Nautilus to unload it: nautilus -q"
