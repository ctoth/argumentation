# Paper Binary Tracking Cleanup - 2026-07-11

Target architecture:
- Scientific-paper PDFs and rendered page images remain local reading assets under `papers/` and are ignored by Git.
- Git tracks paper metadata and research notes, not generated binary reading artifacts.

Forbidden surfaces:
- Any tracked `*.pdf` or `*.png` file.

Slice boundary:
- The 13 page images introduced by `c4e216e6b029fc9052eea4537d9717f901bc2a2f`.

Search gates:
- `git ls-files "*.pdf" "*.png"` returns no paths.
- `git check-ignore` confirms every removed path remains ignored locally.

Runtime gates:
- `uv run pytest -q tests/structured/aba/test_aba_decomposed_prefsat_contract.py tests/structured/aba/test_aba_real_prefsat_contract.py tests/structured/aba/test_aba_native_cnf_prefsat.py tests/structured/aba/test_aba_sparse_narrow_route_contract.py`

## Iteration 1 - tracked paper page-image fixtures

Slice read:
- `.gitignore`
- `src/argumentation/structured/aba/aba_route_policy.py`
- `tests/structured/aba/test_aba_decomposed_prefsat_contract.py`
- `tests/structured/aba/test_aba_real_prefsat_contract.py`
- `tests/structured/aba/test_aba_native_cnf_prefsat.py`
- `tests/structured/aba/test_aba_sparse_narrow_route_contract.py`

Surfaces:
- 13 tracked PNG page images
  - Disposition: delete from the Git index; preserve locally.
  - Owner after cleanup: local `papers/**/pngs/` reading artifacts governed by `.gitignore`.
  - Action: `git rm --cached` on each exact path.
  - Evidence: current code and tests retain page paths only as provenance strings and do not read the binary files.

Gate results:
- Pass: `git ls-files "*.pdf" "*.png"` returned zero paths.
- Pass: all 13 removed paths still existed locally and `git check-ignore` matched each one.
- Pass: the four affected ABA contract files completed with `35 passed in 5.55s`.

Commit:
- `4fa36ce` records the fixed-point cleanup contract and gates.
- `c0d2732` removes the 13 page images from Git tracking while preserving the ignored local files.

Next slice:
- None. The requested binary-tracking scope reaches fixed point when the search and runtime gates pass.
