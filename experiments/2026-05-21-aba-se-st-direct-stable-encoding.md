# ABA SE-ST direct stable ASP encoding

Date: 2026-05-21

Branch: `exp/aba-se-st-direct-stable-encoding`

Workstream:
`notes/workstream-aba-se-st-direct-stable-encoding-2026-05-21.md`

## Hypothesis

The current `SE-ST` clingo route pays for the complete/admissibility
undefeated-derivation layer even though stable semantics only needs the common
choice/support/conflict-free module plus coverage of every out assumption by an
attack from in. A direct stable-only ASP program may reduce the grounded search
surface enough to solve at least one row from the exact five-row timeout
cohort, without invalid witnesses or 10x10 regression.

## Page-image semantics check

Read directly from page images, not extracted PDF text:

- `papers/Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/pngs/page-025.png`
- `papers/Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/pngs/page-026.png`

Page `025` shows Listing 1, module `pi_common`, with the input vocabulary and
core stable-compatible derivation surface:

- `assumption(X)` facts are guessed into `in(X)` or `out(X)`;
- `head(R,X)` and `body(R,X)` encode rules;
- `contrary(X,Y)` encodes that `Y` is the contrary of assumption `X`;
- `supported(X)` is derived from selected assumptions and triggered rules;
- `defeated(X)` is derived when a supported sentence is contrary to `X`;
- `:- in(X), defeated(X).` enforces conflict-freeness.

Page `026` states that stable semantics is `pi_common` conjoined with:

```prolog
:- out(X), not defeated(X).
```

The same page introduces `derived_from_undefeated`,
`triggered_by_undefeated`, and `attacked_by_undefeated` only for the
admissibility module `pi_adm`, and says complete semantics conjoins `pi_adm`
with an additional defended-out constraint. Those undefeated-derivation
predicates are not required for stable single-extension.

Decision from Phase 1: proceed with direct stable-only implementation.

## Source and test commits

- `541ccc5` `experiments/2026-05-21-aba-se-st-direct-stable-encoding.md`
  - recorded the page-image semantics gate before implementation.
- `a1e27a7` `tests/test_aba_multishot.py`,
  `tests/test_aba_sparse_narrow_route_contract.py`
  - added red contracts for the direct stable resource and
    `stable_encoding == "direct_stable"` metadata.
- `4b6ee26` `src/argumentation/encodings/aba_stable_direct.lp`,
  `src/argumentation/aba_incremental.py`, `src/argumentation/aba_asp.py`
  - added the direct stable-only ASP module;
  - changed stable multishot controls to load that module;
  - added stable metadata for multishot stable results.

## Cohort

Generated from the validated 10x10 run:

```powershell
jq '[.rows[] | select(.subtrack == "SE-ST" and .backend_results.auto.status == "timeout") | {year, track, subtrack, instance_kind, instance, arguments_or_atoms}]' data\iccma\2025\runs\direct-asp-auto-10x10-validated.json > data\iccma\2025\runs\aba-se-st-direct-stable-encoding-timeouts.json
```

Validation:

```powershell
jq 'length' data\iccma\2025\runs\aba-se-st-direct-stable-encoding-timeouts.json
jq '[.[] | .subtrack] | unique' data\iccma\2025\runs\aba-se-st-direct-stable-encoding-timeouts.json
```

Result:

- length: `5`
- subtracks: `["SE-ST"]`

Rows:

- `ABAs/abcgen_c7_atoms100_asms200_mra3_mbs2_cp0.9_ins1.aba`
- `ABAs/abcgen_c7_atoms200_asms200_mra3_mbs2_cp0.8_ins1.aba`
- `ABAs/abcgen_c7_atoms200_asms200_mra3_mbs2_cp0.8_ins2.aba`
- `ABAs/abcgen_c7_atoms200_asms200_mra3_mbs2_cp0.9_ins1.aba`
- `ABAs/abcgen_c7_atoms200_asms200_mra3_mbs2_cp0.9_ins2.aba`

## Verification

Red contract gate before implementation:

```powershell
uv run pytest tests\test_aba_multishot.py tests\test_aba_sparse_narrow_route_contract.py
```

Result: `2 failed, 1032 passed`.

Expected failures:

- missing `stable_encoding` metadata on the stable single-extension multishot
  result;
- missing `src/argumentation/encodings/aba_stable_direct.lp`.

Search gates after implementation:

```powershell
rg -n -F '_new_control(extra_program=":- out(X), not defeated(X).")' src tests
rg -n -F "derived_from_undefeated" src\argumentation\encodings\aba_stable_direct.lp
rg -n -F "triggered_by_undefeated" src\argumentation\encodings\aba_stable_direct.lp
rg -n -F "attacked_by_undefeated" src\argumentation\encodings\aba_stable_direct.lp
rg -n -F "stable_encoding" src tests
```

Result:

- old exact stable-witness construction: no results;
- direct stable forbidden undefeated predicates: no results;
- `stable_encoding`: intentional source/test locations only.

Focused gate after implementation:

```powershell
uv run pytest tests\test_aba_multishot.py tests\test_aba_sparse_narrow_route_contract.py
```

Result: `1034 passed in 113.73s`.

## Five-row metric

Command:

```powershell
uv run tools\aba_shape_benchmark.py --timeouts data\iccma\2025\runs\aba-se-st-direct-stable-encoding-timeouts.json --subtrack SE-ST --backend auto --timeout-seconds 40 --output-json data\iccma\2025\runs\aba-se-st-direct-stable-encoding-five-row.json --output-csv data\iccma\2025\runs\aba-se-st-direct-stable-encoding-five-row.csv
```

