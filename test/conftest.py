import logging
import os
import shutil
import stat
import subprocess
import time
from pathlib import Path

import pytest

log = logging.getLogger(__name__)


def _find_git_bash() -> str:
    """Return the path to Git Bash on Windows, falling back to 'bash'.

    git.exe may live at <root>/cmd/git.exe or <root>/mingw64/bin/git.exe,
    so we walk up three levels looking for usr/bin/bash.exe.
    """
    import shutil as _shutil
    git = _shutil.which("git")
    if git:
        p = Path(git).resolve()
        for ancestor in [p.parent, p.parent.parent, p.parent.parent.parent]:
            candidate = ancestor / "usr" / "bin" / "bash.exe"
            if candidate.exists():
                return str(candidate)
    return "bash"


BASH = _find_git_bash()

TEMPLATE_ROOT = Path(__file__).parent.parent
OUT_DIR = Path(__file__).parent / "out"


def _force_rmtree(path: Path) -> None:
    """Remove a directory tree, clearing read-only bits on Windows before each delete."""
    def _on_error(func, p, _exc):
        try:
            os.chmod(p, stat.S_IWRITE)
            func(p)
        except OSError:
            pass
    shutil.rmtree(path, onerror=_on_error)


@pytest.fixture(autouse=True, scope="session")
def clean_out():
    log.info("Cleaning output directory: %s", OUT_DIR)
    _force_rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    yield
    log.info("Removing output directory: %s", OUT_DIR)
    _force_rmtree(OUT_DIR)


@pytest.fixture(scope="session")
def generate(clean_out):
    def _generate(name: str, data: dict[str, str]) -> Path:
        dest = OUT_DIR / name
        if dest.exists():
            _force_rmtree(dest)
        log.info("Generating '%s' → %s", name, dest)
        args = ["copier", "copy", "--trust", "--defaults", "--overwrite", "--vcs-ref", "HEAD"]
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
