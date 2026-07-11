# ICCMA ABA SE-ST optimization history inventory

Date: 2026-07-11

## Scope and method

This is a read-only Git-object inventory of materially distinct ABA stable
single-witness or no-witness/UNSAT optimization attempts. I inspected all local
and remote refs visible in this checkout with `git for-each-ref`, `git log
--all`, `git show <commit>:<path>`, and branch containment/ancestry queries. I
read committed experiment, workstream, plan, and report blobs. I did not use
untracked notes/reports as evidence.

Repository boundary and controls:

- checkout: `C:\Users\Q\code\argumentation`;
- expected and observed tracked HEAD:
  `ece99962e4a5a442735eea4ff08ac5904e16a47c` on `main`;
- `origin/main` observed at
  `5f75a7cdd96f7f08b4665fb3772d60cf650d835c`;
- tracked tree was clean; substantial unrelated untracked material was left
  untouched;
- no checkout, branch/worktree switch, solver, benchmark, holdout read, commit,
  push, or generated-data inspection was performed;
- the only file written is this report.

The campaign control surface is `experiments/INDEX.md`. Its frozen development
baseline is 21/24 solved at `5f75a7c`, with three 10-second timeouts on the
600-assumption `aba_2000_0.3_10_10_*` shape. The sealed holdout was not read.

Status vocabulary used below:

- **kept/current**: production mechanism is an ancestor of tracked HEAD;
- **kept evidence only**: record/instrumentation remains, production delta did
  not land or was later deleted;
- **reverted/abandoned**: implementation was explicitly reversed, removed, or
  failed its promotion gate;
- **superseded**: a later mechanism or diagnosis makes retrying the same idea
  non-novel;
- **untried**: no committed implementation/probe of that exact mechanism and
  semantic scope was found in any visible ref.

## Executive finding

The history is not a blank slate. It already contains both major ASP stable
encodings, broad Clingo configuration/heuristic/lookahead work, integer- and
bit-vector-ranked Z3 closure, SCC-local ranks, support materialization, native
completion CNF with lazy loop formulas, several clause/seed refinements,
CaDiCaL engine and IPASIR-UP variants, eager arc acyclicity, SAT-VE,
well-founded preprocessing, structural routing, and failed broad portfolio
guards.

For the current 2023 SE-ST timeout, the live route is complete-plus-stable
Clingo and the row is a hard UNSAT proof. The forced native alternative has two
separate walls: ranked-Z3 construction (`391/399` profile samples) and, after
removing that construction, a rank-free/native-CNF UNSAT solve of `46.12 s`.
Therefore “remove ranks,” “try direct stable ASP,” “try Clingo configs,” “add
acyclicity,” or “route to native SAT” are not novel candidates.

Only these SE-ST mechanism families remain genuinely untried in committed
history:

1. full stable-problem SCC decomposition or exact cutset/backdoor conditioning
   (not merely SCC-local rank variables or SCC-local acyclicity clauses);
2. a modern native CaDiCaL 2.x/direct engine applied to the **current eager
   arc-acyclic one-shot CNF**, with proof-telemetry comparison against Glucose4
   (the old `cadical195` test used the earlier lazy completion/CEGAR formula);
3. conditionally, a bounded Clingo-first/native-second or parallel exact
   portfolio, but only if a deterministic budget/shape contract can predict
   enough remaining time; the naive broad routing predicate already failed.

The first two are actual new mechanisms. The third is new orchestration over
known solvers, not a new solver, and is not automatically viable under the
current 10-second campaign budget.

## Inventory by mechanism family

### 1. Complete-plus-stable Clingo multishot

Primary lineage:

- `3545b633954cb091739f92ad2529552ed4716d25` — first ABA stable ASP
  encoding;
- `466d38da013cbdbcb89974e306b8720efd74df5d` — L21/TPLP multishot
  `pi_com` control and stable add-on;
