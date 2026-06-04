# Dedup B5 report — unify 5 semantics-dispatch copies into `core.dung.extensions_for`

Branch: `refactor/dedup`. All commands run via `uv run`.

## STEP 1 — confirmation (all 5 dispatch to the SAME `core.dung` functions)

Verified by reading each file's `from argumentation.core.dung import (...)` block: every
extension-function name used in every dispatch is imported from `argumentation.core.dung`. No copy
dispatches any key to a framework-specific / non-dung function. Folding is safe.

| Copy (loc at HEAD) | function | supported keys | target functions (all `core.dung`) | error for unsupported | return type |
|---|---|---|---|---|---|
| `dynamics/enforcement.py:227` | `extensions_for` | grounded, complete, preferred, stable, semi-stable, stage, ideal, cf2 (8) | grounded_extension, complete_extensions, preferred_extensions, stable_extensions, semi_stable_extensions, stage_extensions, ideal_extension, cf2_extensions | `ValueError(f"unsupported semantics: {semantics}")` | `tuple[frozenset[str], ...]`; grounded/ideal wrapped as 1-tuple |
| `frameworks/caf.py:154` | `_argument_extensions` | grounded, complete, preferred, stable, semi-stable, stage, **naive**, cf2 (8; has `naive`, **lacks** `ideal`) | same as above but `naive_extensions` instead of `ideal_extension` | `ValueError(f"unsupported CAF semantics: {semantics}")` | `tuple[frozenset[str], ...]`; grounded wrapped as 1-tuple |
| `frameworks/partial_af.py:161` | `_extensions_for_completion` | grounded, preferred, stable (3) | grounded_extension, preferred_extensions, stable_extensions | `ValueError(f"Unknown semantics: {semantics}")` | **`list[frozenset[str]]`**; preferred/stable rewrapped via `frozenset(...)` |
| `probabilistic/probabilistic.py:457` | `_extensions_for_semantics` | grounded, preferred, stable, complete (4) | grounded_extension, preferred_extensions, stable_extensions, complete_extensions | `ValueError(f"Unknown semantics: {semantics}")` | `tuple[frozenset[str], ...]`; grounded wrapped as 1-tuple |

The "5th copy" is `dynamics/dynamic.py:14`, which does not have its own dispatch body — it imports
`SemanticsName, extensions_for` from `dynamics.enforcement` and reuses them. Preserved by re-export.

Single-extension wrapping (grounded, ideal → 1-tuple) and the `tuple(...)` wrapping for multi-extension
semantics are byte-identical across the tuple-returning copies, so they collapse into the canonical
helper with no behavior change. `partial_af`'s `frozenset(extension)` rewraps are equivalent because the
core extension functions already return `frozenset` elements; its only real difference is the `list`
container, which is preserved (see below).

### partial_af call-site finding
`_extensions_for_completion` has exactly two call sites, both in `partial_af.py`:
- `skeptically_accepted_arguments` (`for extension in _extensions_for_completion(...)`, line ~184)
- `credulously_accepted_arguments` (`for extension in _extensions_for_completion(...)`, line ~202)

Both only **iterate** the result — neither indexes nor mutates it — so they are tuple-compatible.
Per the prompt's default-to-safe directive, the `list` return type was nevertheless preserved
(`list(core.extensions_for(...))`).

## STEP 2 — canonical helper (`src/argumentation/core/dung.py`)

Added at end of `core/dung.py` (co-located with the extension functions; no new module):

```python
SemanticsName = Literal[
    "grounded", "complete", "preferred", "stable",
    "semi-stable", "stage", "ideal", "cf2", "naive",
]   # the UNION of all callers' keys

def extensions_for(framework, semantics: SemanticsName) -> tuple[frozenset[str], ...]:
    # grounded/ideal -> 1-tuple; everything else -> tuple(<list-returning fn>)
    # raises ValueError(f"unsupported semantics: {semantics}") for keys outside the union
```

Also added `from typing import Literal` to the import block. `core.dung` is the lowest layer, so
frameworks + probabilistic + dynamics import it with no upward edge.

## STEP 3 — each caller delegates while preserving its contract

- **`enforcement.py`**: keeps its OWN 8-key `SemanticsName` Literal (grounded, complete, preferred,
  stable, semi-stable, stage, ideal, cf2 — **no `naive`**) and a `_SUPPORTED_SEMANTICS` frozenset of
  those 8 keys. `extensions_for` is a guarded wrapper: it raises the original
  `ValueError(f"unsupported semantics: {semantics}")` for any key outside the 8-key allow-set, otherwise
  delegates the computation to `core.dung.extensions_for` (imported as `_dung_extensions_for`). Both
  `SemanticsName` and `extensions_for` remain importable from `argumentation.dynamics.enforcement`, so
  `dynamic.py:14` and the import-boundary test stay green, and `enforcement.SemanticsName` remains the
  original 8-key type that `dynamic.py` depends on. (See the v2 fix note below — the first cut wrongly
  re-exported core's 9-key helper, which made enforcement start accepting `naive`; that regression is
  fixed.)
