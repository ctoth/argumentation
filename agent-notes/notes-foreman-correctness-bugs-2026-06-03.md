# Foreman: correctness-bug gauntlet (2026-06-03)

Mandate (from Q): fix the 4 verified correctness bugs. Coder/verifier gauntlet with
**codex as external verifier**. TDD. Hypothesis-first. Then discuss the other issues.

Branch: `fix/correctness-bugs` (coder #1 creates it off main). All work committed there.

## Method per bug
1. Coder (claude general-purpose): state hypothesis → write a test that FAILS proving the
   bug (red) → minimal fix → test passes (green) → run related tests → precommit → commit →
   report with commit hash + the red/green evidence.
2. Verifier (codex, external-agents protocol): independently confirm the test genuinely fails
   without the fix and passes with it, the fix is correct + minimal, no regressions, hypothesis
   sound. Writes verdict to reports/. Foreman reads verdict before next bug.

Scope discipline: correctness only. De-duplication / refactors are "the other issues" — note them,
do NOT do them now.

## The 4 bugs (verified earlier, file:line)
- BUG-1 timeout: `iccma_af.py:260` subprocess.run(timeout=) has no `except TimeoutExpired`;
  sibling `iccma_aba.py:201` catches it. Fix = mirror the sibling. → coder: af-timeout
- BUG-2 collision: `aba_asp.py:712` `_reject_id_collisions` uses `len(m)==len(set(m))` (always
  True for a dict). Guard dead; colliding ids silently overwrite. Called at 53-54. → coder: aba-collision
- BUG-3 recursion: `af_sat.py:1603` + `labelling.py:319` two recursive `_is_acyclic` DFS;
  RecursionError on long chains. Fix = make iterative (in place, both). → coder: acyclic-recursion
- BUG-4 epistemic: `epistemic.py:633` fixed 10k-iter projection `break`s on non-convergence and
  returns infeasible point as valid (callers at ~578). HYPOTHESIS — coder confirms first. → coder: epistemic-converge

## Status
- [x] BUG-1 timeout    — coder: a8bd376 DONE | verify: codex PASS (reports/af-timeout-verify-report.md)
- [x] BUG-2 collision  — coder: cec4139 DONE | verify: codex (fix sound) + adjudication (no regression: 7 failures were env-only, all pass on HEAD & base under uv)
- [x] BUG-3 recursion  — coder: 986e857 DONE | verify: codex PASS (reports/acyclic-recursion-verify-report.md; uv run, no spurious failures)
- [x] BUG-4 epistemic  — coder: e86975d DONE | verify: codex PASS (reports/epistemic-converge-verify-report.md; old code returned violation-0.3 point silently, now raises; uv run clean)

## Log
- BUG-1 coder (agent ab9c52e1) committed a8bd376 on branch fix/correctness-bugs. Report claimed
  pyright clean + GREEN. **HARD STOP**: harness diagnostics contradict it — `_timeout_stream` is
  NOT defined in iccma_af.py:273-274 (reportUndefinedVariable), so the committed fix would NameError
  on the timeout path. Report is not trustworthy. Bounced back to same agent with the evidence to
  actually define the helper, paste REAL pytest + pyright output, and clean unused-param warnings in
  the test file (lines 272/288/308/330/359). NOT sent to codex until real-green.
- BUG-1 coder resumed, pushed back with TOOL OUTPUT (not assertion): `_timeout_stream` IS defined at
  iccma_af.py:451 (forward ref, valid Python); committed HEAD blob contains it; `python -c import`
  works; test `1 passed`; project pyright (basic mode) `0 errors`; adapter suite `39 passed, 2 skipped`.
  The editor diagnostic was a stale mid-edit snapshot (taken before the def at L451 was written). The
  unused-param warnings are editor-only stricter-mode noise — those kwargs (capture_output/text/check)
  MUST be named because the adapter passes them; prefixing `_` breaks the call. Accepted that reasoning.
  Coder added commit fda08fd (re-verification doc); fix commit a8bd376 unchanged.
- Decision: do NOT take coder's word as final either — dispatching codex (external verifier) to
  adjudicate a8bd376 independently: confirm _timeout_stream defined, except block mirrors sibling,
  test is a TRUE red-without-fix regression test, green now, no regressions, pyright clean.
  Prompt: prompts/af-timeout-verify.md → reports/af-timeout-verify-report.md.

- BUG-1 VERDICT: codex PASS. Codex built a detached scratch worktree, removed the except block, ran
  with PYTHONPATH=src override, demonstrated RED (TimeoutExpired propagates), restored → GREEN. Fix
  mirrors sibling (both alias SolverProcessError, returncode=-1, _timeout_stream for streams), cleanup
  preserved, scope minimal (16 LOC src + 30 LOC test). pyright 0/0/0. Stale-editor-diagnostic theory
  confirmed correct. BUG-1 closed.
- BUG-2 coder dispatched (prompts/aba-collision-coder.md).

- BUG-2 coder (agent a3845e9d) committed cec4139. Changed _reject_id_collisions signature to take
  pre-dedup source collection + raise ValueError on collision; call sites at 53-54 pass
  framework.assumptions/language. New test tests/structured/aba/test_aba_asp_id_collisions.py. Coder
  claims RED (2 failed)→GREEN (3 passed), regression 34+14 passed, pyright 0/0/0.
  HARNESS DIAGNOSTIC contradiction: reportCallIssue "Expected 2 positional arguments" at aba_asp.py:53,54
  (the call sites). Either stale snapshot (like BUG-1) or real arity mismatch from the signature change.
  Did NOT bounce to coder preemptively — codex (authoritative, runs pyright on disk) adjudicates.
  Dispatched codex: prompts/aba-collision-verify.md → reports/aba-collision-verify-report.md.

- BUG-2 codex verdict: FAIL — but the FAIL is ENVIRONMENTAL, not the fix. Codex confirmed the fix is
  SOUND: reportCallIssue was STALE (arities match, def takes 3, calls pass 3, pyright 0/0/0); bug fixed
  with correct pre-dedup detection; demonstrated true RED-without-fix in scratch worktree; negative
  control passes; scope minimal (aba_asp.py + new test, cec4139). The 7 "regressions" in
  `tests/structured/aba -q` are: 6× `ModuleNotFoundError: No module named 'pysat'` / "requires
  python-sat" (codex ran bare `python -m pytest` WITHOUT the optional `sat` extra → import-fail before
  encoding) + 1× hypothesis DeadlineExceeded (219ms>200ms) on a graph-in-degree timing test. None
  touch _reject_id_collisions. Coder had run a targeted subset (passed); codex ran the full 8-min suite
  in a deps-incomplete env.
