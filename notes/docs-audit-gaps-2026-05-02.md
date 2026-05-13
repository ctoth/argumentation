# docs/gaps.md audit — 2026-05-02

Scout audit of `docs/gaps.md` against current code reality. Read-only.
Cap: 300 lines. All citations are absolute file paths with 1-based lines.

## 0. Audit-target framing

`docs/gaps.md` (38 lines) is structurally a **closed-bug changelog**, not
a "currently-known-limitations" doc. It contains three closed-gap tables
(WS-O-arg-aba-adf at 3-12, WS-O-arg at 14-28, WS-O-arg-vaf-completion at
30-37) and one short open-limitation sentence at line 12 (non-flat ABA).
This shape governs every finding below.

## 1. Verified gaps — line-by-line

| gaps.md line | Claim | Code reality | Action |
|---|---|---|---|
| 7 | ADF kernel present (`adf.py`) | `src/argumentation/adf.py:37-44` defines abstract `AcceptanceCondition` with `NotImplementedError` stubs; concrete `Atom`, `_Not` etc. at `adf.py:47+` override. Kernel exists. | still-true / closed |
| 8 | flat ABA kernel present (`aba.py`) | `src/argumentation/aba.py:27` `NotFlatABAError`; `aba.py:62` raise on non-flat; `aba.py:73` `ABAPlusFramework`; exported at `aba.py:368-370` | still-true / closed |
| 9-10 | foundational ADF/ABA kernels in package | confirmed by row 7-8 evidence | still-true / closed |
| 12 | "Non-flat ABA remains out of scope...`NotFlatABAError`" | `src/argumentation/aba.py:27,62` exact match | still-true (only live open gap) |
| 19 | ASPIC literal IDs sanitised for ASP | `src/argumentation/aspic_encoding.py:1-58` shows encoding surface; readme-sync line 17 confirmed. | still-true / closed |
| 20 | duplicate defeasible rule names rejected | `src/argumentation/aspic_encoding.py` — module exists; specific test pins, per readme-sync. | still-true / closed |
| 21-22 | AF revision Bugs 4 & 5 fixed | `src/argumentation/af_revision.py:22-29,314,335` cited by readme-sync rows 14, 52 | still-true / closed |
| 23 | `strictly_weaker(non-empty,empty)` lifting | `src/argumentation/preference.py` (per readme-sync) | still-true / closed |
| 24 | partial-AF skeptical distinguishes necessary/possible | `src/argumentation/semantics.py` | still-true / closed |
| 25 | MC z-score continuous values | `src/argumentation/probabilistic.py:42-49` `_z_for_confidence` Acklam fallback | still-true / closed |
| 28 | Bug 1 stale-premise note | meta-statement about workstream history | still-true (informational) |
| 34-37 | VAF Bench-Capon helpers | `src/argumentation/vaf_completion.py` per gaps.md table | not directly re-verified; closed status acceptable |

## 2. New limitations the code surfaces but `gaps.md` does NOT mention

| # | Limitation | Source citation |
|---|---|---|
| N1 | Tree-decomposition DP for PrAF: zero asymptotic improvement over brute-force; effective only for treewidth <=~15 | `src/argumentation/probabilistic_treedecomp.py:7-17` (module docstring), repeated at `:1135-1137` |
| N2 | `exact_dp` accepts only grounded semantics, defeat-only PrAFs (no supports, attacks==defeats) | `src/argumentation/probabilistic_treedecomp.py:32-43` `supports_exact_dp` |
| N3 | ABA+ ASP backend not implemented; returns `unavailable_backend` | `src/argumentation/aba_asp.py:97-106` (`reason="ABA+ ASP backend is not implemented"`) |
| N4 | ASPIC+ clingo backend supports grounded only | `notes/workstream-asp-backend-2026-05-01.md:22-24` (verified-by-scout statement; backend returns `unavailable_backend` for non-grounded) |
| N5 | ASP backend covers only last-link preference lifting; weakest-link not covered | `notes/workstream-asp-backend-2026-05-01.md:69-71`; `PreferenceConfig` itself supports both |
| N6 | `practical_reasoning.critical_question_objections` only implements CQ5, CQ6, CQ11; raises `NotImplementedError` for any other Atkinson critical question | `src/argumentation/practical_reasoning.py:139-145` |
| N7 | `enforcement.py` is a brute-force reference oracle, **not** Baumann-style expansion enforcement; may add/remove edges and arguments | `src/argumentation/enforcement.py:1-12` (module docstring) |
| N8 | `datalog_grounding` consumes Gunray's conservative DeLP-compatible inspect_grounding only — Diller 2025 Definition 12 NAP analysis is NOT implemented anywhere | `notes/workstream-datalog-grounding-2026-05-01.md:22`; `src/argumentation/datalog_grounding.py:1-7` cites Gunray as the consumer |
| N9 | Probabilistic strategy alias `dfquad` is accepted by `_ALLOWED_STRATEGIES` but raises downstream | `src/argumentation/probabilistic.py:25-39`; cross-ref `notes/readme-sync-2026-05-02.md:11` |
| N10 | Clingo invoked as subprocess binary, not via the `clingo` python package | `notes/workstream-asp-backend-2026-05-01.md:24-27` |
| N11 | `accrual.py` envelopes give only strong/weak applicability per Prakken 2019; no enumeration of subset accruals, no comparator over accruals | `src/argumentation/accrual.py:20-92` |
| N12 | `aba_sat` / `af_sat` SAT paths are optional (require z3 extra); not advertised as a limitation in gaps.md | `src/argumentation/aba_sat.py:1`, `src/argumentation/af_sat.py:1` (per readme-sync rows 27-28) |

