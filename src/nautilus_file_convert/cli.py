from __future__ import annotations

import argparse
import json
import shlex
import sys
from pathlib import Path

from nautilus_file_convert import __version__
from nautilus_file_convert.jobs import build_jobs
from nautilus_file_convert.menu_cache import write_menu_cache
from nautilus_file_convert.notifications import notify
from nautilus_file_convert.presets import find_preset, load_presets, presets_json
from nautilus_file_convert.runner import run_jobs


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="nautilus-file-convert")
    parser.add_argument("--version", action="version", version=__version__)
    subparsers = parser.add_subparsers(required=True)

    presets_parser = subparsers.add_parser("presets")
    presets_subparsers = presets_parser.add_subparsers(required=True)

    presets_list = presets_subparsers.add_parser("list")
    presets_list.add_argument("--json", action="store_true", dest="as_json")
    presets_list.set_defaults(func=_presets_list)

    presets_cache = presets_subparsers.add_parser("rebuild-cache")
    presets_cache.set_defaults(func=_presets_rebuild_cache)

    convert = subparsers.add_parser("convert")
    convert.add_argument("--preset-id", required=True)
    convert.add_argument("--files-json", type=Path)
    convert.add_argument("--delete-files-json", action="store_true")
    convert.add_argument("--notify", action="store_true")
    convert.add_argument("--dry-run", action="store_true")
    convert.add_argument("files", nargs="*")
    convert.set_defaults(func=_convert)

    doctor = subparsers.add_parser("doctor")
    doctor.set_defaults(func=_doctor)
    return parser


def _presets_list(args: argparse.Namespace) -> int:
    if args.as_json:
        print(presets_json())
        return 0
    for preset in load_presets():
        print(f"{preset.id}\t{preset.name}")
    return 0


def _presets_rebuild_cache(args: argparse.Namespace) -> int:
    path = write_menu_cache()
    print(path)
    return 0


def _convert(args: argparse.Namespace) -> int:
    files = _load_files(args.files, args.files_json, args.delete_files_json)
    preset = find_preset(args.preset_id)
    if not preset.supports_all(files):
        print(f"Preset '{preset.name}' does not support every selected file.", file=sys.stderr)
        return 2

    jobs = build_jobs(preset, files)
    if args.dry_run:
        for job in jobs:
            print(shlex.join(job.command))
        return 0

    if args.notify:
        notify(f"Converting {len(jobs)} file(s)", f"Preset: {preset.name}")
    results = run_jobs(jobs)
    failed = [result for result in results if not result.succeeded]
    if args.notify:
        if failed:
            notify(f"{len(failed)} conversion(s) failed", "Check the conversion log for details.")
        else:
            notify(f"Converted {len(results)} file(s)")
    return 1 if failed else 0


def _doctor(args: argparse.Namespace) -> int:
    import shutil

    required = ["ffmpeg", "gs"]
    missing = [name for name in required if shutil.which(name) is None]
    if shutil.which("magick") is None and shutil.which("convert") is None:
        missing.append("magick or convert")
    if missing:
        print("Missing tools: " + ", ".join(missing))
        return 1
    print("All required tools found.")
    return 0


def _load_files(positional: list[str], files_json: Path | None, delete_files_json: bool) -> list[Path]:
    files = [Path(value).expanduser() for value in positional]
    if files_json:
        with files_json.open("r", encoding="utf-8") as file:
            files.extend(Path(value).expanduser() for value in json.load(file))
        if delete_files_json:
            files_json.unlink(missing_ok=True)
    if not files:
        raise SystemExit("No input files provided.")
    return files
