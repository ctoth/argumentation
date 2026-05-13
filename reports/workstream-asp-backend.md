# Workstream: ASP (Clingo) backend for preferential ABA / ABA+ and preferential ASPIC+

Author: Claude Opus 4.7 (1M) — researcher role
Date: 2026-05-01
Scope: Design only. No implementation. Files inspected read-only.

---

## 1. Technical summary — the Lehtonen trick, restated

Structured argumentation frameworks (ASPIC+, ABA) have two natural levels.
At the **source level** they are a finite collection of typed objects:
ordinary premises `K_p`, axiom premises `K_a`, strict rules `R_s`,
defeasible rules `R_d`, a contrariness function, and (for the preferential
variants) a preorder over `R_d` and `K_p`. At the **abstract level** one
materialises Dung-style arguments, computes attacks/defeats, and runs an
abstract-AF semantics.

The reduction `theory -> abstract AF` is what blows up. A defeasible rule
`r` may participate in many distinct arguments depending on how its body
is supported, and the recursive sub-argument structure means an
ASPIC+ theory of polynomial size in `(|R|, |K|)` can yield up to
`O(2^|R_d| * 2^|K_p|)` syntactically distinct arguments. The current
codebase materialises that AF in `aspic.build_arguments` (see
`src/argumentation/aspic.py:682-776`) and then runs SAT-with-iteration
or brute enumeration on the resulting Dung graph.

Lehtonen, Wallner and Järvisalo's reformulation (2020) is to **never
construct that AF**. They prove (Theorem 5 of the 2020 paper) that for
each abstract semantics `sigma in {adm, com, prf, stb}`, the
`sigma`-extensions of the AF biject with `sigma`-assumptions of the
underlying argumentation theory `T`, where a `sigma`-assumption is a
*pair* `(P, D)` with `P ⊆ K_p` and `D ⊆ R_d`. The search space is
therefore bounded by `2^|K_p| * 2^|R_d|` directly in the source — never
exponentiated by argument trees. Reasoning becomes:

1. Guess `(P, D)`.
2. Compute `Th_T(P, D)` = forward closure of `P ∪ K_a` under `D ∪ R_s`.
3. Compute `att(P, D)` = `{x ∈ K_p ∪ R_d | x̄ ∩ Th_T(P, D) ≠ ∅}`.
4. Check the semantics-specific constraint
   (conflict-freeness, defense, completeness, stability, ⊑-maximality).

Lehtonen 2024 lifts this to preferential ASPIC+ under both elitist and
democratic last-link liftings (Theorem 16): the complexity stays exactly
where Dvořák and Dunne 2012 placed abstract-AF reasoning — `NP` for
credulous, `coNP` for skeptical complete/stable, `Π₂ᴾ` for skeptical
preferred. Crucially, this is the same complexity *without* preferences:
last-link does not raise it. (Weakest-link does — Proposition 17 makes
grounded NP-hard.)

### ASP encoding pattern (Lehtonen 2020, Listings 1-4)

```
% Γ_guess
{ sel(X) : ordinary(X) }.
{ sel(X) : defeasible(X) }.

% Δ_der  — saturated forward derivation
deriv(X)        :- axiom(X).
deriv(X)        :- ordinary(X), sel(X).
deriv(head(R))  :- defeasible(R), sel(R), deriv(B) for each B in body(R).
deriv(head(R))  :- strict(R),               deriv(B) for each B in body(R).

% Δ_adm  — attack, conflict-free, defense
attacked(X) :- ordinary(X)|defeasible(X), contrary(C, X), deriv(C).
:- sel(X), attacked(X).                      % conflict-free
:- sel(X), defending_chain_broken(X).        % defense

% Δ_sem(σ)
% complete:  sel(X) :- ordinary(X),    not attacked(X).
%            sel(R) :- defeasible(R),  applicable(R), not attacked(R).
% stable:    :- ordinary(X),    not sel(X), not attacked(X).
% preferred: saturation block_cand(...) and { not not sel(X) ... }.
```

