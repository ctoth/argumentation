# Bug audit checkpoint - 2026-09-26
- Reproduced five bugs at 978b10edb8eaf106f64cd760cfeedce1c3cbb237; opened ctoth/argumentation issues #3 through #7 with standalone reproductions.
- Findings: disconnected stable MC acceptance, reserved ADF atoms, dynamic attack loss, mixed-relation preferred extensions, and NaN weighted budgets.
- Existing framework/dynamics/ranking/gradual suite: 246 passed, 1 xfailed; production code unchanged and pre-existing untracked work preserved.
- Corrected selected Hunter 2017 paper notes against page images; this was a targeted check, not full-paper reverification. No blocker or confirmed dependency bug.
- Next: verify posted issue bodies and the notes diff, then report links and validation limits. Leave this checkpoint uncommitted.

## Expanded audit checkpoint
- User clarified target is 50+ issues; continuing from five posted findings, with dependency issue authorization.
- Fifteen additional standalone reproductions confirmed: epistemic, revision, gradual, approximation, sensitivity, and I/O defects.
- Batch-one issue creation is running; reproduction scripts, outputs, and post ledger are in the system temp directory argumentation-bug-audit-20260926.
- Full test suite is running in session 61558; no production source edits. Existing paper corrections preserved.
- Next: finish posting this batch, investigate remaining modules, verify distinct root causes, and continue to at least 50 total.

## Timeout investigation checkpoint
- Issues #3 through #37 are posted: 35 findings; continuing toward 50+.
- User flagged the ABA timeout; isolated seeded test is progressing through hundreds of bounded cutsets rather than visibly stuck.
- Attached py-spy to real Python worker PID 168040, not venv launcher; captured 1499 samples with zero errors.
- Dominant sampled work is hashing, Horn closure, and subset enumeration; per-cutset telemetry is saved alongside the profile in the temp audit directory.
- Next: finish the timeout diagnosis, distinguish repeated oracle work from production defects, and continue correctness reproductions. Production source remains unchanged.

## Completed audit checkpoint
- Verified 51 open reproduced findings: issues #3 through #54, excluding withdrawn #20; all posted bodies contain reproduction evidence.
- The isolated 300-example ABA property test passed 1,164 cutset checks in 86.84 seconds; CI uses 600 seconds, versus the audit's 30-second limit.
- Filed the profiler-supported plain ABA Boolean attack inefficiency separately as #54: 160 closure calls versus an equivalent single-closure oracle.
- Report and complete issue index: reports/bug-audit-20260926.md. Targeted Hunter, Cayrol, and prudent-semantics paper notes updated; diff check passes.
- Production code unchanged; report, checkpoint, and paper-note changes left uncommitted. No confirmed dependency issue or remaining posting blocker.

## Broader audit checkpoint, 2026-09-27
- User challenged stopping at 51; expanding by representation and invariant coverage rather than treating that count as a ceiling.
- Reproduced ABA projection identifier collisions and a ranking counter-transitivity checker whose answer changes under argument renaming.
- Reproduced ASPIC backend disagreement on repeated rule antecedents; the comparable native ABA backend control agrees and is not a finding.
- Investigating clingo success exit codes, terminal-status validation, timeout result handling, and finite-chain ranking recursion; new findings not yet posted.
- Existing 51 open audit findings verified live; production code and preexisting workspace changes preserved.

## Broader audit results checkpoint
- Posted and re-fetched 12 additional distinct reproduced issues, #58 through #69; 63 retained audit findings in total.
- Highest-impact new finding: source ASPIC grounded semantics accepts contradictory defeasible conclusions; four generated cases grouped into #65.
- Additional defects cover Datalog binding/provenance/namespaces, ranking invariance and recursion, ABA projection identity, clingo transport, and dropped preprocessing timeout configuration.
- Existing focused Datalog/ASPIC differential/ranking-axiom tests pass: 22 passed in 8.62 seconds. New standalone reproductions and posting evidence are in the 20260927 temp audit directory.
- Updated reports/bug-audit-20260926.md with the continuation and surface inventory; no exhaustion claim, production edits, or confirmed dependency defect.

## Current-main continuation checkpoint
- Fetched origin and created detached audit worktree argumentation-audit-20260927 at 49366bf8da6557f9445b6e465076746daeabfa57; original checkout preserved.
- Current-main bounded ABA extension differential passed 960 comparisons across four semantics with preprocessing on/off.
- Query differential found false skeptical acceptance for an underivable literal with no assumptions or rules; reduced to clingo 5.8.0 symbolic assumptions on absent atoms.
- Fresh clingo controls reproduce both false UNSAT for a negative absent-atom assumption on an empty program and false SAT for a positive absent-atom assumption.
- Checking upstream issue history and preparing bounded reproductions; several prior audit issues have now been fixed, so retained findings are not all currently open.

## Dependency and paper-validation checkpoint
- Filed potassco/clingo#671 after reproducing absent-atom assumption aliasing on both 5.8.0 and latest 5.8.2 in separate installations; downstream application report is argumentation#72, one shared root cause.
- Completed 1,440 ABA skeptical queries: 48 disagreements in assumption-free cases; completed 12,086 Dung SAT/SCC bounded comparisons without semantic disagreement.
- Dung sweep exposes differential-checker false failures when valid single-extension witnesses differ; preparing separate report.
- Inspected Amgoud page images 004,006,007,008,009,010 and Bonzon 001: defense/cardinality/self-contradiction predicates weaken the cited postulates; notes also contain wrong quantifiers and burden formula.
- No production changes; paper-note corrections and reduced postulate reproductions are next.

## Current-main results and committed notes checkpoint
- Filed and verified eight additional local reports: #72-76 and #78-80; potassco/clingo#671 shares #72's root cause, so total retained distinct findings is 71.
- Reopened #16 for post-validation rounding outside an exact belief interval; extended #63 with deterministic multishot timeout-escape evidence.
- Page-image corrections across five paper notes were committed by another process as 0fad795 during review; further Amgoud corrections committed here as b255211, with LF line endings and a focused five-line replacement diff.
- Existing ranking-axiom and solver-differential tests pass: 13 passed in 2.34 seconds; new standalone reproductions fail as documented.
- Updated audit report with pinned revision, comparisons, issue links, upstream verification, commit identities, and limits; no production edits or push by this audit.

## Final verification checkpoint
- Paper-note commits are complete; the audit checkpoint file remains uncommitted as required by the checkpoint hook.
- Eight local issue bodies and one linked dependency issue body match their saved reproduction records.
- No remaining blocker; final checks will confirm commit scope, whitespace, and the original checkout's tracked-file state.
