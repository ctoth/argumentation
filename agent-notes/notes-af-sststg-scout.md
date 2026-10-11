# Scout report: AF semi-stable/stage (SST/STG) — range-vector + CEGAR groundwork

Date: 2026-07-02. Read-only scout. Every code claim below was verified by reading
the cited source lines. Where I could not verify something, I say so explicitly.

Repo paths are all under `C:\Users\Q\code\argumentation`. Line numbers are from the
working tree at scout time (branch `exp/iccma-aba-dcco-100ba-acyc`).

---

## 1. Current SST/STG algorithm(s) and their loop/blocking structure

### Entry points (single-extension finders)
- `find_semi_stable_extension` — `src/argumentation/solving/af_sat.py:853`.
  Calls `_prepare(framework, "semi-stable", ...)` (:862), builds an `AfSatKernel`
  on the residual (:867), then `problem.add_complete_labelling()` (:868) and
  `problem.add_range_definition()` (:869), then delegates to
  `_range_maximal_extension(..., base="complete", ...)` (:870).
- `find_stage_extension` — `af_sat.py:915`. Same shape but
  `_prepare(framework, "stage", ...)` (:924), `problem.add_conflict_free()` (:930),
  `problem.add_range_definition()` (:931), `_range_maximal_extension(..., base="conflict_free", ...)` (:932).

So SST base = complete labelling; STG base = conflict-free. Confirmed at :868/:873 and :930/:935.

### The range vector encoding (`add_range_definition`, `af_sat.py:204-216`)
For each argument `a`: `range_vars[a] == Or(in_vars[a], in_vars[attacker] for attacker in attackers(a))`
(:207-215). This is **exactly** Pu 2017's `r = x + R^+(x)` (range = the set itself plus
everything it attacks). One Boolean `af_range_{i}` var per argument (:120-123). Verified 1:1.

### The core solver: `RangeMaximalTaskSolver` (`af_sat.py:1316-1456`)
Docstring: "Exact range-maximal search for stage and semi-stable tasks." (:1317).
Class constants: `shortcut_depth = 2` (:1319), `shortcut_probe_limit = 24` (:1320),
`dense_shortcut_probe_limit = 0` (:1321).

`find_extension` main loop (`af_sat.py:1336-1364`):
1. If `required_in`/`required_out` present, first run a base feasibility check
   (`_base_extension` with those constraints, :1343-1351); return `None` (unsat) early.
2. `blocked_ranges: list[frozenset[str]] = []` (:1352).
3. `while True` (:1353): get a `seed` via `_seed_extension(...)` passing
   `excluded_range_subsets=blocked_ranges` (:1354-1358). If `seed is None`, return `None` (:1360).
4. Compute `seed_range = range_of(seed, defeats)` (:1361). If `_is_range_maximal(seed_range)`
   return `seed` (:1362-1363). Otherwise append `seed_range` to `blocked_ranges` and loop (:1364).

`_seed_extension` (`af_sat.py:1366-1399`):
1. First try `_high_range_shortcut(...)` (:1373-1379); if it returns a witness, use it.
2. Otherwise binary-search the max feasible range size via `_max_range_size(...)`
   (:1381-1388), then fetch a base extension with `required_range_size=max_range_size`
   (`_base_extension`, :1391-1399).

`_high_range_shortcut` (`af_sat.py:1401-1432`): iterates `_bounded_missing_sets(arguments,
depth=self.shortcut_depth, limit=probe_limit)` (:1411-1415); for each `missing` set builds
`required_range = all_args - missing` (:1416) and asks for a base extension whose range
contains `required_range` (:1418-1426). Returns the first witness found, or `None` after
`probe_limit` probes. `_shortcut_probe_limit` (:1434-1440) drops the probe limit to
`dense_shortcut_probe_limit` (= 0, i.e. shortcut disabled) when `len(arguments) >= 160` and
`len(defeats) >= 8*len(arguments)` (dense large graphs) — otherwise 24.

`_bounded_missing_sets` (`af_sat.py:1492-1508`): BFS over subsets of size `<= depth` (2),
yields the empty set first (full-range probe) then singletons then pairs, capped at `limit`.

`_max_range_size` (`af_sat.py:1459-1489`): **monotone binary search** on range size using
`required_range_size_at_least=midpoint` (:1479); classic low/high bisection (:1468-1489).

