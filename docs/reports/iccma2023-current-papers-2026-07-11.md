# Current-paper guidance for ICCMA 2023 AF and ABA performance diagnosis

## Scope and evidence standard

This report uses only the current artifacts under `papers/`. It does not inspect implementations, benchmark logs, external repositories, or the web. Consequently, every item below is a paper-supported **measurement hypothesis**, not a claim about the repository's current bottleneck. The hypotheses are intended to become executable operational contracts before implementation: route choice, solver-call bounds, candidate/range residual reduction, encoding shape, or calibrated runtime.

The strongest immediate guidance is:

1. Diagnose AF work by task shape. Do not treat preferred/range maximality, ordinary NP witness search, and polynomial reductions as the same solver path.
2. For `DS-PR`, measure an admissibility-only Fudge/CDAS route against preferred-extension growth; the paper evidence says avoiding maximization is the point of the newer algorithm.
3. For ABA, first measure how many instances are decided by the base semantics formula without acyclicity. For the remainder, compare vertex-elimination (VE) and unfounded-set (UFS) acyclicity by encoding size and propagation share, not only wall clock.
4. Keep derivation reasoning at the assumption/rule level. The paper evidence explicitly warns that ABA-to-AF translation can blow up.

## Provenance limitations

The local artifacts are not uniform:

- Explicit paper-reader/page-image provenance is present for PrefSat and ArgSemSAT (`produced_by: ... paper-reader`), and the Dvořák/CEGARTIX note explicitly says it was read from existing KR proceedings page images.
- Fudge and its IJCAI companion have paper-reader provenance and page citations.
- The full JAIR ASPforABA note and the 2025 ABA SAT note contain exact page citations, but their front matter does **not** record page-image reading provenance. Their page-specific claims are usable as current-note evidence, but any implementation depending on exact listing/formula transcription requires rereading the primary PDF page images.
- The μ-toksia note has section/table citations, not exact page citations, and no page-image provenance marker. Its architecture and reduction map are useful for hypothesis selection, but every μ-toksia-dependent implementation detail below is explicitly marked **primary-PDF reread required**.
- `papers/Lehtonen_2021_DeclarativeAlgorithmsComplexityABA/notes.md` is a compact section-cited ASPforABA summary without exact page citations. This report therefore uses the page-cited full artifact at `papers/Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/notes.md` for actionable claims.

## AF diagnosis and improvement hypotheses

### AF-1: Route polynomial and first-level tasks away from maximality loops

**Paper finding.** μ-toksia computes grounded semantics by unit propagation on the complete encoding, reduces skeptical complete acceptance to grounded membership, primes stable solving with the grounded extension, and tests stable existence before using the stage route. It creates one SAT solver per execution and reuses it through assumptions. Source: `papers/Niskanen_2020_MuToksiaEfficientAbstractArgumentationReasoner/notes.md` *(Sec. 3.1-3.2; no exact page citation in the note — primary-PDF reread required)*.

**Measurable hypothesis.** Add task-route telemetry with at least:

- selected route (`grounded`, one-shot stable, stage-via-stable, CEGAR, enumeration);
- SAT solver constructions per task (target for a μ-toksia-style execution: one);
- SAT calls per task;
- grounded lower-bound size and the number/fraction of candidate variables fixed before stable search;
- whether the stable precheck discharged a stage instance without invoking range maximality.

The operational contract is falsifiable: grounded and `DS-CO` should make no search calls; stable should record the grounded lower-bound assumptions; stage should record whether the stable shortcut fired. This does not assert that these routes are currently absent.

### AF-2: Reuse one incremental clause database across related calls

**Paper finding.** Fudge uses CaDiCaL through its C++ API because repeated satisfiability checks and counting benefit from incremental SAT. Source: `papers/Thimm_2021_FudgeLight-weightSolverAbstract/notes.md` *(p.2-p.3)*. CEGARTIX likewise uses incremental MiniSAT as its NP oracle and learns pruning clauses across refinement steps. Source: `papers/Dvorak_2014_ComplexitySensitiveDecisionProcedures/notes.md` *(pp.60-62)*. μ-toksia makes the same architectural claim, but its current note provides only section provenance: `papers/Niskanen_2020_MuToksiaEfficientAbstractArgumentationReasoner/notes.md` *(Sec. 3.1; primary-PDF reread required)*.

