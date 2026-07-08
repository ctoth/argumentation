# exp 4B: unblock simplify_aba(stable) pre-solve hang (ABA SE-ST named rows)

Branch: `exp/aba-simplify-stable-budget` off main@cc50c4a (contains the exp-4
SE-ST routing gate bc140ba). Fix commits: 8a934dc (grounded fixpoint) and
23c6856 (reporting-encoding support facts) -- two call sites of the SAME
exponential primitive; the second was masked by the first until the metric
gate exposed it (see Interpretation).

## Hypothesis

The two frontier-v1 hard cells ABAs/aba_2000_0.1_5_5_{1,6} SE-ST still time out
after the exp-4 routing fix because `solve_aba_with_backend(..., simplify=True)`
runs `simplify_aba(semantics="stable")` before the (0.4s) clingo solve, and that
preprocessing pass exceeds any realistic row budget (verifier: >200s cap
exceeded). If the preprocessing blow-up is removed without changing its output,
both rows flip timeout -> solved in a couple of seconds with no other row lost
or answer changed.

## Investigation

Call chain (read from source): `solve_aba_with_backend` (aba_asp.py:99,
`simplify=True` default) -> `simplify_aba` (aba_preprocessing.py) ->
`grounded_assumption_set_via_supports` -> `_SupportState.from_framework`
(aba_support_model.py:31) -> `_minimal_supports` (aba_support_model.py:108).
`_minimal_supports` enumerates ALL minimal derivation supports per literal via
Cartesian `_combine_supports` over rule bodies -- worst-case exponential in
rule-body width. The aba_2000 shape (bodies up to 5, contrary multiplicity 3,
5560 rules over 2000 atoms) hits that worst case. This is the same
`_add_minimal_support` hotspot the 2026-06-29 DC-CO profile measured at 92.7%
(different caller, same primitive). Everything else in `simplify_aba` is
polynomial (`horn_closure` worklist closures, O(rules) residual construction);
the cheap bail-out at the top of `simplify_aba` computes closures only and does
NOT fire on these instances (measured below), so the framework proceeds to the
grounded fixpoint.

Profiling (`scripts/profile_aba_simplify_stable.py`, run pre-fix; quoted):

```
== aba_2000_0.1_5_5_1.aba: atoms=2000 asms=200 rules=5560
  bail-out closures: 0.026s (bails-out=False)
  closure-based grounded prototype: 0.131s |grounded|=152
  _SupportState.from_framework: TIMEOUT >60s (killed after 60.0s)
== aba_2000_0.1_5_5_6.aba: atoms=2000 asms=200 rules=5400
  bail-out closures: 0.040s (bails-out=False)
  closure-based grounded prototype: 0.124s |grounded|=152
  _SupportState.from_framework: TIMEOUT >60s (killed after 60.0s)
== aba_100_0.1_10_10_6.aba: current=0.011s prototype=0.019s equal=True |grounded|=8
== aba_100_0.1_10_10_7.aba: current=0.009s prototype=0.015s equal=True |grounded|=7
== aba_100_0.1_10_5_7.aba: current=13.962s prototype=0.004s equal=True |grounded|=0
```

The blow-up is entirely inside the minimal-support enumeration; a closure-based
grounded fixpoint answers the same question in 0.13s. Note also |grounded|=152
on the named rows -- the simplification is genuinely useful there (it pins 152
of 200 assumptions; the clingo stable witness size is also 152), so skipping it
would discard real work. The blow-up is already visible at 100 atoms
(aba_100_0.1_10_5_7: 13.96s -> 0.004s, equal results).

## Chosen design: option (a) -- fix the algorithmic blow-up

Replace the support-mask def-operator fixpoint in
`grounded_assumption_set_via_supports` with an exact forward-closure
formulation (renamed `grounded_assumption_set_via_closures`). Per round, for
candidate set `S`:

* `attacked_by(S) = {b : contrary(b) in Th(S)}` -- one Horn closure;
* `a` is defended by `S` iff every assumption set deriving `contrary(a)`
  contains an attacked assumption; by monotonicity of `Th` this holds iff
  `contrary(a) not in Th(assumptions - attacked_by(S))` -- one more closure.

