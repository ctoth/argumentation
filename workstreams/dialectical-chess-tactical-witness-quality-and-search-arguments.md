# Dialectical Chess Tactical Witness Quality And Search Arguments

## Status

Status: executed.

Branch: `main`.

## Goal

Improve the next tactical layer after positional gating:

- make SMT fork witnesses stable, typed, and less noisy;
- expose search results as structured arguments and objections instead of only
  scalar score adjustments;
- ablate whether fork witnesses, search arguments, or their combination beat the
  current fixed-slice baseline.

Input baseline from the positional gating workstream:

| Case | Solved |
| --- | ---: |
| `argument_d2_search1` | 23/100 |
| `argument_d2` | 22/100 |
| `optimizer_d2` | 21/100 |

Working hypothesis:

- The next gain is tactical evidence quality, not more positional weighting.
- Fork witnesses need quality metadata, because a bare `smt:fork:2:500` cannot
  distinguish a forcing fork from a cosmetic or losing fork.
- Search should produce named refutation/support artifacts so argumentation can
  attack and defend search claims instead of swallowing one scalar.

## Non-Negotiables

- Work on `main`.
- Do not create worktrees.
- Use `uv run ...` for every Python command.
- Commit each intentional source, test, or workstream edit atomically with
  explicit path-limited git commands.
- Keep generated diagnostics under `scratch/` uncommitted unless explicitly
  promoted.
- Add progress reporting to any newly created long-running runner.
- Do not remove SMT fork witnesses wholesale; make them typed and ablatable.
- Do not replace argumentation with search. Search must feed arguments or
  objections.

## Owned Paths

Likely source paths:

- `scripts/dialectical_chess/smt.py`
- `scripts/dialectical_chess/search.py`
- `scripts/dialectical_chess/probe.py`
- `scripts/dialectical_chess/arguments.py`
- `scripts/dialectical_chess/optimizer.py`
- `scripts/dialectical_chess/engine.py`
- `scripts/dialectical_chess/bench.py`
- `scripts/dialectical_chess/uci.py`

Likely tests:

- `tests/test_dialectical_chess_evidence_ablation.py`
- `tests/test_dialectical_chess_engine_api.py`

Likely generated diagnostics:

- `scratch\tactical_witness_delta_*.json`
- `scratch\tactical_witness_delta_*.md`
- `scratch\lichess_1200_1600_matrix_core_100_tactical_witness.json`

## Phase 0: Confirm Baseline

Commands:

```powershell
git branch --show-current
git status --short -- .\scripts .\tests .\workstreams .\scratch .\reports
Test-Path .\scratch\lichess_db_puzzle.csv
Test-Path .\scratch\lichess_1200_1600_matrix_core_100_positional_gated.json
```

Acceptance criteria:

- Current branch is `main`.
- No tracked task-owned files are dirty.
- Fixed Lichess puzzle CSV exists.
- Latest fixed matrix exists, or this workstream reruns it before comparing.

## Phase 1: Add Tactical Witness Controls

Goal: make fork/search evidence ablatable.

Implementation:

- Add `smt_fork` to engine/probe/bench/UCI settings.
- Add CLI flags:
  - benchmark: `--no-smt-fork`;
  - probe: `--no-smt-fork`;
  - UCI/probe engine settings must carry it through.
- Extend settings payloads to report `smt_fork`.
- Add matrix rows:
  - `argument_d2_no_fork`;
  - `argument_d2_search1_no_fork`;
  - `optimizer_d2_no_fork`.

Tests:

- settings serialization includes `smt_fork`;
- disabling fork removes fork witnesses from probes;
- benchmark settings report `smt_fork`;
- matrix includes the new no-fork rows.

Acceptance criteria:

- Focused tests fail before implementation and pass after.
- Existing `--no-smt-mate` behavior is unchanged.

## Phase 2: Mine Fork/Search Deltas

Goal: identify exact puzzles where fork witnesses or search arguments change
decisions.

Implementation:

- Add a reusable diagnostic mode or script that compares:
  - fork on vs fork off;
  - search depth 0 vs search depth 1;
  - fork on + search depth 1 vs fork off + search depth 1.
- Emit per changed decision:
  - puzzle id;
  - FEN;
  - expected first move;
  - selected moves;
  - selected move reasons;
  - selected move objections;
  - reply attacks;
  - search line and score;
  - fork witness labels.
- Progress every 10 puzzles.

Acceptance criteria:

- Generated diagnostics identify:
  - fork-only successes;
  - fork-only failures;
  - search-only successes;
  - search-only failures;
  - fork/search interaction deltas.
