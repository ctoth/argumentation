---
title: "Computing Preferred Extensions in Abstract Argumentation: a SAT-based Approach"
authors: "Federico Cerutti, Paul E. Dunne, Massimiliano Giacomin, Mauro Vallati"
year: 2013
venue: "Technical report; extended report of a Theory and Applications of Formal Argumentation paper"
doi_url: "https://doi.org/10.1007/978-3-642-54373-9_12"
pages: 21
produced_by:
  agent: "GPT-5 Codex"
  skill: "paper-reader"
  status: "stated"
  timestamp: "2026-05-02T00:20:53Z"
---
# Computing Preferred Extensions in Abstract Argumentation: a SAT-based Approach

## One-Sentence Summary
The paper defines PrefSat, a SAT-based depth-first enumeration procedure that computes all preferred extensions of a finite abstract argumentation framework by repeatedly solving complete-labelling encodings and extending complete extensions to maximal ones. *(p.1, p.9-p.11)*

## Problem Addressed
Preferred-extension enumeration is computationally intractable in the worst case, but existing practical work was thin compared with the mature theory; the authors target efficient construction/enumeration of all preferred extensions rather than only decision questions. *(p.2-p.4)*

## Key Contributions
- Reduces complete-extension computation to SAT through complete-labelling CNF encodings, then searches the complete-extension space to identify maximal complete extensions, which are exactly preferred extensions. *(p.4, p.9-p.11)*
- Analyzes the six implication terms behind complete labellings, classifies the 64 possible subsets of these terms as weak, correct non-redundant, or redundant, and empirically compares representative encodings. *(p.5-p.9)*
- Implements PrefSat in C++ with PrecoSAT and Glucose backends and evaluates it on 2,816 randomly generated finite argumentation frameworks against ASPARTIX/dlv, ASPARTIX-META/gringo+claspD, and NOF. *(p.12-p.18)*

## Study Design

## Methodology
The paper is theoretical plus computational evaluation. It starts from Dung finite abstract argumentation frameworks, recalls extension and labelling semantics, derives SAT encodings for complete labellings, and uses SAT solver calls as an oracle inside a nested-loop search. The inner loop grows a non-empty complete extension until no strict complete superset can be found; the outer loop blocks already discovered preferred extensions and restarts the search to enumerate all preferred extensions. *(p.1-p.11)*

## Core Definitions
- **Argumentation framework:** An AF is `Gamma = (A, R)`, where `A` is a finite set of arguments and `R subseteq A x A` is the attack relation. `b` attacks `a` iff `(b,a) in R`, also written `b -> a`. The attackers of `a` are `a^- = {b : b -> a}`. *(p.2)*
- **Conflict-free set:** `S subseteq A` is conflict-free iff there are no `a,b in S` such that `a -> b`. *(p.3)*
- **Acceptability:** `a in A` is acceptable w.r.t. `S subseteq A` iff every attacker `b` of `a` is itself attacked by some `c in S`. *(p.3)*
- **Admissible set:** `S` is admissible iff it is conflict-free and every element of `S` is acceptable w.r.t. `S`. *(p.3)*
- **Complete extension:** `S subseteq A` is complete iff `S` is admissible and every argument acceptable w.r.t. `S` is included in `S`. *(p.3)*
- **Preferred extension:** `S subseteq A` is preferred iff it is a maximal, w.r.t. set inclusion, admissible set. *(p.3)*
- **Preferred-complete equivalence:** A set is a preferred extension iff it is a maximal complete extension; therefore every preferred extension is complete. *(p.3)*
- **Three-valued labelling induced by an extension:** An argument is labelled `in` iff it belongs to the extension, `out` iff it is attacked by an argument in the extension, and `undec` otherwise. Complete labellings correspond one-to-one with complete extensions, and preferred extensions correspond to complete labellings that maximize the set of `in` arguments. *(p.3)*

## Complete-Labelling Conditions
For every argument `a`, a complete labelling `Lab : A -> {in,out,undec}` satisfies: *(p.3)*