`_is_range_maximal` (`af_sat.py:1445-1456`): `outside = all_args - range_set`; if empty,
return True (full range) (:1446-1448). Otherwise ask for a base extension with
`required_range=range_set` AND `require_any_range=outside` (:1449-1455) — i.e. "does a base
extension with strictly larger range exist?". Returns True iff that is UNSAT.
**Verified subtlety:** this test threads NO `required_in`/`required_out`, so range-maximality
is checked against ALL base extensions of the framework, not query-constrained ones. This is
semantically correct: SST/STG range-maximality is a global property of the extension, so a
query-excluding seed that is globally range-maximal is a genuine SST/STG extension.

### Blocking clause
`blocked_ranges` are enforced by `exclude_range_subset` (`af_sat.py:300-307`): for a blocked
range `R`, it requires `require_any_range(all_args - R)` (:303-305) — i.e. the next seed's
range must contain at least one argument outside `R`, so its range is NOT a subset of `R`.
This is the range-subset learned/blocking clause. Threaded through `_run_extension` at :986-987.

### Z3 usage: push/pop, NOT assumption literals
`AfSatKernel` holds ONE persistent `self.solver = self.z3.Solver()` (`af_sat.py:110`). The base
labelling and range definition are added ONCE via `solver.add(...)`. Per-call constraints
(require_in/out/range, size bounds, exclusions) are applied inside a `solver.push()` /
`solver.pop()` bracket in `_run_extension` (:969-998), `_admissible_extension` (:1044-1057),
`_admissible_attacker_of_set` (:1068-1075). `AfSatKernel.check` accepts an `assumptions`
tuple (:312) and calls `self.solver.check(*assumptions)` (:320), but every range-maximal call
site passes NO assumptions (e.g. `_run_extension` calls `problem.check(utility_name, ...)` with
no `assumptions=` at :988-994). **So the incremental strategy is Z3 push/pop, not
assumption-literal-based.** This directly answers the open question in
`papers/Pu_2017.../notes.md:99` ("CryptoMiniSat assumptions vs Z3 push/pop"): the code chose
push/pop.

### Acceptance dispatch (DC-/DS-)
`solve_dung_acceptance` (`solver.py:388`) → `_auto_dung_acceptance_backend` routes
semi-stable and stage to `sat` (`solver.py:525`). `semantics == "semi-stable"` →
`_solve_sat_semi_stable_acceptance` (`solver.py:465-475`, body :957-972);
`semantics == "stage"` → `_solve_sat_stage_acceptance` (:476-486, body :975-990). Both call
the shared `_solve_sat_acceptance(find_*_extension, ...)` (:821-855):
- **credulous (DC)**: `find_extension(framework, require_in=query)`; answer = witness is not None (:833-843).
- **skeptical (DS)**: `find_extension(framework, require_out=query)`; answer = counterexample is None (:844-854).

So DC-SST/DC-STG = one range-maximal extension containing the query; DS-SST/DS-STG = one
range-maximal extension excluding the query (a counterexample). Both are single calls into
`RangeMaximalTaskSolver` with `required_in`/`required_out` set by `_prepare`.

### Single-extension dispatch (SE-)
`solve_dung_single_extension` (`solver.py:342`) with `backend="sat"` looks up
`_SAT_SINGLE_EXTENSION_FINDERS[semantics]` (:365) and calls the finder with no
require_in/out (:368-374). `_auto_dung_single_backend` routes semi-stable and stage to `sat`
(`solver.py:517`). SE-SST/SE-STG therefore return the first range-maximal extension found.

---

## 2. Gap analysis vs Pu 2017 (range-vector + maximal-range-then-enumerate)

**Maps 1:1:**
- Range vector `r = x + R^+(x)` ↔ `add_range_definition` (verified above).
- "Find a maximal range, fix it" ↔ `_max_range_size` binary search + `required_range_size`
  exact seed. Pu describes finding a maximal range then enumerating under it (notes.md:64,91).
- Base = admissible/complete for semi-stable, conflict-free for stage ↔ our SST=complete,
  STG=conflict-free (notes.md:61-62).

