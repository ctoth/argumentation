# docs/caf-semantics.md audit — 2026-05-02

Read-only audit of `docs/caf-semantics.md` against `src/argumentation/caf.py`
and `tests/test_caf.py`. All line numbers 1-based.

## 1. Verified gaps

| Doc line(s) | Claim | Code reality | Recommended action |
|---|---|---|---|
| caf-semantics.md:15-16 | "Inherited semantics ... compute ordinary Dung extensions first, then project each extension to its set of claims" | Verified at caf.py:62-71 (`inherited_extensions`) and caf.py:177-178 (`_project`). | PASS — accurate |
| caf-semantics.md:22-23 | "Inherited semantics are available for the Dung semantics supported by the underlying package dispatcher." | `_argument_extensions` (caf.py:154-174) hard-codes a fixed list: `grounded`, `complete`, `preferred`, `stable`, `semi-stable`, `stage`, `naive`, `cf2`. Not all dispatcher semantics are reachable here — for example `eager`, `ideal`, and `stage2` are exported by `argumentation.dung` but `_argument_extensions` raises `ValueError` for them (caf.py:174). | Replace the vague phrasing with the exact list of inherited semantics actually accepted: `grounded`, `complete`, `preferred`, `stable`, `semi-stable`, `stage`, `naive`, `cf2`. |
| caf-semantics.md:25-32 | Lists six claim-level semantics: `preferred`, `naive`, `stable`, `stable-admissible`, `semi-stable`, `stage`. | Confirmed at caf.py:84, 90, 96, 104, 112, 121; raise at caf.py:130. | PASS |
| caf-semantics.md:34-36 | "Claim-level semi-stable and stage semantics use the CAF defeated-claim range: an argument set defeats a claim only when it attacks every argument carrying that claim." | Verified at caf.py:198-213 (`defeated_claims`) and caf.py:249-261 (`_claim_range_maximal`). The text describes the `defeated_claims` rule, not how `_claim_range_maximal` uses it; minor: maximisation is over the *claim range* (`claim ∪ defeated_claims`), not just defeated claims. | Optional clarification: also state that semi-stable/stage select claim sets whose claim-range is non-dominated (caf.py:249-261). |
| caf-semantics.md:40-46 | "exposes ... `is_well_formed(caf)`, `defeated_claims(caf, extension)`, `claim_range(caf, extension)`, `is_i_maximal(claim_sets)`." | Verified: caf.py:181 (`is_well_formed`), caf.py:198 (`defeated_claims`), caf.py:216 (`claim_range`), caf.py:221 (`is_i_maximal`). | PASS |
| caf-semantics.md:42-43 | `is_well_formed` "matching the CAF condition that arguments with the same claim have the same outgoing attack targets." | Verified at caf.py:181-195 (compares `outgoing[left] != outgoing[right]` when `claims[left] == claims[right]`). | PASS |
| caf-semantics.md:8-12 | "A `ClaimAugmentedAF` consists of: a Dung `ArgumentationFramework`; a total claim map assigning exactly one claim identifier to every argument." | Verified: dataclass at caf.py:40-44; `__post_init__` enforces `set(claims) == set(arguments)` and raises `ValueError` on `missing`/`extra` (caf.py:45-54). Also coerces values to `str` (caf.py:55-59). | PASS — could optionally note the `str(claim)` coercion. |
| caf-semantics.md:13-18 | "The module exposes two CAF views: inherited semantics ... claim-level semantics ..." | Two views verified, but the *dispatcher entry point* `extensions(caf, *, semantics, view)` (caf.py:140-151) and the literal type `CAFView = Literal["inherited", "claim_level"]` (caf.py:37) are not mentioned in the doc. | Add a sentence naming `extensions(...)` and the `view` parameter values `"inherited"` / `"claim_level"`. |
| caf-semantics.md (whole) | No mention of `concurrence_holds`. | `concurrence_holds(caf, *, semantics)` at caf.py:133-137 is a public surface; tested at tests/test_caf.py:268. | Add it under "Implemented Predicates" — it directly mirrors the paper's concurrence question (caf-semantics.md:54 already mentions concurrence as a complexity problem). |

## 2. Undocumented CAF surfaces that belong here

