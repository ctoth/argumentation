# Lehtonen et al. 2024 — Complexity Results and Algorithms for Preferential Argumentative Reasoning in ASPIC+

## Date: 2026-03-30

## Key Contributions

1. **Rephrasing of ASPIC+ semantics under last-link principle** — They rephrase argumentation semantics (admissible, complete, stable, preferred, grounded) in terms of defeasible elements (assumptions and defeasible rules) rather than arguments. This avoids the exponential blowup from enumerating all arguments.

2. **Complexity results** — Acceptance under grounded semantics is polynomial-time decidable. Credulous acceptance is NP-complete under admissible, complete, preferred, and stable semantics. Skeptical acceptance is coNP-complete under complete and stable, and Pi_2^P-complete under preferred semantics. These match the complexity of abstract AFs (Dvorak and Dunne 2012), showing preferences under last-link don't increase complexity.

3. **ASP encodings** — Answer set programming encodings for deciding acceptance. Modules: II_common (shared), II_ELI (elitist lifting), II_DEM (democratic lifting). Encodings for credulous/skeptical under all semantics.

4. **Empirical evaluation** — ASPforASPIC solver vs PyArg. ASPforASPIC scales significantly better (solves instances up to 1900 atoms under elitist, 1500 under democratic) vs PyArg which stalls around 50-80 atoms.

5. **Extension to weakest-link** — Section 7 shows the approach extends to weakest-link principle, with similar results. NP-hardness under grounded+weakest-link is shown (Proposition 17), contrasting polynomial grounded+last-link.

## Key Definitions

- **Definition 1**: Argumentation system (AS) = (L, R, n, <=) with language, rules, naming function, partial preorder
- **Definition 2**: Knowledge base = (K_n, K_p, K_a) with necessary/ordinary/assumable premises
- **Definition 3**: Argumentation theory AT = (AS, K) — an AS plus a knowledge base
- **Definition 4**: Arguments — observation-based, strict, defeasible rule-based
- **Definition 5**: Defeats — preference-dependent, with elitist/democratic last-link and weakest-link
- **Definition 6**: Ordering comparison on sets (ELI, DEM)
- **Definition 7**: Last-link principle — argument A < B iff all defeasible rules in top(B) are not less preferred than those in top(A)
- **Definitions 8-9**: Abstract argumentation framework derived from AT with ordering
- **Definition 10**: Assumption (P, D) — an assumption captures derivable atoms from (P, D)
- **Definition 11**: Argument based on (P, D) — argument rooted in assumption
- **Definition 12**: Deductive closure Thy(P, D) — fixed point
- **Definitions 13-20**: Rephrased defeat types (preference-independent, contradictory rebuttal under elitist/democratic lifting, contradictory undermine under elitist/democratic)
- **Definitions 21-24**: Defeat in general, defence by assumptions, applicable rules, s-conflict-free assumptions
- **Proposition 14**: Grounded extension computable in polynomial time via characteristic function iteration
- **Proposition 15**: Grounded extension is a corollary of Dung's fundamental lemma
- **Theorem 16**: Complexity matches abstract AF complexity — NP/coNP/Pi_2^P depending on task and semantics
- **Proposition 17**: Under weakest-link, deciding grounded acceptance is NP-hard (contrast to poly for last-link)

## Relevance to propstore

- **Direct relevance**: propstore's aspic_bridge.py implements last-link preference lifting. This paper provides the theoretical foundation for the complexity of what we compute, and the ASP encodings could replace or augment the Python implementation for scalability.
- **Key insight**: The rephrasing to defeasible elements avoids argument enumeration — propstore currently builds all arguments recursively which won't scale.
- **Weakest-link warning**: If propstore ever switches to weakest-link, grounded acceptance becomes NP-hard (not polynomial).

## Implementation Notes

- ASPforASPIC uses Clingo (Gebser et al. 2016) version 5.7.1 as the ASP solver
- Benchmark instances: random ATs with 5 to 2100 atoms, 5 instances per size
- 40% of atoms are premises, 40% sentences in ordinary relations, 50% of contraries symmetric
- Half rules strict, half defeasible
- Time limit 600s, memory 32GB

## New Leads from References

- Lehtonen, Wallner, Järvisalo 2020 — ASP encodings for ASPIC+ without preferences (already in collection as Lehtonen_2020)
- Lehtonen, Wallner, Järvisalo 2022 — Computing stable conclusions under weakest-link
- Lehtonen, Wallner, Järvisalo 2021 — Declarative algorithms and complexity for assumption-based argumentation
- Odekerken, Bex, Borgo, Testerink 2022 — Approximating stability for applied argument-based inquiry
- Odekerken et al. 2023 — Argumentative reasoning in ASPIC+ under incomplete information (already in collection)
- Prakken 2010 — Abstract framework for argumentation with structured arguments
