# README / metadata overhaul

## 2026-04-18

### GOAL
Improve README, pyproject metadata, docs/architecture.md. Delete CONTRIBUTING.md.

### DONE
- Rewrote README.md from scratch. No propstore mentions. No anti-marketing "non-goals" listing other people's features.
- Sections: Dung, ASPIC+, Bipolar, Partial AFs, AF Revision, Probabilistic AFs, Optional Z3, Preferences, Design, Development. Each has paper citations.
- Updated pyproject.toml: keywords (incl. probabilistic-argumentation, qbaf, df-quad, monte-carlo, tree-decomposition), classifiers, project.urls (Homepage / Repository / Issues), expanded description.
- Rewrote docs/architecture.md: added partial_af, af_revision, all four probabilistic_*, preference, solver to module list. Added probabilistic backend routing section. Documented invariants.
- Deleted CONTRIBUTING.md.

### VERIFIED
- `uv run python -c 'import argumentation; ...'` succeeds; __all__ confirms `probabilistic` is exported.
- README probabilistic example runs end-to-end: strategy='exact_enum', acceptance probs computed, extension_probability=0.774.
- README Dung example outputs verified: grounded=frozenset(), preferred=[{b},{a,c}], stable=[{b},{a,c}], complete=[{},{b},{a,c}]. Matches the comments in the README within set ordering.

### REMAINING
- Could add a tiny module-doc improvement to src/argumentation/__init__.py (one-line docstring is thin given the package now spans probabilistic + revision + partial). LOW PRIORITY — Q said "everything else" but rewriting __init__.py module doc may not be worth the churn. Hold and ask.
- Could tidy aspic.py docstring header to mention partial / probabilistic context. LOW PRIORITY.
- Untracked src/argumentation/probabilistic*.py — these are Q's WIP. NOT mine to commit.
- notes/ directory is not gitignored — may want to add. Defer to Q.

### FILES TOUCHED
- README.md (rewritten)
- pyproject.toml (rewritten with metadata)
- docs/architecture.md (rewritten with probabilistic + invariants)
- CONTRIBUTING.md (deleted)
- notes/readme-overhaul.md (this)

### NEXT
- Report status to Q.
