"""
Template generation tests.  Each scenario calls `copier copy --trust` into
test/out/<name>/ and asserts on the resulting file tree.
"""

import logging
import re
from pathlib import Path

log = logging.getLogger(__name__)

# Matches {{ that is NOT preceded by $ (i.e. not a GitHub Actions expression).
_JINJA_VAR = re.compile(r"(?<!\$)\{\{")

# ---------------------------------------------------------------------------
# Answer sets
# ---------------------------------------------------------------------------

# Mirrors test/script.txt exactly.
PYTHON_ONLY: dict[str, str] = {
    "project_name": "test-crossroot",
    "repo_slug": "test-crossroot",
    "project_description": "A crossroot-powered multi-language repository. TEST",
    "owner_name": "octocat",
    "github_owner": "octocat",
    "license_name": "MIT",
    "include_python": "true",
    "include_typescript": "false",
    "include_java": "false",
    "python_mode": "workspace",
    "python_version": "3.13",
    "python_default_app_name": "test_crossroot_py",
    "include_basedpyright": "true",
    "include_pytest": "true",
    "include_agent_docs": "true",
    "include_github_actions": "true",
    "include_doctor_script": "true",
    "include_update_script": "true",
    "create_example_apps": "true",
}

TYPESCRIPT_ONLY: dict[str, str] = {
    "project_name": "test-ts",
    "repo_slug": "test-ts",
    "project_description": "TypeScript-only crossroot test repo.",
    "owner_name": "octocat",
    "github_owner": "octocat",
    "license_name": "MIT",
    "include_python": "false",
    "include_typescript": "true",
    "include_java": "false",
    "typescript_package_manager": "pnpm",
    "typescript_version": "5",
    "eslint_version": "9",
    "typescript_test_runner": "vitest",
    "typescript_framework": "node-service",
    "include_agent_docs": "true",
    "include_github_actions": "true",
    "include_doctor_script": "true",
    "include_update_script": "true",
    "create_example_apps": "false",
}

TYPESCRIPT_NPM: dict[str, str] = {
    "project_name": "test-ts-npm",
    "repo_slug": "test-ts-npm",
    "project_description": "TypeScript npm test repo.",
    "owner_name": "octocat",
    "github_owner": "octocat",
    "license_name": "MIT",
    "include_python": "false",
    "include_typescript": "true",
    "include_java": "false",
    "typescript_package_manager": "npm",
    "typescript_version": "5",
    "eslint_version": "9",
    "typescript_test_runner": "vitest",
    "typescript_framework": "node-service",
    "include_agent_docs": "true",
    "include_github_actions": "true",
    "include_doctor_script": "true",
    "include_update_script": "true",
    "create_example_apps": "false",
}

TYPESCRIPT_YARN: dict[str, str] = {
    "project_name": "test-ts-yarn",
    "repo_slug": "test-ts-yarn",
    "project_description": "TypeScript yarn test repo.",
    "owner_name": "octocat",
    "github_owner": "octocat",
    "license_name": "MIT",
    "include_python": "false",
    "include_typescript": "true",
    "include_java": "false",
    "typescript_package_manager": "yarn",
    "typescript_version": "5",
    "eslint_version": "9",
    "typescript_test_runner": "vitest",
    "typescript_framework": "node-service",
    "include_agent_docs": "true",
    "include_github_actions": "true",
    "include_doctor_script": "true",
    "include_update_script": "true",
    "create_example_apps": "false",
}

TYPESCRIPT_BUN: dict[str, str] = {
    "project_name": "test-ts-bun",
    "repo_slug": "test-ts-bun",
    "project_description": "TypeScript bun test repo.",
    "owner_name": "octocat",
    "github_owner": "octocat",
    "license_name": "MIT",
    "include_python": "false",
    "include_typescript": "true",
    "include_java": "false",
    "typescript_package_manager": "bun",
    "typescript_version": "5",
    "eslint_version": "9",
    "typescript_test_runner": "vitest",
    "typescript_framework": "node-service",
    "include_agent_docs": "true",
    "include_github_actions": "true",
    "include_doctor_script": "true",
    "include_update_script": "true",
    "create_example_apps": "false",
}

