# ICCMA 2023 Stable-Preferred Shortcut Triage

Date: 2026-07-11

Status: dev-only Round 1 triage probe; candidate killed. No production solver
or evaluator code was changed, and the holdout artifact was not read or run.

Code baseline: `4782b7667886fbf7e15f62bf020dc4bdeea07bb6`
(`4782b76`, `main`, tracked files clean before the probe).

## Candidate and survival gate

Candidate: for flat ABA SE-PR single-extension, first obtain a stable extension
and return that exact witness as a preferred extension, skipping the current
preferred maximization path.

The candidate survived only if all four conditions held on development instance
`benchmarks/aba/aba_2000_0.3_10_10_1.aba`:

1. the framework was flat and automatic routing selected Clingo;
2. stable single-extension returned a witness within 2 seconds under a 5-second cap;
3. the independent preferred verifier accepted that exact witness;
4. current SE-PR entered work the successful stable-first path would skip.

## Exact commands

Live runner flags were confirmed before profiling:

```text
uv run tools/iccma2025_run_native.py --help
```

The help exposed `--profile-workers-dir`, `--profile-workers-format
{flamegraph,raw,speedscope,chrometrace}`, repeatable
`--profile-worker-subtrack`, repeatable `--only-instance`, repeatable
`--only-subtrack`, and `--jobs`.

Reusable direct-API probe:

```text
uv run scripts/probe_iccma2023_stable_preferred_shortcut.py
```

Real-worker profile of only the development SE-PR row:

```text
uv run tools/iccma2025_run_native.py --root data/iccma/2023 --backend auto --max-af-arguments -1 --max-aba-assumptions 1000000 --timeout-seconds 15 --only-instance benchmarks/aba/aba_2000_0.3_10_10_1.aba --only-subtrack SE-PR --jobs 1 --profile-workers-dir data/iccma/2023/profiles/round1-stable-preferred-triage --profile-workers-format raw --profile-worker-subtrack SE-PR --label round1-stable-preferred-triage-20260711 --no-progress
```

No full-frame command was run.

## Live probe values

Shape and route:

- assumptions: `600`
- rules: `7699`
- rule density: `12.83`
- flat: `True`
- `sparse_narrow_native_sat_shape`: `False`
- `large_dense_flat_aba_shape`: `False`
- automatic SE-ST route: `asp`
- automatic SE-PR route: `asp`

Stable single-extension, direct live API, 5-second Clingo solve cap:

- status: `success`
- elapsed: `0.834 s`
- extensions: `()`
- witness: `None`
- solver calls: `1`
- outer iterations: `0`
- inner iterations: `0`
- refinements: `0`

Here `success` means the stable query completed. It does **not** mean a stable
extension exists. The live result contained no extension and therefore no
witness. This corrects the scout premise that the baseline row's `solved`
status established stable existence: the ICCMA row can be solved by reporting
that no stable extension exists.

Independent preferred verification of the exact stable witness:

- witness present: `False`
- accepted as preferred: `False`

There was no witness to verify or return. The diagnostic fails closed with
`AssertionError: exact stable witness failed independent preferred verification`
after printing all four probe sections and the killed verdict.

Current preferred single-extension, direct live API, 15-second Clingo solve cap:

- status: `success`
- elapsed: `10.180 s`
- solver calls: `4`
- outer iterations: `1`
- inner iterations: `3`
- refinements: `3`

Thus current SE-PR does enter additional preferred-maximization work, but there
is no successful stable witness path that can skip it.

## Real-worker profile and comparison to N1

Harness result:

- status: `solved`
- elapsed: `11.074908 s`
- witness size: `350`
- solver calls / outer / inner / refinements: `4 / 1 / 3 / 3`
- raw profile:
  `data/iccma/2023/profiles/round1-stable-preferred-triage/aba-SE-PR-aba_2000_0.3_10_10_1.aba-17dd9f6098c7.raw.txt`

Dominant cost: `928` samples in `clingo.Control.solve` on the real worker stack
`enumerate_preferred -> _grow_to_maximal_not_deriving -> _solve_one ->
clingo.Control.solve`. Initial `_new_control` grounding had `27` samples and
program addition had `19`; refinement grounding had `3`.

N1's automatic stable baseline was likewise Clingo-solve bound (`302 / 384`
principal samples), while N1's forced SAT candidate moved to ranked-closure
construction (`391 / 399`) without reaching the Z3 solve. This probe does not
revive N1: the current SE-PR cost remains Clingo search inside preferred growth,
and the proposed stable shortcut has no witness to return.

## Verdict and next action

Verdict: **KILL**.

The framework is flat and Clingo-routed, and current SE-PR performs extra work,
but stable single-extension returns no witness. Consequently the independent
preferred verifier cannot accept an exact witness, so two required survival
conditions fail. No source experiment is authorized from this candidate.

Next action: return to Round 1 triage with seven probe slots remaining. Select a
candidate that targets Clingo search inside preferred growth. Do not pursue the
scout's assumption-batched-refinement runner-up from this evidence: grounding
was not dominant. Do not reroute this shape to the N1-dead SAT path, and do not
run the sealed holdout.

## Focused diagnostic checks

```text
uv run ruff check scripts/probe_iccma2023_stable_preferred_shortcut.py
```

Result: `All checks passed!`

```text
uv run pyright scripts/probe_iccma2023_stable_preferred_shortcut.py
```

Result: `0 errors, 0 warnings, 0 informations`.

```text
uv run pytest -q tests/structured/aba/test_aba.py::test_assumption_kernel_stable_returns_none_when_no_stable_extension_exists tests/structured/aba/test_aba_multishot.py::test_preferred_single_extension_uses_limited_multishot_witness tests/structured/aba/test_aba_multishot.py::test_stable_single_extension_avoids_full_multishot_enumeration tests/structured/aba/test_aba_multishot.py::test_enumerate_preferred_telemetry_iterates
```

Result: `4 passed in 0.45s`.
