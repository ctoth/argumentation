# Workstream — Decomposition-Guided Treewidth-Aware Encodings for `argumentation`

**Author:** subagent (research/design report)
**Date:** 2026-05-01
**Status:** design only; no implementation in this report
**Target codebase:** `C:/Users/Q/code/argumentation/` (Python library, currently flat-encoding SAT for AF/ABA)

---

## 1. Technical summary

### 1.1 The trick, restated

A naive Dung-AF-to-SAT encoding for stable extensions allocates one Boolean variable `e_a` per argument `a` and emits two clause families (Fichte et al. 2021, p. 3):

- **Conflict-freeness** `conf_R(E) := ⋀_{(a,b) ∈ R} (¬e_a ∨ ¬e_b)`
- **In-or-attacked** `inOrX_R(E) := ⋀_{a ∈ A} (e_a ∨ ⋁_{(b,a) ∈ R} e_b)`

The `inOrX` clause for an argument `a` mentions every variable `e_b` where `b` attacks `a`. In the **primal graph** of the resulting CNF (vertices = variables, edges = co-occurrence in a clause), this creates a clique on `{a} ∪ attackers(a)`. A single high-in-degree node therefore destroys treewidth: even if the original AF has bounded treewidth, the encoded formula's primal graph treewidth is at least `max_a |attackers(a)|`.

This matters because modern CDCL SAT solvers (and especially structure-aware tools like sharpSAT-TD) run in time `2^O(tw) · poly(s)` on instances of bounded primal-graph treewidth. Throwing away treewidth at encoding time forfeits that exponential speedup at solve time.

The decomposition-guided (DG) reduction of Fichte, Hecher, Mahmood, and Meier (IJCAI 2021) replaces the long disjunction `⋁_{(b,a) ∈ R} e_b` with a chain of auxiliary variables propagated along a tree decomposition `T = (T, χ)` of the AF's primal graph. Concretely (Fichte et al. 2021, formula (1), p. 4):

```
d^t_a ↔  ⋁_{t' ∈ children(t), a ∈ χ(t')} d^{t'}_a  ∨  ⋁_{(b,a) ∈ R_t} e_b
```

where `R_t` is the set of attacks on `a` whose source `b` lies in the bag `χ(t)`. The variable `d^t_a` reads "argument `a` has been observed defeated somewhere in the subtree rooted at `t`." Because each clause references only the variables in `χ(t)` plus the corresponding `d`-variables of `t`'s children, every clause sits inside a constant blow-up of one bag. Theorem 5 (p. 4) bounds this blow-up at `|χ'(t)| ≤ 5 · |χ(t)|` for the stable encoding.

The completion clause replaces `inOrX`:

```
e_a ∨ d^{last(a)}_a    for every a ∈ A         (Fichte 2021 formula (3), p. 4)
```

`last(a)` is the highest-up bag containing `a` in the TD; by the connectedness property of tree decompositions this is well-defined.

For admissible/complete the construction adds an analogous "never-attacking" variable `n_a` and propagates with an extra clause family (formulas (4)–(5), p. 4). For preferred / semi-stable / stage, an inequality witness `(ẽ, q_a, q^t)` is added that walks the same TD a second time, costing `2^O(k²) · poly(s)` rather than `2^O(k)` (Mahmood 2025, claim 4).

### 1.2 Bijective preservation → counting for free

Fichte 2021 formulas (6)–(7) (p. 4) and Mahmood 2025 claim 11 establish that the DG encoding's satisfying assignments stand in bijection with the AF's extensions. Once you have such a bijection, model counting on the SAT instance (sharpSAT-TD, Ganak, D4) directly counts extensions. No new encoding work is required. This is a substantial unlock: counting extensions under stable / admissible / complete is `#P`-complete and currently has no production-quality dedicated solver in `argumentation`.

### 1.3 Worked example — star `K_{1,4}` with one center attacked by four leaves

Take `A = {a, b1, b2, b3, b4}`, `R = {(b1, a), (b2, a), (b3, a), (b4, a)}`. The primal graph is a star with `a` at the centre and treewidth `1` (it is a tree).

