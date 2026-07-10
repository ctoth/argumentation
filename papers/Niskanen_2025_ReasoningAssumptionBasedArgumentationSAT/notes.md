---
title: "Reasoning in Assumption-Based Argumentation via SAT"
authors: "Andreas Niskanen, Masood Feyzbakhsh Rankooh, Tuomo Lehtonen, Matti Järvisalo"
year: 2025
venue: "KR 2025 (22nd International Conference on Principles of Knowledge Representation and Reasoning)"
doi_url: "https://proceedings.kr.org/2025/68/"
pages: "707-717"
---

# Reasoning in Assumption-Based Argumentation via SAT

## One-Sentence Summary
The paper develops and evaluates the first purely SAT-based reasoning approaches for (flat, logic-programming-instantiation) assumption-based argumentation (ABA), by encoding the acyclicity constraint on derivations in four different ways — a level-based encoding, a vertex-elimination (graph acyclicity) encoding, a graph-based acyclicity user propagator, and an unfounded-set (UFS) user propagator built on IPASIR-UP — and shows these can match or beat the dominant ASP-based ASPforABA on ICCMA23 and a new CLUSTERED benchmark family. *(p.707-708)*

## Problem Addressed
For abstract argumentation frameworks (AFs), SAT-based solvers dominate; for structured formalisms like ABA the dominant practical approach is ASP, because ASP's stable-model semantics *natively* enforces the acyclicity of derivations (an atom must have a non-circular support), so derivation length never has to be represented explicitly. Translating ABA to AFs suffers worst-case exponential blow-up (Strass, Wyner, and Diller 2019), so reasoning "natively" on the ABA (assumption-set) level is needed. The open gap: no direct SAT encodings / SAT-based solving techniques existed for ABA, because SAT does not natively rule out cyclic self-support of atoms, and that acyclicity constraint over potentially long derivation chains is the hard modelling problem this paper attacks. *(p.708-710)*

## Key Contributions
- First direct SAT encodings and SAT-based solving techniques for ABA (credulous/skeptical acceptance under stable, complete, preferred, ideal). *(p.708)*
- A base propositional encoding of ABA semantics (cf/adm/com/stb) via `x_a`, `y_a`, `z_a` variables, plus four distinct ways to enforce acyclic derivations. *(p.710-712)*
- Two "fully encode acyclicity as clauses" variants: **level-based** encoding (SAT-LEVEL) and **vertex-elimination / graph-based** encoding (SAT-VE). *(p.710-712)*
- Two "acyclicity via user propagator" variants using IPASIR-UP: a **graph-based acyclicity propagator** (SAT-ACYC) and an **unfounded-set propagator** (SAT-UFS) mirroring CLASP's source-pointer technique. *(p.711-713)*
- All four approaches double as the abstraction solver inside CEGAR for beyond-NP tasks (DS-PR skeptical-preferred, SE-ID ideal extension), adapting μ-toksia's iterative SAT algorithms to ABA. *(p.708, 713)*
- A new CLUSTERED ABA benchmark generator (based on StableGenerator ideas) that produces frameworks with many stable/preferred assumption sets while keeping rules acyclic. *(p.713)*
- Open-source implementation at https://bitbucket.org/coreo-group/100ba. *(p.713)*
- Empirical result: SAT-based ABA (esp. SAT-VE and SAT-UFS) is, for the first time, competitive with and can outperform ASPforABA, including ~50% more instances solved on the beyond-NP SE-ID task on CLUSTERED. *(p.708, 714-715)*

