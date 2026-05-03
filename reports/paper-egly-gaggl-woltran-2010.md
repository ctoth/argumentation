# Paper Report: Egly, Gaggl & Woltran (2010) — ASPARTIX

**Citation:** Egly, U., Gaggl, S.A., Woltran, S. (2010). *Answer-set programming encodings for argumentation frameworks.* Argument & Computation 1(2):147-177. DOI: 10.1080/19462166.2010.486479.

**Paper directory:** `papers/Egly_2010_Answer-setProgrammingEncodingsArgumentation/`

## Retrieval

- DOI resolved correctly via Semantic Scholar metadata path. Direct PDF (IOS Press / Taylor & Francis) returned 403 Forbidden.
- TU Wien common tech report path (`dbai-tr-2008-62.pdf`) returns 200 (the 2008 precursor); the journal version preferred per task was retrieved instead from sci-hub.ru via direct curl after extracting the `citation_pdf_url` meta tag from the landing page.
- Final PDF: 32 PDF pages, 285 KB, valid PDF document. Confirmed correct paper by inspecting first page (title/authors/journal masthead) and last page (closes at "Argument and Computation 177").

## Reading

- Read all 32 PDF pages directly via Read Image. Notes written incrementally to `papers/Egly_2010_Answer-setProgrammingEncodingsArgumentation/notes.md`.
- Wrote `description.md`, `abstract.md` (verbatim text), `citations.md` (full reference list + 8 key follow-ups), and `metadata.json`.
- **Per task instructions, did NOT run:** source-bootstrap, register-concepts, extract-claims, register-predicates, author-rules, author-context, source-promote, reconcile, or update papers/index.md.

## Key Findings

1. **Master result (Theorem 3.9, p.168):** For any AF F and e ∈ {stable, adm, pref, semi, comp, ground}, e(F) ≅ AS(π_e(F̂)) under the natural correspondence I ↦ {a | in(a) ∈ I}. Each π_e is a fixed query; only the input database F̂ varies per AF.
2. **Complexity-tight encodings:** π_ground is stratified (P), π_stable / π_adm / π_comp / coherent π_pref reductions sit in normal datalog (NP/coNP), and π_pref / π_semi use disjunction + saturation to land at Σ₂ᴾ / Π₂ᴾ — exactly the natural complexity (Tables 1-3, pp.153/156/169).
3. **Saturation pattern (rules 31-37, p.164):** the recipe for "subset-maximal X" semantics is to guess a candidate T ⊃ S using fresh inN/outN predicates, derive a `fail` atom whenever T fails to be X, then saturate with `inN(X) :- fail, arg(X)` / `outN(X) :- fail, arg(X)` and constrain `:- not fail`. This is the reusable template for any second-level metaproblem.
4. **Generalised AFs (Section 4):**
   - VAFs (Bench-Capon 2003): adapter `π_vaf` derives `defeat` from `att` + `valpref` + `val`. Theorem 4.3, 4.4. Stable on VAFs needs special handling because Bench-Capon defines stability via attack rather than defeat (`π_vaf_stable`, p.171).
   - BAFs (Cayrol & Lagasquie-Schiex 2005): adapter `π_baf` defines `defeat` as att composed with the transitive closure of support. Theorem 4.8 covers stable/adm/pref; Theorem 4.12 covers s-/c-admissible and s-/c-preferred refinements.
5. **Metaproblems via combinator queries:** Coherence (pref ⊆ stable) is a Π₂ᴾ test that reduces to the satisfiability of a small extension of `π_pref` (Cor 3.10). The same pattern works for VAF coherence (Cor 4.5) and the `semi(F) = pref(F)` test (Cor 3.11) using a custom `π_coincide`.
6. **Implementation realities:** ASPARTIX is hosted at www.dbai.tuwien.ac.at/research/project/argumentation/systempage/ on top of DLV. The paper's only empirical claim is "preliminary tests show our approach is able to deal with more than 100 arguments for all considered semantics" (p.174). No comparative benchmark in this paper.
7. **Critique of contemporaries:** Nieves et al. (2008, 2009) and Wakaki & Nitta (2008) require per-instance recompilation of the encoding for preferred/semi-stable; ASPARTIX uses a fixed disjunctive query — argued as more reliable and extensible.

## Usefulness to This Project

**Rating:** High

**What it provides:**
- Verbatim, known-correct ASP encodings for all seven main Dung semantics + two generalised families (VAF, BAF). Drop-in baseline for any pipeline that needs to enumerate AF extensions or compare semantics.
- The saturation template (rules 31-37 / π_satpref) is a generic recipe for encoding any "subset-maximal X" semantics in fixed disjunctive ASP.
- Tight complexity matching demonstrates that the ASP-reduction route is not paying an asymptotic penalty for the harder semantics — useful when justifying the choice of ASP over SAT for preferred/semi-stable.
- Cor 3.10 / 3.11 are templates for the `pref(F) ⊆ stable(F)` and `semi(F) = pref(F)` metaproblems if the project ever needs them.

**Actionable next steps:**
- Lift `π_cf, π_stable, π_adm, π_comp, π_ground, π_pref, π_semi` into the project's reusable `asp/` directory with an aspartix-attribution comment block.
- If targeting clingo rather than DLV, replace the DLV-specific `X < Y` total-order primitive with explicit `total_order(X,Y)` facts or numeric encoding.
- Implement the Cor 3.10 coherence check for any project that needs to test stable-extension existence equivalence.
- Compare against the ASPARTIX-V2 / clingo-based descendants (Dvořák et al. follow-ups) before treating these encodings as state-of-the-art for benchmark performance — paper is from 2010 and only claims correctness, not solver-state-of-the-art.

**Skip if:** the project does not need symbolic enumeration of AF extensions, or if it has already adopted a labelling-based / SAT-based AF solver (e.g., μ-toksia, pyglaf) where the ASPARTIX encodings would only be relevant as a correctness oracle.
