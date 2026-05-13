# Graph-Theory & Preprocessing Speedups for AF / ABA Reasoning — 2026-05-12

Scope: techniques that make Dung-AF and structured (ABA/ASPIC) reasoning faster *in
practice*, emphasizing low-cost wins for the `argumentation` Python library. Companion
to `reports/argumentation-reductions-anchor.md` (which catalogs the SAT/ASP/QBF/Datalog/DG
*reductions*); this report covers the orthogonal axis — structural decomposition and
preprocessing layered *on top of* whatever solver backend is used.

Method note: most concrete numbers below come from web abstracts and secondary sources
(ICCMA result write-ups). Where I could not open the primary PDF (arXiv 1310.4986 is
password-protected on download; several CEUR PDFs returned as binary), I have flagged the
claim as "secondary source" rather than "verified from paper". PDFs retrieved into
`papers/` are listed at the end.

---

## Ranking (expected practical speedup × low implementation cost)

### 1. Grounded-reduct / well-founded preprocessing — HIGHEST PRIORITY, near-free

**Papers / solvers.** This is the de-facto standard ICCMA preprocessing step. µ-toksia
(Niskanen & Järvisalo, "µ-toksia: An Efficient Abstract Argumentation Reasoner", KR 2020 /
ICCMA 2019 winner) computes the grounded extension by Boolean unit propagation and uses it
to settle DC/DS trivially and to seed the SAT instance; the same idea appears in pyglaf
(Alviano), ASPARTIX-V (Dvořák et al., "ASPARTIX-V19/-V21", FoIKS 2020 / arXiv:2109.03166),
fudge (Thimm/Cerutti/Vallati), and crustabri. Folklore precision: the *grounded reduct*
loop is — compute grounded extension `G`; every `a ∈ G` is IN everywhere, every `a` attacked
by `G` is OUT everywhere; delete `G ∪ G⁺` and all incident attacks; iterate on the residual
AF (the residual's own grounded extension is empty by construction after one pass, so it is
really a single pass for *grounded*, but iterating helps when combined with the cheap
reductions in §3). Then solve the residual with the expensive semantics.

**What the library does now.** `dung.grounded_extension` exists. `af_sat.py` lines ~501–510
already use it as a *shortcut* in the preferred-skeptical path (`query in grounded` → accept;
`query in attacked_by(grounded)` → reject; acyclic → grounded settles it). But the SAT
encodings in `af_sat.py` / `sat_encoding.py` for complete/admissible/preferred/stable/semi-stable
do **not** restrict the solved framework to the grounded residual — they encode the full AF.
The ABA path (`aba_sat.py`) similarly does not pre-fix assumptions forced by the
well-founded part.

