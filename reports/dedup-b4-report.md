# B4 report (CRLF-redo): extract shared adapter command-helpers into `solver_adapters/_commands.py`

Branch: `refactor/dedup`. Status: COMPLETE. All test/pyright via `uv run`.

## Why this redo
The first B4 attempt (commits 8ca0a75 + a15e604, now rewound) passed on behavior
but FAILED Codex review on LINE ENDINGS: the Write/Edit tooling normalized
CRLF->LF on every touched file. Consequences: the 6 helpers in `_commands.py`
were LF while the CRLF parent originals made them only normalized-identical
(not byte-identical), and `test_solver_adapters.py` was rewritten whole-file
CRLF->LF (~973 lines), making the 23-repoint diff unreviewable. This redo
preserves each file's existing EOL.

## Step 1 — canonical line endings
- NO `.gitattributes` anywhere (disk or tracked); `core.autocrlf=false`,
  `core.eol` unset. There is NO LF policy, so parent blobs are the truth.
- Parent (`f7d8be5`) blob EOL, measured by BYTES:
  - `src/.../iccma_af.py` -> CRLF (601 CRLF, 0 lone LF)
  - `src/.../iccma_aba.py` -> CRLF (401, 0)
  - `tests/solving/test_solver_adapters.py` -> CRLF (971, 0)
  - `tests/structured/aba/test_aba.py` -> **LF-only (705 lone LF, 0 CRLF)**

`test_aba.py` is genuinely an LF file in this repo (verified: `git status`
clean, HEAD blob is LF). The redo therefore preserves CRLF on the three CRLF
files and LF on `test_aba.py`.