- `0ac957f6dfefc8b9cdc23f179f789c71a194c73c` — route ABA stable witnesses
  through multishot Clingo;
- current historical ref containing the lean-fact refinement:
  `experiment/aba-direct-stable-witness` at
  `37148edaffdd40f4e5c7f3292ad0ac05d4143492`;
- `75d15642ce9423bb304fb3993f67f014706ed42a` on
  `exp/direct-asp-sparse-narrow-routing` — production routing experiment;
- `a18e92effdd7cf1f74dc128a30b409f184b3e508` on
  `exp/aba-se-st-clingo-solver-shape` — retained profile record.

Semantic scope: finite ordinary flat ABA, single stable witness or exact
no-witness result. The stable query uses the complete module plus
`:- out(X), not defeated(X).`; the same multishot owner also supports complete
and preferred tasks.

Operational result: the May 20 sparse route moved a known row to Clingo and
improved the 10x10 fixture from 5/20 to 9/20. On the later five-row SE-ST hard
cohort it solved 0/5 at 30-45 seconds. Real-worker profiles placed 2,450 and
2,416 samples in `clingo.Control.solve`, with add/ground/encoding tiny. On the
current 2023 UNSAT row the automatic Clingo path has 302/384 principal samples
in solve.

Disposition: **kept/current** and still the live baseline on the campaign
timeouts. It is neither dead nor an unexplored encoding.

### 2. Direct stable-only ASP

Two separate implementations exist.

First lineage on `experiment/aba-direct-stable-witness`:

- `f8658678a3b867ac44b82416282c12dee9b83f1e` — add direct stable helper;
- `bea8d779ddfa99778d01c95e442e7ae001a9575a` — use it;
- `94bf528c8d44d8058a1193d98d6c50dd1f373904` — remove helper;
- `c8eaaf63d3ff3b39af860454c576df0c8a4e0fc9` — restore the multishot
  complete-plus-stable path.

Second, explicitly profiled lineage:

- ref `exp/aba-se-st-direct-stable-encoding` at
  `c33e33ce8b2b536308bb7514eff4459b41a22281`;
- `541ccc5`, `a1e27a7`, `4b6ee26` — page-image semantics gate, red contracts,
  and direct stable-only resource/route;
- `4deb85d5c10799138cef67c7596c2fb677ffb0e6` — diagnosed record promoted
  without the production delta.

Semantic scope: ordinary flat ABA SE-ST only; exactly the `pi_common` support,
conflict-free, and every-OUT-defeated conditions, deleting the undefeated
closure used by complete semantics. Correctness contracts passed.

Operational result: 0/5 solved; five timeouts at 45 seconds. The direct path
had 2,440 samples in `clingo.Control.solve` versus 2,450 for the old path;
setup stayed tiny. Those numbers and the ignored raw-profile artifact path are
reported by the committed experiment record at `4deb85d`; the raw profile file
is not itself a Git object and is not being substituted for the committed
record.

Disposition: **reverted/abandoned, diagnosed no-go**. The campaign's H2
“leaner stable-only ASP” premise was explicitly corrected as invalid in
`6929ab74d83ac8ea83a06200204b744e722442a0`. Dead unless new evidence first
invalidates the unchanged-search diagnosis.

### 3. Clingo configurations, heuristics, lookahead, and redundant propagation

Refs and records:

- `exp/aba-se-st-clingo-stats-option-sweep` at
  `ff5f8b356d0508847e19cebb223e783b5ae3a481`;
- `exp/aba-clingo-timeout-diagnostics` at
  `d859d371965bf2c76af691f47dd46a3125cc8b20`;
- `exp/aba-se-st-option-stats-resweep` at
  `95afd16f83d243905e183008605beda61c1d5cc3`;
- `exp/aba-se-st-unit-mechanism-profile` at
  `3a287f75feb427c36c9e8fda341cd8d8707d66c4`;
- `exp/aba-se-st-lookahead-isolation` at
  `a87f6ce65f0d68da9b0636030cfc7e2484b76c77`;