The output projection (`#show accepted_arg/1`, `#show accepted_lit/1` in
the project's protocol) marks a chosen extension. Clingo's stable-model
semantics handles the "guess and verify" structure natively via the
choice rules in `Γ_guess`; saturation handles the `Π₂ᴾ` skeptical
preferred query without an explicit subsolver iteration.

### Worked example (3 rules, 2 defeasible elements)

Argumentation theory `T`:

```
K_p = { p, q }      (ordinary premises)
K_a = { }           (no axioms)
R_s = { s1: a -> b }
R_d = { d1: p => a,
        d2: q => ~p }   (name(d1)=n1, name(d2)=n2)
contraries: ~p of p
```

Argument-enumeration view: build `[p]`, `[q]`, `[p ⇒ a]`,
`[[p ⇒ a] -> b]`, `[q ⇒ ~p]`, four arguments + their attacks. With this
toy size that is fine; with `|R_d|=15` and a branching strict rule it is
not.

`σ`-assumption view: search over `(P, D)` with `P ⊆ {p, q}`,
`D ⊆ {d1, d2}` — sixteen candidates total. For `(P, D) = ({p, q}, {d2})`:
`Th_T = {p, q, ~p}`, so `att = {p}` (since `~p` is derived and `~p ∈ p̄`).
Because `p ∈ P ∩ att`, this `(P, D)` is *not* conflict-free. The encoding
prunes it via `:- sel(X), attacked(X)`. For `(P, D) = ({q}, {d2})`:
`Th_T = {q, ~p}`, `att = {p}`, `p ∉ P ∪ D` — conflict-free, admissible,
and (with no surviving alternative larger than it) a stable assumption.
Clingo finds this directly without ever instantiating an argument tree.

### Why SAT-with-iteration loses

For preferred (`Π₂ᴾ`) semantics SAT requires nested CEGAR loops: an
outer "guess admissible" plus an inner "no strict superset is
admissible" call. Each loop can instantiate `O(2^|args|)` blocking
clauses. ASP's saturation pattern compiles the inner `coNP` check into
the same answer-set search. The asymptotic gain comes from sharing the
grounding between the outer and inner search; the empirical 30× scale
reported in Lehtonen 2024 (1500-1900 atoms vs 50-80 for PyArg) is the
visible cost of that sharing being absent in argument-enumeration plus
SAT.

---

## 2. Evidence base

Sources read for this design:

- `propstore/papers/Lehtonen_2020_AnswerSetProgrammingApproach/notes.md`
  — Listings 1-4, Theorem 5, σ-Assumptions section, complexity table.
- `propstore/papers/Lehtonen_2024_PreferentialASPIC/notes.md` —
  Theorem 16, last-link rephrasing, scale numbers, II_common /
  II_ELI / II_DEM module split, Proposition 17 (weakest-link grounded
  NP-hard).
- `propstore/papers/Bondarenko_1997...` — directory not present in the
  local collection; the structured-to-AF translation it inaugurates is
  the *thing the ASP encoding avoids* and is referenced conceptually
  rather than quoted.
- `propstore/papers/Lehtonen_2017_Reasoning...` — not present locally.
  The referenced predecessor is Lehtonen, Wallner, Järvisalo 2019 (ASP
  for ABA), cited in the 2020 notes' "Related Work" block.

### Quoted scale and complexity facts

Scale (Lehtonen 2024):
- ASPforASPIC: solves benchmarks up to **1900 atoms (elitist)** and
  **1500 atoms (democratic)** within 600s on Clingo 5.7.1, 32 GB.
- PyArg: stalls around **50-80 atoms** on the same generators.
- Lehtonen 2020 (no preferences): up to **N=3000 atoms** at 15 axioms,
  300s timeout, Clingo 4.5.0, "majority of instances solved" for all
  semantics.

Complexity (Lehtonen 2024 Theorem 16, matches Dvořák & Dunne 2012):
- Grounded (last-link): polynomial.
- Credulous adm/com/stb/prf: NP-complete.
- Skeptical com / stb: coNP-complete.
- Skeptical prf: Π₂ᴾ-complete.

Encoding listings (2020 paper, p.7):
- Listing 1 — `Γ_guess`: `{sel(X) : ordinary(X)}`,
  `{sel(X) : defeasible(X)}`.
- Listing 2 — `Δ_der`: derivation closure clauses.
- Listing 3 — `Δ_adm`: attack derivation, conflict-free integrity
  constraint, defense integrity constraint.
- Listing 4 — `Δ_sem(σ)`: per-semantics extras
  (forced inclusion for complete; "every unselected attacked" for
  stable; saturation for preferred).

### Fragments Lehtonen does and does not cover

Covered:
- ASPIC+ argumentation theories with only strict strict-rules (no
  defeasible strict rules), contrariness over ordinary premises only,
  symmetric contrariness on `K_p`.
- Preferential extension under last-link, both elitist and democratic
  liftings (2024).
- Flat ABA via the 2019 ASP-for-ABA predecessor; the 2024 framework
  subsumes it because flat ABA = ASPIC+ with all rules defeasible-free
  premises and no strict rules outside transposition.

Not covered:
- Weakest-link preferences (raises grounded to NP-hard;
  Proposition 17).
- First-order (ungrounded) ASPIC+ — the `propstore` Diller 2025
  workstream is the place for that.
- Incomplete information / stability / relevance (Odekerken et al.
  2023, separate workstream).
- Contrariness over rule names / axioms.
- Non-flat ABA.

The codebase already rejects non-flat ABA at construction
(`src/argumentation/aba.py:62-65`, `NotFlatABAError`), so the ABA scope
of Lehtonen aligns exactly with the ABA scope of this library.

---

## 3. Inspect the current codebase

Files read (no edits): `aba.py`, `aba_sat.py`, `aspic.py`,
`aspic_encoding.py`, `preference.py`, `__init__.py`,
`solver_adapters/clingo.py`, `pyproject.toml`. Glob over `tests/` for
clingo and aspic-encoding tests, peek at
`tests/test_aspic_encodings.py`.

### Where extension queries dispatch today

ABA:
- `aba.complete_extensions / preferred_extensions / stable_extensions /
  grounded_extension / ideal_extension` — pure-Python brute enumeration
  over `2^|K_a|` assumption subsets (`_all_subsets`).
- `aba_sat.support_extensions(framework, semantics)` — bitmask
  enumeration with precomputed minimal supports. Faster constant factors
  but still `2^|K_a|`.
- `aba_sat.sat_stable_extension(framework, ...)` — z3 SAT for *stable*
  only, single witness, optional credulous/skeptical literal constraint.
  No SAT path for admissible/complete/preferred. No ABA+ SAT.
- ABA+ (`ABAPlusFramework`) routes through the same brute path; the
  preference filter lives in `attacks_with_preferences`.

ASPIC+:
- `aspic.build_abstract_framework(system, kb, pref) ->
  ASPICAbstractProjection` — eagerly materialises arguments,
  attacks, defeats, and a Dung `ArgumentationFramework`. This is the
  exponential step.
- `aspic_encoding.solve_aspic_grounded(...)` — calls
  `build_abstract_framework` then runs `dung.grounded_extension` on the
  projection. Tagged `backend="materialized_reference"`.
- `aspic_encoding.solve_aspic_with_backend(...,
  backend="clingo", semantics=...)` — *exists already*. For
  `semantics="grounded"` it dispatches to
  `solver_adapters.clingo.run_aspic_grounded_protocol` with the encoded
  facts. For any other semantics it returns `unavailable_backend` with
  reason `"ASPIC+ clingo backend supports grounded only"`.

### Backend abstraction — partial

There is no `Backend` Protocol. Dispatch is keyword-string:
`backend="materialized_reference" | "clingo" | <other>`. Result type
`ASPICQueryResult` is uniform across backends and carries
`status / semantics / backend / accepted_argument_ids /
accepted_conclusions / encoding / metadata`. The status vocabulary is
already established: `"success" | "unavailable_backend" |
"backend_error" | "protocol_error"`. ABA has no such uniform result
type — the SAT path returns either `tuple[AssumptionSet, ...]` or a
`(bool, AssumptionSet | None)` pair.

### Existing clingo wiring — what is and is not real

`solver_adapters/clingo.py:56-112` writes the *facts only* to a temp
`.lp` file and shells out to a binary. It does **not** ship the
Lehtonen rules (`Γ_guess`, `Δ_der`, `Δ_adm`, `Δ_sem(σ)`). The output
parser expects `accepted_arg(...)` and `accepted_lit(...)` atoms.

`tests/test_aspic_encodings.py:188-308` confirms this: every clingo
test uses `monkeypatch.setattr` against `subprocess.run` and a fake
binary. There is no end-to-end test that actually runs clingo against
a real encoding and checks that grounded results match
`materialized_reference`. The "differential" naming in the test file
is therefore aspirational on this axis — it tests the protocol shape,
not the semantic equivalence.

The reference ASPforABA distribution lives in
`scratch/sources/aspforaba/` with five `.dl` encoding files
(`stb-aba-cred.dl`, `stb-aba-skept.dl`, `stb-aba-enum.dl`,
`com-aba-cred.dl`, `com-aba-skept.dl`). These are the upstream source
files for the rule modules this workstream needs to embed.

### Public API for "compute preferred extensions of an ASPIC+ theory"

There is no first-class function. Callers either:
- materialise via `build_abstract_framework` and call
  `dung.preferred_extensions` on the resulting Dung framework, or
- call `solve_aspic_with_backend(..., semantics="preferred")` and
  receive `unavailable_backend`.

This is the API gap the workstream needs to close.

---

## 4. Workstream design

Six phases. Effort estimates assume one engineer with familiarity with
the existing codebase and basic ASP fluency. Phase 0 is a planning
phase; phases 1-5 are implementation.

### Phase 0 — Bindings and abstraction strategy

Effort: 0.5 day.

Decisions:
1. **Clingo binding.** Keep the existing **subprocess** path; do not
   adopt the `clingo` Python package as a hard dep. Reasoning:
   `pyproject.toml:50` has `dependencies = []` and the project's
   stance is z3 as an optional extra (`[project.optional-dependencies]
   .z3`). Adding `clingo` as `[project.optional-dependencies].asp =
   ["clingo>=5.7"]` is consistent and offers a *future* upgrade path
   to in-process control objects. For now, subprocess is sufficient,
   matches the Lehtonen 2024 reference implementation's invocation
   model, and preserves the zero-runtime-dep posture.
2. **Backend abstraction.** *Decision Q3 (2026-05-01): widened
   keyword-string dispatch, no `Backend` Protocol.* Add `"asp"` to the
   accepted vocabulary of the existing `backend=` keyword on
   `solve_aspic_with_backend` and mint a sibling
   `solve_aba_with_backend(framework, *, backend, semantics, task,
   query=None)` with the same dispatch shape. Concrete dispatchers live
   inline (no Protocol class). The result type is the existing
   `ASPICQueryResult` for ASPIC+; mint `ABAQueryResult` with the same
   shape. Re-evaluate Protocol-promotion when a third or fourth backend
   forces it (likely after Datalog/grounding workstream lands).
3. **Encoding module location.** Bundle the static `.lp` rule modules
   as package data under `src/argumentation/encodings/` (new directory).
   Files: `aspic_common.lp`, `aspic_grounded.lp`, `aspic_admissible.lp`,
   `aspic_complete.lp`, `aspic_stable.lp`, `aspic_preferred.lp`,
   `aspic_pref_eli.lp`, `aspic_pref_dem.lp`, plus mirrors for
   `aba_*.lp`. `solver_adapters/clingo.py` concatenates the
   per-task rules with the per-theory facts before invoking clingo.

Files: `src/argumentation/encodings/` (new dir, empty in this phase),
update `pyproject.toml` for optional `asp` extra and
`[tool.hatch.build.targets.wheel]` package-data inclusion. Add
`clingo>=5.7` to `[dependency-groups].dev` for CI symmetry with
`z3-solver` (*decision Q2 (2026-05-01): symmetric CI*).

Success criterion: dispatch keyword `backend="asp"` accepted on
existing entry points and reports `unavailable_backend` cleanly when
clingo is missing; CI installs clingo and runs the existing
`solve_aspic_with_backend(backend="clingo", semantics="grounded")`
path against the real binary at least once (replaces the current
monkeypatch-only coverage); existing tests still pass.

Risks: the existing `backend="clingo"` path has never been exercised
end-to-end — tests monkeypatch `subprocess.run`. Phase 0 includes a
real-clingo smoke test as the gating step. If the existing path is
broken, fix-in-place as part of Phase 0 rather than carrying the
debt into Phase 1.

### Phase 1 — ABA ASP encoder (Lehtonen 2020 / 2019 ABA path)

Effort: 2 days.

New module `src/argumentation/aba_asp.py`. Responsibilities:
- `encode_aba_theory(framework: ABAFramework) -> ABAEncoding` — emit
  `assumption/1`, `contrary/2`, `head/2`, `body/2`, `rule/1`,
  `axiom/1` facts following the 2019 ABA convention used by the
  ASPforABA reference (`scratch/sources/aspforaba/encodings/*.dl`).
  Mirror `ASPICEncoding` field shape (facts, signature, metadata,
  `literal_by_id`).
- `solve_aba_with_backend(framework, *, backend, semantics, task,
  query=None, binary="clingo", timeout_seconds=30.0) -> ABAQueryResult`.
- Bundle `aba_common.lp + aba_admissible.lp + aba_complete.lp +
  aba_stable.lp + aba_preferred.lp` ports of the listings.

Verification: differential test against `aba_sat.support_extensions`
on the existing test instances and on Hypothesis-generated small ABA
frameworks (max 5 assumptions, 8 rules). Both must produce the same
extension set after canonical ordering. Drop the bitmask backend's
preferred enumeration as a known-correct oracle.

Files: `src/argumentation/aba_asp.py`, encodings under
`src/argumentation/encodings/aba_*.lp`,
`tests/test_aba_asp_differential.py`.

Success criterion: 100% agreement with `aba_sat` on extension sets for
the existing differential test corpus and at least 200
Hypothesis-generated small instances. End-to-end test runs against a
real installed clingo binary, gated on `pytest.mark.skipif(not
shutil.which("clingo"))`.

Risks:
- ASPforABA's `.dl` files use Datalog dialect quirks (no choice
  syntax in some versions). Mitigation: port to plain Clingo ASP
  (`{...}` choice rules and `:- ...` integrity constraints, not
  Datalog `<>` / `not` mixing).
