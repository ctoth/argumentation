---
title: "Crustabri (ICCMA 2023 solver description)"
authors: "Jean-Marie Lagniez, Emmanuel Lonca, Jean-Guy Mailly"
year: 2023
venue: "ICCMA 2023 solver descriptions (bundled)"
status: STUB — full description not retrieved open-access
---

# Crustabri — ICCMA 2023 Abstract Argumentation Reasoner (STUB)

## Status: could not fetch full system description open-access
This is a **stub**. Crustabri's dedicated ICCMA 2023 system-description document is bundled in the ICCMA 2023 solver-and-benchmark descriptions collection, which is hosted at the University of Helsinki repository and was **not machine-retrievable**:

- Bundle handle: https://hdl.handle.net/10138/565357 → redirects to `helda.helsinki.fi`, which is behind an **Anubis anti-bot challenge** (returns a "Making sure you're not a bot!" page, not the PDF). Fetch attempts on 2026-07-09 failed for this reason.
- The ICCMA 2023 solvers page (https://iccma2023.github.io/solvers.html) lists Crustabri (authors Lagniez, Lonca, Mailly) with only a solver **code** download (`solvers/crustabri.zip`), no description PDF link.
- No standalone open-access Crustabri paper (arXiv / proceedings) was found; the only cited standalone paper for the tool family is the predecessor **CoQuiAAS** (ICTAI 2015), which is paywalled at IEEE.

**To obtain the full description later:** open `helda.helsinki.fi/handle/10138/565357` in a real browser (passes the Anubis challenge) and download the bundled solver-descriptions PDF, or email the authors. Alternatively read the source at https://github.com/crillab/crustabri.

## What is known from public sources (ICCMA 2023 site, docs.rs, author pages)
Enough to place the solver; **not** verified against the primary description text.
- **Crustabri** = "RUST ABstract argumentation Reasoner Implementation". Written in **Rust**.
- It is a **SAT-based** reasoner, described as a **rewrite of CoQuiAAS** (the authors' earlier C++ constraint/SAT solver; ICCMA 2015 winner, 2017 GR-track winner, 2019 runner-up).
- Uses an **iterative SAT-based approach with CaDiCaL** as the backend SAT solver.
- Supports **all sub-tracks in the Main track and the ABA track**, plus **DC-CO, DC-ST, DS-ST** in the Dynamic track.
- ICCMA 2023 results: ranked **first in ~11 sub-tracks** across Main and Dynamic, including DC-ST, DC-STG, DS-SST, DS-ST, DS-STG, SE-PR, SE-SST, SE-ST, SE-STG.
- An IPAFAIR interface exists (`crustabri_ipafair` on crates.io/docs.rs) for incremental dynamic reasoning.
- Repo: https://github.com/crillab/crustabri (CRIL / crillab group).

## Likely-transferable techniques (to confirm against the real description)
- **Iterative/incremental SAT with CaDiCaL** — same architectural family as `Niskanen_2020_MuToksiaEfficientAbstractArgumentationReasoner` (single persistent incremental SAT solver, tasks as solve-under-assumptions). Crustabri is a second independent data point that this is the winning design.
- **CoQuiAAS lineage**: grounded via unit propagation, SAT-encoded complete labellings, CEGAR for the Σ₂ᵖ tasks (as in CoQuiAAS/mu-toksia). Worth confirming which CEGAR refinements Crustabri adds.
- **Rust implementation** — a memory-safe alternative to the C++ solvers; relevant only if reimplementation language is ever considered.
- **IPAFAIR incremental interface** for the Dynamic track — the analogue of mu-toksia's selector-variable attack toggling.

## Relevance to Project
Crustabri is the strongest ICCMA 2023 Main/Dynamic-track competitor and shares the incremental-SAT architecture the project is targeting. Once the real description is retrieved, cross-check its DC-ST / DS-ST / SE-* routing against the project's solver and against mu-toksia's task→primitive map. For the ABA track note that Crustabri also entered ABA, so it is a comparison point for the ABA workstream alongside `Lehtonen_2021_DeclarativeAlgorithmsComplexityABA` (ASPforABA).

## Citations (best available)
- Lagniez, J.-M.; Lonca, E.; Mailly, J.-G. 2023. Crustabri. ICCMA 2023 solver description (bundled), https://iccma2023.github.io/solvers.html. Code: https://github.com/crillab/crustabri.
- Predecessor: Lagniez, J.; Lonca, E.; Mailly, J. 2015. CoQuiAAS: A constraint-based quick abstract argumentation solver. In Proc. ICTAI, 928-935. IEEE.
- Context: Bistarelli, Kotthoff, Lagniez, Lonca, Mailly, Rossit, Santini, Taticchi. 2025. ICCMA 2023: 5th International Competition on Computational Models of Argumentation. Artificial Intelligence (ScienceDirect S000437022500030X).
