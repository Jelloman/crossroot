import logging
import shutil
import subprocess
import time
from pathlib import Path

import pytest

log = logging.getLogger(__name__)

TEMPLATE_ROOT = Path(__file__).parent.parent
OUT_DIR = Path(__file__).parent / "out"


@pytest.fixture(autouse=True, scope="session")
def clean_out():
    log.info("Cleaning output directory: %s", OUT_DIR)
    shutil.rmtree(OUT_DIR, ignore_errors=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    yield
    log.info("Removing output directory: %s", OUT_DIR)
    shutil.rmtree(OUT_DIR, ignore_errors=True)


@pytest.fixture(scope="session")
def generate(clean_out):
    def _generate(name: str, data: dict[str, str]) -> Path:
        dest = OUT_DIR / name
        log.info("Generating '%s' → %s", name, dest)
        args = ["copier", "copy", "--trust", "--defaults", "--overwrite"]
        for key, value in data.items():
            args += ["--data", f"{key}={value}"]
        args += [str(TEMPLATE_ROOT), str(dest)]

        t0 = time.monotonic()
        subprocess.run(args, check=True, capture_output=True, text=True)
        elapsed = time.monotonic() - t0

        file_count = sum(1 for p in dest.rglob("*") if p.is_file())
        log.info("Generated %d files in %.2fs", file_count, elapsed)
        return dest

    return _generate