- Preferred-semantics saturation is the most error-prone module. Lift
  it directly from the 2020 listing rather than reinventing.

### Phase 2 — ASPIC+ ASP encoder, full semantics (Lehtonen 2020)

Effort: 3 days.

New module `src/argumentation/aspic_asp.py`. The fact emitter
(`encode_aspic_theory`) already exists and matches Lehtonen's vocabulary
— reuse it as is. The work is to:
- Add the rule-module set (`aspic_common.lp` plus per-semantics) under
  `src/argumentation/encodings/`.
- Extend `solver_adapters/clingo.py` to concatenate the
  semantics-appropriate rule modules with the facts.
- Replace the current "grounded only" guard in
  `solve_aspic_with_backend` with a per-semantics dispatch over
  `{"grounded", "admissible", "complete", "stable", "preferred"}`.
- Add `task ∈ {"enum", "credulous", "skeptical"}` and a `query`
  parameter for credulous/skeptical decisions, matching the existing
  `aba_sat.support_acceptance` shape.

Verification: differential against `build_abstract_framework` +
`dung.<sigma>_extensions` on small instances (≤ 6 ordinary premises,
≤ 6 defeasible rules); skip tests that would explode the
materialisation path.

Files: `src/argumentation/aspic_asp.py`,
`src/argumentation/encodings/aspic_*.lp`,
`tests/test_aspic_asp_differential.py`.

