import io
from contextlib import redirect_stdout
from unittest import TestCase

from nautilus_file_convert.cli import main


class CliTests(TestCase):
    def test_dry_run_prints_command(self) -> None:
        output = io.StringIO()

        with redirect_stdout(output):
            exit_code = main(["convert", "--preset-id", "to-mp3", "--dry-run", "song.wav"])

        self.assertEqual(exit_code, 0)
        self.assertIn("ffmpeg", output.getvalue())
        self.assertIn("song.mp3", output.getvalue())