**Naive encoding.** Variables `e_a, e_{b1}, …, e_{b4}`. The `inOrX` clause for `a` is `(e_a ∨ e_{b1} ∨ e_{b2} ∨ e_{b3} ∨ e_{b4})`. In the primal graph of the CNF this creates a 5-clique. **Primal treewidth becomes 4** even though the AF treewidth was 1.

**DG encoding.** Pick a path TD with bags `χ(t_1) = {a, b1}`, `χ(t_2) = {a, b2}`, `χ(t_3) = {a, b3}`, `χ(t_4) = {a, b4}` (each bag size 2, width 1). Walking up:

- `d^{t_1}_a ↔ e_{b1}`
- `d^{t_2}_a ↔ d^{t_1}_a ∨ e_{b2}`
- `d^{t_3}_a ↔ d^{t_2}_a ∨ e_{b3}`
- `d^{t_4}_a ↔ d^{t_3}_a ∨ e_{b4}`
- Completion: `e_a ∨ d^{t_4}_a`

Each clause sits over at most three variables (`{e_a, e_{b_i}, d^{t_i}_a}` or `{d^{t_{i-1}}_a, d^{t_i}_a, e_{b_i}}`). Primal treewidth of the CNF stays at `O(1)`. The number of variables grew by 4 (one `d` per bag mentioning `a`), but every clause is short and structurally aligned with the TD — exactly what a structure-aware SAT/MC solver wants. 

Generalising: an AF with an in-degree-`n` star uses naive encoding to produce a `(n+1)`-clique in the primal graph, while DG keeps it at `O(1)`. For a `2^O(tw)` solver the practical difference is exponential.

---

## 2. Evidence base

### 2.1 What the literature establishes

**Fichte et al. (IJCAI 2021)** — *Decomposition-Guided Reductions for Argumentation and Treewidth*:

- Defines DG reductions formally: a function taking an instance `I` and a TD `T` of its primal graph, returning a CNF/QBF whose primal-graph TD has width `O(width(T))` (notes p. 3).
- **Stable** encoding (formulas 1, 3): `|χ'(t)| ≤ 5·|χ(t)|` (Theorem 5, p. 4).
- **Admissible** encoding (formulas 4, 5): adds `n_a` "never-attacks-extension" variables.
- **Preferred / semi-stable / stage** (formulas 8–11): inequality variables `(ẽ, q_a, q^t)` propagated along TD; cost goes from `2^O(k)` to `2^O(k²)` (Table 1, p. 6) — for preferred it's actually `2^{2^O(k)}` in the QBF setting, dropping to `2^O(k²)` if you accept double-exp blow-up via Skolemisation (this is why iterative-SAT remains competitive in practice).
- **ETH lower bounds** (Theorem 6, p. 4): no reduction can do asymptotically better. The DG construction is essentially optimal.
- **Bijective preservation** (formulas 6–7, p. 4) → extension counting reduces to model counting.

**Mahmood et al. (AAAI 2025)** — *Structure-Aware Encodings of Argumentation Properties for Clique-width* (arXiv 2511.10767):

- Generalises DG from treewidth to **directed clique-width** (DDG reductions). Where treewidth blows up on dense graphs, clique-width can stay small.
- Claim 1: encoding follows a `k`-expression parse tree; each node adds `O(k)` clauses; satisfying assignments are bijective with extensions.
- Claim 2: stable extension encoding uses **`11k+2` colours** (variables) on top of the input `k`-expression. This is a real constant factor — significantly larger than treewidth's `5·|χ(t)|`.
- Claims 3–4: `2^O(k) · poly(s)` for stable/admissible/complete; `2^O(k²) · poly(s)` for preferred/semi-stable/stage.
- Claim 5: ETH-tight lower bounds match.
- Claim 11: bijective preservation again, so model counting works.
- **Claim 14 (limitation, verbatim from `claims.yaml`):** "The QBF encodings for preferred, semi-stable, and stage semantics, while theoretically optimal in structural complexity, have no experimental evaluation and may not outperform iterative SAT approaches (like CEGAR) in practice." Notes also flag: "Purely theoretical paper — no implementation or benchmarks provided."