- `exp/aba-se-st-defeated-out-propagation` at
  `52ac35bda7e2872f57f8bded20b2aa69f8df081a`;
- current campaign commits `dd95143`, `b2971e2`, and
  `56a946eed4845f3190a4e6be9200cc834c1b0e3a` for the July 11
  default/handy/crafty/trendy SE-PR discriminator.

Semantic scope: no semantic change except the defeated-to-OUT redundant rule;
all are ordinary flat ABA Clingo searches. The May sweep directly covered
SE-ST; the July sweep covered the current hard SE-PR row.

Operational results:

- frumpy/jumpy/tweety/handy/crafty/trendy and
  Berkmin/Vmtf/Vsids/Unit/None: 0/5 SE-ST at 40 seconds;
- Unit and `Vsids + --lookahead=atom` collapsed choices/restarts by roughly
  three orders of magnitude but still consumed the full 39-second solve
  budget and produced no model;
- the Unit real-worker profile remained opaque inside `Control.solve`
  (2,454 samples versus 2,446 baseline);
- `out(X) :- defeated(X).` worsened the representative from 511/48,983
  choices/conflicts to 541/49,851 and remained a timeout; source delta was
  abandoned;
- on the current SE-PR row, fastest `trendy` median was 9.759 seconds and every
  arm retained the same 4/1/3/3 call/iteration/refinement shape; zero arms met
  the preregistered gate.

Disposition: diagnostic timeout/statistics plumbing is **kept/current**;
option/heuristic/propagation route changes are **no-go**. A generic built-in
configuration sweep is superseded. The exact 2023 SE-ST UNSAT row was not run
through every configuration, but history supplies no mechanism-level reason to
spend a campaign probe repeating the same generic family.

### 4. Native Z3 ranked closure and rank variants

Primary commits/branches:

- `57f82959aa41900cf43dd74775e96b8c6f7aa05e` — integer-rank diagnostics;
- historical `experiment/aba-stable-boolean-rank-ladder` — Boolean closure
  ladder (branch name retained in the matrix; no visible current ref);
- historical `experiment/aba-stable-support-sat` — materialized supports (no
  visible current ref);
- `57a5c989856d82c570e7fa0be1e2169e5c9a0a11` — bit-vector ranks promoted;
- historical `experiment/aba-stable-scc-bitvec`, result recorded by
  `1b01949f60ce84a6e271621b7dfefcd977f10706`;
- `7f472b4fd624156e305bc2c5be362a7d89011bf4` — later ranked-Z3 stable owner;
- `4aaefd37175e7558338a1d50af862a1329887435` — delete production-dead
  bit-vector encoder while retaining live Int ranks;
- `exp/iccma2023-aba-600-stable-sat-route` at
  `6d2d1131162d187c614e6684b79717ee2825b70d` — current campaign N1.

Semantic scope: exact flat-ABA stable witness using founded Horn closure.
Integer, bit-vector, Boolean-ladder, and SCC-local rank encodings differ only in
how founded derivability is represented.

Operational results:

- integer ranks: 4,099 assertions, 500 Int ranks, Z3 `unknown` after 60.04 s;
- Boolean ladder: 251,100 assertions/251,050 Boolean vars, 92.50 s build, then
  `unknown`; rejected on construction;
- support materialization: >10 s build and an earlier unbounded run reached
  about 25 GB;
- bit-vector ranks: 3,649 assertions, SAT in about 7.77 s on the historical
  target, 6/16 manifest; promoted, then later deleted as production-dead;
- forced literals plus bit-vector solved but did not improve bit-vector-only;
- SCC-local bit-vector ranks regressed Z3 check from about 7.77 to 11.80 s;
- current 600-assumption forced-SAT route spent 391/399 samples constructing
  ranked closure and did not reach Z3 solve within the probe.

