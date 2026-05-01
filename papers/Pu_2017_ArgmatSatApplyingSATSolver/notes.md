---
title: "argmat-sat: Applying SAT Solvers for Argumentation Problems based on Boolean Matrix Algebra"
authors: "Fuan Pu; Hang Ya; Guiming Luo"
year: 2017
venue: "ICCMA 2017 System Descriptions"
doi_url: "https://argumentationcompetition.org/2017/argmat-sat.pdf"
pages: "1-4"
produced_by:
  agent: "gpt-5"
  skill: "paper-reader"
  status: "stated"
  timestamp: "2026-05-01T23:47:07Z"
---
# argmat-sat: Applying SAT Solvers for Argumentation Problems based on Boolean Matrix Algebra

## One-Sentence Summary
argmat-sat gives compact CNF encodings for basic and range-based Dung semantics, then uses assumption-space search for maximal semantics such as preferred, ideal, semi-stable, and stage.

## Problem Addressed
The paper describes an ICCMA 2017 solver that uses Boolean matrix algebra to produce SAT encodings for argumentation semantics and uses assumption-space algorithms for maximal and maximal-range reasoning tasks. *(p.1)*

## Key Contributions
- Presents CNF encodings for stable, admissible, and complete semantics using Boolean vectors and auxiliary variables. *(p.1-p.2)*
- Introduces range variables `r` for semi-stable and stage semantics. *(p.1-p.3)*
- Uses assumption space to search maximal preferred extensions and ideal semantics. *(p.2-p.4)*
- Uses a two-stage assumption-space process for maximal range semantics: find a maximal range, fix it, enumerate extensions under that range, then repeat. *(p.3)*
- Implements in C++ with CryptoMiniSat5 and supports ICCMA 2017 command interface. *(p.4)*

## Methodology
The solver represents extension membership with a Boolean vector `x`. Auxiliary vectors model attacked arguments, neutrality, and range. Basic semantics are reduced to CNF formulas over these vectors. Maximality is handled outside the base CNF by adding and clearing assumption-space clauses during iterative SAT solving. *(p.1-p.4)*

## Key Equations / Statistical Models

$$
H_\sigma^\Delta(x) = \bigwedge_{x_i \in X} H_\sigma(x_i)
$$

Where the full CNF for semantics `sigma` is the conjunction of per-argument encodings. *(p.2)*

$$
r = x + R^+(x)
$$

Where `r` represents the range of extension vector `x`, i.e. arguments in `x` plus arguments attacked by `x`; this is used for semi-stable/stage encodings. *(p.1-p.3)*

## Parameters

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| Extension vector | `x` | Boolean vector | - | length n | 1 | `x_i = 1` means argument `x_i` is in the extension. |
| Auxiliary attacked/neutrality vectors | `o`, `p` | Boolean vector | - | length n | 1 | Used by admissible and complete encodings. |
| Range vector | `r` | Boolean vector | - | length n | 1-3 | Represents the range of extension `x`. |
| Stable encoding variable count | - | count | n | - | 2 | Table 1. |
| Admissible/complete variable count | - | count | 2n or 3n | - | 2-3 | Depends on encoding variant. |
| Semi-stable/stage variable count | - | count | 2n or 3n | - | 3 | Table 2. |
| SAT engine | - | implementation | CryptoMiniSat5 | - | 4 | Chosen for interface and performance. |

## Methods & Implementation Details
- Stable semantics can be encoded using extension membership alone. *(p.2)*
- Admissible and complete encodings may need auxiliary variables, with multiple variants trading variable count and formula structure. *(p.2)*
- Semi-stable encodings can be based on admissible or complete encodings plus range variables. *(p.3)*
- Stage semantics is encoded using conflict-free plus range variables. *(p.3)*
- Preferred enumeration repeatedly asks for a solution, adds assumption clauses requiring larger solutions, stores a maximal solution, clears assumption clauses, then adds hard blocking clauses against subsets of the maximal solution. *(p.4)*
- Maximal range enumeration first finds a maximal range, then fixes that range and enumerates all extensions under it, clears assumption space, and repeats. *(p.3)*

## Figures of Interest
- **Table 1 (p.2):** CNF conversions for stable, admissible, and complete semantics with variable counts.
- **Table 2 (p.3):** CNF conversions for semi-stable and stage semantics using range vector `r`.
- **Algorithm 1 (p.4):** Assumption-space algorithm for enumerating preferred extensions.

## Results Summary
The paper is a system description rather than a benchmark study. It states that argmat-sat was submitted to ICCMA 2017, supports multi-threading, and runs on Windows and Unix. *(p.4)*

## Limitations
- The table encodings are dense and require careful translation; the paper is terse. *(p.2-p.3)*
- Maximality is handled procedurally through assumption space rather than a single formula. *(p.3-p.4)*
- It does not give a direct skeptical preferred algorithm like Thimm/Cerutti/Vallati 2021. *(p.1-p.4)*

## Arguments Against Prior Work
The paper emphasizes that maximal requirements are hard to encode in pure Boolean formulas, motivating assumption-space search. *(p.2)*

## Design Rationale
- Use Boolean matrix algebra as a systematic way to derive CNF encodings. *(p.1-p.2)*
- Use assumption clauses for maximality because preferred and range-maximal semantics need iterative improvement. *(p.2-p.4)*
- Separate maximal-range search from extension enumeration under a fixed range. *(p.3)*

## Testable Properties
- For stage semantics, candidates must be conflict-free and range-maximal. *(p.3)*
- For semi-stable semantics, candidates must satisfy admissible/complete-style constraints and range-maximality. *(p.3)*
- Preferred enumeration must block subsets of already-found maximal solutions. *(p.4)*
- After a maximal range is fixed, all extensions under that range must be enumerated before searching another range. *(p.3)*

## Relevance to Project
This paper is the main source for upgrading our current `SE-SST` and `SE-STG` witness-only range growth into full range-maximal decision procedures. It also reinforces that maximality should be implemented as iterative solver control, not a monolithic native enumeration call.

## Open Questions
- [ ] Translate Table 2 into our current Z3 variable conventions and differential-test against native `SST`/`STG`.
- [ ] Decide whether to support full enumeration under fixed maximal ranges or only task-directed witnesses/counterexamples for ICCMA.
- [ ] Evaluate CryptoMiniSat-style assumptions versus Z3 push/pop for range loops.

## Related Work Worth Reading
- Fu, Guiming, Jiang 2017 on Boolean algebra encodings.
- Wallner, Weissenbacher, Woltran 2013 on advanced SAT techniques for abstract argumentation.
- CoQuiAAS for constraint-based comparison.
