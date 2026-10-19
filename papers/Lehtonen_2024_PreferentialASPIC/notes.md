# Lehtonen et al. 2024 — Complexity Results and Algorithms for Preferential Argumentative Reasoning in ASPIC+

## Date: 2026-03-30

## Key Contributions

1. **Rephrasing of ASPIC+ semantics under last-link principle** — They rephrase argumentation semantics (admissible, complete, stable, preferred, grounded) in terms of defeasible elements (assumptions and defeasible rules) rather than arguments. This avoids the exponential blowup from enumerating all arguments.

2. **Complexity results** — Acceptance under grounded semantics is polynomial-time decidable. Credulous acceptance is NP-complete under admissible, complete, preferred, and stable semantics. Skeptical acceptance is polynomial-time decidable under admissible and complete semantics, coNP-complete under stable semantics, and Pi_2^P-complete under preferred semantics. These results hold for both elitist and democratic last-link lifting; adding last-link preferences does not increase the acceptance complexity of the corresponding ASPIC+ setting without preferences. *(Theorems 15-16; [page image](pngs/page-006.png))*

3. **ASP encodings** — Answer set programming encodings for the (co)NP-complete acceptance problems under admissible, complete, and stable semantics. Modules include II_common (shared), II_prf (shared preference machinery), II_ELI (elitist lifting), and II_DEM (democratic lifting). Here II_prf names the preference module, not a preferred-semantics encoding. *(Section 5; [scope](pngs/page-006.png), [modules](pngs/page-007.png))*

4. **Empirical evaluation** — ASPforASPIC scales better than PyArg on the tested instances. Under elitist lifting it solves every instance up to 1200 atoms for all four evaluated tasks and some instances at 1800 atoms, but none at 1900 atoms (Table 1). Under democratic lifting the paper reports solving all instances with at most 1900 atoms. PyArg solves no instances above 50 atoms. *(Section 6; [page image](pngs/page-008.png))*

5. **Obstacles to weakest-link** — Section 7 shows why the last-link approach does not transfer directly: grounded acceptance under weakest-link with elitist lifting is NP-hard (Proposition 17), and exact characterization of extensions using assumptions alone can fail. The paper identifies both computational and representational obstacles rather than an extension with similar results. *(Section 7; [page image](pngs/page-008.png))*

## Key Definitions

- **Definition 1**: Argumentation system `AS = (L, contrary, R, n, <=)` with a language of atoms, contrariness function, strict/defeasible rules, naming function, and partial preorder on defeasible rules. *([page image](pngs/page-001.png))*
- **Definition 2**: Knowledge base `K = K_a ∪ K_p` with disjoint sets of axioms `K_a` and ordinary premises `K_p`. In this paper `K_a` means axioms, not assumable premises. *([page image](pngs/page-001.png))*
- **Definition 3**: Argumentation theory `T = (AS, K, <=′)`, where `<=′` is a partial preorder on ordinary premises `K_p`. *([page image](pngs/page-001.png))*
- **Definition 4**: Arguments — observation-based, strict, defeasible rule-based
- **Definition 5**: Defeats — preference-dependent, with elitist/democratic last-link and weakest-link
- **Definition 6**: Ordering comparison on sets (ELI, DEM)
- **Definition 7**: Under last-link, `B ≺ A` iff `LDR(B) ◁_s LDR(A)`, or both last-defeasible-rule sets are empty and `prem_p(B) ◁_s prem_p(A)`, for the chosen elitist/democratic set lifting from Definition 6. This compares last defeasible rule sets, not just top rules, and includes the ordinary-premise case. *([page image](pngs/page-002.png))*
- **Definitions 8-9**: Abstract argumentation framework derived from AT with ordering
- **Definition 10**: Assumption (P, D) — an assumption captures derivable atoms from (P, D)
- **Definition 11**: Argument based on (P, D) — argument rooted in assumption
- **Definition 12**: Deductive closure Thy(P, D) — fixed point
- **Definitions 13-20**: Rephrased defeat types (preference-independent, contradictory rebuttal under elitist/democratic lifting, contradictory undermine under elitist/democratic)
- **Definitions 21-24**: Defeat in general, defence by assumptions, applicable rules, s-conflict-free assumptions
- **Proposition 13**: Counterpart of Dung's fundamental lemma for assumption defence. *([page image](pngs/page-006.png))*
- **Proposition 14**: The least fixpoint `(P*,D*)` of the assumption characteristic function yields grounded extension `Arg_T(P*,D*)`. *([page image](pngs/page-006.png))*
- **Theorem 15**: Grounded acceptance under last-link and either elitist or democratic lifting is polynomial-time decidable. *([page image](pngs/page-006.png))*
- **Theorem 16**: Complexity matches abstract AF complexity — NP/coNP/Pi_2^P depending on task and semantics
- **Proposition 17**: Under weakest-link and elitist lifting, deciding grounded acceptance is NP-hard (contrast to polynomial for last-link). *([page image](pngs/page-008.png))*

## Relevance to propstore

- **Direct relevance**: propstore's aspic_bridge.py implements last-link preference lifting. This paper provides the theoretical foundation for the complexity of what we compute, and the ASP encodings could replace or augment the Python implementation for scalability.
- **Key insight**: The rephrasing to defeasible elements avoids argument enumeration — propstore currently builds all arguments recursively which won't scale.
- **Weakest-link warning**: If propstore ever switches to weakest-link, grounded acceptance becomes NP-hard (not polynomial).

## Implementation Notes

- ASPforASPIC uses Clingo (Gebser et al. 2016) version 5.7.1 as the ASP solver
- Benchmark instances: random ATs with 50 to 2100 atoms, 5 instances per size. *([page image](pngs/page-008.png))*
- 1% of atoms are axioms and 20% ordinary premises; every premise and 10% of rules have a contrary; 40% of sentences occur in a contrary relation, and 50% of contrary relations are symmetric. *([page image](pngs/page-008.png))*
- Half rules strict, half defeasible
- Time limit 600s, memory 32GB

## New Leads from References

- Lehtonen, Wallner, Järvisalo 2020 — ASP encodings for ASPIC+ without preferences (already in collection as Lehtonen_2020)
- Lehtonen, Wallner, Järvisalo 2022 — Computing stable conclusions under weakest-link
- Lehtonen, Wallner, Järvisalo 2021 — Declarative algorithms and complexity for assumption-based argumentation → NOW IN COLLECTION: [Declarative Algorithms and Complexity Results for Assumption-Based Argumentation](../Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/notes.md)
- Odekerken, Bex, Borgo, Testerink 2022 — Approximating stability for applied argument-based inquiry
- Odekerken et al. 2023 — Argumentative reasoning in ASPIC+ under incomplete information (already in collection)
- Prakken 2010 — Abstract framework for argumentation with structured arguments

## Collection Cross-References

### Now in Collection (previously listed as leads)
- [Declarative Algorithms and Complexity Results for Assumption-Based Argumentation](../Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/notes.md) - ABA/ABA+ complexity and direct ASP predecessor to this paper's preferential ASPIC+ encodings.

### Conceptual Links (not citation-based)
- [Declarative Algorithms and Complexity Results for Assumption-Based Argumentation](../Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/notes.md) - same solver-design pattern shifted across structured formalisms: direct reasoning over compact semantic carriers rather than enumerating every argument/AF node first.