- **`caf._argument_extensions`**: kept a `_CAF_SEMANTICS` frozenset allow-set = exactly caf's 8 keys
  (incl `naive`, **excl `ideal`**). On a key not in that set it raises the unchanged
  `ValueError(f"unsupported CAF semantics: {semantics}")`. Accepted keys delegate via
  `extensions_for(framework, cast(SemanticsName, semantics))`. caf does **not** start accepting `ideal`.
- **`partial_af._extensions_for_completion`**: kept a `_COMPLETION_SEMANTICS` frozenset = {grounded,
  preferred, stable}; raises the unchanged `ValueError(f"Unknown semantics: {semantics}")` otherwise;
  returns `list(extensions_for(completion, cast(SemanticsName, semantics)))` — **list container
  preserved**.
- **`probabilistic._extensions_for_semantics`**: kept a `_PROBABILISTIC_SEMANTICS` frozenset = {grounded,
  preferred, stable, complete}; raises the unchanged `ValueError(f"Unknown semantics: {semantics}")`
  otherwise; delegates via `extensions_for(af, cast(SemanticsName, semantics))`.

The dispatch table + single-extension wrapping now exist in exactly ONE place (`core.dung`); the four
callers keep only their own allow-set guard + error wording + return-type adaptation. `cast` is used
(not `# type: ignore`) because pyright is in `basic` mode and rejects passing the loosely-typed `str`
parameter to the `SemanticsName` Literal; the frozenset guard guarantees the cast is sound.

## STEP 4 — verification (real `uv run` output)

### pyright (the 5 edited files)
```
$ uv run python -m pyright src/argumentation/core/dung.py src/argumentation/dynamics/enforcement.py \
    src/argumentation/frameworks/caf.py src/argumentation/frameworks/partial_af.py \
    src/argumentation/probabilistic/probabilistic.py
0 errors, 0 warnings, 0 informations
```
(plus a "new pyright version available" advisory — unrelated to this change.)

### targeted per-caller tests
```
$ uv run python -m pytest tests/dynamics/test_enforcement.py tests/dynamics/test_dynamic.py \
    tests/frameworks/test_caf.py tests/frameworks/test_partial_af.py \
    tests/frameworks/test_partial_af_queries.py tests/probabilistic/test_probabilistic.py \
    tests/test_import_boundaries.py -q
....................................................................     [100%]
68 passed in 1.86s
```

### broad regression
```
$ uv run python -m pytest tests/dynamics tests/frameworks tests/probabilistic tests/core -q
... (15 progress lines) ...
1059 passed in 21.67s
```
No failures, no skips.

## Line-ending discipline

The repo is mixed and has **no `.gitattributes`** with `core.autocrlf=false`. Most files are pure CRLF,
but `core/dung.py` was **mixed at HEAD** (CRLF=628, bare-LF=37 on scattered lines). The editing tool
normalized bare-LF lines adjacent to edited hunks up to CRLF, which produced spurious EOL-only hunks
(`_normalize_relation`, `_attackers_index`, `_targets_index`, `_all_subsets`,
`_strongly_connected_components`, etc.) showing as 81 ins / 37 del. **Fixed** by rebuilding `dung.py`
from the exact HEAD bytes and surgically applying only the two real changes (the new `from typing import
Literal` line, written bare-LF to match its block; the appended helper block, written CRLF to match the
surrounding function bodies). The other four files were pure CRLF at HEAD and stayed pure CRLF (bare-LF=0
before and after) — no churn.

Final byte check (authoritative — `git diff --check` and `sed`/`xxd` are unreliable here because they
strip CR):
```
core/dung.py:        CRLF=671 bareLF=38   (was 37; +1 for the new bare-LF import line)
dynamics/enforcement.py: bareLF=0
frameworks/caf.py:       bareLF=0
frameworks/partial_af.py: bareLF=0
probabilistic/probabilistic.py: bareLF=0
```

`git diff --stat` (proportional to the logical change — net code reduction, no whole-file churn):
```
 src/argumentation/core/dung.py                   | 44 +++++++++++++++++++++++
 src/argumentation/dynamics/enforcement.py        | 44 ++---------------------
 src/argumentation/frameworks/caf.py              | 46 +++++++++++-------------
 src/argumentation/frameworks/partial_af.py       | 20 +++++------
 src/argumentation/probabilistic/probabilistic.py | 25 ++++++-------
 5 files changed, 86 insertions(+), 93 deletions(-)
```
Hunk inspection: each file shows only its import-block hunk + its dispatch-function hunk — no phantom
EOL-flip hunks.

