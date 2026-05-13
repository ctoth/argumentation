# Wave B2 — SCC-recursive solving for complete / preferred / stable

Date: 2026-05-12. Branch: `experiment/graph-speedup-wave-a-preprocessing`.
Spec: `reports/scc-recursive-algorithm.md` (Baroni-Giacomin-Guida, AIJ 168, 2005, Def 20 / Thm 43).

## What was built

New module `src/argumentation/scc_recursive.py`:

- `scc_extensions(framework, semantics, *, decompose=True)` — enumerate
  complete / preferred / stable extensions via the SCC-recursive schema, composed
  under the Wave A grounded-reduct preprocessing. `decompose=False` opts out of
  *both* layers and calls the existing flat enumerator directly.
- `scc_credulously_accepted` / `scc_skeptically_accepted` — DC/DS for those three
  semantics, routed through full enumeration (spec UNRESOLVED #2 — query-driven
  pruning deferred; correct, not maximally clever, as the prompt allows).
- `LAST_SOLVE` — module-level telemetry on the most recent solve (semantics,
  residual size, residual SCC count, whether the flat fast path was taken, notes).

Pipeline (for complete/preferred/stable):

```
simplify_af(framework, semantics)        # Wave A grounded reduct -> residual + lift data
  -> SCC-decompose the residual
     -> if <= 1 SCC (incl. empty residual): flat base solve on the residual directly  [fast path]
     -> else: GF(residual, residual.arguments)  -- BG&G Def 20 recursion
  -> simplification.lift_all(residual_extensions)   # add the grounded part back
```

