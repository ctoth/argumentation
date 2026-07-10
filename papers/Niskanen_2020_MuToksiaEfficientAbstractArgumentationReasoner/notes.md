---
title: "mu-toksia: An Efficient Abstract Argumentation Reasoner"
authors: "Andreas Niskanen, Matti Järvisalo"
year: 2020
venue: "Proc. 17th International Conference on Principles of Knowledge Representation and Reasoning (KR 2020), Applications and Systems track, pp. 800-804"
doi_url: "https://doi.org/10.24963/kr.2020/82"
pages: 5
---

# mu-toksia: An Efficient Abstract Argumentation Reasoner

## One-Sentence Summary
mu-toksia is a C++ SAT-based abstract-argumentation reasoner that instantiates a **single SAT solver once per execution** and answers every reasoning task (credulous/skeptical acceptance, single extension, enumeration) over both static and dynamic AFs by **incremental solving under assumptions** against one persistent clause database, winning all main-track tasks of ICCMA 2019 while deliberately avoiding specialized per-semantics algorithms. *(abstract, Sec 3.1)*

## Problem Addressed
ICCMA-scale abstract argumentation requires solving NP-hard (credulous complete/preferred, semi-stable, stage) and Σ₂ᵖ-hard (skeptical preferred, semi-stable, stage) acceptance and enumeration tasks across many semantics, plus the ICCMA 2019 **dynamic track**, where a base AF is followed by a sequence of attack additions/deletions and each intermediate AF must be answered. Building a separate optimized algorithm per (semantics, task, static/dynamic) combination is a large engineering surface. mu-toksia's thesis: a single incremental SAT engine plus a small library of encodings and CEGAR loops covers all of it and is state-of-the-art in practice. *(Sec 1, Sec 3.1)*

## Key Contributions
- A **single-SAT-instance architecture**: one SAT solver created per run, kept alive through its assumptions API; all iterative computation reuses solver state (learned clauses, activity) instead of rebuilding. *(Sec 3.1)*
- **Explicit SAT encodings** (Figure 1) for conflict-free, admissible, complete, and stable sets over Boolean variables `x_a` (a is in the extension) and `y_a` (a is attacked by the extension). *(Sec 3.2)*
- **Task reductions that reuse primitives**: grounded = unit propagation on `com(F)`; DS-CO via grounded; stable primed with the grounded extension as a mandatory lower bound; DS-PR / semi-stable / stage via the Dvořák et al. (2014) CEGAR loop; ideal via union-of-admissible + subset maximization. *(Sec 3.2)*
- **Dynamic-AF handling for free**: one selector variable `r_{a,b}` per toggleable attack, switched on/off as a SAT assumption, lets every static technique run unchanged on dynamic AFs. *(Sec 3.2)*
- **Empirical evidence beyond ICCMA 2019** on harder ICCMA 2017 instances (1800s limit), where mu-toksia ranks first on DC-CO, DS-PR, DC-SST, DS-SST, DC-STG, DS-STG, DC-ID and contributes most to the virtual best solver on all tasks except *-ST. *(Sec 4, Table 1)*

## The SAT encodings (Figure 1) — load-bearing
Variables (per argument `a`, and per attack for dynamic AFs):
- `x_a` — true iff `a` is included in the (candidate) σ-extension.
- `y_a` — true iff `a` is attacked by the extension (some in-attacker of `a` is selected).
- `r_{a,b}` — reifies a **dynamic** attack `(a,b) ∈ R_d`; used as a SAT assumption to switch the attack present/absent during incremental solving. For static tasks `R_d = ∅` and the encodings collapse to the standard ones.
- `s_{a,b}`, `z_{a,b}` — auxiliary variables supporting the dynamic-attack encoding (from the companion dynamic-AF paper, Niskanen & Järvisalo 2020).

Encoding structure (standard encodings of Besnard & Doutre 2004):
- `cf(F)`: for each static attack `(a,b) ∈ R_s`, clause `(¬x_a ∨ ¬x_b)`; for each dynamic attack, `(r_{a,b} → (¬x_a ∨ ¬x_b))`.
- `adm(F) = cf(F)` plus, for each argument, clauses tying `y_a` to its attackers and requiring every attacker of a selected argument to be attacked back (defense).
- `com(F) = adm(F)` plus the reinstatement direction (every defended argument must be in).
- `stb(F) = adm(F)` plus `(x_a ∨ y_a)` for every argument (range covers all arguments; nothing is undecided).