Note on `git diff --check`: it reports "trailing whitespace" on every added CRLF line. This is a
repo-wide artifact of CRLF content under `core.autocrlf=false` with no `.gitattributes` (git reads the
file as LF and treats the `\r` as trailing whitespace); it fires identically on pre-existing CRLF lines
and is **not** introduced by this change. The reliable EOL signal is the byte check + numstat
proportionality above.

## Fix v2 — enforcement contract regression (Codex FAIL)

Codex's behavioral verification caught one regression in the first cut: enforcement's `extensions_for`
had **widened** its contract. The first cut re-exported `core.dung.extensions_for` (the 9-key union,
incl `naive`) as `enforcement.extensions_for` and re-exported core's 9-key `SemanticsName`. At the parent
(`2b02121`), enforcement's key set was the 8 classic semantics with **no `naive`**, and `naive` was
rejected:
```
parent: enforcement naive contract-check: ERR ValueError msg=unsupported semantics: naive
1st cut: enforcement naive contract-check: OK  type=tuple value=[['a'], ['b']]   # REGRESSION
```

Fix (same per-caller allow-set pattern already used by caf/partial_af/probabilistic, now applied to
enforcement too):
- enforcement keeps its OWN 8-key `SemanticsName` Literal (no `naive`) — NOT core's 9-key union. So
  `dynamic.py:14`'s `from ...enforcement import SemanticsName` still gets the original 8-key type.
- enforcement imports core's helper aliased as `_dung_extensions_for` and adds a `_SUPPORTED_SEMANTICS`
  frozenset of its 8 keys. `enforcement.extensions_for` is a guarded wrapper that raises
  `ValueError(f"unsupported semantics: {semantics}")` for any key outside the 8, else delegates to
  `_dung_extensions_for`. The dispatch table still lives only in `core.dung`; enforcement adds only a
  contract guard (not a duplicated dispatch).
- `core.dung` is unchanged (keeps its 9-key `SemanticsName` + `extensions_for`).

### enforcement behavioral proof (this fix, AF = `a -> b`)
```
$ uv run python -c "<probe over the 8 keys + naive + bogus>"
grounded     -> OK type=tuple value=[['a']]
complete     -> OK type=tuple value=[['a']]
preferred    -> OK type=tuple value=[['a']]
stable       -> OK type=tuple value=[['a']]
semi-stable  -> OK type=tuple value=[['a']]
stage        -> OK type=tuple value=[['a']]
ideal        -> OK type=tuple value=[['a']]
cf2          -> OK type=tuple value=[['a']]
naive        -> ERR ValueError: unsupported semantics: naive      # matches parent
bogus        -> ERR ValueError: unsupported semantics: bogus
enforcement.SemanticsName members = ('grounded','complete','preferred','stable',
                                     'semi-stable','stage','ideal','cf2')   # original 8, no naive
```

### re-verification of the fix
```
$ uv run python -m pyright src/argumentation/dynamics/enforcement.py src/argumentation/core/dung.py
0 errors, 0 warnings, 0 informations

$ uv run python -m pytest tests/test_import_boundaries.py tests/dynamics/test_dynamic.py -q
11 passed

$ uv run python -m pytest tests/dynamics tests/frameworks tests/probabilistic tests/core -q
1059 passed
```
`git diff --numstat` for the fix (vs the first B5 commit): `38  2  src/argumentation/dynamics/enforcement.py`
— two hunks (import block + the re-added guarded wrapper), pure CRLF (bare-LF=0), no whole-file churn.

## Commit
Two commits on `refactor/dedup`:
1. `refactor: unify semantics dispatch into core.dung.extensions_for` — the structural dedup.
2. The enforcement contract fix above. Hashes are recorded in the task hand-off (they shift on
   `--amend`, so are not hard-coded here).

## Out of scope — noticed
- The repo has no `.gitattributes`; the mixed CRLF/LF state (and `dung.py`'s in-file mix) is a latent
  trap for any tool that normalizes EOLs. A `* text=auto eol=crlf` (or an explicit per-file policy)
  would make future diffs robust. Not changed here — out of scope for this dedup.
- `caf.extensions`/`inherited_extensions`/`claim_level_extensions` still take `semantics: str` (not
  `SemanticsName`); the public CAF surface remains string-typed. Tightening it is a separate change.
- `partial_af` / `probabilistic` query entry points likewise accept `semantics: str`; only the private
  dispatch helpers were touched. The list-vs-tuple return of `_extensions_for_completion` was preserved
  conservatively even though both call sites are tuple-compatible.
