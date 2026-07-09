# Coder report: exp 5 — arc-acyclic foundedness for the sparse-narrow stable solver

Branch `exp/abcgen-arc-acyc` (isolated worktree agent-a2a16e2a1e9526e8b), base
2d11b94 (CI-green tip; local `main` ref was stale at 5dd6a03 — 2d11b94 taken
from local `exp/ci-green`, no fetch needed). Commits:

- `b446dfb` — derivation (committed BEFORE implementation, per mandate)
- `08e19cd` — iteration 1: arc-justification encoding + lazy edge-cycle CEGAR
- `9ca0b56` — iteration 2: eager blocking of ALL static intra-SCC cycles
- final commit — scripts (`scripts/profile_abcgen_stable.py`,
  `scripts/run_abcgen_arc_acyc_cells.sh`), experiment-doc
  Interpretation/Decision, this report

Experiment record: `experiments/2026-07-09-abcgen-arc-acyc.md` (Hypothesis /
Derivation / Single Variable / Fast Contracts / Metric Gate / Interpretation /
Decision).

## 1. Verified anatomy deltas vs the scout

1. **`aba_acyc_sat.py` is NOT on main.** The reuse-inventory module exists only
   on branch `exp/iccma-aba-dcco-100ba-acyc` (commits f010c8c/9019603/20506d2),
   which has DIVERGED from main. I read it via `git show 58b13df:...` and
   ported the mechanism (shape builder, edge/rule-justified clause families,
   cycle detection), re-derived for the stable completion encoding.
2. `aba_sat.py` symbol lines on 2d11b94 all match the scout's citations
   (`_NativeSparseNarrowStableSolver`:703, `_add_completion_clauses`:767,
   `stable_extension`:804, `_loop_formula_for`:905, routing entry :133-166).