Equivalence with the old per-mask test is one-to-one: `contrary(a) in Th(X)`
iff some minimal support `s` of `contrary(a)` satisfies `s subseteq X`; with
`X = assumptions - attacked`, such `s` exists iff some support avoids
`attacked` entirely (including the empty support, i.e. fact-derivable
contraries -- the old code's `support == 0 -> never defended` branch). The
monotone fixpoint iteration (`selected | defended`, stop on no change) is
unchanged. Cost: at most `|assumptions|+1` rounds x 2 linear closures --
worst-case polynomial, so simplify_aba as a whole becomes polynomial.

Options (b) time-budget and (c) skip-for-asp-stable were NOT implemented:

* (b) budget: unnecessary once the pass is worst-case polynomial; a budget
  would add a config surface and a fall-through path (and a lost 152/200
  fixed_in) to guard against a blow-up that no longer exists.
* (c) skip: provably answer-preserving (the lift is
  `residual_extension | fixed_in` and clingo solves the unsimplified program
  fine in 0.376s), but it forfeits the simplification's genuine value on this
  shape and leaves the exponential primitive live for every other
  simplify_aba caller (SE-PR, DC-*, the SAT paths) and for
  `AbaIncrementalSolver.grounded_extension`, which calls the same function.
  Option (a) fixes all of those at once.

## Single Variable

One mechanism is removed from the SE-ST hot path: the worst-case-exponential
`_minimal_supports` enumeration. It sat at two call sites, fixed in two
commits:

1. **8a934dc** -- `grounded_assumption_set_via_supports` built
   `_SupportState.from_framework` (= `_minimal_supports`) to iterate the def
   operator; replaced by the closure-based fixpoint above (renamed
   `grounded_assumption_set_via_closures`).
2. **23c6856** -- with (1) in place the named rows STILL timed out: the first
   fixed benchmark run (label `aba-simplify-fixed-simplifyonly`, kept in
   data/iccma/2025/runs) showed 226/94 with both named rows at 15s. Root
   cause: `_solve_simplified` (aba_asp.py) rebuilt
   `encode_aba_theory(original)` with the default `include_supports=True` --
   `_minimal_supports` on the FULL original framework, for `support_*` facts
   the asp/clingo backends never read (the encoding there is reporting-only
   payload; the residual solve builds its own core-facts encoding, and
   `solve_aba_with_backend` already gates support facts on
   `backend not in {"asp", "clingo"}`). Fix: apply the same gate at the two
   `_solve_simplified*` encode calls. The only observable difference besides
   speed is the result's `encoding.metadata["encoding"]` label
   (`flat_aba_core_facts` instead of `flat_aba_assumption_support_facts`) on
   simplified asp/clingo results; no test or consumer reads support facts
   there (grepped).

No routing, solver, semantics, or configuration change. Same answers by the
equivalence argument above, enforced by the existing differential oracles.

End-to-end probe on the production entry point
(`scripts/probe_aba_sest_named_row.py`, `solve_aba_single_extension`
backend=auto, branch code):

```
aba_2000_0.1_5_5_1.aba: solved in 0.539s witness_size=152 solver=clingo_multishot preprocessing=grounded_reduct_aba
aba_2000_0.1_5_5_6.aba: solved in 0.483s witness_size=152 solver=clingo_multishot preprocessing=grounded_reduct_aba
```

## Fast Contracts

TDD RED (all on a 3**12-minimal-support layered-choice framework,
`_layered_choice_blowup_framework`: `q_0` fact, each `q_i` derivable from
`q_{i-1}` plus one of three per-level assumptions, `contrary(t) = q_12`;
grounded = all 36 choice assumptions, `fixed_out = {t}`; all under
`pytest.mark.timeout(60)`):

* commit 8a934dc: `test_grounded_via_closures_polynomial_on_minimal_support_blowup`
  and `test_simplify_aba_stable_polynomial_on_minimal_support_blowup` -- red
  before (timeout, stack pinned at `aba_support_model.py:153
  _add_minimal_support` under `_SupportState.from_framework`), green after.
* commit 23c6856: `test_asp_stable_single_extension_polynomial_on_minimal_support_blowup`
  drives the full `solve_aba_with_backend(backend="asp", semantics="stable",
  task="single-extension")` path -- red before (timeout, stack pinned at the
  `encode_aba_theory` -> `_minimal_supports` -> `_add_minimal_support` call in
  `_solve_simplified`), green after (`3 passed in 0.36s` for the blowup
  selection).

Full gates on the final commit 23c6856:

```
uv run pytest tests/solving tests/interop -q
291 passed, 3 skipped in 6.38s        (skips: pre-existing env skips)
uv run pytest tests/structured -q
1481 passed in 1990.33s               (exp-4 baseline was 1478; +3 = new tests;
                                       wall time inflated by machine load, all green)
```

## Metric Gate

Command (same SE-ST slice command as exp 4, including its
`--max-af-arguments 1` AF-row skip; labels per this experiment):

```
uv run tools/iccma2025_run_native.py --root C:\Users\Q\code\argumentation\data\iccma\2025
  --only-subtrack SE-ST --backend auto --max-af-arguments 1
  --max-aba-assumptions 1000000 --timeout-seconds 15
  --label aba-simplify-<baseline|fixed> --no-progress
```

Baseline ran with the worktree detached at main@cc50c4a (editable venv -- the
exp-4 lesson), fixed with the branch checked out at 23c6856; no src edits
during either run. Comparison recomputed by
`scripts/compare_aba_sest_routes.py` (exp-4's script; includes native witness
verification).

| run | solved | timeout |
|---|---|---|
| baseline (main cc50c4a) | 225 | 95 |
| fixed-simplifyonly (8a934dc, superseded) | 226 | 94 |
| fixed (23c6856) | **241** | **79** |

(320 ABA rows executed, 322 AF rows skipped, 15s cap, both runs.)

* **Named rows**: aba_2000_0.1_5_5_1 timeout 15.027s -> **solved 0.743s**
  (witness 152); aba_2000_0.1_5_5_6 timeout 15.014s -> **solved 0.681s**
  (witness 152).
* Lost: **0**. Answer mismatches on 225 commonly-solved: **0**.
* Gained: **16** (all timeout -> solved): aba_2000_0.1_5_5_{1,3,6,9},
  aba_5000_0.1_5_5_1, aba_500_0.3_5_5_3, aba_2000_0.3_10_10_9, and 9
  abcgen_c5/c7-family rows (e.g. abcgen_c5_atoms100_asms200_cp0.8_ins1
  15s -> 0.824s, w=261). All 9 gained rows with positive witnesses natively
  verified as stable extensions (9/16; the other 7 are negative "no stable
  extension" clingo-UNSAT answers with no cheap native check -- flagged, same
  treatment as exp 4).
* Commonly-solved aggregate elapsed: 348.71s -> 312.82s = **-10.29%** (well
  under the +10% kill line, in the wrong direction to kill).
* abcgen c25/c35/c7 dense rows: status unchanged row-for-row (every
  baseline-solved stays solved at comparable time, every timeout stays
  timeout) -- the abcgen completion-SAT/clingo hardness is untouched, as
  expected.
* 10 per-row >10% slowdowns among commonly-solved rows, all on sub-second
  rows with 0.05-0.25s absolute deltas. Spot reruns of the 3 worst on the
  quiet machine (fixed code, `--only-instance`): aba_100_0.3_5_10_0 0.226s
  (baseline 0.226s, contended 0.301s), aba_500_0.1_5_5_3 0.315s (0.323s /
  0.443s), aba_500_0.3_5_5_2 0.297s (0.287s / 0.367s) -- baseline-level,
  environmental noise, not change-caused.

Frontier-v1 SE-ST chunk (frozen manifest, 120s, branch code,
`scripts/run_frontier_v1.py --subtrack SE-ST`, label
frontier-v1-aba-simplify-23c6856): 4 cells -> **2 solved + 2 timeout**. The
two solves are exactly the named rows (reported as "deviations" from their
frozen `hard`=timeout expectation -- the desired flips, witness_size=152
each); the two 120s timeouts are the abcgen hard cells
(abcgen_c25_atoms25_asms35_ins1, abcgen_c35_atoms35_asms30_ins2), which are a
different bottleneck (completion-SAT loop formulas; scout verified clingo
times out on them too) and out of scope here.

## Interpretation

The hypothesis was right about the mechanism but incomplete about the count:
the pre-solve `simplify_aba` hang WAS the exponential minimal-support
enumeration, but the same primitive also ran a second time after the solve,
inside `_solve_simplified`'s reporting-only `encode_aba_theory(original)`.
The first fixed run (`aba-simplify-fixed-simplifyonly`) is the controlled
evidence: with only the grounded fixpoint fixed, the named rows still timed
out at 15s -- the post-solve encode alone exceeds the row budget. With both
call sites gated, the full production path runs in ~0.5-0.7s on the named
rows (probe + benchmark agree), i.e. preprocessing (0.13s grounded fixpoint)
+ clingo solve (~0.4s) now dominate, as the scout's decomposition predicted.
The 14 sibling gains (incl. 9 abcgen_c5 rows not named in any prior
experiment) show the blow-up was gating a whole family, not two instances.
No budget mechanism was needed: the pass is now worst-case polynomial, so
there is nothing left to starve the solve.

## Decision

PROMOTE (recommend merging `exp/aba-simplify-stable-budget` into main):
both named frontier-v1 SE-ST cells flip timeout -> solved (~0.7s at 15s cap;
confirmed at 120s frontier replay), +16 solved on the SE-ST slice, 0 lost,
0 answer changes, aggregate -10.29% on commonly-solved rows, all suites
green with 3 new red->green regression tests. Follow-ups (out of scope):
the abcgen completion-SAT stable hardness (cap200 Phase 2 SCC-level-map
recommendation stands), and auditing the remaining `_minimal_supports`
consumers (`sat_support_extension` DC-* paths, `support_reference` backend)
for the same worst-case blow-up.
