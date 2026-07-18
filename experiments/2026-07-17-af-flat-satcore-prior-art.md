# Prior-art search record — sat-core engine on flat AF SAT paths (candidate B)

Date: 2026-07-17
Branch: `exp/af-flat-satcore` (off `main` @ `f4b8eac`).
Candidate: **B** — route flat AF acceptance/extension SAT paths through Z3
`Tactic('sat')` (sat-core) instead of the default SMT core, targeting
single-SCC families (ER_300) where the SCC-cone routing never fires because
the cone equals the whole graph.

This satisfies the AGENTS.md prior-art gate. **Headline: candidate B was
already executed through the probe + routing-derivation stage by
`exp/af-satcore-flat` (2026-07-10) and left at "Decision: TO BE FILLED". Its
committed evidence contradicts this dispatch's triage gate.**

## 1. Locations and terms searched

- `experiments/`, `notes/`, `reports/`, git branches/log; `papers/`.
- Terms: `sat-core`, `Tactic('sat')`, `engine=`, `smt`, `flat`, `CDCL`,
  `PbGe`/`PbEq`, `PREFERRED_CONE_MIN_DEFEATS`.
- Source: `src/argumentation/solving/af_sat.py`,
  `src/argumentation/solving/af_scc_cone.py`.

## 2. Decisive hit — `exp/af-satcore-flat` @ `3973193` (the pre-emption)

Branch `exp/af-satcore-flat` (base `b70a1d6`), one commit "Probe smt vs
sat-core on flat AF paths; derive routing before code". It contains:
`experiments/2026-07-10-af-satcore-flat.md`, a 74-cell A/B probe
(`logs/af-satcore-flat-probe.jsonl`), `scripts/probe_af_satcore_flat.py`,
`scripts/summarize_af_satcore_probe.py`. Status per the meta-scoreboard scout
(`notes-iccma-meta-scoreboard-scout-20260717.md:27`): "INCOMPLETE — only
probe/preregistration committed, Decision TO BE FILLED".

**What it already established (committed evidence):**

- **Zero answer disagreements** across all 74 probed cells (both engines agree
  everywhere they both finish) — the answer-preserving safety this candidate
  needs is already measured.
- **Per-op routing derivation** (from the table):
  1. Complete finder (`dc_co`/`ds_co`, single check): win-or-tie at every
     size/density, one TO→solved flip (ER_300_20_2 dc_co 87.6 s). → sat-core
     **unconditional**.
  2. Preferred witness loop (`dc_pr`/`se_pr`, `find_preferred_extension`):
     win-or-tie incl. 1.7× on tiny BA and a ≥2.3× TO→solved on ER_400_60_3
     se_pr (56.1 s). → sat-core **unconditional**.
  3. CDAS `ds_pr`: small-instance pathology reproduces (BA_160_80_2 0.42 s →
     11.55 s, **27×**, at 289 defeats); win-or-tie from ~9 901 defeats up.
     → sat-core **iff input defeats ≥ 15 000** (reuse `PREFERRED_CONE_MIN_DEFEATS`).
  4. Stable (`dc_st`/`ds_st`): no ≥1.1× win, one 1.18× loss → **keep smt**.
  5. Ideal: 1.54× loss small, both-TO at scale → **keep smt**.
  6. Semi-stable / stage: **excluded by construction** — the range-maximal
     loop uses `PbGe`/`PbEq` which `Tactic('sat')` does not support.

- **Its own gate-exposure note (the reason it stalled):** "the frontier DS-PR
  ER cells themselves (ER_300_20_2, ER_400_60_3, ER_500_10_10) stayed both-TO
  under both engines, so **no frontier flip is predicted**. The t15 slice is
  predicted unchanged outside noise." The two ≥2× wins land on cells **no
  current gate/manifest samples** (ER_300_50_8's row is DS-SST = excluded;
  ER_400_60_3 se_pr has no AF SE frontier row; ER_300_20_2 dc_co has no DC-CO
  frontier row).

**Cause of stall: null headline gate payoff.** Not unsafe, not wrong — it
predicts no frontier flip and no t15 change, so there was no metric to record
a GO against, and the decision was left blank.

## 3. Applicability to current main (verified this session)

The prior probe was on `b70a1d6`; main is now `f4b8eac`. The 6A engine
threading has since landed, so on current main:

- `find_complete_extension`, `find_stable_extension`,
  `is_preferred_skeptically_accepted` **already accept `engine=`** (default
  `"smt"`; only the cone path passes `"sat-core"`).
- `find_preferred_extension`, `find_semi_stable_extension`,
  `find_stage_extension`, `find_ideal_extension` do **not** take `engine=`.
- `PbGe`/`PbEq` at `af_sat.py:304,314`; `Tactic("sat")` at `:60` — the
  semi-stable/stage exclusion holds unchanged.

So the prior routing derivation transfers directly; nothing in the interim
landings invalidates it.

## 4. This dispatch's triage gate is contradicted by prior evidence

The dispatch proposed the triage gate: "ER_300 DS-SST or DS-PR timeout row
flips at t120 --jobs 1, or dominant cost shifts in py-spy." Committed prior
evidence (AGENTS.md evidence rank 2, above reviewer opinion rank 5):

- **DS-SST is impossible** for sat-core — semi-stable uses pseudo-Boolean
  range constraints `Tactic('sat')` cannot express. Not a tuning gap; a
  construction exclusion.
- **ER DS-PR frontier cells are both-TO** under both engines — sat-core does
  not flip them.

The only sat-core wins are TO→solved on **off-gate** instances no frontier
manifest or t15 slice currently samples.

## 5. Papers

mu-toksia (`Niskanen_2020_MuToksia…`, read this session pp.1–2) and Crustabri
(p.20) both use external CDCL SAT solvers (Glucose/CryptoMiniSAT, CaDiCaL) —
consistent with "a CDCL core beats a general SMT core on the purely
propositional labelling encodings," which is the mechanism behind the 165×
`Tactic('sat')` win measured in 6A (`2026-07-10-af-scc-acceptance.md`). No
paper bears more directly than the in-repo committed probe; the decisive
evidence for this candidate is rank-2 (the 74-cell A/B table), not a paper.

## 6. Verdict of the search

**Candidate B is ~90% pre-empted by `exp/af-satcore-flat`.** The probe is done
(74 cells, zero disagreements), the routing is derived, safety is measured,
and the code substrate (engine threading) partly landed via 6A. What remains
is implementation + gate confirmation — but the prior probe's own gate-exposure
note predicts **no frontier flip and no t15 change**, and the dispatch's
DS-SST/ER-DS-PR flip gate is **falsified** by that committed evidence.

Recommendation (to team-lead, not a unilateral goal change): either
**(a)** finish the safe, answer-preserving routing change (implement the
derived predicate, confirm zero regression + the off-gate TO→solved flips,
record GO as a coverage/robustness win — no headline frontier move); or
**(b)** stand down candidate B as a frontier lever, since prior committed
evidence says it will not flip a sampled cell, and redirect budget to a
candidate with live frontier payoff (e.g. C: SAT-VE, or the search-reduction
levers named by the candidate-A kill). Presenting the evidence before
implementing toward a contradicted gate.