**What our encoding/loop lacks vs Pu:**
- Pu's second stage **enumerates ALL extensions under the fixed maximal range** before
  clearing assumption space and searching another range (notes.md:64,91). We do NOT enumerate;
  we return the first witness under a maximal range because the task is single-witness /
  acceptance, not extension enumeration. For DS/DC/SE this is sufficient; for a future
  EE-SST/EE-STG (enumerate-all) task it is not implemented.
- Pu clears assumption space then adds **hard blocking clauses against subsets of the found
  maximal solution** (notes.md:63). We block by requiring a strictly larger range
  (`exclude_range_subset`) under push/pop instead of persistent hard clauses.
- Pu uses CryptoMiniSat assumption literals; we use Z3 push/pop (see §1). The
  assumption-vs-push/pop tradeoff (notes.md:99) is unexplored empirically in-repo — I did not
  find any benchmark comparing the two.

---

## 3. Gap analysis vs Dvorak 2014 CEGAR (second-level tasks)

Dvorak's generic SAT/CEGAR (notes.md:60-61, formulas at notes.md:76-114):
`phi = phi_BASE-SEM(sigma) AND q AND SHORTCUTS_sigma`, iterate: find candidate `I`, strengthen
via `psi_sigma^I` (a base extension with strictly larger RANGE for sem/stg; strictly larger SET
for prf), accept if UNSAT else learn `gamma_sigma^I` (exclude ranges contained in current
range). `BASE-SEM(sem)=com`, `BASE-SEM(stg)=cf`, shortcut depth `d=2` (notes.md:154).

**What maps:**
- `BASE-SEM(sem)=com` / `BASE-SEM(stg)=cf` ↔ our SST=complete, STG=conflict-free (exact match).
- `psi_sigma^I` (strictly-larger-range test) ↔ `_is_range_maximal` (:1449-1455).
- `gamma_sigma^I` (exclude subranges) ↔ `exclude_range_subset` (:300-307).
- Dvorak's bounded-`d=2` range shortcut (SHORTCUTS_sigma) ↔ our `_high_range_shortcut` with
  `shortcut_depth = 2` (:1319, :1411). Same depth constant.

**What we lack vs Dvorak:**
- **No complexity-sensitive fragment detection / dispatch.** Dvorak's whole point is detecting
  lower-complexity fragments (acyclic, coherent, stable-consistent, unique-preferred, bounded-k)
  and dropping to a first-level oracle (notes.md:150-171). Our SST/STG path runs the same
  range-maximal loop regardless of instance structure. I found no fragment detection in the
  range-maximal path (grep for `scc|component|strongly_connected|topolog` in `af_sat.py`
  returned NO matches).
- **No stable-first shortcut.** If a stable extension exists, every semi-stable extension IS
  stable (and for coherent AFs preferred=stable) — a single stable SAT call would decide many
  rows. `find_stable_extension` exists (`af_sat.py`, exported at :1659) but is NOT invoked from
  the SST/STG path. (The DS-PR notes at `notes/ds-pr-timeouts-2026-05-02.md:8,13` flag the same
  missing stable shortcut for preferred.)
- **No SCC / grounded-reduct-driven decomposition inside the loop.** SCC decomposition exists in
  `core/dung.py` per `notes/ds-pr-timeouts-2026-05-02.md:7` but is not wired into the SST/STG
  solver (confirmed: no SCC symbols in `af_sat.py`). Only the up-front grounded reduct in
  `_prepare` applies, and only for SST (see §4).
- Query threading: Dvorak threads `q` into every oracle call. We thread require_in/out into the
  **seed** search and base feasibility, but deliberately NOT into `_is_range_maximal` (correct,
  see §1). We do not implement Dvorak's early-accept skeptical shortcut that stops as soon as a
  base candidate with the excluded query and any attacker configuration is found — our loop
  always drives to a globally range-maximal seed.

---

## 4. Preprocessing applicability (grounded reduct / SCC), verified

Source: `src/argumentation/core/preprocessing.py`.

- `GROUNDED_REDUCT_SEMANTICS` (:69-79) = `{complete, preferred, stable, semi-stable, grounded,
  ideal}`. **Includes `semi-stable`; EXCLUDES `stage`** (verified by reading the frozenset
  members :70-76 and the absence of "stage").
- `simplify_af` (:121-153): `apply_grounded = semantics is None or semantics in
  GROUNDED_REDUCT_SEMANTICS` (:133). When true it fixes the grounded extension IN and
  grounded-attacked arguments OUT (:138-142). When false, only the always-sound pure self-loop
  sink removal runs (docstring :128-131).
