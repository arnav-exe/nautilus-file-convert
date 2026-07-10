from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from nautilus_file_convert.presets import Preset


@dataclass(frozen=True)
class ConversionJob:
    preset: Preset
    input_path: Path
    output_path: Path
    command: tuple[str, ...]


def build_jobs(preset: Preset, input_paths: list[Path]) -> list[ConversionJob]:
    from nautilus_file_convert.backends.commands import build_command

    jobs: list[ConversionJob] = []
    for input_path in input_paths:
        output_path = unique_output_path(input_path, preset.output_extension)
        jobs.append(
            ConversionJob(
                preset=preset,
                input_path=input_path,
                output_path=output_path,
                command=tuple(build_command(preset, input_path, output_path)),
            )
        )
    return jobs


def unique_output_path(input_path: Path, output_extension: str) -> Path:
    suffix = "." + output_extension.lower().lstrip(".")
    candidate = input_path.with_suffix(suffix)
    if candidate != input_path and not candidate.exists():
        return candidate

    stem = input_path.stem
    for index in range(1, 1000):
        candidate = input_path.with_name(f"{stem} ({index}){suffix}")
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Could not create a unique output path for {input_path}")
