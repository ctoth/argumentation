---
title: "Fudge: A light-weight solver for abstract argumentation based on SAT reductions"
authors: "Matthias Thimm; Federico Cerutti; Mauro Vallati"
year: 2021
venue: "arXiv"
doi_url: "https://arxiv.org/abs/2109.03106"
pages: "1-3"
produced_by:
  agent: "gpt-5"
  skill: "paper-reader"
  status: "stated"
  timestamp: "2026-05-01T23:43:18Z"
---
# Fudge: A light-weight solver for abstract argumentation based on SAT reductions

## One-Sentence Summary
Fudge is a compact C++ SAT-based abstract-argumentation solver whose distinctive value is novel encodings for `DS-PR` and ideal semantics, backed by incremental SAT solving.

## Problem Addressed
The paper describes a solver for ICCMA-style abstract argumentation tasks over complete, grounded, stable, preferred, and ideal semantics. It highlights the same bottleneck as the IJCAI paper: preferred skeptical reasoning is hard because common algorithms compute or maximize preferred extensions, while Fudge avoids that step. *(p.1-p.2)*

## Key Contributions
- Supports `SE`, `CE`, `DC`, and `DS` style problems for `CO`, `GR`, `ST`, `PR`, and `ID`, with `DC` and `DS` equivalent for unique-extension semantics such as grounded and ideal. *(p.1-p.2)*
- Uses ordinary SAT reductions for first-level tasks, illustrated with stable semantics. *(p.2)*
- Reuses the new skeptical-preferred characterization from Thimm, Cerutti, and Vallati 2021. *(p.2)*
- Uses an ideal-semantics characterization where the ideal set is the largest admissible set satisfying a non-attack condition against admissible attackers. *(p.2)*
- Implements the solver in C++ using CaDiCaL 1.3 through the C++ API, specifically because incremental SAT solving benefits repeated satisfiability checks and counting tasks. *(p.3)*

## Methodology
Fudge treats abstract-argumentation reasoning as a collection of SAT oracle calls. For stable extension witness search, it creates one propositional variable `in_a` per argument and constrains conflict-freeness and outsider attack coverage. For preferred skeptical and ideal tasks, it does not rely on enumerating or maximizing preferred extensions; instead it uses admissibility checks from the authors' newer characterizations. *(p.2-p.3)*

## Key Equations / Statistical Models

$$
S^+ = \{a \in A \mid \exists b \in S, bRa\}
$$

$$
S^- = \{a \in A \mid \exists b \in S, aRb\}
$$

Where `S+` is the set attacked by `S`, and `S-` is the set attacking `S`. *(p.1)*

$$
\Phi_1(AF) = \bigwedge_{(a,b) \in R} \neg(in_a \wedge in_b)
$$

Where `Phi_1` enforces conflict-freeness for stable-extension search. *(p.2)*

$$
\Phi_2(AF) = \bigwedge_{a \in A} (\neg in_a \leftrightarrow \bigvee_{(b,a) \in R} in_b)
$$

Where `Phi_2` enforces that every argument outside a stable extension is attacked by an included argument. *(p.2)*

## Parameters

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| SAT solver | - | implementation | CaDiCaL 1.3 | - | 3 | Used through C++ API. |
| Argument variable | `in_a` | Boolean | - | true/false | 2 | True iff argument `a` is in the candidate extension. |
| Supported semantics | `sigma` | set | `{CO, GR, ST, PR, ID}` | - | 1-2 | Solver coverage claimed in system description. |

## Methods & Implementation Details
- Stable witness formula is satisfiable iff the AF has a stable extension; a model of `Phi_1 and Phi_2` gives one stable extension. *(p.2)*
- First-level polynomial-hierarchy tasks are handled similarly; counting is implemented through iterative satisfiability tests over extension models. *(p.2)*
- For `DS-PR`, Fudge uses the theorem that `a` is skeptically accepted iff an admissible set containing `a` exists and every admissible set containing `a` attacked by another admissible set can be extended together with `a`. *(p.2)*
- For ideal semantics, the paper cites Dung et al. 2007 and the later observation that the largest admissible subset of arguments not attacked by admissible sets yields the ideal extension. *(p.2)*
- Incremental SAT is an explicit engineering choice, because repeated related SAT calls dominate these algorithms. *(p.3)*

## Figures of Interest
No figures.

## Results Summary
This system description does not present new benchmark tables; it points to the companion IJCAI 2021 work for algorithm details and experiments. It does state that the new encodings are intended to avoid the costly maximization step in hard abstract-argumentation problems. *(p.3)*

## Limitations
- The paper is a short system description and does not provide clause-level encodings for the `DS-PR` and ideal utility functions. *(p.2-p.3)*
- It covers `ID` but not semi-stable or stage semantics. *(p.1-p.2)*
- Source availability is stated, but the paper does not give repository layout or API details. *(p.3)*

## Arguments Against Prior Work
- The key criticism is that some abstract-argumentation problems become expensive because prior approaches perform maximization to compute preferred extensions. Fudge is designed to avoid that maximization where possible. *(p.2-p.3)*

## Design Rationale
- Use a small SAT-oriented architecture rather than ASP/CP machinery. *(p.2)*
- Use incremental SAT for repeated satisfiability checks. *(p.3)*
- Reuse standard reductions where they are enough; reserve novel encodings for `DS-PR` and ideal semantics. *(p.1-p.3)*

## Testable Properties
- Stable encoding must forbid any attacked pair from both being `in`. *(p.2)*
- Stable encoding must require every non-in argument to be attacked by some in argument. *(p.2)*
- `DS-PR` implementation must not need to construct preferred extensions. *(p.2)*
- Ideal computation can be expressed without performing skeptical preferred acceptance for every argument. *(p.2)*
- Repeated SAT calls should use an incremental solver interface in the production architecture. *(p.3)*

## Relevance to Project
This paper supports turning our current ad hoc Z3 helper functions into a proper incremental SAT backend object. It also confirms that the hard solver path should be `DS-PR` and ideal first, with standard reductions retained for easier witness tasks.

## Open Questions
- [ ] Retrieve Fudge source from the URL in the paper and compare its SAT utility APIs with our planned Python/Z3 API.
- [ ] Decide whether Z3 `push`/`pop` is sufficient for the first incremental implementation or whether we need a lower-level SAT adapter.
- [ ] Confirm how Fudge implements counting tasks, since our current ICCMA runner mostly needs witness and decision tasks.

## Related Work Worth Reading
- Thimm, Cerutti, Vallati 2021 on skeptical preferred without preferred extensions.
- Dung, Mancarella, Toni 2007 on ideal skeptical argumentation.
- Besnard, Doutre, Herzig 2014 on encoding argument graphs in logic.
