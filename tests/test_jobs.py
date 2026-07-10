import tempfile
from os import environ
from pathlib import Path
from unittest import TestCase

from nautilus_file_convert.jobs import build_jobs, unique_output_path
from nautilus_file_convert.presets import find_preset


class JobTests(TestCase):
    def test_generates_unique_output_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "clip.mov"
            input_path.write_text("fake", encoding="utf-8")
            existing = Path(directory) / "clip.mp4"
            existing.write_text("fake", encoding="utf-8")

            self.assertEqual(unique_output_path(input_path, "mp4"), Path(directory) / "clip (1).mp4")

    def test_builds_ffmpeg_command(self) -> None:
        preset = find_preset("to-mp4")

        job = build_jobs(preset, [Path("clip.mov")])[0]

        self.assertEqual(job.command[:5], ("ffmpeg", "-nostdin", "-hide_banner", "-n", "-i"))
        self.assertEqual(job.command[-1], "clip.mp4")

    def test_builds_imagemagick_command_from_override(self) -> None:
        preset = find_preset("to-png")
        old_value = environ.get("NAUTILUS_FILE_CONVERT_IMAGEMAGICK")
        environ["NAUTILUS_FILE_CONVERT_IMAGEMAGICK"] = "magick-test"
        try:
            job = build_jobs(preset, [Path("image.jpg")])[0]
        finally:
            if old_value is None:
                environ.pop("NAUTILUS_FILE_CONVERT_IMAGEMAGICK", None)
            else:
                environ["NAUTILUS_FILE_CONVERT_IMAGEMAGICK"] = old_value

        self.assertEqual(job.command[0], "magick-test")
        self.assertEqual(job.command[-1], "image.png")
