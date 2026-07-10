from __future__ import annotations

import json
import tomllib
from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path
from typing import Any

from nautilus_file_convert import paths


@dataclass(frozen=True)
class Preset:
    id: str
    name: str
    category: str
    backend: str
    output_extension: str
    input_extensions: frozenset[str]
    args: tuple[str, ...] = field(default_factory=tuple)

    def supports_extension(self, extension: str) -> bool:
        normalized = extension.lower().lstrip(".")
        return normalized in self.input_extensions

    def supports_all(self, file_paths: list[Path]) -> bool:
        return bool(file_paths) and all(self.supports_extension(path.suffix) for path in file_paths)

    def to_menu_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "input_extensions": sorted(self.input_extensions),
        }


def load_presets() -> list[Preset]:
    preset_data = _load_toml_resource("presets/defaults.toml")
    user_path = paths.user_presets_path()
    if user_path.exists():
        preset_data = _merge_preset_data(preset_data, _load_toml_file(user_path))
    return [_parse_preset(item) for item in preset_data.get("preset", [])]


def find_preset(preset_id: str) -> Preset:
    for preset in load_presets():
        if preset.id == preset_id:
            return preset
    raise ValueError(f"Unknown preset: {preset_id}")


def presets_json() -> str:
    return json.dumps([preset.to_menu_dict() for preset in load_presets()], indent=2)


def _load_toml_resource(name: str) -> dict[str, Any]:
    data = resources.files("nautilus_file_convert").joinpath(name).read_bytes()
    return tomllib.loads(data.decode("utf-8"))


def _load_toml_file(path: Path) -> dict[str, Any]:
    with path.open("rb") as file:
        return tomllib.load(file)


def _merge_preset_data(defaults: dict[str, Any], user: dict[str, Any]) -> dict[str, Any]:
    by_id = {item["id"]: item for item in defaults.get("preset", [])}
    for item in user.get("preset", []):
        by_id[item["id"]] = item
    return {"preset": list(by_id.values())}


def _parse_preset(item: dict[str, Any]) -> Preset:
    input_extensions = item.get("input_extensions", [])
    if not input_extensions:
        raise ValueError(f"Preset {item.get('id', '<missing id>')} has no input extensions")
    return Preset(
        id=item["id"],
        name=item["name"],
        category=item.get("category", "Other"),
        backend=item["backend"],
        output_extension=item["output_extension"].lower().lstrip("."),
        input_extensions=frozenset(extension.lower().lstrip(".") for extension in input_extensions),
        args=tuple(str(arg) for arg in item.get("args", [])),
    )