- **Stage is deliberately excluded, with a documented counterexample** (quoted verbatim from
  `preprocessing.py:83-88`):
  > NOTE: ``stage`` is deliberately absent. Stage extensions are conflict-free
  > [not complete] ... neither contain the grounded extension nor exclude the
  > grounded-attacked arguments. Concrete counterexample: AF = ({a,b,c}, {(a,a),(b,c),(c,a)})
  > has grounded {b}, but {c} is a stage extension (range {a,c}, incomparable to range {b,c}
  > of {b}). Applying the grounded reduct would wrongly force c OUT.
  The module docstring repeats this at :47-50. There is a regression fixture for it in
  `tests/core/test_preprocessing.py:60` (`# stage breaks naive grounded reduct`).
- Net: **SST gets the grounded reduct; STG gets only self-loop-sink removal.** SCC decomposition
  is applied to neither in the SST/STG SAT path (not wired — see §3).

---

## 5. Tests covering SST/STG

Primary: `tests/solving/test_solver_encoding.py`
- `test_kernel_range_maximal_extensions_handle_basic_witnesses` (:296) — basic SST/STG witnesses
  incl. require_in/require_out.
- Trace-structure tests: `test_kernel_range_maximal_search_traces_range_checks` (:306),
  `test_stage_search_uses_cardinality_max_range_on_iccma_slow_row` (:397),
  `test_stage_full_range_shortcut_runs_before_cardinality_search` (:434),
  `test_semi_stable_full_range_shortcut_runs_before_cardinality_search` (:445),
  `test_stage_high_range_shortcut_runs_before_cardinality_search` (:456). These assert the
  utility-name ordering (`*_full_range_shortcut`, `*_high_range_shortcut`,
  `*_max_range_at_least`, `*_max_range_exact`, `*_range_maximality`, `*_base_feasibility`) — a
  coder changing the loop MUST keep these telemetry labels or update these tests.
- Differential vs native oracle: `test_kernel_semi_stable_extension_returns_native_witness`
  (:827), `test_kernel_semi_stable_required_labels_match_native_oracle` (:837),
  `test_kernel_stage_extension_returns_native_witness` (:864),
  `test_kernel_stage_required_labels_match_native_oracle` (:874). These are the correctness
  guardrails — any encoding/loop change must keep them green.

Preprocessing: `tests/core/test_preprocessing.py` — stage-excluded-from-grounded-reduct fixture
(:60) plus semantics-parametrized reduct-correctness tests (:114, :122).

Interop / benchmark harness: `tests/interop/test_iccma_range_trace_compare.py`,
`tests/interop/test_iccma_run_timeout_rows.py`, `tests/interop/test_iccma_run_selected.py`.

**pytest selectors a coder would use** (PowerShell, repo root, `uv run`):
```
uv run pytest -q tests/solving/test_solver_encoding.py
uv run pytest -q tests/core/test_preprocessing.py
uv run pytest -q tests/solving/test_solver_encoding.py -k "semi_stable or stage or range_maximal"
uv run pytest -q tests/interop/test_iccma_range_trace_compare.py
```
(The Phase-4 note `workstreams/cap200-solver-frontier.md:160` uses
`uv run pytest -q tests\test_solver_encoding.py tests\test_dung.py` — those top-level paths do
not exist in the current tree; the real paths are `tests/solving/test_solver_encoding.py` and
`tests/core/test_dung.py`. Note this stale path if you copy that command.)

---

## 6. Benchmark command for SST/STG-only rows

Tool: `tools/iccma2025_run_native.py` (argparse read at :99-198). **There is NO
`--semantics`/`--task`/`--problem` flag.** Filtering is by subtrack/instance:
- `--only-subtrack <SUBTRACK>` (repeatable, :162-167) filters `task["subtrack"]` (:247).
- `--only-instance <relative_path>` (repeatable, :156-161).
- Other relevant flags: `--backend {auto,native,iccma,100ba-acyc}` (:106-110, default auto),
  `--timeout-seconds` (default 5.0, :126), `--max-af-arguments` (default 100, :124),
  `--event-log-path`, `--profile-workers-dir` (py-spy), `--root` (default `DATA_ROOT`).