**Measurable hypothesis.** For every iterative AF route, record solver constructions, calls per construction, assumptions per call, learned/blocking clauses added, and cumulative clauses retained. The minimum contract is `solver_constructions == 1` for one task execution unless an explicitly measured backend limitation prevents it. Compare cold-rebuild and persistent modes on identical call sequences; the decision criterion is reduced cumulative solve time without changed answers or increased call count.

### AF-3: Diagnose `DS-PR` by separating admissible conflict search from preferred maximization

**Paper finding.** Fudge's companion algorithm CDAS decides skeptical preferred acceptance using admissible-set queries without constructing preferred extensions. It first checks whether the query can occur in an admissible set, then searches for admissible attackers and attempts to extend them together with the query; specific UNSAT outcomes decide acceptance or rejection. Each utility is SAT-solvable. Source: `papers/Thimm_2021_SkepticalReasoningPreferredSemantics/notes.md` *(p.2069-p.2072)*. The short Fudge system paper confirms that avoiding preferred maximization is its distinguishing `DS-PR` technique. Source: `papers/Thimm_2021_FudgeLight-weightSolverAbstract/notes.md` *(p.2-p.3)*.

**Measurable hypothesis.** Compare two labeled routes on the same `DS-PR` instances:

- preferred-growth/CEGAR: count candidate-to-maximal growth calls, strict-superset calls, and final preferred counterexamples;
- CDAS: count `AdmExt`, admissible-attacker, and `AdmExtAtt` calls; count stored conflict patterns; record the size of the uncovered admissible residual after each learned exclusion.

The route contract is that CDAS performs zero preferred-extension maximization calls. Promotion requires fewer total oracle calls or a smaller calibrated cumulative solve time on the target family, while preserving results. A primary-PDF page-image reread is required before transcribing `AdmExtAtt`, because the local note says the clause-level utility encodings are only summarized and the online proof appendix is absent *(p.2070, p.2072-p.2073)*.

### AF-4: Keep PrefSat as an explicit enumeration/growth baseline, not the default answer to `DS-PR`

**Paper finding.** PrefSat grows a complete extension monotonically: fix current `in` arguments, require at least one additional `in`, repeat until no strict complete superset exists, then block the preferred extension and all its subsets. Source: `papers/Cerutti_2013_ComputingPreferredExtensionsAbstract/notes.md` *(p.9-p.11)*. The same note reports that logically equivalent complete-labelling encodings materially change runtime and that `C_2` was best overall on its random AF study, with density-dependent variation *(p.5-p.9, p.13-p.15)*. ArgSemSAT similarly uses complete labellings and iterative preferred search. Source: `papers/Cerutti_2015_ArgSemSAT-1.0ExploitingSATSolvers/notes.md` *(p.2-p.4)*.

**Measurable hypothesis.** When preferred enumeration or a preferred witness is actually required, record:

- inner-loop depth and strict `in`-set growth per SAT call;
- outer-loop preferred-extension count and subsets excluded per blocking clause;
- three-valued labelling variable/clause counts;
- graph density and per-encoding solve time for any encoding comparison.

The invariant is strict growth after every satisfiable inner-loop call. A repeated `in` set is an operational failure. For `DS-PR`, PrefSat-derived growth should be separately labeled so it can be compared directly with CDAS rather than hidden behind a generic `sat` route.

### AF-5: Instrument CEGAR by candidate and range residual, not only elapsed time

**Paper finding.** CEGARTIX uses complete extensions as the preferred/semi-stable base and conflict-free sets as the stage base. For preferred semantics it searches proper supersets and learns clauses excluding subsets of a candidate. For semi-stable/stage it searches strictly larger ranges and learns clauses excluding contained ranges. Source: `papers/Dvorak_2014_ComplexitySensitiveDecisionProcedures/notes.md` *(p.60-p.61)*. Its semi-stable/stage shortcut examines ranges missing at most depth `d`, with prototype `d=2` *(p.61-p.62)*.

**Measurable hypothesis.** Each refinement iteration should emit:

- base candidate size and range size;
- strict-superset or strict-larger-range oracle result;
- number of candidates/ranges excluded by the learned clause;
- remaining query-compatible candidate count when enumerable, or a deterministic proxy such as unfixed membership/range variables;
- shortcut depth, shortcut hits, and oracle calls avoided.