- Decision: NOT bouncing the coder (can't fix "pysat not installed in verifier env"). Dispatching a
  regression-adjudication subagent to PROVE the 7 failures are pre-existing (present on base `main`,
  identical) and unrelated to cec4139, run via the project env (uv/.venv with dev deps). Worktrees so
  nothing is disturbed. prompts/aba-collision-regression-adjudication.md.

- BUG-2 adjudication: DETERMINATION = NO regression. uv .venv has pysat; all 7 node-ids `7 passed` on
  HEAD cec4139 AND on base 8ed6eb1 (scratch worktree). Hypothesis deadline test passed both; the 219ms
  was a slow-bare-run flake. BUG-2 CLOSED.
- LESSON: codex/verifiers MUST run tests via `uv run python -m pytest` (project env) — bare interpreter
  lacks optional sat/asp/z3 extras and yields false regressions. Applied to BUG-3/BUG-4 verify prompts.
- CLEANUP TODO (end of gauntlet): leftover git worktree `../argumentation-aba-collision-scratch` from
  codex BUG-2 verify was not removed; remove it at the end.
- BUG-3 coder dispatched (prompts/acyclic-recursion-coder.md), instructed to use `uv run` for tests.

- BUG-3 coder (agent a3e27545) committed 986e857. Both _is_acyclic → iterative post-order DFS
  (explicit (arg, entered) stack), in place, no shared helper, finite.py untouched. Test
  tests/solving/test_is_acyclic_recursion.py (N=3000, parametrized over both fns). Coder (via uv run):
  RED 4 failed (RecursionError at labelling.py:334) → GREEN 14 passed; semantics 6 cases both fns;
  regression tests/core+tests/solving = 1028 passed 2 skipped; pyright 0/0/0. Harness ✶ warning at
  af_sat.py:991 (_admissible_extension unused) is PRE-EXISTING dead code far from edit — not BUG-3.
- Dispatched codex to verify (uv run mandated): prompts/acyclic-recursion-verify.md →
  reports/acyclic-recursion-verify-report.md.

- BUG-3 VERDICT: codex PASS. Scratch-worktree red (RecursionError both fns) → green; 6 semantic cases
  ×2 fns; 1028 passed/2 skipped (uv); pyright 0/0/0; scope = 2 src + 1 test. uv-run mandate worked.
  BUG-3 CLOSED.
- BUG-4 coder dispatched (prompts/epistemic-converge-coder.md) — hypothesis-first MANDATORY (least
  pre-verified), uv run mandated, fail-loud directive.

- BUG-4 coder (agent ad2ccae1) committed e86975d. Hypothesis CONFIRMED (over-constrained a>=0.8,b>=0.8,
  a+b<=1 returned point with violation 0.3, silently). Added EpistemicProjectionError(RuntimeError) with
  .violation/.iterations/.tolerance; _project_labelling now raises on non-convergence; added
  max_iterations param (default 10_000, behavior-preserving). Test
  tests/probabilistic/test_epistemic_lp_convergence.py. Coder (uv run): RED (ImportError) → GREEN 4
  passed; regression tests/probabilistic 56 passed; pyright 0/0/0.
  HARNESS diagnostics: test-file EpistemicProjectionError unknown-import (L16) + "No parameter
  max_iterations" (L55) = same stale-snapshot pattern (symbols defined in epistemic.py saved after the
  snapshot). epistemic.py ✶ unreachable at 159/208/239/262/405 = PRE-EXISTING; ✶ iteration-not-accessed
  L658 = check exception reports correct iteration count.
