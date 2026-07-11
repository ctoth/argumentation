# ICCMA 2023 SE-PR CEGAR Re-grounding Churn Triage

Date: 2026-07-11

Status: **Round 1 probe 4 triaged out; diagnosed negative.** Evidence-only
integration of the authorized hotspot proposal and the H3 semantic/profile
scouts. No production source slice was created, no solver or benchmark was
run, no new profile was captured, and the sealed holdout was neither read nor
run.

Code baseline: `main` at
`f701c2f19d7d8d6f770b233450c639c2786a7a14`, with clean tracked state before
integration. Unrelated untracked files were preserved.

## Candidate and survival gate

H3 as proposed in `reports/iccma-round1-hotspot-scout-20260711.md`: the two hard
development SE-PR rows are dominated by CEGAR grow-to-maximal re-grounding
churn, so batching or replacing permanent per-step refinements should remove
enough orchestration work to turn at least one 10-second timeout into a solved
row.

This is a campaign triage probe, not a full experiment-protocol run. The
proposal's cheapest falsification was to inspect the existing preferred-growth
telemetry and real-worker profile. H3 survives only if both conditions hold:

1. the completed hard-row telemetry shows enough inner iterations,
   refinements, or solver calls for repeated orchestration to be a plausible
   dominant cost; and
2. grounding/program-add/Python orchestration accounts for enough of the
   profile to clear the greater-than-1.074908-second (9.71%) reduction required
   to move the profiled row below the campaign's 10-second budget.

A short loop or a solve-dominated profile kills the stated mechanism before a
source experiment. Semantic exactness remains mandatory: any replacement must
return an independently valid preferred witness and retain an exact maximality
certificate rather than merely reduce public API calls.

## Evidence adjudicated

The campaign manager explicitly authorized the previously untracked H3
proposal as a premise and required it in this same evidence commit. The three
retained scout artifacts are:

- `reports/iccma-round1-hotspot-scout-20260711.md`;
- `reports/iccma-h3-cegar-semantic-scout-20260711.md`;
- `reports/iccma-h3-cegar-profile-scout-20260711.md`.

They were checked against the committed campaign frame and ledger, the
committed Round 1 probe-1 telemetry/profile record, and current source/tests.
The authoritative committed probe-1 evidence is
`experiments/2026-07-11-iccma2023-stable-preferred-triage.md`, introduced by
commit `2091a7d`. Its named raw JSON and py-spy files are generated diagnostics,
not blobs at this baseline; they were not used as a separate untracked premise.

Relevant current blobs at the adjudicated commit:

| Surface | Git blob |
|---|---|
| `experiments/2026-07-11-iccma2023-stable-preferred-triage.md` | `d152b83991953417ad05d750d5fc8aa6285855dd` |
| `src/argumentation/structured/aba/aba_incremental.py` | `1a41f08255db497c7fe6fc400a5f8ba3ff9477e9` |
| `tests/structured/aba/test_aba_multishot.py` | `47dd80b06c8889d93179b2772d54c82491ab1b3a` |
| `tests/structured/aba/test_aba_incremental_paper_properties.py` | `5bd6c89d75c6cae30d047e3ca398bae35b0809de` |
| `tests/structured/aba/test_aba_asp_differential.py` | `f7fdf814fe7f39222c55e28d9a27a545a75cafef` |
| `tests/structured/aba/test_aba_semantic_properties.py` | `7fc51cc67e2344416273e41f8fa0f15bc4606572` |

## Telemetry and profiler comparison

Probe 1's development-only real-worker diagnostic completed
`aba_2000_0.3_10_10_1.aba` / SE-PR in **11.074908 s**, returned an independently
valid preferred witness of size 350, and recorded:

| telemetry | value |
|---|---:|
| solver calls | 4 |
| outer iterations | 1 |
| inner iterations | 3 |
| refinement clauses | 3 |

The exact shape is therefore **4 / 1 / 3 / 3**. It is one seed solve followed
by a short strict-superset chain whose last inner solve proves that no strict
complete superset remains. Three refinement clauses represent two successful
growth steps and the final maximality proof; this is not high-count churn.

The committed real-worker py-spy accounting places **928 samples inside
`clingo.Control.solve` on the grow-to-maximal stack**, versus **3 samples in
refinement grounding**. Initial grounding accounts for 27 samples and initial
program addition for 19. The broader profile scout accounts for 1,043 total
samples, 968 of them in `Control.solve`; even an impossible removal of every
sample outside solve leaves an Amdahl estimate of about 10.28 seconds, still
over budget. Removing refinement grounding alone has a measured ceiling of
3/1,043 samples (0.29%, about 0.032 seconds).

Dominant cost before: Clingo search inside the individual inner preferred-growth
solve calls. Dominant cost after: unchanged by construction because there is no
source/config delta. The intended invariant did not show pathological loop or
re-ground counts, and the observed non-solve work cannot move the campaign
metric. A redundant profile would add no decision-changing evidence.