JAVA_ONLY: dict[str, str] = {
    "project_name": "test-java",
    "repo_slug": "test-java",
    "project_description": "Java-only crossroot test repo.",
    "owner_name": "octocat",
    "github_owner": "octocat",
    "license_name": "MIT",
    "include_python": "false",
    "include_typescript": "false",
    "include_java": "true",
    "java_build_tool": "gradle",
    "java_project_kind": "application",
    "include_agent_docs": "true",
    "include_github_actions": "true",
    "include_doctor_script": "true",
    "include_update_script": "true",
    "create_example_apps": "false",
}

POLYGLOT: dict[str, str] = {
    "project_name": "test-polyglot",
    "repo_slug": "test-polyglot",
    "project_description": "Polyglot crossroot test repo.",
    "owner_name": "octocat",
    "github_owner": "octocat",
    "license_name": "MIT",
    "include_python": "true",
    "include_typescript": "true",
    "include_java": "true",
    "python_mode": "workspace",
    "python_version": "3.13",
    "python_default_app_name": "test_polyglot_py",
    "include_basedpyright": "true",
    "include_pytest": "true",
    "typescript_package_manager": "pnpm",
    "typescript_version": "5",
    "eslint_version": "9",
    "typescript_test_runner": "vitest",
    "typescript_framework": "node-service",
    "java_build_tool": "gradle",
    "java_project_kind": "application",
    "include_agent_docs": "true",
    "include_github_actions": "true",
    "include_doctor_script": "true",
    "include_update_script": "true",
    "create_example_apps": "false",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_TEXT_SUFFIXES = {
    ".py", ".toml", ".yml", ".yaml", ".sh", ".md", ".mdc",
    ".json", ".ts", ".kts", ".txt", ".cfg", ".ini", ".html",
}
# copier.yml in generated repos is intentionally a stub that may be edited
# by users to hold Jinja; skip it in the artifact scan.
_JINJA_SCAN_SKIP = {"copier.yml"}


def assert_core_files(out: Path, data: dict[str, str]) -> None:
    log.info("Checking core files...")
    required = [
        ".copier-answers.yml",
        "README.md",
        "pyproject.toml",
        "noxfile.py",
        "scripts/croot",
        "scripts/bootstrap.sh",
        "scripts/check.sh",
        "go/README.md",
        "rust/README.md",
    ]
    for rel in required:
        assert (out / rel).exists(), f"Missing core file: {rel}"

    if data.get("include_agent_docs") == "true":
        log.info("Checking agent-doc files...")
        agent_files = [
            "CLAUDE.md",
            "AGENTS.md",
            ".cursor/rules/platform-rules.mdc",
            ".cursor/rules/project-overview.mdc",
            ".cursor/rules/workflows.mdc",
            "docs/agent-src/overview.md",
            "docs/agent-src/coding-standards.md",
            "docs/agent-src/workflows.md",
            "docs/agent-src/platform-rules.md",
            "scripts/gen-agent-docs.sh",
            "tools/render_agent_docs.py",
        ]
        for rel in agent_files:
            assert (out / rel).exists(), f"Missing agent-doc file: {rel}"

    if data.get("include_github_actions") == "true":
        assert (out / ".github/workflows/ci.yml").exists()
        assert (out / ".github/workflows/validate-template.yml").exists()

    if data.get("include_doctor_script") == "true":
        assert (out / "scripts/doctor.sh").exists()

    if data.get("include_update_script") == "true":
        assert (out / "scripts/update-template.sh").exists()


def assert_no_jinja_artifacts(out: Path) -> None:
    """Fail if any rendered text file still contains raw Jinja syntax."""
    checked = 0
    for path in out.rglob("*"):
        if not path.is_file():
            continue
        if path.name in _JINJA_SCAN_SKIP:
            continue
        if path.suffix.lower() not in _TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        checked += 1
        rel = path.relative_to(out)
        assert not _JINJA_VAR.search(text), f"Unrendered Jinja variable in {rel}"
        assert "{%" not in text, f"Unrendered Jinja block in {rel}"
    log.info("Jinja artifact scan: %d text files checked, none contained raw Jinja", checked)


def assert_python_module(out: Path, app_name: str) -> None:
    log.info("Checking Python module '%s'...", app_name)
    python_files = [
        f"python/apps/{app_name}/pyproject.toml",
        f"python/apps/{app_name}/src/{app_name}/__init__.py",
        f"python/apps/{app_name}/tests/test_placeholder.py",
        "python/libs/.gitkeep",
        "python/tools/.gitkeep",
    ]
    for rel in python_files:
        assert (out / rel).exists(), f"Missing Python file: {rel}"


def assert_typescript_module(out: Path, data: dict[str, str]) -> None:
    log.info("Checking TypeScript module...")
    ts_files = [
        "package.json",
        "tsconfig.base.json",
        "tsconfig.json",
        "eslint.config.mjs",
        ".prettierrc",
        "typescript/packages/.gitkeep",
        "typescript/tools/.gitkeep",
    ]
    for rel in ts_files:
        assert (out / rel).exists(), f"Missing TypeScript file: {rel}"

    pm = data.get("typescript_package_manager", "pnpm")
    if pm == "pnpm":
        assert (out / "pnpm-workspace.yaml").exists(), "Missing pnpm-workspace.yaml"
        assert not (out / ".yarnrc.yml").exists(), ".yarnrc.yml should be absent for pnpm"
    elif pm == "yarn":
        assert (out / ".yarnrc.yml").exists(), "Missing .yarnrc.yml for yarn"
        assert not (out / "pnpm-workspace.yaml").exists(), "pnpm-workspace.yaml should be absent for yarn"
    else:
        assert not (out / "pnpm-workspace.yaml").exists(), "pnpm-workspace.yaml should be absent"
        assert not (out / ".yarnrc.yml").exists(), ".yarnrc.yml should be absent"

    framework = data.get("typescript_framework", "none")
    if framework != "none":
        assert (out / "typescript/apps/web/package.json").exists(), "Missing typescript/apps/web/package.json"
        assert (out / "typescript/apps/web/tsconfig.json").exists(), "Missing typescript/apps/web/tsconfig.json"
        assert (out / "typescript/apps/web/src/index.ts").exists(), "Missing typescript/apps/web/src/index.ts"
        runner = data.get("typescript_test_runner", "vitest")
        if runner == "vitest":
            assert (out / "typescript/apps/web/vitest.config.ts").exists(), "Missing vitest.config.ts"
            assert not (out / "typescript/apps/web/jest.config.js").exists(), "jest.config.js should be absent"
        else:
            assert (out / "typescript/apps/web/jest.config.js").exists(), "Missing jest.config.js"
            assert not (out / "typescript/apps/web/vitest.config.ts").exists(), "vitest.config.ts should be absent"


def assert_java_module(out: Path) -> None:
    log.info("Checking Java module...")
    java_files = [
        "java/build.gradle.kts",
        "java/settings.gradle.kts",
        "java/apps/app/build.gradle.kts",
        "java/libs/.gitkeep",
        "java/tools/.gitkeep",
    ]
    for rel in java_files:
        assert (out / rel).exists(), f"Missing Java file: {rel}"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_python_only(generate) -> None:
    out = generate("test-python", PYTHON_ONLY)

    assert_core_files(out, PYTHON_ONLY)
    assert_python_module(out, "test_crossroot_py")
    assert_no_jinja_artifacts(out)

    assert not (out / "typescript").exists(), "typescript/ should be absent"
    assert not (out / "java").exists(), "java/ should be absent"


def test_typescript_only(generate) -> None:
    out = generate("test-ts", TYPESCRIPT_ONLY)

    assert_core_files(out, TYPESCRIPT_ONLY)
    assert_typescript_module(out, TYPESCRIPT_ONLY)
    assert_no_jinja_artifacts(out)

    assert not (out / "python").exists(), "python/ should be absent"
    assert not (out / "java").exists(), "java/ should be absent"


def test_java_only(generate) -> None:
    out = generate("test-java", JAVA_ONLY)

    assert_core_files(out, JAVA_ONLY)
    assert_java_module(out)
    assert_no_jinja_artifacts(out)

    assert not (out / "python").exists(), "python/ should be absent"
    assert not (out / "typescript").exists(), "typescript/ should be absent"


def test_polyglot(generate) -> None:
    out = generate("test-polyglot", POLYGLOT)

    assert_core_files(out, POLYGLOT)
    assert_python_module(out, "test_polyglot_py")
    assert_typescript_module(out, POLYGLOT)
    assert_java_module(out)
    assert_no_jinja_artifacts(out)
