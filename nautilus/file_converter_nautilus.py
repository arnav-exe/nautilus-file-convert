from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import unquote, urlparse

from gi.repository import GObject, Nautilus


APP_NAME = "NautilusFileConvert"
CACHE_PATH = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "nautilus-file-convert" / "menu-cache.json"
CLI = os.environ.get("NAUTILUS_FILE_CONVERT_CLI", "nautilus-file-convert")


class FileConvertMenuProvider(GObject.GObject, Nautilus.MenuProvider):
    def get_file_items(self, files):
        paths = [_local_path(file_info) for file_info in files]
        paths = [path for path in paths if path and path.is_file()]
        if not paths:
            return []

        presets = _compatible_presets(paths)
        if not presets:
            return []

        root = Nautilus.MenuItem(
            name=f"{APP_NAME}::Root",
            label="File Converter",
            tip="Convert selected files",
        )
        submenu = Nautilus.Menu()
        root.set_submenu(submenu)

        categories = {}
        for preset in presets:
            categories.setdefault(preset.get("category", "Other"), []).append(preset)

        for category, category_presets in sorted(categories.items()):
            category_item = Nautilus.MenuItem(
                name=f"{APP_NAME}::Category::{category}",
                label=category,
            )
            category_menu = Nautilus.Menu()
            category_item.set_submenu(category_menu)
            submenu.append_item(category_item)

            for preset in category_presets:
                item = Nautilus.MenuItem(
                    name=f"{APP_NAME}::Preset::{preset['id']}",
                    label=preset["name"],
                )
                item.connect("activate", _run_conversion, preset["id"], paths)
                category_menu.append_item(item)

        return [root]


def _local_path(file_info) -> Path | None:
    uri = file_info.get_uri()
    parsed = urlparse(uri)
    if parsed.scheme != "file":
        return None
    return Path(unquote(parsed.path))


def _compatible_presets(paths: list[Path]) -> list[dict]:
    try:
        with CACHE_PATH.open("r", encoding="utf-8") as file:
            cache = json.load(file)
    except OSError:
        return []

    extensions = {path.suffix.lower().lstrip(".") for path in paths}
    return [
        preset
        for preset in cache.get("presets", [])
        if extensions and extensions.issubset(set(preset.get("input_extensions", [])))
    ]


def _run_conversion(_menu_item, preset_id: str, paths: list[Path]) -> None:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as file:
        json.dump([str(path) for path in paths], file)
        files_json = file.name

    subprocess.Popen(
        [
            CLI,
            "convert",
            "--preset-id",
            preset_id,
            "--files-json",
            files_json,
            "--delete-files-json",
            "--notify",
        ],
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
