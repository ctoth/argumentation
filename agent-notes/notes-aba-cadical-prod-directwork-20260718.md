# CaDiCaL productionization — direct work state (2026-07-18, manager executing)

Context: harness-terminated workers; I am finishing exp/aba-cadical-engine-prod
by hand per its own preregistration (experiments/2026-07-18-aba-cadical-engine-prod.md).

## Facts established
- Landed on main this session: da1dce7 (census instrumentation), e0aa824
  (flat sat-core; live-proved ER_300_20_2 dc_co solves 104.19s where pre-merge
  it timed out >120s).
- Branch exp/aba-cadical-engine-prod (worktree C:\Users\Q\code\aba-cadical-prod-wt),
  commits bcafe2e/5e28406/21fe29f: routing predicate `_stable_engine_for`
  (rules>=24000 or recursive_rules>=300 -> strong engine), fallback
  `_stable_extension_with_fallback`, phase parity, 7 contracts green per worker.
- **D0 GATE FAILED**: pysat cadical195 (1.9.5) on the byte-identical c35 CNF
  (abcgen_c35_atoms35_asms30_mra3_mbs2_cp0.8_ins2: 36991v/135900c, build 0.6s)
  ran >300s vs the <=76s gate. Killed. 1.9.5 does NOT carry the 2.x win.
- Preregistered fallback is therefore ACTIVE: vendored CaDiCaL 2.2.1 batch
  DIMACS on the flat path. Existing binary from Probe 7:
  C:\Users\Q\AppData\Local\Temp\argumentation-probe7-cadical221-20260711-a62b6c3\cadical\build\cadical.exe
  (rel-2.2.1; Wave-1 measured 25.28s/9.19s on c35 CNFs with it).

## Current step
Implement the fallback dependency per prereg: strong engine = external cadical
2.2.1 batch solve (export clauses -> DIMACS -> cadical.exe -> parse v-lines ->
model), keeping pysat glucose4 for everything else and the no-row-loss fallback
intact. Then: contracts, dev slice (c35 flip <=120s, c25 no-regression, safety
gate), full ABA suite, commit, merge to main, live-proof one row.

## Blockers
- None. Binary exists in Temp (not reproducible long-term — prereg requires a
  committed build script; include scripts/build_cadical221.md|sh in the commit).

## Progress (fallback implementation, direct)
- aba_sat.py: _STABLE_ENGINE_STRONG -> "cadical221-batch"; added
  _find_cadical221_binary (env ARGUMENTATION_CADICAL221 override, else
  tools/solvers/cadical-2.2.1/cadical.exe) + _BatchDimacsCadical adapter
  (add_clause/set_phases/solve/get_model; assumption units as unit clauses;
  rc10/20 protocol; raises on anything else -> caught by no-row-loss fallback).
- Binary vendored from the Probe-7 build (2.2.1 confirmed via --version);
  tools/solvers/ gitignored; scripts/build_cadical221.sh committed for
  reproducibility (pins rel-2.2.1).
- Contract tests repointed cadical195 -> cadical221-batch: 7/7 PASS including
  oracle parity with the real binary.
- Next: dev-slice gates via shipped path (c35 asms30/asms35 flip <=120s, c25
  <=63.1s no-regression), ABA suite, pyright, commit, merge, live-proof.

## Decisions made by me (recorded for Q)
- D0 FAIL verdict by wall-clock (>300s vs 76s gate) without waiting for the
  solve to return — the gate is a time bound; exceeding it IS the result.
- Proceeding to vendored-2.2.1 fallback without asking: it is the preregistered
  fallback path, reversible, and gates decide the merge.
