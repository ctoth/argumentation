---
title: "ConArg: a Tool to Solve (Weighted) Abstract Argumentation Frameworks with (Soft) Constraints"
authors: "Stefano Bistarelli; Francesco Santini"
year: 2012
venue: "arXiv preprint"
doi_url: "https://arxiv.org/abs/1212.2857v2"
pages: 37
produced_by:
  agent: "GPT-5 Codex"
  skill: "paper-reader"
  status: "stated"
  timestamp: "2026-05-02T00:24:09Z"
---
# ConArg: a Tool to Solve (Weighted) Abstract Argumentation Frameworks with (Soft) Constraints

## One-Sentence Summary
ConArg is a Java/JaCoP constraint-programming tool that computes Dung-style and weighted argumentation extensions by translating AF/WAF semantics into finite-domain CSP/SCSP constraints and using small-world graph generators for experiments. *(p.1, p.8, p.17, p.21)*

## Problem Addressed
The paper addresses the computational problem of enumerating and checking argumentation extensions, including weighted argumentation frameworks where attacks have costs, probabilities, fuzziness, or preference values, and asks whether CP plus soft constraints can provide a common quantitative solver architecture. *(p.1-p.3, p.11-p.13)*

## Key Contributions
- Defines ConArg as a Java tool using JaCoP to import `.dl` interaction graphs or generate Barabasi/Kleinberg small-world graphs and compute conflict-free, admissible, complete, stable, grounded, preferred, semi-stable, stage, ideal, alpha-extension, and beta-grounded problems. *(p.1, p.21-p.24)*
- Gives explicit CSP encodings for classical AF semantics: one Boolean variable per argument, conflict-free/admissible/complete/stable constraint families, and second-stage SetVar CSPs for grounded, preferred, semi-stable, stage, and ideal semantics. *(p.8-p.11)*
- Recasts WAFs as semiring-based argumentation frameworks `AF_S = <Args, R, W, S>` and defines alpha-conflict-free, alpha-stable, alpha-admissible, alpha-complete, alpha-grounded, alpha-preferred, and alpha-semi-stable semantics. *(p.12-p.16)*
- Maps weighted alpha-semantics to SCSPs by associating semiring-valued costs/preferences with attack constraints, summing/composing these costs, and bounding them with a user-supplied threshold alpha. *(p.17-p.20)*
- Implements beta-grounded WAF problems, including credulous, skeptical, and minimal-budget variants, by deriving WAFs after removing attacks whose strengths sum to a beta budget. *(p.5-p.6, p.20-p.21)*
- Reports performance tests over Barabasi and Kleinberg random small-world networks and a comparison showing ConArg faster than ASPARTIX on three selected DLV-based benchmark problems. *(p.25-p.32)*

## Study Design
Non-empirical systems/theory paper with solver benchmarks. Experiments average over 10 generated random networks per network size, use depth-first search with JaCoP's `MostConstrainedStatic` variable heuristic and `IndomainSimpleRandom` value heuristic, and impose a 180-second timeout. *(p.25-p.28)*

## Methodology
ConArg represents each argument `a_i` by a finite-domain variable with domain `{1,0}`, where `1` means the argument is in the extension and `0` means it is excluded. The AF interaction graph uses parent/child language: if `b` attacks `a`, then `b` is a parent of `a`; if `c` attacks `b`, then `c` is a grandparent of `a`. Classical semantics are encoded by adding the appropriate sets of hard constraints and solving the resulting CSP. Weighted semantics add semiring-valued costs/preferences for attacks and impose threshold constraints over composed costs. *(p.8-p.10, p.17-p.20)*

## Key Equations / Statistical Models

$$
AF = \langle Args, R \rangle
$$
Where `Args` is the set of arguments and `R` is the binary attack relation over `Args`; `a_i R a_j` means `a_i` attacks `a_j`. *(p.3-p.4)*

$$
WAF = \langle Args, R, w \rangle,\quad w: R \to \mathbb{R}^{+}
$$
Where `w` assigns real-valued weights to attacks, and an inconsistency budget `beta in R+` is the total attack weight one is willing to disregard. *(p.5)*

