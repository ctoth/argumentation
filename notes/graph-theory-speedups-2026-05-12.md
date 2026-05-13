# Graph-theory & preprocessing speedups research — 2026-05-12 — DONE

Report written: reports/graph-theory-speedups-2026-05-12.md
PDFs: papers/Cerutti_2014_SCC_SAT_PreferredExtensions.pdf (password-protected though),
      papers/Lehtonen_2021_IncrementalASP_ABA.pdf

Ranking in report: 1) grounded-reduct preprocessing 2) cheap structural reductions
3) SCC-recursive enumeration 4) ABA assumption-level/incremental 5) treewidth DP (low pri)
6) anytime grounded / caching / portfolio.

Key codebase facts found: af_revision.py has Baumann/Oikarinen-Woltran kernels (unused pre-solve);
dung.py has _strongly_connected_components used only for CF2/stage2; af_sat.py:501-510 has grounded
shortcuts in preferred-skeptical only; approximate.py exists; clingo wired.