## Study Design (empirical papers)
- **Type:** Empirical solver-runtime evaluation (algorithm benchmarking).
- **Hardware/Limits:** 2.50-GHz Intel Xeon Gold 6248 CPUs, 15-min (900s) per-instance time limit, 16-GB memory limit. *(p.713)*
- **Systems compared:** ASPforABA (ASP, CLINGO 5.6.2 backend) vs SAT-LEVEL, SAT-VE, SAT-ACYC, SAT-UFS (all CaDiCaL 2.1.3 + IPASIR-UP). *(p.713)*
- **Problems:** DC-CO, DC-ST, DS-ST, DS-PR, SE-ID. *(p.713)*
- **Benchmarks:** ICCMA23 ABA track (400 ABFs, but heavily filtered — see below) and a new CLUSTERED set (450 ABFs → 1350 acceptance queries). *(p.713)*

## Methodology
ABA reasoning is reduced to finding a σ-assumption set for σ ∈ {adm, com, stb}. Boolean variables `x_a` (a is in the assumption set A_τ), `y_a` (A_τ attacks {a}), and `z_a` (A_τ does not defend {a}, i.e. {a} attacked by B_τ = A_τ ∪ {undefeated non-members}) are introduced per assumption a. Semantics are encoded by `φ_cf`, `φ_adm`, `φ_com`, `φ_stb`. The technical crux is faithfully encoding the *derivation* of an atom from an assumption set, which requires an acyclicity constraint (an atom must not cyclically support itself). Four mechanisms enforce that acyclicity; two are "eager" clause encodings and two are "lazy" propagators via IPASIR-UP. For beyond-NP problems (DS-PR, SE-ID) the SAT encoding of complete semantics is used as an abstraction inside an iterative CEGAR loop adapted from μ-toksia.

## Key Equations / Statistical Models

Base semantics encodings over per-assumption variables `x_a`, `y_a`, `z_a` (a ∈ A): *(p.710)*

$$
\varphi_{cf}(F) = \bigwedge_{a \in \mathcal{A}} (x_a \rightarrow \neg y_a)
$$
An assumption in the set cannot be attacked by the set (conflict-freeness). *(p.710)*

$$
\varphi_{adm}(F) = \varphi_{cf}(F) \wedge \bigwedge_{a \in \mathcal{A}} (x_a \rightarrow \neg z_a)
$$
Admissibility: an assumption in the set must be defended (not `z_a`). *(p.710)*

$$
\varphi_{com}(F) = \varphi_{adm}(F) \wedge \bigwedge_{a \in \mathcal{A}} (\neg z_a \rightarrow x_a)
$$
Completeness: every defended assumption is in the set. *(p.710)*

$$
\varphi_{stb}(F) = \varphi_{cf}(F) \wedge \bigwedge_{a \in \mathcal{A}} (\neg x_a \rightarrow y_a)
$$
Stability: every assumption not in the set is attacked by the set. *(p.710)*

Where: `x_a=1` iff a ∈ A_τ; `y_a=1` iff A_τ attacks {a}; `z_a=1` iff B_τ attacks {a} (A_τ does not defend {a}), with B_τ = A_τ ∪ {a ∈ A | τ(y_a)=0}. *(p.710)*

**Level-based acyclicity (SAT-LEVEL), Section 3.1.** Upper bound U = |L| − |A| (for flat ABA U may be |L|−|A|). Variables `d_s^i` (s derived from A_τ at iteration i) and `e_s^i` (s derived from B_τ at iteration i) for each non-assumption s ∈ L\A and i = 1..U. *(p.710)*

$$
\varphi_{att}^{lvl}(F) = \bigwedge_{a \in \mathcal{A}} \left( y_a \leftrightarrow \psi_{att}^{lvl}(a) \right)
$$
where ψ_att^lvl(a) is `x_{ā}` if the contrary ā is an assumption, and `⋁_{i=1}^{U} d_{ā}^i` otherwise (i.e. {a} attacked iff its contrary ā is derivable from A_τ). *(p.710)*

$$
\varphi_{ndef}^{lvl}(F) = \bigwedge_{a \in \mathcal{A}} \left( z_a \leftrightarrow \psi_{ndef}^{lvl}(a) \right)
$$
where ψ_ndef^lvl(a) is `¬y_{ā}` if contrary ā is an assumption and `⋁_{i=1}^{U} e_{ā}^i` otherwise ({a} not defended iff ā derivable from B_τ). *(p.710)*

