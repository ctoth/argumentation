# Research: nonstable AF solver backend

## Summary
The current timeout pattern is expected: stable AF tasks now use a SAT witness path, but complete/preferred/semi-stable/stage/ideal tasks still fall back to native extension enumeration in the package. The research consensus behind competitive ICCMA solvers is not "enumerate everything faster"; it is task-directed SAT/ASP/CP with encodings for base semantics plus iterative maximality/range checks. The right project direction is a package-local Dung AF SAT portfolio: complete/admissible/range encodings in Z3 first, preferred and semi-stable via iterative maximality checks, and task-specific acceptance procedures that avoid full extension enumeration when possible.

## Approaches Found

### SAT over Complete Labellings
**Source:** https://www.argumentationcompetition.org/2015/pdf/paper_10.pdf  
**Description:** ArgSemSAT encodes complete labellings into SAT and uses iterative SAT calls to solve complete, grounded, preferred, stable, and acceptance tasks. Preferred extensions are searched in the space of complete labellings, with additional constraints driving the search toward maximal `in` sets.  
**Pros:** Directly matches our Dung API; gives a clean path for SE/DC/DS under complete and preferred; proven competitive in ICCMA.  
**Cons:** Preferred skeptical acceptance and maximality require iterative calls, not one CNF.  
**Complexity:** Medium.

### SAT Algorithms for Preferred Extensions
**Source:** https://arxiv.org/abs/1310.4986  
**Description:** Cerutti, Dunne, Giacomin, and Vallati reduce complete-extension computation to SAT, then use a depth-first/iterative method to derive preferred extensions.  
**Pros:** Good first implementation target for `SE-PR` and preferred witness search; aligns with our existing SAT stable code.  
**Cons:** Extension enumeration can still be expensive; acceptance should be task-directed where possible.  
**Complexity:** Medium.

### Direct Preferred Skeptical Acceptance and Ideal
**Source:** https://www.ijcai.org/proceedings/2021/285  
**Description:** Thimm, Cerutti, and Vallati avoid computing preferred extensions for skeptical preferred acceptance, using an iterative SAT algorithm based on a new characterization; they apply related ideas to ideal semantics.  
**Pros:** Targets one of our worst cases, `DS-PR`, without enumerating all preferred extensions. Also points at a better `ID` implementation.  
**Cons:** More algorithmically delicate than simple complete-labelling SAT.  
**Complexity:** High.

### Fudge-Style SAT Reductions
**Source:** https://arxiv.org/abs/2109.03106  
**Description:** Fudge is a lightweight SAT-based abstract argumentation solver using standard reductions plus novel encodings for skeptical preferred and ideal tasks.  
**Pros:** Best model for our package-local solver: small, SAT-centric, task-oriented.  
**Cons:** The paper is a system description; we still need to implement and test the encodings locally.  
**Complexity:** Medium to High.

### Complexity-Sensitive SAT Procedures
**Source:** https://eprints.cs.univie.ac.at/3787/  
**Description:** Dvorak, Jarvisalo, Wallner, and Woltran propose using lower-complexity decision procedures whenever possible, then iterative SAT for harder preferred, semi-stable, and stage reasoning.  
**Pros:** Strong design principle for `auto`: cheap special cases first, hard semantics second.  
**Cons:** More portfolio logic; not a single backend function.  
**Complexity:** High.

### SAT Matrix Encodings for Maximal and Range Semantics
**Source:** https://argumentationcompetition.org/2017/argmat-sat.pdf  
**Description:** argmat-sat describes CNF encodings for stable, admissible, complete, and range-based semantics, with assumption-based algorithms for preferred/ideal and semi-stable/stage.  
**Pros:** Directly covers our timeout family: `PR`, `ID`, `SST`, and `STG`.  
**Cons:** The PDF is a system paper, so details need careful translation into tested code.  
**Complexity:** Medium to High.

### Constraint Programming
**Source:** https://arxiv.org/abs/1212.2857  
**Description:** ConArg models AF reasoning as constraint programming and supports complete, preferred, semi-stable, stage, ideal, and related tasks.  
**Pros:** Broad semantics coverage; useful as an external comparison oracle.  
**Cons:** Pulling in CP engines is a heavier dependency path than extending our current Z3/SAT backend.  
**Complexity:** High.