Result:

- solved: `0/5`
- timeout: `5/5`
- invalid witnesses: `0`
- runner errors: `0`
- each row timed out with reason `timeout>45.0`

Rows:

| Instance | Status | Reason | Validation |
| --- | --- | --- | --- |
| `ABAs/abcgen_c7_atoms100_asms200_mra3_mbs2_cp0.9_ins1.aba` | timeout | `timeout>45.0` | not checked |
| `ABAs/abcgen_c7_atoms200_asms200_mra3_mbs2_cp0.8_ins1.aba` | timeout | `timeout>45.0` | not checked |
| `ABAs/abcgen_c7_atoms200_asms200_mra3_mbs2_cp0.8_ins2.aba` | timeout | `timeout>45.0` | not checked |
| `ABAs/abcgen_c7_atoms200_asms200_mra3_mbs2_cp0.9_ins1.aba` | timeout | `timeout>45.0` | not checked |
| `ABAs/abcgen_c7_atoms200_asms200_mra3_mbs2_cp0.9_ins2.aba` | timeout | `timeout>45.0` | not checked |

The five-row metric gate failed. The direct stable-only encoding did not solve
any member of the timeout cohort and did not produce a measured deterministic
surface reduction naming a next deletion target.

## Failure analysis

Profile command on the direct-stable branch:

```powershell
uv run tools\aba_shape_benchmark.py --instance data\iccma\2025\extracted\instances\ABAs\abcgen_c7_atoms100_asms200_mra3_mbs2_cp0.9_ins1.aba --subtrack SE-ST --backend auto --timeout-seconds 35 --profile-dir data\iccma\2025\profiles\aba-se-st-direct-stable-encoding\small --profile-format raw --profile-duration-seconds 25 --output-json data\iccma\2025\runs\aba-se-st-direct-stable-encoding-profile-small.json --output-csv data\iccma\2025\runs\aba-se-st-direct-stable-encoding-profile-small.csv
```

Profile result:

- row status: `profiled`
- reason: `profile_duration_elapsed`
- elapsed: `24.820364300045185` seconds
- profile:
  `data/iccma/2025/profiles/aba-se-st-direct-stable-encoding/small/aba-SE-ST-auto-abcgen_c7_atoms100_asms200_mra3_mbs2_cp0.9_ins1.aba-4f3ede81e1a5.raw.txt`

Direct-stable hot frames:

- `solve_aba_single_extension -> _solve_asp_aba_single_extension -> solve_aba_with_backend -> _solve_multishot -> find_stable_extension -> _solve_one -> solve (clingo\control.py:1065) -> _c_call`: `2440` samples
- `find_stable_extension -> _new_stable_control -> add (clingo\control.py:320)`: `21` samples
- `find_stable_extension -> _new_stable_control -> ground (clingo\control.py:566)`: `16` samples
- encoding, simplification, parse, and resource loading: single-digit samples

Compared against the prior `pi_com` stable path from
`experiments/2026-05-20-aba-se-st-clingo-solver-shape.md` on the same row:

- old stable hot path in `clingo.Control.solve`: `2450` samples
- old add: `17` samples
- old ground: `9` samples
- old encoding: single-digit samples

Interpretation:

- the bottleneck did not move;
- direct stable did not shrink the observed `clingo.Control.solve` dominance;
- add/ground stayed tiny and slightly larger in the direct-stable profile;
- deleting the complete/admissibility undefeated layer changed the encoding
  surface, but not the hard search shape that matters for this row.

The direct-stable experiment is now a true diagnosed no-go rather than only a
promotion no-go.

Next target from evidence: a successful `SE-ST` experiment must change clingo's
search space/order more substantially than deleting the undefeated complete
layer. The next workstream should target a measured clingo search-shape
invariant, such as deterministic grounded/residual reduction, decomposition, or
a semantics-preserving constraint that changes the solve search profile before
the full benchmark gate.

## 10x10 regression metric

Not run. Phase 6 failed, and the workstream's metric-fail branch requires
abandoning the source delta and not promoting the direct stable route.

## Decision

No-go.

Abandon the direct stable source/test delta. Keep this experiment record as a
failed first-class result. The direct stable-only encoding is semantically
cleaner and passes focused correctness contracts, but it does not crack the
current five-row `SE-ST` timeout problem and does not move the profile out of
`clingo.Control.solve`.

Next architecture target: not clingo options, not SAT engine swapping, not
IPASIR callbacks, and not merely deleting the complete/admissibility layer. The
next experiment needs a stronger operational contract that changes the search
problem shape before full benchmark time.

## Generated diagnostics

Generated diagnostics are not committed:

- `data/iccma/2025/runs/aba-se-st-direct-stable-encoding-*.json`
- `data/iccma/2025/runs/aba-se-st-direct-stable-encoding-*.csv`

## Retroactive protocol audit

Protocol status: true diagnosed no-go.

The follow-up `py-spy` profile on the direct-stable branch shows the bottleneck
stayed in `clingo.Control.solve` with essentially the same sample count as the
old `pi_com` stable path. The experiment now explains why the metric failed:
the encoding deletion did not change the hard clingo search shape.

Required follow-up: choose an `SE-ST` experiment that changes a measured
clingo search-shape invariant before running the full benchmark gate.
