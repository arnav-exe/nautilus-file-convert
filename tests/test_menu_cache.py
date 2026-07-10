import json
import tempfile
from pathlib import Path
from unittest import TestCase

from nautilus_file_convert.menu_cache import write_menu_cache


class MenuCacheTests(TestCase):
    def test_writes_cache(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = write_menu_cache(Path(directory) / "menu-cache.json")

            data = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(data["version"], 1)
        self.assertTrue(data["presets"])