`GF(AF, C)`: if `|SCCS(AF)| <= 1` → base solve; else process SCCs in a topological
order of the condensation (own deterministic topo sort — `dung._strongly_connected_components`
re-sorts and loses Tarjan's reverse-topo order), and for each SCC `S` and each
partial extension `E` over ancestor SCCs compute `D(S,E)` / `U(S,E)` / `UP(S,E)`
per [BG&G05] Def 18, restrict to `UP(S,E)`, recurse `GF(AF↓UP(S,E), U(S,E) ∩ C)`,
cross-product the per-SCC partials. Preferred maximality is enforced per-SCC inside
the base function (`PE(AF,C)` = ⊆-maximal `CE(AF,C)`), exactly as Prop 41 requires —
no separate global maximality filter.

Base function `_base_solve(semantics, AF, C)`:

- If `C ⊇ AF.arguments` (the top-level call, and every recursive call that did not
  actually restrict membership) → delegate to the **existing flat enumerator**
  (`dung.complete_extensions` / `preferred_extensions` / `stable_extensions`). We do
  not reimplement the flat solver.
- Otherwise (genuine `C` restriction — only reachable at recursion depth ≥ 1, on a
  small disconnected sub-AF of a single SCC) → enumerate over the subsets of the
  sub-AF using `dung.admissible` / `dung.characteristic_fn`:
  - complete: `{E ⊆ C : E admissible in AF ∧ F_AF(E) ∩ C ⊆ E}` ([BG&G05] CE def).
  - preferred: ⊆-maximal elements of the above.
  - stable: `C` is provably inert ([BG&G05] p. 188, `SE(AF,C) = SE(AF)`) → flat
    enumerator again.

### Spec "UNRESOLVED" items — how resolved

1. **The `(AF, C)`-restricted base-solve encoding.** The spec floated threading a
   "force not-IN" constraint through the Z3 single-extension finders in `af_sat.py`.
   That does not work for *enumeration* (those finders return one witness, not a set)
   and the `require_out` knob they expose is "force OUT", which the spec itself flags
   as the wrong semantics. **Resolved by** enumerating the base case directly over the
   subsets of the sub-AF with the `dung` primitives — exact against the [BG&G05]
   definitions, and cheap because every sub-AF handed to the base solve is a single
   SCC of the post-preprocessing residual (small). Verified against the brute-force
   oracle on 580+ AFs (see Tests). This is the same finite-candidate enumeration
   `dung.complete_extensions` etc. already use, plus the `C` membership filter.
2. **Query-driven DC/DS pruning** ([Cer14] KR 2014, PDF not retrievable). **Deferred** —
   DC/DS go through full enumeration for this wave (correct). Follow-up gated on
   retrieving [Cer14] / cracking `papers/Cerutti_2014_SCC_SAT_PreferredExtensions.pdf`.
3. (Directionality classification of semi-stable/stage — not relevant here; those
   semantics were left untouched, per the spec and the hard stops.)

## Where it is wired (default ON, transparent)

- `src/argumentation/solver.py` — `_dung_extensions(...)` routes
  complete / preferred / stable through `scc_extensions(framework, semantics)`
  (the `backend="native"` enumeration path used by `solve_dung_extensions`,
  `solve_dung_single_extension`, `solve_dung_acceptance`). The old
  `complete_extensions`/`preferred_extensions`/`stable_extensions` branches are kept
  below as dead-but-defensive fallback.
- `src/argumentation/sat_encoding.py` — `sat_extensions(...)` routes
  complete / preferred / stable through `scc_extensions` (the `backend="sat"` path).

Callers (`solver.py`, the ICCMA CLI adapters that go through `solve_dung_*`) get
identical results — verified by the unchanged full test suite — just faster.

## How it composes with the `af_sat.py` kernel

It does *not* thread through the `AfSatKernel` incremental-solver design at all — the
SCC layer sits **outside** any kernel: it decomposes first, then the per-SCC base
solve is the existing flat enumerator (`dung.*_extensions`, which the SAT backend
already delegated to for complete/preferred). The Z3 incremental kernel in
`af_sat.py` is used only by the single-extension *finders* and the
preferred-skeptical CEGAR loop, which are untouched. This is the "put the SCC layer
outside the kernel" option the prompt offered, chosen because (a) the flat
enumeration path was never the Z3 kernel anyway, and (b) it keeps the change
contained and obviously sound.

## Tests — `tests/test_scc_recursive.py` (582 tests, all pass)

- **Oracle equivalence**, for complete/preferred/stable:
  - hand-built battery of 12 multi-SCC AFs: empty AF; size-1 SCC with/without
    self-loop; single 3-cycle; long grounding chain feeding a 2-cycle; two 2-cycles
    one feeding the other (residual = 2 SCCs); diamond condensation of 2-cycles;
    parallel independent SCCs; an SCC attacked by a fully-UNDEC upstream odd cycle
    (the `D`-set case); self-loop inside a larger SCC; mixed chain + self-loop sink +
    isolated arg; size-3 SCC feeding a size-1.
  - 180 random AFs of varied size (0–8 args) / density (0.1–0.45) / self-loops.
  - For each: assert `scc-path (decompose=True) == flat-path (decompose=False) ==
    brute-force `dung.*_extensions``, *and* DC/DS for a sampled argument agree.
- **Recursion-path-exercised**: 300 random AFs; ≥1 must trigger the SCC recursion
  (not the flat fast path) — confirmed via `LAST_SOLVE.flat_fast_path is False`.
  (Offline: 474/2400 (semantics × instance) hit the recursion in a 800-instance run.)
- **Fast-path behaviour**: single-SCC input, empty-residual input, and empty AF all
  take the flat path — asserted via `LAST_SOLVE` telemetry (not timing).
- **Opt-out**: `decompose=False` matches the brute-force oracle and reports the flat
  fast path.
- **Rejection**: `scc_extensions(af, "semi-stable" | "stage" | "grounded" | "ideal" |
  "admissible")` raises `ValueError`.

### Full suite

`python -m pytest --ignore=tests/test_datalog_grounding.py -q --tb=no`
→ **`1 failed, 1491 passed, 2 skipped`** (1491 = 909 Wave-A baseline + 582 new).
The 1 failure is the pre-existing `tests/test_solver_encoding.py::test_kernel_ideal_extension_is_admissible`
(documented in the Wave A report; unrelated, ideal semantics, untouched). No
regression. (Note: on this box's 32-bit Python, running the full suite *with*
tracebacks enabled triggers a `MemoryError` inside pytest's traceback renderer on an
unrelated huge-AF failure frame — a tooling artifact; `--tb=no` runs clean. Mention
for the next runner.)

## Before/after benchmark (`bench_scc_b2.py`)

Best-of-3 wall clock; `flat` = `decompose=False` (= the pre-Wave-B2 path), `scc` =
`decompose=True` (the new default). "EXCEEDED" = the flat path blew its
65536-subset exact-enumeration budget (`dung.complete_extensions` cap) — the SCC
path solves it anyway.

```
=== layered_cycles(4 layers x 3-cycle)  (|A|=12, |->|=15) ===
  EE-complete : flat=  78.13ms  scc=  0.27ms  speedup= 293x   (#ext=1)
  EE-preferred: flat=  77.33ms  scc=  0.28ms  speedup= 278x   (#ext=1)
  EE-stable   : flat=  77.52ms  scc=  0.17ms  speedup= 451x   (#ext=0)
  DS-PR(L0_0) : flat=  77.46ms  scc=  0.27ms  speedup= 283x

=== layered_cycles(3 layers x 4-cycle)  (|A|=12, |->|=14) ===
  EE-complete : flat=  76.54ms  scc=  1.52ms  speedup=  50x   (#ext=14)
  EE-preferred: flat=  77.11ms  scc=  1.18ms  speedup=  65x   (#ext=5)
  EE-stable   : flat=  76.52ms  scc=  1.18ms  speedup=  65x   (#ext=5)
  DS-PR(L0_0) : flat=  82.95ms  scc=  1.20ms  speedup=  69x

=== many_small_sccs(6 two-cycles, tree)  (|A|=12, |->|=17) ===
  EE-complete : flat= 105.52ms  scc=  8.14ms  speedup=  13x   (#ext=176)
  EE-preferred: flat= 106.76ms  scc=  2.49ms  speedup=  43x   (#ext=23)
  EE-stable   : flat= 104.92ms  scc=  2.67ms  speedup=  39x   (#ext=23)
  DS-PR(s0a)  : flat= 112.71ms  scc=  2.71ms  speedup=  42x

=== many_small_sccs(7 two-cycles, tree)  (|A|=14, |->|=20) ===
  EE-complete : flat= 496.49ms  scc= 21.11ms  speedup=  24x   (#ext=446)
  EE-preferred: flat= 502.75ms  scc=  4.76ms  speedup= 106x   (#ext=41)
  EE-stable   : flat= 485.86ms  scc=  4.69ms  speedup= 104x   (#ext=41)
  DS-PR(s0a)  : flat= 491.26ms  scc=  4.88ms  speedup= 101x

=== layered_cycles(6 layers x 3-cycle) [big]  (|A|=18, |->|=23) ===
  EE-complete : flat= EXCEEDED   scc=  0.37ms  speedup=  inf  (#ext=1)
  EE-preferred: flat= EXCEEDED   scc=  0.40ms  speedup=  inf  (#ext=1)
  EE-stable   : flat= EXCEEDED   scc=  0.20ms  speedup=  inf  (#ext=0)
  DS-PR(L0_0) : flat= EXCEEDED   scc=  0.38ms  speedup=  inf

=== many_small_sccs(15 two-cycles, tree) [big]  (|A|=30, |->|=44) ===
  EE-complete : flat= EXCEEDED   scc=20430.6ms speedup=  inf  (#ext=370557)
  EE-preferred: flat= EXCEEDED   scc= 280.99ms speedup=  inf  (#ext=2306)
  EE-stable   : flat= EXCEEDED   scc= 284.39ms speedup=  inf  (#ext=2306)
  DS-PR(s0a)  : flat= EXCEEDED   scc= 276.24ms speedup=  inf

=== giant_scc(13 nodes, density 0.15) [no-help control]  (|A|=13, |->|=45) ===
  EE-complete : flat= 284.79ms  scc=279.39ms  speedup= 1.02x  (#ext=3)
  EE-preferred: flat= 282.82ms  scc=279.70ms  speedup= 1.01x  (#ext=1)
  EE-stable   : flat= 292.25ms  scc=287.20ms  speedup= 1.02x  (#ext=1)
  DS-PR(g0)   : flat= 283.10ms  scc=280.67ms  speedup= 1.01x

=== giant_scc(14 nodes, density 0.10) [no-help control]  (|A|=14, |->|=31) ===
  EE-complete : flat= 492.98ms  scc=504.99ms  speedup= 0.98x  (#ext=4)
  EE-preferred: flat= 495.01ms  scc=505.73ms  speedup= 0.98x  (#ext=2)
  EE-stable   : flat= 497.42ms  scc=505.86ms  speedup= 0.98x  (#ext=2)
  DS-PR(g0)   : flat= 500.33ms  scc=498.02ms  speedup= 1.00x
```

Summary: 13×–450× on layered / many-small-SCC instances; the flat path can't even
finish the larger layered ones (SCC path: sub-millisecond–sub-second); the
single-giant-SCC **no-help control shows ≈0.98–1.02×** — within noise, no
regression, exactly the "free or a win" property the spec predicts (one Tarjan pass +
a `len(SCCS)==1` check, then straight to the flat path). (The `EE-complete` row of
`many_small_sccs(15)` at 20.4 s is just because that instance genuinely has 370 557
complete extensions — the per-SCC blow-up is intrinsic, not overhead; preferred /
stable / DS-PR on the same instance are ~0.28 s.)

ICCMA cap-100 corpus is not in the repo (established by Wave A); generated instances
used. `bench/instance_gen.py` only has ABA/ASPIC generators, so the AF generators
live in `bench_scc_b2.py`.

## pyright on touched files

```
$ python -m pyright src/argumentation/scc_recursive.py src/argumentation/solver.py \
                    src/argumentation/sat_encoding.py tests/test_scc_recursive.py
0 errors, 0 warnings, 0 informations
```

`ruff check` on the new/modified files: clean, except a **pre-existing** `F401`
(`argumentation.aba_sat.support_extensions` imported but unused) in `solver.py` that
predates this change (confirmed by `git stash` + re-check) and is outside the lines
touched — left alone.

## Files

- `src/argumentation/scc_recursive.py` (new)
- `src/argumentation/solver.py` (wired `_dung_extensions`)
- `src/argumentation/sat_encoding.py` (wired `sat_extensions`)
- `tests/test_scc_recursive.py` (new)
- `bench_scc_b2.py` (new — benchmark harness)
- `notes/graph-speedup-wave-b2-scc-impl.md`, `reports/graph-speedup-wave-b2-scc-impl.md`

## Notes for Wave C (ABA) / reviewers

- The SCC layer is **outside** any incremental Z3 kernel — Wave C can reuse the same
  "decompose AF → per-block flat solve" shape without fighting `AfSatKernel`.
- DC/DS query-driven pruning is the obvious next perf win (UNRESOLVED #2); needs the
  [Cer14] KR-2014 algorithm. Currently DC/DS = enumerate-then-check.
- Semi-stable / stage / ideal / grounded / admissible were **not** touched (they are
  not cleanly SCC-recursive per the spec). ABA / ASPIC paths untouched. Wave A
  preprocessing logic untouched (only composed with).
- `scc_extensions` is only valid for `{"complete","preferred","stable"}`; it raises
  `ValueError` otherwise — callers must dispatch on semantics first (they do).

## Commit

`<HASH>` — see below; filled in after `git commit`.