Disposition: integer-ranked Z3 remains a live explicit route but is rejected
for the current campaign shape. The historical alternative rank encodings are
**dead/superseded** for retry purposes. “SCC decomposition” in the matrix was
only SCC-local rank encoding, not full component solving; that distinction is
important for the novel-candidate section.

### 5. Native completion CNF, lazy loop CEGAR, and clause/seed refinements

Main/branch lineage:

- `60680444a1b6f540384e8fe29c218783c2681ae6` and
  `d01b696b0ca1cf296db134d5a5e814a2ebdcdda1` — native stable SAT backend
  and structural route;
- `47deb57055d9ac9a7beaeac156ab152d0e61b4d7` and `d65abf92` — loop
  formulas/component learning;
- `612a385` then `ed6b06d` — ranked closure added and reverted;
- ref `exp/aba-sparse-narrow-learned-sat` at
  `0b36c553666d111bd7e10b7120a9889797034be4`;
- completion route commits `dd9667e`, `5512441`, `7886f75`, `721a967`,
  `c1f8c4d`; result records are committed on `main`;
- `c1cd687` small support nogoods kept on the experiment baseline;
  `51afae5` extended nogoods rejected;
- `6a09fe4` greedy stable seeds rejected;
- `0936d01`/`680eccf`/`a82c413` SCC-local founded levels added, narrowed,
  removed;
- `cd2fd22`/`9cd40ce` static SCC loop preload added/removed;
- `96e25cd`/`368ed45` support-derived phases added/removed;
- `633b72a`/`9f3e827` support-core reduction added/reverted;
- `bd9cf3b`/`105da14` CaDiCaL inprocessing added/reverted.

Semantic scope: exact stable witness over completion variables plus
foundedness/loop constraints; sparse/narrow shape route. Some branch records
also exercised SE-PR through a stable-first shortcut.

Operational result: the strongest completion-SAT branch baseline reached 4/5
focused rows; the remaining row was dominated by PySAT/CDCL solve (`897`
samples), not construction. The main Glucose4 hard-row profile solved in
151.84 s with 150.96 s exclusive in `pysat.solve`; the last two refinement
solves dominated (`53.18 s`, `102.73 s`). Projected-assumption SAT was a true
profiled no-go: it retained a 321-sample SAT stack and added substantial
coverage/closure/candidate work. Most individual clause/seed/phase refinements
were reverted after gate regressions; several lack mechanism-level profiles
and must be described as promotion no-go, diagnosis incomplete, rather than
universal impossibility results.

Disposition: native SAT infrastructure/fixedpoint validation and some guarded
loop/pruning pieces are **kept/current**. The general learned route and its
failed refinements are **abandoned/superseded** by completion SAT and then eager
acyclicity. Another wrapper, seed, phase hint, static loop preload, support-core
shrink, or generic inprocessing pass is not genuinely novel.

### 6. CaDiCaL and IPASIR-UP

Refs and commits:

- `exp/aba-sparse-narrow-cadical195-engine` at
  `7e39df8c49bddbdb3773d4d081081e158e344e68`;
- `exp/ipasir-up-overhead-probe` at
  `b910d05e4534d9b99857d1b365b99cc11051e175`;
- `exp/ipasir-up-model-only-probe` at
  `c6846dc207fbc9aecc653ab009618f5c63fdccfe`;
- `exp/aba-sparse-narrow-ipasir-check-model` at
  `90a9f1f3cfae861a818be92d20ed07f6e2635f24`.

Operational results:

- CaDiCaL195 engine-only: 134.84 s versus Glucose4 144.83 s, but more checks
  and loop formulas; profile still raw CDCL solve; not promoted;
- observe-all no-op propagator: 3.36x ABA-like overhead; killed;
- check-model-only synthetic: 1.27x overhead; survived feasibility;
- real check-model callback: timeout beyond 245 s; profile moved into expensive
  Python unsupported-loop discovery and formula construction inside the
  callback; abandoned.

Cross-semantic branch evidence:

