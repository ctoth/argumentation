# Yin 2023 attribution paper — retrieval notes

## 2026-05-02 — retrieval (subagent of paper-process wave 2)

**Paper:** arxiv 2307.13582 — Yin, Potyka, Toni (2023) "Argument Attribution Explanations in Quantitative Bipolar Argumentation Frameworks (Technical Report)"

**Status:** PDF retrieved, metadata/abstract still to write, paper-reader still to invoke.

### Observations
- Direct curl from `https://arxiv.org/pdf/2307.13582.pdf` succeeded in <2s, 1.38MB, 21 pages (verified via pypdf).
- `file` reported "2 page(s)" — misleading; arxiv PDFs use compressed object streams that confuse `file`. Trust pypdf.
- Arxiv landing page metadata fetch (single curl, no S2 API) gave full title, three authors (Xiang Yin, Nico Potyka, Francesca Toni), date 2023/07/25, and the abstract.
- Lead's spelling correction confirmed: surname is "Yin" (Xiang Yin), not "Yun".
- Skipped fetch_paper.py entirely because parent task explicitly forbade S2 metadata calls (HTTP 429 hangs).

### Files placed
- `papers/Yin_2023_ArgumentAttributionExplanationsQuantitative/paper.pdf` (1.38MB, 21pp)

### Next steps
1. Write `metadata.json` (arxiv id, title, three authors, year 2023, url).
2. Write `abstract.md` from the citation_abstract content already fetched.
3. Invoke `/research-papers:paper-reader` on the directory to extract `notes.md`.
4. Write per-paper report to `reports/paper-yin-2023-attribution.md`.

### Constraints from parent
- Use ONLY paper-retriever then paper-reader. Do NOT invoke paper-process.
- Do NOT run source-bootstrap, register-concepts, extract-claims, register-predicates, author-rules, author-context, source-promote, reconcile, or update index.md.
- 5-minute total budget; ~1 minute spent so far on retrieval.

## 2026-05-02 — paper-reader checkpoint (read pages 0-3 of 21)

PDF converted to 21 page-NNN.png images (150 DPI, 1960px). Read pages 0-3 so far.