Success criterion: full agreement with the materialised reference on
small instances; documented timeout-margin for the materialised path
beyond `|R_d| + |K_p| ≥ 12`.

Risks:
- Argument-id reconstruction. Lehtonen's encoding accepts `(P, D)`
  pairs. Callers expect `accepted_argument_ids` populated. *Decision
  Q10 (2026-05-01): option A — reconstruct arguments post-hoc by
  running `build_arguments_for(...)` filtered by the accepted
  defeasible elements.* Pay the materialisation cost to match the SAT
  backend's surface; callers do not have to special-case the ASP
  backend's result shape. Document the per-query cost in
  `metadata["postproc_argument_reconstruction_seconds"]` so it is
  visible in profiling.

### Phase 3 — Preferential lifting (Lehtonen 2024)

Effort: 3 days.

Add `aspic_pref_eli.lp` (II_ELI) and `aspic_pref_dem.lp` (II_DEM)
modules. The fact emitter already produces `preferred(stronger,
weaker)` facts (`aspic_encoding.py:96-102`); the rule modules consume
them.

Routing: `solve_aspic_with_backend` reads `pref.comparison ∈
{"elitist", "democratic"}` and selects the appropriate module.
`pref.link == "weakest"` returns `unavailable_backend` with reason
`"ASP backend covers last-link only; weakest-link grounded is NP-hard
per Lehtonen 2024 Prop 17"`.