The operational contract is monotone residual reduction: preferred iterations must eliminate at least the current candidate's subset region; range iterations must eliminate at least the current contained-range region. If two iterations leave the chosen residual proxy unchanged, the loop is not demonstrating the paper's refinement shape.

### AF-6: Route on extension/range shape, not small graph-distance folklore

**Paper finding.** Dvořák et al. show that many syntactic fragments recover full second-level hardness at graph deletion distance one, while bounded extension count or bounded missing range yields bounded-oracle procedures for fixed bounds. Source: `papers/Dvorak_2014_ComplexitySensitiveDecisionProcedures/notes.md` *(pp.58-60)*.

**Measurable hypothesis.** Before adding a graph-class shortcut, measure the property that can change routing: estimated/observed number of extensions, arguments outside candidate ranges, stable existence, and shortcut coverage. A route based only on being one vertex from acyclic/odd-cycle-free/unique-preferred is not supported by this paper. A useful contract is: invoke a bounded-range shortcut only when the measured missing-range bound is within its configured depth, and report the calls saved.

### AF-7: Treat ideal semantics as its own residual-shrinking algorithm

**Paper finding.** Fudge/CDIS repeatedly removes arguments attacked by admissible sets from the preferred super-core, then removes arguments not defended inside the remaining candidate; the result is the ideal extension. Source: `papers/Thimm_2021_SkepticalReasoningPreferredSemantics/notes.md` *(p.2071-p.2073)*. μ-toksia describes a related union-of-admissible plus subset-maximization route, but only section citations are present in the local note: `papers/Niskanen_2020_MuToksiaEfficientAbstractArgumentationReasoner/notes.md` *(Sec. 3.2; primary-PDF reread required)*.

**Measurable hypothesis.** Record candidate super-core size after each admissible-attack removal, then after each internal-defense cleanup, plus SAT calls in each phase. Require strict candidate shrinkage on every nonterminal iteration. Compare CDIS with any preferred-enumeration-derived ideal route by total oracle calls and residual trajectory.

## ABA diagnosis and improvement hypotheses

### ABA-1: Measure direct assumption-level reasoning against translation expansion

**Paper finding.** ASPforABA represents assumptions, indexed rule heads/bodies, contraries, and queries directly, computes forward support, and avoids materializing an abstract AF; the authors identify ABA-to-AF translation as potentially exponentially larger and empirically compare against translation-based systems. Source: `papers/Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/notes.md` *(p.289-p.290, p.297-p.302)*. The 2025 SAT paper repeats the worst-case exponential-blow-up motivation. Source: `papers/Niskanen_2025_ReasoningAssumptionBasedArgumentationSAT/notes.md` *(p.708)*.

**Measurable hypothesis.** Route telemetry should report original assumptions, sentences, rules, body literals, and any generated AF arguments/attacks. The direct route's shape contract is no materialized argument graph. If a translation route exists, select it only with an explicit expansion bound and compare `generated_arguments / assumptions`, `generated_attacks / rules`, construction time, and peak memory.

Both cited notes lack explicit page-image provenance in front matter; reread primary PDF page images before relying on exact input-fact syntax or benchmark table transcription.

### ABA-2: Give grounded, stable, complete, and preferred distinct operational contracts

**Paper finding.** ASPforABA uses a shared forward-support/conflict-free module. Stable adds the requirement that every out assumption be defeated; admissibility checks attacks from undefeated assumptions; complete additionally includes every defended assumption; preferred applies subset-maximal optimization; grounded uses an explicit fixpoint bounded by the number of assumptions. Source: `papers/Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/notes.md` *(p.290-p.292)*. Skeptical acceptance is a counterexample search whose UNSAT result means accepted *(p.290)*.

**Measurable hypothesis.** Record the selected semantic add-on and enforce:

- grounded: at most `|A|` fixpoint rounds and no general model-enumeration route;
- stable: one base witness/counterexample solve, with every non-member attacked;
- complete: counts of undefeated assumptions and defended-but-out residuals;
- preferred: explicitly labeled subset-maximization or CEGAR calls;
- skeptical: counterexample solve count and UNSAT termination.