**Dvořák, Pichler, Woltran (2012)** — FPT algorithms for abstract argumentation. The FPT baseline against which DG SAT-encodings compete: Dvořák gives direct dynamic-programming algorithms over tree decompositions (`2^O(k) · poly(n)` for stable, etc.); DG instead compiles to SAT and lets a generic solver realise the same bound. (Local copy: `propstore/papers/Dvorak_2012_…/paper.pdf`; only PDF and PNGs present locally — no extracted notes — so deeper page-level claims were not verified for this report.)

### 2.2 What the literature has *not* done

Two important gaps, taken seriously below:

1. **No published implementation of DG/DDG reductions for AFs.** Fichte 2021 §6 explicitly defers practical implementation to future work. Mahmood 2025 claim 14 is explicit: no experimental evaluation. ICCMA 2023 reports (Bistarelli et al. 2025) and the ICCMA 2025 preliminary report do not list any solver advertising DG-style encodings; winners use direct flat encodings plus CEGAR / iterative-SAT for maximisation tasks. The folklore conclusion in the community is that real ICCMA AFs are sparse but irregular — TD heuristics often find width 50+ — and so the asymptotic win does not visibly land. **This is the core risk of the workstream.**
2. **No published DG reduction for ABA.** Fichte 2021 §4 covers logic-based argumentation (ARG, ARG-Check, ARG-Rel of Besnard–Hunter), but not Bondarenko-style assumption-based argumentation. The natural primal graph for ABA is over assumptions with edges following minimal-support attack relationships, and the structure-preserving encoding for that has not been written down. **This is the novel contribution opportunity.**
3. **No benchmark instances purpose-built for low-tw AFs.** ICCMA instances are not curated by treewidth. There is no public AF benchmark family with controlled treewidth `k = 2, 4, 8, 16, 32, …`; demonstrating a DG win requires constructing such a family.

---

## 3. Workstream design

### 3.1 Existing entry points (verified by reading the source)

- `src/argumentation/sat_encoding.py` — `encode_stable_extensions()` produces the flat CNF; `sat_extensions(framework, semantics)` is the dispatch entry point that brute-force enumerates over satisfying assignments. The Z3-backed `sat_stable_extension()` exists as the "task-directed" path.
- `src/argumentation/aba_sat.py` — `_SupportState` precomputes minimal supports as bitmasks. `support_extensions()` and `support_acceptance()` brute-force over `2^|assumptions|` masks. The Z3 `sat_stable_extension()` here uses the flat in-or-attacked pattern over assumption support sets.
- `src/argumentation/dung.py` — `ArgumentationFramework` plus `_attackers_index()` (already builds reverse adjacency).
- `src/argumentation/probabilistic_treedecomp.py` — **already has `TreeDecomposition`, `NiceTDNode`, `NiceTreeDecomposition` dataclasses** (lines 51–89). Currently used by a grounded-DP backend that the file's own header acknowledges has zero asymptotic benefit. **This scaffolding is reusable.** No bag-walking generator that processes nodes in post-order is in place — that needs to be added.

The new module should sit alongside `sat_encoding.py` rather than replace it, so the flat encoder remains as a correctness oracle and a fast fallback for high-treewidth instances.

### 3.2 Phase plan

**Architectural posture (decisions 2026-05-01).**

- **Q3 (keyword dispatch, no Backend Protocol):** the existing
  `encoding="flat" | "dg"` kwarg routing pattern stays — no Protocol
  promotion in this workstream. Consistent with ASP and Datalog
  workstreams.
- **Q6 (model counting kept):** Phase 5 ships.
- **Q7 (ABA-DG kept):** Phase 3 ships, despite being novel-research
  with no published precedent and a real risk of failing on wide
  assumption-attack primal graphs.
- **Q8 (success bar (c)):** the workstream is not "done" until all
  six phases ship — DG encoding lands, equisatisfiable, opt-in;
  benchmark win on at least one realistic instance class; model
  counting works.
- **Q13 (pysat optional dep):** added in Phase 0.
- **Q14 (htd optional dep):** added in Phase 0.
- **Q15 (serial execution, runs third):** this workstream cannot
  begin until both ASP and Datalog workstreams ship.

#### Phase 0 — Tree-decomposition backend + optional dependency wiring (1–2 days)

**Deliverable:** `src/argumentation/treedecomp.py` exposing `compute_tree_decomposition(graph) -> TreeDecomposition` with at least one in-tree heuristic and a documented optional path to an external solver.