Files: `src/argumentation/encodings/aspic_pref_eli.lp`,
`aspic_pref_dem.lp`, update `aspic_asp.py` dispatch, update
`tests/test_aspic_asp_differential.py` to cover both liftings.

Success criterion: agreement with `compute_defeats` +
`dung.<sigma>_extensions` on small preferential instances under both
liftings; agreement test specifically around the contradictory-rebut
case where elitist and democratic disagree.

Risks:
- Preference fact direction. The current emitter writes
  `preferred(stronger, weaker)` which is the opposite of
  `preference.py`'s `(weaker, stronger)` tuple convention. Verify
  before assuming Lehtonen's modules read in the same direction; if
  not, swap once at emission rather than rewriting modules.

### Phase 4 — Benchmark harness

Effort: 2 days base + 2-4 days for external-systems sub-phase
(*decision Q12 (2026-05-01): include external systems*).

New `bench/` directory (or extend an existing one if present —
inspect during the phase). Generators for ABA and ASPIC+ instances
parameterised by `(|K_p|, |R_d|, body_size, defeasible_ratio)`.
Targets: matched runs with the SAT/brute backend at `N ∈ {5, 10, 20,
40}` and ASP-only runs at `N ∈ {100, 250, 500, 1000}`. Time and
memory captured. Output as a CSV plus a short Markdown report under
`reports/bench-asp-vs-sat-2026-MM-DD.md`.

