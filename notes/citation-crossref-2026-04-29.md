# Citation cross-reference — 2026-04-29

Scope: every paper-citation in `C:\Users\Q\code\argumentation\src\argumentation\*.py`,
`README.md`, `docs/architecture.md`, and `CITATIONS.md`, cross-checked against
directories under `C:\Users\Q\code\propstore\papers\`. Observations only.

## Citations in code (file:line, citation, anchor)

### `src/argumentation/aba.py`
- L3 — "Bondarenko, Dung, Kowalski, and Toni 1997" — module docstring
- L5 — "Toni 2014" — module docstring
- L6 — "Cyras and Toni 2016" — module docstring
- L64 — "Bondarenko et al. 1997 Def 4.10" — error string inside flat-ABA validator

### `src/argumentation/accrual.py`
- L40 — "Prakken 2019: weak applicability" — function docstring (`weak_applicability`)
- L102 — "Prakken 2019 studies the Dung-style relation" — function docstring (`accrual_envelope`)

### `src/argumentation/adf.py`
- L3 — "Brewka and Woltran 2010" — module docstring
- L4 — "Brewka et al. 2013" — module docstring (operator semantics)
- L5 — "Polberg 2017" — module docstring (formula-AST)

### `src/argumentation/af_revision.py`
- L181 — "Baumann 2014, ECAI pp. 63-68" — `baumann_2015_kernel_union_expand`
- L196,L198 — "Baumann 2014" — kernel helper
- L211,L213 — "Baumann 2015, Definition 5.10" — kernel helper
- L271 — "Unhandled Baumann kernel semantics" — error string
- L335 — "Cayrol, de Saint-Cyr, and Lagasquie-Schiex 2010, JAIR 38, Table 3" — change-classification helper

### `src/argumentation/aspic.py`
Citations (all Modgil & Prakken 2018 unless noted):
- L4, L9 — module docstring (Defs 1-2)
- L29 — "Riveret 2017 Def 2.1" (class `GroundAtom`)
- L30 — "Diller et al. 2025 Def 7" (class `GroundAtom`)
- L55, L74, L91, L110, L120, L141, L154, L167, L197, L228, L265, L278, L287, L314, L329, L382, L479, L513, L525, L530, L538, L549, L571, L579, L594, L610, L667, L687, L789, L815, L940, L1000, L1116, L1137, L1180, L1255, L1288, L1372 — anchored to specific Defs (1, 2, 4, 5, 6, 7, 8, 9, 12, 19) on the listed classes/functions
- L146 — "Prakken 2010, Def 3.4 (p.47-48)" — `Rule`
- L352 — "Prakken 2010, Def. 5.1 (pp. 141-142)" — `transposition_closure`
- L399, L441 — "Prakken 2010, Defs. 5.1-5.3" — `strict_closure`
- L640, L645 — "Prakken 2010, Def 3.8" — `is_firm`, `is_strict`
- L688 — "Prakken 2010, Def 3.6 (p.36)" — `build_arguments`
- L832 — "Toni (2014): ABA backward chaining" — `build_arguments`
- L833 — "Besnard & Hunter (2001, Def 6.1, p.215)" — same
- L835 — "de Kleer (1986, p.214): ATMS" — same
- L1010 — "Pollock 1987, Def 2.4, p.485" — `compute_attacks`
- L1014 — "Pollock 1987, Def 2.5, p.485" — same
- L1257 — "Pollock 1987, Def 2.5, p.485" — `compute_defeats`

### `src/argumentation/aspic_encoding.py`
- L25 — "Niskanen, and Jarvisalo 2024, Section 5" — module docstring (preceded in same docstring by "Lehtonen,")

### `src/argumentation/aspic_incomplete.py`
- L47 — "Odekerken, Diller, and Borg style incomplete-information" — function docstring

### `src/argumentation/bipolar.py`
- L3 — "Cayrol and Lagasquie-Schiex 2005" — module docstring
- L4 — "Amgoud et al. 2008" — module docstring
- L20, L112 — "Cayrol & Lagasquie-Schiex (2005, Definition 3)" — `cayrol_derived_defeats`
- L209 — "Cayrol 2005, Definition 6" — set-conflict-free helper
- L217 — "Cayrol 2005, Definition 7" — safe set
- L231 — "Cayrol 2005, Definition 5" — set-defends helper
- L247, L257, L267 — "Cayrol 2005, Definitions 9/10/11" — d/s/c-admissible helpers
- L325 — "Cayrol 2005, Definition 8" — `stable_extensions`
- L353 — "Cayrol and Lagasquie-Schiex 2005, p. 385" — instantiation helper

### `src/argumentation/dfquad.py`
- L15 — "Rago, Toni, Aurisicchio, and Baroni 2016, KR, p. 65, Defs. 1-3" — module docstring
- L34 — "Rago et al. 2016, KR, p. 65, Def. 1 and Lemma 1" — sequence helper
- L58 — "Rago et al. 2016, KR, p. 66, Def. 3" — score function
- L140 — "Rago, Cyras, and Toni 2016, SAFA, p. 35, Defs. 1-3" — BAF helper

### `src/argumentation/dung.py`
- L7 — "Dung, P.M. (1995)" — module docstring
- L31 — "Dung 1995: AF = (Args, Defeats)" — `ArgumentationFramework`
- L32, L100 — "Modgil & Prakken 2018 Def 14" — same/`conflict_free`
- L136 — "Dung 1995, Definition 17" — `characteristic_fn`
- L172, L173 — "Modgil & Prakken 2018 Def 14"; "Dung 1995 Def 6" — `admissible`
- L201 — "Dung 1995, Definition 20 + Theorem 25 (least fixed point)" — `grounded_extension`
- L226 — "Dung 1995, Definition 10" — `complete_extensions`
- L261 — "Dung 1995, Definition 8" — `preferred_extensions`
- L279, L280 — "Dung 1995, Definition 12"; "Modgil & Prakken 2018, Definition 14" — `stable_extensions`
- L325 — "Caminada 2011, Definition 2.3" — `semi_stable_extensions`
- L333 — "Gaggl and Woltran 2013, p. 927" — `stage_extensions`
- L351 — "Caminada 2007's eager extension" — `eager_extension`
- L503, L515 — "Gaggl and Woltran 2013, Definition 2.7" / SCC-recursive — `cf2_extensions`/`stage2_extensions`
- L551 — "Coste-Marquis, Devred, and Marquis 2005, pp. 1-2" — prudent helpers
- L617 — "Coste-Marquis, Devred, and Marquis 2005, p. 3" — `prudent_grounded_extension`
- L652 — "Dung, Mancarella, and Toni 2007, Definition 2.2 and Theorem 2.1" — `ideal_extension`

### `src/argumentation/equational.py`
- L23 — "Gabbay 2012, Argument & Computation, pp. 104-108" — class docstring

### `src/argumentation/gradual.py`
- L15, L95, L114, L173 — Potyka 2018 (Def 1, KR p.150 Def 2) — BAG class / quadratic_energy_strengths
- L299 — "Al Anaissy et al. 2024, Definition 12" — `revised_direct_impact`
- L361 — "Al Anaissy et al. 2024, Definition 13" — `shapley_attack_impacts`

### `src/argumentation/gradual_principles.py`
- L57, L83, L105 — "Baroni, Rago, and Toni 2019, IJAR 105" (pp. 252-286, p.258, pp.258-259 GPs 7-11)

### `src/argumentation/labelling.py`
- L147, L163 — "Caminada 2006, p. 3" — labelling rules
- L196 — "Caminada 2006 reinstatement" — complete labellings
- L225 — "Caminada 2006, p. 5" — grounded labelling
- L269 — "Caminada 2006, pp. 6-7" — semi-stable labelling

### `src/argumentation/matt_toni.py`
- L22 — "Matt and Toni 2008, JELIA, p. 291, Definition 6" — strength function

### `src/argumentation/partial_af.py`
- L291 — "Coste-Marquis et al. 2007" — merge distance helper

### `src/argumentation/practical_reasoning.py`
- L17, L45, L152, L171, L196 — "Atkinson & Bench-Capon 2007" (pp. 858, 860-861, 862 CQ5/CQ6/CQ11) — AS1 helpers and CQ generators

### `src/argumentation/preference.py`
- L54 — "Modgil & Prakken 2018, Def 19" — `strictly_weaker`

### `src/argumentation/probabilistic.py`
- L7 — "Li et al. (2012, Algorithm 1)" — module docstring
- L8 — "Hunter & Thimm (2017, Prop 18)" — module docstring
- L664, L665 — Li 2012 / Hunter & Thimm 2017 — sampler entry
- L776, L856 — "Li (2012, p.2)" — deterministic strategy / acceptance helper
- L787 — "Li 2012, p.8: exact beats MC below ~13 args" — auto-router
- L811 — "Popescu & Wallner 2024" — auto-router exact_dp branch
- L911, L960, L963 — "Li et al. (2012, Algorithm 1, p.5)"; "Li et al. (2012, Eq. 5, p.7)" — MC routine
- L1023 — "Hunter & Thimm (2017, Prop 18)" — component decomposition
- L1123 — "Agresti-Coull stopping (Li 2012, Eq. 5, p.7)" — sampler comment
- L1184 — "Li et al. (2012, p.3-4)" — exact enum
- L1260 — "Popescu & Wallner (2024)" — `paper_td` strategy
- L1393 — "Freedman et al. (2025, p.3)" — DF-QuAD strategy
- L1399 — "Li 2012's P_A is currently used as Rago 2016's τ" — design note (signals an interpretation choice)

### `src/argumentation/probabilistic_components.py`
- L14 — "Hunter & Thimm (2017, Prop 18)" — component decomposer

### `src/argumentation/probabilistic_treedecomp.py`
- L3 — "Popescu & Wallner (2024)" — module docstring; explicitly states code "is currently an adapted grounded-semantics edge-tracking backend, not their full I/O/U witness-table algorithm"
- L54, L70, L84 — "Popescu & Wallner (2024, p.4-5 / p.5)" — `TreeDecomposition`, `NiceTDNode`, `NiceTreeDecomposition`
- L174 — "Popescu and Wallner's TD tables" — `PaperTDLabel`
- L185 — "Popescu and Wallner 2024, p.590" — `PaperTDRow`
- L200 — "Popescu and Wallner 2024, Algorithm 1 line 4" — `paper_leaf_rows`
- L226 — "first narrow part of Popescu and Wallner 2024" — `paper_introduce_rows`
- L305 — "Popescu and Wallner 2024, Algorithm 3" — `paper_forget_rows`
- L363 — "Popescu and Wallner 2024, Algorithm 4" — `paper_join_rows`
- L419 — "Popescu and Wallner 2024, Algorithm 1 evaluates a nice tree decomposition" — `compute_paper_exact_extension_probability`
- L755, L771, L820 — "Popescu & Wallner (2024, p.4 / p.4-5)" — primal-graph builders / TD validation
- L972 — "Popescu & Wallner (2024, p.5)" — nice TD conversion
- L1131 — "is not the full Popescu & Wallner I/O/U witness-table DP" — `compute_exact_dp` warning
- L1162 — "Reuses Popescu & Wallner-style nice tree decompositions" — section header
- L1226, L1340 — "Popescu & Wallner (2024, Algorithms 1-3)" — grounded DP
- L1230 — "Hunter & Thimm (2017, Prop 18)" — grounded DP
- L1234 — "Dung 1995, Theorem 25" — grounded DP
- L1461 — "Dung 1995, Definition 20" — fixpoint computation
- L1634 — "Popescu & Wallner (2024, p.6)" — combine compatible rows

### `src/argumentation/ranking.py`
- L44 — "Besnard-Hunter Categoriser" — `categoriser_ranking`
- L46 — "Bonzon et al. 2016, Definition 9" — same
- L109 — "Bonzon et al. 2016, Definitions 15-16" — burden ranking
- L155 — "Amgoud and Ben-Naim 2013" — discussion-based ranking

### `src/argumentation/ranking_axioms.py`
- L4 — "Amgoud and Ben-Naim 2013 pp. 3-8 and Bonzon et al. 2016 pp. 1-2" — module docstring
- L38, L79, L102, L135, L158, L177, L198, L247 — "Amgoud and Ben-Naim 2013" with explicit p. 3 / 4 / 4-5 / 5 / 6 / 6 / 8 / 8 cites — axiom checks
- L120, L224, L272 — "Bonzon et al. 2016 p. 1 / p. 5" — axiom checks

### `src/argumentation/subjective_aspic.py`
- L35 — "Wallner et al. 2024, Definition 11" — subjective KB helper
- L76 — "Wallner et al. 2024, Definition 13" — defeasible-rule survival
- L101 — "Wallner et al. 2024, Definitions 12-14" — combined filter

### `src/argumentation/vaf.py`
- L3 — "Bench-Capon 2003 extends Dung AFs" — module docstring
- L24 — "Bench-Capon 2003 p. 435, Definition 5.1" — `ValueArgumentationFramework`
- L108 — "p. 436, Definition 5.3" — defeat helper
- L149, L165 — "p. 437, Definitions 6.1/6.2" — acceptance helpers

### `src/argumentation/vaf_completion.py`
- L1 — "Bench-Capon 2003 chain, line, and fact-value VAF helpers" — module docstring
- L17 — "Bench-Capon 2003 p. 440 Theorem 6.6" — status classes
- L28 — "Bench-Capon 2003 p. 438, Definition 6.3" — chain numbering
- L65 — "Bench-Capon 2003 p. 439, Definition 6.5" — chain link helper

### `src/argumentation/weighted.py`
- L17 — "Dunne et al. 2011, Definitions 4-6" — weighted system class

## Citations in docs (file:line, citation)

### `README.md`
- L77 — "Modgil & Prakken (2018) Def 14"
- L85-87 — "Caminada 2011", "Gaggl & Woltran 2013", "Dung, Mancarella & Toni 2007"
- L116-119 — "Dung, P. M. (1995). On the acceptability of arguments..."
- L119 — "Caminada, M. (2011). Semi-stable semantics. In *COMMA 2006*."
- L120-121 — "Gaggl, S. A. & Woltran, S. (2013). The cf2 argumentation semantics revisited"
- L122-123 — "Dung, P. M., Mancarella, P. & Toni, F. (2007). Computing ideal sceptical argumentation"
- L183-184 — "Modgil, S. & Prakken, H. (2018). A general account of argumentation with preferences"
- L212-213 — "Lehtonen, Niskanen & Järvisalo 2024"
- L236-237 — "Lehtonen, T., Niskanen, A., & Järvisalo, M. (2024). Reasoning over ASPIC+ in answer set programming. *KR 2024*"
- L238-239 — "Odekerken, D., Borg, A. & Bex, F. (2023). Justification, stability and relevance for case-based reasoning..."
- L267-268 — "Cayrol, C. & Lagasquie-Schiex, M.-C. (2005). On the acceptability of arguments in bipolar argumentation frameworks. In *ECSQARU 2005*"
- L336-337 — "Baumann, R. (2015). Context-free and context-sensitive kernels: update and deletion equivalence in abstract argumentation. In *ECAI 2014*"
- L338-339 — "Diller, M., Haret, A., Linsbichler, T., Rümmele, S., & Woltran, S. (2015). An extension-based approach to belief revision in abstract argumentation"
- L340-341 — "Cayrol, C., de Saint-Cyr, F. D., & Lagasquie-Schiex, M.-C. (2014). Change in abstract argumentation frameworks: adding an argument"
- L377-393 — strategy table cites Li et al. 2012, Hunter & Thimm 2017 Prop 18, Popescu & Wallner 2024, Freedman et al. 2025
- L416-417 — "Li, H., Oren, N., & Norman, T. J. (2012). Probabilistic argumentation frameworks. In *TAFA 2011*"
- L418-419 — "Hunter, A. & Thimm, M. (2017). Probabilistic reasoning with abstract argumentation frameworks. *JAIR*, 59, 565–611"
- L420-421 — "Popescu, A. & Wallner, J. P. (2024). Tree-decomposition-based dynamic programming for probabilistic abstract argumentation"
- L422-424 — "Freedman, G., Rago, A., Albini, E., Toni, F., & Cocarascu, O. (2025). Argumentative Large Language Models for explainable and contestable claim verification"
- L466 — "Al Anaissy et al. 2024, Definition 13"
- L468-479 — Wallner-style filtering, Bench-Capon VAF, Atkinson and Bench-Capon AATS
- L557 — "Modgil & Prakken Def 19"

### `docs/architecture.md`
- L9 — "Dung 1995"
- L10-12 — "Caminada 2011", "Gaggl & Woltran 2013", "Dung, Mancarella & Toni 2007"
- L23-24 — "Modgil & Prakken 2018"
- L26 — "Lehtonen, Niskanen & Järvisalo 2024"
- L33 — "Bondarenko et al. 1997; Čyras & Toni 2016"
- L36 — "Brewka & Woltran 2010; Brewka et al. 2013"
- L44-45 — "Baumann 2015; Diller 2015; Cayrol 2014"
- L48-50 — "Li et al. 2012; Popescu & Wallner 2024; Freedman et al. 2025"
- L52-53 — "Hunter & Thimm 2017, Proposition 18"
- L67 — "Al Anaissy et al. 2024"
- L70-72 — "Bench-Capon"; "Atkinson and Bench-Capon"
- L81 — "Modgil & Prakken 2018 Def 19"
- L131 — "Popescu & Wallner (2024) Algorithm 1"
- L164-165 — "Modgil & Prakken 2018 Def 14"; "Dung 1995 Def 6"

### `CITATIONS.md`
- L5-7 — `argumentation.dung.stable_extensions` cites Dung 1995 Def 12
- L9-13 — same function notes "Modgil and Prakken preference-aware split"
- L17-22 — `argumentation.probabilistic` strategy `exact_dp` notes deliberate divergence from Popescu and Wallner (2024); "adapted grounded-acceptance edge-tracking backend, not their full I/O/U witness-table algorithm"; states "currently supports only credulous grounded acceptance on defeat-only worlds (no support relations, attacks == defeats)"
- L24-26 — `exact_dp` "tables key on full edge sets and forgotten arguments" — asymptotic-complexity divergence note
- L28-30 — `paper_td` strategy "is the paper-faithful Popescu and Wallner Algorithm 1 ... opt-in and answers extension_probability queries only"

## Distinct citations cross-checked vs propstore

(`HIT` = directory exists; slug given in parens. `MISMATCH` = a structural mismatch between
the in-text citation and the available propstore directory. `MISS` = no directory found.)

- Dung 1995 — HIT: `Dung_1995_AcceptabilityArguments`
  (NOTE: prompt suggested slug `Dung_1995_AcceptabilityArgumentsFundamental`; actual ends at `…AcceptabilityArguments`.)
- Modgil & Prakken 2018 — HIT: `Modgil_2018_GeneralAccountArgumentationPreferences`
- Prakken 2010 — HIT: `Prakken_2010_AbstractFrameworkArgumentationStructured`
- Prakken 2019 — HIT: `Prakken_2019_ModellingAccrualArgumentsASPIC`
- Caminada 2006 — HIT: `Caminada_2006_IssueReinstatementArgumentation`
- Caminada 2007 — HIT: `Caminada_2007_EvaluationArgumentationFormalisms`
- Caminada 2011 (semi-stable, COMMA 2006) — MISMATCH (year): no `Caminada_2011_*` dir; closest is `Caminada_2006_IssueReinstatementArgumentation`. README L119 itself states "Caminada, M. (2011). Semi-stable semantics. In *COMMA 2006*." — venue/year split.
- Cayrol & Lagasquie-Schiex 2005 — HIT: `Cayrol_2005_AcceptabilityArgumentsBipolarArgumentation`
- Cayrol 2014 — HIT: `Cayrol_2014_ChangeAbstractArgumentationFrameworks`
- Cayrol, de Saint-Cyr, Lagasquie-Schiex 2010 (af_revision.py:335, JAIR 38) — MISS: no `Cayrol_2010_*` dir.
- Popescu & Wallner 2024 — HIT (multiple): `Popescu_2024_AlgorithmicProbabilisticArgumentationConstellation`, `Popescu_2024_AdvancingAlgorithmicApproachesProbabilistic`, `Popescu_2024_ProbabilisticArgumentationConstellation`
- Hunter & Thimm 2017 — HIT: `Hunter_2017_ProbabilisticReasoningAbstractArgumentation`
- Li et al. 2012 — MISMATCH (year): closest is `Li_2011_ProbabilisticArgumentationFrameworks` (TAFA 2011 proceedings). README L416-417 acknowledges venue is TAFA 2011 but cites year 2012. Same paper.
- Baumann 2014 (af_revision.py:181/198, ECAI pp. 63-68) — MISS / MISMATCH: no `Baumann_2014_*` dir; only `Baumann_2010_*`, `Baumann_2015_AGMMeetsAbstractArgumentation`, `Baumann_2019_AGMContractionDung` exist. README L336 cites this same Baumann work as "Baumann (2015) … In *ECAI 2014*", suggesting the 2014/2015 split is publication-year vs venue-year.
- Baumann 2015 — HIT: `Baumann_2015_AGMMeetsAbstractArgumentation`
- Diller 2015 — HIT: `Diller_2015_ExtensionBasedBeliefRevision`
- Diller et al. 2025 (aspic.py:30 Def 7) — HIT: `Diller_2025_GroundingRule-BasedArgumentationDatalog`
- Brewka & Woltran 2010 — HIT: `Brewka_2010_AbstractDialecticalFrameworks`
- Brewka et al. 2013 — HIT: `Brewka_2013_AbstractDialecticalFrameworksRevisited`
- Bondarenko et al. 1997 — HIT: `Bondarenko_1997_AbstractArgumentation-TheoreticApproachDefault`
- Cyras & Toni 2016 — HIT: `Čyras_2016_ABAAssumption-BasedArgumentationPreferences` (Č Unicode)
- Toni 2014 — HIT: `Toni_2014_TutorialAssumption-basedArgumentation`
- Lehtonen, Niskanen & Järvisalo 2024 — HIT (slug differs): `Lehtonen_2024_PreferentialASPIC`. The propstore slug names "PreferentialASPIC" while README L237 says "Reasoning over ASPIC+ in answer set programming. KR 2024" — same authors+year but different paper title in slug; could be a different Lehtonen 2024 paper.
- Odekerken Borg Bex 2023 — HIT: `Odekerken_2023_ArgumentationReasoningASPICIncompleteInformation`
- Bench-Capon 2003 — HIT: `Bench-Capon_2003_PersuasionPracticalArgumentValue-based`
- Atkinson & Bench-Capon 2007 — HIT: `Atkinson_2007_PracticalReasoningPresumptiveArgumentation`
- Al Anaissy et al. 2024 — HIT: `AlAnaissy_2024_ImpactMeasuresGradualArgumentation` (note: no underscore between "Al" and "Anaissy")
- Freedman et al. 2025 — HIT: `Freedman_2025_ArgumentativeLLMsClaimVerification`
- Gaggl & Woltran 2013 — HIT: `Gaggl_2013_CF2ArgumentationSemanticsRevisited` (also `Gaggl_2012_CF2ArgumentationSemanticsRevisited`)
- Coste-Marquis, Devred, Marquis 2005 (prudent semantics) — HIT: `Coste-Marquis_2005_PrudentSemantics`
- Coste-Marquis et al. 2007 (merging) — HIT: `Coste-Marquis_2007_MergingDung'sArgumentationSystems`
- Pollock 1987 — HIT: `Pollock_1987_DefeasibleReasoning`
- Besnard & Hunter 2001 — HIT: `Besnard_2001_Logic-basedTheoryDeductiveArguments`
- de Kleer 1986 — HIT: `deKleer_1986_AssumptionBasedTMS` and `deKleer_1986_ProblemSolvingATMS`
- Polberg 2017 — HIT: `Polberg_2017_DevelopingAbstractDialecticalFramework`
- Dung, Mancarella & Toni 2007 — HIT: `Dung_2007_ComputingIdealScepticalArgumentation`
- Rago et al. 2016 (KR — DF-QuAD) — HIT: `Rago_2016_DiscontinuityFreeQuAD` (DF-QuAD original)
- Rago, Cyras & Toni 2016 (SAFA) — HIT: `Rago_2016_AdaptingDFQuADBipolarArgumentation`
- Baroni, Rago & Toni 2019 — HIT: `Baroni_2019_GradualArgumentationPrinciples`
- Potyka 2018 — HIT: `Potyka_2018_ContinuousDynamicalSystemsWeighted`
- Bonzon et al. 2016 — HIT: `Bonzon_2016_ComparativeStudyRanking-basedSemantics`
- Riveret 2017 — HIT: `Riveret_2017_LabellingFrameworkProbabilisticArgumentation`
- Matt & Toni 2008 — HIT: `Matt_2008_Game-TheoreticMeasureArgumentStrength`
- Dunne et al. 2011 — HIT: `Dunne_2011_WeightedArgumentSystemsBasic`
- Gabbay 2012 — HIT: `Gabbay_2012_EquationalApproachArgumentationNetworks`
- Wallner et al. 2024 (subjective_aspic.py) — HIT: `Wallner_2024_ValueBasedReasoningInASPIC`
- Amgoud & Ben-Naim 2013 — HIT: `Amgoud_2013_Ranking-BasedSemanticsArgumentationFrameworks`
- Amgoud et al. 2008 — HIT: `Amgoud_2008_BipolarityArgumentationFrameworks`

