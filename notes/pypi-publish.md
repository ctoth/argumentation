# PyPI publish

## 2026-04-18

### GOAL
Publish the package to production PyPI for the first time using uv. Token in $PYPI_TOKEN.

### OBSERVED
- `pyproject.toml`: name=`argumentation`, version=`0.1.0`, build-backend=hatchling, packages=`src/argumentation`.
- `dist/` already had `argumentation-0.1.0-{whl,tar.gz}` (Apr 18 16:24). Will be regenerated under new dist name.
- PyPI **already hosts** `argumentation` 0.1.0, uploaded 2025-02-26, not yanked. Unrelated package ("Python argument parser for complex applications"). Confirmed via JSON API + Simple index. Project page hits Cloudflare bot challenge — JSON/Simple are authoritative.
- `pip show` showed nothing because it inspects the local venv, not PyPI. Use `pip index versions <name>` to query PyPI.

### NAME PROBE
Available (404): pyargumentation, py-argumentation, argumentation-kit, argumentation-py, formal-argumentation, dung-argumentation, af-argumentation, argkit, argumentations, argumentation-framework, argumentation-toolkit.
Taken (200): arglib, argue.

### DECISION
Q chose `formal-argumentation` after recommendation. Distribution name only — `import argumentation` stays.

### PLAN
1. Edit `pyproject.toml`: `name = "formal-argumentation"`.
2. Update README install lines (`uv add "argumentation @ ..."` → `uv add "formal-argumentation @ ..."`, plus the optional-deps variant). Title and prose can stay as `argumentation` since the import name is unchanged — only the dist name is being changed for PyPI.
3. Clean `dist/` (remove old `argumentation-*` artifacts).
4. `uv build`.
5. `uv publish --token "$PYPI_TOKEN"`.

### BLOCKER
None right now. Proceeding to edits + build + publish.

### IRREVERSIBILITY NOTE
Once published to prod PyPI, version `0.1.0` of `formal-argumentation` cannot be re-uploaded or deleted. If the wheel turns out wrong, the only path is bumping to 0.1.1.

### OUTCOME
Published `formal-argumentation` 0.1.0 to prod PyPI. Both wheel + sdist live, verified via JSON API. https://pypi.org/project/formal-argumentation/0.1.0/

### GOTCHA — TOKEN QUOTING
First publish attempt 403'd. `$PYPI_TOKEN` was set to a value beginning with a literal `"` (length 181, prefix `"pyp`). Stripped surrounding quotes at the call site (`${PYPI_TOKEN%\"}` then `${PYPI_TOKEN#\"}`), retry succeeded. Q's env was not modified — only the value passed to `uv publish` was cleaned. If Q wants this not to bite again, fix the env var so it holds `pypi-...` without quotes.