## Semantic exactness

Current `enumerate_preferred(limit=1)` first obtains a complete seed, then adds
`constr(out(I))` and solves under `in(I)` assumptions. The constraint blocks
the current candidate and its subsets; a satisfiable result is a strict
complete superset, while the final unsatisfiable result proves no such superset
exists. The returned complete set is therefore subset-maximal and preferred.

Current committed tests independently cover the exact boundary:

- refinement blocks exactly a candidate and its subsets;
- multishot preferred enumeration matches native and support-reference
  semantics over fixed and generated frameworks;
- preferred sets are maximal admissible sets;
- SE-PR single-extension requests one preferred witness; and
- concrete fixtures require multiple refinements and multiple outer
  iterations, so those operations cannot be erased generally.

Returning the first complete seed, stopping after a fixed number of growth
steps, treating stable nonexistence as preferred nonexistence, or returning a
heuristically large model would be semantically inexact. A one-shot optimizer
is admissible only if it proves global optimality: a maximum-cardinality
complete set is inclusion-maximal and hence preferred. One public solver call
is an operational signal, not proof of less internal search.

## Verdict and kill criteria

**KILL H3 as stated.** The causal premise is falsified: the loop is short,
refinement grounding is negligible, and the profile is dominated by the exact
Clingo solves needed to find strict supersets and certify maximality. Expected
primary-metric gain from a re-grounding/program-add/Python-churn-only change is
**0 newly solved rows**. No source experiment, benchmark, or new profile is
authorized from this candidate.

Revival requires new paired evidence that contradicts this profile and a
normally running operational contract added before a source slice. At minimum
that contract must preserve an independently checked preferred witness, expose
refinement-ground calls directly, and demonstrate a genuine reduction in both
hard solve calls and refinement grounds. A grounding-only reduction that
retains the four hard solves does not reopen H3.

Campaign kill-criterion accounting:

- Probe budget before this record: 3/8 used.
- This record consumes Round 1 probe 4: **4/8 used; 4 probes remain**.
- Full experiments: **0/3 used; 3 remain**.
- No candidate survives this probe.
- Budget is not exhausted, and Round 1 is still the first triage round.
- This evidence-only probe created no production source slice, so it does not
  advance the ledger's three-consecutive-source-slices criterion; the recorded
  N1/N2 count remains two.

No campaign kill criterion fires. Round 1 remains open.

## Next evidence-directed target

The next candidate is a separately framed **exact one-shot preferred-maximality
search** (for example, proved maximum-cardinality complete-set optimization),
not a revival of re-grounding churn. It must target the search performed inside
the inner Clingo solves and be preregistered with:

1. a normally running semantic contract proving every returned single witness
   is preferred against the independent native/support references, including
   no-stable, multi-refinement, and multiple-outer-iteration cases;
2. a deterministic operational contract that fails on the current 4/1/3/3
   shape and bounds the replacement's exact-maximality work, without equating
   a lower API-call count with a speedup; and
3. a paired two-development-row survival gate requiring an independently valid
   witness and at least one baseline timeout to become solved inside 10 seconds
   before any full-frame benchmark.

If no exact encoding and failing operational contract can be stated, do not
open the source slice. Generic Clingo configuration, the killed SAT route, and
grounding-only batching are excluded by the existing ledger evidence.

## Focused checks

```text
uv run pytest -q \
  tests/structured/aba/test_aba_incremental_paper_properties.py::test_lehtonen_p6_refinement_blocks_candidate_and_subsets \
  tests/structured/aba/test_aba_multishot.py::test_multishot_enumeration_matches_native_and_support_reference \
  tests/structured/aba/test_aba_multishot.py::test_preferred_single_extension_uses_limited_multishot_witness \
  tests/structured/aba/test_aba_multishot.py::test_cegar_loop_accumulates_refinement_clauses \
  tests/structured/aba/test_aba_multishot.py::test_cegar_loop_multiple_outer_iterations \
  tests/structured/aba/test_aba_multishot.py::test_enumerate_preferred_telemetry_iterates \
  tests/structured/aba/test_aba_asp_differential.py::test_aba_asp_matches_support_reference_on_generated_frameworks \
  tests/structured/aba/test_aba_semantic_properties.py::test_preferred_sets_are_maximal_admissible_sets
```

Result: **519 passed in 14.79 s**.

`git diff --check` was also run over the five-path integration diff before
commit and passed with no whitespace errors.

## Final accounting

- Production source slice: **none**.
- Solver/benchmark run: **none**.
- New/redundant profile: **none**.
- Sealed holdout access/run: **none**.
- Promotion/full experiment: **none**.
- Retained outcome: diagnosed negative triage evidence only.