$$
Lab(a) = in \Leftrightarrow \forall b \in a^- : Lab(b) = out
$$

$$
Lab(a) = out \Leftrightarrow \exists b \in a^- : Lab(b) = in
$$

$$
Lab(a) = undec \Leftrightarrow (\forall b \in a^- : Lab(b) \ne in) \wedge (\exists c \in a^- : Lab(c) = undec)
$$

Where `a^-` is the attacker set of `a`. *(p.3)*

The authors split these biconditionals into six implication terms: `C_in^->`, `C_in^<-`, `C_out^->`, `C_out^<-`, `C_undec^->`, and `C_undec^<-`. Their conjunction is the full complete-labelling condition, but several strict subsets are already equivalent and some subsets are weak. *(p.5-p.7)*

## SAT Encoding
Let `k = |A|`, and let `phi : {1,...,k} -> A` be an indexing of arguments. For each argument index `i`, define Boolean variables `I_i`, `O_i`, and `U_i`, meaning respectively that argument `i` is labelled `in`, `out`, or `undec`. The variable set is `V(Gamma) = union_{1 <= i <= |A|} {I_i, O_i, U_i}`. *(p.7)*

Formula (1) enforces exactly one label for every argument: *(p.7)*

$$
\bigwedge_{i \in \{1,\ldots,k\}} ((I_i \vee O_i \vee U_i) \wedge (\neg I_i \vee \neg O_i) \wedge (\neg I_i \vee \neg U_i) \wedge (\neg O_i \vee \neg U_i))
$$

Formula (2) handles unattacked arguments by forcing them `in`: *(p.7)*

$$
\bigwedge_{\{i \mid \phi(i)^- = \emptyset\}} (I_i \wedge \neg O_i \wedge \neg U_i)
$$

Formula (9) enforces the non-empty extension requirement used by the SAT encoding: *(p.8)*

$$
\bigvee_{i \in \{1,\ldots,k\}} I_i
$$

Formulas (3)-(8) encode the six complete-labelling implications for attacked arguments and are selectively included in the six tested encodings `C_1`, `C_1^a`, `C_1^b`, `C_1^c`, `C_2`, and `C_3`. *(p.8-p.9)*

## Encoding Classification
- There are 64 subsets of the six complete-labelling implication terms: 1 of cardinality 0, 6 of cardinality 1, 15 of cardinality 2, 20 of cardinality 3, 15 of cardinality 4, 6 of cardinality 5, and 1 of cardinality 6. *(p.6)*
- A constraint subset is **weak** if some framework and labelling satisfies all its terms without being a complete labelling. It is **correct and non-redundant** if it identifies complete labellings and every strict subset is weak. It is **redundant** if it identifies complete labellings but some strict subset is also correct. *(p.6)*
- Proposition 3 identifies six weak constraints of cardinality 3 by counterexample frameworks in Fig. 1. *(p.6)*
- Corollary 1: all cardinality 0, 1, and 2 constraints are weak; among cardinality 3 constraints, two are correct non-redundant and eighteen are weak; among cardinality 4 constraints, three are correct non-redundant, six weak, and six redundant; all cardinality 5 and 6 constraints are redundant. *(p.6-p.7)*
- The empirical study keeps the five correct non-redundant constraints plus the full six-term encoding as a representative redundant encoding; the remaining twelve redundant constraints are left for future work. *(p.7)*

## Algorithm
**Algorithm 1: Enumerating preferred extensions of an AF.** Input `Gamma = (A,R)`. Output `E_p subseteq 2^A`. The algorithm initializes `E_p = emptyset` and `cnf = Pi_Gamma`, where `Pi_Gamma` is one of the complete-labelling encodings. It uses two helper functions: `SS(cnf)` returns a satisfying assignment for the CNF or `epsilon` if unsatisfiable; `INARGS(assignment)` converts the `in` variables in an assignment into the corresponding set of arguments. *(p.9-p.10)*