## Step 2 — rewind
`git reset --hard f7d8be5` -> HEAD at `f7d8be5` ("docs: record final B3 dedup
commit hash in report"); both B4 commits gone. `reports/dedup-b4-verify-report.md`
(untracked) left on disk.

## Step 3 — extraction (CRLF-preserving, byte-level)
- `src/argumentation/solver_adapters/_commands.py`: 6 helpers extracted as exact
  AST spans from the CRLF parent `iccma_af.py` and written as BYTES with CRLF.
  Result: 68 CRLF, 0 lone LF.
- `iccma_af.py` / `iccma_aba.py`: byte-level exact-string edits (no whole-file
  rewrite). Dropped now-unused `os` / `shlex` / `shutil` imports, added
  `from argumentation.solver_adapters._commands import (_problem_prefix, _resolve_command, _semantic_lines, _timeout_stream)`,
  deleted the 6 local helper defs. CRLF preserved (af 555/0, aba 355/0). No
  helper defs remain in either adapter.
- `clingo.py`: untouched (its distinct `_resolve_command` — no shlex, with
  `sys.executable -m clingo` fallback — is intentionally not merged). `git diff
  --stat` on clingo.py is empty.

## Step 4 — tests
- `tests/solving/test_solver_command_helpers.py`: new characterization tests for
  the shared helpers, including the flagged edge cases (unbalanced/lone quote ->
  `[]`; dequoted/mismatched/nested-quote `_strip_outer_quotes`; `_resolve_command`
  existing-path precedence, unknown -> None, command-line-with-args, unbalanced
  -> None, empty-string `Path("")`->`.` quirk; `_timeout_stream` invalid-byte
  `errors="replace"` -> U+FFFD; `_problem_prefix`/`_semantic_lines` filtering;
  single-source-of-truth identity check). Written as CRLF (239, 0 lone LF).
- `tests/solving/test_solver_adapters.py`: ONLY the 23 `shutil.which` patch-target
  repoints (14 af + 9 aba) `iccma_af.shutil.which`/`iccma_aba.shutil.which` ->
  `_commands.shutil.which`, applied at byte level. CRLF preserved (971, 0 lone LF).
  Required because `shutil.which` now executes inside `_commands._resolve_command`;
  production behavior unchanged.
- `tests/structured/aba/test_aba.py`: 2 same repoints, LF preserved (705, 0 CRLF).

## Verify — pasted output

### Staged diff-stat (test_solver_adapters.py = 46 lines = 23 repoints, NOT ~1900)

```
$ git diff --cached --stat
 src/argumentation/solver_adapters/_commands.py |  68 +++++++
 src/argumentation/solver_adapters/iccma_aba.py |  58 +-----
 src/argumentation/solver_adapters/iccma_af.py  |  58 +-----
 tests/solving/test_solver_adapters.py          |  46 ++---
 tests/solving/test_solver_command_helpers.py   | 239 +++++++++++++++++++++++++
 tests/structured/aba/test_aba.py               |   4 +-
 6 files changed, 344 insertions(+), 129 deletions(-)
```

The two adapter diffs are identical with and without `--ignore-space-at-eol`
(58 lines each) => no EOL churn; they are real import/deletion changes.

### Byte-identity probe vs CRLF parent (Codex's check)

```
$ python <AST-span extract of f7d8be5:iccma_af.py vs new _commands.py>
_resolve_command: BYTE-IDENTICAL  parent_crlf=13 new_crlf=13 bytes=452/452
_split_command: BYTE-IDENTICAL  parent_crlf=6 new_crlf=6 bytes=220/220
_strip_outer_quotes: BYTE-IDENTICAL  parent_crlf=4 new_crlf=4 bytes=169/169
_timeout_stream: BYTE-IDENTICAL  parent_crlf=6 new_crlf=6 bytes=206/206
_problem_prefix: BYTE-IDENTICAL  parent_crlf=2 new_crlf=2 bytes=89/89
_semantic_lines: BYTE-IDENTICAL  parent_crlf=6 new_crlf=6 bytes=194/194
ALL 6 BYTE-IDENTICAL TO CRLF PARENT: True
```

(`_resolve_command` now shows new_crlf=13, matching parent — the original failure
was head_crlf=0.)

### pytest

```
$ uv run python -m pytest tests/solving/test_solver_adapters.py tests/solving/test_solver_command_helpers.py tests/structured/aba/test_aba.py tests/solving/test_iccma_cli.py tests/interop -q
..........................s.............s............................... [ 40%]
........................................................................ [ 80%]
..................................                                       [100%]
176 passed, 2 skipped in 4.68s
```

(2 skips pre-existing: live external solver binaries not installed —
`ICCMA_AF_SOLVER` / `ASPFORABA_SOLVER`.)

### pyright

```
$ uv run python -m pyright src/argumentation/solver_adapters/_commands.py src/argumentation/solver_adapters/iccma_af.py src/argumentation/solver_adapters/iccma_aba.py tests/solving/test_solver_command_helpers.py
0 errors, 0 warnings, 0 informations
```

### clingo untouched + single-source helpers

```
$ git diff --stat -- src/argumentation/solver_adapters/clingo.py
(empty)
$ grep def _resolve_command|_split_command|_strip_outer_quotes|_timeout_stream|_problem_prefix|_semantic_lines
clingo.py:295:def _resolve_command(...)        # distinct variant, kept
_commands.py:22/37/45/51/59/63: the six shared helpers (only copy)
```

### EOL sanity (final, all staged files)

```
_commands.py                 CRLF=68   loneLF=0
iccma_af.py                  CRLF=555  loneLF=0
iccma_aba.py                 CRLF=355  loneLF=0
test_solver_command_helpers.py CRLF=239 loneLF=0
test_solver_adapters.py      CRLF=971  loneLF=0
test_aba.py                  CRLF=0    loneLF=705  (LF, matching its parent blob)
```

## Commit

`9f8979cc6cb7bab5b77f14fe5010605d996d71eb` on `refactor/dedup`
("refactor: extract shared ICCMA adapter command helpers").

## Out of scope — noticed
- `_resolve_command("")` returns `['.']` (`Path("")` normalizes to `.` which
  exists). Pinned as current behavior, not fixed.
- `_split_command` quote/posix handling is platform-dependent (`posix = os.name
  != "nt"`). Left as-is.
- The adapters still duplicate a `_command(...)` builder and `_parse_*` /
  `_unsupported_problem` scaffolding with small differences (not byte-identical) —
  out of scope for B4.
