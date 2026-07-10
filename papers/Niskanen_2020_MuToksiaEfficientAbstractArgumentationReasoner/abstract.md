# Abstract

## Original Text (Verbatim)

We describe the mu-toksia argumentation reasoning system. The system supports a range of different reasoning tasks over both standard and dynamic abstract argumentation frameworks under essentially all central argumentation semantics, covering all tracks and reasoning tasks considered in the most recent International Competition on Computational Models of Argumentation (ICCMA 2019). mu-toksia ranked first in all reasoning tasks in the main track of ICCMA 2019, and has been shown to scale noticeably better on the dynamic track tasks than its current competitors. In this paper, we provide an overview of mu-toksia and its algorithmic and implementation-level details, and provide further empirical evidence beyond ICCMA 2019 on the efficiency of mu-toksia compared to related systems.

---

## Our Interpretation

mu-toksia is the ICCMA 2019 main-track-winning abstract-argumentation reasoner and the canonical "single incremental SAT solver" architecture this project's solver is converging on. Its defining engineering choice is that exactly one SAT solver instance is created per invocation and kept alive through its assumptions API for the whole run, so every task (credulous/skeptical acceptance, single-extension, enumeration) is a sequence of incremental solve calls against a shared clause database rather than a fresh encoding per query. It deliberately avoids specialized per-semantics algorithms: grounded is unit propagation on the complete encoding; DS-CO reduces to grounded; DS-PR, semi-stable and stage use the Dvořák et al. (2014) CEGAR loop (without Cegartix's shortcuts); stable is primed with the grounded extension as a lower bound; ideal is union-of-admissible plus a subset-maximization pass. Dynamic AFs are handled by adding one selector variable `r_{a,b}` per toggleable attack and flipping attacks on/off purely through SAT assumptions, reusing all the static machinery. It is the direct architectural precedent for the project's incremental `af_sat` backend (see `Cerutti_2015_ArgSemSAT-1.0ExploitingSATSolvers`, `Thimm_2021_FudgeLight-weightSolverAbstract`).