## 3. Closed gaps the doc still lists as open

None. `gaps.md` lists no currently-open gap other than non-flat ABA
(line 12), which is verified still open at `aba.py:27,62`.

## 4. Cross-references with `notes/workstream-*.md`

| Workstream note | gaps.md alignment | Open question for rewriter |
|---|---|---|
| `notes/workstream-asp-backend-2026-05-01.md` (lines 1-107) | Designs preferential ABA / ABA+ / ASPIC+ ASP backend per Lehtonen 2020/2024. NOT mentioned in gaps.md; relates to N3, N4, N5, N10. | Decide whether to surface as "planned, not implemented" gap |
| `notes/workstream-datalog-grounding-2026-05-01.md` (lines 1-54) | Designs FO ASPIC+ grounding using Gunray. Implementation partially in place at `datalog_grounding.py`; Diller-12 NAP missing. Relates to N8. | Decide whether to flag NAP gap and FO-only-via-gunray dep |
| `notes/readme-sync-2026-05-02.md` (lines 1-168) | Catalogs README/code drift; not gap-specific but surfaces limitations the README hides (rows 11, 14, 17, 31; "open questions" 1-8 at lines 152-168) | Use as authoritative cross-check for any limitation a rewriter adds |

No `notes/workstream-*.md` other than the two above exists in the tree
(Glob result on this date).

## 5. Prose recommendations (severe issues only)

- **R1.** The doc title "Argumentation Gaps" misrepresents content.
  Either rename to `closed-bugs.md` / `workstream-changelog.md`, or
  restructure so the FIRST section is "Currently-known limitations" and
  the closed-bug tables move to an appendix. Today a reader looking for
  "what does this package not do?" gets only one sentence (line 12).
- **R2.** Add at least N1, N2, N3, N5, N6, N7, N8 as first-class
  limitation entries with file:line citations. Each has a docstring or
  failure-path that already supplies the wording.
- **R3.** `notes/readme-sync-orchestrator-2026-05-02.md:43` instructs
  the README rewriter to defer the README's *Non-goals* and
  *Approximate* discussion to gaps.md. Today's gaps.md cannot absorb
  that content because it has no "Non-goals" or "Approximate" section.
  Add both before the README rewrite lands.
- **R4.** `docs/architecture.md:223-229` already has its own *Non-goals*
  paragraph. Decide where canonical non-goals live (architecture.md vs
  gaps.md) before duplication enters the README.

## 6. Cross-doc dependencies

- `docs/gaps.md` contains zero outbound cross-doc links.
- Inbound references: only `notes/readme-sync-orchestrator-2026-05-02.md:43`
  (planning note for the README rewrite).
- Adjacent docs in `docs/`: `architecture.md`, `backends.md`,
  `caf-semantics.md`, `iccma-data.md`, `iccma-2025-data.md`, `setaf.md`.
  None inspected for outbound link to gaps.md (Grep of `docs/` for
  `gaps|limitation|non-goal` returned only `architecture.md:223`
  ("## Non-goals") and gaps.md's own headers).
- Duplication risk: `architecture.md:223-229` Non-goals overlaps with
  the README "Non-goals" section that the orchestrator wants moved
  here. Three potential homes for the same content unless reconciled.

## 7. Verdict

`docs/gaps.md` is **factually accurate but structurally wrong for its
filename**: it's a workstream changelog with a single live-limitation
sentence, while at least 10-12 limitations are documented in module
docstrings and not mirrored here. Health: MEDIUM. A rewriter must (a)
add a "Currently-known limitations" section sourced from items N1-N8
above, and (b) reconcile non-goals with `docs/architecture.md` before
the README rewrite redirects readers to this file.
