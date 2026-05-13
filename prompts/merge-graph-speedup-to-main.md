# Merge the graph-speedup workstream to main + cleanup

You are a coding subagent. This task is git-ref-mutating — do every step carefully, verify before each destructive operation, and STOP if anything looks wrong. Working dir: `C:\Users\Q\code\argumentation`. Target branch: `main`.

## Pre-flight inventory you can rely on (verified by recon)

- Current branch: `experiment/graph-speedup-wave-a-preprocessing`, HEAD `c9f4a18`, 10 commits ahead of `main`, 0 behind, merges cleanly into `main` (`git merge-tree --write-tree` exit 0).
- Working tree: 0 tracked files modified; 63 untracked `.md` files across `notes/`, `reports/`, `prompts/`, and the repo root (the workstream's coordination log + per-wave reports/notes/prompts + paper notes). Plus retrieved PDFs in `papers/`: `Baroni_2005_SCC_recursiveness.pdf`, `Cerutti_2014_SCC_SAT_PreferredExtensions.pdf`, `Lehtonen_2021_IncrementalASP_ABA.pdf` — load-bearing for cited reports.
- `main` is currently 15 commits ahead of `origin/main` (pre-existing — not from this workstream).
- Other branches present: `experiment/aba-se-pr-st-assumption-kernel` (ancestor of main), `experiment/iccma-af-regression-after-grounded-fastpath` (ancestor), `experiment/aba-stable-forced-literals` (ancestor), `dynamic-af-workstream` (ancestor); and four spike branches Q has approved deleting: `aba-stable-scc-bitvec`, `aba-stable-bitvec-profiled`, `aba-stable-support-sat`, `aba-stable-boolean-rank-ladder`.
- Second worktree: `C:\Users\Q\code\argumentation-dynamic-clean` on `dynamic-af-workstream` (fully merged into main).

## What Q approved

1. **Merge** `experiment/graph-speedup-wave-a-preprocessing` into `main` with `--no-ff` (merge commit preserved).
2. **Commit all 63 untracked `.md` files** as one docs commit on `main` BEFORE the merge (so the merge commit shows clean), plus the three workstream PDFs in `papers/` IF `papers/` is not in `.gitignore`.
3. **Push `main` to `origin`** after merging.
4. **Delete the four spike branches locally** (`git branch -D`).
5. **Drop the second worktree** at `C:\Users\Q\code\argumentation-dynamic-clean` (`git worktree remove`).

## Execute in this order, verifying after each step

### Step 0 — sanity baseline
- `git status --short` and `git rev-parse --abbrev-ref HEAD` and `git log --oneline -1`. If anything contradicts the inventory above (e.g. modified tracked files appear, or HEAD isn't `c9f4a18` on `experiment/graph-speedup-wave-a-preprocessing`), STOP and report.
- Quick test sanity on the feature branch is not required — Wave C4's two consecutive runs already established `1 failed (pre-existing) / 2641 passed / 2 skipped`. Do not re-run the full suite (slow). You WILL re-run it after the merge — see Step 6.

### Step 1 — checkout main
- `git checkout main`. Confirm with `git log --oneline -1`.

### Step 2 — stage docs + PDFs
- Check `.gitignore` for `papers/` and for `.md` patterns under `notes/`, `reports/`, `prompts/`. If any of those locations is gitignored, that's Q's intent — leave those files alone.
- For non-ignored paths: `git add notes/ reports/ prompts/ notes-*.md` (root-level `notes-*.md` coordination log) and, if `papers/` isn't ignored, `git add papers/Baroni_2005_SCC_recursiveness.pdf papers/Cerutti_2014_SCC_SAT_PreferredExtensions.pdf papers/Lehtonen_2021_IncrementalASP_ABA.pdf` (only these three — don't sweep other `papers/` content).
- `git status --short` after staging. Confirm: only the expected untracked files are now staged; no tracked-file modifications snuck in. List the staged paths in the report.

### Step 3 — docs commit
```
git commit -m "Add foreman coordination log and graph-speedup workstream docs

Notes, reports, and per-wave prompts produced during the graph-theory
speedup workstream (Wave A preprocessing through Wave C4 fixes), plus
the three retrieved reference PDFs cited in the reports."
```
(Adjust the message lightly if the staged-path list shouldn't claim PDFs — drop that line.)

### Step 4 — the merge
- `git merge --no-ff experiment/graph-speedup-wave-a-preprocessing -m "Merge graph-theory speedup workstream

AF preprocessing layer (grounded reduct + cheap structural reductions),
SCC-recursive solving for complete/preferred/stable, well-founded ABA
preprocessing + Z3 CEGAR refactor, and clingo multi-shot incremental
CEGAR for ABA (ASPforABA reproduction). +1826 tests; 2641 passed."`
- Confirm a merge commit was created (`git log --oneline -3` should show two parents on the new HEAD via `git log --graph --oneline -5`).

### Step 5 — sanity post-merge
- `git status --short` should be clean.
- `git log --oneline --graph -8` — paste into the report.
- Working-tree integrity: `python -c "import argumentation"` should succeed (`pip install -e .` already done historically; if it fails because deps moved, that's a finding — STOP and report; do NOT push a broken main).

### Step 6 — post-merge suite check
- Run `python -m pytest -q --ignore=tests/test_datalog_grounding.py --tb=no` on `main` post-merge. Required because we're about to push. Target: `1 failed (test_kernel_ideal_extension_is_admissible — the pre-existing AF-kernel bug) / 2641 passed / 2 skipped`. ANYTHING else = STOP, do not push, report the failures.

### Step 7 — push
- `git push origin main`. Capture the output. If it's rejected (non-fast-forward, hook reject, auth), STOP — do not `--force` anything — and report.

### Step 8 — delete spike branches
- For each of `aba-stable-scc-bitvec`, `aba-stable-bitvec-profiled`, `aba-stable-support-sat`, `aba-stable-boolean-rank-ladder`: first verify it's NOT an ancestor of main (`git merge-base --is-ancestor <branch> main` — exit 1 = not ancestor = safe to `-D`; exit 0 = already merged = use `-d`). If a branch IS an ancestor, that's a recon discrepancy — note it and use `-d` (safe delete) instead of `-D`. Report the per-branch SHA you deleted so it's recoverable from reflog if needed.

### Step 9 — drop second worktree
- `git worktree list` to confirm `C:\Users\Q\code\argumentation-dynamic-clean` exists and is on `dynamic-af-workstream`.
- `git worktree remove C:\Users\Q\code\argumentation-dynamic-clean` — only if its working tree is clean. If it's dirty, STOP and report; do not `--force`.
- After remove: `git worktree prune`. Then if `dynamic-af-workstream` is now branch-only and an ancestor of main, you may also `git branch -d dynamic-af-workstream` (safe delete only).

## Report → `reports/merge-graph-speedup-2026-05-13.md`

Include:
- Pre-flight `git status` output.
- The list of paths actually committed in the docs commit (Step 3).
- The merge commit SHA (Step 4) and `git log --oneline --graph -8`.
- Post-merge suite result (Step 6).
- `git push` output (Step 7).
- Per-spike-branch deletion: SHA at deletion, ancestor check result.
- Worktree-remove output.
- Final `git branch -a` + `git worktree list` + `git status` on main.

No need for separate commit hash for the report — append it after the docs/merge commits if you want, or leave it uncommitted; Q's call. State which you did.

## Hard stops

- If any verification step fails (Steps 0, 5, 6, 7, 8, 9 each have their own stop conditions), STOP immediately and report the exact state. Do not attempt recovery without instruction.
- Do NOT use `--force`, `--force-with-lease`, `--no-verify`, `--no-gpg-sign`, or `reset --hard` anywhere.
- Do NOT amend the workstream commits, rewrite the wave-a branch's history, or rebase. The branch is fine — merge as-is.
- Do NOT touch other repos, other branches not listed, or the second worktree's contents beyond `worktree remove`.