- Dispatched codex (uv run mandate) to adjudicate stale-vs-real + verify exception carries correct
  values: prompts/epistemic-converge-verify.md → reports/epistemic-converge-verify-report.md.

- BUG-4 VERDICT: codex PASS. Stale snapshot confirmed; exception fields correct (violation 0.6,
  iterations 10000, tol 1e-10); old code returned violation-0.3 point silently → now raises; negative
  control + 56 passed; scope minimal. BUG-4 CLOSED.
- Housekeeping (agent aa226dbb): removed stray worktree argumentation-aba-collision-scratch, pruned.
  Branch fix/correctness-bugs = 5 commits ahead of main (a8bd376, fda08fd, cec4139, 986e857, e86975d),
  working tree clean re tracked files (only expected untracked scratch), net src+test delta
  9 files +406/-41.

## GAUNTLET COMPLETE — all 4 correctness bugs fixed & codex-verified PASS
Branch `fix/correctness-bugs` (NOT merged, NOT pushed — awaiting Q's call on merge/PR).
- BUG-1 a8bd376 — iccma_af subprocess timeout now returns structured error (mirrors iccma_aba)
- BUG-2 cec4139 — ABA ASP id-collision now fails loud (was a dead always-true guard)
- BUG-3 986e857 — both _is_acyclic now iterative (was RecursionError on long chains)
- BUG-4 e86975d — epistemic projection raises EpistemicProjectionError on non-convergence (was silent wrong answer)
Each: hypothesis-first, TDD red→green, codex independently demonstrated red-without-fix + no
regressions (uv run). Lesson banked: verifiers MUST use `uv run` (bare interp lacks optional extras).

## DUPLICATION WORKSTREAM (Q: "tackle the duplication", as foreman, codex as verifier)
Three read-only scouts done (reports/dup-scout-{frameworks,aba,solving}.md). They CORRECTED several
roast claims. Synthesis → ordered ladder of extractions, lowest risk first. Each = coder + codex verify
gauntlet on branch fix/correctness-bugs (or a new branch — TBD). aba_sat.py changes MUST be serial
(many touch it). Papers/repo-size concern already retracted (gitignored; 731KB tracked).

### Scout-corrected reality
- Frameworks: "dung.py copy-pasted per framework" is OVERSTATED. SETAF (collective attacks) & bipolar
  (set-defeat) predicates are legitimately specialized — CANNOT unify. RETRACTED: af_revision:122 is
  all_extensions not _range_maximal; vaf_completion:191 is fact_first_audiences (not Dung).
- ABA: Horn closure = 5 real bodies +1 delegate, NOT 6 gratuitous. Bitset closure (aba_sat:1667) is a
  legit separate representation (prod hot path) — KEEP. Z3 ranked-closure: bitvec encoder
  (aba_sat:2097) is PRODUCTION-DEAD (only a parity test) → DELETE. _load_z3 has 5 copies across 4
  layers — must centralize DOWN in core (solver_adapters is ABOVE aba).
- Solving: _is_acyclic pair now algorithmically identical (986e857) → trivial merge to core, already
  parametrized by test_is_acyclic_recursion. Adapter command-helpers byte-identical iccma_af/iccma_aba
  (+2 more: _problem_prefix,_semantic_lines) → extract to solver_adapters/_commands.py; clingo.py
  variant is DIFFERENT, don't merge. Stable-SAT encoding ×4: A=prod, B=diagnostic, C=test-only ORACLE
  (keep independent — do NOT unify A↔C). _semantics table omits CF2.

### Planned gauntlet batches (low→high risk)
- B1 DELETE dead bitvec ranked-closure encoder aba_sat:2097 + its parity test (production-dead).
- B2 MERGE _is_acyclic → one helper in core/finite (set+sorted); both call sites use it. Verifiable now.
- B3 _prefsat_closure (aba_sat:2084, naive O(rules²), 3 prod callers) → call canonical aba._closure.
- B4 EXTRACT adapter command-helpers (iccma_af/iccma_aba identical 6 fns) → solver_adapters/_commands.py.
- B5 UNIFY semantics-dispatch (5 copies: enforcement[canonical], caf, partial_af, probabilistic) → one
  extensions_for + SemanticsName Literal in core, re-export from enforcement. Highest value, MED risk
  (drift: caf +naive/-ideal, partial_af returns list — unified must cover union, callers use subsets).
- B6 CENTRALIZE _load_z3 (5 copies) → core; B7 add CF2 to solver_differential._semantics; B8 merge the
  two Int ranked-closure encoders behind one helper (after B1).
- Optional/lower value: _all_subsets reinventions (approximate/caf/af_revision — mind approximate_semi_
  stable order-sensitivity), _range_maximal (approximate.py:53 near-identical to dung).

### DECISIONS FOR Q (flagged, not decided unilaterally)
1. AssumptionKernel (aba_sat) is TEST-ONLY (oracle for 5 tests); deleting it also deletes those tests
   but removes closure-copy-D + one _load_clingo "for free". Delete, or keep as oracle? (irreversible-ish
   — removing test coverage) → ASK.
2. HIGH-risk stable-SAT encoding dedup (A/B/C): scout says only safe move is a tiny A+B clause-shape
   helper; low value, real risk. Do it, or SKIP? → recommend SKIP.

### Q DECISIONS (answered)
1. AssumptionKernel = DECIDE LATER (park kernel-deletion to the end; everything else proceeds —
   _prefsat_closure→canonical, _load_z3 centralization etc. don't depend on it).
2. Stable-SAT (af_sat AfSatKernel A/B/C) dedup = SKIP. NOTE: this is SEPARATE from the ABA ranked-
   closure encoders (B1 bitvec delete, B8 Int merge) which DO proceed.
Branch strategy: refactor/dedup off fix/correctness-bugs (stacks on bug fixes, separate PR).

### Dedup gauntlet progress
- [x] B1 delete dead bitvec ranked-closure encoder — coder 4aaefd3 DONE | codex PASS. Committed tree
      complete despite a coder stash-hiccup (verified: stash empty, tracked status clean, both deletions
      present). 1332 passed; base-vs-HEAD pyright 6→6 no new errors. (coder's "7→6" claim was slightly
      off; codex's 6→6 authoritative — conclusion unchanged.)
- [x] B2 _is_acyclic merge to core — coder e253467 DONE | codex PASS. Delegation real (stale snapshot),
      traversal only in finite.py, behavior spot-check matches across 5 cases, 1021 passed, tree clean.
- [x] B3 _prefsat_closure → canonical _closure — coder ef261a1 DONE | codex PASS. git-confirmed gone
      from committed tree (harness snapshot was stale), 4 callers repointed, codex's OWN 2400-example
      equivalence probe at parent passed, 1332 passed, tool errors pre-existing. Tree clean.
- [x] B4 adapter command-helpers → solver_adapters/_commands.py — coder 9f8979c DONE (after CRLF redo) |
      codex re-verify PASS. 6 helpers byte-identical to CRLF parent, test diff clean 23/23 (no churn),
      per-file EOL correct (test_aba.py is LF, rest CRLF), clingo untouched, 176 passed. First attempt
      (8ca0a75) FAILED on CRLF→LF churn; redone clean.
- [x] B5 semantics-dispatch unify → core extensions_for + SemanticsName — coder ce49c246 + fix 18b08bb |
      codex PASS (after 1 FAIL: enforcement widened to accept naive; fixed with 8-key guard). All 4 callers'
      contracts == parent (behavioral diff), dispatch in core only, 1059 passed, EOL clean. Hardest batch done.
- [x] B6 _load_z3 → core/optional_deps.py — coder 75d129b DONE | codex behavioral checks ALL PASS
      (module committed, 3 messages preserved, lazy import, monkeypatch targets survive, _import_z3
      exclusion sound, lint-imports KEPT, 1649 passed, numstat proportional). Codex returned literal FAIL
      ONLY on "files must be CRLF" — but that criterion was WRONG (my verify prompt's bad assumption).
      GROUND TRUTH (I ran git blob byte-counts): af_sat.py + aba_sat.py are NATIVELY LF since original
      base 8ed6eb1 (af_sat lone_lf=1650, aba_sat lone_lf=2527). B6 preserved each file's native ending
      (optional_deps/epistemic CRLF; af_sat/aba_sat LF). NO churn. B6 is CORRECT — accepted.
      LESSON: repo is PER-FILE MIXED; verify EOL vs each file's BASE-BLOB ending, not blanket CRLF.
      (Coder's report wrongly said "all CRLF" — mis-measured, but outcome correct.)
- [x] B8 Int ranked-closure encoder merge — coder 39276b8 DONE | codex behavioral probe PASS (18 cases
      parent==HEAD exact: var names, constraints, return types, clause counts; PROBE_MATCH=True). Suspected
      tuple-return bug DISPROVEN (committed plain encoder returns dict; editor diags stale). Parity+prefsat
      +1332 passed, aba_sat.py pyright 0, LF preserved. Codex literal FAIL was my prompt's wrong criterion
      ("test_aba.py 0 errors") — test_aba.py has 6 PRE-EXISTING errors (est. in B1, B8 didn't touch it).
      B8 ACCEPTED.
- [ ] B7 CF2 table (deferred to Q — behavior-touch, optional)
- [ ] (end) AssumptionKernel decision revisit

- B1 coder (agent a1b351c4) committed 4aaefd3 on refactor/dedup. Grep-proved
  _add_bitvec_ranked_closure_constraints had ZERO src/ callers; deleted it (63 LOC) + its moot parity
  test test_bitvec_ranked_closure_matches_native_closure (29 LOC). Live Int encoder keeps its own test
  (test_aba.py:274). Suite `1332 passed` via uv run. aba_sat.py pyright 0 errors; 6 test-file errors
  PRE-EXISTING (base 7→6, deletion removed one). Helpers _rules_by_consequent/_literal_key still live.
  FLAG: coder reported a git stash pop mishap during verification (briefly reverted test edit; claims
  caught+re-popped before commit) → codex must confirm committed tree complete, nothing stashed/lost.
- NEW dead-code surfaced by harness (future batch candidate): aba_sat.py _native_sparse_narrow_
  fixedpoint_extension (1232), _sat_preferred_cegar_extension (1798), _sat_admissible_cegar_extension
  (1822) all unused — matches original review's ~250 LOC test-only/dead finding. Consider B-extra.
- Dispatched codex to verify B1 (prompts/dedup-b1-verify.md → reports/dedup-b1-verify-report.md),
  including explicit stash-mishap / committed-completeness check + base pyright comparison.

- B2 coder dispatched (prompts/dedup-b2-coder.md): merge identical _is_acyclic → one helper in
  core/finite.py (generic style, set+sorted determinism); both call sites delegate; update
  test_is_acyclic_recursion.py to exercise the single helper preserving all assertions.

- B2 coder (agent aec3e802) committed e253467 (+e290f03 doc). Merged _is_acyclic → core.finite.is_acyclic
  (generic Mapping[T,Iterable[T]], styled like strongly_connected_components); both _is_acyclic now thin
  adapters delegating; traversal grep-confirmed in finite.py only. Test repointed at single helper, all
  assertions preserved. uv run: 7 passed; tests/core+solving 1021 passed/2 skipped; pyright 0/0/0.
  Harness ✶ "is_acyclic not accessed" at labelling.py:17 + af_sat.py:18 = stale-snapshot pattern (if
  real, empty adapters would break & tests fail — they passed). Codex adjudicating
  (prompts/dedup-b2-verify.md → reports/dedup-b2-verify-report.md), incl. behavior-equivalence spot-check.
- B3 prompt staged (prompts/dedup-b3-coder.md): _prefsat_closure → canonical native_aba._closure;
  MUST prove equivalence before swap (probe old-vs-canonical across random ABA frameworks; STOP if
  mismatch). Hold dispatch until B2 PASS (serial, both touch aba_sat / shared branch).

- B3 coder dispatched (prompts/dedup-b3-coder.md): prove _prefsat_closure == native_aba._closure across
  random ABA frameworks, then remove/delegate. STOP-if-mismatch built in.

- B3 coder (agent ac2ea6d3) committed ef261a1 (+f7d8be5 doc). Claims: 2400-sample equivalence (0
  mismatch), removed _prefsat_closure, repointed 4 callers (3 aba_sat + 1 tools/aba_shape_benchmark) to
  native_aba._closure, deleted probe test. uv run: 1332 passed; 39 prefsat/shape contract passed;
  aba_sat.py pyright 0/0/0. tools/aba_shape_benchmark 5 pyright errors claimed pre-existing.
  HARNESS AMBIGUITY (important): diagnostics show _prefsat_closure STILL at aba_sat.py:2084 + _closure
  import unused + probe test file still referencing it. Could be stale mid-edit snapshots (many edits)
  OR an incomplete commit. NOTE pyright basic doesn't flag unused imports/funcs, so coder's "0 errors"
  doesn't disprove a leftover. Codex dispatched to check COMMITTED state via git
  (prompts/dedup-b3-verify.md → reports/dedup-b3-verify-report.md): git grep _prefsat_closure must be
  ZERO on HEAD, callers use canonical, + independent equivalence re-proof at ef261a1^.
- B4 prompt staged (prompts/dedup-b4-coder.md): extract 6 byte-identical adapter helpers
  (_resolve_command/_split_command/_strip_outer_quotes/_timeout_stream/_problem_prefix/_semantic_lines)
  to solver_adapters/_commands.py; leave clingo.py variant; add characterization unit tests (none exist
  today). Hold until B3 PASS.

- B4 coder dispatched (prompts/dedup-b4-coder.md): extract 6 byte-identical adapter helpers →
  solver_adapters/_commands.py, add characterization tests, leave clingo.py variant.

- B4 coder (agent a1d2ea43) committed 8ca0a75 (+a15e604 doc). Claims: 6 helpers byte-identical
  (AST-verified), moved to solver_adapters/_commands.py, local copies deleted, os/shlex/shutil dropped
  from adapters, clingo.py untouched, +characterization test test_solver_command_helpers.py, +repointed
  25 shutil.which monkeypatch targets to _commands.shutil.which in test_solver_adapters.py & test_aba.py.
  uv run: 114 passed/2 skipped + 25 passed; pyright 4 files 0/0/0.
  HARNESS RED FLAGS (loudest yet, could be real): reportMissingImports for _commands in 3 files +
  shutil/shlex/os UNDEFINED at active call sites iccma_af.py:428-442, iccma_aba.py:341-349. If real →
  _commands.py uncommitted and/or adapters left code using dropped imports = NameError-broken commit.
  But coder's pasted pyright 0 errors + 114 passed contradict that → likely stale snapshot. Codex
  dispatched to check COMMITTED state via git + runtime import smoke (prompts/dedup-b4-verify.md →
  reports/dedup-b4-verify-report.md): _commands committed?, no undefined names?, byte-identity vs
  parent, clingo untouched, monkeypatch repoints mechanical+exercise path.

- B5 prompt staged (prompts/dedup-b5-coder.md). Scout report read: line 43 confirms all 5 dispatch over
  SAME core.dung functions → safe to unify. Canonical = core/dung.py extensions_for + SemanticsName
  Literal (union of 9 keys incl naive). Each caller KEEPS its own allow-set guard + error wording +
  return type (caf: naive/no-ideal/"unsupported CAF semantics"; partial_af: 3 keys/list/"Unknown
  semantics"; probabilistic: 4 keys). enforcement re-exports both names (dynamic.py:14 + import-linter).
  STEP-1 confirm-before-implement + STOP-if-non-dung-dispatch built in. Hold until B4 PASS.

- B4 codex verdict: FAIL — but SUBSTANTIVE this time (not env). Behavior all correct (_commands committed
  & importable, pyright 0, clingo untouched, repoints reach path, 176 passed). FAIL cause: coder tooling
  converted CRLF→LF on touched files. (1) 6 helpers only normalized-identical not byte-identical (parent
  CRLF, _commands LF; codex af_crlf=13/head_crlf=0). (2) test_solver_adapters.py rewritten whole-file
  CRLF→LF: raw 973/973 lines masking just 25 real repoints — unreviewable diff + LF-into-CRLF-repo. Harness
  reportMissingImports/undefined-name flags WERE stale (codex confirmed committed state clean).
- ROOT TOOLING ISSUE: coder file-writes normalize CRLF→LF. B2/B3 stats look proportional (no whole-file
  churn) so likely fine, but new-file creation (_commands.py) + full-file rewrites are the LF source.
  B5+ touch many files → MUST add EOL-preservation directive + diff-stat sanity check.
- ACTION: bounced B4 to coder a1d2ea43 (SendMessage) to redo preserving CRLF: reset --hard f7d8be5,
  recreate _commands.py in CRLF (byte-identical helpers), apply ONLY 25 repoints to test_solver_adapters.py
  from the CRLF original, verify diff-stat ~25 lines not ~1900 + byte-identity probe. Repo is CRLF-canonical
  (parent blobs CRLF; coder to confirm no .gitattributes LF policy).

- B4 REDO done (coder a1d2ea43): reset --hard f7d8be5, rebuilt with byte-level EOL discipline. Byte-identity
  probe: ALL 6 helpers byte-identical to CRLF parent (_resolve_command new_crlf=13). test_solver_adapters.py
  diff = 46 lines (23 repoints), raw==ignore-eol → no churn. 176 passed, pyright 0/0/0, clingo untouched.
  New commits 9f8979c (refactor) + 2b02121 (doc).
  REPO EOL CORRECTION: repo is MIXED — most files CRLF but test_aba.py is genuinely LF (705 LF/0 CRLF).
  codex's earlier "CRLF preserved for test_aba.py" was inaccurate. B5+ prompt updated: match EACH file's
  existing ending, not assume CRLF. (25 total repoints = 23 in test_solver_adapters + 2 in test_aba.)
- Dispatched codex focused RE-verify of B4 redo (prompts/dedup-b4-reverify.md → reports/dedup-b4-reverify-
  report.md): byte-identity, diff-stat no-churn, per-file EOL correctness, behavior intact, the
  test_solver_command_helpers.py:226 _commands diagnostic.

- B4 RE-verify: codex PASS. EOL discipline worked. B4 CLOSED.
- B5 coder dispatched (prompts/dedup-b5-coder.md, EOL-hardened): unify 5 semantics-dispatch copies →
  core/dung.py extensions_for + SemanticsName; per-caller contract preserved.

- B5 coder (agent a4b17387) committed ce49c246. STEP-1 confirmed all 5 dispatch to same core.dung fns.
  Unified → core/dung.py extensions_for + SemanticsName. Each caller keeps contract (enforcement
  re-exports both names; caf naive/no-ideal/"unsupported CAF semantics"; partial_af 3keys/list/"Unknown
  semantics"; probabilistic 4keys). Used cast() not type:ignore. Caught+fixed a core/dung.py EOL churn
  (rebuilt from bytes → 44/0 two clean hunks). Diff-stat proportional (5 files, 86/93). uv run: pyright
  0/0/0, 68 targeted + 1059 broad passed.
  HARNESS FLOOD (resolve): reportUndefinedVariable in enforcement:217-231 (dispatch fns), caf:174 +
  partial_af:171 (extensions_for/cast/SemanticsName), dung:709 unreachable, Literal:17 unused. Same
  stale-snapshot pattern (basic pyright wouldn't give 0 errors if real) but B5 is behavior-critical →
  codex must check committed state + per-caller contract behaviorally.
- NOTE: `git diff --check` flags trailing-whitespace on EVERY CRLF line here (autocrlf=false artifact) —
  NOT a usable EOL signal; use byte counts + numstat. Repo has no .gitattributes (latent EOL trap).
- Dispatched codex to verify B5 (prompts/dedup-b5-verify.md → reports/dedup-b5-verify-report.md): undefined
  -name resolution + runtime import, dispatch-in-one-place, per-caller contract (supported+unsupported keys,
  exact error msg, return type) vs parent ce49c246^, dynamic.py+import-linter, broad regression, EOL.

- B5 codex verdict: FAIL — REAL behavioral regression (not stale/env). Harness undefined-name floods WERE
  stale (pyright 0, imports work, 1059 passed). But codex HEAD-vs-parent behavioral diff caught it:
  enforcement.extensions_for WIDENED its contract — parent REJECTED `naive` ("unsupported semantics:
  naive"); HEAD ACCEPTS it (coder re-exported bare canonical core.extensions_for which supports 9-key
  union incl naive). caf/partial_af/probabilistic all match parent exactly (kept their guards); only
  enforcement got the bare canonical. Classic silent-drift: pyright-clean + all-tests-green yet contract
  changed. Only the explicit behavioral diff vs parent caught it — exactly why that check was in the prompt.
- FIX (bounced to coder a4b17387): enforcement must preserve its ORIGINAL 8-key contract — keep its own
  8-key SemanticsName Literal (excl naive) + an allow-set guard in extensions_for that rejects naive +
  unknowns with "unsupported semantics: {x}", then delegates computation to core.dung.extensions_for
  (like the other 3 callers do). dynamic.py imports enforcement.SemanticsName (must stay 8-key) +
  extensions_for. Re-verify enforcement rejects naive == parent.

- B5 FIX done (coder, commit 18b08bb): enforcement now keeps its 8-key SemanticsName + guard-then-delegate
  extensions_for; behavioral proof shows naive REJECTED ("unsupported semantics: naive") == parent. Fix
  commit touches only enforcement.py + report (38/2, CRLF, proportional). pyright 0/0/0, 1059 passed.
  Harness undefined-name flags (extensions_for 286/389) are stale again. Dispatched focused codex
  re-verify (prompts/dedup-b5-reverify.md → reports/dedup-b5-reverify-report.md): enforcement contract ==
  parent (esp. naive rejected), other 3 callers unchanged, dispatch in one place, no EOL churn.

- B5 RE-verify: codex PASS. B5 CLOSED.
- B6 coder dispatched (prompts/dedup-b6-coder.md, EOL-hardened): centralize 5 _load_z3 copies → core
  loader, preserve per-caller messages + lazy import + any test monkeypatch targets.

- B6 coder (agent a55a2d56) committed 75d129b (+c5aa6bc doc). STEP-1: only 4 z3 loaders not 5;
  optimization._import_z3 has DIFFERENT contract (returns None, monkeypatched by name) → correctly LEFT
  UNTOUCHED. Centralized the 3 RAISING loaders → core/optional_deps.py load_z3(feature) (parametrized
  message preserves each: "SAT solving..."/"ABA stable SAT..."/"linear epistemic..."). af_sat+aba_sat keep
  thin _load_z3 delegators (monkeypatch targets). Lazy import preserved. uv run: pyright 0/0/0, 1649
  passed, lint-imports KEPT. CRLF clean, numstat proportional (24/2/2/2).
  Harness reportMissingImports core.optional_deps in 3 files = stale (pyright couldn't be 0 if real).
- Dispatched codex verify (prompts/dedup-b6-verify.md → reports/dedup-b6-verify-report.md): module
  committed+resolvable, loader in one place, per-caller messages+lazy import preserved, monkeypatch
  targets survive, _import_z3 exclusion sound, import-linter + regression, EOL.

- B6 ACCEPTED (codex behavioral PASS; EOL FAIL was my prompt's wrong CRLF assumption — af_sat/aba_sat
  natively LF, verified). B6 CLOSED.
- B8 coder dispatched (prompts/dedup-b8-coder.md): merge 2 Int ranked-closure encoders in aba_sat.py
  (note: aba_sat.py is LF — prompt says match each file's endings). Prove identity-modulo-(prefix,tally)
  first. (B7 CF2 table deferred to Q checkpoint.)

- B8 coder (agent a8b20731) committed 39276b8. Merged 2 Int encoders → _emit_ranked_closure_constraints
  (always returns (derived, clause_count)); plain wrapper returns bare dict, prefsat returns tuple.
  Coder SAID first attempt leaked dict|tuple union (11 pyright errors) then reworked to concrete tuple,
  claims pyright 0 + parity 1 passed + 1332 passed. aba_sat.py stays LF, numstat 43/64 proportional.
  SUSPECTED BROKEN COMMIT: harness diagnostics EXACTLY match the bug the coder said they fixed —
  tuple[dict,int] leaking where dict expected: .items() fails at aba_sat:1775 + test_aba:282, [key]
  fails at 1735/1788/1928/1932/1934. Either stale (broken first attempt) or the committed plain encoder
  still returns tuple (→ AttributeError at runtime, contradicting "1332 passed"). Highest broken-commit
  suspicion of the session.
- Dispatched codex to adjudicate committed blob (prompts/dedup-b8-verify.md → reports/dedup-b8-verify-
  report.md): does committed _add_ranked_closure_constraints return dict or tuple? pyright on HEAD,
  parity+prefsat actually pass?, behavioral identity, LF preserved.

## DEDUP GAUNTLET — all planned extractions DONE & verified
refactor/dedup (off fix/correctness-bugs). Commits: 4aaefd3(B1) e253467(B2) ef261a1(B3) 9f8979c(B4)
ce49c246+18b08bb(B5) 75d129b(B6) 39276b8(B8) + doc commits. All codex-verified behavior-preserving.
META: 2 false-alarm codex FAILs (B6 blanket-CRLF, B8 test_aba-0-errors) were MY over-strict verify
criteria vs repo's pre-existing state (mixed per-file EOL; 6 pre-existing test_aba.py pyright errors).
Underlying code sound in both — proven by direct evidence. Verify criteria must respect pre-existing baseline.

### Remaining (Q checkpoint — presenting now)
- B7 CF2 semantics-table drift: align/unify iccma_cli.PROBLEM_SEMANTICS vs solver_differential._semantics
  (adds CF2 to solver_differential = behavior-touch). Optional.
- AssumptionKernel (deferred "decide later"): test-only oracle; delete reclaims closure-copy + _load_clingo
  dup but removes 5 oracle tests.
- Dead-code batch: aba_sat _native_sparse_narrow_fixedpoint_extension(1233), _sat_preferred_cegar_extension
  (1799), _sat_admissible_cegar_extension(1823), af_sat _admissible_extension(993) — harness-flagged unused;
  B1-style deletions if confirmed dead. ~clean win.
- Merge/PR: refactor/dedup contains BOTH bug fixes + dedup. One PR or two? Merge to main? (NOT pushed yet.)

### Current blocker
Q checkpoint: presenting full results + 4 forward decisions. refactor/dedup HEAD = 39276b8 (+B8 doc).
Done: 4 bugs + dedup B1-B6,B8.

## Next (per Q's mandate "then let's talk about the other issues")
The other issues from the original roast (NOT touched): no public API surface; god files (aba_sat
2527 LOC etc.); pervasive duplication (Dung machinery per-framework, 6× Horn closure, 4× stable SAT
encoding, 3× ranked-closure); benchmark cruft in lib (route_policy PNG paths, telemetry in hot loops);
brute-force enumerators w/o caps; packaging (gunray [grounding] extra 404 on PyPI; 302MB papers/;
fake test markers); stringly-typed APIs / Any-soup. Await Q's direction on which to tackle.