- `exp/iccma-aba-dcco-100ba-acyc` at
  `f21c22f89e934cdf9e149b582ed0e33214bcd067` contains
  `9019603` lazy CNF and `20506d2` CaDiCaL195 observed-edge propagator
  prototypes for **DC-CO**, not SE-ST;
- the lazy DC-CO prototype needed 101 cyclic candidates on the fast row and a
  39.43-second first SAT model on the hard row;
- the propagator solved both rows but required 53k-81k Python callbacks and
  was far slower than external `100ba-acyc`.

Disposition: PySAT-level IPASIR callback designs are **profiled no-go** as
implemented. The DC-CO branch proves capability, not SE-ST performance, and
cannot be substituted for an SE-ST experiment. A C/C++ propagator is not
identical to these Python callbacks, but it needs a new ownership/integration
case rather than being called “untried IPASIR.”

### 7. Eager acyclicity: arc cycles and SAT-VE

Arc lineage:

- ref `exp/abcgen-arc-acyc` at
  `b90ebe09a4413a0abb9390370705ed6ce9415b94`;
- `b446dfb` derivation, `08e19cd` first edge-cycle CEGAR,
  `9ca0b56` eager all-cycles iteration, record `b90ebe09`;
- this ref is an ancestor of current HEAD.

SAT-VE lineage:

- ref `exp/aba-satve` at
  `777c5ea41c9270c639eb68cab1308a9cd9598876`;
- implementation commit `39feffec994fb3dfe850dbbc8d5f957990210011`;
- branch is not an ancestor of current HEAD.

Semantic scope: exact stable foundedness. Arc acyclicity selects an acyclic
justification graph inside literal SCCs; SAT-VE replaces explicit cycle clauses
with vertex-elimination pair/transitivity clauses.

Operational results:

- eager arc encoding removed the growing loop entirely: c25 changed from 12
  growing solves totaling 178.3 s to one 56.0-second solve; an SE-PR c25 cell
  flipped at 65.3 s; c35 remained one 522-second-scale CDCL solve;
- SAT-VE built in <=0.65 s and was exact, but c25 was 275.6 s versus arc 63.1
  s, and c35 was comparable-to-worse (648.7/757.7 s); no route was wired.

Disposition: eager arc is **kept/current**. SAT-VE is a **measured routing
no-go**, retained only as a selectable branch encoding. More acyclicity
encodings are not evidence-directed for the current c35/UNSAT walls: two very
different complete acyclicity mechanisms converged on CDCL hardness, while
encoding build was subsecond.

### 8. Preprocessing, supports, kernels, and forced literals

Lineage:

- `e0397de` plus reverts `3db2924`/`6873dfa`, recorded by `4a34b76` — early
  forced-grounded preprocessing regressed all 11 SE-PR rows;
- `bba03f1230a1eadc6251ab5f2efdd1cf07ddd015` — assumption-kernel stable
  shortcut;
- `e54facfa878c5c45c13440a131b54c9b11c99b3` — well-founded grounded
  reduct plus persistent ranked-Z3 preferred kernel;
- `a6bb30c5c4d584f7274974f4b261cd00b7eec636` — bypass stable support
  preprocessing;
- ref `exp/aba-simplify-stable-budget` at
  `5dd6a0314c821524d593e967dae45b5786696e4f`, with kept fixes
  `8a934dc` and `23c6856`;
- current campaign preprocessing kill at
  `f701c2f19d7d8d6f770b233450c639c2786a7a14`.

Operational results: the July simplifier fix replaced exponential minimal
support enumeration with Horn closures and stopped emitting unused support
facts to Clingo, improving the 2025 SE-ST slice from 225/320 to 241/320 with no
lost rows. That mechanism is **kept/current**. On the current 600-assumption
development pair, however, the existing reduct fixes 0 assumptions and removes
0 rules: residuals remain 600/600 and 7,867/7,867 or 7,699/7,699. Core-fact
encoding is already active.

