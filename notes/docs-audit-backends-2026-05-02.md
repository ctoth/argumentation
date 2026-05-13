# docs/backends.md audit — 2026-05-02

Read-only scout audit of `docs/backends.md` against current code reality.
Cross-referenced with `notes/readme-sync-2026-05-02.md` (referred to below as
"readme-sync").

Truth sources read:
- `src/argumentation/backends.py` (50 lines total)
- `src/argumentation/solver_adapters/clingo.py`
- `src/argumentation/solver.py` (lines 1-100, 557-560)
- `src/argumentation/solver_adapters/iccma_aba.py` (lines 1-80)
- `src/argumentation/solver_adapters/iccma_af.py` (lines 1-80)
- `src/argumentation/aba_asp.py` (lines 1-189)
- `src/argumentation/aba_sat.py` (lines 1-60)
- `src/argumentation/af_sat.py` (lines 1-60)

## 1. Verified gaps

| doc-line | claim | code-reality | recommended-action |
|---|---|---|---|
| backends.md:6 | Signature `default_backend(semantics, theory_size, has_preferences, weakest_link)` | Matches backends.py:17-22; signature is positional in code but doc omits return type `-> str` | Add return type annotation in the documented signature for clarity |
| backends.md:9 | "Current rule:" | Rule body is verified correct against backends.py:23-33. PASS | none |
| backends.md:12-16 | Pseudocode rule with 4 branches ending in `materialized_reference` fallback | Verified line-by-line against backends.py:25-33. PASS | none |
| backends.md:13 | `if semantics == "grounded": asp` | backends.py:27-28 — note this branch fires regardless of `has_clingo()`; code does NOT check capability before returning `"asp"` | Document that grounded returns `"asp"` unconditionally (no `has_clingo()` guard); a caller with no clingo installed will receive a `SolverUnavailable` only at solve time |
| backends.md:14 | `if theory_size > 30 and has_clingo(): asp` | Verified backends.py:29-30. PASS | none |
| backends.md:15-16 | `if has_z3(): sat` else `materialized_reference` | Verified backends.py:31-33. PASS | none |
| backends.md:19-21 | `has_clingo()` accepts `clingo` on PATH or installed `clingo` package, "subprocess adapter invokes as `python -m clingo`" | backends.py:9-10 confirms PATH-or-package detection. clingo.py:295-304 (`_resolve_command`) confirms `[sys.executable, "-m", "clingo"]` fallback when binary == "clingo" and the Python package is importable | PASS |
| backends.md:23-24 | "Users can still pass an explicit `backend=` argument to the solver entry points" | Confirmed: `solve_aspic_with_backend` accepts `backend` (aspic_encoding.py:188); `aba_asp.run_aba_query` accepts `backend` (aba_asp.py:118, 131) | PASS — but the doc never names the entry points; see Section 2 |
| backends.md:24 | "selection helper is a policy function, not a forced dispatch layer" | True: nothing in solver.py imports `default_backend`; grep shows only tests and docs reference it | PASS |
| backends.md:29 | "Inspect `metadata[\"stdout\"]` or `metadata[\"stderr\"]` on backend failures" | Confirmed: aspic_encoding.py:244, 295, 355-357; aba_asp.py:169, 315-317 populate these keys. NOTE: `SolverProcessError` / `SolverProtocolError` (solver_results.py:31-32, 52-53) expose `stdout`/`stderr` as dataclass attributes, not `.metadata[...]`. For solver.py-style results the pattern is `result.stdout`, not `result.metadata["stdout"]` | Clarify which result type owns `metadata["stdout"]` (aba_asp / aspic_encoding) vs which exposes `.stdout` directly (solver_results dataclasses) |
| backends.md:31 | "run `uv run python -m clingo program.lp 0`" | Matches the subprocess invocation at clingo.py:113 (`[*command_prefix, str(path), "0"]`) when prefix is `python -m clingo`. PASS | none |

## 2. Undocumented backend surfaces that belong here