3. **ROUTING PREMISE PARTLY FALSE on current main.** The mandate said all 3
   abcgen instances route to the stable-first sparse-narrow solver. Verified
   reality (`solving/solver.py:487 _auto_aba_backend_for_framework`):
   - SE-PR (preferred, single-extension): sparse-narrow shape → `sat` →
     stable-first (≥700 asms) → my solver. TRUE for both SE-PR cells.
   - SE-ST (stable, single-extension): needs `large_dense_flat_aba_shape`
     (rule_density > 25) AND sparse-narrow. abcgen_c25 has density
     18132/875 = **20.7 → routes to clingo**, never reaching the changed
     solver. This gate was set DELIBERATELY by
     `experiments/2026-07-07-aba-sest-clingo-route.md` ("abcgen_c25 …
     stays asp"). abcgen_c35_asms30 (31066/1050 = 29.6) does route to the
     changed solver.
   Consequence: SE-ST c25 is unreachable by this experiment's single variable;
   flipping it requires a routing-gate change, which I did NOT make
   (single-variable discipline; recommended as follow-up, §8).
4. `scratchpad/abcgen_stable_profile.py` no longer exists anywhere — the
   committed replacement is `scripts/profile_abcgen_stable.py`.

## 2. What was built (mechanism, per the committed derivation)

Single variable: the well-foundedness mechanism inside
`_NativeSparseNarrowStableSolver`. Everything else (completion + contrary
clauses, routing, result surfaces) unchanged.

- Bipartite atom/body-node dependency graph → iterative Tarjan → recursive
  rules (body node in head's SCC) → intra-SCC derivation edges.
- New vars: `edge[(b,h)]` per intra-SCC edge, `just[r]` per recursive rule.
- Clauses: (J) `just[r] ↔ support[r] ∧ ⋀ edges`; (C′) completion only-if uses
  `just[r]` instead of `support[r]` for recursive rules; (D) demand pruning
  `edge → ⋁ justs`; acyclicity via **eager enumeration of ALL elementary
  cycles of the static edge graph** (deterministic capped DFS; caps 20k
  cycles / 2M steps) each blocked by a short all-negative clause. If a cap
  trips: reciprocal guards + lazy edge-cycle CEGAR fallback (correct either
  way). Lazy loop-formula machinery deleted; `loop_formulas` telemetry pinned 0.
- Safety net: bitset-Horn-closure verification of the final model
  (raise-on-encoding-bug; derivation proves it can't fire; it never fired in
  any run or test).
- Soundness + completeness for stable semantics derived and committed BEFORE
  implementation (b446dfb): soundness by induction over (SCC condensation
  rank, intra-SCC topological order of selected edges); completeness by
  selecting level-minimal justifying rules whose edges strictly increase
  T_P level. Two load-bearing structural facts (F1: non-recursive rules have
  no same-SCC body atom; F2: recursive rules have ≥1) proved in the record.

TDD: RED test first — fixture (contrary(a)=c, rules {c←a, c←d, d←c}) where
EVERY completion model is unfounded, forcing the old solver to emit a loop
formula; observed failure `assert 1 == 0` on the loop-formula telemetry before
implementation. Iteration 2 had its own RED (KeyError on the new eager-cycle
telemetry key). GREEN + REFACTOR (helper extraction, eager/lazy split) done;
tests in `tests/structured/aba/test_aba_stable_arc_acyclic.py` (3 tests) plus
the pre-existing oracle property tests.

## 3. Encoding size (the propagator-fallback question)

Eager clause volume did NOT explode — the IPASIR-UP propagator was not needed:

| instance | asms | rules | recursive rules | edge vars | eager cycle clauses | build |
|---|---:|---:|---:|---:|---:|---:|
| c25_ins1 | 875 | 18132 | 187 | 194 | 92 (max len 8) | 0.26s |
| c35_asms30_ins2 | 1050 | 31066 | 732 | 818 | 822 (max len 21) | 0.48s |
| c35_asms35_ins2 | 1225 | ~35k | 689 | 762 | 718 (max len 18) | 0.56s |

## 4. Microbench profile (flatness evidence; scripts/profile_abcgen_stable.py)

c25 (the scout's probe instance), per-solve seconds:

- BASELINE (pristine, loop-formula CEGAR): 15.3, 14.1, 55.9, 14.1, 71.7,
  108.6 — **growing**, 6 checks, 191 loop formulas, total **280.7s**
  (reproduces the scout's 247.9s mechanism on my tree, slightly worse).
- Iteration 1 (edge-cycle CEGAR): 1.2, 0.004, 7.8, 21.2, 16.7, 0.2, 11.6,
  32.0, 11.4, 0.03, 29.5, 46.5 — still growing-ish, 12 checks, total 178.3s.
- Iteration 2 (eager all-cycles): **ONE solve, 56.0s, zero CEGAR rounds** —
  flat by construction. Witness size 76, closure-verified.

c35_asms30 (iteration 2): ONE solve = **522.2s**. Flat (single solve), but the
single CDCL solve is itself the wall on the bigger cell — this is the
giant-SCC/instance-hardness wall the stop rule names, not CEGAR degradation.
c35_asms35 fixed profile was lost to a killed background task (its t120 cell
status is recorded); not re-run within budget.

Stop-rule evaluation: after 2 iterations the profile does NOT grow (single
solve). The stop rule's "profile still grows" trigger is NOT met; its deeper
concern (the wall is instance size, not the lazy CEGAR) IS what the c35
measurement shows. No third encoding iteration attempted, per the rule.

## 5. Metric gate (all re-baselined on this tree, t120, runner auto backend)

| cell | baseline (b446dfb) | fixed (9ca0b56) |
|---|---|---|
| SE-ST c25_ins1 | timeout 120s | timeout 120s (clingo route — unreachable by this variable) |
| SE-ST c35_asms30_ins2 | timeout 120s | timeout 120s (my path; single solve 522s) |
| SE-PR c25_ins1 | timeout 120s | **SOLVED 65.3s, witness 76** (route metadata: native_sparse_narrow_sat / monotone_cegar_stable_witness) |
| SE-PR c35_asms35_ins2 | timeout 120s | timeout 120s (my path) |

SUCCESS criterion (both SE-ST cells < 120s): **NOT met** — one SE-ST cell
cannot be reached by the changed code on current main (routing), the other
needs 522s for its single solve. Bonus criterion (SE-PR flip): **met for c25**
(+1 solved frontier cell, no losses).

## 6. Guard slice (SE-ST t15, exp-4B command shape) — PASSED

Command: `uv run tools/iccma2025_run_native.py --only-subtrack SE-ST
--backend auto --max-af-arguments 1 --max-aba-assumptions 1000000
--timeout-seconds 15 --label abcgen-arc-acyc-sest-guard-<phase>
--no-progress`; comparison by `scripts/compare_aba_sest_routes.py`
(full output: logs/abcgen-arc-acyc-guard-compare.log).

| metric | baseline (b446dfb) | fixed (9ca0b56) | kill criterion | verdict |
|---|---|---|---|---|
| ABA rows solved / timeout | 241 / 79 | 242 / 78 | lost row > 0 | **0 lost** ✓ |
| answer mismatches (241 common) | — | 0 | > 0 | ✓ |
| commonly-solved elapsed | 358.19s | 340.27s (−5.00%) | > +10% | ✓ (net faster) |
| gained | — | +1: abcgen_c7_atoms200_asms100_cp0.8_ins1 TO→solved 14.07s | — | witness natively verified stable (1/1) |

7 individual rows regressed >10%, all sub-2s (e.g. 0.878→1.102s) — noise
scale; the aggregate −5% governs. Named rows aba_2000_0.1_5_5_{1,6} unchanged
(~0.7s). Note the exp-4B-era baseline was 225/95; current main is already at
241/79 on this slice.

## 7. Correctness gates

- `uv run pytest tests/solving tests/interop tests/structured`: 1484 passed
  (structured) + 291 passed / 3 skipped (solving+interop) on the implementation.
- Full CI-equivalent `uv run pytest` before final commit:
  **2954 passed, 4 skipped, 1 xfailed** (main was 2951/4/1; +3 = the new
  arc-acyclic tests). Exit 0. Log: logs/abcgen-arc-acyc-full-pytest.log.

## 8. Kill / stop evaluation and recommendation

- **Kill checks: all clear.** Guard: 0 lost rows, 0 answer mismatches,
  common-time −5.0% (limit +10%), +1 gained row. Cells: nothing lost, SE-PR
  c25 gained. Exactness: property tests + fixtures green; every new witness
  closure-verified.
- **Stop rule: not triggered.** After iteration 2 the per-solve profile is
  flat (single solve). The rule's escalation clause is still the right read
  for c35: its single solve costs 522s, so the residual wall is instance/SCC
  scale, not the CEGAR — do not iterate the encoding further.
- **Recommendation: PROMOTE** `exp/abcgen-arc-acyc` (recommend-only; no merge
  performed from this worktree). The change is strictly better on every
  measured surface: mechanism (280.7s/6 growing solves → 56.0s/1 solve on
  c25), frontier (+1 SE-PR cell at t120), guard slice (+1 row, −5% time,
  nothing lost), and it deletes the known-degenerate loop-formula mechanism.
- **Follow-ups for the foreman (out of this experiment's single variable):**
  1. Routing-gate experiment: abcgen-shaped SE-ST rows (sparse-narrow,
     density ≤ 25, cycle-heavy) currently go to clingo, which also times out;
     with this encoding the native solver does c25 in ~56-65s. Re-examine the
     `large_dense_flat_aba_shape` AND-gate from
     experiments/2026-07-07-aba-sest-clingo-route.md for the abcgen shape
     (e.g., admit sparse-narrow cycle-heavy shapes, or try-stable-first with
     budget). That alone should flip SE-ST c25 at t120.
  2. c35-scale single-solve hardness (522s): escalate to SCC-decomposition /
     cutset preprocessing (queue items 5 and 9), per the scout's stop-rule
     recommendation.
  3. Optional: re-measure the c35_asms35 profile (lost to a killed background
     task) if its number matters for the routing follow-up.

## Incidents (full disclosure)

1. The first baseline background run was launched before implementation began,
   but its 4 runner cells started AFTER solver edits had begun in the working
   tree → contaminated. Killed the process tree, deleted its logs and run
   JSONs, and re-ran all baseline cells from a pristine detached checkout of
   b446dfb. The baseline MICROBENCH from that first run is valid (its
   loop_formulas=191 telemetry proves it executed the old code) and was kept.
2. A later background chunk (bmo53thnu) was killed by the environment (~26 min
   lifetime) — cost: the c35_asms35 fixed microbench only; its cell result was
   already recorded.
