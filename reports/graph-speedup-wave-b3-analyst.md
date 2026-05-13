# Wave B3 — Adversarial correctness review of `scc_recursive.py`

Date: 2026-05-12. Analyst subagent. Read-only on source; ran tests/benchmarks/oracle batteries.
Branch `experiment/graph-speedup-wave-a-preprocessing`, HEAD `b882a25` atop `cebb9a9`.

## Verdict: **SOUND** — ship it, proceed to Wave C.

No oracle disagreement found in any handcrafted adversarial AF or in ~1200 random AFs across the
three semantics. Spec conformance is faithful. Suite and pyright are clean modulo the documented
pre-existing failure. The only items below are minor cleanup, not correctness blockers.

## Spec-conformance findings

Checked `src/argumentation/scc_recursive.py` against `reports/scc-recursive-algorithm.md`
([BG&G05] Def 18/20, Thm 43).

- **Recursion shape (`_gf`, lines 224-268)** matches Def 20: `len(sccs) <= 1` → base solve;
  otherwise process SCCs in a topological order of the condensation, threading partial `E` over
  ancestor SCCs, cross-producting per-SCC results. Correct.
- **`D(S,E)` (lines 248-252)**: `{a ∈ S | ∃ b ∈ (E ∩ outparents(S)) : b → a}` — `e_out = e & outparents`,
  `any((b,a) in af.defeats for b in e_out)`. Matches Def 18.
- **`UP(S,E) = S \ D(S,E)` (line 253)**. Matches.
- **`U(S,E)` (lines 254-262)**: requires `a` not attacked from outside by `E` *and* every external
  attacker `b ∈ (outparents ∩ parents(a))` is attacked by `E` (`any((d,b) in af.defeats for d in e)`,
  using the *full* partial `e`, which is correct — `E → β` is over all of `E`). Matches Def 18.
  `P(S,E) = UP \ U` is implicit (`sub_c = u_set & c`), as the spec pseudocode notes.
- **`subAF = AF↓UP(S,E)`, `subC = U(S,E) ∩ C` (lines 263-264)**: matches the `C' = U(S,E) ∩ C`
  threading in Def 20. Top level passes `C = residual.arguments` (line 325). Correct.
- **Base function (`_base_solve`, lines 159-176)**:
  - `c >= af.arguments` (membership unrestricted) → plain flat enumerator `complete/preferred/stable_extensions`.
    This is the top-level call and any sub-AF reached with `C` = its whole arg-set. Correct collapse.
  - complete in C (`_base_complete_in_c`, lines 110-132): candidate `⊆ C`, admissible *in the full
    sub-AF*, and `F_AF(E) ∩ C ⊆ E`. This is exactly `CE(AF,C)` from [BG&G05] Def 23, and crucially
    it does **not** restrict the sub-AF to `C` (defense checked in the full sub-AF) — the spec's
    "subtle, do not skip" point on p. 184 is honored: `admissible(candidate, af.arguments, af.defeats,...)`
    and `characteristic_fn(candidate, af.arguments, af.defeats,...)` both use the *whole* sub-AF.
  - preferred in C (`_base_preferred_in_c`, lines 135-139): ⊆-maximal elements of `CE(AF,C)` =
    `PE(AF,C)` ([BG&G05] Prop 31). Maximality is enforced *per restricted sub-AF*, not
    globally-then-projected — matches the "one place to be careful" in §2.3.
  - stable: `C` provably inert ([BG&G05] p. 188) → flat `stable_extensions`. Correct, and an SCC
    sub-AF with no stable extension (odd cycle, self-loop sink) returns `[]`, killing that branch —
    matches `dung.stable_extensions` returning `[]`. Verified by handcrafted cases.
  - The spec's UNRESOLVED #1 ("force not-IN, not OUT" SAT encoding) is sidestepped entirely by
    direct subset enumeration over the (small, post-preprocessing) single-SCC sub-AFs. This is
    sound by construction (`candidate <= c` is literally `E ⊆ C`) and verified against the brute
    oracle. Reasonable resolution.