| surface | source | why it belongs here |
|---|---|---|
| `has_clingo()` / `has_z3()` capability detection | backends.py:9-14 | Doc names `has_clingo()` once (line 19) and `has_z3()` once (line 15) inside the rule, but never says they are public callable predicates importable from `argumentation.backends`. The `__all__` at backends.py:50 exports both |
| `backend_choice_reason(...)` | backends.py:36-47 | Returns a debug string with all inputs plus `has_clingo`/`has_z3` values; not mentioned at all in backends.md. This is the natural diagnostic counterpart to `default_backend(...)` and the doc's debugging section (lines 26-31) is the right place for it |
| Returned backend identifiers `"asp"`, `"sat"`, `"materialized_reference"` | backends.py:26, 28, 30, 32, 33 | Doc shows these in pseudocode but never lists them as the canonical set of strings consumers should compare against. Grep confirms `"materialized_reference"` is also produced by aspic_encoding.py:146 and accepted by aba_asp.py:118 |
| `"support_reference"` alias for ABA | aba_asp.py:118 | aba_asp accepts `{"support_reference", "materialized_reference"}` interchangeably as the reference path. Not in backends.py and not in backends.md; would surprise a user who only knows `default_backend`'s output set |
| Solver entry points that consume the backend choice | solver.py:138-360 (aba/dung/adf/setaf), aspic_encoding.py:188 (`solve_aspic_with_backend`), aba_asp.py:118+131 (`run_aba_query`) | Doc says "explicit `backend=` argument to the solver entry points" without naming any. Per readme-sync line 32, README itself does not name the `solver` module |
| `ICCMAConfig` / `SATConfig` | solver.py:60-74 | These dataclasses are how a caller passes binary/timeout to the ICCMA subprocess paths and trace sinks to the SAT path; they are the actual "explicit backend=" plumbing for the ICCMA/SAT cases. Backends.md does not mention them |
| ICCMA env vars (`ASPFORABA_SOLVER`, `ICCMA_AF_SOLVER`, `ICCMA_ABA_SOLVER`) | NOT FOUND in solver_adapters | Grep for `os.environ`, `os.getenv`, `getenv`, `environ[` across `src/argumentation/solver_adapters/` returned **zero hits**. The README claim cited in readme-sync line 35 ("README's mention of `ICCMA_ABA_SOLVER` and `ASPFORABA_SOLVER` env vars") does not appear to be backed by code. Backends.md should either omit env vars or document the actual binary-passing mechanism (`ICCMAConfig.binary`). Not verified whether vars are read elsewhere — flagging for confirmation |
| ASPFORABA backend status | solver.py:171-172, 220-221, 557-560 | `backend == "aspforaba"` branches return a hard `SolverUnavailable` with reason "ASPFORABA invocation contract is not configured". The doc never warns that this string is a recognized-but-unimplemented backend |
| Clingo subprocess parsing surface | clingo.py:22-23 (regexes), 80-151 (`run_extension_enumeration_protocol`), 154-210 (`run_aspic_grounded_protocol`), 213-292 (parsers) | Backends.md does not mention that the adapter parses `accepted_arg(...)` / `accepted_lit(...)` from clingo stdout, that protocol output is sorted deterministically (clingo.py:285-288), or that packaged `.lp` modules under `argumentation/encodings/` are concatenated with facts (clingo.py:307-312). All would help a "Debugging clingo programs" reader |
| ICCMA AF supported problems | iccma_af.py:55-71 (`SUPPORTED_AF_PROBLEMS`) | The doc never references the ICCMA subprocess adapter despite mentioning "explicit backend=". Names of the supported problem codes (`DC-CO`, `DC-ST`, `DC-SST`, `DC-STG`, `DS-PR`, `DS-ST`, `DS-SST`, `DS-STG`, `SE-PR`, `SE-ST`, `SE-SST`, `SE-STG`, `SE-ID`) belong somewhere; this doc is the natural home |
| ICCMA ABA supported problems | iccma_aba.py:35-44 (`SUPPORTED_ABA_PROBLEMS` = `DC-CO`, `DC-ST`, `DS-PR`, `DS-ST`, `SE-PR`, `SE-ST`) | Same reasoning |
| `af_sat.AfSatKernel` / `SATCheck` / `SATTraceSink` | af_sat.py:20-60 | The `"sat"` backend is mentioned in the rule but the doc never says (a) the SAT kernel uses Z3, (b) telemetry is available via `SATTraceSink`, (c) the kernel is incremental and reusable per AF |
| `aba_sat.support_extensions` / `support_acceptance` | aba_sat.py:9-65 | Pure-Python (no Z3) bitmask-based ABA support enumeration. Distinct from the `"sat"` backend choice which uses Z3 for AFs. Backends.md gives no hint that `"sat"` for AFs and ABA support solving are different code paths |