**Optional deps to register in `pyproject.toml` (decisions Q13, Q14):**

- `[project.optional-dependencies].treewidth = ["python-sat>=0.1.8"]`
  for CDCL via CaDiCaL/CryptoMiniSat (Phase 5 model counters need
  DIMACS, so we need at least one DIMACS-emitting path; Z3 stays
  for general-purpose use).
- **htd binary:** documented as a `$PATH` requirement, not a Python
  package. `treedecomp.py` detects it via `shutil.which("htd_main")`
  and falls back to NetworkX min-fill if missing.
- CI symmetric per decision Q2: install htd binary in CI alongside
  z3-solver and clingo so the htd path is exercised, not just
  documented.

**Options for the TD heuristic:**

- **NetworkX `treewidth_min_fill_in` / `treewidth_min_degree`** (already a transitive dep via probabilistic stack? — needs check). Pros: pure Python, zero new deps, well-tested. Cons: heuristic, no quality guarantees, slow on large graphs.
- **htd** (C++, MIT). Pros: best-in-class heuristics, used by ASP/SAT structure-aware research community. Cons: no maintained Python binding I could find — would need a thin subprocess wrapper that shells out to `htd_main` and parses the PACE `.td` output format.
- **FlowCutter** (C++, PACE 2017 winner for heuristic track). Same pros/cons as htd.
- **Jdrasil** (Java). Quality is good; JVM startup overhead is bad for short jobs.

**Recommendation, confirmed by decision Q14:** ship `treedecomp.py` with the NetworkX min-fill heuristic as the default, plus a `backend="htd"` path that subprocess-invokes htd if `htd_main` is on `$PATH` and parses `.td` output. The PACE `.td` format is small and well-specified. This keeps the library installable without C deps but lets a power user opt into a serious TD solver.

**Success criterion:** for the star example in §1.3, the heuristic returns width 1; for a dense ICCMA AF, the heuristic returns *some* TD without crashing, even if the width is poor. Plus: pysat is importable from the `[treewidth]` extra; `htd_main` is detected in CI.

**Risk:** TD heuristic quality variance is real. If `min_fill_in` returns a width-50 TD for a width-10 AF, the entire DG advantage evaporates. Mitigation: log the achieved width and fall back to flat encoding above a threshold (say, width > 25).

#### Phase 1 — Basic DG-stable encoder for AFs (3–5 days)

**Deliverable:** `src/argumentation/dg_encoding.py`:

- `nice_tree_decomposition(td: TreeDecomposition) -> NiceTreeDecomposition` (convert to introduce/forget/join form; the existing `NiceTDNode` dataclass already covers the shape).
- `encode_stable_dg(framework, td) -> CNFEncoding` implementing Fichte formulas (1) and (3). Reuse the existing `CNFEncoding` from `sat_encoding.py` — adopt the same variable-id convention so existing CNF consumers (DIMACS writers, model counters) work unchanged.
- A test in `tests/test_dg_encoding.py` that, for every AF in the existing test corpus with ≤ 6 arguments, verifies the set of stable extensions matches `sat_extensions(framework, "stable")`. **This equisatisfiability test is the only correctness gate that matters** for Phase 1.

**Files added:** `src/argumentation/treedecomp.py`, `src/argumentation/dg_encoding.py`, `tests/test_dg_encoding.py`.
**Files changed:** `src/argumentation/sat_encoding.py` — add `encoding="flat" | "dg"` kwarg routing on `sat_extensions`.

**Success criterion:** equisatisfiability holds on every AF the current test suite uses. CNF size and primal-graph width are recorded but not yet optimised.

**Risk:** off-by-one in the `last(a)` definition (which bag is the topmost containing `a`?). Mitigation: explicit unit tests on hand-constructed TDs.

#### Phase 2 — Admissible / complete / preferred (3–5 days)

**Deliverable:** extend `dg_encoding.py` with:

- `encode_admissible_dg` (Fichte formulas 4, 5)
- `encode_complete_dg` — combine admissible-DG with the standard complete-extension fixpoint clause (each defended argument must be in)
- `encode_preferred_dg_iterative` — keep the existing CEGAR-style "ask SAT for an admissible set, then ask for any strict superset, repeat" loop but use the DG admissible encoding inside. This sidesteps the QBF formulas (8)–(11) which are theoretically pretty but produce 2-QBFs no in-tree solver handles. **This is the right pragmatic choice: Mahmood claim 14 explicitly hedges that QBF preferred encodings may lose to iterative SAT in practice.**

