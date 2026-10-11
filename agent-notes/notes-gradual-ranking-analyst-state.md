# Analyst state: gradual/ranking correctness review (2026-07-10)

Checkpoint 3. Final findings go in reply text, not here.

## Files read (full)
gradual src: gradual.py, llm_surface.py, dfquad.py, equational.py, sensitivity.py,
gradual_principles.py, __init__.py; core/fixpoint.py
ranking src: ranking.py, matt_toni.py, _graph.py, ranking_axioms.py, weighted.py
papers notes: Gabbay_2012, Matt_2008, Potyka_2018, Bonzon_2016
tests read: test_llm_surface.py, test_gabbay_equational_fixpoint.py,
test_gabbay_equational_relation_to_dung.py, test_ranking.py, test_ranking_axioms.py

## Candidate findings (see checkpoint 2 for details; unchanged unless noted)
F1 llm_surface discards convergence metadata (explain_acceptance :89-104, contest :123/:143;
   contest can't even pass tolerance/max_iterations). Tests only cover converging graphs.
F2 equational.py:51-58 support_value=1.0 default when no supporters -> isolated arg strength 1.0
   regardless of base; strength-0 supporter discontinuity. Tests all use weight 1.0 (masked).
F3 ranking_axioms._group_at_least_as_acceptable greedy matching in name order can miss valid
   injection -> counter_transitivity/SCT false violations. Counterexample designed (b1,w2,b2,w1).
F4 discussion_based_ranking: frontier-set weighted-sum heuristic; VP violation counterexample
   (a<-b, b<-c1, b<-c2: score(a)=7/6 > 1.0 unattacked). Dbs satisfies VP per Bonzon Table 2.
   Tests only assert "total preorder" for these semantics — no values checked (test_ranking.py:104-121).
F5 burden ranking by final-step number, converged=True unconditional, no convergence check.
F6 h_categoriser cap min(1,sum) not literature h-categoriser (naming/definition).
F7 iterated_graded_ranking ad-hoc (not Grossi-Modgil).
F8 tuples_ranking not Cayrol Tuples*; /10^level digit collisions.
F9 self_contradiction allows ties (Bonzon requires strict per notes? notes say "no higher" —
   actually Bonzon notes line 133 says "ranked no higher than" -> maybe checker OK. Downgrade F9a.
   cardinality_precedence restricted to unattacked attackers (Bonzon notes line 134 say CP requires
   all-non-attacked attackers! "(all non-attacked)" — so restriction may be faithful. Downgrade.)
   strict_addition_of_defense_branch local-shape can false-flag. Keep as PLAUSIBLE only.
F10 gradual_principles checks are coarse; PRINCIPLE_COMPLIANCE claims gabbay_inverse balance=HOLDS
    which F2 contradicts (execute principle_balance with equational + isolated arg w=0.5).

## Cleared
- matt_toni reward formula matches paper Table 1 (hand-checked F2 s(b)=0.25, F3 0.5).
  papers/Matt_2008/notes.md itself misstates payoff (ratio form) and proponent sets (admissible)
  — inconsistent with its own Table 1. Notes bug, not code bug.
- iterate_fixpoint honest. weighted.py faithful to Dunne direct definition.
- Potyka agg/influence formulas in gradual.py match Potyka 2018 notes (equilibrium strength w +
  (1-w)h(E) / w - w*h(-E), h = x^2/(1+x^2)). quadratic_impact matches.
- categoriser matches Cat definition incl. unattacked=1 special case; Bonzon running example test.
- test_ranking.py has non-convergence-is-data test for categoriser (good).

## Test coverage observations
- test_ranking_axioms.py: only positive cases; never tests that checkers report violations
  (no negative fixtures), so F3 miss is unsurprising.
- equational tests: only weights 1.0 (masks F2).
- llm_surface tests: tiny acyclic graphs; convergence flag never surfaced.

## TODO next
1. Execute confirmations (uv run python): F1 (cyclic QBAF or max_iterations=1 via
   explain_acceptance — note explain_acceptance accepts max_iterations, contest does not;
   need genuinely non-converging graph for contest OR show discrete/cont non-convergence),
   F2 (isolated arg 0.5 -> 1.0; principle_balance contradiction), F3 (direct call), F4 (VP).
2. Check whether quadratic continuous model can fail to converge at all in practice: strong
   attack 2-cycle? Potyka: cyclic convergence empirical ~99%. Try known hard cycle; if not
   found, F1 confirm via explain_acceptance(max_iterations=1) silent garbage + API shape.
3. Skim remaining gradual tests (dfquad, principles, potyka convergence, sensitivity) + matt_toni
   tests + test_weighted.py.
4. Skim Rago_2016 notes (DF-QuAD formulas + bipolar SAFA neutral point) to judge
   dfquad_bipolar_strengths (claims Rago SAFA Defs 1-3 but just uniform base score).
5. Kampik_2024 / AlAnaissy_2024 / Baroni_2019 / Freedman_2025 notes skim if time.

## Blockers
None.
