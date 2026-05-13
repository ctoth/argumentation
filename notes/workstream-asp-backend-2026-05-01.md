# Workstream design — ASP backend for preferential ABA / ASPIC+

## Date: 2026-05-01

## Task
Design (no implementation) workstream for adding a Clingo-based ASP backend
covering preferential ABA / ABA+ and preferential ASPIC+, per Lehtonen 2020
and Lehtonen 2024. Deliverable: `reports/workstream-asp-backend.md`,
~2000-3500 words.

## Observations from codebase (verified by Read)

### Existing backend infrastructure — NOT greenfield
- `src/argumentation/solver_adapters/clingo.py` ALREADY EXISTS. It runs
  clingo via `subprocess`, uses temp .lp files, parses `accepted_arg(...)`
  and `accepted_lit(...)` atoms. Returns
  `ClingoAnswerSetSuccess | ClingoUnavailable | ClingoProcessError | ClingoProtocolError`.
- `aspic_encoding.encode_aspic_theory` already emits Lehtonen-2024-style
  facts: `axiom/1`, `premise/1`, `s_head/2`, `s_body/2`, `d_head/2`,
  `d_body/2`, `contrary/2`, `ctrd/2`, `preferred/2`. Metadata tag is
  `lehtonen_2024_assumption_facts`.
- `aspic_encoding.solve_aspic_with_backend(backend="clingo", semantics="grounded")`
  is wired up. Returns `unavailable_backend` for non-grounded semantics
  with reason "ASPIC+ clingo backend supports grounded only".
- Clingo is invoked as a subprocess BINARY, not via the Python `clingo`
  package. The protocol expects an .lp encoding file to live somewhere
  (search for that file is the next thing to do).

### What's missing
- No `aba_asp.py` module. ABA backend is `aba_sat.py` only (z3-based,
  optional dep). ABA solving has bitmask brute-force (`_SupportState`)
  for stable/complete/preferred + a true z3 SAT path for stable.
- No admissible/complete/stable/preferred clingo path for ASPIC+.
- No preference lifting in the ASP path (encoding emits `preferred/2`
  but there's no published listing module that consumes it for
  elitist/democratic last-link). The bundled .lp file likely encodes
  one specific lifting — needs verification.
- No backend-selection abstraction beyond the per-call `backend=` arg.

### pyproject.toml
- `dependencies = []` — strict zero runtime deps stance.
- `z3-solver` is in `[project.optional-dependencies].z3` AND in dev group.
- Adding `clingo` would follow the same pattern: optional extra, not core
  dep. Subprocess approach already works without the python binding.

## Papers — read

### Lehtonen 2020 (notes.md, 240 lines)
- Argumentation Theories (ATs): restricted ASPIC+ — no preferences,
  contrariness only on ordinary premises, all strict rules.
- σ-assumptions = pairs (P, D) of ordinary premises × defeasible rules.
  Theorem 5: σ-assumptions biject with σ-extensions for σ ∈
  {adm, com, prf, stb}.
- Bound: at most 2^|K_p| × 2^|R_d|, polynomial-WIDTH search space
  vs exponential argument enumeration.
- Listings 1-4: Γ_guess (choice rules), Δ_der (forward derivation),
  Δ_adm (attack + conflict-free + defense), Δ_sem(σ)
  (complete/stable/preferred via saturation for prf).
- Scale: N up to 3000 atoms, 15 axioms, 300s timeout, Clingo 4.5.0.
  Most instances solve under 1s at N=500.

### Lehtonen 2024 (notes.md, 59 lines)
- Extends to preferential ASPIC+ under last-link, both elitist and
  democratic lifting. Modules II_common, II_ELI, II_DEM.
- Theorem 16: Preferential complexity matches abstract AF —
  cred NP-complete (adm/com/stb/prf), skep coNP-complete (com/stb),
  Π₂ᴾ-complete (skep prf). Grounded poly under last-link.
- Proposition 17: Under WEAKEST-link, even grounded acceptance
  is NP-hard. Codebase's PreferenceConfig supports both
  link="last" and link="weakest" — the ASP backend per Lehtonen
  only covers last-link.
- Scale: ASPforASPIC handles 1500 (DEM) / 1900 (ELI) atoms vs
  PyArg's 50-80. Clingo 5.7.1, 600s, 32GB.

### Bondarenko 1997 directory
- Not in `propstore/papers/` collection (Glob returned no results).
- Workstream report should still mention it conceptually as the source
  of the structured-to-AF translation that ASP avoids.

### Lehtonen 2017 ABA paper
- Not in collection. Will reference Lehtonen 2019 ASP-for-ABA from
  the cross-references in Lehtonen 2020 notes ("Lehtonen, Wallner,
  Järvisalo 2019 — ASP for assumption-based argumentation (ABA),
  predecessor to this work") if needed.

## Things still to verify before report
- Is there an actual .lp encoding file shipped with the project,
  or does clingo only get bare facts? (Search for *.lp files)
- Does `solver_adapters/clingo.py` implement the Lehtonen Listings
  1-4 inline anywhere, or is the program assumed to be authored
  externally? Looking at the function — only facts are written;
  no rules/encoding module included. So "grounded" must currently
  rely on the user supplying their own encoding, OR there's a
  bundled .lp template. NEED TO VERIFY.
- Existing tests for the clingo path — what semantics do they
  cover end-to-end? (Skip — design only, but worth one Glob.)

## Current blocker
None. Have enough to write Sections 1-3 fully and design Sections 4-6.
Need 1-2 more reads (search for .lp files, peek at one test for
clingo path) then draft the report.

## Plan for remaining work
1. Glob for .lp files and one clingo test file.
2. Write `reports/workstream-asp-backend.md` per the spec.
3. Done.