The corrected JAIR grounded encoding supersedes the erroneous 2019 version *(p.292, p.311-p.312)*. Primary-PDF page-image reread is required before implementation because the note lacks explicit page-image provenance and the correction is semantically load-bearing.

### ABA-3: First screen with the base semantics formula; invoke acyclicity only on the residual

**Paper finding.** In the 2025 evaluation, many ICCMA23 ABA instances were already unsatisfiable without any acyclicity constraint: 216 for `DC-ST`, 289 for `DS-ST`, and 154 for `DC-CO` (therefore also `DS-PR`); these were filtered from the acyclicity comparison. Source: `papers/Niskanen_2025_ReasoningAssumptionBasedArgumentationSAT/notes.md` *(p.713)*.

**Measurable hypothesis.** Add a route counter for `base_formula_decided_before_acyclicity`, split by task and answer. Measure:

- total instances;
- base-formula decisions;
- instances passed to acyclicity;
- base and acyclicity build/solve time separately;
- residual atoms/rules/SCCs after any query cone or base simplification.

This is the highest-priority ABA diagnostic because it can reject an operationally hopeless assumption that every ICCMA23 instance needs the expensive acyclicity machinery. It is a measurement contract, not authorization to reproduce the paper's evaluation filtering in correctness runs. The note lacks explicit page-image provenance; reread p.713 before using the exact published counts as a gate baseline.

### ABA-4: Prefer VE over level encoding when level duplication dominates shape

**Paper finding.** SAT-LEVEL duplicates derivation variables through upper bound `U = |L|-|A|`; SAT-VE encodes activated derivation edges plus vertex-elimination acyclicity. On the reported data, SAT-VE used about 167k variables versus 8M for SAT-LEVEL on ICCMA23, while SAT-LEVEL suffered memory failures on most CLUSTERED instances. Source: `papers/Niskanen_2025_ReasoningAssumptionBasedArgumentationSAT/notes.md` *(p.710-p.712, p.714-p.715)*.

**Measurable hypothesis.** Before solving, compute projected level and VE variable/clause counts, `U`, rule-graph vertices/edges, fill edges, and SCC sizes. Route to VE when the calibrated projected level size exceeds the VE size/memory budget. The contract must be based on measured local encoding size, not the paper's average. Also record VE clause blow-up over the base encoding; the paper reports that this ratio varies drastically on ICCMA23 *(p.715)*.

Primary-PDF page-image reread is required before transcribing the VE constraints or treating the reported averages as exact, because the note lacks an explicit page-image provenance marker.

### ABA-5: Compare VE and UFS using clause growth versus propagation share

**Paper finding.** SAT-UFS keeps source pointers for non-circular support and propagates false for unfounded atoms; its runtime share averaged below 4% but reached 81% on some ICCMA23 instances. SAT-UFS was strong on `SE-ID`, while SAT-VE was strongest on several one-shot tasks. Source: `papers/Niskanen_2025_ReasoningAssumptionBasedArgumentationSAT/notes.md` *(p.712-p.715)*.

**Measurable hypothesis.** A VE/UFS comparison must report:

- VE fill clauses and clause/base ratio;
- UFS propagation calls, source-pointer changes, unfounded atoms found, reason-clause sizes, and propagation-time share;
- SAT decisions/conflicts/restarts and total oracle calls;
- route result by task (`DC-CO`, `DC-ST`, `DS-ST`, `DS-PR`, `SE-ID`).

A route hypothesis worth testing is VE for compact one-shot residuals and UFS when VE fill clauses exceed a calibrated threshold or on `SE-ID`; this is not yet a recommendation because the papers provide aggregate results, not this repository's route boundary. Primary-PDF reread is required before implementing the source-pointer reason clauses.

### ABA-6: Drop the defense-side derivation machinery for stable semantics

**Paper finding.** For stable semantics, the 2025 SAT encodings omit `z`, `phi_ndef`, and the `B_tau` derivation machinery because every non-member assumption is attacked. Source: `papers/Niskanen_2025_ReasoningAssumptionBasedArgumentationSAT/notes.md` *(p.711-p.712)*.

**Measurable hypothesis.** The stable route should report zero defense-side variables/clauses and compare encoding size with a generic complete/admissible construction. The operational contract is a strict reduction in variables/clauses without changed `DC-ST`/`DS-ST` answers. Primary-PDF reread is required before exact clause transcription.