Derivation-of-atom-at-level definitions φ_A(s,i) and φ_B(s,i): *(p.710-711)*

$$
d_s^i \leftrightarrow \bigvee_{\substack{r \in \mathcal{R} \\ head(r)=s}} \left( \bigwedge_{\substack{a \in body(r) \\ a \in \mathcal{A}}} x_a \wedge \bigwedge_{\substack{a \in body(r) \\ a \in \mathcal{L}\setminus\mathcal{A}}} d_a^{i-1} \right)
$$
with `d_s^0 = 0` for all s ∈ L\A: s is derived from A_τ at iteration i iff some rule with head s has all assumption body atoms set true and all non-assumption body atoms derived by iteration i−1. *(p.711)*

$$
e_s^i \leftrightarrow \bigvee_{\substack{r \in \mathcal{R} \\ head(r)=s}} \left( \bigwedge_{\substack{a \in body(r) \\ a \in \mathcal{A}}} \neg y_a \wedge \bigwedge_{\substack{a \in body(r) \\ a \in \mathcal{L}\setminus\mathcal{A}}} e_a^{i-1} \right)
$$
same for derivations from B_τ (assumption in body must be un-attacked, i.e. `¬y_a`). *(p.711)*

**Proposition 1:** For σ ∈ {adm, com, stb}, τ satisfying Φ_σ^lvl(F) = φ_σ(F) ∧ φ_att^lvl(F) ∧ φ_ndef^lvl(F) ∧ ⋀_{s∈L}⋀_{i=1}^U φ_A(s,i) ∧ ⋀_{s∈L}⋀_{i=1}^U φ_B(s,i) corresponds to a σ-extension A_τ, and vice versa. For **stable** semantics φ_ndef and φ_B(s,i) are **not needed** (every assumption outside A_τ is attacked). *(p.711)*

**Graph-based acyclicity (SAT-VE / SAT-ACYC), Section 3.2.** Non-assumption variables `d_a`, `e_a`; plus edge-activation variables `r_{s,t}^d`, `r_{s,t}^e` for each s,t ∈ L\A with a rule head(r)=s, t ∈ body(r). Semantics reuse `φ_att`, `φ_ndef` (non-indexed forms with ψ_att(a)=`x_ā` or `d_ā`; ψ_ndef(a)=`¬y_ā` or `e_ā`). *(p.711-712)*

$$
\varphi_A^{acyc}(s) = \left( \bigvee_{\substack{r \in \mathcal{R}\\head(r)=s}} \left( \bigwedge_{\substack{a\in body(r)\\a\in\mathcal{A}}} x_a \wedge \bigwedge_{\substack{a\in body(r)\\a\in\mathcal{L}\setminus\mathcal{A}}} d_a \right) \rightarrow d_s \right) \wedge \left( d_s \rightarrow \bigvee_{\substack{r\in\mathcal{R}\\head(r)=s}} \left( \bigwedge_{\substack{a\in body(r)\\a\in\mathcal{A}}} x_a \wedge \bigwedge_{\substack{a\in body(r)\\a\in\mathcal{L}\setminus\mathcal{A}}} (d_a \wedge r_{a,s}^d) \right) \right)
$$
If a rule with head s has a satisfied body then s is derived; and if s is derived, all edge variables `r_{a,s}^d` for a ∈ body(r) ∩ (L\A) must be true. Analogous `φ_B^acyc(s)` uses `e`, `r^e`. *(p.712)*

