# ICCMA campaign dispatch log (foreman) — running (updated 2026-07-10 ~02:45)

Strategy: notes-iccma-timeout-strategy-2026-07-01.md. Goal: 4 falsifiable
end-states. Directive: merged to main + CI GREEN — HOLDING.
STATE: origin/main = a460bf9+ (parallel-driver landing mid-CI-watch).
SCOREBOARD: FRONTIER 18/30 measured (from 9/30). Sweep now 5.1 min.

## Q'S "WHY HOURS" — ARITHMETIC + STRUCTURAL FIX (this cycle)
Per-experiment chain decomposed: 2x ~40min SERIAL t15 slice guards +
~10min frontier cells (parallel now) + ~6min suite + ~10min probes.
The 40-min term = tools/iccma2025_run_native.py still serial (same
defect class as the frontier driver pre-2940cc7). DISPATCHED
runner-parallel-coder (exp/runner-parallel): --jobs N on the runner's
row loop (default 1 = byte-identical serial; thread-safe JSONL writes;
deterministic order; smoke proof = real DS-PR t15 slice at --jobs 8,
target <=8 min vs ~40). After landing: experiment chains drop to
~30-45 min total. prompts/runner-parallel-coder.md.
Verified-parallel evidence given to Q: both 7A/7B worktrees writing
within minutes + 15 live python processes at 02:32.

## IN FLIGHT (4)
- frontier-parallel landing (CI watch; coder resumes at conclusion).
- satcore-coder (7A): probe phase running (probe-driver log 02:31).
- satve-coder (7B): VE clauses implemented, microbench 02:25; state
  checkpoints healthy.
- runner-parallel-coder (7C, NEW): guard-runner parallelism.
FILE DOMAINS: 7A=af_sat/solver.py, 7B=structured/aba, 7C=tools/ +
frontier script — disjoint. Benchmark contention noted symmetric.

## MODE OFFER TO Q (pending his word)
Fast mode offered: land on smoke+CI, skip full gauntlet for low-risk,
fix-forward with nightly frontier sweep. Not activated; full gauntlet
remains default until Q says "fast mode".

## LEDGER
DS-PR 229->235 | SST 576->578 | SE-ST 217->241 | Frontier 9->18/30.
10 landings + parallel-driver landing imminent. 0 losses, 0 wrong
answers. Remaining hard (in-scope 10): crusti DS-PR x2 (6C queued),
DS-ST crusti x2 (new idea needed), ER x2 (7A candidate), abcgen c35 x2
(7B running), SE-ST c25 (budget routing queued), scc none left.

## Current blocker
None.