**Files changed:** `dg_encoding.py`; `sat_encoding.py` to route `semantics="preferred"` through the iterative DG path when `encoding="dg"`.

**Success criterion:** equisatisfiability against the existing `preferred_extensions` enumerator on small AFs.

**Risk:** the iterative loop reuses the underlying solver across calls. Need to confirm Z3 incremental mode preserves the DG variable layout, or switch to feeding DIMACS to an external CDCL solver (CaDiCaL via `pysat`).

#### Phase 3 — DG encoding for ABA (5–8 days, novel work)

**Deliverable:** `src/argumentation/aba_dg.py`:

- Build the **assumption-attack graph** of an ABA framework: nodes are assumptions; an edge `α → β` exists iff some minimal support set for the contrary of `β` contains `α`. This is the natural primal graph for the `aba_sat.py`-style flat encoding's `_any_support_selected` clause.
- Compute a TD on this graph.
- Replace the long `_any_support_selected(z3, variables, attack_supports[α])` clause (currently O(|supports|) variables in one clause) with a DG-style auxiliary chain: `d^t_α ↔ ⋁ children ∨ ⋁ supports-fully-in-bag(t)`. The subtlety: a single attack-support may contain multiple assumptions, so the encoding needs an auxiliary `s_S` per support set indicating "all of `S` is in the extension," with `s_S = ⋀_{α∈S} e_α`. This Tseitin step is straightforward but new — it has no published treatment, so the workstream should record the reduction explicitly in a docstring with a small worked example.

**Files added:** `src/argumentation/aba_dg.py`, `tests/test_aba_dg.py`.
**Files changed:** `aba_sat.py` to route to `aba_dg` when an `encoding="dg"` flag is set.

**Success criterion:** equisatisfiability against `support_extensions` on the existing ABA test corpus for stable, admissible, complete, preferred.

**Risk:** the extra `s_S` Tseitin variables themselves create wide clauses (one per support, each as wide as the support). If any single support has many assumptions, the trick partially breaks down. Need to inspect what support widths actually arise on benchmark ABA instances. **This is a real research question and should be flagged to Q before phase 3 begins.**

#### Phase 4 — Benchmarking harness (3–5 days base + 2–4 days for external systems per Q12)

**Deliverable:** `bench/dg_vs_flat.py`:

- Pull existing ICCMA AF instances (already present? check `iccma.py` — currently a parser/CLI). Otherwise download a small representative slice.
- Synthesise a low-treewidth AF family: tree-shaped attack graphs of width 2, 4, 8, 16; grid AFs of width 4×n; balanced binary trees with extra random attacks across siblings.
- For each instance: time flat-CNF + Z3, DG-CNF + Z3, DG-CNF + external CDCL (CaDiCaL), record solve time, encoding time, CNF size, primal-graph treewidth.
- Output a CSV plus a summary plot.

**External-systems sub-phase (decision Q12, 2026-05-01).** Required,
not stretch. Install and calibrate the comparison set:

- **μ-toksia** (ICCMA 2019/2023 winner, the canonical SAT-based AF
  baseline that DG would have to beat to claim a real win)
- **fudge, pyglaf, crustabri** (other recent ICCMA finalists)
- **Mahmood reference implementation** if accessible (clique-width
  encoder)
- Document install instructions, version numbers, and any patching
  in `bench/README.md` for reproducibility
- Windows install caveat applies: external systems may need WSL or
  container fallback; CI runs only the base DG-vs-flat comparison,
  external columns stay manual.

**Success criterion:**

- (base) on the synthetic low-treewidth family, DG dominates flat
  for treewidth ≤ 8 and argument count ≥ 50.
- (external) on at least one realistic instance class (synthetic
  low-tw or selected ICCMA subset), DG-CNF + CaDiCaL beats μ-toksia
  on solve time. **This is the decision-Q8(c) success bar — the
  workstream is not "done" without this evidence.**
- Document where DG wins, ties, or loses without spinning the result.