Subtrack strings are the ICCMA problem codes (`PROBLEM_TO_SEMANTICS`, :30-38; `SST→semi-stable`,
`STG→stage`). `DEFAULT_AF_SUBTRACKS` (:40-54) contains `DC-SST`, `DS-SST`, `SE-SST` **but NOT
any `-STG` subtrack.** STG codes are supported by `split_subtrack` (:1223-1224) and the
problem map, but a subtrack only runs if the data `--root` actually has a matching `.results`
directory (`infer_af_subtracks` :300-308, gated by `supported_runner_subtrack` :312). So:

SST-only run (works against the standard data root):
```
uv run tools\iccma2025_run_native.py --only-subtrack DC-SST --only-subtrack DS-SST --only-subtrack SE-SST --backend auto --timeout-seconds 15
```
STG-only run — same shape with `SE-STG`/`DC-STG`/`DS-STG`, but **only if the data root exposes
those subtracks**; I did not verify that the ICCMA 2025 data root under `DATA_ROOT` contains STG
result dirs, so a coder must confirm before relying on it.

Alternative used by the frontier plan: `tools\iccma_run_timeout_rows.py --timeouts
tests\manifests\iccma2025-cap200-timeouts.json --timeout-seconds 15 --backend auto --output
...` (`workstreams/cap200-solver-frontier.md:161`) — replays a fixed timeout manifest rather
than filtering by semantics. The manifest `tests/manifests/iccma2025-cap200-timeouts.json`
exists (it showed in the tests grep). I did not open it to confirm which SST/STG rows it lists.

**I did not run any benchmark** (Bash is warded and the task is read-only).

---

## 7. Risks / open questions for a coder

1. **Telemetry-coupled tests.** The trace-ordering tests in `test_solver_encoding.py`
   (:306-518) assert exact `utility_name` strings and their order. Any loop restructuring
   (e.g. adding a stable-first shortcut or reordering shortcut vs binary search) will break
   these even when the answer is still correct. Plan to update them deliberately, and keep the
   differential-vs-native tests (:827-889) as the real correctness gate.
2. **Stage cannot use the grounded reduct** (§4, documented counterexample). Any speedup for STG
   must come from something OTHER than grounded/complete-based reduction — e.g. self-loop sink
   removal (already applied), SCC decomposition on conflict-free structure, or a cf-specific
   fragment. Do not "fix" STG by adding it to `GROUNDED_REDUCT_SEMANTICS` — there is a regression
   fixture (`test_preprocessing.py:60`) and a proof-by-counterexample against it.
3. **Dense-graph shortcut disabling.** `_shortcut_probe_limit` returns 0 (shortcut off) for
   `>=160` args and `>=8x` density (:1434-1440). The worst ICCMA families cited in the mission
   (ER_300, crusti) are large/dense, so they likely fall into the shortcut-disabled regime and
   go straight to binary search — verify with `--event-log-path` traces before assuming the
   shortcut helps them. (I did not profile these instances.)
4. **Z3 push/pop vs assumptions is unmeasured** (§1-2). If a coder wants Pu's assumption-literal
   style, that is a real rewrite of the check machinery (`_run_extension`), not a local tweak,
   and Z3's assumption API differs from CryptoMiniSat's. No in-repo benchmark justifies switching.
5. **No fragment/complexity dispatch** (§3). The highest-leverage Dvorak-style win — stable-first
   shortcut and coherent/acyclic detection — is entirely unimplemented for SST/STG. `find_stable_extension`
   and acyclicity helpers (`_is_acyclic`, `af_sat.py:1636`) already exist to build on.
6. **STG subtrack availability in the data root is unconfirmed** (§6). Confirm the data root has
   STG result dirs before designing a STG-only benchmark loop; the default subtrack list omits STG.
7. **Stale command paths** in `cap200-solver-frontier.md:160` (`tests\test_solver_encoding.py`,
   `tests\test_dung.py`) no longer match the tree (now under `tests/solving/` and `tests/core/`).

### Things I could not determine
- Which specific SST/STG instances time out (ER_300/crusti named in the mission were not
  individually profiled — I ran nothing).
- Contents of `tests/manifests/iccma2025-cap200-timeouts.json` (not opened).
- Whether `DATA_ROOT` currently contains STG `.results` subtrack directories.