$$
P = \langle V, D, C \rangle
$$
Where `V={x_1,...,x_n}` is a set of variables, `D={D_1,...,D_n}` the domains with `x_i in D_i`, and `C={c_1,...,c_t}` constraints. Each constraint is a pair `<RO_j,O_j>` whose relation `RO_j` is defined over scope `O_j`. *(p.6)*

$$
S = \langle A,+,\times,0,1\rangle
$$
Where `A` is the semiring carrier; `0` and `1` are bottom and top elements; `+` is closed, associative, commutative, idempotent with unit `0` and absorbing element `1`; `x` is closed, associative, commutative, distributes over `+`, has unit `1`, and absorbing element `0`. The order is `a <=_S b` iff `a+b=b`, so `b` is better than `a`. *(p.7)*

$$
(c_1 \otimes c_2)\eta = c_1\eta \times c_2\eta
$$
Where soft-constraint combination builds a new constraint by multiplying semiring values for each tuple. *(p.7)*

$$
c\Downarrow_{V\setminus\{v\}}(\eta)=\sum_{d\in D} c\eta[v:=d]
$$
Where projection eliminates variable `v` by summing over its domain. *(p.8)*

$$
blevel(P)=Sol(P)\Downarrow_{\emptyset},\quad Sol(P)=\bigotimes C
$$
Where `blevel(P)` is the best consistency level of the SCSP. A problem is alpha-consistent when `blevel(P)=alpha`, consistent when some `alpha >_S 0` exists, and inconsistent otherwise. *(p.8)*

$$
AF_S = \langle Args, R, W, S\rangle
$$
Where `S=<A,+,x,0,1>` is a semiring and `W: Args x Args -> A` is the weight function; for `(a,b) in R`, `W(a,b)=s` means `a` attacks `b` with strength `s`. *(p.13)*

$$
W(B,a)=k \iff \prod_{b\in B}^{S} W(b,a)=k
$$
Where the product composes the weights of all attacks from argument set `B` against argument `a`. *(p.14)*

$$
W(B,D)=k \iff \prod_{b\in B,d\in D}^{S} W(b,d)=k
$$
Where the product composes all attacks from set `B` to set `D`. *(p.14)*

## Parameters

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| Classical AF argument-in-extension variable | `a_i` | Boolean | - | `{0,1}` | p.8 | `1` means the argument is included in the extension, `0` excluded. |
| Weighted inconsistency budget | `beta` | attack-weight total | user input | `R+` | p.5, p.20 | Total attack weight tolerated/removed for beta-grounded WAF variants. |
| Alpha threshold for alpha-extensions | `alpha` | semiring value | user input | `A` | p.14-p.20 | Bounds tolerated attack strength/cost inside alpha-extension semantics. |
| Weighted semiring | `S_W` | semiring | - | `<R+ U {infty}, min, +hat, infty, 0>` | p.7, p.13, p.20 | Models costs or support votes to minimize; `+hat` is arithmetic plus. |
| Fuzzy semiring | `S_F` | semiring | - | `<[0..1], max, min, 0, 1>` | p.7, p.12-p.13, p.20 | Models fuzzy attack strength or preference values. |
| Probabilistic semiring | `S_P` | semiring | - | `<[0..1], max, xhat, 0, 1>` | p.7, p.12 | Uses arithmetic multiplication to compose independent probabilities. |
| Boolean semiring | `S_B` | semiring | - | `<{true,false}, OR, AND, false, true>` | p.7, p.13 | Casts crisp CSP/classical AFs into semiring framework. |
| Barabasi generator attachment probability | `p` | probability | - | `(degree(v)+1)/(|E|+|V|)` | p.22 | Probability of connecting new vertex to existing vertex `v`. |
| Kleinberg clustering exponent | `theta` | dimensionless | user specified | - | p.22 | Long-range links chosen with probability proportional to `d^theta`. |
| Performance timeout | - | seconds | 180 | fixed | p.25, p.27 | Search interrupted after threshold; timed-out table rows marked with `*`. |
| Benchmark hardware | - | machine spec | MacBook | 2.4 GHz Core Duo, 4 GB 1067 MHz DDR3 RAM | p.30 | Used for all collected performance results. |

## Effect Sizes / Key Quantitative Results

