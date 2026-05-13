# DG Treewidth Workstream Design — 2026-05-01

Subagent task: write `reports/workstream-dg-treewidth.md` (~2000-3500 words) covering Fichte 2021 + Mahmood 2025 DG/DDG encodings, with concrete phase plan slotting into existing `argumentation` codebase.

## Observations so far

- **Codebase entry points read:**
  - `src/argumentation/sat_encoding.py` — flat CNF stable encoder (`encode_stable_extensions`), Z3-backed `sat_stable_extension`, brute-force enumeration over masks. Uses one variable per argument; the "in or attacked" clause exactly matches the naive `inOrX_R(E)` Fichte calls out as treewidth-breaking.
  - `src/argumentation/aba_sat.py` — `_SupportState` with bitmask-precomputed minimal supports; Z3 stable solver iterates over assumptions, asserting `var ↔ ¬any(attack_support_selected)`. Built around minimal support sets — non-trivial to retrofit DG since the natural primal graph here is over assumptions, not arguments.
  - `src/argumentation/dung.py` — `ArgumentationFramework` with `arguments`, `defeats`, optional `attacks`. `_attackers_index` already provides reverse-adjacency.
  - `src/argumentation/probabilistic_treedecomp.py` — already has `TreeDecomposition`, `NiceTDNode`, `NiceTreeDecomposition` dataclasses. Adapter currently for grounded DP only and explicitly notes "row count O(2^|defeats| * 2^|args|) — zero asymptotic improvement". This is reusable scaffolding; the bag-walk infrastructure is partially there.
  - `src/argumentation/aba.py` — `ABAFramework` with `language`, `rules`, `assumptions`, `contrary`. Flat ABA only.

- **Paper notes read:**
  - Fichte 2021 `notes.md` — full set of formulas (1-11) plus Theorem 5 (|χ'(t)| ≤ 5·|χ(t)| for stable). Bound table on p.6 is gold for the report.
  - Mahmood 2025 `claims.yaml` — claims 1-15 extracted. **Key:** claim14 explicitly notes "no experimental evaluation". Mahmood notes.md does NOT exist — only claims.yaml, abstract.md, citations.md, description.md. I should not fabricate quotes from a notes.md that isn't there.
  - Dvorak 2012 has only `paper.pdf` and `pngs/` — no extracted notes/claims. I'll cite it as the FPT-baseline reference but cannot quote specific page-level details without reading the PDF.

## What's not yet done
- Skim Mahmood description.md/abstract.md to ground my report claims.
- Web-search ICCMA 2023/2024/2025 winners and any DG implementation status.
- Look at htd / jdrasil / FlowCutter / networkx TD options.
- Then write the report.

## Current blocker
None — I have enough to proceed. Just paused for the checkpoint hook.

## Plan for the report
1. Tech summary with worked 5-arg AF example (e.g., star K_{1,4} where treewidth = 1 but naive encoding's in-or-attacked clause has all 5 vars in one clause → primal-graph clique).
2. Evidence base — quote Fichte formulas 1, 3, 4, 5, 8-11 verbatim from notes.md; cite Mahmood claims 1-5, 11, 14 by id; flag that no implementation exists yet.
3. Phase 0-5 plan slotting into existing files: new module `dg_encoding.py` next to `sat_encoding.py`; reuse `probabilistic_treedecomp.TreeDecomposition`; extend `aba_sat.py` with optional DG path.
4. Risks: ICCMA flat-encoding dominance; TD heuristic engineering cost; Python overhead vs C bindings; Mahmood clique-width vs Fichte treewidth tradeoff.
5. Open questions for Q — concrete ones around: TD library choice, ABA-DG novelty risk appetite, model counting backend (sharpSAT-TD vs Ganak), benchmark family construction, whether Z3 or external CDCL (CaDiCaL) is the target.
