# ICCMA 2023 probe 6 ABA backdoor semantic contract

Date: 2026-07-11

Repository base: `4a355691ec43d46a8d4251e16d4f6a9917a2702cb`

Status: **SEMANTIC KILL. OPERATIONAL WORK IS UNAUTHORIZED.**

No production `src/` path, solver, SAT/ASP/Z3 authority, ICCMA row, holdout,
benchmark, profile, timing metric, or operational shape measurement was used.

## Frozen contract implemented

`scripts/aba_backdoor_cutset_reference.py` is a bounded diagnostic/reference,
not a route. Before exhaustive reasoning it enforces the frozen domain of
`0..5` assumptions, at most `4` non-assumption literals, at most `8` rules,
rule-body width at most `3`, and cutsets of size at most
`min(3, |A'|)`. It independently implements:

- least factual closure and removal of fact-attacked assumptions;
- normalized compact literal/rule-factor/contrary incidence components;
- deterministic enumeration of every qualifying empty and nonempty assumption
  cutset;
- fail-closed exact collective-attack ownership;
- selected/rejected cut assignments, exact per-component attacked-cut
  signatures, their global union, and cut-defense obligations;
- independent exhaustive local admissible enumeration under each fixed state;
- canonical lift and deduplication followed by one global strict-inclusion
  maximality filter.

Conditioned results are produced only by that bounded reference. The current
direct native authority and independent support-mask authority are comparison
oracles; neither is used as a fallback to create a conditioned result.

## Red then green

The complete focused test module was added first. Its first run failed during
collection because `scripts.aba_backdoor_cutset_reference` did not exist. After
the reference was implemented, the fixed-seed focused gate passed.

The final focused module contains `15` collected tests: the ten frozen named
fixtures, three explicit fail-closed/path tests, the adversarial fixed-`k`
rejection, and one Hypothesis property with exactly `300` deterministic
examples and `deadline=None`. For every generated framework it enumerates every
qualifying `K` with `|K| <= min(3, |A'|)` and compares the complete conditioned
admissible family in both directions with independent exhaustive admissibility,
the direct native predicate, and the support-mask predicate. It compares the
globally maximal family in both directions with both current preferred-family
authorities.

## Exact named-path totals

Across the nine composable named fixtures, the recorded path totals are:

| Path | Count |
|---|---:|
| factual normalizations | 1 |
| qualifying `K=empty` cutsets | 4 |
| qualifying nonempty cutsets | 5 |
| selected cut states | 5 |
| rejected cut states | 5 |
| nonempty attacked-cut signatures | 4 |
| cut-defense obligations created | 2 |
| cut-defense obligations discharged | 1 |
| inactive collective tails | 20 |
| activated collective tails | 10 |
| independently enumerated residual components | 16 |
| canonical deduplication passes | 9 |
| duplicate lifts removed | 0 |
| incomparable preferred maxima | 2 |

The diagnostic separately proves cap overflow, ambiguous ownership, missing
path coverage, and support-oracle disagreement fail closed. Unhandled
exceptions propagate as failure; there is no fallback path.

## Semantic kill

The literal frozen fixture `two_component_cut_attack_union` is:

```text
{a} -> k
{b} -> k
K = {k}
```

In stored-rule form, both attacks require rule factors with the same head
literal `contrary(k)`. After deleting the assumption vertex `k`, both rule
factors remain connected through that shared literal. Their body assumptions
`a` and `b` therefore remain in **one** assumption-bearing residual component.
`K={k}` is not a separator under the adjudication's frozen compact
rule/contrary factor-incidence definition.

The contract rejects this fixture with `NonSeparatorError`; it does not silently
compose it, rename its components, or substitute a different two-target
fixture. Consequently the frozen requirement that this named fixture exercise
two independent residual attacked-`K` contributions and lift deduplication is
unsatisfiable. The complete frozen semantic gate does not pass even though all
nine actually qualifying named fixtures and all 300 generated examples agree
with both authorities.

The bounded adversarial family is also explicitly rejected at `K={x}` as a
non-separator, as required. This kill is not a hard-row or operational result.

## Verification

```text
uv run pytest -q --hypothesis-seed=6006 tests/structured/aba/test_aba_backdoor_cutset_contract.py
15 passed; 300 deterministic Hypothesis examples; deadline=None

uv run pytest -q tests/structured/aba/test_aba_scc_composition_contract.py tests/structured/aba/test_aba_decomposed_prefsat_contract.py tests/structured/aba/test_aba_semantic_properties.py
32 passed

uv run ruff format scripts/aba_backdoor_cutset_reference.py tests/structured/aba/test_aba_backdoor_cutset_contract.py
2 files left unchanged after the initial formatting pass

uv run ruff check scripts/aba_backdoor_cutset_reference.py tests/structured/aba/test_aba_backdoor_cutset_contract.py
All checks passed

uv run pyright scripts/aba_backdoor_cutset_reference.py tests/structured/aba/test_aba_backdoor_cutset_contract.py
0 errors, 0 warnings, 0 informations
```

## Verdict and authorization

Verdict: **semantic kill**. Probe usage becomes **6 / 8 triage probes** and
full-experiment usage remains **0 / 3**.

The later support-free operational contract is not preregistered or authorized,
because the adjudication authorized it only after a complete semantic pass.
The only allowed next action is campaign-level correction or replacement of the
inconsistent frozen fixture/theorem package, or selection of the next inventory
candidate. No operational telemetry, production route, solver probe, benchmark,
hard row, or holdout action may follow from this record.
