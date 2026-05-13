# SOTA assessment of argumentation pkg vs propstore needs

Date: 2026-04-25

## What's in argumentation (verified via wc -l, README)
- dung.py (327): grounded/complete/preferred/stable; backend="auto" → brute or z3
- dung_z3.py (293): SAT enumeration, SolverSat/Unsat/Unknown, 30s timeout
- aspic.py (1332): full ASPIC+ a la Modgil/Prakken 2018, elitist/democratic, last/weakest link
- bipolar.py (327): Cayrol-style support, derived defeats, d/s/c-admissible
- partial_af.py (424): completion enumeration, sum/max/leximax merge, consensual_expand
- af_revision.py (361): Baumann kernel union, Diller formula/framework revision, Cayrol classifier
- probabilistic.py (1353) + components/dfquad/treedecomp (~2.5k): Li 2012 enum/MC,
  Hunter-Thimm component decomposition, Popescu-Wallner 2024 tree-decomp DP, DF-QuAD
- semantics.py (143): generic dispatch
- preference.py (82): SPO closure, elitist/democratic, generic defeat resolution

## What's NOT in argumentation (gap candidates)
- Ranking-based semantics (h-categorizer, Amgoud 2013, Bonzon 2016 comparison)
- Weighted AFs (Dunne 2011 WAFs with inconsistency budget)
- Abstract dialectical frameworks (Brewka 2010/2013 ADFs) — strict superset of bipolar/Dung
- ABA / assumption-based argumentation (Bondarenko 1997)
- SETAFs / claim-augmented AFs
- Enforcement (Baumann 2010 ExpandingAFs) — only have revision, not enforcement
- ICCMA solver interop (Niskanen 2020 Toksia, ICCMA 2023 Järvisalo 2025)
- Value-based AFs (Bench-Capon 2003), Wallner 2024 value-based ASPIC
- Continuous dynamical systems for weighted (Potyka 2018) — partial via DF-QuAD
- Ranking principles (Bonzon 2016) — none of these implemented

## Propstore consumption pattern
- propstore/aspic_bridge/, claim_graph.py, praf/, belief_set/ are adapters
- argumentation owns finite formal kernel; propstore owns claim/context/store/CLI
- 224 papers in propstore/papers — argumentation cites a small subset

## Verdict shape
Solid, not SOTA. The kernel is well-cited and correct but covers the canonical
1995-2018 line + a handful of 2024 picks (Popescu-Wallner DP, DF-QuAD). Major
2010s-2020s SOTA families absent: ranking semantics, ADFs, ABA, enforcement,
SETAF, ICCMA solver protocol.

## Top gaps for propstore utility
1. Ranking semantics (h-cat, burden, social-AF) — propstore has fragility/calibration,
   ranking semantics give per-arg scores compatible with quantitative claim signals
2. ADFs — strict superset for bipolar+; propstore stances already polar
3. ICCMA solver protocol — scalability beyond Z3 for big claim graphs
4. Enforcement — propstore's revision adapters could use it for "make claim X accepted"
5. ABA — propstore has rules/predicates already (knowledge/rules/, predicates/)

## Risks
- Don't pull SL opinions / calibration into argumentation (boundary doc explicit)
- Probabilistic strategy="auto" thresholds (≤13 args) may overclaim for real
  propstore graphs — needs benchmarking
- DF-QuAD branding as "SOTA" — it's 2025 but only one of several gradual families
