# formal-argumentation release review — 2026-04-18

GOAL: Produce four-section public-release review of this Python package.

## Observations

- pyproject.toml: name=formal-argumentation, version=0.1.0, Dev Status :: 3 - Alpha. No `license` field, no `license-files`, no LICENSE file at repo root. Classifiers omit any License :: trove. Authors entry has no email.
- No LICENSE / COPYING / CHANGELOG / AUTHORS at repo root.
- .gitignore missing: `dist/`, `*.egg-info/`, `build/`, `.hypothesis/`, `notes/`, `pyghidra_mcp_projects/`, `.venv/` is listed. `dist/` tracked-wheel artifacts currently untracked but present.
- README install uses `uv add` only; no `pip install formal-argumentation`. Powershell fences only.
- `src/argumentation/__init__.py` re-exports 8 submodules but NOT `dung_z3`, `solver`, `probabilistic_components`, `probabilistic_dfquad`, `probabilistic_treedecomp`. README references `argumentation.dung_z3` — works via explicit import, but not in `__all__`.
- README mentions dfquad strategies `dfquad_quad`/`dfquad_baf`; probabilistic.py `_ALLOWED_STRATEGIES` includes them. OK.
- Repo contains `pyghidra_mcp_projects/` dir — unrelated artifacts sitting in repo root.
- Tests: 267 passed in 27.41s. pytest markers unit/property/differential declared.
- `requires-python = ">=3.11"` — uses `frozenset[str]` PEP 585 generics everywhere (fine on 3.11+).
- No CI config (.github/workflows) visible.
- No `py.typed` needs verification — file exists per ls.
- dung.py stable_extensions does NOT require admissibility (only conflict-free + attacks all outsiders); classical Dung stable is conflict-free + attacks outsiders — OK per Def 12. But preferred uses `<` on completes which works since frozenset supports strict subset.
- docs/architecture.md exists; only doc file.
- CONTRIBUTING refers only to powershell commands.
- Author: "ctoth" no email. Homepage URL points to github.com/ctoth/argumentation — can't verify without network.

## Gaps to check
- whether wheel contains py.typed (probably since packages=src/argumentation includes it)
- whether README examples actually work — didn't execute
- License absence is the blocker.

## Plan
Write the four-section response now, <=1200 words, under 100 words cap rule is overridden by task length spec.

## 2026-04-19 attack-pass on prior review

Verified facts (tool-observed):
- `.gitignore` (7 lines) lists `.venv/ .pytest_cache/ __pycache__/ *.py[cod] .coverage htmlcov/` — does NOT list `dist/`, `*.egg-info/`, `build/`, `.hypothesis/`, `notes/`, `pyghidra_mcp_projects/`. Prior review CORRECT.
- `dist/` contains wheel+sdist; `pyghidra_mcp_projects/` and `notes/` present untracked (git status). Untracked, not tracked — wording matters.
- Wheel `namelist()` shows no LICENSE/NOTICE file; no `formal_argumentation-0.1.0.dist-info/licenses/` entry. METADATA has no `License-Expression` / `License-File` / `Classifier: License` fields. License absence is real blocker.
- `src/argumentation/__init__.py` re-exports 8 modules; `dung_z3 solver probabilistic_components probabilistic_dfquad probabilistic_treedecomp` excluded. README does reference `argumentation.dung_z3` explicitly (verify).
- README Dung example executes correctly via `uv run`: grounded=∅, preferred=[{b},{a,c}], stable=[{b},{a,c}], complete=[∅,{b},{a,c}]. Order differs from README comment but set membership matches.
- `dung.py:262` stable uses `cf_relation = attacks if attacks is not None else defeats`; outsider coverage uses `defeats`. This is Modgil-Prakken style (CF on attacks, defeat on defeats), NOT classic Dung Def 12. Prior review glossed over this.
- `preferred_extensions` uses `ext < other` (strict subset on frozenset) — fine, prior review CORRECT.
- `py.typed` present in wheel — CORRECT.
- pyproject author has `name="ctoth"` no email — CORRECT.

Unverified/needs-check for attack pass:
- Does README actually reference `dung_z3`?  Need grep.
- Are there other README examples that break?
- CHANGELOG absent — trivially true (ls showed none).
- CI absent — no `.github/` in ls.
- stable semantics divergence: is this a missed blocker or an intentional M&P extension?
- `uv add formal-argumentation` — will it work without a published package? Prior review didn't flag this; only wheel is local.

Blockers to surface: license absent in wheel metadata AND sdist; stable semantics CF-on-attacks divergence from Dung Def 12 (the cited reference); untracked `pyghidra_mcp_projects/` is unrelated vendor dir inside repo; README install assumes published PyPI package.

