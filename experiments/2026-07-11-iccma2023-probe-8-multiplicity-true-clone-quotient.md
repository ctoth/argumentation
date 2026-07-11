# ICCMA 2023 Probe 8: Multiplicity-Aware True-Clone Quotienting for ABA SE-PR

Date: 2026-07-11

Status: **GATE A PASS; Gate B authorized but not started; Probe 8 not consumed**.

Preregistration base: `858c0cd2ad057301bb0ea05b970845ad9d149c48`

This record adopts the Probe 8 selector recommendation, corrected by fresh
adversarial review. It freezes exactly one family: multiplicity-aware
true-clone/module quotienting for ordinary flat ABA preferred semantics. The
semantic gate precedes every development-row access; shape telemetry makes no
wall-clock prediction; and a quotient state lifts to the complete preferred
family, never merely to one representative.

## Decision this probe can change

Probe 8 can answer only this question:

> Does an exact, independently certified true-clone quotient preserve the
> complete ABA preferred-extension family on bounded authorities, and do either
> of the two authorized SE-PR development rows contain a nontrivial certified
> fix-outside class that strictly reduces normalized rule templates?

A negative Gate A result kills the family without opening a development row or
consuming the probe. A negative Gate B result kills the family after consuming
Probe 8. Passing both gates is directional shape evidence only. It can authorize
one separately committed diagnostic solver slice under this record; it cannot
authorize a production route, encoding, full experiment, holdout access, or
promotion.

## Premise, novelty, and mechanism

Current source and history inventory found no multiplicity-aware ABA preferred
quotient implementation after `0d03790`; the later work covers SCC
conditioning, cutsets, and a direct CaDiCaL candidate. This is therefore a
novel campaign family rather than a retry of a recorded quotient experiment.

The cautious mechanism hypothesis is that an exact quotient may reduce
symmetric choices encountered during Clingo's preferred/maximality search. The
committed profile places 928 samples in `clingo.Control.solve` and only three in
refinement grounding, so a search-space change is relevant. That profile does
**not** prove symmetry is the cause of the Clingo cost, and shape reduction does
not predict a wall-clock speedup.

This family does not overlap with SCC/decomposition, small backdoor/cutset
conditioning, support enumeration or extraction, solver configuration or
portfolio selection, or routing. No result may be credited to any of those
mechanisms.

## Frozen normalized framework and exact class authority

The input is an ordinary flat ABA framework represented as a deterministic
colored incidence hypergraph with literal nodes colored as assumption or
non-assumption and with separate rule nodes, together with colored contrary,
rule-head, and rule-body-membership incidences. Normalization preserves distinct
rule nodes and therefore rule multiplicity, factual rules, exact body
membership, and all literal identities. No support family is computed or
embedded.

A candidate quotient class contains assumptions only. For every distinct pair
`a,b` in a class, the transposition exchanging `a` and `b` and fixing every
node outside that class must be independently verified as an automorphism of
the **complete** normalized framework. The full node colors and every normalized
incidence must be preserved. The verifier consumes only the serialized complete
hypergraph and proposed transposition, not the class finder's signatures or
conclusion. This independently verified full-framework automorphism is the sole
authority for class membership.

Color equality, equal local degree/signature, matching attacker counts, or an
automorphism that also moves an outside node is insufficient. In particular,
two assumptions whose matching depends on exchanging separate A/B attacker,
literal, or rule nodes are entangled coupled classes and must be rejected. A
class is nontrivial only when its size is at least two and every required
fix-outside transposition is certified.

Each certified class of size `m` is represented by an exact multiplicity
`k in {0,...,m}`. Singleton assumptions remain explicit Boolean choices.
Normalized quotient rule templates retain exact multiplicity and enough
incidence provenance to reconstruct and verify the original rule multiset.

## Frozen family lift and separate witness selection

The **family lift** of one quotient state is its full orbit expansion: for each
certified class of size `m` with quotient multiplicity `k`, enumerate every
size-`k` subset of that class; combine those choices across all classes and with
the state's explicit singleton choices. The lift of a quotient result family is
the set union of those expansions, deduplicated only by exact assumption-set
identity.

