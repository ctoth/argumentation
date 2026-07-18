# 2026-07-18 — Productionize the CaDiCaL engine win on the flat stable path

Branch: `exp/aba-cadical-engine-prod` (base `f4b8eac` = main). Wave 2 of the
c35 lane. Preregistered BEFORE implementation. Timing gates are DEFERRED until
the census-worker releases machine priority; reading/contracts/implementation
proceed first, all synchronous.

Prior evidence (Wave 1, `experiments/2026-07-17-aba-c35-cadical-engine.md`):
direct CaDiCaL 2.2.1 solves the flat eager-arc c35 SE-ST CNF in 9–25s (models
verified) where glucose4 times out >651s / 591.6s; c25 24.4s < glucose 63.1s.
Triage GO, directional. This experiment turns that into a routed production
change with a real dependency, a structural predicate, phase parity, and a
no-row-loss fallback.

## Hypothesis and single variable

**Hypothesis:** routing the flat one-shot stable/SE-ST CNF solve to a stronger
CDCL engine, gated by a structural predicate, converts the c35-class timeouts to
solved rows without losing or slowing any currently-solved row.

**Single variable:** the SAT engine used for the flat stable solve
(`_NativeSparseNarrowStableSolver`), chosen by a structural predicate. Nothing
else changes: parser, encoding (eager-arc completion + acyclicity clauses),
variable numbering, assumptions, phase vector, witness interpretation, and the
incremental CEGAR paths (`native_cnf_prefsat_extension` / SE-PR growth loop /
DS-PR) are all untouched.

## Scope — flat one-shot path ONLY

In scope: `_NativeSparseNarrowStableSolver` (the flat SE-ST solve;
`stable_extension()` with `require_assumptions=frozenset()` is checks=1, no
CEGAR — the exact path Wave-1 evidence covers). Seam: the hardcoded
`solver_class(name="glucose4")` at `aba_sat.py:868`.

OUT of scope (do not touch): `_NativeCnfPrefSatSolver`
(`aba_sat.py:456`, the preferred CEGAR loop), SE-PR, DS-PR, and any incremental
`solve(assumptions=...)` refinement loop. Wave-1 evidence does not cover
incremental engine behavior; the 2026-05-20 cadical195 record even shows it
*increased* CEGAR checks/loop formulas on a different shape.

## Dependency decision — gate D0 (deferred timing)

No CaDiCaL 2.x PyPI wheel exists (checked pypi.org: no `cadical`/`kissat`
standalone package). pysat 1.9.dev2 bundles CaDiCaL up to **1.9.5**
(`cadical195`) and Kissat 4.0.4 (`kissat404`).

- `kissat404` is **DISQUALIFIED**: it **segfaults** in pysat on the small
  fidelity CNF (exit 139) even for a trivial solve. A segfaulting engine cannot
  satisfy "cannot lose a row".
- `cadical195` **correctness PASSES** now (non-timing): on the small fidelity
  CNF it returns SAT with a model that satisfies every clause (947/947),
  matching glucose4 and the rel-2.2.1 binary.

**D0 (deferred, --jobs 1):** cadical195 must reproduce the Wave-1 win on the
byte-identical c35 eager-arc CNF — solve c35_asms30_ins2 to verified SAT in
**≤ 120s** (the budget) AND within **≤ 3× the rel-2.2.1 25.28s** (i.e. ≤ ~76s),
`--jobs 1`. If D0 passes → **primary dependency = pysat `cadical195`** (bundled,
reproducible, no build, incremental-capable). If D0 fails (1.9.5 does not carry
the 2.x improvement) → **fallback dependency = a committed vendored CaDiCaL
2.2.1 build script** driving `cadical.exe` as a batch DIMACS solver on the flat
path, matching Wave-1 evidence exactly. The implementation is written
engine-agnostic so D0 only flips which engine the predicate selects.

CAUTION carried from `2026-05-20-cadical195-sparse-narrow-engine.md`: on a
*different* shape (c7/atoms200/asms100) and the *incremental* path, cadical195
was only ~7% faster than glucose4. D0 tests the *flat c35* path specifically;
that prior weak result is not evidence about this path.

## Structural routing predicate (measured features, not family names)

Routing MUST NOT key on instance/family names. The predicate reads features
measured at build time from the constructed CNF/framework:
- `clauses` (exported clause count), `variables`, `assumptions`,
- `acyc_recursive_rules` (recursive-rule / `just_vars` count) and `acyc_edges`
  (the intra-SCC edge-graph size) — the structural "giant recursive core"
  signal that distinguishes the c35 class.

Predicate `route_strong(features) -> bool` returns true only above a threshold
calibrated on the dev slice so that the routed set is **a superset of the
glucose4-timeout rows and a subset of the strong-engine-solved rows**. Default
threshold is conservative (only the giant class routes; everything glucose
already solves keeps glucose). The exact feature+threshold is frozen after the
dev-slice calibration (deferred timing) and recorded here.

## Phase parity

`set_phases` (`aba_sat.py:922`: in-vars positive, edge-vars negative) is applied
identically regardless of engine (it runs in `__init__` before any solve). A
contract test asserts the phase vector passed to the routed engine is
byte-identical to the glucose4 phase vector for the same framework.

## No-row-loss fallback (portfolio safety invariant, AGENTS.md)

- The predicate routes to the strong engine only on structurally
  glucose-doomed rows; on those, a strong-engine timeout loses nothing (glucose
  times out too).
- If the strong engine raises/errors/returns UNKNOWN (not a clean SAT/UNSAT),
  the flat path **falls back to glucose4** on the same CNF within the remaining
  budget.
- **Safety gate (dev slice):** for EVERY dev row where glucose4 solves within
  budget, the shipped path must also solve it within budget (either not routed,
  or the strong engine solves it). Any row that glucose solved and the routed
  build does not = immediate NO-GO. This is the concrete "cannot lose a row"
  check.

## Fast contracts (TDD, committed RED before implementation)

`tests/structured/aba/test_aba_stable_engine_routing.py`:
1. **Default unchanged:** a sub-threshold framework selects `glucose4`
   (existing telemetry/behavior tests stay green).
2. **Routing:** an above-threshold synthetic framework selects the strong
   engine; `route_strong` returns true; telemetry records the engine choice.
3. **Correctness parity:** on small/medium frameworks (incl. cyclic-support),
   the routed-engine stable extension equals the glucose4 extension equals the
   `support_extensions` oracle; `require_assumptions` honored.
4. **Phase parity:** the phase vector for the routed engine == the glucose4
   phase vector (same framework).
5. **Fallback:** with an injected strong-engine error, the flat path returns the
   correct glucose4 extension (no crash, no lost answer).
6. cadical195 model validity: a returned SAT model satisfies every emitted
   clause (independent check).

Existing suites `tests/structured/aba` then full CI-equivalent
(pytest, pyright, ruff, uv build) before final commit.

## Dev slice / metric gate (DEFERRED timing, --jobs 1)

After D0 and green contracts, once census releases the machine:
1. c35 rows (asms30_ins2, asms35_ins2): flip to solved under t120 with the
   routed engine; per-row timing `--jobs 1`.
2. c25 no-regression row (asms35_ins1): routed build solves it ≤ its glucose
   baseline (63.1s), no answer change.
3. abcgen c25 + ABA property suite + full ABA suite: no regression, no lost row.
4. Safety gate: no dev row solved by glucose but not by the routed build.

SUCCESS = c35 rows flip AND the no-row-loss safety gate holds AND phase/
correctness contracts pass. STOP RULE: 2 implementation iterations max. This is
still recommend-only; the verifier promotes.