Directed graphs from activated edges: *(p.712)*
$$
E_\tau^d = \{(s,t) \mid s,t \in \mathcal{L}\setminus\mathcal{A}, \tau(r_{s,t}^d)=1\}, \quad E_\tau^e = \{(s,t) \mid s,t \in \mathcal{L}\setminus\mathcal{A}, \tau(r_{s,t}^e)=1\}
$$
Acyclicity of G_τ^d (and G_τ^e) makes satisfying assignments correspond to σ-extensions. Redundancy-limiting link: *(p.712)*
$$
\varphi_G = \bigwedge_{\substack{s,t\in\mathcal{L}\setminus\mathcal{A}\\ \exists r\in\mathcal{R}: head(r)=s, t\in body(r)}} (r_{s,t}^d \rightarrow r_{s,t}^e)
$$
ensures G_τ^d is a subgraph of G_τ^e (derivations from A_τ reused for B_τ, since A_τ ⊆ B_τ). For σ = stb, G_τ^σ = G_τ^d; for σ ∈ {adm, com}, G_τ^σ = G_τ^e. **Proposition 3** ties Φ_σ^acyc(F) = φ_σ(F) ∧ φ_att(F) ∧ φ_ndef(F) ∧ ⋀ φ_A^acyc(s) ∧ ⋀ φ_B^acyc(s) with acyclic G_τ^σ to σ-extensions. φ_ndef and φ_B^acyc(s) not required for stable. *(p.712)*

**Vertex elimination fill-in (SAT-VE), Section 3.2 (Rankooh & Rintanen 2022; Rose, Tarjan, Lueker 1976).** For each v ∈ L\A: *(p.712)*
$$
F(v) = \{ \langle x,y \rangle \mid \langle x,v \rangle \in E, \langle v,y \rangle \in E, x \neq y \}
$$
$$
G(v) = ((\mathcal{L}\setminus\mathcal{A})\setminus\{v\},\ E(v) \cup F(v)), \quad E(v) = \{\langle x,y\rangle \in E \mid x \neq v \neq y\}
$$
For elimination order α: {1..n} → L, cumulative fill-in `F_α(G) = ⋃_{i=1}^{n-1} F_{i-1}(α(i))`, vertex-elimination graph `G_α^* = (L, E ∪ F_α(G))`. Key property: regardless of order α, a cycle in G induces a 2-cycle in G_α^*. Encoding introduces `e_{s,t}^*` for edges of G_α^* (only if α(s) ≤ α(t), using `¬e_{s,t}^*` if α(s) > α(t)) plus constraints `r_{s,t}^d → e_{s,t}^*` (σ=stb) / `r_{s,t}^e → e_{s,t}^*` and, for each i and ⟨s,t⟩ ∈ F_{i-1}(α(i)): `e_{s,α(i)}^* ∧ e_{α(i),t}^* → e_{s,t}^*`. *(p.712)*

**UFS propagator base encoding (SAT-UFS), Section 4.2:** *(p.712)*
$$
\varphi_A^{ufs}(s) = d_s \leftrightarrow \bigvee_{\substack{r\in\mathcal{R}\\head(r)=s}} \left( \bigwedge_{\substack{a\in body(r)\\a\in\mathcal{A}}} x_a \wedge \bigwedge_{\substack{a\in body(r)\\a\in\mathcal{L}\setminus\mathcal{A}}} d_a \right)
$$
$$
\varphi_B^{ufs}(s) = e_s \leftrightarrow \bigvee_{\substack{r\in\mathcal{R}\\head(r)=s}} \left( \bigwedge_{\substack{a\in body(r)\\a\in\mathcal{A}}} \neg y_a \wedge \bigwedge_{\substack{a\in body(r)\\a\in\mathcal{L}\setminus\mathcal{A}}} e_a \right)
$$
This "simpler encoding" (both sides of the equivalence, no acyclicity clauses) is completed by the UFS propagator that forbids circular support. Φ_σ^ufs(F) = φ_σ(F) ∧ φ_att(F) ∧ φ_ndef(F) ∧ ⋀ φ_A^ufs(s) ∧ ⋀ φ_B^ufs(s); φ_ndef and φ_B^ufs not required for stable. *(p.712-713)*