This full expansion must equal the complete preferred-extension family from
both independent authorities:

1. `native_aba.preferred_extensions`; and
2. `support_extensions(..., preferred)`.

A **canonical witness selector** is a separate, later solver-output operation:
after full-family correctness has been established, it may choose the
lexicographically least lifted preferred extension from a quotient result when
SE-PR needs one witness. It is never the family lift and cannot be used in Gate
A family equality.

Changing the class definition, permitting an outside-moving automorphism,
choosing a single representative as the lift, or weakening complete-family
equality invalidates this preregistration rather than tuning the family.

## Gate A: free bounded semantic contract before any development row

Gate A is a separate committed semantic-contract slice. It must be committed
before Gate B implementation or any access to either permitted ICCMA row. It
must not read any campaign development or holdout instance.

Exact command:

```powershell
uv run pytest -q `
  tests/structured/aba/test_aba_preferred_true_clone_quotient_contract.py `
  --timeout=60
```

The contract runs fail-closed under a 60-second outer cap and 512 MiB process
cap. A timeout, memory breach, exception, incomplete authority result, or
unparseable result is a semantic kill, not an invitation to retry.

### Twelve named fixtures

The fixture set is exactly these twelve named frameworks:

1. `true_clone_size2_complete_family`
2. `true_clone_size3_complete_family`
3. `true_clone_size3_partial_k1`
4. `true_clone_size3_partial_k2`
5. `conjunctive_support_true_clones`
6. `factual_attacker_true_clones`
7. `mutual_and_self_attack_true_clones`
8. `no_stable_but_preferred_true_clones`
9. `near_clone_distinct_contrary_rejected`
10. `near_clone_rule_signature_rejected`
11. `entangled_ab_attacker_matching_rejected`
12. `multi_class_orbit_expansion_no_loss_or_duplicate`

Fixture 10 contains named subcases differing by exactly one rule head, one body
membership, and one factual rule. Across the suite, size-2 and size-3 classes,
conjunctive support, factual attackers, mutual attack, self-attack, the absence
of a stable extension, and nontrivial partial multiplicities `0 < k < m` are
exercised. Fixture 11 must prove that matching A/B attackers requiring coupled
outside swaps do not form a class.

### Fixed generated population

In addition to the twelve fixtures, Gate A checks **exactly 300** ordinary flat
ABA frameworks generated with fixed seed **`2026071108`**. Each generated
framework has at most eight assumptions and at most sixteen rules. The seed,
ordered framework index, normalized framework hash, assumption/rule counts,
certified classes, and authority-family sizes must be emitted for reproduction.

For every fixture and every generated framework, the independently verified
class certificates are checked against the complete normalized framework, and
the fully expanded quotient preferred family must equal the complete family
returned by each authority separately. Equality includes empty/nonempty family
status and exact assumption sets; no extension may be lost, invented, or
duplicated. At least one checked result must exercise a nontrivial `0 < k < m`
lift.

Any authority disagreement, invalid or missing transposition certificate,
acceptance of an entangled or near-clone class, duplicate/lost extension,
failure to execute partial multiplicity, population-count mismatch, timeout,
or resource-cap breach is a **semantic kill**. Gate B remains closed, no dev row
is opened, and budget remains 6/8. The Gate A implementation and result must be
committed before any next slice.

### Gate A result — PASS

Gate A was implemented test-first as one diagnostic/reference/test/record
slice. The first exact focused invocation was red at collection with
`ModuleNotFoundError: No module named
'scripts.aba_true_clone_quotient_reference'`. No reference implementation
existed at that point.

The bounded reference now:

- rejects more than eight assumptions, sixteen rules, 32 total literals,
  body width above eight, more than 256 concrete subsets, or more than 256
  quotient states before exhaustive semantic reasoning;
- serializes every assumption/non-assumption literal node and every distinct
  rule node, with separate contrary, head, body-membership, and factual-rule
  incidences;
- verifies each proposed assumption transposition from that serialization
  alone, exchanging only the two assumption nodes and fixing all other
  literal/rule nodes;