- **Topological order (`_topological_scc_order`, lines 184-216)**: builds the condensation DAG from
  `defeats`, Kahn's algorithm, deterministic tie-break by sorted member tuple. Parents before
  children — correct (Def 20 needs ancestor SCCs processed first). The `len(result) != len(sccs)`
  guard would catch a non-DAG (impossible by construction). Note: `_strongly_connected_components`
  is recursive Tarjan and re-sorts SCCs (destroying Tarjan's reverse-topo emission order), so
  recomputing the topo order here is the right call — exactly as the spec §4 warns.
- **Edge cases — all verified by handcrafted AFs (results equal brute oracle for all 3 semantics):**
  empty AF; single self-attacking arg as whole SCC; self-loop feeding another node; self-loop
  *inside* a larger SCC; odd 3-cycle; even 4-cycle; whole AF one SCC (equals flat); chain of cycles;
  parallel source SCCs; deep nested condensation (3 cycles in a chain); acyclic chain (preprocessing
  solves everything → empty residual); source node feeding a cycle; SCC attacked only by an UNDEC
  upstream 2-cycle.
- **Soundness gating**: `SCC_RECURSIVE_SEMANTICS = {complete, preferred, stable}` (line 68);
  `scc_extensions` raises `ValueError` for anything else (lines 293-296). `solver.py:984` and
  `sat_encoding.py:136-138` route only complete/preferred/stable through `scc_extensions`;
  semi-stable, stage, ideal, grounded, admissible keep their flat paths (`solver.py:990+`,
  `sat_encoding.py:139+`). `grounded` is handled separately before the SCC dispatch in both. Correct.
- **Preprocessing composition**: `scc_extensions` calls `simplify_af(framework, semantics=semantics)`
  first (line 307), SCC-decomposes the *residual* (line 311), and `simplification.lift_all(...)` at
  the end (line 327). If the residual has ≤1 SCC it skips the recursion machinery and base-solves
  the residual directly (lines 314-321) — zero SCC-layer overhead. Order is exactly the spec §3
  prescription: simplify → decompose residual → base-solve per SCC → lift per-SCC → lift `G` back.
- **`decompose=False`** (lines 302-305): bypasses *both* preprocessing and the SCC layer, calling
  `_base_solve(semantics, framework, framework.arguments)` → since `C` = all args, this is
  `_flat_enumerate` = the plain `dung.*_extensions`. Verified identical to the SCC path and to the
  brute oracle on every test AF. Real opt-out.

## Oracle comparisons run

- **Handcrafted adversarial battery** (13 AFs listed above × {complete, preferred, stable}):
  `set(scc_extensions(af, sem)) == set(dung.<sem>_extensions(af))` AND
  `set(scc_extensions(af, sem, decompose=False)) == ...` — **0 mismatches**.
- **Random battery #1**: 800 trials, n ∈ [1,12], density ∈ {0.1,0.15,0.2,0.3,0.4}, all 3 semantics,
  scc vs flat vs brute — **0 mismatches, 0 exceptions**.
- **Random battery #2**: 400 trials, n ∈ [8,14], density ∈ {0.08,0.12,0.18}, all 3 semantics,
  scc vs brute — **0 mismatches**. The SCC recursion path (`LAST_SOLVE.flat_fast_path is False`)
  was actually exercised 545 times across these trials, so the decomposition machinery is genuinely
  being tested, not just the fast-path fall-through.

No oracle disagreement anywhere. No P0.

## Suite + pyright

- `python -m pytest -q --ignore=tests/test_datalog_grounding.py --tb=no`:
  **1 failed, 1491 passed, 2 skipped** in ~77s. The single failure is
  `tests/test_solver_encoding.py::test_kernel_ideal_extension_is_admissible` — the documented
  pre-existing failure, unrelated to this wave. Nothing else fails.
- `pyright src/argumentation/scc_recursive.py src/argumentation/solver.py src/argumentation/sat_encoding.py tests/test_scc_recursive.py`:
  **0 errors, 0 warnings, 0 informations.** (The new-diagnostics noise reported during the coder's
  run is gone in the committed state — clean.)

## Performance sanity (spot-check, direction only)

- Layered AF (20 chained 3-cycles, 60 args): `scc_extensions(..., 'preferred')` ≈ 0.001s, residual
  has 20 SCCs, recursion path used. The flat path can't even run it (`ExactEnumerationExceeded` at
  60 args / 65536 candidates) — so the SCC layer is a categorical enabler here, not just a constant-factor.
- Single giant SCC (12-node dense strongly-connected, density ~0.3): scc ≈ 0.135s vs flat ≈ 0.136s,
  results identical, `flat_fast_path = True`. ≈1.0×, no regression.

Direction confirmed; no pathological slowdown observed.

## Minor cleanup items (NOT correctness issues)

1. **`bench_scc_b2.py` committed at the repo root** (added in `cebb9a9`, 126 lines). Root-level
   bench-script clutter; consider moving to a `benchmarks/` dir or dropping it. Not a blocker.
2. **`_flat_enumerate` / base solve inherits the flat enumerator's `ExactEnumerationExceeded` cap.**
   If the *residual* is a single SCC larger than ~16 args, `scc_extensions` will raise rather than
   fall back to the iterated-SAT solver in `af_sat.py`. This is pre-existing behavior of the brute
   enumerator (not introduced by Wave B2), and the SCC layer's whole point is to shrink the per-SCC
   sub-AF below that cap — but worth noting as a Wave C consideration: a giant residual SCC is
   exactly the "when it hurts" case from spec §5, and right now it hard-errors instead of degrading
   to SAT. Flag for Wave C, not a B2 defect.
3. **Recursive Tarjan + recursive `_gf`**: deep condensations (long chains of SCCs) recurse in
   Python; the spec §4 already flagged this. Post-preprocessing residuals are typically shallow, and
   the 20-deep chain above worked fine, but a pathological 1000-deep chain would hit the recursion
   limit. Low priority.

## Bottom line

The implementation is a faithful, well-documented realization of [BG&G05] Def 20 / Thm 43, correctly
composed under the Wave A grounded-reduct preprocessing, correctly gated to complete/preferred/stable
only, with a real `decompose=False` opt-out. Every oracle comparison I could throw at it passed.
**SOUND.** Proceed to Wave C; carry items 1-2 forward as cleanup/scoping notes.