## Section A — cited but missing from propstore

- **Cayrol, de Saint-Cyr, Lagasquie-Schiex 2010, JAIR 38** (cited at `af_revision.py:335` for Table 3 of grounded-argument-addition classification). No `Cayrol_2010_*` directory exists in `propstore/papers/`.
- **Baumann 2014, ECAI pp. 63-68** (cited at `af_revision.py:181` and `af_revision.py:198` for stable-kernel characterisation). No `Baumann_2014_*` directory exists. README L336 cites the same work as Baumann 2015 (publication year) in ECAI 2014 (venue year), suggesting publication/venue-year disagreement; the only Baumann directory plausibly matching is `Baumann_2015_AGMMeetsAbstractArgumentation`, but the title does not obviously match an ECAI 2014 kernel-equivalence paper.

## Section B — name/year mismatches

- **Caminada 2011 ↔ propstore Caminada 2006.** Code (`dung.py:325`) cites "Caminada 2011, Definition 2.3" for `semi_stable_extensions`. README L119 cites "Caminada (2011). Semi-stable semantics. In *COMMA 2006*." Propstore has only `Caminada_2006_IssueReinstatementArgumentation` (a different paper) and `Caminada_2007_EvaluationArgumentationFormalisms`. There is no propstore directory whose slug names "SemiStable" or year 2011. The actual "Semi-Stable Semantics" paper (COMMA 2006) is unrepresented under either year label in propstore (could not be located by `grep Caminada` over the directory listing).
- **Li 2012 ↔ propstore Li 2011.** Code consistently cites "Li et al. 2012" / "Li 2012". Propstore has `Li_2011_ProbabilisticArgumentationFrameworks` (TAFA 2011). README L416 explicitly resolves: "Li, H., Oren, N., & Norman, T. J. (2012). … In *TAFA 2011*." Same paper, year-label disagreement only.
- **Baumann 2014 ↔ Baumann 2015.** Code (`af_revision.py:181`) cites "Baumann 2014, ECAI pp. 63-68"; README L336-337 cites "Baumann (2015). Context-free and context-sensitive kernels: update and deletion equivalence in abstract argumentation. In *ECAI 2014*." Propstore directory `Baumann_2015_AGMMeetsAbstractArgumentation` has a different title — so even the README's bibliographic entry does not obviously match the available propstore slug. Cannot confirm which Baumann paper the propstore directory holds without reading its contents (out of scope per the prompt, which forbids PDF reads).
- **Lehtonen 2024 (KR — ASPIC+ ASP) ↔ propstore `Lehtonen_2024_PreferentialASPIC`.** Authors and year match, but propstore slug names "PreferentialASPIC", not "Reasoning over ASPIC+ in answer set programming". The propstore directory may be a different Lehtonen 2024 paper than the one cited.
- **Cyras & Toni 2016 ↔ `Čyras_2016_ABAAssumption-BasedArgumentationPreferences`.** Source code (e.g. `aba.py:6`) writes the ASCII spelling "Cyras"; the propstore directory uses Unicode "Č". Not a content mismatch — only a unicode/normalisation note for any string-equality lookups.
- **Al Anaissy 2024 ↔ `AlAnaissy_2024_ImpactMeasuresGradualArgumentation`.** Code (e.g. `gradual.py:299`) writes "Al Anaissy" with a space; the propstore directory has no underscore between "Al" and "Anaissy". String-equality note only.
- **Brewka 2013 ↔ `Brewka_2013_AbstractDialecticalFrameworksRevisited`.** No mismatch — the directory matches; included here only to flag that `aba.py:3` uses comma serial form ("Bondarenko, Dung, Kowalski, and Toni 1997") while the propstore slug uses only the first author. Standard convention; not a problem.