- accepts a nontrivial class only after every within-class pair has such a
  certificate;
- independently enumerates concrete admissibility and quotient-state
  maximality without calling either comparison authority to construct the
  result;
- expands each state to the Cartesian product of every exact-size class
  subset and explicit singleton selection, then unions complete preferred
  orbits with an overlap check; and
- keeps the canonical witness selector as a separate post-family operation.

The test module contains exactly the twelve frozen top-level fixture names.
It certifies nonvacuous size-2 and size-3 classes, explicitly expands `k=1`
and `k=2` size-3 orbits, and covers conjunctive support, factual attack,
mutual and self attack, no-stable/preferred behavior, distinct-contrary and
head/body/factual-rule near clones, attacker-matched entangled A/B symmetry,
and two simultaneous classes without loss or duplication. The fixed-seed
Hypothesis contract uses seed `2026071108`, `max_examples=300`,
`deadline=None`, no example database, and generation-only phases. Every
example emits its ordered index, normalized SHA-256, assumption/rule counts,
certified classes, and all three family sizes as deterministic JSON in pytest
capture. All generated frameworks are ordinary flat ABA and remain within the
frozen eight-assumption/sixteen-rule maxima.

The exact Gate A command runs under a reversible hard 512 MiB process-memory
limit (Windows Job Object in this environment) and the frozen 60-second pytest
timeout. Final result:

```text
15 passed in 22.16s
```

Relevant existing semantic gates also passed:

```text
uv run pytest -q tests/structured/aba/test_aba_semantic_properties.py tests/structured/aba/test_aba_scc_composition_contract.py --timeout=60
24 passed in 3.40s

uv run pytest -q tests/structured/aba/test_aba_backdoor_cutset_contract.py --timeout=90
15 passed in 61.76s
```

An initial combined existing-gate run added a 60-second per-test timeout and
timed out only in Probe 6's 300-example native preferred enumeration after 38
passing tests. It produced no assertion or semantic counterexample. The
isolated Probe 6 rerun used modest observed-runtime slack and passed unchanged.

Verdict: **GATE A PASS**. Gate B is authorized only after this complete slice
is committed. No ICCMA row or corpus file was opened, no solver or benchmark
was run, no production source/routing/encoding was changed, and no holdout was
touched. Usage remains exactly **6 / 8 triage probes** and **0 / 3 full
experiments**; Probe 8 remains **not consumed**.

## Gate B: consumed shape-only probe on two development rows

Gate B may begin only from a committed passing Gate A. First access to either
authorized row consumes Probe 8 immediately and changes usage to **7 / 8 triage
probes; 0 / 3 full experiments**, regardless of the result.

Only these development SE-PR rows are permitted:

1. `data/iccma/2023/extracted/instances/benchmarks/aba/aba_2000_0.3_10_10_0.aba`
   — 600 assumptions and 7,867 rules.
2. `data/iccma/2023/extracted/instances/benchmarks/aba/aba_2000_0.3_10_10_1.aba`
   — 600 assumptions and 7,699 rules; the recorded diagnostic completed in
   11.074908 seconds with a 350-assumption preferred witness.

No other development row, full population, SE-ST row, guard row, or holdout row
may be opened.

Gate B constructs only the normalized colored incidence hypergraph. It applies
deterministic color refinement as a candidate partition, then checks every
required within-class transposition against the complete normalized framework.
The per-transposition fix-outside automorphism verification is the sole class
authority. Color refinement may reject candidates cheaply but may never certify
a class.

Gate B performs no solver call, Clingo grounding/solve, preferred computation,
support enumeration, support extraction, or benchmark timing. Each row has a
5-second and 512 MiB process cap; one 15-second outer cap covers both rows. Any
timeout, memory breach, crash, missing field, or ambiguous certificate fails
closed with no retry.

For each row, the committed result must report:

- exact path/hash and original assumption/rule counts;
- every certified class and each per-transposition certificate;
- certified class count and largest certified class;
- exact raw original state count `2^n`;
- exact raw collapsed-state count
  `2^s * product(m_i + 1)`, where `s` is the singleton count;