**Risk:** the honest expected result is "DG ties or loses on real
ICCMA instances and only wins on the synthetic family." Decision
Q8 chose success bar (c) anyway, accepting this as the worst-case
outcome — the synthetic-family win is the floor we ship. If even
the synthetic-family win fails to materialise, that is an
unambiguous workstream failure to report honestly to Q.

#### Phase 5 — Model counting backend (3–5 days)

**Deliverable:** `src/argumentation/dg_counting.py`:

- Add formulas (6)–(7) (Fichte) to the DG-admissible encoding to enforce bijective preservation.
- Subprocess wrapper around `sharpSAT-td` (or Ganak) reading DIMACS, returning model count.
- New public function `count_extensions(framework, semantics, *, backend="sharpsat-td")`.

**Files added:** `dg_counting.py`, `tests/test_dg_counting.py`.

**Success criterion:** for AFs where brute-force enumeration is feasible (≤ 16 arguments), counts match. For larger instances, the count returns in reasonable time on the synthetic low-treewidth family.

**Risk:** sharpSAT-TD's input is reasonably standard DIMACS but its preprocessor sometimes mangles variable IDs; need to either disable preprocessing or map back through its variable witness. Ganak is a safer bet API-wise but generally slightly slower.

### 3.3 Total effort estimate

Roughly **20–34 person-days** for phases 0–5 with the
external-systems sub-phase from decision Q12 included. Phases 0–2
are the safe/expected-win path (~7–12 days); phase 3 is the
novel/risky path (~5–8 days, kept per decision Q7); phases 4–5 are
the demonstration/payoff path (~8–14 days including external
systems).

This workstream **runs third** in the serial sequence per decision
Q15 (ASP → Datalog → DG). It cannot begin until both prior
workstreams ship.

---

## 4. Risks and unknowns

### 4.1 The ICCMA reality

ICCMA winners (μ-toksia, fudge, pyglaf, crustabri) all use direct flat encodings + CEGAR for maximisation. The community has not adopted DG. Two candidate explanations:

- **Charitable reading:** nobody has tried hard enough; the asymptotic theory is right and an engineering effort would land it.
- **Cynical reading:** real ICCMA instances have treewidth in the 50–200 range, the constants in `2^O(tw)` are not generous, and CDCL on flat encodings exploits VSIG / clause learning enough that the structural advantage doesn't materialise.

**No web-search evidence I could surface confirms either reading.** No ICCMA write-up I found (2023 design paper, 2025 preliminary report) explicitly benchmarks DG vs flat encodings. This is the load-bearing risk.

### 4.2 TD heuristic quality

`networkx.algorithms.approximation.treewidth_min_fill_in` is fine for small/structured graphs and embarrassing for large irregular graphs. For any serious benchmarking the workstream needs htd or FlowCutter, which means C++ subprocess wiring. Engineering time spent on TD quality directly determines whether the rest of the work shows a win.

### 4.3 Mahmood clique-width vs Fichte treewidth

Mahmood's `11k+2` constant is large. The crossover where clique-width-`k` beats treewidth-`k'` requires `k' / k > 11 / 5 ≈ 2.2` and the constants in the SAT solver's `2^O(·)` to behave. For sparse AFs treewidth is the right pick. For AFs with many high-degree hubs (e.g., AFs derived from logic programs with shared atoms) clique-width could win — but this is speculation until measured. **Phase plan above does Fichte first; Mahmood's clique-width encoding is a Phase 6+ that I have not scoped.**

### 4.4 Python overhead

The DG construction itself is `O(|TD| · max_bag_size · |R|)`. For a 10k-argument AF with width 30 this is on the order of millions of clauses — still fine in Python, but DIMACS serialisation in pure Python is slow. Will need to profile and possibly write the DIMACS emitter with `bytearray` accumulation.

### 4.5 Bijective preservation gotcha

The bijection in Fichte (6)–(7) requires the auxiliary `n_a` and `d_a` variables to be **functionally determined** by `e_a`. If a downstream change introduces an under-constrained auxiliary, model counts double. The counting tests must include hand-checked small instances, not just self-consistency checks.

---

## 5. Decisions (resolved 2026-05-01)

All five gating decisions resolved. Restated here as the canonical
record:

