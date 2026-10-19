# Round 1 triage-probe worker — stable-first SE-PR shortcut

Date: 2026-07-11
Role: triage-probe worker (CLI). `ward set experiment` to run.

## Hypothesis (mine only)
On a flat ABA framework, a stable extension is a valid preferred extension, so
SE-PR single-extension may safely try the stable path first and bypass the
preferred maximization loop when stable succeeds.

## Scope / guardrails
- TRIAGE PROBE ONLY. Do not modify production solver code or evaluator tests.
  Do not implement the shortcut.
- Frozen dev instance: `benchmarks/aba/aba_2000_0.3_10_10_1.aba` ONLY (row1).
  This is T3 (SE-PR timeout) but SE-ST solved in ~1.2 s — the interesting row.
- One reusable diagnostic script under scripts/, run with `uv run`. No python -c,
  no inline PS, no bare python, no heredoc.
- Never touch holdout. Preserve untracked files. No checkout/stash/clean/reset/
  restore/push.
- Expected HEAD begins at `4782b76`. Reconcile if newer campaign commit; abort on
  unrelated tracked change.

## Probe must establish (dev instance only)
1. framework shape/flatness + current auto route
2. stable single-extension result under calibrated 5 s solve budget
3. stable witness passes repo INDEPENDENT preferred-extension validity check
   (not merely the stable checker)
4. current preferred-path telemetry: is maximization loop entered? solver/outer/
   refinement counts
5. py-spy real-worker profile of this SE-PR row @ 15 s cap; dominant cost;
   compare to committed N1 profile (302/384 in clingo.Control.solve).

## Survive criteria (ALL required)
- flatness/soundness premise holds
- auto route is Clingo, not recorded-dead SAT path
- stable finds witness within 2 s in measured run
- independent preferred verifier accepts it
- current SE-PR telemetry/profile shows work a stable-first success would skip
Else: KILL and name exact failed premise.

## Key source facts (from reports, to VERIFY in source)
- parse: `from argumentation.interop.iccma import parse_aba`
- solve: `argumentation.structured.aba.aba_asp.solve_aba_with_backend`
- route: `argumentation.structured.aba.aba_route_policy` — sparse_narrow needs
  assumptions>=700 (600 fails), large_dense needs density>25 (~13 fails) → auto→clingo
- flat check: `_is_flat_aba` in aba_route_policy
- SE-PR path: find_preferred_extension → enumerate_preferred(limit=1) CEGAR loop
  (aba_incremental.py ~591-637)
- telemetry: _incremental_telemetry_metadata (aba_asp.py ~366-373): solver_calls,
  outer_iterations, inner_iterations, refinement_clauses, clingo_grounding
- independent preferred verifier: solver_differential.py (need to locate exact call)
- instance path: data/iccma/2023/extracted/instances/benchmarks/aba/aba_2000_0.3_10_10_1.aba

## VERIFIED SOURCE FACTS (2026-07-11)
- git: HEAD == 4782b76 (expected), no tracked changes. `ward set experiment` done.
- parse_aba: src/argumentation/interop/iccma.py:180 → ABAFramework.
- ABAFramework.__post_init__ (aba.py:62-67) REJECTS non-flat at construction
  (NotFlatABAError). So a parsed ABAFramework is flat BY CONSTRUCTION — independent
  flatness guarantee, on top of aba_route_policy._is_flat_aba (route_policy.py:77).
- Route: _auto_aba_backend_for_framework (solver.py:522) → sat only if
  sparse_narrow_native_sat_shape (needs assumptions>=700; 600 FAILS, route_policy:58)
  for preferred SE, or (large_dense AND sparse_narrow) for stable SE. Falls to
  _auto_aba_backend (solver.py:504) → returns "asp" (clingo) for preferred SE and
  stable SE when clingo present. => 600-assumption instance routes auto→clingo. CONFIRMED in source; verify at runtime.
- solve_aba_with_backend (aba_asp.py:99): backend, semantics, task='single-extension',
  clingo_solve_timeout_seconds. backend 'clingo' → _solve_multishot.
- _solve_multishot (aba_asp.py:244): stable SE → find_stable_extension;
  preferred SE → find_preferred_extension → enumerate_preferred(limit=1) CEGAR loop.
  On ClingoSolveTimeout returns status='timeout' WITH accumulated telemetry metadata
  (aba_asp.py:318-328).
- Telemetry metadata fields (_incremental_telemetry_metadata aba_asp.py:366): 
  refinement_clauses, outer_iterations, inner_iterations, solver_calls, clingo_grounding.
- SE-PR loop (aba_incremental.py:595 enumerate_preferred): outer seed solve + inner
  _grow_to_maximal_not_deriving (adds refine{n} constraints, re-grounds each). This is
  the loop the shortcut would skip.