## Parameters

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| Max derivation length upper bound (level enc.) | U | iterations | — | =\|L\|−\|A\| for flat ABA | 710 | Number of level copies of d_s^i / e_s^i |
| Per-instance time limit | — | s | 900 | — | 713 | 15 min |
| Memory limit | — | GB | 16 | — | 713 | — |
| CLUSTERED partitions | P | count | — | [5,7] or {25,30,35} | 713-714 | number of assumption clusters |
| CLUSTERED assumptions/partition | P_A | count | — | [25,30,35] or [100,150,200] | 713-714 | fresh assumptions per partition |
| CLUSTERED non-assumption atoms/partition | P_L | count | — | [25,30,35] or [100,150,200] | 713-714 | fresh non-assumption atoms |
| CLUSTERED max rules per atom | mra | count | 3 | — | 713-714 | fixed at 3 for benchmark set |
| CLUSTERED max rule body size | mrs | count | 2 | — | 713-714 | fixed at 2 for benchmark set |
| CLUSTERED contrary probability | C | probability | — | {0.8, 0.9} | 713-714 | C near 1 → each partition a stable ext |
| ICCMA23 atoms per ABF | — | count | — | {25,100,500,2000,5000} | 713 | 80 instances each |
| ICCMA23 assumption fraction | — | % | — | {10, 30} | 713 | half instances 10%, half 30% |
| ICCMA23 (mra, mrs) combos | — | — | — | (5,5),(5,10),(10,5),(10,10) | 713 | 10 ABFs each |

## Effect Sizes / Key Quantitative Results

Table 1 (ICCMA23), #solved (mean runtime s), best per (mra,mrs) in bold. Selected rows: *(p.714)*

| Outcome | Measure | Value | Context | Page |
|---------|---------|-------|---------|------|
| DC-CO, (10,10) | #solved | SAT-VE **72** vs ASPforABA 65 | SAT-VE best | 714 |
| DC-ST, (10,10) | #solved | SAT-VE **55** vs ASPforABA 46 | SAT-VE best | 714 |
| DS-ST, (10,10) | #solved | SAT-VE **19** vs ASPforABA 13 | SAT-VE best | 714 |
| SE-ID, (10,5) | #solved | SAT-UFS **100** vs ASPforABA 99 | SAT-UFS best | 714 |
| SE-ID, (10,10) | #solved | ASPforABA 89 = SAT-ACYC 89 = SAT-UFS 89 | tie | 714 |
| SE-ID (CLUSTERED) beyond-NP | rel. instances solved | SAT-VE ≈ +50% vs ASPforABA | SAT-VE excels | 715 |
| DC-ST YES (CLUSTERED) | #solved | SAT-VE 663 vs ASPforABA 655 | narrow SAT-VE win | 715 |
| Encoding size ICCMA23 (avg) | vars / clauses | SAT-VE 167k / 32M; SAT-LEVEL 8M / 33M | SAT-VE far fewer vars | 715 |
| Encoding size CLUSTERED | vars / clauses | SAT-VE 7k / 45M; SAT-LEVEL 8M / 75M | SAT-VE compactness | 715 |
| SAT-VE clause blow-up vs base (no acyc) | ratio | ICCMA23 min 1.12 max 2833.5 avg 224.9; CLUSTERED min 1.03 max 1.74 avg 1.14 | overhead of acyclicity | 715 |
| UFS propagation share of runtime | % | CLUSTERED max 4% (avg <1%); ICCMA23 max 81% (avg <4%) | propagator cost | 715 |

Overall ranking on CLUSTERED: SAT-VE solves the most on each problem (except DS-PR, where ASPforABA leads under ~800s); SAT-ACYC is least performant aside from SAT-LEVEL; SAT-LEVEL memouts on most CLUSTERED instances. *(p.714-715)*

