# Paper-derived code corrections

## Goal
Correct the five confirmed implementation mismatches identified after the visual paper-note audit. Make each correction its own commit, then publish the complete series as one PR. Q authorized this on 2026-10-19; the earlier "make it so" remains in the session. Leave the PR open for review; do not merge it under the earlier notes-only integration instruction.

## State
Branch `fix/paper-code-corrections` starts at origin/main `1e1029e5539c3783dcabca95b0e958761867814a` in `C:/Users/Q/code/argumentation-paper-code-corrections`. All five scoped corrections are implemented and checked against the original paper page images. Four separate commits already exist: `6a2a33a` (impact), `d308240` (distance), `152277f` (expansion), and `4682283` (classification). The fifth commit contains transposition closure and this record update. No local tests, typecheck, build, or other CI steps have run. Publication and hosted CI are next. Preserve the primary checkout's uncommitted audit record and all unrelated artifacts. The failed old temporary-directory cleanup is outside this task.

## Decisions and why
- Smallest change: fix the existing functions and the existing assertions/generators that encode their incorrect contracts. Roughly 100-180 production lines and comparable or fewer test/doc lines across five commits; no new public framework, flags, compatibility facade, solver optimization, or new guards.
- Commit 1: revised impact removes external attacks entering X, and target-preserving node deletion removes edges touching all of X. Correct existing self-attack expectations. About 20-35 production lines.
- Commit 2: PAF edit distance charges 0/0.5/1 per Definition 18; update objective annotations and existing expectations. About 10-20 production lines.
- Commit 3: consensual expansion receives the profile, imports uncontested outside relations, and is used by the existing merge operators. Update all current callers/docs and assertions. About 35-65 production lines.
- Commit 4: classify Cayrol extension-family changes using the paper's cardinalities, quantifiers, and decisive precedence. Correct existing mistaken tests. About 15-30 production lines.
- Commit 5: transposition closure retains all seed strict rules and generated transpositions; remove unsupported pruning and revise existing generator restrictions. About 10-25 production lines removed/changed.
- Paper evidence is exclusively original page images in the primary checkout. No extraction, OCR, or extracted-paper-text navigation. No local CI steps; use hosted PR CI. No new tests/guards; correct existing tests where they encode a wrong contract.
- Workers own disjoint source/test/doc paths and do not commit. The primary stages only each correction's owned paths and commits them separately. PAF distance and expansion share files and therefore run sequentially.
- Consensual expansion now takes the full profile as its second argument; all repository callers and API documentation were updated. Passing only a universe cannot determine the paper's consensual relations.
- The closure correction removes unsupported pruning rather than adding machinery. Its existing nontrivial-argument property now excludes a rule whose consequent is already an antecedent, matching the argument builder's existing restriction to non-repeating conclusion paths. Changing argument enumeration is outside these five corrections.

## Source evidence
- AlAnaissy 2024 original images 001,003-004: external incoming attacks, node/edge deletion, self-attack example.
- Coste-Marquis 2007 original images 006-010: generic versus consensual expansion, Example 14, edit distance.
- Cayrol (local 2014 directory, actual 2010 publication) original images 006,008-011,016: structural classifications and examples.
- Prakken 2010 original image 012: Definitions 5.1-5.3, extensive closure under every transposition.

## Surprises
The existing tests asserted positive self-impact and whole-unit ignorance distance, accepted expansive classification with unequal family counts, and excluded valid transpositions. Those expectations and generator restrictions are corrected alongside the implementation. The argument builder still restricts repeated conclusions; this series does not claim to settle broader argument-enumeration completeness.

## Next step
Commit closure as the fifth correction, then push and open one combined PR for hosted validation on its exact head. Leave the PR open. Stop and report any execution/check failure under the standing instructions.
