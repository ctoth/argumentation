# Recon — enumerate branches and assess merge-readiness against `main`

You are a scout subagent. Read-only — do NOT merge, push, rebase, or change refs. Working dir: `C:\Users\Q\code\argumentation`. Write `reports/merge-recon-2026-05-13.md`.

## Goal

Q wants to merge "all branches that actually succeeded" down to `main`. I need a clean, accurate picture of every local and remote branch in the repo, its state relative to `main`, and whether it can be considered "succeeded" (= tests pass, work is real, not abandoned).

## What to gather

1. **Branch inventory.** `git branch -a` and `git for-each-ref --sort=-committerdate refs/heads refs/remotes --format='%(refname:short) %(committerdate:iso) %(authorname) %(subject)'`. List every local branch and every remote-tracking branch that isn't a duplicate of a local one. Note the current branch.
2. **For each non-main branch** report:
   - Commits ahead of `main` (`git rev-list --count main..<branch>`) and behind (`git rev-list --count <branch>..main`).
   - Last commit date, author, subject.
   - The actual commits ahead, short-form: `git log --oneline main..<branch>` (cap at 30 lines per branch; if more, say so and show first 30).
   - Does it merge cleanly into `main`? (`git merge-tree $(git merge-base main <branch>) main <branch>` — non-empty output with conflict markers = conflicts; or `git merge --no-commit --no-ff <branch> && git merge --abort` on a fresh worktree if you must, but prefer `merge-tree` to avoid mutating state).
   - Any obvious smell: stale (>30 days untouched), uncommitted-WIP-looking subjects ("wip", "fixup", "tmp"), debug-only commits.
3. **The known feature branch.** `experiment/graph-speedup-wave-a-preprocessing` is this workstream's branch (10 commits, forked off `experiment/aba-se-pr-st-assumption-kernel`). Confirm its parent and where each diverges from `main`. Both should be candidates for merge.
4. **Test status, where cheap.** For each branch you'd recommend merging, note whether `notes-*.md` / `reports/*.md` indicate a clean test run on that branch. Do NOT actually check out and run tests — too slow, and the workstream notes already record results for the graph-speedup branch. If a branch has no record of passing tests, flag it as "test status unknown".
5. **Working-tree state.** `git status --short` and `git stash list`. Are there uncommitted changes? Untracked files we'd want to deal with first? The workstream produced many untracked `notes/*.md`, `reports/*.md`, `prompts/*.md` at root + under those dirs — list how many are untracked vs tracked, so we can decide whether to stash, commit, or leave.

## Deliverable

`reports/merge-recon-2026-05-13.md` structured as:
- **Repo state right now** — current branch, working-tree summary, stash count.
- **Branches table** — name | ahead/behind main | last commit | merges cleanly? | recommendation (MERGE / SKIP / NEEDS-DECISION / ABANDONED-LOOKING).
- **Recommended merge order** — if there's a dependency chain (e.g. wave-a-preprocessing depends on aba-se-pr-st-assumption-kernel), state it. If branches are independent, say so.
- **Conflicts you spotted** — exact files and a one-line characterization.
- **Open questions for the foreman** — anything where Q's call is needed before merging (e.g. "branch X has no test record — verify before merge?").

Do not propose to actually merge. Just give the picture.
