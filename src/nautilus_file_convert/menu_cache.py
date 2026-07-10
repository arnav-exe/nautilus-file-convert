from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nautilus_file_convert import paths
from nautilus_file_convert.presets import Preset, load_presets


def build_menu_cache(presets: list[Preset] | None = None) -> dict[str, Any]:
    return {
        "version": 1,
        "presets": [preset.to_menu_dict() for preset in presets or load_presets()],
    }


def write_menu_cache(path: Path | None = None) -> Path:
    target = path or paths.menu_cache_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as file:
        json.dump(build_menu_cache(), file, indent=2, sort_keys=True)
        file.write("\n")
    return target