## Key Papers
- [Cerutti, Dunne, Giacomin, Vallati (2013)](https://arxiv.org/abs/1310.4986) - SAT-based preferred-extension computation via complete-extension SAT search.
- [Dvorak, Jarvisalo, Wallner, Woltran (2014)](https://eprints.cs.univie.ac.at/3787/) - Complexity-sensitive SAT decision procedures for preferred, semi-stable, and stage semantics.
- [Cerutti, Vallati, Giacomin (2015)](https://www.argumentationcompetition.org/2015/pdf/paper_10.pdf) - ArgSemSAT system design around complete-labelling SAT.
- [Thimm, Cerutti, Vallati (2021)](https://www.ijcai.org/proceedings/2021/285) - Skeptical preferred reasoning without computing preferred extensions; also ideal extension ideas.
- [Thimm, Cerutti, Vallati (2021)](https://arxiv.org/abs/2109.03106) - Fudge SAT-based solver system.
- [Pu, Ya, Luo (2017)](https://argumentationcompetition.org/2017/argmat-sat.pdf) - SAT encodings for basic, maximal, and range semantics.
- [ICCMA 2023 overview](https://www.sciencedirect.com/science/article/pii/S000437022500030X) - Current competition context, benchmark/data availability, and solver landscape.

## Existing Implementations
- **ArgSemSAT**: C++/Glucose SAT solver family for grounded, complete, preferred, and stable ICCMA tasks.
- **Fudge**: lightweight SAT-reduction solver for abstract argumentation, including preferred skeptical and ideal-oriented encodings.
- **argmat-sat**: SAT solver using Boolean matrix encodings and assumption-based maximality/range algorithms.
- **ConArg**: constraint-programming solver supporting many Dung semantics; better as a comparison oracle than as the first dependency.
- **ASPARTIX/clingo family**: ASP route for broad semantics coverage; useful later if we want an external portfolio backend.

## Complexity vs Quality Tradeoffs
The low-effort fix is runner filtering, but that only avoids the problem. A useful solver fix starts with complete-labelling SAT because complete semantics is the base for preferred and semi-stable. A medium implementation gets fast `SE-CO`, `DC-CO`, `DS-CO`, `DC-PR`, and preferred witness search. A high-quality ICCMA-oriented backend adds direct skeptical preferred, range-maximal semi-stable/stage, and ideal algorithms, all task-directed so acceptance checks do not enumerate full extension families unless the task requires enumeration.

## Recommended Workstream

### Phase 1: Define the SAT Surface
- Add `src/argumentation/af_sat.py` or expand `sat_encoding.py` around three-valued complete labellings.
- Variables per argument: `in[a]`, `out[a]`, `undec[a]`, exactly-one constraints.
- Encode complete labelling conditions:
  - `in[a]` iff all attackers are `out`.
  - `out[a]` iff some attacker is `in`.
  - `undec[a]` iff not `in` and not `out`.
- Add helpers for model-to-extension and blocking clauses.
- Differential tests against native semantics for generated AFs up to small sizes.

### Phase 2: Fast Complete Tasks
- Implement `sat_complete_extension(framework, require_in=None, require_out=None)`.
- Route `SE-CO`, `DC-CO`, and `DS-CO` through SAT in `auto`.
- For skeptical complete, check unsatisfiability of a complete extension with query out.
- This should remove many native complete timeouts quickly.

### Phase 3: Preferred Without Full Enumeration
- Implement admissible/complete candidate growth to a subset-maximal preferred extension.
- Route `SE-PR` through iterative SAT growth.
- Route `DC-PR` through the finite-AF fact that every admissible set extends to a preferred extension: check admissible/complete support containing the query, then grow only for a witness if needed.
- Implement `DS-PR` using the IJCAI 2021/Fudge-style direct counterexample procedure, not full preferred enumeration.

### Phase 4: Semi-Stable and Stage via Range Maximality
- Add range variables or computed range constraints.
- Implement iterative SAT search that grows range until no strict range extension exists.
- Route `SE-SST`, `DC-SST`, `DS-SST`, and later `STG` through range-maximal search.
- Differential-test range maximality against native on small AFs.

### Phase 5: Ideal
- First implementation: derive preferred-skeptical accepted set and compute the maximal admissible subset contained in it.
- Better implementation: port Fudge/IJCAI ideal-specific SAT procedure.
- Route `SE-ID` and `DC/DS-ID` only after differential tests pass.

### Phase 6: Portfolio Defaults
- Keep `auto` as the public default.
- Routing target:
  - `ST`: existing stable SAT.
  - `GR`: native grounded, already polynomial.
  - `CO`: complete-labelling SAT.
  - `PR`: SAT growth/direct preferred algorithms.
  - `SST/STG`: range-maximal SAT.
  - `ID`: ideal-specific SAT.
- Keep native as a correctness oracle and tiny-instance fallback, not the default ICCMA path.

## Estimated Implementation Effort
- **Minimal approach:** 1-2 focused days for complete-labelling SAT plus `CO` routing and tests.
- **Useful approach:** 3-5 focused days for complete plus preferred `SE/DC` and partial `DS-PR`.
- **Full approach:** 1-2 weeks for preferred skeptical, semi-stable/stage range maximality, ideal, broad differential tests, and runner benchmarks.

## Open Questions
- [ ] Do we want to use Z3 only, or define a solver-neutral incremental SAT adapter now?
- [ ] Should `sat_encoding.py` remain CNF-only, with Z3 algorithms in a new `af_sat.py`?
- [ ] Which ICCMA subtracks should become acceptance-first versus extension-enumeration-first?
- [ ] Should we add external ASP/clingo as a portfolio backend after the package-local SAT work?

## References
- Cerutti, Dunne, Giacomin, Vallati. Computing Preferred Extensions in Abstract Argumentation: a SAT-based Approach. https://arxiv.org/abs/1310.4986
- Dvorak, Jarvisalo, Wallner, Woltran. Complexity-Sensitive Decision Procedures for Abstract Argumentation. https://eprints.cs.univie.ac.at/3787/
- Cerutti, Vallati, Giacomin. ArgSemSAT-1.0: Exploiting SAT Solvers in Abstract Argumentation. https://www.argumentationcompetition.org/2015/pdf/paper_10.pdf
- Thimm, Cerutti, Vallati. Skeptical Reasoning with Preferred Semantics in Abstract Argumentation without Computing Preferred Extensions. https://www.ijcai.org/proceedings/2021/285
- Thimm, Cerutti, Vallati. Fudge: A light-weight solver for abstract argumentation based on SAT reductions. https://arxiv.org/abs/2109.03106
- Pu, Ya, Luo. argmat-sat: Applying SAT Solvers for Argumentation Problems based on Boolean Matrix Algebra. https://argumentationcompetition.org/2017/argmat-sat.pdf
- ICCMA 2023 overview. https://www.sciencedirect.com/science/article/pii/S000437022500030X
