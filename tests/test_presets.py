from pathlib import Path
from unittest import TestCase

from nautilus_file_convert.presets import find_preset, load_presets


class PresetTests(TestCase):
    def test_loads_default_presets(self) -> None:
        presets = load_presets()

        self.assertTrue(any(preset.id == "to-mp4" for preset in presets))
        self.assertTrue(any(preset.id == "to-pdf" for preset in presets))

    def test_checks_multi_file_compatibility(self) -> None:
        preset = find_preset("to-mp4")

        self.assertTrue(preset.supports_all([Path("one.mov"), Path("two.mkv")]))
        self.assertFalse(preset.supports_all([Path("one.mov"), Path("two.png")]))