- At least three concrete regression candidates are extracted unless fewer
  exist in the fixed slice.

## Phase 3: Write Failing Tests First

Goal: encode mined tactical-witness failures.

Required tests:

- Fork witness labels include typed quality:
  - target count;
  - target value;
  - moved piece;
  - whether the forking piece is immediately capturable;
  - whether the move gives check.
- Bad fork witnesses cannot outrank a stronger concrete capture or promotion in
  tactical contexts.
- Search results produce structured reasons/objections:
  - positive search support;
  - negative search refutation;
  - search line visible in trace.
- Disabling fork evidence changes only fork-derived labels, not mate/search
  labels.

Acceptance criteria:

- Tests fail for the intended reason before implementation.
- Tests use mined puzzle ids where available.

## Phase 4: Implement Fork Witness Quality

Goal: replace bare fork evidence with richer tactical evidence.

Target labels:

- keep compatibility label: `smt:fork:2:500`;
- add typed labels such as:
  - `smt:fork:targets:<count>:value:<value>`;
  - `smt:fork:piece:<piece>`;
  - `smt:fork:gives_check`;
  - `smt:fork:moved_piece_en_pris:<value>`;
  - `smt:fork:net:<value>`.

Selection semantics:

- positive fork support should use effective/net value where possible;
- a fork whose moved piece is immediately capturable should be lower priority
  unless it gives check or wins enough material;
- bare fork count should not outrank concrete material or promotion.

Acceptance criteria:

- Fork quality tests pass.
- Existing fork witness tests pass.
- Matrix rows can ablate fork on/off.

## Phase 5: Implement Search Arguments

Goal: make shallow search legible to argumentation.

Target labels:

- positive:
  - `search:<backend>:<score>` remains for compatibility;
  - `search_support:<backend>:<score>`;
  - `search_line:<move1>-<move2>-...`.
- negative:
  - `search_refutes:<backend>:<score>`;
  - `search_line:<move1>-<move2>-...`.

Argument behavior:

- positive search support is tactical support;
- negative search refutation is an objection;
- search line remains visible in benchmark payloads and UCI output.

Acceptance criteria:

- Search argument tests pass.
- `argument_d2_search1` remains available and interpretable.

## Phase 6: Benchmark And Ablate

Focused tests:

```powershell
uv run --with chess --with z3-solver pytest .\tests\test_dialectical_chess_evidence_ablation.py .\tests\test_dialectical_chess_engine_api.py .\tests\test_dialectical_chess_cleanup.py .\tests\test_dialectical_chess_loss_mining.py -q
```

Fixed matrix:

```powershell
uv run --with chess --with z3-solver .\scripts\dialectical_chess_bench.py --experiment-matrix --lichess-puzzles .\scratch\lichess_db_puzzle.csv --rating-min 1200 --rating-max 1600 --limit 100 --matrix-preset core --progress-every 25 --json-out .\scratch\lichess_1200_1600_matrix_core_100_tactical_witness.json 1>$null
```

Timeout:

- start with `300s`, based on the prior measured fixed matrix runtime.
- actual rerun budget used here was `360s`, because the core matrix expanded
  from 18 rows to 21 rows after adding no-fork ablations.

Acceptance criteria:

- Record whether any row beats `argument_d2_search1` at `23/100`.
- Record whether no-fork rows improve or hurt.
- Record whether search arguments improve trace quality even if not raw score.
- If no row improves, identify the exact bottleneck and next workstream.

## Phase 7: Record Results

Update this workstream with:

- commands run;
- generated diagnostics;
- focused test results;
- fixed matrix results;
- interpretation;
- recommendation.

Completion definition:

- fork controls implemented and tested;
- fork/search deltas mined;
- fork witness quality implemented and tested;
- search arguments implemented and tested;
- fixed matrix rerun recorded;
- every intentional edit committed;
- generated diagnostics left uncommitted.

## Execution Results

Workflow actually used: this workstream, executed on `main` without worktrees.

Commits produced:

- `c6c6fb1 Add tactical witness chess workstream`
- `5708495 Add failing SMT fork control tests`
- `442e44e Add SMT fork engine controls`
- `91cd804 Add failing tactical witness diagnostic test`
- `64d7513 Add tactical witness comparison benchmark`
- `6266829 Add tactical witness summary script`
- `ba63782 Add failing tactical quality tests`
- `f186edb Qualify fork and search chess evidence`

Focused verification:

