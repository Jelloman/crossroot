# crossroot

crossroot is a Copier-powered framework for bootstrapping and evolving multi-language, cross-platform monorepos with a lightweight root control plane, a strict modern Python stack, and synchronized instructions for coding agents.

crossroot uses a Python-based root control plane and optional language islands. Python powers repository orchestration, validation, template updates, and agent-doc generation, while language-specific modules preserve their own native toolchains and conventions.

crossroot has an opinionated set of tooling for each language, based around strict linting, type checking and unit testing.

It is designed for repos that want:
- Root-level command ergonomics across multiple language subprojects.
- A clean, deliberate root directory instead of tool sprawl.
- First-class support for Windows, macOS, and Linux.
- A bash-first command surface, using Git Bash on Windows.
- A reusable Python control layer built on `uv`, `nox`, `ruff`, `basedpyright`, `pytest`, and `Copier`.
- A single source of truth for `CLAUDE.md`, `AGENTS.md`, and editor/agent rules.

## Quick Start

```bash
# Install Copier (once)
uv tool install copier

# Generate a new repo from crossroot
copier copy gh:Jelloman/crossroot path/to/new-repo

# Bootstrap and validate
cd path/to/new-repo
bash scripts/bootstrap.sh   # installs deps; then add scripts/ to your PATH
croot check                 # runs lint, typecheck, and tests
```

## Instructions

Generated repos ship with a `scripts/` directory. The `croot` dispatcher is the
primary entry point; the rest are invoked either through `croot` or directly.

| Script | Purpose |
|--------|---------|
| `croot` | Dispatcher that finds the repo root (via `.copier-answers.yml`) and forwards to the scripts below. Run `croot <command>` from anywhere in the repo. |
| `bootstrap.sh` | Verifies required tools (git, uv, and any language-module tools), runs `uv sync`, installs TypeScript/Java deps if enabled, and advises on adding `scripts/` to your `PATH`. |
| `check.sh` | Runs the `check` Nox session (`uv run nox -s check`) — lint, format check, typecheck, and tests across enabled language modules. |
| `doctor.sh` | Diagnoses the local environment: prints OS, shell, detected tool versions, and the presence of key repo files. Use when something seems off. |
| `gen-agent-docs.sh` | Regenerates `CLAUDE.md`, `AGENTS.md`, and `.cursor/rules/` from the canonical sources in `docs/agent-src/`. Run after editing agent docs. |
| `update-template.sh` | Applies upstream crossroot template changes to the repo via `copier update --trust`. Review the diff carefully before committing. |

## Why crossroot

I've started multiple Python projects recently and find myself repeating a lot of setup and tooling.
Some of my projects are Python-only, others are polyglot.
Problems I'm addressing:
- rebuilding tooling from scratch in every new project;
- multi-language repos grow inconsistent command patterns;
- Windows support becomes accidental or broken;
- root directories collect random scripts and docs;
- proliferation of directories I need to run things from; 
- agent instructions drift, and need to be repeated.

crossroot is meant to solve those problems at the repo-framework level.

## What crossroot provides

crossroot gives you a **root control plane** for a polyglot repo:
- a standard root command model;
- root-level validation and diagnostics;
- a synchronized agent-doc system;
- cross-platform CI expectations;
- optional language modules with opinionated defaults.

The root is intentionally small. Language-specific work lives in language-specific subprojects.

## Core principles

- The root is a control plane, not a junk drawer.
- Bash is the baseline shell.
- Windows support means Git Bash is supported intentionally, not accidentally.
- Python execution happens through `uv run` and/or Nox.
- Multi-language repos should keep each language in a clear island.
- Agent instructions should be generated from one canonical source.
- CI should enforce cross-platform behavior instead of trusting it.
- The template must support both project creation and ongoing updates.

## Scope

crossroot is a **repo framework**, not an app framework.

It does:
- bootstrap repository structure;
- standardize commands and docs;
- set Python defaults;
- coordinate multiple language subprojects;
- support template updates via Copier.

It does not:
- replace native build systems for Python, Java, TypeScript, Rust, Go, or other languages;
- require every repo to include every language;
- force every Python repo into one workspace model;
- aim for every shell or editor to be equally supported.

## Default Python stack

The default Python toolchain is:
- `uv`
- `nox`
- `ruff`
- `basedpyright`
- `pytest`
- `Copier`

These tools form the default Python control layer for the repository.

## Language modules

crossroot is designed as:
- a **core control-plane template**, plus
- optional **language modules**.

Initial target modules:
- Python
- TypeScript
- Java

Planned future modules:
- Rust
- Go

Each module should preserve that language’s native best practices while integrating with the root command model and docs system.

## Typical layout

```text
repo/
├─ pyproject.toml
├─ uv.lock
├─ noxfile.py
├─ copier.yml
├─ .copier-answers.yml
├─ CLAUDE.md
├─ AGENTS.md
├─ .cursor/
│  └─ rules/
├─ .github/
│  └─ workflows/
├─ scripts/
├─ docs/
│  └─ agent-src/
├─ python/
├─ typescript/
├─ java/
├─ rust/
├─ go/
├─ infra/
└─ util/
```

Not every directory needs to exist in every generated repo. The structure is modular.

## Standard root commands

A crossroot repo should expose a small and predictable set of root commands, such as:
- `bootstrap`
- `check`
- `test`
- `lint`
- `format`
- `typecheck`
- `doctor`
- `update-template`

These commands may delegate to `uv`, Nox, npm/pnpm/bun, Gradle, or other native tools under the hood.

## Agent docs

crossroot uses one canonical source for repo instructions and generates:
- `CLAUDE.md`
- `AGENTS.md`
- Cursor rules
- other editor/agent-specific outputs later if desired

The goal is to keep agent instructions short, layered, and synchronized.

## Platform support

crossroot treats these as first-class:
- Windows via Git Bash
- macOS via native bash
- Linux via native bash

Every generated repo should validate on all three in CI.

## Long-term vision

crossroot should let a repo start small, grow across languages, and still feel coherent months later.

The root stays light.
Commands stay predictable.
Python stays modern.
Other languages keep their own best practices.
Agent guidance stays in sync.
