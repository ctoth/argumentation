# Wave B1 — Pin down the SCC-recursive algorithm for AF semantics

You are a research subagent. You have web access. Working dir: `C:\Users\Q\code\argumentation`. You write a report; you do NOT change code.

## Goal

Produce `reports/scc-recursive-algorithm.md` — a precise, implementation-ready specification of the SCC-recursive schema for computing the **core extension-based semantics of Dung abstract argumentation frameworks**: complete, preferred, stable, semi-stable, stage. (Grounded is already O(V+E) and out of scope. Ideal is out of scope.) A coder will implement Python from your report and nothing else, so it must be self-contained and unambiguous.

## Why this is delicate

The naive "topologically process the SCCs" idea is wrong in the details. The real schema (Baroni, Giacomin & Guida, "SCC-recursiveness: a general schema for argumentation semantics", Artificial Intelligence 168 (2005) 162–210) handles, for each SCC `S`, three sets coming from already-processed predecessor SCCs:
- arguments of `S` attacked by an argument that is definitely accepted (IN) upstream → excluded from `S`;
- arguments of `S` attacked only by upstream arguments that are definitely rejected (OUT) → behave normally;
- arguments of `S` attacked by an upstream argument whose status is UNDEC (provisionally defeated / "D" set) → these need the special treatment that the base function `BF`/`GF` handles, and getting this wrong silently produces wrong extensions.

I want the exact recursion: the function signature (AF restricted to an SCC, plus the set of "externally undefined-attacked" arguments), the base case for a single SCC under each semantics, how partial extensions from each SCC are combined (cross-product over a topological order of the condensation), and how the per-semantics maximality (preferred, semi-stable, stage) interacts with the decomposition — note that SCC-recursiveness does NOT trivially commute with global maximality for all semantics, so be explicit about which of {complete, preferred, stable, semi-stable, stage} are genuinely SCC-recursive in BG&G's sense and which need care or are not decomposable this way.

## What to deliver in the report

1. **Which of the five semantics are SCC-recursive** per BG&G (and any later correction in the literature), with the citation. If one of them is *not* SCC-recursive, say so plainly and recommend "use flat SAT for that one" — do not have the coder fake it.
2. **The exact algorithm** for the ones that are: pseudocode for the recursive function, the base-semantics function for a single SCC, the combination step. Notation defined. Edge cases: empty AF, single SCC (whole AF is one SCC → degenerates to the base case = flat solve), self-attacks inside an SCC, an SCC of size 1.
3. **How it composes with the Wave A preprocessing** (`src/argumentation/preprocessing.py` — read `reports/graph-speedup-wave-a-preprocessing.md` and `notes/graph-speedup-wave-a-preprocessing.md`): the residual AF post-grounded-reduct is the input; confirm the SCC recursion is sound on the residual.
4. **What the codebase already has to build on**: read `src/argumentation/dung.py` — it has `_strongly_connected_components` (Tarjan, ~line 410), `_component_defeated` (~line 491), and a worked SCC-recursive loop in `_is_cf2_extension` / `_is_stage2_extension` / their enumerators (~lines 516–579). Note exactly what's reusable and what isn't (CF2/stage2 use a *different* base case — naive sets — so the loop shape transfers but the base function doesn't).
5. **Expected speedup & when it helps / hurts**: layered AFs with many small SCCs → big win; one giant SCC → pure overhead (so the implementation should detect single-SCC and skip straight to flat SAT). Any reported numbers from ArgSemSAT / ConArg / ICCMA you can find.
6. **Reference implementations to cross-check against**: ASPARTIX-V encodings, ConArg, ArgSemSAT (Cerutti, Giacomin, Vallati — arXiv:1310.4986), pyglaf, the ICCMA solver descriptions. Links/citations.

## Paper retrieval

Try to get the BG&G AIJ 2005 paper: DOI `10.1016/j.artint.2005.05.006`. ScienceDirect will likely 403; try sci-hub mirrors via Chrome if available, or find an author preprint / a survey that reproduces the schema verbatim (Baroni-Caminada-Giacomin "An introduction to argumentation semantics", KER 2011, reproduces a lot of it; Dvořák & Gaggl have treatments too). Also re-check `papers/Cerutti_2014_SCC_SAT_PreferredExtensions.pdf` — the previous researcher said arXiv served a password-locked PDF; try re-downloading `https://arxiv.org/pdf/1310.4986` or the published version. Whatever you successfully retrieve, note it and cite page/section numbers; whatever you can't, say so and rely on the secondary sources you *can* read — but be explicit about which claims rest on which source.

## Hard rule

Do not guess the algorithm. Every step of the pseudocode must be traceable to a source you actually read (cite it). If you cannot pin a step down from a readable source, flag it as "UNRESOLVED — coder must verify against oracle tests" rather than inventing it. Soundness of the final implementation depends entirely on this report being right.
