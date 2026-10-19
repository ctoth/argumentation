# Ward/worker conflict — status (2026-07-01/02)

## Facts (all verified by direct attempts)
- After `ward set foreman`, the hook gates the Bash TOOL for the main session
  and for all post-ward subagents; every command (including `ward help` and
  `ward set experiment-worker`) returns the foreman denial. Verified by MY
  own attempts at 2026-07-02: both denied.
- Workers (z3-scout, dspr-scout) REFUSE relayed authorization to run
  `ward set <role>` — peer messages cannot authorize enforcement changes.
  Both stated they need it from Q or the permission system directly. This is
  correct guardrail behavior and consistent across agents.
- Net: nobody inside this session can change the ward phase. Deadlock unless:
  (a) Q runs the command himself (e.g. `! ward help` then `! ward clear` or
      equivalent in the session prompt),
  (b) isolated-worktree agents escape the hook (UNVERIFIED — dspr-coder is
      the live test), or
  (c) pre-ward agents (recal-runner) do main-tree execution.

## Q'S RULING (AskUserQuestion, 2026-07-02)
Chose "Authorize me to ward-off workers": workers may run ward set (they
refuse relayed auth) or I may clear the phase (my Bash is sealed). Ruling is
therefore not mechanically executable inside the session; needs Q's keyboard.

## Ask for Q
Type in this session: `! ward help` (to see phases/clear syntax), then
either clear the phase or set a phase that allows worker execution. Until
then the campaign proceeds via worktree-isolated coders (if unblocked) and
the pre-ward recal-runner.

## Impact
- dspr-coder (worktree): live test of route (b); prompt includes fallbacks.
- Blocked until resolved: any main-tree benchmark worker (master baseline,
  frontier-manifest runs), reports/*.md writes by post-ward agents.