Disposition: support-free core facts, grounded reduct, kernel shortcuts, and
forced-literal/grounded preprocessing have all been tried. Stronger fixed-core
preprocessing would be new only if it proves a new necessary-condition theorem
and strictly shrinks a hard framework before solve; relabeling the current
identity reduct is not a candidate.

### 9. Decomposition and conditioning

What was actually tried:

- SCC extraction and SCC-local diagnostics;
- SCC-local bit-vector rank variables (11.80 s versus 7.77 s global bitvec);
- SCC-local founded levels (removed);
- static SCC loop preload (removed);
- SCC-local arc-acyclic justification (kept and useful);
- exact ABA decomposition planner/composition commits `3536db3` and
  `dff109c` for **preferred/complete PrefSat products**, not SE-ST;
- DC-CO query-cone/routing work on `exp/iccma-aba-dcco-100ba-acyc`, a
  different task.

What was not found in any committed ref: an exact SE-ST solver that decomposes
the whole ABA stable problem into independently solved SCC residuals with a
proved composition rule, or conditions on a measured small cutset/backdoor and
solves the residual components. The matrix's phrase “SCC decomposition” refers
to SCC-local bit-vector ranks, not this full mechanism.

Disposition: **full stable decomposition/cutset conditioning is genuinely
untried**. It is also repeatedly named as the evidence-directed next target by
the arc/SAT-VE records. It is not automatically promising: the current 2023
hard shape needs a committed structural measurement showing more than one
useful component or a small separator.

### 10. Routing and portfolios

Successful/kept routing:

- `experiment/aba-c1-stable-route` at
  `63f0a5b28116adc91d4c9090e9844146c842f972`: large dense C1 moved to SAT,
  auto 21.34 s versus ASP timeout;
- `exp/direct-asp-sparse-narrow-routing` at `75d15642...`: sparse stable
  moved to Clingo, 5/20 -> 9/20;
- `exp/aba-sest-clingo-route-v2` at
  `024b65ca2308b486fe2735fddc8a4349384ad302` and integrated record
  `cc50c4a001b56af1747b295bb84fc5eabb597bf1`: restrict SAT override to
  sparse-narrow, +10 solved and no losses;
- simplifier follow-up `5dd6a031...`: +16 additional solved.

Failed/unpromoted routing:

- `exp/aba-sest-sparse-route` at
  `52aa965a9078aac78e741f6aea48d6a0282b74f3`: sparse-narrow-only routing
  flipped the t120 c25 row but lost 16 change-attributable t15 rows and
  regressed common time 11.90%; killed;
- `exp/iccma-aba-dcco-100ba-acyc` routing discovery: 16/20 DC-CO rows solved,
  but the best SCC-size guard over-rejected known solved rows; not promoted and
  semantically out of SE-ST scope;
- current 2023 forced native route N1: timeout, bottleneck moved to ranked
  construction;
- stable-first preferred shortcut: current hard SE-PR framework has no stable
  witness, so no shortcut result exists.

Disposition: shape-based routing is **kept/current**, but every broad predicate
named above has been measured. A budget-aware sequential or parallel portfolio
has been recommended after the sparse-route kill but no committed
implementation/probe was found. It is conditionally novel orchestration, not a
new solving mechanism.

### 11. Exact no-stable/UNSAT proof on the current campaign row

Records:

- `exp/iccma2023-aba-600-stable-sat-route` at
  `6d2d1131162d187c614e6684b79717ee2825b70d`;
- `experiments/2026-07-11-iccma2023-aba-stable-base-unsat-screen.md`, record
  commit `5f75a7cdd96f7f08b4665fb3772d60cf650d835c`.

Exact result: `aba_2000_0.3_10_10_0.aba` SE-ST has no stable extension. The
rank-free/native-CNF base formula is already UNSAT without cycle blocking;
build took 0.56 s and the proof took 46.12 s. This is stronger than a timeout
classification: removing foundedness does not produce a model, so the complete
formula is also UNSAT.