## Section C — CITATIONS.md divergence claims verified

`CITATIONS.md` describes two divergence/clarification points:

1. **`argumentation.dung.stable_extensions` — "preference-aware split"** (CITATIONS.md L9-13).
   Claim: when an `ArgumentationFramework` includes both `attacks` and `defeats`, stable
   extensions are attack-conflict-free over `attacks` and defeat every outsider via `defeats`.
   Verification: `dung.py:271-291` shows `stable_extensions` reading
   `cf_relation = framework.attacks if framework.attacks is not None else framework.defeats`
   and computing `stable_labellings` (which uses defeats for outsider coverage), then
   filtering by `conflict_free(labelling.extension, cf_relation)`.
   Result: code matches the stated divergence/behavior in CITATIONS.md.

2. **`argumentation.probabilistic` strategy `exact_dp` — adapted, not paper-faithful**
   (CITATIONS.md L17-30).
   Claim: `exact_dp` is an adapted grounded-acceptance edge-tracking backend, only
   credulous grounded on defeat-only worlds, not the paper's I/O/U witness-table DP;
   `paper_td` is the paper-faithful Algorithm 1 for extension-probability queries only.
   Verification: `probabilistic_treedecomp.py:1-17` module docstring explicitly states
   "the executable DP is currently an adapted grounded-semantics edge-tracking backend,
   not their full I/O/U witness-table algorithm" and "Current native support is intentionally
   narrower than the paper: grounded semantics on defeat-only probabilistic worlds where
   `attacks == defeats` and there are no support relations." The `supports_exact_dp`
   gate at L32-43 enforces these constraints (returns False unless semantics == "grounded",
   no support relations, and attacks == defeats). The `compute_paper_exact_extension_probability`
   surface at L411-428 accepts only `semantics="complete"`, raises on support relations
   and on `attacks != defeats`, and L419 cites "Popescu and Wallner 2024, Algorithm 1
   evaluates a nice tree decomposition bottom-up using I/O/U-labelled rows with witnesses."
   Result: code matches both halves of the CITATIONS.md statement (divergent `exact_dp`
   plus opt-in paper-faithful `paper_td`).