| Outcome | Measure | Value | CI | p | Population/Context | Page |
|---------|---------|-------|----|---|--------------------|------|
| ConArg vs ASPARTIX admissible benchmark | time reduction | 74% | - | - | 36-node Kleinberg networks, all admissible extensions | p.31-p.32 |
| ConArg vs ASPARTIX complete benchmark | time reduction | 65% | - | - | 49-node Kleinberg networks, all complete extensions | p.31-p.32 |
| ConArg vs ASPARTIX stable benchmark | time reduction | 72% | - | - | 64-node Kleinberg networks, all stable extensions | p.31-p.32 |
| ConArg admissible benchmark | wall time | 7.27 s | - | - | 36-node networks in Figure 14 | p.32 |
| ASPARTIX admissible benchmark | wall time | 27.87 s | - | - | 36-node networks in Figure 14 | p.32 |
| ConArg complete benchmark | wall time | 75.86 s | - | - | 49-node networks in Figure 14 | p.32 |
| ASPARTIX complete benchmark | wall time | 214.74 s | - | - | 49-node networks in Figure 14 | p.32 |
| ConArg stable benchmark | wall time | 19.02 s | - | - | 64-node networks in Figure 14 | p.32 |
| ASPARTIX stable benchmark | wall time | 66.37 s | - | - | 64-node networks in Figure 14 | p.32 |

## Methods & Implementation Details
- ConArg is implemented in Java with NetBeans and uses JaCoP for finite-domain CP, including arithmetic constraints, equalities/inequalities, logical constraints, reified and conditional constraints, combinatorial/global constraints, decomposable constraints, auxiliary variables, and modular search. *(p.21)*
- The tool can generate or import interaction graphs: Barabasi random networks, Kleinberg random networks, a paper case-study graph, ASPARTIX `.dl` imports, and the weighted graph in Figure 4. *(p.21-p.23)*
- Classical conflict-free constraints forbid including both endpoints of an attack: for attack `R(a_i,a_j)`, reject `a_i=1 and a_j=1`; all other assignments are allowed. *(p.8)*
- Classical admissible constraints prevent taking a child argument attacked by an undefended parent; if `a_i` has parent `a_p` and no grandparent, enforce unary `a_i=0`; with grandparents `a_g1...a_gk`, enforce not taking `a_i` unless at least one grandparent is included. *(p.9)*
- Classical complete constraints require every argument defended by extension `B` to be in `B`, except those that would be attacked by `B` itself; formal constraints add defended grandchildren when their parents are not included. *(p.9)*
- Classical stable constraints require every excluded argument to be attacked by some included argument; unattacked arguments must be included. *(p.9)*
- Grounded and preferred extensions are computed in two steps: first enumerate complete or admissible extensions, then translate them into JaCoP `SetVar` values and apply set-inclusion constraints to identify least or maximal sets. *(p.10)*
- Preferred-checking for a candidate set `T` enumerates admissible extensions and applies `AinB(T,Y)` to each admissible solution `Y`, so it uses fewer constraints than full preferred enumeration. *(p.10)*
- Semi-stable and stage extensions compute ranges with one auxiliary integer variable per argument and JaCoP `IfThenElse`, `Or`, and `XeqC` constraints; maximality is then handled through a second CSP. *(p.10)*
- Ideal semantics uses a second CSP to keep admissible extensions contained in the intersection of all preferred extensions and a third CSP to maximize set inclusion. *(p.11)*
- User-defined constraints are supported with conditional constraints, e.g. "extensions must contain `a` when they contain `b`" or "must not contain one of `c` or `d` when they contain both `a` and `b`." *(p.11)*
- Weighted alpha-conflict-free constraints assign attack cost `s` when both endpoints of an attack are included and top preference otherwise; total attack cost is summed/composed and constrained by alpha. *(p.18-p.20)*
- Alpha-admissible constraints differ from crisp admissibility because an attacked argument can be tolerated when defense is strong enough: the composition of selected grandparent-to-parent attack weights must be at least as strong as the parent-to-child attack. *(p.18)*
- Alpha-complete and alpha-stable constraints extend the same weighted-cost machinery to their corresponding crisp constraint classes. *(p.18-p.20)*
- ConArg implements two semirings directly: weighted and fuzzy. *(p.20)*