1. Set `cnfdf = cnf` and `prefcand = emptyset`. *(p.9)*
2. Inner loop: call `SS(cnfdf)`. If a solution is returned, set `prefcand` to the corresponding `INARGS`; force every argument currently in `prefcand` to remain `in`; add a disjunction requiring at least one further argument not already in `prefcand` to be `in`; repeat until no strict complete superset can be found or all arguments are already included. *(p.9-p.11)*
3. If the inner loop leaves a non-empty `prefcand`, add it to `E_p`. Then add a blocking condition requiring future solutions to include at least one argument outside this preferred extension, so already found preferred extensions and their subsets cannot be rediscovered. *(p.9-p.11)*
4. Outer loop repeats until no `prefcand` is produced. If `E_p` remains empty, return `{emptyset}`; otherwise return all accumulated preferred extensions. *(p.9-p.11)*

**Correctness theorem:** For any finite AF `Gamma = (A,R)`, Algorithm 1 returns exactly `E_PR(Gamma)`. Termination follows because the inner loop strictly increases the `in` set and the outer loop decreases the unexplored potential solution space. Soundness follows because each output is a complete extension with no complete strict superset. Completeness follows because blocking formulas only forbid subsets of already discovered preferred extensions, so no different preferred extension is lost. *(p.10-p.11)*

## Parameters
| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| Argument count | `|A|` | arguments | - | 25-200 in steps of 25 | 12 | Main random-AF classes. |
| Fixed attack probability | `p_att` | probability | - | 0.25, 0.5, 0.75 | 12 | Ordered-pair attack generation; self-attacks included. |
| First-method class size | - | AFs/class | 50 | - | 12 | 8 argument sizes x 3 probabilities x 50 = 1,200 AFs. |
| Random attack-count class size | - | AFs/class | 200 | - | 12 | 8 additional classes; `n_att` drawn uniformly between 0 and `|A|^2`. |
| Extreme singleton classes | - | classes | 16 | - | 12 | Empty attack relation and fully connected attack relation for each argument count. |
| Total test frameworks | - | AFs | 2,816 | - | 12 | All empirical analysis inputs. |
| Timeout per AF | - | minutes | 15 | - | 12 | Failure if no solution within time limit. |
| RAM | - | GB | 4 | - | 12 | No explicit RAM limit, but runs fail at memory saturation including swap. |
| CPU | - | GHz | 2.80 | - | 12 | Quad-core Intel Xeon, Linux. |
| IPC valid-case score | - | score | `1/(1+log10(T/T*))` | 0-1 | 13 | `T*` is best valid time; failures score 0; runtimes below 1 sec score 1. |
| Normalized IPC score | - | score | `(IPC / # valid cases) * 100` | 0-100 | 13 | Used for performance plots. |

## Effect Sizes / Key Quantitative Results
| Outcome | Measure | Value | CI | p | Population/Context | Page |
|---------|---------|-------|----|---|--------------------|------|
| Best SAT labelling encoding | Average runtime | `C_2` fastest overall among generated AFs | - | - | PS-GLU encodings | 13-14 |
| `C_2` average time at `|A|=25` | seconds | `6.25E-04` | - | - | PS-GLU; Table 1 | 14 |
| `C_2` average time at `|A|=100` | seconds | `6.39E-02` | - | - | PS-GLU; Table 1 | 14 |
| `C_2` average time at `|A|=200` | seconds | `1.38E+00` | - | - | PS-GLU; Table 1 | 14 |
| PS-GLU average time at `|A|=25` | seconds | `6.27E-04` | - | - | Five-system comparison; Table 2 | 18 |
| PS-GLU average time at `|A|=200` | seconds | `4.79E-01` | - | - | Five-system comparison; Table 2 | 18 |
| PS-PRE average time at `|A|=200` | seconds | `1.02E+00` | - | - | Five-system comparison; Table 2 | 18 |
| ASP average time at `|A|=200` | seconds | `1.24E+02` | - | - | Five-system comparison; Table 2 | 18 |
| ASP-META average time at `|A|=200` | seconds | `2.27E+01` | - | - | Five-system comparison; Table 2 | 18 |
| NOF average time at `|A|=200` | seconds | `5.02E+01` | - | - | Five-system comparison; Table 2 | 18 |
| Solution success | Percent success | PS-GLU, PS-PRE, ASP-META solve all cases; ASP and NOF decline as `|A|` grows | - | - | All test cases grouped by `|A|` | 14, 16 |
| Large-framework IPC | IPC normalized to 100 | PS-GLU remains near 100; PS-PRE declines less than ASP/NOF; ASP-META around 40 at high `|A|` | - | - | `|A|` grouped results | 16-17 |

