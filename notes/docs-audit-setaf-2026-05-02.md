# Docs audit — `docs/setaf.md` — 2026-05-02

Read-only audit of `C:\Users\Q\code\argumentation\docs\setaf.md` against
`src/argumentation/setaf.py`, `src/argumentation/setaf_io.py`, and
`tests/test_setaf*.py`. All line numbers 1-based.

## 1. Verified gaps

| doc-line | Claim | Code reality | Recommended action |
|---|---|---|---|
| setaf.md:14-17 | Lists "complete, grounded, preferred, stable" as the implemented core semantics. | `setaf.py` also exports `semi_stable_extensions` (setaf.py:137) and `stage_extensions` (setaf.py:141), each defined as range-maximal over complete / conflict-free sets respectively. | Add semi-stable and stage to the bullet enumerating implemented semantics, with the same one-line definitions. |
| setaf.md:14-17 | No mention of the characteristic function or admissibility as standalone surface. | `admissible` (setaf.py:71), `characteristic_fn` (setaf.py:80), `attacks_argument` (setaf.py:49), `defends` (setaf.py:61), `range_of` (setaf.py:119), `conflict_free` (setaf.py:40) are all top-level public functions. | Either name them as part of the semantic API or add a short "Public functions" subsection citing module path. |
| setaf.md:10 | "A set `S` attacks argument `a` iff there is an attack `(T, a)` with `T <= S`." | Matches `attacks_argument` (setaf.py:49-58) and the property test `test_definition_1_attack_activation_iff_tail_is_contained` (test_setaf.py:171-179). | PASS — keep wording. |
| setaf.md:11 | "`S` is conflict-free iff no active attack targets an argument in `S`." | Matches `conflict_free` (setaf.py:40-46) and `test_definition_2_...` (test_setaf.py:182-191). | PASS. |
| setaf.md:12-13 | Defense definition. | Matches `defends` (setaf.py:61-68); test at test_setaf.py:118-129. | PASS. |
| setaf.md:14-15 | "Complete extensions are admissible fixed points of the characteristic function" | Matches `complete_extensions` (setaf.py:97-103) — filters subsets by `admissible(...) and characteristic_fn(...) == candidate`. | PASS. |
| setaf.md:15 | "grounded is the subset-minimal complete extension" | Implemented as least fixed-point of the characteristic function in `grounded_extension` (setaf.py:88-94), proven equivalent by `test_grounded_is_subset_minimal_complete_extension` (test_setaf.py:208-214). Docstring describes effect; implementation is iterative least-fixed-point, not enumeration of completes. | PASS — wording is correct in the mathematical sense. |
| setaf.md:16-17 | "stable extensions are conflict-free sets whose SETAF range is all arguments." | Matches `stable_extensions` (setaf.py:128-134) and `test_definition_3_stable_iff_conflict_free_and_full_range` (test_setaf.py:194-204). | PASS. |
| setaf.md:21-22 | "supports the ASPARTIX SETAF fact format documented by TU Wien". | `setaf_io.py:1-6` says "ASP fact format using `arg/1`, `att/2`, `mem/2`"; no URL/citation in code or doc. | Optional: add an explicit citation/URL to the TU Wien spec, or remove "documented by TU Wien" since neither code nor doc cites a source. |
| setaf.md:33-35 | "uses only `arg/1`, `att/2`, and `mem/2` facts." | Confirmed — `_ASPARTIX_FACT_RE` (setaf_io.py:15-17) matches exactly those predicates; writer (setaf_io.py:65-81) emits only those. | PASS. |
| setaf.md:24-31 | Example uses `att(r1,c).` then `mem(r1,a).`/`mem(r1,b).` | Matches `test_parse_aspartix_setaf_official_fixture` (test_setaf_io.py:42-55). | PASS. |
| setaf.md:38-40 | "compact `p setaf` format … not documented or exposed as an ICCMA SETAF format." | Matches `parse_compact_setaf` / `write_compact_setaf` (setaf_io.py:84-123); module docstring (setaf_io.py:1-6) repeats the same caveat. | PASS. |
| setaf.md:42-46 | "does not implement the splitting algorithms from the splitting paper" | No `split`/`splitting` symbol in `setaf.py`. | PASS — accurate non-goal. |

## 2. Undocumented SETAF surfaces

These exist in `setaf.py` / `setaf_io.py` and are not mentioned anywhere in `docs/setaf.md`:

