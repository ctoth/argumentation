# Dialectical Chess Experiment Matrix

## Goal

Make the Lichess puzzle baseline comparable across selector and evidence
settings, using the same fixed sample and a reproducible command.

## Matrix

Preset: `core`.

Cases:

- `argument_d0`
- `argument_d1`
- `argument_d2`
- `score_static`
- `support_d1`
- `support_d2`
- `categoriser_d1`
- `categoriser_d2`
- `grounded_d1`
- `grounded_d2`
- `argument_d2_no_positional`
- `argument_d2_no_smt`
- `argument_d2_search1`

Fixed inputs:

- Official Lichess puzzle CSV: `scratch\lichess_db_puzzle.csv`
- Rating window: `1200-1600`
- Limit: `100`
- Scoring target: first engine move only
- Reply analysis defaults:
  - `max_replies=128`
  - `max_defense_nodes=5000`
  - `min_defense_material=300`

Command:

```powershell
uv run --with chess --with z3-solver .\scripts\dialectical_chess_bench.py `
  --experiment-matrix `
  --lichess-puzzles .\scratch\lichess_db_puzzle.csv `
  --rating-min 1200 `
  --rating-max 1600 `
  --limit 100 `
  --matrix-preset core `
  --progress-every 25 `
  --json-out .\scratch\lichess_1200_1600_matrix_core_100.json
```

Timeout chosen before launch: `300s`.

Result artifact:

- `scratch\lichess_1200_1600_matrix_core_100.json`

## Sample Composition

No, this sample was not restricted to solve-in-two puzzles.

The runner filtered by rating only. It did not require `mateIn2`, `short`, a
particular line length, or any theme. It scored only the first expected engine
move from the Lichess `Moves` field.

Line move counts in the selected sample:

- `2`: 9
- `4`: 63
- `6`: 26
- `8`: 2

Mate theme counts in the selected sample:

- `mateIn1`: 9
- `mateIn2`: 10
- `mateIn3`: 3

Other high-count themes:

- `endgame`: 48
- `middlegame`: 44
- `advantage`: 40
- `crushing`: 37
- `long`: 26
- `master`: 18
- `fork`: 14

## Results

Sorted by solved count:

| Case | Solved | Hit Rate | Elapsed ms |
| --- | ---: | ---: | ---: |
| `argument_d2_no_positional` | 21/100 | 0.21 | 8105.14 |
| `grounded_d2` | 19/100 | 0.19 | 8826.61 |
| `argument_d2_search1` | 18/100 | 0.18 | 11335.15 |
| `argument_d1` | 17/100 | 0.17 | 8249.95 |
| `argument_d2` | 17/100 | 0.17 | 8752.84 |
| `categoriser_d2` | 17/100 | 0.17 | 8707.79 |
| `grounded_d1` | 17/100 | 0.17 | 8327.92 |
| `argument_d2_no_smt` | 17/100 | 0.17 | 7422.86 |
| `categoriser_d1` | 16/100 | 0.16 | 8498.88 |
| `support_d1` | 15/100 | 0.15 | 8312.59 |
| `argument_d0` | 14/100 | 0.14 | 3902.50 |
| `score_static` | 13/100 | 0.13 | 3755.37 |
| `support_d2` | 13/100 | 0.13 | 8886.57 |

## Notes

- The `17%` argument-depth-2 result reproduces inside the matrix.
- Static score alone gets `13%`, so the argument stack is currently buying about
  four points on this fixed slice.
- Disabling positional reasons improves this slice to `21%`, which means the
  current positional reasons are noisy for puzzle solving. They may still be
  useful for game play, but they need gating or tactical deference.
- Disabling SMT mate does not change this slice: `17%` either way. On this
  sample, SMT mate plumbing is not moving the first-move selection result.
- One ply of alpha-beta search improves the depth-2 argument case from `17%` to
  `18%` at a runtime cost. That is a small gain, not yet a compelling search
  story.
- `grounded_d2` reaches `19%`, which suggests the grounded extension is worth a
  closer look as a selector, especially once positional reason noise is reduced.

## Verification

Targeted test command:

```powershell
uv run --with chess --with z3-solver pytest .\tests\test_dialectical_chess_evidence_ablation.py -q
```

Result:

- `19 passed`