## Per-task algorithms (Sec 3.2) — the reuse map
- **Grounded (grd).** Unit propagation on `com(F)` yields the polytime grounded extension (as in CoQuiAAS). Acceptance = check whether `x_q` is propagated true. No search. *(This is why grounded is nearly free and is used as a subroutine below.)*
- **Complete (com).** Credulous acceptance of `q`: one SAT call on `adm(F) ∧ x_q` (NP-complete). Skeptical acceptance: via grounded (grounded ⊆ every complete extension and is the ∩). Single extension: grounded. Enumeration: enumerate all models of `com(F)`, after each extension `E` add the blocking clause `⋁_{a∈E} ¬x_a ∨ ⋁_{a∉E} x_a` until UNSAT.
- **Stable (stb).** First compute grounded `E_grd` (subset of every stable extension). Credulous: `stb(F) ∧ ⋀_{a∈E_grd} x_a ∧ x_q`. Skeptical: UNSAT of `stb(F) ∧ ⋀_{a∈E_grd} x_a ∧ ¬x_q`. Single/enumeration: on `stb(F) ∧ ⋀_{a∈E_grd} x_a`. Priming with grounded is a cheap, always-valid lower bound that shrinks the search.
- **Preferred (prf).** Credulous acceptance = credulous acceptance under complete (they coincide). Skeptical acceptance (Σ₂ᵖ-complete): the iterative SAT-based **CEGAR** approach of Dvořák et al. (2014), *without* Cegartix's shortcuts.
- **Semi-stable (sem) & stage (stg).** Introduce range variables `r_a ↔ (x_a ∨ y_a)`. Credulous/skeptical via the Dvořák et al. (2014) CEGAR algorithms, again omitting shortcuts. For stage, first test whether a stable extension exists (assume `⋀_a r_a`); if so, run the stable algorithm instead. Single extension: subset-maximize a complete extension (resp. conflict-free set for stage) w.r.t. the range. Enumeration: assume the range after subset-maximization, enumerate all complete (resp. cf) extensions with that range, then add a clause blocking all subsets of that range and iterate.
- **Ideal (id).** Compute the union of admissible extensions on `com(F)` (add `⋁_{a∉E} x_a` per extension found); reject early if `q` not in the union. Then keep the union-arguments not attacked by the union; reject if `q` not there. Assume all arguments outside that set are out, and iteratively subset-maximize a complete extension within it — this is exactly the ideal extension (Dunne, Dvořák & Woltran 2013; Wallner, Weissenbacher & Woltran 2013).

## Dynamic AFs — generalization (Sec 3.2)
Given base AF `F=(A,R)` and a change sequence `Λ=(δ_1,…,δ_n)` where each `δ_i` is `+(a,b)` or `−(a,b)`, mu-toksia partitions attacks into **static** `R_s = ⋂ R_i` (always present) and **dynamic** `R_d = (⋃ R_i) \ R_s` (toggled). Each dynamic attack `(a,b)` gets a reification variable `r_{a,b}` conditioning its clauses. To answer the task at step `i`, mu-toksia solves under the SAT assumptions setting each `r_{a,b}` to its present/absent value in `R_i`. Because attacks are switched via assumptions rather than clause edits, the same solver instance and all learned clauses persist across the whole sequence, giving the incremental speedup that beats competitors on the dynamic track. The full dynamic algorithm is in the companion paper (Niskanen & Järvisalo, ECAI 2020).

## Implementation, Availability, Usage (Sec 3.3)
- **Language / libs:** C++ with standard STL data structures (only external dependency: a Boost hash function). MIT license. Repository: https://bitbucket.org/andreasniskanen/mu-toksia.
- **SAT backends:** interfaces to **Glucose** (Audemard & Simon 2018) and **CryptoMiniSAT** (Soos et al. 2009). A generic `SATSolver.h` interface lets any assumptions-capable SAT solver be plugged in. (Evaluation used CryptoMiniSAT 5.6.8.)
- **Solver-tuning detail:** in the CEGAR algorithms, variables are decided to their **positive polarity** by default, giving modest gains over the solver default.
- **Input formats:** APX (`arg(a).`, `att(a,b).`) and TGF; dynamic changes as `+att(a,b).`/`-att(a,b).` (APX) or `+a b`/`-a b` (TGF).
- **CLI:** `./mu-toksia -p <task> -f <file> -fo <format> [-a <query>] [-m <modfile>]`, e.g. `-p DS-PR` (skeptical preferred) or `-p DC-CO-D` (credulous complete on a dynamic AF); `-m` supplies the change file for dynamic tasks.

## Semantics definitions used (Sec 2)
For AF `F=(A,R)`: `D_F(S)` = arguments defended by `S`; range `R_F(S) = S ∪ {a | ∃ b∈S, (b,a)∈R}`. `S∈adm` iff `S⊆D_F(S)`; `com` iff `S=D_F(S)`; `prf` = ⊆-maximal complete; `stb` iff `R_F(S)=A`; `sem` = complete with ⊆-maximal range; `stg` = conflict-free with ⊆-maximal range; `grd` = ⊆-minimal complete; `id` = ⊆-maximal admissible contained in every preferred extension. Supported tasks: DC, DS, SE, EE for `com, prf, stb, sem, stg, grd, id` (static) and `com, prf, stb, grd` (dynamic).