1. **Model counting (Phase 5)?** → **Yes.** Bijective-preservation
   extra clauses (Fichte (6)–(7)) ship; Phase 5 in scope. Justified
   by counting use-cases in probabilistic argumentation and
   enumeration-with-bound queries.
2. **External TD-solver dependency (htd)?** → **Add as optional
   dep.** NetworkX default for portability; htd via
   `$PATH` + `shutil.which("htd_main")` detection. CI installs htd
   binary so the path is exercised.
3. **External SAT backend (pysat)?** → **Add pysat as optional
   dep** under `[treewidth]` extra. Required for Phase 5 (model
   counters consume DIMACS). Z3 stays for general-purpose use; pysat
   wraps CaDiCaL/CryptoMiniSat for DIMACS workloads.
4. **Phase 3 (ABA-DG, novel research)?** → **Keep.** Q accepted the
   risk that the natural ABA primal graph may give wide TDs
   (minimal supports overlap → DG advantage evaporates). If Phase 3
   fails, document the negative result honestly rather than
   retrofitting.
5. **Success bar?** → **(c)** — DG encoding lands, equisatisfiable,
   opt-in (Phases 0–2) + benchmark win on at least one realistic
   instance class (Phase 4) + model counting works (Phase 5). Phase
   3 (ABA-DG) is in addition to (c), not part of it. The honest
   expected outcome of the ICCMA benchmark is "no clear win on
   real instances; win on synthetic low-tw family"; this is the
   floor we ship and call success.

Cross-workstream decisions also affecting this workstream:

- **Q3 (keyword dispatch, no Backend Protocol):** existing
  `encoding="flat" | "dg"` kwarg routing pattern stays. Consistent
  with ASP and Datalog workstreams.
- **Q12 (include external benchmarks):** Phase 4 expands by 2-4
  days to install and calibrate μ-toksia, fudge, pyglaf, crustabri,
  and the Mahmood reference if accessible. The ICCMA SAT-based
  baselines are the only honest opponents for a DG advantage claim.
- **Q15 (serial execution).** This workstream runs **third**, after
  ASP and Datalog ship. Earliest start: ~5-8 weeks out depending on
  upstream workstream slip.

---

## Sources

- [Decomposition-Guided Reductions for Argumentation and Treewidth (Fichte et al., IJCAI 2021)](https://www.ijcai.org/proceedings/2021/0259.pdf)
- [Structure-Aware Encodings of Argumentation Properties for Clique-width (Mahmood et al., AAAI 2025 / arXiv 2511.10767)](https://arxiv.org/abs/2511.10767)
- [PACE-challenge/Treewidth — list of solvers, instances, tools](https://github.com/PACE-challenge/Treewidth)
- [htd — C++ tree decomposition library (mabseher)](https://github.com/mabseher/htd)
- [Jdrasil — Java tree decomposition library (maxbannach)](https://github.com/maxbannach/Jdrasil)
- [FlowCutter — PACE 2017 heuristic submission (Hamann & Strasser)](https://arxiv.org/abs/1709.08949)
- [NetworkX `treewidth_min_fill_in` documentation](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.approximation.treewidth.treewidth_min_fill_in.html)
- [SharpSAT-TD in Model Counting Competitions 2021–2023 (Korhonen)](https://arxiv.org/pdf/2308.15819)
- [GANAK: A Scalable Probabilistic Exact Model Counter (IJCAI 2019)](https://www.ijcai.org/proceedings/2019/0163.pdf)
- [ICCMA 2023 design and analysis (Bistarelli et al., 2025)](https://www.sciencedirect.com/science/article/pii/S000437022500030X)
- [ICCMA 2025 competition site](https://www.argumentationcompetition.org/2025/index.html)
- Local: `C:/Users/Q/code/propstore/papers/Fichte_2021_Decomposition-GuidedReductionsArgumentationTreewidth/notes.md`
- Local: `C:/Users/Q/code/propstore/papers/Mahmood_2025_Structure-AwareEncodingsArgumentationProperties/claims.yaml`
- Local: `C:/Users/Q/code/propstore/papers/Dvorak_2012_FixedParameterTractableAlgorithmsAbstractArgumentation/paper.pdf` (no extracted notes)
