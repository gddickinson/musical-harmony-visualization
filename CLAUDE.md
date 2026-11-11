# Claude collaboration notes for `muscial-harmony-visualization`

This project was built with substantial assistance from **Claude (Anthropic)**, primarily via **Claude Code**.

## Global preferences

George's global Claude preferences live in `~/.claude/CLAUDE.md` and apply to every project. Highlights:

- Keep all source files under 500 lines; split into focused modules if approaching that limit.
- For Python projects, maintain an `INTERFACE.md` at the project root as a navigation map of modules, classes, and key functions.
- Prefer many small, focused files over fewer large ones.
- Group related functionality; extract reusable logic into utility modules.

## Project navigation

@INTERFACE.md

See [`INTERFACE.md`](./INTERFACE.md) for a navigation map of this repository's modules and how they connect. Read `INTERFACE.md` before opening individual source files.

## Working with Claude on this repo

When directing Claude Code on this codebase, follow the global rules above, prefer making targeted edits via the `Edit` tool over rewriting whole files, and update `INTERFACE.md` whenever the project structure changes.

## Web interface

`web/` (FastAPI + ES modules, `python run_web.py`, port 8165) and the static GitHub Pages site. The JS engines in
`web/static/*_engine.js` port `theory.py`, `harmony_layout.py` and `synthesis.py`: after changing those, run
`python scripts/make_fixture.py` and `python -m pytest -q tests/ test_theory.py` (includes the node tests).