## Methods & Implementation Details
- PrefSat is implemented in C++ and integrated with PrecoSAT and Glucose, yielding PS-PRE and PS-GLU. *(p.12)*
- The evaluation uses random finite AFs generated by argument count and attack-density regime; self-attacks are included in ordered-pair generation. *(p.12)*
- Compared systems are ASPARTIX with `dlv` (ASP), ASPARTIX-META with `gringo` and `claspD` (ASP-META), and NOF; none of the five systems uses parallel execution. *(p.14)*
- PS-GLU with `C_2` is selected for final comparison because it always outperforms PS-PRE on the selected encoding and because `C_2` is best overall on generated AFs. *(p.13-p.14)*
- The non-empty SAT encoding means the algorithm treats the empty preferred-extension case specially: if no non-empty preferred extension is found, it returns `{emptyset}`. *(p.8-p.9)*
- Performance is measured both by success within 15 minutes and by IPC-style normalized speed score, not only by raw runtime. *(p.12-p.13)*

## Figures of Interest
- **Fig. 1 (p.6):** Four small AFs used as counterexamples to show weakness of selected constraint subsets.
- **Fig. 2 (p.13):** IPC score by number of arguments for PS-GLU using the six alternative encodings; `C_2` stays highest.
- **Fig. 3 (p.15):** IPC score by attack percentage for `|A|=200`, showing that the best encoding can vary with graph density but `C_2` remains strong.
- **Fig. 4 (p.16):** Percentage of successful runs; PS-GLU, PS-PRE, and ASP-META maintain 100% success, while ASP and NOF fall with increasing `|A|`.
- **Fig. 5 (p.17):** IPC score by argument count across the five systems; PS-GLU dominates, PS-PRE is second for large frameworks, and ASP/NOF drop sharply.
- **Fig. 6 (p.19):** IPC score by attack percentage at `|A|=175`; PS-GLU stays near 100 while competitors vary by density.

## Results Summary
The choice of SAT encoding materially affects performance. `C_2` gives the best overall performance on generated AFs, although dense graphs include situations where `C_3` performs better than `C_1`. *(p.13-p.15)*

PS-GLU and PS-PRE both outperform ASP and NOF on all values `|A| > 25`, and the gap grows as `|A|` increases. PS-GLU is significantly faster than PS-PRE for `|A| > 175`. ASP-META solves all cases but has poorer IPC performance under the logarithmic IPC measure. *(p.14-p.17)*

The authors note that ASP-META can find preferred extensions for no-attack frameworks with 100 arguments in 1.27 seconds, but PS-PRE and PS-GLU are almost zero seconds there, so ASP-META receives an IPC value near zero and is indistinguishable from systems that fail on that condition. *(p.17)*

## Limitations
- The empirical comparison uses synthetic randomly generated AFs; derived AFs from knowledge bases and infinite-framework representations are reserved for future research. *(p.12, p.20)*
- Only six encodings are evaluated; twelve other redundant complete-labelling constraints are explicitly left for future work. *(p.7)*
- NOF is penalized by the relatively scarce memory availability of the test platform, since it often ran out of memory before the timeout. *(p.14)*
- Java tools aimed mainly at interactive use, such as ConArg and Dungine, are excluded because they are not suitable for systematic efficiency comparison on large test sets. *(p.19)*
- The paper compares empirical efficiency, but does not provide a new worst-case complexity classification for preferred enumeration. *(p.2, p.19)*

