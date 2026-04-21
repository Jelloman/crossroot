"""
Integration tests: generate each scenario then run bootstrap.sh and nox -s check.

These tests are slower than test_generate.py because they execute uv sync and
full nox sessions inside the generated repo.  We use separate output directories
(run-*) so the two test files don't overwrite each other's repos.

We intentionally run `nox -s check` rather than bare `nox` to avoid the
`format` session (which modifies files in place) and `gen-agent-docs`.
"""

import logging
import os
import subprocess
import sys
from pathlib import Path

from conftest import BASH
from test_generate import (
    JAVA_ONLY,
    POLYGLOT,
    PYTHON_ONLY,
    TYPESCRIPT_BUN,
    TYPESCRIPT_NPM,
    TYPESCRIPT_ONLY,
    TYPESCRIPT_YARN,
)

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_ENV = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}


def _run(label: str, args: list[str], cwd: Path) -> None:
    log.info("$ %s", " ".join(args))
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True, env=_ENV)
    for line in result.stdout.splitlines():
        log.info("  %s", line)
    for line in result.stderr.splitlines():
        level = logging.WARNING if result.returncode != 0 else logging.INFO
        log.log(level, "  %s", line)
    assert result.returncode == 0, (
        f"{label} exited {result.returncode}\n"
        f"--- stdout ---\n{result.stdout}\n"
        f"--- stderr ---\n{result.stderr}"
    )
    log.info("%s passed", label)


def _bootstrap(out: Path) -> None:
    _run("bootstrap.sh", [BASH, "scripts/bootstrap.sh"], out)


def _nox_check(out: Path) -> None:
    _run("nox -s check", ["uv", "run", "nox", "-s", "check"], out)


def _ts_check(out: Path, pm: str) -> None:
    if sys.platform == "win32":
        cmd = ["cmd", "/c", pm, "run", "check"]
    else:
        cmd = [pm, "run", "check"]
    _run(f"{pm} run check", cmd, out)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_python_only_runs(generate) -> None:
    out = generate("run-python", PYTHON_ONLY)
    _bootstrap(out)
    _nox_check(out)


def test_typescript_only_runs(generate) -> None:
    out = generate("run-ts", TYPESCRIPT_ONLY)
    _bootstrap(out)
    _nox_check(out)
    _ts_check(out, TYPESCRIPT_ONLY["typescript_package_manager"])


def test_typescript_npm_runs(generate) -> None:
    out = generate("run-ts-npm", TYPESCRIPT_NPM)
    _bootstrap(out)
    _nox_check(out)
    _ts_check(out, "npm")


def test_typescript_yarn_runs(generate) -> None:
    out = generate("run-ts-yarn", TYPESCRIPT_YARN)
    _bootstrap(out)
    _nox_check(out)
    _ts_check(out, "yarn")


def test_typescript_bun_runs(generate) -> None:
    out = generate("run-ts-bun", TYPESCRIPT_BUN)
    _bootstrap(out)
    _nox_check(out)
    _ts_check(out, "bun")


def test_java_only_runs(generate) -> None:
    out = generate("run-java", JAVA_ONLY)
    _bootstrap(out)
    _nox_check(out)


def test_polyglot_runs(generate) -> None:
    out = generate("run-polyglot", POLYGLOT)
    _bootstrap(out)
    _nox_check(out)
    _ts_check(out, POLYGLOT["typescript_package_manager"])
