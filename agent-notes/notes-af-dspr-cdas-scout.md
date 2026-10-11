# Scout report: AF DS-PR (CDAS) / SE-ID (CDIS) implementation groundwork

Deliverable fallback location (reports/ write blocked by ward hook; team-lead
directed this path). Every code claim cites file:line. Two blocked items noted
explicitly: Bash (git diff) and reports/ Write were denied by the hook.

## Headline finding (changes the mission's premise)

The current DS-PR path is ALREADY CDAS-shaped, and `find_ideal_extension` is ALREADY
CDIS-shaped. The mission assumes "replace an enumeration algorithm with CDAS," but the
enumeration replacement already happened. `PreferredSkepticalTaskSolver` is docstringed
"CDAS-style skeptical preferred acceptance solver" (src/argumentation/solving/af_sat.py:700)
and `is_preferred_skeptically_accepted` says "Decide preferred skeptical acceptance using
CDAS admissibility checks" (af_sat.py:677).

The real gap versus Thimm 2021 is two specific pieces inside the existing loop — and they
are exactly the two bottlenecks the prior diagnosis note flagged:

1. Per-iteration maximization (`_grow_preferred`, af_sat.py:761 calling af_sat.py:1265).
   The DS-PR loop grows each extended attacker candidate to a maximal complete extension.
   This is precisely the `AdmSup` superset-maximization step the paper says CDAS AVOIDS.
2. Weak blocking lemma (`learn_witness_region`, af_sat.py:1150): the learned clause is
   just "OR over arguments outside the extension," giving weak per-iteration progress.
   Same weak clause notes/ds-pr-timeouts-2026-05-02.md:6 identified.

So the coder's task is better framed as "bring the existing CDAS/CDIS implementation in
line with the paper by removing the maximization step and strengthening the learned
clause," not "write CDAS from scratch."

## 1. Exact current DS-PR algorithm

Entry: `is_preferred_skeptically_accepted(framework, query, ...)` at af_sat.py:669.
- If simplify=True (default): `simplify_af(framework, semantics="preferred")` (af_sat.py:680).
  Query in fixed_in -> True; in fixed_out -> False; else continue on simplification.residual.
- Delegates to `PreferredSkepticalTaskSolver(...).decide(query)` (af_sat.py:692; class :699;
  decide :713).

decide(query) flow:
1. Shortcuts (`_shortcut`, af_sat.py:774): self-attacking query -> False; unattacked query ->
   True; query in grounded -> True; query attacked by grounded -> False; if AF acyclic,
   answer = query in grounded.
2. Preferred super-core (`PreferredSuperCoreSolver.compute`, af_sat.py:818/832) = PSC(AF):
   start current = all arguments; repeatedly find an admissible set attacking current and
   remove current - attacked_by(attacker); then `_prune_to_admissible_subset`. If
   required_query subset of super_core -> return True (af_sat.py:724).