External-systems sub-phase: install and calibrate the comparison set:
- **ASPforABA** (the ASPforABA reference implementation — `.dl` files
  already in `scratch/sources/aspforaba/`; needs install + harness)
- **ASPforASPIC** (the Lehtonen reference)
- **TOAST** if reachable
- **ANGRY** if reachable
- **ICCMA 2023 ASPIC+ track instances** via
  `solver_adapters/iccma_aba.py` if format is compatible
- Document install instructions, version numbers, and any patching in
  `bench/README.md` for reproducibility

Files: `bench/asp_vs_sat.py`, `bench/instance_gen.py`,
`bench/external_systems/` (subprocess wrappers per system),
`bench/README.md`.

Success criterion:
- (base) replicates the qualitative shape of Lehtonen 2024 Figure 2 —
  SAT/brute saturates around `N=40`, ASP continues into the hundreds.
- (external) reproduces published ASPforASPIC numbers within 2× on
  matched instance sets; documents any divergence.

Risks:
- Synthetic instance generators that systematically favour one
  backend. Mitigation: cross-check against the ICCMA 2023 ASPIC+
  track instance set.
- External systems may not install cleanly on Windows. Mitigation:
  document WSL or container path as fallback; CI runs only the
  base benchmark, external comparison stays manual.

### Phase 5 — Backend selection heuristic