## Methods & Implementation Details
- SAT backend: CaDiCaL 2.1.3; propagators via IPASIR-UP interface (Fazekas et al. 2024). *(p.713)*
- Four system names: SAT-LEVEL (level encoding), SAT-VE (vertex-elimination encoding), SAT-ACYC (graph-based acyclicity propagator), SAT-UFS (unfounded-set propagator). *(p.713)*
- **Graph-based acyclicity propagator (Section 4.1):** init with Φ_σ^acyc(F); for σ=stb all `r_{s,t}^d` observed, for σ∈{adm,com} `r_{s,t}^e` observed. Edges labeled possible/enabled/disabled; when an observed var set true/false the edge is enabled/disabled and its decision level recorded; on backtrack, enabled/disabled edges above new level revert to possible. On propagation, for each newly enabled edge (s,t): DFS from t along enabled edges — if s reached, a cycle C found → external clause `⋁_{(u,v)∈C} ¬r_{u,v}^d` (resp `¬r_{u,v}^e`). Otherwise DFS from s along reversed enabled edges; with N1 = nodes reachable from t, N2 = nodes reverse-reachable from s, P = edges labeled possible, propagate `¬r_{u,v}` for each (u,v) ∈ P ∩ (N1×N2); reason clause `⋁_{(u',v')∈C'} ¬r_{u',v'}^d` where C' is the "almost-cycle". *(p.712)*
- **UFS propagator (Section 4.2):** follows CLASP's source-pointer approach, implemented via IPASIR-UP; all `d_s`, `e_s` observed. Keep two source pointers `source_d(s)`, `source_e(s)` per s ∈ L\A. While τ(d_s)≠0 (resp τ(e_s)≠0), try to set source pointer to a rule r ∈ R giving non-circular support for s. Atoms U for which no source pointer can be established are unfounded → propagate `¬d_s` (resp `¬e_s`) with reason clause stating no rule can provide external support for U. *(p.713)*
- **Beyond-NP (DS-PR, SE-ID):** adapt μ-toksia's iterative SAT algorithms to ABA. DS-PR: SAT-based CEGAR (Dvořák et al. 2014) — iteratively find candidate complete extensions not containing the query argument, check for counterexample supersets. SE-ID: iterative SAT first finds all arguments attacked by a complete extension, then finds unique subset-maximal complete extension in the complement (Niskanen & Järvisalo 2020). Complete-semantics encoding serves as base abstraction; all four acyclicity variants usable as abstraction solver. *(p.713)*
- **Base-semantics idea for derivations:** an atom x derivable from S iff there is an "activated" rule for x whose body atoms are each assumptions in S or derived by another activated rule. Cyclic self-support (e.g. rules (x←y),(y←x)) must be forbidden — that is the entire purpose of the acyclicity machinery. *(p.710)*
- **CLUSTERED generator:** choose P partitions; per partition i, A_i = P_A fresh assumptions each with a fresh contrary, L_i = P_L fresh non-assumption atoms; for each x ∈ L_i generate r ∈ [1,mra] rules of size s ∈ [1,mrs] with body drawn from L_i ∪ A_i; for each assumption a ∈ A\A_i add rule (ā ← x) for random x ∈ L_i with probability C. Consequence: SCCs of the rule graph cannot exceed P_L; no attacks within a partition; C near 1 → each partition self-attacks most outside assumptions, yielding many stable extensions. Two sub-sets: "small number of large partitions" (P,P_A,P_L ∈ [25,30,35]) and "large number of small partitions" (P ∈ [5,7], P_A,P_L ∈ [100,150,200]). 5 ABFs per (P,P_L,P_A) combo × C ∈ {0.8,0.9} = 450 ABFs; 3 query types per ABF (an assumption, a contrary atom, an atom that is neither) = 1350 acceptance instances. *(p.713-714)*