## Arguments Against Prior Work
- Dedicated labelling algorithms for preferred-extension computation share a transition-over-labellings strategy; the best such method is used as the only dedicated-algorithm comparator because it outperformed previous ones. *(p.4)*
- ASPARTIX is general and supports preferred computation, but translating AFs to ASP and solving via `dlv`/`gringo`/`claspD` is empirically slower than the direct SAT approach in this evaluation. *(p.4, p.14-p.18)*
- The most relevant prior SAT solver work focuses on acceptance problems and does not address extension enumeration, whereas this paper enumerates extensions. *(p.18)*
- MaxSAT is conceptually related because preferred labellings maximize `in` arguments, but the authors argue preferred extension computation is not simply MaxSAT because it maximizes acceptability of a subset of variables rather than the number of satisfiable constraints. *(p.18-p.19)*

## Design Rationale
- Preferred extensions can be obtained by maximizing complete extensions under set inclusion; this lets the algorithm use complete-labelling SAT encodings instead of directly encoding preferred semantics. *(p.3-p.4)*
- Multiple logically equivalent complete-labelling encodings are considered because redundant clauses may speed a solver through additional constraints, while excess syntactic complexity may hurt performance. *(p.5)*
- The algorithm enforces monotonic growth in the inner loop by fixing all current `in` arguments and requiring at least one additional argument to become `in`; this makes the search depth-first over complete-extension supersets. *(p.9-p.11)*
- The outer-loop blocking condition excludes subsets of already discovered preferred extensions so that future solver calls explore only candidates that can lead to new preferred extensions. *(p.9-p.11)*
- Glucose is chosen alongside PrecoSAT because both were strong SAT competition winners, giving two high-quality solver backends for the same generated CNFs. *(p.12)*

## Testable Properties
- For any finite AF, the implementation of Algorithm 1 must return exactly the set of preferred extensions. *(p.10)*
- Every satisfying assignment of the chosen `Pi_Gamma` encoding must correspond to a non-empty complete labelling, and every non-empty complete extension must be represented. *(p.7-p.9)*
- In each inner-loop iteration with a successful SAT call, `INARGS(lastcompfound)` strictly increases until no strict complete superset exists or all arguments are included. *(p.10-p.11)*
- If no non-empty complete extension is returned by the SAT solver from the initial encoding, the algorithm must return `{emptyset}`. *(p.9-p.11)*
- On the paper's random-AF benchmark design, PS-GLU with `C_2` should be the best overall system among the evaluated systems by normalized IPC score. *(p.13-p.18)*

## Relevance to Project
This paper is directly relevant to SAT-backed abstract-argumentation solvers. It gives a concrete enumeration algorithm, a comparison of logically equivalent complete-labelling encodings, and benchmark-generation parameters that can be reused for regression tests of preferred-extension enumeration.

## Open Questions
- [ ] Whether the twelve unevaluated redundant encodings can outperform `C_2` on specific graph families. *(p.7)*
- [ ] How PrefSat behaves on AFs derived from real knowledge bases rather than random graph models. *(p.20)*
- [ ] How to adapt the same approach to infinite argumentation frameworks and SCC-recursive subframework decomposition. *(p.20)*
- [ ] Whether a MaxSAT-style formulation can be made useful despite the conceptual mismatch identified by the authors. *(p.18-p.19)*

## Related Work Worth Reading
- Dung 1995 for the base abstract argumentation framework and acceptability semantics. *(p.1-p.3, p.21)*
- Caminada and Gabbay 2009 for complete labellings and the labelling view used by the algorithm. *(p.3, p.21)*
- Nofal, Dunne, and Atkinson 2012 for the strongest dedicated preferred-extension enumeration comparator. *(p.4, p.21)*
- Egly, Gaggl, and Woltran 2008 for ASPARTIX as the ASP-based translation approach. *(p.4, p.21)*
- Wallner, Weissenbacher, and Woltran 2013 for related advanced SAT techniques for argumentation. *(p.18, p.21)*
