from __future__ import annotations

import os
from pathlib import Path

APP_ID = "nautilus-file-convert"


def _xdg_path(env_name: str, default: Path) -> Path:
    value = os.environ.get(env_name)
    return Path(value).expanduser() if value else default


def config_dir() -> Path:
    return _xdg_path("XDG_CONFIG_HOME", Path.home() / ".config") / APP_ID


def cache_dir() -> Path:
    return _xdg_path("XDG_CACHE_HOME", Path.home() / ".cache") / APP_ID


def state_dir() -> Path:
    return _xdg_path("XDG_STATE_HOME", Path.home() / ".local" / "state") / APP_ID


def user_presets_path() -> Path:
    return config_dir() / "presets.toml"


def menu_cache_path() -> Path:
    return cache_dir() / "menu-cache.json"


def logs_dir() -> Path:
    return state_dir() / "logs"