Disposition: the base-UNSAT precheck is **negative** as a front-end because a
46-second proof cannot precede a 5-10-second worker. It also kills the claim
that rank removal alone fixes the row. A new candidate must shorten the UNSAT
proof itself or decompose it; it cannot merely move construction cost.

## Reconciliation of current campaign suggestions

| Suggestion | Historical verdict |
|---|---|
| H1 Clingo configuration/portfolio | Built-in config/heuristic families were exhaustively negative on five SE-ST rows; July current-row config triage was also negative for SE-PR. The exact SE-ST row/config cross-product is technically unmeasured, but another generic sweep is superseded and explicitly discouraged by the ledger. A true multi-engine portfolio is distinct and untried. |
| H2 lean stable-only ASP | Exact implementation already exists at `4b6ee26`; 0/5 and 2,440-versus-2,450 solve samples; abandoned. Invalid premise. |
| H3 CEGAR re-grounding churn | This is SE-PR evidence, not an SE-ST attempt: the hard preferred row is only 4/1/3/3, with 968/1,043 samples in solve and 3 in refinement grounding. Killed at `9873b47`; batching preferred-refinement grounding cannot move that metric and must not be relabeled as stable work. |
| H4 support-free/core-fact or stronger current reduct | Core facts and grounded reduct are production. On hard rows the reduct is identity. The suggestion as stated is already implemented; only a new theorem-backed reduction is novel. |
| H5 rank-free closure | Native rank-free base formula already builds in 0.56 s and proves UNSAT in 46.12 s. Rank deletion moves but does not shrink the bottleneck. Killed unless a materially different formula targets proof complexity. |
| Global max-cardinality preferred witness | This is also SE-PR evidence, not an SE-ST mechanism. The exact one-shot Lehtonen `pi_com` construction with `#maximize`, proved-optimum waiting, and single-witness return was implemented on `experiment/aba-asp-saturation-preferred` (`fe1c317`, `aa56b7c`, `b6c9b1d`; failure record `408f4b0`). Semantic gates passed, but T1/T3/T5/T6/T8 timed out on `auto`, `asp`, and `sat`; the earlier untouched-candidate premise was invalid. |
| Direct stable encoding | Tried twice; latest exact/profiled version abandoned. |
| Native SAT/Z3 engine swap | Glucose4, CaDiCaL195, integer ranks, bitvec ranks, and completion CNF all measured. Modern CaDiCaL on the current eager-arc one-shot formula is the only materially different untried engine/formula pairing. |
| Lazy CNF/IPASIR | Model-level lazy loop clauses, check-model IPASIR, observe-all, and observed-edge Python propagators have committed negatives. A native C++ propagator is different implementation ownership, but requires a new integration case. |
| Acyclicity | Loop formulas, SCC levels, eager arc cycles, and SAT-VE all tried. Current wall is one CDCL solve, not encoding build or CEGAR count. |
| Decomposition/cutset | Only local encodings and non-SE-ST products exist. Full stable decomposition/backdoor conditioning remains genuinely untried. |
| Broad sparse routing | Tried and killed by 16 lost t15 rows. A portfolio or finer evidence-based predicate is required. |

## Only genuinely novel SE-ST candidates

### Candidate A: exact full-problem SCC decomposition or cutset/backdoor conditioning

Why novel: no visible committed ref composes exact stable witnesses/UNSAT
across ABA SCC residuals or branches on a measured small separator. Existing
SCC work changes local encoding only.

Required evidence before a probe:

1. On the current 600-assumption UNSAT dev row and the c35 one-solve wall,
   commit deterministic telemetry for the exact graph being decomposed:
   component count, largest component, separator/backdoor size, cross-component
   contrary/rule dependencies, and residual size after conditioning.
2. State and test the composition theorem for ordinary flat ABA stable
   semantics, including no-stable-extension propagation and empty/factual
   attackers. Do not substitute AF SCC recursion or preferred-product
   composition.