## Spot-checks

### 1. Dung 1995 — `dung.py` defeats vs Definition numbers
- Code references (with explicit definitions cited):
  - `dung.py:201` — grounded "Definition 20 + Theorem 25 (least fixed point)"
  - `dung.py:226` — complete "Definition 10"
  - `dung.py:261` — preferred "Definition 8"
  - `dung.py:279` — stable "Definition 12"
  - `dung.py:136` — characteristic_fn "Definition 17"
  - `dung.py:173` — defends "Definition 6"
- Propstore `Dung_1995_AcceptabilityArguments/notes.md` lists the actual Dung 1995
  definitions as:
  - Def 2 (AF), Def 5 (conflict-free), Def 6 (acceptability/admissibility),
    Def 7 (preferred extension), Def 13 (stable extension), Def 16 (characteristic
    function), Def 20 (grounded extension), Def 23 (complete extension).
- Comparison:
  - Code "grounded = Def 20 + Theorem 25" → notes.md says grounded extension is
    Def 20 (least fixed point of $F_{AF}$) and Theorem 25 establishes the relation.
    **MATCH.**
  - Code "preferred = Def 8" → notes.md gives **Def 7** for preferred extension.
    **MISMATCH** (off by one — code cites Def 8, paper notes give Def 7).
  - Code "complete = Def 10" → notes.md gives **Def 23** for complete extension.
    **MISMATCH.** Lemma 24 (p.330) characterises complete via $E = F_{AF}(E)$.
  - Code "stable = Def 12" → notes.md gives **Def 13** for stable extension; Corollary
    12 is "Every argumentation framework possesses at least one preferred extension."
    **MISMATCH** (off by one).
  - Code "characteristic_fn = Def 17" → notes.md gives **Def 16** for characteristic
    function. **MISMATCH** (off by one).
  - Code "defends = Dung 1995 Def 6" → notes.md gives Def 6 = acceptability and
    admissibility (covers "defends"). **MATCH** in spirit (Def 6 is the right anchor
    for the "defends" / acceptability concept).