3. Seed: `_complete_extension(required_in=required_query)` (af_sat.py:733). None -> return
   False (no admissible/complete set contains query; matches paper "no admissible set
   containing a -> NO").
4. CEGAR loop (af_sat.py:748):
   - attacker = `_PreferredSkepticalAttackerSolver.find_attacker(...)` — an admissible set
     attacking the admissible-with-query candidate. None -> return TRUE (matches "AdmExtAtt
     unsatisfiable -> YES").
   - extended = `_complete_extension(required_in = attacker | required_query)`. None ->
     return FALSE (matches "AdmExt(S' u {a}) unsat -> NO").
   - extended = `_grow_preferred(extended)` — MAXIMIZATION step (deviation from paper).
     None -> False.
   - `attacker_problem.learn_witness_region(extended)`; loop_index += 1; repeat.

The attacker sub-solver (`_PreferredSkepticalAttackerSolver`, af_sat.py:1078) holds its OWN
z3.Solver (separate from the AfSatKernel), persistent across iterations, accumulating
learned clauses via solver.add. It has attacker_vars and candidate_vars, both constrained
admissible via `_add_admissible_constraints` (af_sat.py:1103-1104); candidate_vars forced
to include the query (:1105-1106); and an Or over attack pairs requiring the attacker to
attack the candidate (:1108-1112).

Blocking lemma (`learn_witness_region`, af_sat.py:1150): outside = arguments - extension;
adds Or(attacker_vars[a] for a in outside), or BoolVal(False) when the extension is
everything. Just forbids the attacker from being a subset of the seen extension — weak
progress.

Termination/correctness: correctness is asserted by property test
`test_kernel_direct_skeptical_preferred_matches_native_oracle`
(tests/solving/test_solver_encoding.py:735), which checks the solver against
all(query in ext for ext in preferred_extensions(...)). Termination relies on the learned
clause eventually exhausting attacker candidates; the weak clause is what makes iteration
counts explode on hard instances.

## 2. Exact current SE-ID / DC-ID / DS-ID algorithm

`find_ideal_extension(framework, ...)` at af_sat.py:882 — this is CDIS:
- If simplify=True: `simplify_af(framework, semantics="ideal")`, recurse on residual, lift
  back (:889-898).
- Build AfSatKernel, add_admissible_labelling.
- current = all arguments; loop: `_admissible_attacker_of_set(current)` (af_sat.py:1060);
  if an admissible attacker exists, current = current - attacked_by(attacker); else break
  (:902-910).
- Return `_prune_to_admissible_subset(current, defeats)` (af_sat.py:912; helper :1214, which
  removes attacked args then iteratively drops args with undefended attackers).

Matches CDIS: remove arguments attacked by admissible sets (-> PSC), then reduce to the
maximal admissible subset.

Dispatch:
- SE-ID: `solve_dung_single_extension` (solver.py:342) -> auto backend returns "sat" for
  ideal (`_auto_dung_single_backend`, solver.py:513-520) -> `_SAT_SINGLE_EXTENSION_FINDERS
  ["ideal"] = find_ideal_extension` (solver.py:128).
- DC-ID / DS-ID: `solve_dung_acceptance` -> auto backend returns "sat" for ideal
  (solver.py:525) -> `_solve_sat_ideal_acceptance` (solver.py:931) computes the single ideal
  extension once and answers query in extension for both credulous and skeptical
  (:944-953). Since ideal is unique-extension, DC-ID == DS-ID, consistent with Fudge.

Note: find_ideal_extension uses NO CEGAR loop and NO maximization — already the clean
pruning form, so CDIS needs far less rework than CDAS.

## 3. CDAS mapping onto our code

Paper utility functions map to existing helpers:
- AdmExt(S) -> `_complete_extension(required_in=S)` (af_sat.py:1001; complete rather than
  admissible, but existence is equivalent since every admissible set extends to a complete
  one).
- AdmArgAtt / attacking-admissible-set search -> `_PreferredSkepticalAttackerSolver.
  find_attacker` (af_sat.py:1114) and `_admissible_attacker_of_set` (af_sat.py:1060).
- Stored excluded set E -> the accumulated learned clauses in the attacker solver.

What would be replaced: the body of the decide loop — specifically dropping the
`_grow_preferred` call (af_sat.py:761) and strengthening `learn_witness_region`
(af_sat.py:1150) to the paper's exclusion of the seen extended set rather than a bare "some
outsider" clause. What stays: AfSatKernel encodings, PreferredSuperCoreSolver, the shortcut
ladder, simplify_af preprocessing, find_ideal_extension.

New SAT queries needed: likely none new in kind — CDAS reuses admissible/complete existence
and attacking-admissible-set queries, all already implemented. The change is loop structure
and learned-clause content, not new encodings.

Z3 incrementality:
- AfSatKernel uses one z3.Solver per AF and drives per-call constraints via solver.push() /
  require_* (solver.add) / check() / solver.pop() (af_sat.py:969-998, 1044-1057). Incremental
  via push/pop scopes. check() accepts an assumptions tuple (af_sat.py:312) but callers use
  push+add+pop, NOT assumption literals — assumption-based solving is available but unused.
- The attacker solver (af_sat.py:1078) uses a single persistent solver with monotonic
  solver.add for learned clauses (no push/pop) — a true incremental CEGAR accumulation. So
  the codebase already supports the incremental pattern Fudge recommends; a stronger
  blocking clause slots directly into learn_witness_region.

## 4. Grounded reduct + SCC wiring into DS-PR

- Grounded reduct: already wired. `simplify_af(..., semantics="preferred")` and "ideal" are
  both in GROUNDED_REDUCT_SEMANTICS (core/preprocessing.py:69-78; includes complete/
  preferred/stable/semi-stable/grounded/ideal; excludes stage and admissible with documented
  counterexamples). Grounded extension -> fixed_in; grounded-attacked -> fixed_out; residual
  solved (preprocessing.py:138-142). So the prior note's hypothesis 2 ("grounded reduct not
  used as preprocessor") is now STALE/RESOLVED for the SAT DS-PR and ideal paths.
- SCC decomposition: core/scc_recursive.py exists but HARD-STOPS at complete/preferred/stable
  enumeration only (scc_recursive.py:45-46: "only complete / preferred / stable. Semi-stable,
  stage, grounded, ideal, admissible keep their existing flat paths"). It is an enumeration
  layer, not an acceptance layer. The SAT DS-PR acceptance path
  (is_preferred_skeptically_accepted) does NOT invoke SCC at all. What prevents wiring it in:
  the SCC layer produces full extension enumerations for the three semantics, whereas DS-PR
  is a decision that avoids enumeration by design; there is no acceptance-oriented SCC entry
  point on the SAT path today. Prior note hypothesis 2 (SCC would shrink hard instances)
  remains UNADDRESSED for DS-PR.

## 5. Tests covering DS-PR / SE-ID

Primary: tests/solving/test_solver_encoding.py (imports at :1-45):
- DS-PR correctness vs native oracle:
  test_kernel_direct_skeptical_preferred_matches_native_oracle (:735), plus concrete cases
  at :129-130.
- Super-core containment: :621, :748.
- Ideal vs native oracle: :575, :762, and test_kernel_ideal_extension_matches_native_oracle
  at :759.
- Learn-witness telemetry: :234-239.

Also: tests/solving/test_solver_differential.py (property-based differential vs
argumentation.core.dung oracles, credulous/skeptical at :76), and
tests/core/test_dung_ideal_admissibility.py.

Run just these:
    uv run pytest tests/solving/test_solver_encoding.py tests/solving/test_solver_differential.py
Narrow to DS-PR/ideal specifically with -k:
    uv run pytest tests/solving/test_solver_encoding.py -k "skeptical or ideal or super_core"
(Caveat: pytest NOT executed — Bash blocked in this session. Verify the runner invocation.)

## 6. Benchmarking DS-PR rows with tools/iccma2025_run_native.py

Flags (argparse at tools/iccma2025_run_native.py:105-172):
- --only-subtrack DS-PR (repeatable, :162) — selects only DS-PR.
- --only-instance <manifest relative_path> (repeatable, :156) — selects specific instances.
- --max-af-arguments (default 100 = cap-100, :124), --timeout-seconds (default 5.0, :126),
  --backend auto (default; routes DS-PR -> SAT via _auto_dung_acceptance_backend),
  --root (default data/iccma/2025, :20/105), --label, --event-log-path, --profile-workers-dir.

DS-PR only, cap-100:
    uv run python tools/iccma2025_run_native.py --only-subtrack DS-PR --backend auto
Specific instances (e.g. historical timeout cases irvine-shuttle / BA_60_60_3 /
Small-result-b76):
    uv run python tools/iccma2025_run_native.py --only-subtrack DS-PR \
      --only-instance <relative_path_1> --only-instance <relative_path_2>

Family selection (mainkwt / ER / crusti): there is NO dedicated --family flag. Families are
encoded in the manifest relative_path, so select them via repeated --only-instance with the
family's paths (or filter the manifest yourself). Instances are enumerated from
iccma-*-manifest.json under the root (:266-274). The coder should confirm exact relative
paths for each family before running.

## 7. Branch delta — UNVERIFIED (blocked)

Could NOT run `git diff master...HEAD --stat -- src/` because Bash is blocked by the ward
hook. Indirect evidence: the start-of-session git status showed NO modified tracked files —
only untracked logs/notes/prompts — so the working tree has no uncommitted src/ changes. The
recent commits (58b13df, 4f03afc, f367720, 0d5ac3c, 8800185) are all ABA DC-CO routing-shape
and doc work, none naming AF-side files. So af_sat.py, solver.py, preprocessing.py, and
scc_recursive.py are almost certainly identical to master, but this MUST be confirmed. Action
for coder: run `git diff master...HEAD --stat -- src/` before branching, and branch the CDAS
work off master as planned.

## 8. Risks and open questions for the coder

1. `_grow_preferred` may be load-bearing, not just an optimization. It's inside the
   correctness-tested loop. Removing it changes what gets fed to learn_witness_region. The
   coder must re-derive whether the paper's loop (no maximization, exclude the exact extended
   set) preserves the invariant checked by
   test_kernel_direct_skeptical_preferred_matches_native_oracle (test_solver_encoding.py:735).
   Do not assume it's a free deletion.
2. Strengthening learn_witness_region: the paper excludes the stored extended admissible set
   E; the current clause only forbids some outsider. Need to encode "exclude this exact seen
   extended set (and its subsets)" without over-pruning valid attackers. exclude_exact_
   extension (af_sat.py:287) exists on the kernel but the attacker solver has its own vars —
   a matching exclusion helper would be needed on _PreferredSkepticalAttackerSolver.
3. Two separate Z3 solvers (kernel vs attacker solver) don't share learned clauses. Fudge's
   incremental-SAT advantage assumes one incremental instance. Consider whether the attacker
   and extension queries should share a solver; today they don't (af_sat.py:727 kernel vs
   :741/1091 attacker solver).
4. SCC is not on the DS-PR path and the SCC layer explicitly excludes ideal/acceptance. If
   SCC decomposition is in scope for DS-PR, it needs a new acceptance-oriented entry point,
   not reuse of scc_recursive.py.
5. Grounded reduct is already applied — don't re-add it; verify no double-application when
   composing with any new preprocessing.
6. check() supports assumption literals but the path uses push/pop. If moving to
   assumption-based incremental solving (Fudge style), that's an architectural change
   touching every _run_extension/_admissible_extension caller.
7. Benchmark verification gap: could not run pytest or the harness (Bash blocked), so all run
   commands above are from source inspection only and should be smoke-tested.
