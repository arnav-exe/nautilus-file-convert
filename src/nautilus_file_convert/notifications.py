from __future__ import annotations

import shutil
import subprocess


def notify(summary: str, body: str = "") -> None:
    executable = shutil.which("notify-send")
    if executable is None:
        return
    subprocess.Popen(
        [executable, "Nautilus File Convert", summary, body],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