```powershell
uv run --with chess --with z3-solver pytest .\tests\test_dialectical_chess_engine_api.py .\tests\test_dialectical_chess_evidence_ablation.py .\tests\test_dialectical_chess_cleanup.py .\tests\test_dialectical_chess_loss_mining.py -q
```

Result: `48 passed in 2.79s`.

Tactical witness diagnostic:

```powershell
uv run --with chess --with z3-solver .\scripts\dialectical_chess_bench.py --compare-tactical-witness --lichess-puzzles .\scratch\lichess_db_puzzle.csv --rating-min 1200 --rating-max 1600 --limit 100 --selector-mode argument --dialectic-depth 2 --progress-every 10 --json-out .\scratch\tactical_witness_delta_argument_d2_qualified.json 1>$null
uv run .\scripts\dialectical_chess_tactical_witness_summary.py .\scratch\tactical_witness_delta_argument_d2_qualified.json --markdown-out .\scratch\tactical_witness_delta_argument_d2_qualified.md
```

Variant totals:

| Variant | Solved |
| --- | ---: |
| `fork_on` | 24/100 |
| `fork_off` | 22/100 |
| `search1` | 26/100 |
| `search1_no_fork` | 26/100 |

Delta totals:

| Pair | Changed | Left-only success | Right-only success |
| --- | ---: | ---: | ---: |
| `fork_on_vs_fork_off` | 22 | 5 | 3 |
| `fork_on_vs_search1` | 19 | 2 | 4 |
| `search1_vs_search1_no_fork` | 20 | 4 | 4 |
| `fork_off_vs_search1_no_fork` | 19 | 1 | 5 |

Fixed matrix:

```powershell
uv run --with chess --with z3-solver .\scripts\dialectical_chess_bench.py --experiment-matrix --lichess-puzzles .\scratch\lichess_db_puzzle.csv --rating-min 1200 --rating-max 1600 --limit 100 --matrix-preset core --progress-every 25 --json-out .\scratch\lichess_1200_1600_matrix_core_100_tactical_witness.json 1>$null
uv run .\scripts\dialectical_chess_matrix_summary.py .\scratch\lichess_1200_1600_matrix_core_100_tactical_witness.json --markdown-out .\scratch\lichess_1200_1600_matrix_core_100_tactical_witness.md
```

Runtime: `286884.619 ms`.

Top fixed-matrix rows:

| Case | Solved | Elapsed ms |
| --- | ---: | ---: |
| `argument_d2_search1_no_fork` | 26/100 | 14082.93 |
| `argument_d2_search1` | 26/100 | 17398.90 |
| `argument_d2_no_smt` | 24/100 | 11794.14 |
| `argument_d2` | 24/100 | 12725.21 |
| `argument_d2_no_positional` | 23/100 | 10870.14 |
| `grounded_d2` | 23/100 | 12381.17 |
| `argument_d2_no_fork` | 22/100 | 12134.62 |
| `argument_mate_theme_depth` | 22/100 | 14693.56 |
| `optimizer_d2_no_fork` | 22/100 | 19433.79 |

Sample shape:

- total puzzles: `100`
- line move counts: `{'2': 9, '4': 63, '6': 26, '8': 2}`
- mate theme counts: `{'mateIn1': 9, 'mateIn2': 10, 'mateIn3': 3}`

## Interpretation

The baseline moved from `23/100` to `26/100` on the same fixed
1200-1600 Lichess slice. That is a real kept gain for this slice.

Fork witness quality helped the non-search argument engine: `argument_d2`
increased from `22/100` in the positional-gating baseline to `24/100`.
The no-fork ablation solved `22/100`, so the qualified SMT fork witness is now
net-positive in static argument selection.

Search arguments helped more than fork quality alone: both
`argument_d2_search1` and `argument_d2_search1_no_fork` solved `26/100`.
The no-fork search row was faster on this run, so shallow search support is
currently carrying the top-line improvement more cleanly than fork witnesses in
the searched setting.

The optimizer path did not benefit in this slice: `optimizer_d2` solved
`20/100`, and `optimizer_d2_no_fork` solved `22/100`. The tactical argument
selector remains the stronger path for this benchmark.

## Recommendation

Keep the qualified SMT fork witness, because it improves the non-search
argument engine and gives useful typed traces. For the next strength workstream,
prioritize search-as-arguments over more scalar optimization:

- mine the `search1`/`search1_no_fork` tie cases where different moves have the
  same shallow score;
- turn principal variation evidence into attackable claims about threats,
  recaptures, and forced replies instead of one `search_support` label;
- use the changed-decision records as regression tests before changing
  selection semantics again.