## Results Summary (Sec 4, Table 1)
On the ICCMA 2017 acceptance instances (empirically harder than ICCMA 2019; 1800s / 16 GB limits) mu-toksia is compared against argmat-sat, ArgSemSAT, Aspartix V19-4, Cegartix, CoQuiAAS, and pyglaf. mu-toksia **solves the most instances** on DC-CO (325), DS-PR (326), DC-SST (336), DS-SST (327), DC-STG (317), DS-STG (314), DC-ID (327), and ties Aspartix on DC-ST; the only loss is DS-ST (312 vs Aspartix 316), hypothesized to be because stable ≈ answer-set semantics favors the ASP-based Aspartix. mu-toksia makes the **largest contribution to the virtual best solver (VBS)** on every task except the *-ST tasks, and on DC-SST/DC-STG/DC-ID sits very close to the VBS curve. *(Table 1, Figure 2)*

## Parameters / Configuration

| Name | Where | Value in paper | Notes |
|------|-------|----------------|-------|
| SAT backend | build | Glucose / CryptoMiniSAT | pluggable via `SATSolver.h` |
| CEGAR variable polarity | solver flag | positive | modest gain over default |
| SAT instances per run | architecture | 1 | kept alive via assumptions API |
| Time / memory limit (eval) | experiment | 1800 s / 16 GB | 3× the ICCMA 10-min limit |
| `x_a` | encoding | Boolean | a in σ-extension |
| `y_a` | encoding | Boolean | a attacked by extension |
| `r_{a,b}` | encoding | Boolean (assumption) | dynamic attack present/absent |

## Relevance to Project
mu-toksia is the **architectural target** for this project's SAT backend. The project already ingests `Cerutti_2015_ArgSemSAT-1.0ExploitingSATSolvers` and `Thimm_2021_FudgeLight-weightSolverAbstract` as SAT-solver references; mu-toksia is the competition-winning, most-general instance of the same idea and the cleanest source for:
1. **The single-persistent-incremental-SAT-solver pattern** — one instance per run, all tasks as solve-under-assumptions, matching the direction of refactoring the package's SAT helpers into an incremental task-directed backend (`solving/af_sat.py`, `solving/solver.py`).
2. **The task→primitive reduction map** — grounded by unit propagation, DS-CO via grounded, stable primed by grounded, DS-PR/SST/STG via CEGAR without shortcuts, ideal via union-of-admissible + subset-maximize. This is a concrete checklist for which acceptance routes should be native SAT loops vs. reductions.
3. **Assumption-based attack toggling for dynamics** — the `r_{a,b}` selector-variable trick is directly applicable to any incremental/query-directed reasoning where the attack set changes (dynamic track, SCC-local re-solving in `core/scc_recursive.py`, incremental ABA in the ABA workstream).
4. **The range-variable + CEGAR encoding** for semi-stable and stage — a template for replacing range-maximal native enumeration with task-directed SAT loops (cf. `Pu_2017_ArgmatSatApplyingSATSolver`, `Dvorak_2014_ComplexitySensitiveDecisionProcedures`, which supplies the CEGAR oracle structure).

## Related Work Worth Reading
- Dvořák, Järvisalo, Wallner, Woltran (2014), *Complexity-sensitive decision procedures for abstract argumentation* — the CEGAR algorithms mu-toksia implements for DS-PR/sem/stg. Already in the collection as `Dvorak_2014_ComplexitySensitiveDecisionProcedures`.
- Cerutti, Giacomin, Vallati — ArgSemSAT (`Cerutti_2015_ArgSemSAT-1.0ExploitingSATSolvers`), the other complete-labelling SAT solver.
- Lagniez, Lonca, Mailly (2015), *CoQuiAAS* — the constraint/SAT solver whose grounded-by-propagation idea mu-toksia reuses; predecessor of crustabri (see `Mailly_2023_CrustabriRustArgumentationReasoner`).
- Besnard & Doutre (2004), *Checking the acceptability of a set of arguments* — origin of the SAT encodings in Figure 1.
- Niskanen & Järvisalo (2020, ECAI), *Algorithms for dynamic argumentation frameworks: an incremental SAT-based approach* — the companion paper with the full dynamic-track algorithm behind the `r_{a,b}` variables.

## Open Questions / Notes for Us
- [ ] mu-toksia omits Cegartix's CEGAR "shortcuts"; measure whether adding shortcuts helps our hard DS-PR families.
- [ ] The DS-ST loss to Aspartix suggests an ASP backend may still win on stable — worth remembering for backend routing (cf. the ASP references `Egly_2010_...`, `Lehtonen_2021_DeclarativeAlgorithmsComplexityABA`).
- [ ] The single-instance design assumes the solver's assumptions interface is cheap to re-enter; verify our chosen backend (PySAT/CaDiCaL) has comparable incremental performance.
