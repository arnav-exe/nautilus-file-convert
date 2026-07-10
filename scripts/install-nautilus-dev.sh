#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python_bin="$repo_root/venv/bin/python"
extension_src="$repo_root/nautilus/file_converter_nautilus.py"
bin_dir="$HOME/.local/bin"
extension_dir="$HOME/.local/share/nautilus-python/extensions"
wrapper_path="$bin_dir/nautilus-file-convert"
extension_link="$extension_dir/file_converter_nautilus.py"

if [[ ! -x "$python_bin" ]]; then
    echo "Missing venv Python: $python_bin" >&2
    exit 1
fi

if ! python3 - <<'PY' >/dev/null 2>&1
import gi
gi.require_version("Nautilus", "4.0")
from gi.repository import Nautilus
PY
then
    echo "Missing Nautilus Python bindings." >&2
    echo "Install them first: sudo apt install python3-nautilus" >&2
    exit 1
fi

mkdir -p "$bin_dir" "$extension_dir"

cat > "$wrapper_path" <<EOF
#!/usr/bin/env bash
exec "$python_bin" -m nautilus_file_convert "\$@"
EOF
chmod +x "$wrapper_path"

ln -sf "$extension_src" "$extension_link"
"$python_bin" -m pip install -e "$repo_root" >/dev/null
"$python_bin" -m nautilus_file_convert presets rebuild-cache >/dev/null

echo "Installed development Nautilus integration:"
echo "  CLI wrapper: $wrapper_path"
echo "  Nautilus extension: $extension_link"
echo
echo "Restart Nautilus to load it: nautilus -q"
echo "If the menu does not appear, install python3-nautilus and restart Nautilus again."