Effort: 1 day.

Add `default_backend(semantics: str, theory_size: int, has_preferences:
bool, weakest_link: bool) -> str` to `backends.py`. Rule:

```
if weakest_link:                       return "materialized_reference"
if semantics == "grounded":            return "asp"  # poly anyway, asp scales
if theory_size > 30 and has_clingo():  return "asp"
if has_z3():                           return "sat"
return "materialized_reference"
```

`theory_size = |K_p| + |R_d|`. The 30 cutoff is the empirical knee
between brute-feasible and brute-blown; tune from Phase 4 numbers.
Capability detection via `shutil.which("clingo")` and
`importlib.util.find_spec("z3")`. Document the rule in
`docs/backends.md` (new file).

Files: extend `src/argumentation/backends.py`, `docs/backends.md`,
`tests/test_backend_selection.py`.

Success criterion: dispatch table matches the documented rule for all
relevant input combinations; users can override with explicit
`backend=` argument.

Risks: silent backend changes between releases. Mitigation: log the
chosen backend in `metadata["backend_choice_reason"]` of the result.

### Phase ordering and cumulative effort

Sequential: 0.5 + 2 + 3 + 3 + (2 + 2-4 external) + 1 ≈ **13.5–15.5
engineer-days**, plus review and CI churn. Phases 1 and 2 share most
of the encoding-module authoring work; if a single engineer takes
both, count 4 instead of 5 elapsed days for the pair. Phase 3 cannot
start until Phase 2 lands because it shares dispatch surface. Phase 4
can start in parallel with Phase 3 once Phase 2 is on a feature
branch.

This workstream runs **first** in the serial sequence per decision
Q15 (ASP → Datalog → DG). The Datalog workstream cannot begin until
this one ships.

---

## 5. Risks and unknowns

### Clingo as a runtime dependency

`pyproject.toml:50` is `dependencies = []`. The project carries z3 as
an optional extra and has the same pattern available for clingo. The
subprocess approach side-steps the Python `clingo` package and only
requires the binary on PATH at call time. Risk class: **low**, no
deviation from established stance. The `[project.optional-dependencies]
.asp` extra is recommended for tests and documentation, *not* required
for installation.

### ASP solver opacity

Clingo timeouts return `ClingoProcessError` today. For users
debugging "preferred extension came back wrong / slow", the available
information is stdout/stderr — far less actionable than a SAT trace.
Mitigations:
- Always include the generated `.lp` file path in `metadata` on error
  (currently `_write_temp_program` deletes it; gate deletion on
  successful return only).
- Provide `solve_aspic_with_backend(..., debug=True)` that retains
  the `.lp` file and writes it under `out/asp-debug/` for offline
  reproduction with `clingo --verbose=3`.
- Document a "minimal repro" recipe in `docs/backends.md`.

### API surface impact

`solve_aspic_with_backend` already accepts `backend=` and `semantics=`
keywords; widening the accepted semantics set is purely additive. The
new `Backend` Protocol changes nothing for callers using the existing
free-function entry points. The new `solve_aba_with_backend` is net-new.
Risk class: **low**. Bumping the project version from `0.2.0` to
`0.3.0` matches the surface change.

### Greenfield vs incremental

This is **not greenfield**. Confirmed by reading `aspic_encoding.py`
and `solver_adapters/clingo.py`: facts emission, subprocess driver,
result types, and one-semantics dispatch are already present. The
existing tests for the clingo path use `monkeypatch` against
`subprocess.run` — they validate the protocol and not real clingo
execution. A real-clingo end-to-end test does not currently exist; the
workstream must add at least one in Phase 1 or 2 to validate the rule
modules against an installed solver.

### Other unknowns to call out

- **Which Clingo version to target?** Lehtonen 2020 used 4.5.0,
  Lehtonen 2024 used 5.7.1. The reference ASPforABA distribution in
  `scratch/sources/aspforaba/aspforaba/clingo-5.6.2/` suggests a 5.6+
  baseline. The choice rule and saturation patterns the encoding uses
  are stable across the 5.x line. Recommend `clingo >= 5.5`.
