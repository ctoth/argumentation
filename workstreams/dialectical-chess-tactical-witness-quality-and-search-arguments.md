# Dialectical Chess Tactical Witness Quality And Search Arguments

## Status

Status: proposed.

Branch: `main`.

## Goal

Improve the next tactical layer after positional gating:

- make SMT fork witnesses stable, typed, and less noisy;
- expose search results as structured arguments and objections instead of only
  scalar score adjustments;
- ablate whether fork witnesses, search arguments, or their combination beat the
  current fixed-slice baseline.

Current relevant baseline from the positional gating workstream:

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