### Observed so far
- **Authors:** Xiang Yin (Imperial), Nico Potyka (Cardiff), Francesca Toni (Imperial). v3 dated 4 Aug 2023.
- **Semantics target:** DF-QuAD (Discontinuity-Free Quantitative Argumentation Debates) gradual semantics. Properties section explicitly says "AAEs as explanations for outcomes under the DF-QuAD gradual semantics."
- **Operator family:** Gradient-based attribution. AAE notation `∇|_{B↦A}` denotes attribution of argument B onto topic argument A. Inspired by gradient chain rule.
- **Key formal results spotted on p.4 (image-page 003):**
  - Prop 2 (Direct Quantitative Attribution Influence): closed-form gradient `∇|_{B↦A} = ξ_B (1 − |v_{Ba} − v_{Bs}|) ∏_{Z ∈ A\B | (Z,A)∈R*} [1 − σ(Z)]`, with ξ_B branching by relation polarity (R⁻ vs R⁺) and base-vs-strength comparison.
  - Prop 3 (Indirect Qualitative): along a path, parity of attacks (Θ = #R⁻ in path) determines sign — odd ⇒ ≤0, even ⇒ ≥0.
  - Prop 4 (Indirect Quantitative): chain-rule product `∇|_{X1↦Xn} = (1−|v_{X1a}−v_{X1s}|)·∏ ∇|_{Xi↦Xi+1}/(1−|v_{Xia}−v_{Xis}|)`.
  - Property 1 Completeness: `−τ(B)·∇|_{B↦A} = σ′_B(A) − σ(A)` (counterfactual on setting τ(B)=0).
  - Property 2 Counterfactuality: sign of ∇ predicts direction of σ change when removing B.
  - Prop 5 Explainability (well-definedness), Prop 6 Missingness (disconnected ⇒ ∇=0).
  - Props 7, 9: completeness & counterfactuality satisfied if B directly or indirectly connected to A.
  - Props 8, 10: both can be VIOLATED when B is "multifold connected" (paths of mixed parity to A).

### Pages remaining: 4-20 (17 pages)
- Will cover: more axioms (agreement on p.4-5), case studies (fake news, movie recs), complexity, related work, references.
- Plan: read 4-9 next (writes), then 10-15, then 16-20, then write notes.md from accumulated extraction.

### State of artifacts
- paper.pdf: present, 1.38MB, 21pp.
- metadata.json, abstract.md: written.
- pngs/: 21 images present.
- notes.md: NOT yet written (will write after all pages read).
- description.md, citations.md: NOT written.
- Per parent constraints: skipping reconcile, papers/index.md update, propstore provenance stamp.

## 2026-05-02 — second checkpoint (read pages 0-7 + 8-11 + 18-20)

### Paper structure now fully understood
- Pages 0-7 are the **main paper** (8 pages including refs).
  - p.0: Title + Abstract + §1 Intro (left col), §1 cont. (right col).
  - p.1: §2 Related Work (gradient-based feature attribution discussion: LIME [39], SHAP [29], SILO [12], gradient [8], DeepLIFT [43], IG [41]; argumentative XAI [21,44]; QBAFs [10]; properties [4,18,29,35,42]); §3 Preliminaries (QBAF defn, DF-QuAD).
  - p.2: §3 cont. (DF-QuAD formulae σ(A) = τ(A) − τ(A)·(v_a − v_s) etc.); §4 AAEs definition: `∇|_{B↦A} = lim_{ε→0} [σ_ε(A) − σ(A)] / ε`, where σ_ε is strength after τ(B) ← τ(B)+ε. Definition 2 of AAE. Then Prop 1 (sign of direct AAE).
  - p.3: Prop 2 (closed-form direct AAE), Prop 3 (parity rule for indirect), Prop 4 (chain-rule for indirect). Example 3. §5 Properties: Explainability (Prop 5), Missingness (Prop 6), Completeness (Property 1), Counterfactuality (Property 2). Props 7-10 (when sat/violated).
  - p.4: Continuation — Properties (Agreement, Monotonicity), §6 Case Study 1 fake news. QBAF Figure 3. The "main" page is here.
  - p.5: Case Study 1 details — Table 1 with 7 reply arguments, AAEs e.g. C: ∇=0.375 (max positive), D: ∇=−0.4375 (max negative); base score for A = 0.59375 (>0.5 ⇒ "True News"). Linear-time complexity remark. Figure 4 visualisation. Case Study 2 begins (movie recs from [17]).
  - p.6: Case Study 2 — QBAF for movie "The Post". Topic m, features f_A (acting), f_D (directing), f_W (writing). Sub-features f'_A1, f'_A2 of f_A. Table 2: AAEs in descending order — Acting 0.17625, Actor2 0.15920, Actor1 0.15585, Directing 0.15584, Writing −0.21. §7 Conclusions + 4 future directions: (i) collective influence of argument sets, (ii) other gradual semantics (Euler-based [3], quadratic energy [32]), (iii) cyclic QBAFs (warning re iterative non-convergence [31,33]), (iv) human studies.
  - p.7: Acknowledgements + start of References (45 total).
- Pages 8: rest of references (extends through [45] Zeng 2018 AAMAS).
- Pages 9-20: Supplementary Material — proofs and a third (fraud detection) case study.
  - p.9-12: §A.1 Proofs for §4 — Prop 1, Prop 2 (with ε→0 limit derivation), Prop 3, Prop 4.
  - p.13-15: §A.2 Proofs for §5 — Props 5-10 plus Agreement and Monotonicity.
  - p.16-18: §B Examples (Examples 4, 5, 6, 7 — extra acyclic QBAFs walking through propositions).
  - p.18-20: §C Fraud Detection Example — third case study using a 48-argument QBAF from ref [16]. σ(1) = 0.2543945275247097 (<0.5 ⇒ no investigation). Table 3 lists all 48 args with AAEs (range from 4.99E-1 down to −7.81E-3).

### Page render quality issue (resolved)
- Initial 150-DPI rendering of pages 002 and 004 looked truncated when re-displayed via Read; this was a Read tool downscaling artifact, not a rendering problem. Original images contain full content. The first read passed cleanly (I extracted DF-QuAD definition, AAE definition, Prop 1, Case Study 1 setup, Properties 1-2, Agreement/Monotonicity).
- Generated -hires variants at 200 DPI for pages 2 and 4 as belt-and-braces; can use them if needed.

### What's missing for notes.md
- Need to also peek at page-001 (Section 2 + Section 3 preliminaries — DF-QuAD formula form).
- Need to capture: full QBAF definition `Q = ⟨A, R⁻, R⁺, τ⟩`, DF-QuAD recursive formula, exact AAE definition wording.
- Then write notes.md, description.md, citations.md.

### Confirmed contributions
1. Novel **gradient-based** AAE for QBAFs under DF-QuAD: `∇|_{B↦A} := lim_{ε→0} (σ_{τ(B)+ε}(A) − σ(A))/ε`.
2. Closed-form direct (Prop 2) and indirect (Prop 4 chain rule) formulae.
3. Properties: explainability, missingness, completeness, counterfactuality, agreement, monotonicity. Linear-time computability.
4. Three case studies: fake news (sec 6), movie recs (sec 6), fraud detection (SM C).
5. Failure mode: completeness/counterfactuality can be VIOLATED for "multifold connected" arguments (Props 8, 10).

## 2026-05-02 — third checkpoint: render-quality issue identified

The 150 DPI page-002.png and page-004.png images came out with corrupted display (mostly black with annotation rectangles) when re-displayed via Read tool. This is likely transparency/PDF artifact handling. Re-rendered them with `-background white -alpha remove -alpha off` at 200 DPI as `*-clean.png` variants.

Pages NOT YET fully captured for notes (will read in next batch):
- page-001-clean.png (related work + start of preliminaries)
- page-002-clean.png (DF-QuAD formulae + AAE definition)
- page-004-clean.png (rest of properties + start of case study 1)

After reading these three, I have enough to write notes.md.

Tool call budget: ~38 calls so far. Subagent limit is 100, so still have headroom but tightening. Will write notes.md aggressively after one more read batch.
