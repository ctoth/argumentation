# Paper transcription audit

## Goal
Compare package definitions and paper notes with the original papers, correct confirmed mistranscriptions, commit the corrections, and integrate them onto main. Q authorized implementation with "make it so" on 2026-10-19.

## State
Three editing subagents completed comparisons in structured, quantitative/probabilistic, and specialized framework lanes. The primary agent covers abstract/bipolar semantics and solver papers, reviews the corrections, and checks original pages independently. A separate read-only verifier checked eleven selected large/formula-heavy rewrites and found no introduced defect. Corrections currently touch 54 existing notes plus CITATIONS.md. Publication, hosted CI, and integration are pending.

## Decisions and why
- Smallest change: correct erroneous prose, equations, and examples in existing paper notes and any directly corresponding citation text. Expected size: a few lines per confirmed error, plus this audit record. No new protocols, features, tests, or performance research.
- Work in an isolated worktree based on local main `f6607537d9597cdfd553ee0aaa7df9ac16cef904`; preserve the existing license branch and all untracked files.
- This is a package-to-literature audit, not a review of the unrelated license PR #107. Do not publish a PR review.
- Use original local PDFs and existing page images; retain binary artifacts outside commits. For black/transparent stored images, render the original PDF to an opaque image in memory. Do not rerun CI steps locally.
- Q clarified that papers must only be read through visual page images, never extracted text, even for navigation. Corrected the standing source rule in `C:/Users/Q/.codex/AGENTS.md` first and told all three subagents. No correction is accepted on the strength of the earlier primary-agent pdftotext output; original images supply the evidence.
- Keep source-paper inconsistencies explicit: Niskanen2025 has inconsistent B-derivation signs; Cayrol's addition paper has conflicting cardinalities in definitions and summary tables. Do not silently rewrite the paper.
- Preserve correct dense notes and repair repeated erroneous statements where they recur. This is a transcription audit, not implementation or solver-performance work; no production changes or new tests/guards.

## Surprises
- The primary checkout initially used `license-mit`. Another session merged license PR #107 while this audit ran; primary main and origin/main are now `ee16aa6435a47fd2faf489b59ca7bcc58b484ea0`. Preserve that work and all unrelated untracked artifacts.
- There are 72 tracked paper-note files, plus source-only/artifact directories. This is a targeted audit of definitions, formulas, algorithms, examples, and selected reported results, not a word-for-word reread of every paper and proof.
- Some stored PNGs obscure text. Claims not visually established remain outside coverage. The original sources remain ignored local artifacts; page-image links in notes refer to those artifacts.

## Correction coverage

Source identifiers below are zero-based `pngs/page-NNN.png` in the corresponding `papers/` directory of the primary checkout, unless marked PDF. Exact statement-to-image references are also retained beside the corrections. Ranges list inspected pages supporting corrections, not a claim that every sentence on those pages was audited.