| Surface | Location | Recommendation |
|---|---|---|
| `extensions(caf, *, semantics, view)` dispatcher | caf.py:140-151 | Document as the canonical entry point; mention `view: CAFView`. |
| `CAFView` literal alias | caf.py:37 | Mention `"inherited"` / `"claim_level"` literals; users importing the type need to know the spelling (note underscore in `claim_level`, not hyphen). |
| `concurrence_holds(caf, *, semantics)` | caf.py:133-137 | Add to "Implemented Predicates" — paper-faithful concurrence test. |
| Exact list of inherited semantics | caf.py:158-174 | Replace caf-semantics.md:22-23 vague phrasing with the eight literal semantics names. |
| Exact list of claim-level semantics raise | caf.py:130 | Already covered, but worth saying that unsupported semantics raise `ValueError`. |
| `ValueError` on bad claim map | caf.py:50-54 | Optional: doc the precondition that the claim map domain equals the argument set. |
| Hyphen vs underscore inconsistency | `view` is `claim_level` (caf.py:37) but most CAF semantics names are hyphenated: `semi-stable`, `stable-admissible`, `stage`. | Worth flagging in the doc so users do not write `claim-level` or `semi_stable`. |

## 3. Code-example verification

The doc contains zero code examples. Nothing to verify here.

Recommendation: a minimal example would help, e.g. KR 2020 Example 1 at
tests/test_caf.py:31-44 + tests/test_caf.py:149-160 makes a tight 12-line
illustration of the inherited-vs-claim-level split.

## 4. Citation / reference audit

| Citation in doc | Verdict | Notes |
|---|---|---|
| caf-semantics.md:53 "2023 Artificial Intelligence paper" | matches | caf.py:9-10 cites "Dvorak, Gressler, Rapberger, and Woltran (2023). The complexity landscape of claim-augmented argumentation frameworks." Doc does not name the authors — minor. |
| caf-semantics.md:66 "KR 2020 / AIJ definitions" | matches | caf.py:11-12 cites "Dvorak, Rapberger, and Woltran (2020). Argumentation semantics under a claim-centric view." Tests reference KR 2020 examples 1-6 and AIJ 2023 Definition 6 (tests/test_caf.py:149, 163, 182, 193, 205, 218, 230, 302). |
| caf-semantics.md:68 "KR 2020 propositions for cl-preferred, cl-naive, stable-variant concurrence, I-maximality, unique-claim coincidence" | matches | Tests cover Propositions 1, 2, 3, 5, 6, 8, 10, 11, and Lemmas 1, 3 (tests/test_caf.py:397, 405, 411, 419, 427, 433, 444, 451, 384, 458). |
| Author names not given | review | Doc cites venues but not full author lists. caf.py:9-12 has them. Minor consistency suggestion: at least give Dvorak-Rapberger-Woltran 2020 / Dvorak-Gressler-Rapberger-Woltran 2023 to match caf.py docstring style. |

## 5. Prose recommendations (severe only)

- **caf-semantics.md:22-23** "Inherited semantics are available for the Dung
  semantics supported by the underlying package dispatcher" overstates: the
  CAF wrapper has its *own* hard-coded dispatch (caf.py:154-174) and does not
  forward to e.g. `eager_extension` or `stage2_extensions` even though those
  are exported from `argumentation.dung`. Users who try
  `inherited_extensions(caf, semantics="eager")` will get
  `ValueError: unsupported CAF semantics: eager`. Replace the sentence with
  an enumerated list.
- **caf-semantics.md:13-18** advertises "two CAF views" without naming the
  dispatcher (`extensions(...)` at caf.py:140) or the literal values
  (`"inherited"`, `"claim_level"`). A user reading only this doc cannot call
  the dispatched form.
- No mention of `concurrence_holds` even though concurrence is a major theme
  of both the cited papers and is tested (tests/test_caf.py:268).

## 6. Cross-doc dependencies

- `notes/readme-sync-2026-05-02.md` Section 5 (Surface tier proposal) places
  `caf` under "Specialized frameworks". A README rewrite that summarises CAF
  in one line should not contradict caf-semantics.md's clearer enumeration.
- `notes/readme-sync-2026-05-02.md` does not currently flag any caf-specific
  README drift, so this audit's findings are independent of the README
  workstream.
- caf-semantics.md:60 "implements the finite semantic computations above"
  refers back to itself; no dependency on other docs.
- The doc references "the underlying package dispatcher" (caf-semantics.md:23)
  — this is `argumentation.dung`'s extension functions and (separately)
  `argumentation.semantics`'s generic dispatcher. The phrasing is ambiguous;
  if a separate `docs/dung-semantics.md` or similar exists and the rewriter
  wants to link, this is the right spot.

## 7. Verdict

Healthy. The doc is short, paper-faithful, and has no false claims about
implemented semantics. The two real gaps are (a) overstated inherited-
semantics coverage at caf-semantics.md:22-23 (eight literals are accepted,
not "whatever the dispatcher supports") and (b) missing mention of the
`extensions(...)` dispatcher, the `CAFView` literal, and `concurrence_holds`.
A 30-minute rewrite plus one runnable example would close every observed gap.