## Figures of Interest
- **Figure 1 (p.4):** Dung AF example with arguments `a,b,c,d` and directed attacks, e.g. `c` attacks `d`.
- **Figure 2 (p.8):** Weighted SCSP graph over variables `X,Y`, unary constraints `c1,c3`, binary constraint `c2`, and weighted semiring example with best level 7 for `X=a,Y=b`.
- **Figure 3 (p.12):** Fuzzy WAF weather example with `a1`, `a2`, `a3` and attack weights 0.9, 0.9, 0.5.
- **Figure 4 (p.13):** Weighted interaction graph over `{a,b,c,d,e}` with weights `7,8,9,8,5,6`.
- **Figure 5 (p.17):** Inclusion hierarchy among alpha-extensions: alpha-stable subset alpha-semi-stable subset alpha-preferred subset alpha-complete, and alpha-grounded subset alpha-complete.
- **Figure 6 (p.20):** JaCoP code for alpha-conflict-free extensions using `IfThenElse`, `And`, `XeqC`, `Sum`, and `XlteqC`.
- **Figure 7 (p.21):** Graph-creation window selecting Barabasi/Kleinberg/import/example graph, semiring type, number of nodes, and max arc weight.
- **Figure 8 (p.23):** Problem-selection dropdown grouped into classical, coalitional, alpha-extension, and beta-grounded problems.
- **Figure 9 (p.24):** Example beta-grounded solution for beta=6, 8th of 13 solutions, with removed arcs shown as dotted lines.
- **Figure 10 (p.26):** Barabasi small-world graph with 40 nodes and hubs 0, 1, 2.
- **Figure 11 (p.27):** Kleinberg small-world graph with 36 nodes, grid structure, and no big hubs.
- **Figure 12 (p.28):** Counts of 1- through 5-conflict-free extensions in 16- and 36-node Kleinberg networks.
- **Figure 13 (p.29):** Counts of beta-grounded extensions for beta=1..4 on 16, 25, 36, 49, and 64-node Kleinberg networks.
- **Figure 14 (p.32):** Runtime comparison between ConArg and ASPARTIX.

## Results Summary
Barabasi networks show one complete and one stable extension regardless of size in Table 1, but conflict-free and admissible extension counts grow quickly and often hit the 180-second threshold at larger sizes; grounded and preferred checking remain millisecond-scale. *(p.26-p.28)* Kleinberg networks are more balanced: conflict-free/admissible counts still grow sharply, but complete and stable counts can reach hundreds of thousands without the same hub-driven pattern. *(p.27-p.29)* The authors identify "attention thresholds" where exhaustive enumeration becomes infeasible: around 32-40 nodes for conflict-free/admissible enumeration, 37 nodes for Barabasi admissible, and 49/64 nodes for Kleinberg complete/stable. *(p.29)* CP works very well for yes/no checks but degrades on exhaustive enumeration of loosely constrained semantics. *(p.29-p.30)* Adding weights further increases solution counts because more conflicts are tolerated; the authors suggest approximately order-of-magnitude growth per tolerance increment in many beta/alpha settings. *(p.30)*

## Limitations
- Performance depends strongly on topology; the same small-world label hides important differences between Barabasi hubs and Kleinberg grid-like graphs. *(p.28-p.30)*
- Exhaustive enumeration of weakly constrained semantics, especially conflict-free and admissible sets, is the main scalability bottleneck even with CP. *(p.29-p.30)*
- The experiments use generated small-world graphs rather than real social-network AFs/WAFs; real-data evaluation is left for future work. *(p.34)*
- The tool's small-world graph support uses generic Barabasi/Kleinberg properties, and the authors explicitly say no in-depth study had yet characterized the correct small-world properties for argumentation networks. *(p.25)*
- Weighted semantics can greatly increase the number of accepted extensions as the tolerance threshold rises. *(p.30)*

## Arguments Against Prior Work
- ASPARTIX is mature for classical Dung AFs and some generalizations, but the paper states ASPARTIX cannot solve weighted AFs, motivating ConArg's weighted/soft-constraint path. *(p.30-p.31, p.33)*
- Prior WAF complexity work by Dunne et al. defines hard problems and complexity proofs but does not provide a solving mechanism; ConArg targets practical solution of those problems. *(p.31-p.32)*
- SAT encodings can solve acceptability by satisfiability, but the authors argue CP is more expressive in modeling complex semantics and user-defined constraints, and lets users tune solver information more directly. *(p.32-p.33)*
- Gorgias-C offers logic programming plus constraints but is framed as a more general multi-agent reasoning framework and had not presented computational results for AF problems. *(p.32)*