- Summary: definition numbers in `dung.py` are off-by-one from those in the
  propstore notes for preferred (8 vs 7), stable (12 vs 13), characteristic_fn
  (17 vs 16), and complete (10 vs 23 — large mismatch). Cannot determine without
  reading the PDF whether the propstore notes or the code is using a different
  numbering convention (e.g. Lemma vs Definition labelling, journal vs reprint
  numbering); reporting observation only.

### 2. Popescu & Wallner 2024 `paper_td` — Algorithm 1
- `probabilistic_treedecomp.py:419` claims "Popescu and Wallner 2024, Algorithm 1
  evaluates a nice tree decomposition bottom-up using I/O/U-labelled rows with
  witnesses."
- Propstore `Popescu_2024_AlgorithmicProbabilisticArgumentationConstellation/notes.md`
  L122-126: "Algorithm 1: Main DP — Compute nice tree-decomposition of primal PAF
  graph; Initialize empty table for each bag; Process bottom-up (post-order
  traversal); At root, sum probabilities of all valid complete extensions."
- L114-120: "Each bag maintains a table of rows, each row is a tuple: $E_i$ partial
  subframework; $att_i$ attacks; $c_i$ complete labelling candidate (in/out/undec);
  $p_i$ probability; $w_i$ witness."
- L173-174 of source ("PaperTDLabel" enum and "I/O/U labels used by Popescu and
  Wallner's TD tables") aligns with notes "in/out/undec".
- Result: code's claim matches paper's notes.md description. **MATCH.**

### 3. Brewka et al. 2013 — operator semantics
- `adf.py:4` claims "Brewka et al. 2013 recast ADF semantics through the three-valued
  consensus operator."
- Propstore `Brewka_2013_AbstractDialecticalFrameworksRevisited/notes.md` L41-43:
  "$\Gamma_D(v)(s) = \bigsqcap \{ w(\varphi_s) \mid w \in [v]_2 \}$ ... the meet
  takes the consensus truth value over all such completions. The grounded model is
  the least fixpoint of this operator."
- L83 of notes: "Three-valued interpretations use Kleene truth values $t,f,u$".
- Result: code's "three-valued consensus operator" claim matches notes.md
  characterisation of $\Gamma_D$ as a consensus over two-valued completions.
  **MATCH.**

## Notes on coverage

- The grep walk over `src/argumentation/*.py` was exhaustive against the
  patterns used; results saved in
  `~/.claude/projects/.../tool-results/toolu_0155uBjvFmb5GHdqMFvHAdcv.txt`
  (194 lines) and `…/toolu_01C7fRpft8SWEgc72fw8uomA.txt` (containing additional
  passes for Wallner / Niskanen / Atkinson / Pollock / Besnard / de Kleer).
- `tests/`, `notes/`, and `out/` were not surveyed (out of task scope).
- I did not read any propstore PDFs; only `notes.md` files for the three
  spot-check papers were consulted, per the prompt instruction.