- exact unceiled symmetric decision reduction
  `n - log2(collapsed_state_count)`, including the positive
  `2 - log2(3)` credit for every size-2 class;
- normalized original and quotient rule-template counts; and
- rule-template reconstruction/multiplicity certificates.

No ceiling is applied to the decision reduction. The selector's former
effective-bit threshold and 20%-to-9.7% wall-clock inference are not retained.
Shape telemetry predicts **no speedup** and is not time calibration.

**Shape survival requires, on at least one permitted row, both:**

1. at least one nontrivial certified fix-outside class; and
2. quotient rule-template count strictly less than the normalized original
   rule-template count.

Anything else kills the family. Larger reduction percentages may be reported
only as exploratory, nonpredictive floors; they cannot substitute for or be
interpreted as a wall-clock threshold.

## Conditional diagnostic solver slice

Only if committed Gate A and Gate B results both pass may a separately committed
diagnostic solver slice run. It uses exactly one of the two permitted rows: the
row with the greatest unceiled symmetric decision reduction, breaking ties by
the greatest strict rule-template decrease and then lexicographically by path.

Single variable: current Clingo SE-PR control versus the same Clingo
version/configuration operating on the exact certified multiplicity quotient.
There is no solver/configuration sweep, alternate backend, support extraction,
portfolio, route, production encoding, or fallback.

- jobs: `1`;
- internal cap: 9 seconds;
- outer process cap: 10 seconds;
- first run the quotient candidate once (`Q0`);
- if `Q0` does not return a semantically authorized preferred witness in
  `< 9.0 s`, stop;
- otherwise run exactly `B1,Q1,B2,Q2,B3,Q3`, without retry, extra row, changed
  order, or remembered control substitution.

The canonical witness selector may format the returned SE-PR witness only after
the quotient result has been fully expanded and checked against the frozen
authorities. All class, quotient-template, and lift certificates must remain
identical to the passing gates.

Diagnostic survival requires every `Q1..Q3` to return an authorized preferred
witness in `< 9.0 s`, quotient median `<= 8.0 s`, every `B1..B3` to time out at
the 9-second internal cap, and every semantic/shape identity to remain fixed.
This is triage evidence only.

On any consumed-probe miss, status is initially
`promotion no-go; diagnosis incomplete`. Attach `py-spy` to the real control
and quotient workers/processes, not merely a wrapper, and record the paired
profiles, dominant cost before/after, whether the intended search invariant
moved, shrank, or stayed unchanged, and the next target justified by that
evidence. Wall time alone cannot complete the diagnosis.

## Kill, campaign, and promotion boundaries

At this preregistration commit, usage remains exactly **6 / 8 triage probes**
and **0 / 3 full experiments**. Probe 8 is preregistered and **not consumed**.
Gate A is free; Gate B consumes Probe 8 on first permitted-row access.

Campaign kill has not fired yet. This is the last selected quotient family.
Failure at any frozen semantic, shape, or diagnostic boundary ends this family
and the campaign proceeds to its required final synthesis; it does not redefine
classes or lift, relax a cap/threshold, retry a row, widen to another quotient
family, or revive SCC/backdoor/support/portfolio work.

Even a positive diagnostic cannot change production. Before any production
route or encoding change, a later full experiment must be separately
preregistered with a committed baseline, sealed evaluator, fast contracts,
instrumentation, paired analysis, minimum meaningful effect of at least +1
solved dev row, failure-analysis gate, and independent promotion verifier. Only
that later verifier may access the holdout or promote a source delta.

## Inputs and provenance

- Selector recommendation:
  `C:\Users\Q\AppData\Local\Temp\iccma-candidate8-selector-20260711.txt`
- Novelty inventory:
  `reports/iccma-history-sepr-inventory-20260711.md`
- Bottleneck record:
  `experiments/2026-07-11-iccma2023-cegar-regrounding-churn-triage.md`
- Campaign ledger and sealed populations: `experiments/INDEX.md` and
  `experiments/iccma2023-frame/`

No test, script, source, row, solver, benchmark, probe, or holdout was opened or
run while writing this records-only preregistration.