## INDEPENDENT PREFERRED CHECK DESIGN (sound, polynomial, reference-kernel aba.py)
Public primitives: aba.admissible(fw,S), aba.conflict_free(fw,S), aba.attacks(fw,att,tgt).
Witness S from clingo STABLE solver. Independent check (NOT the clingo stable solver):
  (A) admissible(fw,S) == True  → S admissible/self-defending.
  (B) MAXIMALITY: conflict_free(fw,S) AND for every a in assumptions-S:
      NOT conflict_free(fw, S|{a}). 
      SOUND PROOF: any admissible (hence conflict-free) T ⊋ S has a in T\S; S|{a}⊆T;
      subset of conflict-free is conflict-free ⇒ S|{a} conflict-free — contradiction.
      ⇒ no admissible proper superset ⇒ S is ⊆-maximal admissible ⇒ PREFERRED.
  (B) is a genuine maximality/preferred check ("not merely the stable checker").
  Also cross-check stability via reference kernel (attacks all outside) for the record.

## PLAN
- scripts/diagnose_aba_stable_preferred_shortcut.py (reusable): item1 shape/route,
  item2 stable SE @5s + telemetry + wall, item3 independent preferred check (A)+(B).
  Bounded & deterministic. Run via `uv run`.
- item4 preferred-loop telemetry + profile: from runner py-spy 15s SE-PR row JSON
  (real worker, real budget). Compare dominant cost to N1 (302/384 clingo.Control.solve).
- Then: focused tests + diagnostic; write experiments/ record; update INDEX.md Round 1
  + probe budget; ONE atomic commit (script+record+INDEX). No push.

## OPEN: verify bounded preferred call behavior empirically; confirm runner surfaces telemetry.
## Status: source verified. Next: write+test diagnostic script.

## RETRY SESSION 2026-07-11 (CLI worker, opus)
- HEAD == 4782b76 confirmed, tracked clean. `ward set experiment` done. No prior
  script/record exist yet — must create both.
- CONFIRMED API SIGNATURES (read source this session):
  - solve_aba_with_backend(framework, *, backend, semantics, task='enum', query=None,
    binary='clingo', timeout_seconds=30.0, simplify=True, clingo_control_args=(),
    collect_clingo_statistics=False, clingo_solve_timeout_seconds=None) -> ABAQueryResult
    (aba_asp.py:99). NOTE keyword `clingo_solve_timeout_seconds` is the calibrated solve
    cap; `timeout_seconds` is subprocess. For single-extension pass task='single-extension'.
  - ABAQueryResult (frozen dataclass aba_asp.py:31): fields status, semantics, backend,
    extensions: tuple[AssumptionSet,...], accepted_assumptions: AssumptionSet, encoding,
    metadata: dict, witness=None. Single-ext success → extensions=(ext,), status likely
    'success'; ClingoSolveTimeout → status='timeout' WITH telemetry metadata.
  - _incremental_telemetry_metadata keys: refinement_clauses, outer_iterations,
    inner_iterations, solver_calls, clingo_control_args (aba_asp.py:366).
  - aba.py primitives (public): attacks(fw, attacker_assumptions, target_assumptions)@97,
    conflict_free(fw, S)@127, admissible(fw, S)@131, stable_extensions(fw)@170.
  - ABAFramework.__post_init__ raises NotFlatABAError if any assumption is a rule head
    (aba.py:62) → parsed fw is flat by construction. Independent flatness guarantee.
- Extension elements: need to confirm the extension returned is a frozenset of assumption
  Literals compatible with admissible()/conflict_free() inputs. WILL verify at runtime.
- Next: write scripts/probe_iccma2023_stable_preferred_shortcut.py, run it, then py-spy.

## CRITICAL CORRECTION (this session)
- aba.py reference kernel (admissible/conflict_free/attacks/stable_extensions) is
  EXPONENTIAL: `_all_subsets`/`_defends` enumerate the powerset of all 600
  assumptions (2**600). My earlier "independent check via aba.admissible" plan was
  INFEASIBLE. solver_differential is differential (re-runs the exponential native
  backend) — also unusable at scale.
- REPLACED with a self-contained POLYNOMIAL independent preferred verifier using
  ONLY horn_closure (`_closure.py:19`). Soundness (flat ABA, cl=horn_closure):
  attacks(X,a) <=> contrary[a] in cl(X); conflict-free(S) <=> no a in S has
  contrary[a] in cl(S); admissible(S) <=> conflict-free AND for a in S:
  contrary[a] not in cl(U) where U = assumptions not attacked by S; maximal-
  conflict-free(S) <=> every outside assumption attacked by S. THEOREM: admissible
  + maximal-conflict-free => preferred (sufficient; a stable ext always satisfies).
  Two Horn closures total. This is genuinely independent of the clingo stable
  solver and NOT merely the stable checker (verifies admissibility + maximality).
- CONFIRMED live runner CLI flags: --root --backend --max-af-arguments
  --max-aba-assumptions --timeout-seconds --label --profile-workers-dir
  --profile-workers-format --profile-worker-subtrack --only-instance
  --only-subtrack --jobs (all present, iccma2025_run_native.py:103-159).
- Route confirmed in source: _auto_aba_backend_for_framework('auto',sem,
  task='single-extension',framework=fw); sparse_narrow needs assumptions>=700
  (600 fails, route_policy:58) => both SE-ST/SE-PR route to 'asp' (clingo).
- SCRIPT WRITTEN: scripts/probe_iccma2023_stable_preferred_shortcut.py.
  Blocker/next: RUN it via uv; then py-spy runner on SE-PR row @15s raw; then
  write experiments record + INDEX update; one atomic commit (script+record+INDEX).