| Surface | Location | Notes |
|---|---|---|
| `SETAF` dataclass shape | setaf.py:13-37 | `frozen=True`; coerces tails to `frozenset` and arguments to `str`; raises on empty tails (setaf.py:26-28) and on attacks referencing undeclared arguments (setaf.py:29-35). The doc says "pair `(A, R)`" but never names the dataclass or its precondition raises. |
| `CollectiveAttack` type alias | setaf.py:10 | `tuple[frozenset[str], str]` — load-bearing for type hints. |
| `attacks_argument(framework, candidate, target)` | setaf.py:49-58 | Public predicate. |
| `defends(framework, candidate, argument)` | setaf.py:61-68 | Public predicate. |
| `admissible(framework, candidate)` | setaf.py:71-77 | Public predicate. |
| `characteristic_fn(framework, candidate)` | setaf.py:80-85 | Public function returning the defended set. |
| `range_of(framework, candidate)` | setaf.py:119-125 | Public; doc references "range" (setaf.md:17) without exposing the helper. |
| `semi_stable_extensions(framework)` | setaf.py:137-138 | Range-maximal among complete extensions. |
| `stage_extensions(framework)` | setaf.py:141-147 | Range-maximal among conflict-free sets. |
| `parse_aspartix_setaf` / `write_aspartix_setaf` | setaf_io.py:20-81 | Doc names the format but not the function symbols. |
| Round-trip / determinism guarantees | setaf_io.py:65-81; test_setaf_io.py:60-72 | Writer is deterministic (sorted args, sorted attacks, `r{index}` names) and round-trips. Worth one sentence. |
| Comment / blank-line handling | setaf_io.py:28 (`%`); setaf_io.py:91 (`#`) | ASPARTIX parser skips `%` comments; compact parser skips `#` comments. Currently undocumented. |
| Validation errors raised by parser | setaf_io.py:32, 38, 43, 47, 50, 56; tests test_setaf_io.py:75-92 | Reject missing dot, compact-style header in ASPARTIX input, `mem` referencing unknown attack id, empty tails. |
| `_check_candidate` precondition surface | setaf.py:180-183 | `conflict_free` and `admissible` raise `ValueError` on candidate arguments not in framework — relevant to anyone composing these calls. |

## 3. Code-example verification

The doc contains exactly one code block (setaf.md:24-31) — six ASPARTIX fact lines. No Python examples are shown.

| Block | Verdict | Notes |
|---|---|---|
| ASPARTIX fact example, setaf.md:24-31 | PASS | Identical text body to `test_parse_aspartix_setaf_official_fixture` (test_setaf_io.py:42-55), which round-trips through `parse_aspartix_setaf`. |

Gap: no Python usage example for constructing a `SETAF` directly, calling `complete_extensions`, or round-tripping through `write_aspartix_setaf`. A rewriter may want at least one such example mirroring the README's Dung block (README.md:51-73 per `notes/readme-sync-2026-05-02.md:45`).

## 4. Citation / reference audit

| Reference | Verdict | Notes |
|---|---|---|
| "splitting paper" (setaf.md:7-8, 45-46) | needs-update | Cited by phrase only; no author/year/venue. The doc says "page images" implying a specific source, but it is not named. Either inline the full citation or drop the phrase. |
| "ASPARTIX SETAF fact format documented by TU Wien" (setaf.md:21-22) | needs-update | No URL or paper. The closest in-tree referent is `notes/paper-egly-gaggl-woltran-2010-retrieval.md` (per `notes/readme-sync-2026-05-02.md:80`); pin to that paper or to TU Wien's online ASPARTIX page. |
| "ICCMA 2023 rules document" (setaf.md:39-40) | review needed | Asserts the ICCMA 2023 rules cover AF and ABA but not SETAF. Plausible but uncited; if kept, add a link or omit. |
| Definitions 1-3 anchoring tests (test_setaf.py:171, 184, 196) | undercited in doc | The tests explicitly tag "Definition 1/2/3" from a SETAF paper; the doc references "the splitting paper" without specifying which definitions are which. Consider attaching definition numbers to the bullet list at setaf.md:10-13. |

## 5. Prose recommendations (severe only)

- The semantics list at setaf.md:14-17 omits two implemented semantics (semi-stable, stage). A reader following the doc would conclude they are not supported. This is the single most material drift.
- "splitting paper page images" (setaf.md:7-8) is informal-internal language; in user-facing docs replace with a proper citation or remove.
- The doc never names any Python symbol other than `parse_compact_setaf` / `write_compact_setaf` (setaf.md:38). A rewriter should at minimum surface `SETAF`, `parse_aspartix_setaf`, `write_aspartix_setaf`, and the public predicates / extension functions.

## 6. Cross-doc dependencies

- `README.md` does not currently document SETAF as a primary example surface (per `notes/readme-sync-2026-05-02.md` Section 5, the proposed grouping places `setaf` and `setaf_io` under "Specialized frameworks"). Any rewrite of `docs/setaf.md` should leave room for the README to link in.
- `solver.py:120` exposes `solve_setaf_extensions` per `notes/readme-sync-2026-05-02.md:16` — currently unmentioned in either README or `docs/setaf.md`. If `docs/setaf.md` aims to be the single SETAF reference, it should at minimum mention the solver entry point or explicitly defer it.
- `src/argumentation/__init__.py:37,80-81` re-exports `setaf` and `setaf_io` as package-level names; the doc does not establish the import surface (`from argumentation import setaf, setaf_io` vs. `from argumentation.setaf import SETAF`).
- `notes/paper-egly-gaggl-woltran-2010-retrieval.md` is the standing in-tree note on the ASPARTIX format; if a citation is added, this note is the natural anchor.
- Splitting-related future work: no in-tree note for splitting algorithms; `setaf.md:42-46` is the only place this is discussed.

## 7. Verdict

`docs/setaf.md` is mathematically accurate where it speaks, but materially incomplete. The biggest gap is that two implemented semantics (semi-stable, stage) are silently omitted from the semantics list, and no public Python symbol is named beyond two compact-format helpers — a rewriter should treat this as an "expand surface coverage" job rather than a "fix wrong claims" job. Citations are vague and should be tightened.