**How it'd slot in.** Add a `reduce_to_grounded_residual(framework) -> (residual_af, fixed_in,
fixed_out)` helper in `dung.py`; have the SAT/ASP enumerators (a) emit `fixed_in`/`fixed_out`
unconditionally as the prefix of every extension and (b) build the CNF over the residual only.
For enumeration, post-hoc re-union `fixed_in` into each returned extension. This is pure graph
manipulation, no new solver dependency, and it is the single most reliable speedup in the
competitive-solver literature. For ABA, the analogue is "assumptions whose contrary is never
derivable from any assumption set are forced IN; assumptions whose contrary is derivable from
∅ are forced OUT" — cheaper than it sounds since the support masks are already precomputed.

---

### 2. Cheap one-shot structural reductions (self-attackers, dominated args, acyclic / symmetric special cases) — near-free, compounds with #1

**Papers.**
- Self-attacking arguments `a R a`: can never be in any conflict-free set, so delete `a` and
  every attack `a R b`. Standard; appears in essentially every competitive solver and is the
  basis of Baumann's *stable kernel* (Baumann, "Context-free and context-sensitive kernels:
  update and deletion equivalence in abstract argumentation", ECAI 2014; see also Oikarinen &
  Woltran, "Characterizing strong equivalence for argumentation frameworks", AIJ 175, 2011 —
  the stable/admissible/complete/grounded kernels). The library *already implements these
  kernels* in `af_revision.py` (`stable_kernel`, `baumann_2015_kernel`, `_is_baumann_kernel_redundant`)
  — but only uses them for revision/equivalence, not as a *pre-solve simplifier*.
- "Arguments attacked by an unattacked argument": unattacked args are in grounded, so this is
  subsumed by §1, but detecting it without the full grounded fixpoint is one BFS layer.
- Acyclic AF ⇒ unique extension = grounded = stable = preferred = complete (Dung 1995). Cheap
  cycle check (the library already has SCC machinery in `dung.py:_strongly_connected_components`);
  if every SCC is a singleton with no self-loop, return `grounded_extension` and skip the solver
  entirely for *all* admissibility-based semantics.
- Symmetric AF (irreflexive + `R = R⁻¹`) ⇒ coherent and relatively grounded; naive sets =
  preferred = stable, and these are *polynomial* to enumerate (maximal independent sets of an
  undirected graph component-wise). Coste-Marquis, Devred & Marquis, "Symmetric Argumentation
  Frameworks", ECSQARU 2005, LNCS 3571. Detecting symmetry is O(|R|).
- "Bridgeless / SCC-trivial dominated arguments": an argument with no attackers and a single
  outgoing attack chain — collapsible. Subsumed by §1 in most cases.

**What the library does now.** Has SCC code (used only for CF2/stage2), has the Baumann/
Oikarinen-Woltran kernels (used only for revision), has `grounded_extension`. None of it is
wired into a "simplify before you solve" front door.

**How it'd slot in.** A single `preprocess_af(framework, semantics) -> (residual, recombine_fn,
maybe_full_answer)` function: (1) drop self-attackers; (2) if acyclic → return grounded; (3) if
symmetric → return naive-set enumerator; (4) apply the kernel for the requested semantics
(`af_revision.baumann_2015_kernel`) to shrink the attack relation; (5) apply §1's grounded
residual; (6) hand the shrunk AF to the SAT/ASP backend. Each step is a few lines and they
compose. Risk: must be careful that the kernel chosen matches the *queried* semantics
(stable-kernel only sound for stable; admissible-kernel for admissible/complete/preferred etc.) —
the existing `AFKernelSemantics` enum already encodes this.

---

### 3. SCC-recursive computation of standard semantics — moderate cost, large speedup on layered AFs

**Papers.**
- Baroni, Giacomin & Guida, "SCC-recursiveness: a general schema for argumentation semantics",
  Artificial Intelligence 168(1–2):162–210, 2005. Establishes that all of Dung's
  admissibility-based semantics (complete, preferred, stable, grounded) plus stage and CF2 are
  SCC-recursive: extensions of the whole AF can be reconstructed from extensions of the
  sub-frameworks induced by each SCC of the *condensation* DAG, processed in topological order,
  with each SCC's sub-AF further restricted by which of its attackers from upstream SCCs are
  IN / OUT / UNDEC ("defended" / "attacked" / "provisionally defended" labels passed downstream).
- Cerutti, Giacomin & Vallati, "Computing Preferred Extensions in Abstract Argumentation: a
  SAT-Based Approach", arXiv:1310.4986 (TAFA 2013 / published 2014 LNCS 8306) — the ArgSemSAT
  line. Combines per-SCC SAT calls with the SCC recursion. Secondary source: "delivers
  significantly better performance in the large majority of considered cases" vs ASPARTIX,
  ConArg, and the non-SCC PrefSAT baseline.
- Cerutti, Giacomin & Vallati, "An SCC Recursive Meta-Algorithm for Computing Preferred
  Labellings in Abstract Argumentation" (Univ. Huddersfield, eprints 19946; AAAI/COMMA-era).
  Secondary source: "significant improvement of performances" from the recursion; the
  meta-algorithm is parametric in a "base algorithm" for the single-SCC case.
- Cerutti, Tachmazidis, Vallati, Batsakis, Giacomin & Antoniou, "Exploiting Parallelism for
  Hard Problems in Abstract Argumentation", AAAI 2015 — parallel SCC-recursive preferred
  enumeration (independent sibling SCCs solved concurrently).
- ASPARTIX-V21 (Dvořák et al., arXiv:2109.03166) moved from monolithic one-shot ASP to
  multi-shot / domain-heuristic encodings; ConArg (Bistarelli & Santini, constraint programming)
  also exploits component structure.

**Is it "just topologically process the SCCs"?** No. Two subtleties: (a) you must thread three
labels (defended / attacked / provisionally-defended-i.e.-undec) from already-processed upstream
SCCs into the restriction of the current SCC's sub-AF — the "in or attacked from outside" status
prunes which arguments of the SCC are even candidates; (b) for *preferred/stable* a single SCC
can still have multiple extensions, so you get a **product** over SCCs and must enumerate the
cross-product (with the upstream labels constraining each factor). The win is that each SAT call
is over one SCC, not the whole AF, and learned clauses don't have to span unrelated components.
On AFs that are essentially one giant SCC there is no benefit and a small overhead.

**Implementation cost on top of an existing SAT-per-query solver.** Medium. You need: condensation
DAG (have `_strongly_connected_components` already; need topological order, easy), the
label-restriction logic, and a recursion that for each SCC calls the existing
`af_sat`/`sat_encoding` enumerator on the *restricted* sub-AF then crosses results. ~150–300 LOC.
The existing CF2/stage2 code in `dung.py` (lines 516–568) is literally a worked example of the
SCC-recursive loop — it can be generalized so that complete/preferred/stable use the same
skeleton with a different single-SCC base case (SAT call instead of naive-sets).

**How it'd slot in.** New `dung._scc_recursive(framework, base_solver, label)` driving the
existing per-SCC SAT base case; `af_sat.preferred_extensions` etc. dispatch to it when the
condensation has > 1 non-trivial node. Combine with §1+§2 first (often the residual after
grounded-reduct is *already* a union of small SCCs). Lowest-risk first deliverable: just the
*topological grounded propagation* (which is §1 done SCC-by-SCC) before any SAT — then graduate
to full SCC-recursive enumeration.

---

### 4. ABA / ASPIC-specific construction-side speedups — moderate cost, large win on structured inputs

**Papers.**
- Lehtonen, Wallner & Järvisalo, "Reasoning over Assumption-Based Argumentation Frameworks via
  Direct Answer Set Programming Encodings", AAAI 2019. The point: do **not** materialize the
  abstract AF (which is worst-case exponential in #arguments); encode ABA semantics *directly*
  over assumptions and the deductive closure.
- Lehtonen, Wallner & Järvisalo, "Declarative Algorithms and Complexity Results for
  Assumption-Based Argumentation", JAIR 2021 (jair.1.12479) — the underlying complexity /
  algorithm story.
- Lehtonen, Wallner & Järvisalo, "Harnessing Incremental Answer Set Solving for Reasoning in
  Assumption-Based Argumentation", arXiv:2108.04192 (TPLP 2021 / ICLP). CEGAR + incremental ASP
  for Π₂ᵖ ABA tasks (skeptical preferred). This is the ASPforABA solver that won the ICCMA 2021
  and 2023 ABA tracks. PDF retrieved.
- Construction-side: the AF built from ABA need not be enumerated eagerly — you only need the
  attacks reachable from the query. "Lazy" / on-demand argument construction (the contrary
  derivations as bitmask supports) is exactly the library's `aba_sat.py` support-mask approach;
  the literature analogue is the "claim-level" reasoning in the above papers.

**What the library does now.** `aba_sat.py` uses precomputed support bitmasks for contraries
(avoids materializing arguments — good, this is already the right idea). `aba_asp.py` exists.
But: (a) ABA preferred uses iterative-SAT over admissible models; an *incremental* ASP CEGAR
loop (à la ASPforABA) or even keeping the SAT solver instance alive with assumptions would be
faster; (b) no grounded-reduct-style fixing of forced assumptions before the search; (c) the
flat-ABA restriction (`NotFlatABAError`) is fine but means non-flat ABA still falls back to AF
materialization — Lehtonen et al. handle the logic-programming fragment without that.

**How it'd slot in.** Two cheap pieces first: (1) before solving any ABA semantics, run a
"well-founded assumptions" pass — repeatedly: any assumption with no support for its contrary
is forced IN, anything whose contrary has a support contained in the current forced-IN set is
forced OUT — and restrict the SAT/ASP search to the remainder (mirror of §1). (2) For ABA
preferred, keep one SAT solver alive across the admissible-maximization iterations using
assumption literals + blocking clauses instead of rebuilding. Bigger piece: an ASP CEGAR
backend for ABA-DS-PR matching ASPforABA. The library already has clingo wired (commit 8ab2a6f
"Load clingo through optional dependency helper"), so the dependency cost is paid.

---

### 5. Treewidth / structural-parameter DP — LOW priority for this library right now

**Papers.**
- Dvořák, Pichler & Woltran, "Towards fixed-parameter tractable algorithms for abstract
  argumentation", AIJ 186, 2012 — concrete tree-decomposition DP for the standard semantics.
- Fichte, Hecher & Meier, "Decomposition-Guided Reductions for Argumentation and Treewidth"
  (IJCAI 2021) and Mahmood, "Structure-Aware Encodings…" (2025) — DG/DDG SAT encodings that
  *preserve* treewidth/clique-width (covered in the anchor report §2.5).
- Fichte, Hecher & Meier, "A-Folio DPDB" — the ICCMA 2021 sub-track winner for **counting**
  Complete and Stable extensions. Secondary source (AAC-230013 ICCMA 2021/22 write-up): A-Folio
  DPDB is a *portfolio* — it measures the AF's treewidth and runs DPDB (a tree-decomposition DP
  on a relational DB engine) when treewidth < threshold, else falls back to µ-toksia for
  enumeration then counts. It is "the first ICCMA winner based on tree-width analysis of the
  instances" — but only in the *counting* track, not the standard enumeration/acceptance tracks.
- Fichte, Hecher & Meier, "Counting Complexity for Reasoning in Abstract Argumentation", JAIR
  (counting motivation).
- Dvořák, Hecher, König, Schidler, Szeider & Woltran, "Tractable Abstract Argumentation via
  Backdoor-Treewidth", AAAI 2022 (ojs.aaai.org/20501) — combines small backdoors with treewidth;
  still mostly a theory result.
- Hecher et al., "Taming High Treewidth with Abstraction, Nested DP, and Database Technology"
  (nestHDB) — handles treewidth up to ~266 by nested DP, but for #SAT, not argumentation directly.

**Status assessment.** On the *standard* ICCMA tracks (DC/DS/SE/EE for the admissibility
semantics) flat SAT (µ-toksia, fudge, crustabri) and ASP (ASPARTIX, pyglaf) still beat the
treewidth-DP solvers — the treewidth approach has only won the *counting* track via A-Folio
DPDB. Real ICCMA benchmark instances are *not* generated to have small treewidth; many
generated families (Barabási–Albert, Watts–Strogatz, Erdős–Rényi, grid, "stable-general") have
treewidth that grows with size, and the real-world-derived instances (planning, traffic) are
mixed. (See Mailly & Maratea, "Assessment of benchmarks for abstract argumentation", Argument
& Computation 2019, for the benchmark-structure analysis.) The planned-but-unimplemented
DG-encoding workstream in this repo (`notes/dg-treewidth-workstream-2026-05-01.md`,
`reports/workstream-dg-treewidth.md`) is a reasonable long-term bet *only* if the library's
users feed it structured/locally-constrained AFs.

**Cheap "if tw < k then DP else SAT" portfolio?** Marginal. Computing even a heuristic tree
decomposition (min-degree / min-fill) is cheap, but you then need a working DP *or* a
treewidth-preserving DG encoder to cash it in, and neither exists in the library yet. The
*cheap* part of this idea that *is* worth doing: compute a quick treewidth upper bound and, if
it's tiny (say ≤ 6), the AF is almost certainly also acyclic-ish / SCC-shallow and §1–§3 will
already crush it. So fold treewidth-detection into the §2 preprocessing as a *diagnostic*, not
as a portfolio switch, until a DP backend exists.

**How it'd slot in (when ready).** `dung.treewidth_upper_bound(framework)` via NetworkX's
`junction_tree` / min-fill heuristic; expose as instance metadata for the (future) portfolio
selector in `solver.py` / `backends.py`. Not a near-term win.

---

### 6. Anytime / approximation, caching, portfolio-by-graph-features — opportunistic

- **Anytime grounded / range approximation.** The library already has `approximate.py`
  (`approximate_grounded`, `approximate_semi_stable`, `k_stable_extensions`). ICCMA's
  Approximate Track is won by HARPER++ (Thimm — basically "return grounded as the approximate
  answer", remarkably effective) and AFGCN / AFGNN (graph-neural-net acceptability predictors,
  e.g. arXiv:2404.18672). Cheap win: make `approximate_grounded` the default fast-path answer
  for credulous queries and only escalate to SAT if grounded leaves the query UNDEC — this is
  essentially what HARPER++ does and it is one function call.
- **Caching grounded across related queries.** When answering many DC/DS queries on the same AF
  (or the dynamic-AF case in `dynamic.py`), compute the grounded extension and the §1 residual
  *once* and memoize on the framework identity. The dynamic track (ICCMA 2019+) rewards
  incremental recomputation — Greco & Parisi, "Incremental computation of abstract argumentation
  semantics", and the decomposition-based incremental approach (Springer AMAI, "Toward
  incremental computation of argumentation semantics: a decomposition-based approach") use SCC
  locality: only re-solve the SCCs touched by the update. The library's `dynamic.py` could reuse
  the §3 SCC machinery for this.
- **Portfolio selection by graph features.** Predictive-model solver selection exists (e.g.
  "Predictive models and abstract argumentation: the case of high-complexity semantics", KER) —
  feature vector = (#args, #attacks, density, #SCCs, max SCC size, treewidth bound, symmetry
  flag, acyclic flag) → pick SAT vs ASP vs DP. Premature for this library until there are ≥ 2
  competitive backends to choose between; but the *feature extraction* is exactly the §2/§5
  diagnostics, so it comes for free once those land.

---

## Summary table

| # | Technique | Key paper(s) | Impl cost | Expected practical win | Library gap |
|---|-----------|--------------|-----------|------------------------|-------------|
| 1 | Grounded-reduct preprocessing | µ-toksia (Niskanen & Järvisalo, KR 2020); folklore | tiny | large, reliable | encoders solve full AF, not residual |
| 2 | Cheap structural reductions (self-attack, acyclic, symmetric, kernels) | Coste-Marquis et al. ECSQARU 2005; Baumann ECAI 2014; Oikarinen & Woltran AIJ 2011 | tiny | large on easy/structured instances | kernels exist (`af_revision.py`) but not used pre-solve |
| 3 | SCC-recursive enumeration | Baroni-Giacomin-Guida AIJ 2005; Cerutti-Giacomin-Vallati arXiv:1310.4986; AAAI 2015 (parallel) | medium | large on layered/multi-SCC AFs | SCC code exists, used only for CF2/stage2 |
| 4 | ABA assumption-level / incremental | Lehtonen-Wallner-Järvisalo AAAI 2019, JAIR 2021, arXiv:2108.04192 | medium | large on structured inputs | support masks good; no well-founded fixing, no incremental loop |
| 5 | Treewidth DP / DG encodings / portfolio | Dvořák et al. AIJ 2012; Fichte et al. IJCAI 2021; A-Folio DPDB; AAAI 2022 backdoor-treewidth | high | small (counting only at ICCMA) | unimplemented workstream |
| 6 | Anytime grounded, query caching, GNN/portfolio | HARPER++ (Thimm); AFGCN (arXiv:2404.18672); incremental-AAMAI | tiny–medium | medium | `approximate.py` exists, not default fast-path |

**Recommended order of work:** 1 → 2 → (fold treewidth/feature *diagnostics* in here) → 4
(well-founded assumption fixing + keep ABA-preferred SAT solver alive) → 3 (full SCC-recursive
enumeration, reusing the CF2/stage2 skeleton) → 6 (HARPER++-style grounded fast-path) → 5
(only if benchmarks warrant).

---

## PDFs retrieved into `papers/`

- `papers/Cerutti_2014_SCC_SAT_PreferredExtensions.pdf` — arXiv:1310.4986, "Computing Preferred
  Extensions in Abstract Argumentation: a SAT-based Approach" (ArgSemSAT; SCC-recursive + SAT).
  NOTE: the downloaded PDF is password-protected (arXiv served an encrypted copy) — content not
  re-verified from the file; abstract-level claims only. Replace with the LNCS 8306 version if a
  clean copy is needed.
- `papers/Lehtonen_2021_IncrementalASP_ABA.pdf` — arXiv:2108.04192, "Harnessing Incremental
  Answer Set Solving for Reasoning in Assumption-Based Argumentation" (ASPforABA; 4-page version).

**Not retrieved (paywalled / binary):** Baroni-Giacomin-Guida AIJ 2005 (Elsevier, DOI
10.1016/j.artint.2005.05.006); Coste-Marquis et al. ECSQARU 2005 (Springer LNCS 3571, DOI
10.1007/11518655_28); Dvořák-Pichler-Woltran AIJ 2012 (DOI 10.1016/j.artint.2012.03.005);
ICCMA 2023 results paper (ScienceDirect S000437022500030X — HTTP 403); ASPARTIX-V21 is open at
arXiv:2109.03166 if wanted.

## Things I'm inferring rather than citing verbatim

- Exact speedup *multipliers* for SCC-recursive preferred (the primary PDF was unreadable;
  "significantly better in the large majority of cases" is the abstract's wording, not a number).
- That the library's SAT encoders solve the *full* AF rather than a residual — inferred from
  reading `af_sat.py` line numbers via grep, not from running the encoders; worth a quick check
  before building §1.
- ICCMA 2023 main-track winner identity (could not open the results PDF/page cleanly; fudge and
  crustabri were strong, ASPforABA won the ABA track — that last one is well-attested).