## 3. Code-example verification

backends.md contains two literal code blocks:

| block | content | verdict |
|---|---|---|
| backends.md:5-7 | `default_backend(semantics, theory_size, has_preferences, weakest_link)` | PASS — signature matches backends.py:17-22 exactly |
| backends.md:11-17 | Pseudocode rule body | PASS — line-by-line correspondence to backends.py:25-33 |
| backends.md:31 | `uv run python -m clingo program.lp 0` | PLAUSIBLE — matches clingo.py:113 invocation pattern (positional `0` for "all answer sets"). Not directly executed; the `uv run` prefix is project-specific and not verified against any pyproject script entry |

## 4. Citation/reference audit

Doc contains zero academic citations. No-op section.

The doc references one Python module (`argumentation.backends`, line 3) — verified at `src/argumentation/backends.py`.

## 5. Prose recommendations (severe only)

- Title/scope mismatch: file is titled "Backend Selection" but the only backend surface it actually documents is the `default_backend` policy function. A reader looking for "what backends exist, how do I install them, what does each do" will not find that here. Recommend retitle to `Backend Selection Policy` OR expand scope to cover the surfaces in Section 2.
- The `weakest_link` parameter (backends.md:12) is never explained. Code (backends.py:21, 25) and the test suite (`test_backend_selection.py:7`) treat it as a boolean flag indicating ASPIC+ weakest-link defeat. A reader of backends.md alone cannot infer what triggers this branch.
- The `has_preferences` parameter is in the signature (backends.md:6) but does not appear in the rule body (backends.md:11-16), and code at backends.py:24 has `del has_preferences` — i.e., it is currently unused. Doc should call this out so callers don't waste time tuning it.
- Debugging section (lines 26-31) jumps from "metadata stdout/stderr" to "reducer work" without defining "reducer". `reports/workstream-asp-backend.md` is the likely referent but not linked.

## 6. Cross-doc dependencies

- backends.md does not link to any other doc in `docs/`.
- No other doc in `docs/` references `backends.md` (grep `backends\.md|backends` across `docs/` returned only the self-reference at backends.md:3).
- Conceptual overlap: `docs/architecture.md` (not read in this audit) is the natural place for higher-level "what backends exist" prose; backends.md should probably link to it. Not verified.
- `reports/workstream-asp-backend.md:494-519` (not in `docs/` but in `reports/`) contains the original specification of the `default_backend` rule; backends.md is effectively the user-facing distillation of that report. No link between them.

## 7. Verdict

Backends.md is **technically accurate but severely under-scoped**. Every claim it makes is verifiable against `src/argumentation/backends.py`, but the doc covers ~10% of the backend surface area users actually need: it omits `has_clingo`/`has_z3` as public predicates, omits `backend_choice_reason`, omits the canonical backend-string set, omits all solver entry points and config dataclasses, omits the ICCMA/SAT adapter surfaces, and includes one `metadata["stdout"]` debugging tip whose locus (aba_asp / aspic_encoding vs solver_results) is ambiguous. A rewriter should treat the existing 32 lines as a verified core and expand around them.