| Paper directory prefix | Corrected subjects | Source images |
|---|---|---|
| AlAnaissy_2024 | Gradual recurrences, deletion operators, Shapley definition, principles/tables | 001-005, 008-009 |
| Amgoud_2004 | Valuation input order/formulas, paths, desire/plan definitions and examples | 003-007 |
| Amgoud_2008 | Valuation input order, support closure, direct defense, unachievable desires | 014-015, 021-022 |
| Amgoud_2013 | Notation, group comparisons, CT direction, postulates, Bbs counterexample | 002-005, 007, 011 |
| Baroni_2005 | General selection need not be admissible; alternative stable definition | 017-018, 025-026 |
| Baroni_2019 | One-way GP implications, base-weight/group principles, balance classifications | 005-008, 010-011, 015 |
| Baumann_2015 | Four kernels, model inclusion, expansion, actual revision construction | 001-005 |
| Besnard_2001 | Attack target, equivalent arguments, normal form | 004-006 |
| Bistarelli_2012 | Conditional example's antecedent and exclusive-or consequent | 010 |
| Bonzon_2016 | Discussion/burden/tuple rankings and property classifications | 003-005 |
| Brewka_2010 | Original BADF reduct, translations, examples, proof standards, complexity | 002, 004-008 |
| Brewka_2013 | False-atom reduct, actual dynamic-preference example, theorem numbers | 003, 005 |
| Caminada_2006 | Minimal-undec/preferred implication and acceptance theorems | 005, 009 |
| Caminada_2007 | Attacks, consistency, transposition, examples, theorem scope, complexity, bibliography | 004-027, 039; appendix proofs 028-038 excluded |
| Cayrol_2005 | Safety/closure, admissibility/properties, actual worked examples | 003-005, 008-009 |
| Cayrol_2014 | Actual 2010 publication, cardinalities, quantifiers, monotony, proposition conditions | 000, 006-008, 010, 012-013, 015-022 |
| Coste-Marquis_2007 | Consensual expansion, edit cost, proposition conditions, majority completions, joint acceptance | 005-010, 013-015, 017-021 |
| Delobelle_2019 | Retained target node loses incident edges when in removed set | 004 |
| Diller_2015 | Revision result type, total preorder, postulates, theorem directions | 000-005 |
| Diller_2025 | Dependency approximation, transformations/algorithms, extension vs conclusion preservation, setup | 001-007, 009; obscured 008 excluded |
| Dung_1995 | Lemma 46 odd/even iteration indices; stable-definition citation | 007, 021 |
| Dung_2007 | Admissibility prerequisite in ideal-set characterization | 008 |
| Dunne_2011 | Initial/admissible verification vs grounded; symmetric exception; budgetless POSITION | 009-014, 022-023 |
| Dvorak_2014 | Complete-extension SAT clause uses membership, not range membership | 007 |
| Freedman_2025 | Path parity, addition vs edge-switching, QEM strictness, actual datasets/results/figures | 003, 006, 017; opaque PDF pp.3,5,6,8,17 |
| Gabbay_2012 | Eq_max complete-labelling correspondence vs product equations | 020-021 |
| Gaggl_2013 | Conflict-free prerequisite in separated-framework theorem | 012 |
| Hunter_2017 | Probability-function hierarchy implications | 015-016 |
| Kampik_2024 | Removed coalition interpretation and actual movie example | 009, 039 |
| Lehtonen_2021_DeclarativeAlgorithmsComplexityResults | Iteration adds at least one assumption unless fixed | 014 |
| Lehtonen_2024 | Preference lifting, complexity, well-formedness, empirical setup/results | 001-002, 006-008 |
| Li_2011 | Eligible subgraphs, conditional edge probabilities, probability-one elements | 002 |
| Mailly_2023 | Fourteen descriptions; Crustabri selector groups all attacks to a target | 005-006, 020 |
| Matt_2008 | Strategy spaces, payoff, strength bounds and attack effects | 003-004, 006-009 |
| Modgil_2018 | Explosive consequence, reasonable inducing order, attack/defeat conditions | 011, 013, 018, 020-022 |
| Niskanen_2025 | Explicit source inconsistency annotation for B-derivation signs | 003-005 |
| Odekerken_2023 | Actual all-defeasible ASPIC fragment, rebut, futures/status/relevance and algorithm | 001-007; empirical section excluded |
| Oikarinen_2010 | Four kernels and exact strong/local equivalence distinctions | opaque original PDF indices 5-14,17-21 |
| Polberg_2017 | Nonempty SETAF tails; standard/partially acyclic range; model-first reduct | 027, 075-077, 080; thesis not exhaustively read |
| Popescu_2023 | Proper-subset MSO quantifier, defeated assumptions, counterwitness requirements | 006-008 |
| Popescu_2024_Algorithmic and Popescu_2024_Probabilistic | Absent-attack product restricted to eligible endpoint pairs | each 002; distinct local PDFs |
| Potyka_2018 | Euler and quadratic-energy formulas, ODE, trajectory/equilibrium distinction | 001-002 |
| Prakken_2010 | Attack/defeat numbering, LastDefRules, preference lifting, closure and examples | 005,007-009,012-013,015-017,020 |
| Prakken_2019 | Not-less-preferred defeat and antitone defeat vs monotone characteristic function | page-04.png, page-05.png |
| Rago_2016_Adapting | Polarity sign/closed form, ordering, cyclic existence vs uniqueness | 001,004-005 |
| Rago_2016_Discontinuity | Original QuAD vs DF-QuAD aggregation and balance | 000-006 |
| Riveret_2017 | OUT/UN quantifiers and OFF distinction | 015 |
| Strass_2013 | Inclusion arrows and Kripke-Kleene/well-founded distinction | 005,028 |
| Thimm_2021_Fudge | The admissible attacker is extended with the query | 001 |
| Thimm_2021_Skeptical | AdmExtAtt returns attacker; CDAS quantifies over any query-containing set | 001-004 |
| Toni_2014 | Culprit vs defense flowchart filter | 016,018 |
| Wallner_2024 | Subjective rule-name filtering and complementary-literal condition | 006,009 |
| deKleer_1986_AssumptionBasedTMS | Nogood supersets, not subsets | 021 |

## Coverage limits and unchanged comparisons

Bounded checks without a correction: Atkinson2007 (003-008), Bench-Capon2003 (002-003,006-011,016), Bondarenko1997 (024-025), Cyras2016 (004-005,007), Dimopoulos2002 (009-011,024), Toni2013 (007-008), Pollock1987 (017-018), deKleer ProblemSolving (001; apparent source inconsistency retained), Cerutti2013 (008-010 algorithm), Cerutti2015 (001-003), Coste-Marquis2005 (001-003 definitions and iteration), Pu2017 (000-003), Niskanen2020 (opaque PDF indices 1-2), and selected Mailly2023 descriptions. These are not clean bills of health for all their notes.

Not source-verified: Baumann2019 and Lehtonen2020 have no local PDF/page images; the separate Lehtonen2021 ABA note has not received its own visual audit. Yin2023 has a readable definition page (003) matching the note, but most equation/prose images obscure text and remain outside coverage. The separate incremental-ASP source/artifact directory and source-only Popescu Advancing directory were inventoried; no new notes were created. Unlisted proofs, empirical claims, and collection cross-references remain outside the targeted comparison.

## Verification and integration

- Evidence method: visual original-page comparisons; corrected notes carry local image/PDF-page provenance.
- No production implementation changes and no local test/typecheck/build execution. Hosted PR CI will supply package validation.
- Separate verifier covered Baumann2015, Diller2025, Odekerken2023, Caminada2007, Freedman2025, Baroni2019, both Rago2016 papers, Potyka2018, and AlAnaissy2024; its verdict was bounded to those inspected changes.
- Required PR review ledger and exact-head hosted checks remain pending. No external review comments have been posted.

## Next step
Commit the scoped corrections and this record, publish a PR for hosted CI, finish the source/diff review, run the existing PR ledger gate, and normally merge the corrections onto main if no blocker remains.