## Design Rationale
- Constraint programming is chosen because AF/WAF extension computation is combinatorial, hard in general, and naturally expressible as constraints over argument-in/out variables plus additional optimization or set-inclusion constraints. *(p.2-p.3, p.6-p.8)*
- Semiring-based soft constraints are chosen because fuzziness, cost, probability, and crisp Boolean semantics can be represented by changing the semiring carrier and operations while retaining one computational framework. *(p.7, p.12-p.13)*
- Small-world graph generation is included because social-network-style discussion fora are a plausible application domain for argumentation networks, and topology materially affects performance. *(p.2-p.3, p.25-p.30)*
- The tool supports user-defined constraints because real uses may require side conditions beyond canonical semantics. *(p.11, p.33)*

## Testable Properties
- In classical AF encoding, a solution using only conflict-free constraints corresponds exactly to a conflict-free extension. *(p.9-p.10)*
- In classical AF encoding, using conflict-free plus admissible constraints corresponds exactly to admissible extensions. *(p.9-p.10)*
- In classical AF encoding, adding complete constraints corresponds exactly to complete extensions; adding stable constraints corresponds exactly to stable extensions. *(p.9-p.10)*
- Every alpha-complete extension is alpha-admissible. *(p.16)*
- Every alpha-preferred extension is alpha-complete. *(p.16)*
- Every alpha-grounded extension is contained in every alpha-preferred extension. *(p.16)*
- Every alpha-stable extension is alpha-semi-stable, and every alpha-semi-stable extension is alpha-preferred. *(p.16)*
- For a classical AF and any semiring-based alpha-version, 1-conflict-free extensions correspond to classical conflict-free extensions, 1-semi-stable and 1-stable correspond to their classical counterparts, and 1-admissible/1-complete/1-grounded/1-preferred are subsets of the corresponding classical semantics. *(p.17)*
- If an extension is `alpha1`-conflict-free, it is also `alpha2`-conflict-free when `alpha2 <_S alpha1`. *(p.14)*
- ConArg's weighted alpha implementation should reject a solution when total attack cost exceeds alpha. *(p.19-p.20)*

## Relevance to Project
This paper is directly relevant to computational argumentation infrastructure: it provides a concrete constraint-programming representation for Dung and weighted semantics, identifies where enumeration blows up, and gives implementation-ready mappings for crisp and semiring-valued attack constraints. It is especially useful for comparing SAT/ASP-style solvers with CP/SCSP formulations and for designing weighted argumentation semantics with explicit tolerance thresholds. *(p.8-p.20, p.25-p.33)*

## Open Questions
- [ ] How well do the ConArg encodings perform on current CP/SAT/SMT solvers rather than 2012-era JaCoP/DLV baselines? *(p.29-p.32)*
- [ ] Which real social-network discussion datasets can be translated into AFs/WAFs with meaningful topology and attack weights? *(p.34)*
- [ ] Can topology-aware global constraints or symmetry breaking improve enumeration for weakly constrained semantics? *(p.29-p.30, p.34)*
- [ ] How should semiring choices be validated against actual meanings of cost, probability, fuzziness, or user trust? *(p.12-p.14)*

## Related Work Worth Reading
- Dunne et al. 2011 on weighted argument systems, inconsistency budgets, and complexity for beta-grounded problems. *(p.5-p.6, p.34)*
- Bistarelli et al. 1997 and 2004 on semiring-based soft constraints, the algebraic basis of the paper's weighted framework. *(p.7, p.35)*
- Dung 1995 for the canonical abstract argumentation semantics used throughout ConArg. *(p.3-p.5, p.35)*
- Egly et al. 2008 and Dvorak et al. 2011 on ASPARTIX and answer-set-based AF solving, the principal comparison point. *(p.1, p.30-p.31, p.34, p.37)*
- Amgoud and Devred 2011 on encoding argumentation frameworks as CSPs, a closely related qualitative-preference mapping. *(p.33, p.37)*