### ABA-7: Reuse complete semantics as the abstraction for beyond-NP tasks

**Paper finding.** The 2025 SAT systems adapt μ-toksia's iterative algorithms: `DS-PR` uses CEGAR over complete extensions not containing the query, and `SE-ID` first finds arguments attacked by complete extensions before finding the unique subset-maximal complete extension in the complement. All four acyclicity variants can serve as the abstraction solver. Source: `papers/Niskanen_2025_ReasoningAssumptionBasedArgumentationSAT/notes.md` *(p.708, p.713)*.

**Measurable hypothesis.** For `DS-PR`, record abstraction calls, candidate complete-set sizes, strict-superset counterexample calls, learned exclusions, and residual query-compatible complete candidates. For `SE-ID`, record the attacked-union candidate size after each call, complement size, and final subset-maximization calls. Compare VE and UFS under the identical abstraction call sequence so acyclicity cost is not confounded with algorithmic call count.

The 2025 paper reports SAT-VE solving about 50% more CLUSTERED `SE-ID` instances than ASPforABA while ASPforABA remained stronger on `DS-PR` until roughly 800 seconds *(p.714-p.715)*. Those aggregate observations motivate separate task routing, but do not establish the current repository's boundary. Primary-PDF reread is required before using the numerical result as an acceptance threshold.

### ABA-8: Preserve corrected grounded and ideal algorithms

**Paper finding.** The JAIR paper states that its preliminary 2019 grounded encoding was erroneous and supplies a counterexample; it also corrects Dunne's ideal algorithm, whose original defense check could return a non-ideal set. Source: `papers/Lehtonen_2021_DeclarativeAlgorithmsComplexityResults/notes.md` *(p.292-p.293, p.311-p.313)*.

**Measurable hypothesis.** Any performance experiment touching grounded or ideal must first include correctness contracts for the cited counterexample shapes. Grounded telemetry should show monotone `in` growth across at most `|A|` rounds. Ideal telemetry should show strict candidate shrinkage under all relevant attackers, not only attackers wholly outside the candidate. Performance promotion is invalid if either correction is bypassed.

Primary-PDF page-image reread is mandatory before encoding these corrections because the local note has no explicit page-image provenance and summarizes, rather than reproduces, the appendices.

## Recommended measurement order

This order follows the paper-supported decision points and avoids mixing source slices:

1. **Freeze task/family telemetry.** For every ICCMA23 AF/ABA run: task, answer, route, solver constructions/calls, per-call time, and deterministic residual-shape metrics.
2. **ABA base-formula screen.** Measure how many target instances terminate before acyclicity and the exact residual passed onward.
3. **ABA acyclicity shape.** On only that residual, measure projected/actual LEVEL, VE, and UFS costs; compare VE clause ratio with UFS propagation share.
4. **AF `DS-PR`.** Compare preferred-growth/CEGAR and admissibility-only CDAS using identical instances and explicit oracle-call categories.
5. **AF range tasks.** Instrument CEGAR residual shrinkage and bounded-range shortcut coverage.
6. **Ideal tasks.** Measure candidate-super-core/attacked-union shrinkage separately for AF and ABA.

Each experiment should end in either a kept, measured improvement or a full revert. A missed wall-clock target without the solver-call and residual-shape evidence above is only a promotion no-go with incomplete diagnosis.

## Primary-PDF rereads required before implementation

The current collection is sufficient to choose measurements, but not to safely transcribe every algorithm. Reread page images for:

- μ-toksia Sec. 3.1-3.2: exact assumption usage, grounded priming, stage stable shortcut, CEGAR details, and ideal loop; the note has no page citations.
- Fudge/CDAS p.2070-p.2073: `AdmExtAtt` quantification and omitted proof appendix before implementing the admissibility-only route.
- ASPforABA p.290-p.296 and p.311-p.313: exact ASP listings plus corrected grounded and ideal behavior; the full note lacks an explicit page-image provenance marker.
- ABA SAT p.710-p.715: exact VE/UFS clauses, propagator reasons, evaluation filtering, and table values; the note lacks an explicit page-image provenance marker.

No primary-PDF reread is needed merely to add the diagnostic counters and contracts described here, provided they are treated as measurements and not as claims that a specific algorithm is already correct or faster.