- **Can the existing `accepted_arg/1` show statement be retained?**
  Lehtonen's encodings naturally project `sel(X)` for selected
  defeasible elements, not arguments. Either extend the encoding with
  a `accepted_arg(X) :- sel(X).` shim or change the parser to accept
  `sel/1`. The shim path keeps `solver_adapters/clingo.py` parser
  unchanged.
- **Does `iccma_aba.py` impose structural constraints we must match
  for benchmarking?** Inspect during Phase 4 — not blocking earlier
  phases.

---

## 6. Decisions (resolved 2026-05-01)

All Phase 0 gating decisions resolved. The five questions originally
posed in this section have answers now baked into the phase
descriptions above; restated here as the canonical record:

1. **Optional extra naming.** → Add
   `[project.optional-dependencies].asp = ["clingo>=5.7"]` for tests
   and docs. Subprocess at runtime; the Python package is for
   in-process control objects in a future iteration.
2. **Backend abstraction depth.** → Widened keyword-string dispatch.
   No `Backend` Protocol in this workstream. Re-evaluate when a third
   or fourth backend lands (likely Datalog/grounding).
3. **`accepted_argument_ids` for ASP results.** → Populate via
   post-hoc `build_arguments_for`. Pay the materialisation cost to
   match the SAT backend's surface; record the cost in
   `metadata["postproc_argument_reconstruction_seconds"]`.
4. **Weakest-link policy.** → Hard-fail with `unavailable_backend`
   and reason `"ASP backend covers last-link only; weakest-link
   grounded is NP-hard per Lehtonen 2024 Prop 17"`. No silent
   fall-through.
5. **End-to-end clingo CI.** → Symmetric with z3. Add `clingo>=5.7`
   to `[dependency-groups].dev` so CI installs it and the
   `solve_aspic_with_backend(backend="clingo", ...)` path runs
   against a real binary in CI from Phase 0 onward.

Cross-workstream decisions also affecting this workstream:

- **Q12 (include external benchmarks):** Phase 4 expands by 2-4 days
  to install and calibrate ASPforABA, ASPforASPIC, TOAST, ANGRY, and
  ICCMA 2023 ASPIC+ track instances.
- **Q15 (serial execution):** This workstream runs **first**. Datalog
  starts only after this ships.

Open question deferred to the Datalog workstream: when the third
backend lands, does keyword dispatch still scale or does the
`Backend` Protocol promotion become forced? Re-evaluate then.

---

## Appendix — file inventory

Read (no edits):

```
src/argumentation/aba.py
src/argumentation/aba_sat.py
src/argumentation/aspic.py
src/argumentation/aspic_encoding.py
src/argumentation/preference.py
src/argumentation/__init__.py
src/argumentation/solver_adapters/clingo.py
pyproject.toml
tests/test_aspic_encodings.py  (lines 1-310, partial)
propstore/papers/Lehtonen_2020_AnswerSetProgrammingApproach/notes.md
propstore/papers/Lehtonen_2024_PreferentialASPIC/notes.md
```

To create:

```
src/argumentation/backends.py            (Phase 0)
src/argumentation/encodings/             (Phase 0..3, dir + .lp files)
src/argumentation/aba_asp.py             (Phase 1)
src/argumentation/aspic_asp.py           (Phase 2)
tests/test_aba_asp_differential.py       (Phase 1)
tests/test_aspic_asp_differential.py     (Phase 2..3)
tests/test_backend_selection.py          (Phase 5)
bench/asp_vs_sat.py                      (Phase 4)
bench/instance_gen.py                    (Phase 4)
docs/backends.md                         (Phase 5)
reports/bench-asp-vs-sat-2026-MM-DD.md   (Phase 4 output)
```

To modify:

```
src/argumentation/solver_adapters/clingo.py    (Phases 1..3)
src/argumentation/aspic_encoding.py            (Phase 2: drop grounded-only guard)
src/argumentation/__init__.py                  (Phase 1, 2: export new modules)
pyproject.toml                                 (Phase 0: asp extra, package data)
```
