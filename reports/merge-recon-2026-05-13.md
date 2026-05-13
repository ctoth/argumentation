# Merge recon — 2026-05-13

Scout report. Read-only, no refs mutated.

## Repo state right now

- Working directory: `C:\Users\Q\code\argumentation`
- git version: 2.45.2.windows.1
- Current branch (this worktree): `experiment/graph-speedup-wave-a-preprocessing` at `c9f4a18`.
- Second worktree: `C:\Users\Q\code\argumentation-dynamic-clean` checked out on `dynamic-af-workstream` (5b56b9d). Explains the `+ dynamic-af-workstream` marker in `git branch -a`.
- Working tree (this worktree): **0 modified, 0 staged, 63 untracked files**:
  - `notes/`: 35 untracked `.md` files
  - `reports/`: 16 untracked `.md` files
  - `prompts/`: 11 untracked `.md` files
  - root: 1 untracked (`notes-graph-speedup-foreman-2026-05-12.md`)
- Stash list: **empty**.
- `main` (local) is **15 commits ahead of `origin/main`**; `origin/main` is 0 ahead of local main. Local main has not been pushed.

## Branch ahead/behind vs local `main` (8ab2a6f)

| Branch | ahead | behind | last commit | merges clean? | recommendation |
|---|---:|---:|---|---|---|
| experiment/graph-speedup-wave-a-preprocessing | 10 | 0 | 2026-05-12 20:38 — `Note final commit hash in C4 report` (c9f4a18) | **YES** (clean, fast-forward) | **MERGE** |
| experiment/aba-se-pr-st-assumption-kernel | 0 | 0 | 2026-05-12 16:56 — `Load clingo through optional dependency helper` (8ab2a6f) | trivially identical to main | SKIP — already merged (ref equals main) |
| experiment/iccma-af-regression-after-grounded-fastpath | 0 | 10 | 2026-05-12 15:40 — `Short-circuit infeasible range tasks` (aeba455) | n/a; ancestor of main | SKIP — already merged |
| experiment/aba-stable-forced-literals | 0 | 16 | 2026-05-12 01:12 — `Group ABA closure rules once` (8d28624) | n/a; ancestor of main | SKIP — already merged |
| experiment/aba-stable-scc-bitvec | 1 | 40 | 2026-05-10 01:25 — `Try SCC-local bit-vector ABA stable ranks` | **NO** — conflict in `src/argumentation/aba_sat.py` | ABANDONED-LOOKING |
| experiment/aba-stable-bitvec-profiled | 5 | 42 | 2026-05-10 01:12 — `Correct ABA stable bit-vector route` | **NO** — conflicts in `src/argumentation/aba_sat.py`, `tests/test_aba.py` | ABANDONED-LOOKING |
| experiment/aba-stable-support-sat | 2 | 45 | 2026-05-10 00:45 — `Try support-materialized ABA stable SAT` | **NO** — conflict in `src/argumentation/aba_sat.py` | ABANDONED-LOOKING |
| experiment/aba-stable-boolean-rank-ladder | 2 | 46 | 2026-05-10 00:40 — `Try ABA stable Boolean rank ladder` | **NO** — conflicts in `src/argumentation/aba_sat.py`, `tests/test_aba.py` | ABANDONED-LOOKING |
| dynamic-af-workstream | 0 | 361 | 2026-04-30 15:03 — `Mark dynamic AF workstream complete` (5b56b9d) | n/a; ancestor of main | SKIP — already merged (and checked out in second worktree) |

### Commits ahead on `experiment/graph-speedup-wave-a-preprocessing` (10, all on main)
```
c9f4a18 Note final commit hash in C4 report
598d505 Fix empty-attacker ABA grounded bug + C4 cleanups
b2cd74f Add Wave C2b ABA multi-shot report
466d38d Add clingo multi-shot incremental CEGAR for ABA (Wave C2b)
bf3862d Add Wave C2a ABA preprocessing report
e54facf Add ABA well-founded preprocessing + reuse Z3 preferred-growth solver
b882a25 Record commit hash in Wave B2 SCC report
cebb9a9 Add SCC-recursive solving for complete/preferred/stable (Wave B2)
50f9204 Record commit hash in Wave A preprocessing report
f827ff1 Add AF grounded-reduct preprocessing layer (Wave A)
```

### Commits ahead on the four `aba-stable-*` exploratory branches
```
aba-stable-scc-bitvec (1):
  5907a60 Try SCC-local bit-vector ABA stable ranks

aba-stable-bitvec-profiled (5):
  b508bae Correct ABA stable bit-vector route
  ed2e78e Route ABA stable through profiled bit-vector ranks
  796b533 Set ABA stable Z3 timeout
  52e6a8e Use profiled ABA bit-vector stable ranks
  f7b6820 Add profiled ABA bit-vector closure property

aba-stable-support-sat (2):
  6313258 Try support-materialized ABA stable SAT
  75449e7 Add ABA support stable witness property

aba-stable-boolean-rank-ladder (2):
  62c3dc2 Try ABA stable Boolean rank ladder
  53ba769 Add ABA ladder closure property
```

