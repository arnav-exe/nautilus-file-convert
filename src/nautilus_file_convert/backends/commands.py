from __future__ import annotations

from pathlib import Path
import os
import shutil

from nautilus_file_convert.presets import Preset


def build_command(preset: Preset, input_path: Path, output_path: Path) -> list[str]:
    if preset.backend == "ffmpeg":
        return _build_ffmpeg_command(preset, input_path, output_path)
    if preset.backend == "imagemagick":
        return _build_imagemagick_command(preset, input_path, output_path)
    raise ValueError(f"Unsupported backend: {preset.backend}")


def _build_ffmpeg_command(preset: Preset, input_path: Path, output_path: Path) -> list[str]:
    return [
        "ffmpeg",
        "-nostdin",
        "-hide_banner",
        "-n",
        "-i",
        str(input_path),
        *preset.args,
        str(output_path),
    ]


def _build_imagemagick_command(preset: Preset, input_path: Path, output_path: Path) -> list[str]:
    executable = os.environ.get("NAUTILUS_FILE_CONVERT_IMAGEMAGICK")
    if not executable:
        executable = "magick" if shutil.which("magick") else "convert"
    return [executable, str(input_path), *preset.args, str(output_path)]
