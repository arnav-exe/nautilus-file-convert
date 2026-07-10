from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from nautilus_file_convert import paths
from nautilus_file_convert.jobs import ConversionJob


@dataclass(frozen=True)
class JobResult:
    job: ConversionJob
    return_code: int

    @property
    def succeeded(self) -> bool:
        return self.return_code == 0


def run_jobs(jobs: list[ConversionJob], dry_run: bool = False) -> list[JobResult]:
    if dry_run:
        return [JobResult(job=job, return_code=0) for job in jobs]

    log_file = _new_log_file()
    results: list[JobResult] = []
    with log_file.open("w", encoding="utf-8") as log:
        for job in jobs:
            log.write(f"[{datetime.now().isoformat(timespec='seconds')}] {job.input_path}\n")
            log.write("Command: " + " ".join(job.command) + "\n")
            completed = subprocess.run(
                ["nice", "-n", "10", "ionice", "-c", "2", "-n", "7", *job.command],
                stdout=log,
                stderr=subprocess.STDOUT,
                check=False,
            )
            log.write(f"Return code: {completed.returncode}\n\n")
            results.append(JobResult(job=job, return_code=completed.returncode))
    return results


def _new_log_file() -> Path:
    log_dir = paths.logs_dir()
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return log_dir / f"conversion-{timestamp}.log"