## Parent chain — confirmation

Prompt asserted: `experiment/graph-speedup-wave-a-preprocessing` forked off `experiment/aba-se-pr-st-assumption-kernel` (10 commits). Verified:

- `git merge-base wave-a aba-se-pr-st-assumption-kernel` = `8ab2a6f` ("Load clingo through optional dependency helper").
- `git merge-base wave-a main` = `8ab2a6f` (same commit).
- `main` HEAD = `8ab2a6f`.
- `aba-se-pr-st-assumption-kernel` HEAD = `8ab2a6f` (identical to main).

In other words: the assumption-kernel branch's tip is already on `main`; wave-a forks straight off `main` (= the old assumption-kernel tip). So:

- `experiment/aba-se-pr-st-assumption-kernel` is **already merged** and contributes nothing new.
- `experiment/graph-speedup-wave-a-preprocessing` is a **clean fast-forward of main** (ahead=10, behind=0). No rebase needed.

## Test status

- `experiment/graph-speedup-wave-a-preprocessing`: notes record clean test runs. `notes/graph-speedup-wave-c4-fixes.md:23` says **"Suite 1 failed (kernel ideal AF, pre-existing/unrelated), 2641 passed x2. ruff+pyright clean."** This was for commit `598d505`; the tip `c9f4a18` is a documentation-only follow-up ("Note final commit hash in C4 report"). Per prompt I am NOT re-running tests.
- All four `aba-stable-*` exploratory branches: commit subjects begin with `Try ...` (smell: speculative spike). No notes/reports record passing tests on these tips. Last activity 2026-05-10, three days before this report.
- Branches that are already ancestors of main need no further check.

## Conflicts spotted

All conflicts are in the four exploratory `aba-stable-*` branches, all centred on `src/argumentation/aba_sat.py`. Main has clearly moved that file forward since these spikes were cut.

| Branch | Conflicting files |
|---|---|
| experiment/aba-stable-scc-bitvec | `src/argumentation/aba_sat.py` (auto-merge succeeded on `tests/test_aba.py`, `tools/aba_stable_diagnostics.py`) |
| experiment/aba-stable-bitvec-profiled | `src/argumentation/aba_sat.py`, `tests/test_aba.py` |
| experiment/aba-stable-support-sat | `src/argumentation/aba_sat.py` (auto-merge on `tests/test_aba.py`) |
| experiment/aba-stable-boolean-rank-ladder | `src/argumentation/aba_sat.py`, `tests/test_aba.py` |

`experiment/graph-speedup-wave-a-preprocessing` has **no conflicts**.

## Recommended merge order

There is effectively one merge to do:

1. `experiment/graph-speedup-wave-a-preprocessing` → `main` (clean fast-forward, 10 commits).

All other non-main local branches either already are ancestors of `main` (no merge needed; can be deleted) or are abandoned exploratory spikes that conflict on `aba_sat.py` and have no test record.

Separately: `main` is 15 commits ahead of `origin/main`; pushing `main` (and the wave-a tip, if Q wants the branch on the remote) is a follow-on, not a merge.

No dependency chain among mergeable branches: only one merges. The wave-a branch was nominally based on `aba-se-pr-st-assumption-kernel`, but since that branch is already at main's tip, the dependency has resolved itself.

## Open questions for the foreman

1. **63 untracked notes/reports/prompts** in the working tree — leave alone, commit on `main`, or commit on `experiment/graph-speedup-wave-a-preprocessing` before merging? They look like cross-workstream documentation accumulated over weeks (multiple workstreams represented: `citation-crossref`, `docs-audit-*`, `reduction-tricks-*`, `workstream-asp-backend`, plus the graph-speedup ones from the current workstream). They are not tied to wave-a only.
2. **Push policy.** Local `main` is 15 commits ahead of `origin/main`. Push before or after the wave-a merge? (No instruction in the prompt.)
3. **Cleanup of merged branches.** `experiment/aba-se-pr-st-assumption-kernel`, `experiment/iccma-af-regression-after-grounded-fastpath`, `experiment/aba-stable-forced-literals`, `dynamic-af-workstream` are already ancestors of `main`. Delete them, or keep as historical pointers?
4. **The four abandoned `aba-stable-*` spikes.** Subjects say "Try …"; last touched 2026-05-10; conflict on `aba_sat.py`. Delete, or keep around as reference (some carry a "property" commit that could be salvaged later — e.g. `f7b6820 Add profiled ABA bit-vector closure property`, `53ba769 Add ABA ladder closure property`, `75449e7 Add ABA support stable witness property`)?
5. **Second worktree.** `C:\Users\Q\code\argumentation-dynamic-clean` is still pinned to `dynamic-af-workstream`. That branch is fully merged. Worktree no longer load-bearing — leave or `git worktree remove`?
