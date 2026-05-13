# README sync — orchestrator notes

Coordinator notes for the full-restructure README overhaul (Option B from the plan). Scout is writing the gap matrix to `notes/readme-sync-2026-05-02.md` — do not collide.

## 2026-05-02 — kickoff and Phase 1/2 dispatch

**State:** Plan locked, Option B (restructure with TOC + tldr + tiered table). Phases 1 and 2 in progress in parallel.

**Phase 1 (gap matrix):** Scout dispatched in background, agentId `a7f0ca0fbb4ef939e`. Output target `notes/readme-sync-2026-05-02.md`. Scout has the pre-flight observations baked into its prompt (extras drift, off-by-one strategy count, CLI non-goal contradiction, undocumented modules: aba_asp, aba_sat, af_sat, iccma_cli, backends, datalog_grounding, solver_results, solver_adapters).

**Phase 2 (install/ergo audit):** Started.
- `uv 0.8.8`, Python 3.13.5 — confirmed working.
- `uv sync` clean: 18 packages resolved/audited.
- Installed package metadata: `formal-argumentation 0.2.0`, editable, no runtime requires (matches `dependencies = []` in pyproject — README's "dependency-free kernel" claim holds for the core).
- `uv run pyright src` running in background (id `bt2efyal7`, log `out/pyright-readme-sync.log`).
- `uv run pytest -vv --timeout=60` running in background (id `b4fognwn1`, log `out/pytest-readme-sync.log`).

**What I know (verified):**
- pyproject extras: `z3`, `asp = clingo>=5.7`, `grounding = gunray (git)`. README documents only `[z3]`. README's install section is wrong/incomplete.
- `dependencies = []` at the core, so the "dependency-free kernel" framing survives — but only for the kernel, not for the full surface. README needs to clarify.
- `requires-python = ">=3.11"` matches README claim.
- PyPI distribution name confirmed `formal-argumentation` (matches README).
- `gunray` source: `git+https://github.com/ctoth/gunray.git` (uv source), not on PyPI. Install instructions for `[grounding]` will need a note about this — `uv add formal-argumentation[grounding]` will not resolve from PyPI alone.

**Blockers:** none. Waiting on scout (Phase 1).

**Pyright result (2026-05-02):** Clean. `0 errors, 0 warnings, 0 informations`. The non-zero exit code was a bogus `tee` failure (`out` is a 7.9 KB FILE not a directory — prior accident, not mine to clean). README's `Typing :: Typed` classifier and typed-package framing hold.

**Pytest result (2026-05-02):** `1 failed, 779 passed, 2 skipped in 61.79s`. The single failure is in `tests/test_epistemic_probability.py::test_any_probability_function_induces_valid_probability_labelling` — Hypothesis falsifying example: `induced_probability_labelling` produces a value outside `[0.0, 1.0]` when given a normalized distribution where mass concentrates on overlapping pairs (`{a,c}: 0.346, {b,c}: 0.448, {a,b,c}: 0.206`). The induced labelling for `c` exceeds 1.0. Pre-existing bug in `argumentation.epistemic`, not introduced by sync. Real bug — should be ticketed but is out of scope for README sync. README *Development* section currently says `uv run pytest -vv` implying it passes; this is now slightly false. Decision needed: flag known failure in README, or stay silent and fix the bug separately. Default = stay silent, file separate issue.

**`out/` gotcha:** `out` exists as a regular file in the repo root. Future logs should go to `notes/` or rely on the task-output files directly. Do not `mkdir out`.

**Phase 2 verdict:** complete.

Plan: when scout returns, synthesize gap matrix into Phase 3 structural draft.

## Existing docs the new README should link to (instead of duplicating)

`docs/` already contains:

- `architecture.md` — the kernel's overall architecture. New README's *Design* section can shrink and link here.
- `backends.md` — covers `argumentation.backends` (a module the current README does not mention at all — the doc page exists but the public-facing readme is silent on it).
- `gaps.md` — limitations and gaps (the *Non-goals* + *Approximate* discussion can defer here).
- `setaf.md` — SETAF semantics deep dive.
- `caf-semantics.md` — CAF deep dive.
- `iccma-data.md`, `iccma-2025-data.md` — benchmark data setup.

`CONTRIBUTING.md` exists at root. New README's *Development* section should link to it.

**Implication for Phase 3:** the new README can be shorter than 661 lines because the per-family deep dives belong in `docs/`. README's job is the elevator pitch, the surface-tier table, and runnable smoke examples per tier — not encyclopedia entries.

## 2026-05-02 — checkpoint after Phase 3a (docs audit swarm)

**State:** Phases 1, 2, 3, 3a complete. `[project.scripts]` entry added (Phase 9 task). Currently in Phase 4a (docs rewrites).

**Completed artifacts:**
- `notes/readme-sync-2026-05-02.md` — README gap matrix (scout) ✓
- `README.draft.md` — full restructured README (~430 lines, down from 661); examples verified for Dung quickstart, labelling, ranking (with .ranking, not .ordered_tiers), probabilistic, bipolar, ICCMA. ✓
- `pyproject.toml` — `[project.scripts]` entry added; `iccma-cli --help` works. ✓
- 7 doc audits at `notes/docs-audit-{name}-2026-05-02.md` ✓

**Verified env vars (resolves backends scout flag):**
`ASPFORABA_SOLVER`, `ICCMA_AF_SOLVER`, `ICCMA_ABA_SOLVER` are read at `tests/test_solver_adapters.py:565,829`. Backends scout grepped only `solver_adapters/` and missed the test layer. README's "used by smoke tests" wording is accurate.

**Per-doc rewrite plan (Phase 4a, doing self):**

1. `docs/architecture.md` — fix six→seven strategies; expand `solver_adapters` to subpackage with 3 adapters; add `af_sat`, `aba_asp`, `aba_sat`, `backends`, `datalog_grounding`, `solver_differential`, `solver_results`; reconcile CLI non-goal (now have `iccma-cli`); name `solver_capability_matrix` host module; tier-group the modules list; cross-link siblings; fix Cayrol 2010 / Caminada citations.

2. `docs/backends.md` — add `has_clingo()`/`has_z3()` as public predicates, `backend_choice_reason()`, canonical backend strings (`asp`/`sat`/`materialized_reference`/`support_reference`), name entry points (`solve_aspic_with_backend`, `run_aba_query`, `solver.solve_*`), `ICCMAConfig`/`SATConfig`, ICCMA AF/ABA supported problem codes, `aspforaba` recognized-but-unimplemented, document grounded branch returns "asp" without `has_clingo` guard, clarify `metadata["stdout"]` (aba_asp/aspic_encoding) vs `.stdout` (solver_results), document env vars at test layer.

3. `docs/gaps.md` — restructure: lead with "Currently-known limitations" (12 new items: PrAF treewidth zero-asymptotic, exact_dp grounded-only/defeat-only, ABA+ ASP not implemented, ASPIC+ ASP grounded-only, ASP last-link only, CQ5/6/11 only, brute-force enforcement, datalog NAP missing, dfquad alias raises, clingo subprocess only, accrual envelopes only, SAT extras need z3); demote closed-bug tables to appendix; absorb non-goals from architecture.md.

4. `docs/setaf.md` — add `semi_stable_extensions` and `stage_extensions` to semantics list; surface `SETAF`, `parse_aspartix_setaf`, `write_aspartix_setaf`, `admissible`, `characteristic_fn`, `range_of`, `attacks_argument`, `defends`, `conflict_free`; tighten "splitting paper" and "TU Wien" citations or drop; add one Python example.

5. `docs/caf-semantics.md` — replace "supported by the underlying package dispatcher" with the exact 8-literal list (grounded/complete/preferred/stable/semi-stable/stage/naive/cf2); name `extensions(caf, *, semantics, view)`, `CAFView` literal `"inherited"`/`"claim_level"`, `concurrence_holds`; add minimal example.

6. `docs/iccma-data.md` — add `extract` subcommand with example; document `data/iccma/<year>/{archives,extracted,manifests}/` layout; document `--root`, `--json`, strict-mode exit code, resumable .part downloads; cross-link iccma-2025-data.md; add 2023 Zenodo DOI.

7. `docs/iccma-2025-data.md` — fix Zenodo "DOI" wording (record ids, not DOIs); add `auto` backend, `--label`, `--no-progress`, `ICCMA_AF_SOLVER` fallback, `runs/` output layout, task matrix definitions; warn about `--max-aba-assumptions 0` silently disabling ABA.

**No blockers.** Proceeding to write rewrites sequentially.

## 2026-05-02 — Phase 4a progress checkpoint (6/7 docs done)

**Rewrites complete (verified-text):**
- `docs/caf-semantics.md` — 8-literal inherited list explicit, `extensions(...)` dispatcher named, `CAFView` literal documented, `concurrence_holds` added, runnable example added.
- `docs/setaf.md` — `semi_stable`/`stage` added to semantics list, full public API surfaced (`SETAF`, `parse_aspartix_setaf`, `write_aspartix_setaf`, `admissible`, `characteristic_fn`, `range_of`, `attacks_argument`, `defends`, `conflict_free`), Python example added, "splitting paper page images" replaced with proper citation form.
- `docs/backends.md` — capability detection (`has_clingo`, `has_z3`, `backend_choice_reason`) named as public; canonical backend-string table; entry points listed; ICCMA adapter table with supported problem codes; SAT vs aba_sat distinction; env var test-layer reading documented; debugging section split between `metadata["stdout"]` (aba_asp/aspic_encoding) and `.stdout` (solver_results).
- `docs/gaps.md` — restructured: 15 currently-known limitations leading section (L1-L15), Non-goals section absorbed, closed-bug tables demoted to appendix.
- `docs/iccma-data.md` — `extract` subcommand documented with example, `data/iccma/<year>/{archives,extracted,manifests}/` layout shown, `--root`/`--json`/strict-mode exit code/resumable .part downloads documented, 2023 Zenodo record id added, cross-link to iccma-2025-data.md and runner scripts.
- `docs/iccma-2025-data.md` — DOI vs Zenodo-record-id wording fixed, `auto` backend documented, `--label` and `--no-progress` documented, `ICCMA_AF_SOLVER` fallback noted, `runs/` output layout added, task matrix definitions with timeouts listed, `--max-aba-assumptions 0` warning added.

**Remaining:**
- `docs/architecture.md` — last and largest. Umbrella doc that links to everything. Will tier-group the modules list, fix six→seven strategies, expand `solver_adapters` to subpackage, add 7 undocumented modules, reconcile CLI non-goal, name `solver_capability_matrix` host, fix Cayrol 2010 / Caminada citations, add cross-doc "See also".

**After architecture.md:**
- Phase 5 verification gate — run every code block from README.draft.md + every code block from rewritten docs. Run pyright, pytest. Decide whether to swap README.md ← README.draft.md.
- Phase 6 commit.

**No blockers.**

## 2026-05-02 — Phase 5 verification progress

**Caught one real bug in own draft:** I had renamed `cayrol_2014_classify_grounded_argument_addition` → `cayrol_2010_...` in README.draft.md and architecture.md based on the citation reconcile (paper is JAIR 2010). The function name is the load-bearing identifier; only the *citation prose* needs reconciling. Reverted: function references use `cayrol_2014_...`, citation in prose says "cited to Cayrol et al. 2010, JAIR 38". Both files fixed.

**Verified runnable from rewritten artifacts:**

README.draft.md examples that ran clean:
- Dung quickstart (4-cycle), Labelling, Ranking, Probabilistic, Bipolar, ICCMA, ASPIC+, ASPIC encoding, AF revision (with cayrol_2014), generic semantics dispatch, SAT encoding, iccma-cli --help.

Doc examples that ran clean:
- caf-semantics.md `extensions(caf, semantics='preferred', view=...)`.
- setaf.md `SETAF` + all 6 semantics; ASPARTIX round-trip.
- backends.md `has_clingo`/`has_z3`/`default_backend`/`backend_choice_reason`.

**Remaining Phase 5 work:**
- Final pytest run (baseline was 779/782 with one pre-existing `epistemic` failure; need to confirm no NEW failures).
- Final pyright run (was clean before; doc changes don't touch src).
- Decide swap README.md ← README.draft.md, then commit.

## 2026-05-02 — Phase 5 caught test_docs_surface.py contract

Pytest after my doc rewrites: 777 pass, 2 skip, **3 fail** — 2 new failures introduced.

**The contract:** `tests/test_docs_surface.py` pins specific substrings that must appear verbatim in `README.md` AND `docs/architecture.md`. Required phrases include "not the full Popescu & Wallner I/O/U witness-table DP", "unsupported combinations return typed unavailable" (case-sensitive lowercase u for architecture; "unsupported task/semantics/backend combinations return typed unavailable" for README), "External callers supply already-projected frameworks", "does not own caller", "identity, storage, merge policy, provenance, or rendering policy".

**Fixes applied so far:**
- architecture.md — joined the broken-line "I/O/U witness-table DP" phrase; replaced "Unsupported task/semantics/backend combinations" with "unsupported combinations"; added "does not own caller identity, storage, merge policy, provenance, or rendering policy" to the External callers sentence. All 3 architecture pins now present.
- README.draft.md — added "not the full Popescu & Wallner I/O/U witness-table DP" to the `exact_dp` bullet.

**Still missing in README.draft.md:** "External callers supply already-projected frameworks", "does not own caller", "identity, storage, merge policy, provenance, or rendering policy". Solver surfaces section currently ends without the closing rationale paragraph.

**Next:** patch README.draft.md, rerun pytest (expect 779 pass, 1 fail = epistemic pre-existing), swap README.md ← README.draft.md, commit.

**Next concrete actions when scout returns:**
1. Read scout's notes file end-to-end.
2. Reconcile against my Phase 2 findings (extras, gunray-via-git note).
3. Begin Phase 3 draft at `README.draft.md`.