## Figures of Interest
- **Table 1 (p.714):** #solved and mean runtime for all 5 systems on ICCMA23 across (mra,mrs) ∈ {(10,10),(10,5),(5,10),(5,5)} for DC-CO, DC-ST, DS-ST, DS-PR, SE-ID. (5,10) instances trivial for all solvers.
- **Fig 1 (p.714):** cactus/coverage plots (instances solved vs per-instance time limit) for DC-ST, DS-ST, DC-CO, DS-PR, SE-ID on CLUSTERED; SAT-VE line highest.
- **Fig 2 (p.715):** per-instance runtime scatter of ASPforABA vs SAT-VE on CLUSTERED for DC-ST, DS-ST, DC-CO, DS-PR, SE-ID, split by NO/YES answer (and by #clusters for SE-ID); SAT-VE wins especially on NO-instances (CaDiCaL better at UNSAT proofs) and as cluster count grows (25/30/35).

## Results Summary
On ICCMA23, SAT-VE and SAT-UFS perform particularly well and outperform ASPforABA on many problems; SAT-UFS excels on SE-ID, SAT-VE on the one-shot DC-CO/DC-ST/DS-ST. SAT-LEVEL is weakest. On CLUSTERED, SAT-VE solves the most on every problem except DS-PR (ASPforABA leads until ~800s); on SE-ID SAT-VE solves ~50% more than ASPforABA. SAT-VE encodings are dramatically more variable-compact than SAT-LEVEL (167k vs 8M vars on ICCMA23). *(p.714-715)*

## Limitations
- A significant part of ICCMA23 is trivially unsatisfiable *without* any acyclicity constraint (216 for DC-ST, 289 for DS-ST, 154 for DC-CO and hence DS-PR); the authors filtered these out (except SE-ID, which always has an ideal extension). So the ICCMA23 evaluation covers only the acyclicity-relevant subset. *(p.713)*
- SAT-LEVEL scales poorly (memouts on most CLUSTERED instances) because of the U-indexed level variables. *(p.714-715)*
- SAT-ACYC (graph propagator) is the least performant aside from SAT-LEVEL. *(p.715)*
- On ICCMA23 the UFS propagator can consume up to 81% of runtime (avg <4%) — propagation overhead is instance-dependent. *(p.715)*
- Scope restricted to flat, logic-programming instantiation of ABA (no assumptions as rule heads). *(p.708)*

## Arguments Against Prior Work
- ABA→AF translation (to reuse SAT-based AF reasoners) suffers worst-case exponential blow-up (Strass, Wyner, and Diller 2019), motivating native ABA-level reasoning. *(p.708)*
- Prior structured-argumentation practice is essentially ASP-only for ABA; purely SAT-based approaches were "essentially non-existent" — SAT cannot natively enforce acyclic derivations the way ASP stable semantics does, so a naive SAT encoding wrongly allows cyclic self-support (rules (x←y),(y←x) both activated with no assumption support). *(p.708, 710)*
- The dominant ASPforABA (best in ICCMA 2023 ABA track) is the state-of-the-art baseline the paper aims to beat; it uses CLINGO one-shot for NP tasks and CEGAR-style iteration for DS-PR / cautious mode for SE-ID. *(p.708, 713)*

## Design Rationale
- Two acyclicity philosophies: (i) fully encode acyclicity as clauses — either explicit level-indexing (SAT-LEVEL) or the compact vertex-elimination encoding (SAT-VE) that lets the SAT solver reason/learn on the acyclicity constraint at the propositional level; (ii) enforce acyclicity lazily via a user propagator (SAT-ACYC graph DFS, or SAT-UFS source pointers) so no acyclicity clauses are materialized. *(p.708, 710-713)*
- Vertex elimination chosen for compactness: it avoids the U-indexed level blow-up while still allowing direct propositional reasoning about acyclicity; the key theoretical guarantee (a cycle in G induces a 2-cycle in G_α^* regardless of ordering) makes the encoding sound. *(p.712, 715)*
- UFS propagator chosen to import ASP's proven source-pointer technique into SAT, directly attacking the same non-circular-support problem that makes ASP natively good at ABA. *(p.712-713)*
- `φ_G` (r^d ⊆ r^e) added to reuse A_τ derivations for B_τ since A_τ ⊆ B_τ, limiting redundancy. *(p.712)*
- For stable semantics, the B_τ-side machinery (φ_ndef, φ_B, z-variables) is dropped because every non-member assumption is attacked. *(p.711-712)*

## Testable Properties
- For σ ∈ {adm, com, stb}, satisfying assignments of Φ_σ^lvl(F) ↔ σ-extensions A_τ = {a | τ(x_a)=1} (Prop. 1). *(p.711)*
- For σ ∈ {adm, com, stb}, satisfying assignments of Φ_σ^acyc(F) with G_τ^σ acyclic ↔ σ-extensions (Prop. 3). *(p.712)*
- An atom x is derivable from S ⊆ A iff there is an acyclic subgraph G_S^x of the rule graph G meeting the three conditions of Prop. 2. *(p.711)*
- Regardless of elimination order α, any cycle in G induces a 2-cycle in the vertex-elimination graph G_α^* (soundness of the VE encoding). *(p.712)*
- For σ = stb, edge set G_τ^σ = G_τ^d (`r_{s,t}^d`); for σ ∈ {adm, com}, G_τ^σ = G_τ^e (`r_{s,t}^e`). *(p.712)*
- Level upper bound U = |L| − |A| suffices for flat ABA derivations. *(p.710)*
- Complexity landscape (context, Cyras/Heinrich/Toni 2021, Dimopoulos et al. 2002): credulous acceptance NP-complete under adm/com/prf/stb; skeptical in P under adm & com, Π₂^P-complete under preferred, coNP-complete under stable; both acceptance problems in Θ₂^P under ideal. *(p.710)*

## Relevance to Project
Directly on-target for this repo's ABA SAT work. This repo has `src/argumentation/structured/aba/aba_acyc_sat.py` (a DC-CO-era cone/acyclicity prototype) and an "exp-5 eager arc-acyclic stable" encoding in `src/argumentation/structured/aba/aba_sat.py`. The paper is the reference design for exactly these encodings: the `x_a`/`y_a`/`z_a` base variables, the cf/adm/com/stb clause sets, and the four acyclicity mechanisms. See `plug-in-mapping.md` in this directory for a concrete mapping of the paper's variants (level / VE / graph-acyc-propagator / UFS-propagator) onto our two modules, stating which we have, partially have, and lack. The reference implementation is at https://bitbucket.org/coreo-group/100ba (hence the repo/branch shorthand "100ba").

## Open Questions
- [ ] Could SAT-UFS's high worst-case propagation share (81% on some ICCMA23 instances) be reduced with a better source-pointer scheduling?
- [ ] Would a hybrid (VE encoding + UFS propagator) combine SAT-VE's compactness with UFS's SE-ID strength?
- [ ] How do these encodings extend to non-flat ABA (assumptions as heads), which is out of scope here?

## Related Work Worth Reading
- Rankooh and Rintanen 2022 — Propositional encodings of acyclicity and reachability by vertex elimination (the VE encoding basis). *(p.712)*
- Gebser, Janhunen, and Rintanen 2014 — SAT modulo graphs: acyclicity (the acyclicity-propagator basis). *(p.712)*
- Gebser, Kaufmann, and Schaub 2012 — Conflict-driven ASP / source pointers (UFS propagator basis). *(p.713)*
- Fazekas et al. 2024 — Satisfiability modulo user propagators / IPASIR-UP (the interface enabling SAT-ACYC and SAT-UFS). *(p.712)*
- Lehtonen, Wallner, and Järvisalo 2021a — Declarative algorithms and complexity for ABA (ASPforABA baseline). *(p.713)*
- Niskanen and Järvisalo 2020 — μ-toksia (iterative SAT algorithms adapted for DS-PR/SE-ID). *(p.713)*
- Cerutti et al. 2014 — StableGenerator (basis for CLUSTERED). *(p.713)*
