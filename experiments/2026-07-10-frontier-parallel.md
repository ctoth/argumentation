# Frontier-v1 driver parallelism (--jobs)

Date: 2026-07-10. Branch: exp/frontier-parallel.

## Change

`scripts/run_frontier_v1.py` gains `--jobs N` (default `min(8, cpu-2)`,
floor 1). Rows go to a `ThreadPoolExecutor`; each row still runs in its own
subprocess via `tools.iccma_run_selected.run_selected` ->
`tools.iccma2025_run_native.run_child`, unchanged — same per-row command,
semantics, and per-subprocess wall-clock timeout kill. Futures are collected
in submit order, so the output file keeps manifest order regardless of
completion order, and the run JSON schema is unchanged (no new keys).
`--jobs 1` keeps the exact prior serial loop for contention-free timings; a
contention caveat is printed alongside the summary when jobs > 1.

The change lives entirely at the row-dispatch level of the driver because
the driver already shells out one subprocess per row; no runner flags were
needed. `tools/iccma2025_run_native.py` is untouched.

## Before / After wall-clock (30-row frontier-v1 sweep, t=120s)

- Before (serial): >= 34.0 min lower bound — the post-4b baseline had 17
  timeout rows x 120 s = 2040 s before counting any solved-row time
  (solved rows carry no elapsed field). Observed serial sweeps ran ~50 min.
- After (`--jobs 8`, label `frontier-v1-post-6a-parallel`, 32-CPU host):
  **304 s = 5.1 min** wall-clock for all 30 rows (its 12 timeout rows x
  120 s alone would cost 24 min serially). Target was <= 12 min.

## Equivalence evidence

- `tests/interop/test_frontier_v1_parallel.py`: a 4-row synthetic manifest
  (DC-CO true, DC-CO false, SE-ST, DS-PR) run at `--jobs 1` and `--jobs 2`
  produces identical per-row (status, answer), identical summaries,
  identical payload keysets, and manifest-ordered rows in both outputs.
- Real sweep (label `frontier-v1-post-6a-parallel`, `--jobs 8`, t=120):
  30/30 rows, output in manifest order, 18 solved / 12 timeout / 0 other.
  No serial `frontier-v1-post-6a` run existed at measurement time, so this
  run doubles as the post-6A scoreboard measurement. Against the post-4b
  serial baseline (last full 30-row sweep): 25/30 cells identical
  (status + answer); the 5 differing cells are all hard-class
  timeout -> solved improvements from solver work landed between 4b and
  6A (`crusti_g2io_175_0.2_511_18` DC-CO, `crusti_g2io_225_0.2_127_42`
  DC-CO, `scc_7481_39_0.4_0.1_14` DC-CO, `crusti_g2io_125_0.5_31_17`
  DS-PR, `abcgen_c25_atoms25_asms35_mra3_mbs2_cp0.8_ins1` SE-PR) — no
  solved -> timeout regressions under 8-way contention and no answer
  flips on any shared solved row.