3. Add a normally running operational contract that fails on baseline and
   requires strict largest-residual reduction or a bounded branch count before
   any full benchmark.
4. Kill before implementation if the hard row is one inseparable component and
   no small separator exists.

### Candidate B: modern native CaDiCaL 2.x/direct engine on the current eager-arc one-shot CNF

Why novel: `cadical195` was tested on the older completion/lazy-loop CEGAR
formula; SAT-VE used Glucose4; the current eager-arc formula is one solve with
zero loop refinements. No committed ref tests a current CaDiCaL 2.x engine on
that exact formula.

Required evidence before a probe:

1. Confirm an owned, callable engine/version and whether proof/search
   statistics are accessible without Python per-assignment callbacks.
2. Freeze the exact current eager-arc CNF blob/telemetry and compare the same
   CNF, seeds, phase policy, timeout, and worker path against Glucose4. Engine
   must be the single variable.
3. Add an operational contract over one-solve status and solver statistics;
   semantic properties alone are insufficient.
4. Profile the real worker/solver process if the metric misses. Do not infer a
   mechanism from a timeout or from the historical `cadical195` result.

### Candidate C, conditional: bounded Clingo-first/native fallback or parallel exact portfolio

Why only conditional: no committed portfolio implementation was found, and the
broad sparse route proved complementary wins exist. However, the current frame
allows only 10 seconds per row, so sequential fallback may have no remaining
budget and parallel racing can change CPU contention, violating the calibrated
baseline.

Required evidence before a probe:

1. A deterministic pre-solve contract must identify rows where the first arm
   is cheaply decisive or where enough budget remains for the second arm.
2. Pin total CPU/process budget, cancellation behavior, witness validation,
   and UNSAT/no-witness authority. A timeout from one arm is not an UNSAT
   certificate.
3. Calibrate sequential and parallel overhead under `--jobs 1`; do not compare
   a multicore portfolio against the single-worker frame without reframing the
   metric.
4. If no shape/budget contract predicts a win on at least one current timeout,
   do not spend a probe.

## Final disposition

No other current suggestion survives the history check as genuinely novel.
In particular, direct stable ASP, generic Clingo options/lookahead, rank-free
closure, support-free encoding, grounded preprocessing, rank encodings,
loop-formula tweaks, Python IPASIR callbacks, eager arc acyclicity, SAT-VE,
and broad sparse routing all have committed evidence and must not be reopened
without new evidence that contradicts their recorded failure mechanism.

The H2 and global max-cardinality invalidity corrections are both incorporated
here. H2 is prior SE-ST work and is dead as stated. Global maximum-cardinality
preferred solving is prior SE-PR work and must not be mislabeled as an SE-ST
attempt, but it is still a dead cross-campaign candidate family rather than
untouched territory.

## Inventory-freeze selection

**Selected next target family: directed ABA SCC-recursive exact
conditioning/decomposition.** It is the single selected family because it is the
cheapest common falsification target across both hard framework shapes: one
executable semantic contract can kill an invalid composition rule before any
shape measurement, while a valid rule would create the precondition for later
SE-ST and SE-PR residual-shape contracts. The history above distinguishes it
from SCC-local ranks or acyclicity clauses, the already-tried undirected
preferred product, and AF SCC recursion. That distinction establishes only
novelty, not semantic composition or operational usefulness.

The exact next executable semantic composition contract question is:

> For every finite ordinary flat ABA framework in the bounded generated test
> domain, does a directed assumption-dependency/attack SCC recursion with
> explicit predecessor-boundary conditioning return, after lifting, exactly the
> same stable-extension set and exactly the same preferred-extension set as the
> direct semantic oracles, in both directions, including cross-SCC rule and
> contrary dependencies, empty and factual attackers, and branches with no
> extension?

This question must be encoded and answered before any hard-row shape
measurement, operational contract, solver call, benchmark, or source slice.
Candidates B and C remain unselected; this freeze does not authorize work on
them.
