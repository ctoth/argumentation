---
title: "Solver and Benchmark Descriptions of ICCMA 2023: 5th International Competition on Computational Models of Argumentation"
authors: "Matti Järvisalo, Tuomo Lehtonen, Andreas Niskanen (editors)"
year: 2023
venue: "University of Helsinki Department of Computer Science, Series of Publications B, Report B-2023-3"
doi_url: "https://hdl.handle.net/10138/565357"
pages: 40
note: "Provenance: read directly from pngs/page-000.png through page-039.png generated from the canonical HELDA PDF."
---

# Solver and Benchmark Descriptions of ICCMA 2023

## One-Sentence Summary

This volume documents the solver architectures submitted to ICCMA 2023 and one benchmark generator, with especially actionable descriptions of incremental SAT, ASP, tree-decomposition, learned approximation, gradual-score approximation, dynamic argumentation, and ABA-to-AF translation techniques. *(pp.3, 5-6)*

## Problem Addressed

ICCMA encourages systems for reasoning in argumentation formalisms and supplies challenging benchmarks; the fifth edition covered exact abstract argumentation, approximate abstract argumentation, dynamic reasoning over related frameworks, and structured assumption-based argumentation (ABA). *(p.3)* The main track required sequential open-source exact solvers, while a no-limits subtrack admitted systems using capabilities such as parallel computation; the approximate track accepted inexact answers under a time-oriented regime; the dynamic track used the IPAFAIR API; and the ABA track debuted in 2023. *(p.3)*

## Key Contributions

- A compact primary-source record of 12 submitted solvers—AFGCN v2, ARIPOTER-Degrees, ARIPOTER-hcat, ASTRA, AcbAr, ASPforABA, Crustabri, fargo-limited, flexABle, Fudge, harper++, k-Solutions, mu-toksia, and PORTSAT—and the Crusti_g2io benchmark generator. *(pp.5-6)*
- Cross-paradigm implementation descriptions spanning SAT and incremental SAT, ASP/Clingo, dynamic programming on tree decompositions, bounded ABA-to-AF instantiation, GCN inference, gradual scoring, and depth-limited search. *(pp.8-35)*
- The direct Crustabri description: a Rust rewrite/evolution of CoQuiAAS using iterative CaDiCaL calls, direct maximal-subset enumeration, selector-based dynamic updates, and ABA-to-AF translation. *(p.20)*

## Competition Structure and Reasoning Surface

- Exact semantics named by the editors are complete, stable, semi-stable, stage, and ideal; reasoning problems include credulous acceptance, skeptical acceptance, and finding a single extension. *(p.3)*
- The four tracks were Main, Approximate, Dynamic, and ABA. Main was sequential/open-source exact reasoning; Approximate allowed incorrect answers but rewarded shorter time; Dynamic queried sequences of related AFs through IPAFAIR; ABA targeted the logic-programming fragment of assumption-based argumentation. *(p.3)*

## Solver-by-Solver Methods and Implementation Details

### AFGCN v2

- Approximates credulous or skeptical acceptance with a graph convolutional network trained on instances from earlier competitions under a randomized regime intended to improve generalization. Runtime features include the grounded extension, random input features, graph coloring, PageRank, closeness centrality, eigenvector centrality, and in/out degrees. *(pp.8-9)*
- The network has an input layer, four repeated GCN-plus-dropout blocks, residual connections that reintroduce original features and normalized adjacency at each block, and a sigmoid output giving an acceptance probability for every argument. Training uses Adam, binary cross-entropy, variable learning rate, dynamic rebalancing, and automated outlier exclusion. *(p.8)*
- Raw per-node feature vectors are standardized to zero mean and unit variance. The final model has four layers with 128 features per layer. Implementation uses Python, PyTorch, Deep Graph Library, and NumPy. *(p.9)*
- At runtime a shell wrapper loads task-specific parameters, computes the grounded extension with a NumPy solver, performs inference for all arguments in parallel, applies a threshold adapted to semantics and AF size, and prints only the queried argument’s predicted status. It entered only the Approximate track and supports DC/DS for CO, PR, ST, SST, STG plus DS-ID. *(p.9)*

### ARIPOTER-Degrees

- First applies grounded reasoning: an argument in the grounded extension is accepted for all considered semantics except stage; an argument attacked by the grounded extension is rejected. Remaining arguments are classified by comparing out-degree and in-degree. *(pp.10-11)*

$$
\delta^+(a) > k\,\delta^-(a)
$$

Where $\delta^+(a)$ and $\delta^-(a)$ are the out-degree and in-degree of argument $a$, and $k$ is a task-calibrated real parameter; the solver answers YES when $a$ is grounded or the inequality holds, otherwise NO. *(p.11)*

- Java implementation stores each AF as double adjacency lists (attackers and attacked arguments) and exposes `ArgumentationFramework` plus an abstract `Solver.solve` surface. *(p.11)*

| Name | Symbol | Units | Default | Range | Page | Notes |
|---|---|---:|---:|---:|---:|---|
| Degree ratio, DC-CO | $k$ | - | $|A|$ | - | 11 | Experimental choice |
| Degree ratio, DC-ST | $k$ | - | $|A|$ | - | 11 | Experimental choice |
| Degree ratio, DS-ST | $k$ | - | 0.1 | - | 11 | Experimental choice |
| Degree ratio, DC-ID | $k$ | - | $|A|$ | - | 11 | DS-ID is equivalent |
| Degree ratio, DC-SST | $k$ | - | $|A|$ | - | 11 | Experimental choice |
| Degree ratio, DS-SST | $k$ | - | $|A|$ | - | 11 | Experimental choice |
| Degree ratio, DC-STG | $k$ | - | 0 | - | 11 | Experimental choice |
| Degree ratio, DS-STG | $k$ | - | $|A|$ | - | 11 | Experimental choice |

### ARIPOTER-hcat

- Uses grounded reasoning for immediately determined arguments, then classifies unresolved arguments with the classical h-categorizer gradual semantics. *(pp.12-13)*

$$
\operatorname{hcat}(a,F)=\frac{1}{1+\sum_{(b,a)\in R}\operatorname{hcat}(b,F)}
$$

Where $F=(A,R)$ and the recursively defined score lies in $(0,1]$. *(p.12)*

$$
a\in GR(F)\;\lor\;\operatorname{hcat}(a,F)\geq\tau
$$

Where $\tau\in[0,1]$ is calibrated by task; the solver answers YES exactly when the disjunction holds. *(p.13)*

- Java implementation again uses double adjacency lists and the `ArgumentationFramework`/abstract `Solver.solve` structure. The authors propose adding other gradual semantics in future. *(p.13)*

| Name | Symbol | Units | Default | Range | Page | Notes |
|---|---|---:|---:|---:|---:|---|
| h-categorizer threshold, DC-CO | $\tau$ | - | 0.5 | 0-1 | 13 | Experimental choice |
| h-categorizer threshold, DS-PR | $\tau$ | - | 1 | 0-1 | 13 | Experimental choice |
| h-categorizer threshold, DC-ST | $\tau$ | - | 0.5 | 0-1 | 13 | Experimental choice |
| h-categorizer threshold, DS-ST | $\tau$ | - | 0 | 0-1 | 13 | Experimental choice |
| h-categorizer threshold, DC-ID | $\tau$ | - | 1 | 0-1 | 13 | DS-ID is equivalent |
| h-categorizer threshold, DC-SST | $\tau$ | - | 0.5 | 0-1 | 13 | Experimental choice |
| h-categorizer threshold, DS-SST | $\tau$ | - | 1 | 0-1 | 13 | Experimental choice |
| h-categorizer threshold, DC-STG | $\tau$ | - | 0 | 0-1 | 13 | Experimental choice |
| h-categorizer threshold, DS-STG | $\tau$ | - | 1 | 0-1 | 13 | Experimental choice |

### ASTRA

- Solves ABA through dynamic programming over a tree decomposition. D-FLAT constructs a decomposition using the `htd` library, then executes an ASP-specified DP algorithm; ASTRA parses the ABA/query/semantics, supplies an ASP encoding and parameters, and interprets D-FLAT output. *(pp.14-15)*
- Its underlying graph has atoms and rules as vertices; an atom connects to a rule when it appears in the rule head or body, and contrary atoms are connected. *(p.14)*
- Supports DC-CO, DC-ST, DS-CO, DS-ST, SE-CO, and SE-ST. *(p.15)*
- The architectural bet is that tree-width captures structural closeness and that bottom-up bag computation can make otherwise hard ABA reasoning tractable on bounded-treewidth instances. *(pp.14-15)*

### AcbAr

- Uses a polynomially bounded ABA-to-AF route: first removes circularity, then translates non-circular ABA to atomic ABA, instantiates a polynomial-size AF, and calls the SAT-based mu-toksia AF solver. *(pp.16-17)*
- Circularity removal copies rules and atoms to simulate derivations up to a height $k$ chosen as the size of the relevant rule-dependency SCC, preserving all derivations while eliminating repeated atoms on derivation paths. *(pp.16-17)*
- Atomic conversion introduces two assumptions for each body atom $a$: one for derivability $a_d$ and one for non-derivability $a_{nd}$; body occurrences become $a_d$, with contraries arranged between $a_d$, $a_{nd}$, and $a$. Each assumption and derivable rule then becomes an AF argument. *(p.17)*
- Supports DC-CO, DC-ST, DS-ST, DS-PR, SE-ST, and SE-PR. *(p.17)*

### ASPforABA

- Encodes ABA directly in ASP over sets of assumptions, with nondeterministic assumption guesses, derivability rules, and a conflict-freeness constraint. Stable semantics additionally requires each excluded assumption’s contrary to be derived; complete semantics enforces self-defense and that every defended assumption is included. *(p.18)*
- SE needs one Clingo call. DC adds query derivability and treats satisfiability as credulous acceptance; DS searches for a counterexample and treats unsatisfiability as skeptical acceptance. DC-CO, DC-ST, DS-ST, and SE-ST need one call; DS-PR and SE-PR use multiple incremental Clingo calls. *(p.18)*
- Preferred reasoning is CEGAR-like: maximize a complete assumption set through iterative superset constraints. For DS-PR, require the query derivable, then seek a complete strict superset not deriving it; if found, it is a counterexample, otherwise exclude subsets of the maximized set and continue. Python’s Clingo interface preserves incremental computation. *(pp.18-19)*

### Crustabri — evolution from CoQuiAAS

- Crustabri is a Rust rewrite of CoQuiAAS and participates in every Main and Dynamic subtrack plus ABA, with the ABA limitation that it cannot test acceptance of atoms that are not assumptions. *(p.20)*
- It is intended as a reusable toolbox: multiple encodings, optional certificates, instance checking, extensible format I/O, and a competition CLI wrapper. SAT encodings are mainly inherited from CoQuiAAS, except stage semantics no longer needs additional variables. *(p.20)*
- CoQuiAAS treated its internal (co)MSS engine as a difficult-to-reuse black box. Crustabri instead uses CaDiCaL for both decision and optimization via iterative calls. This enables direct maximal-subset enumeration and improved results for ideal semantics and stage/semi-stable acceptance, although regression can occur when seeking a stage or semi-stable extension. *(p.20)*
- ABA is translated to an AF: deduction sets become arguments, and one argument attacks another when the first conclusion is the contrary of an assumption in the second. *(p.20)*
- Dynamic reasoning reuses one SAT solver throughout. Each attack’s constraints use a selector. Deleting an attack discards its selector; adding a replacement attack adds fresh constraints with a fresh selector. Adding an argument declares a variable; deleting an argument removes incident attacks and marks its SAT variable unused. *(p.20)*
- IPAFAIR packaging comprises the core Crustabri crate, Rust IPAFAIR bindings, and a composed Crustabri IPAFAIR crate, intended for publication on crates.io. *(p.20)*

## Parameters

The context-specific ARIPOTER parameter tables are preserved under their solver sections. The remaining operational constants and reported calibration points are consolidated here.

| Name | Symbol | Units | Default | Range | Page | Notes |
|---|---|---:|---:|---:|---:|---|
| AFGCN repeated GCN blocks | - | blocks | 4 | - | 8 | Each combines GCN and dropout |
| AFGCN hidden features per layer | - | features | 128 | - | 9 | Four-layer final runtime model |
| fargo-limited search depth | $n$ | recursive levels | not stated | $\mathbb{N}\cup\{\infty\}$ | 21-22 | Infinite depth is complete |
| k-Solutions witness budget | $k$ | extensions | 3 | $k\geq1$ | 29 | Submitted configuration |
| mu-toksia Glucose version | - | version | 4.1 | - | 31 | Main and Dynamic submissions |
| mu-toksia CryptoMiniSat version | - | version | 5.11.4 | - | 31 | Main-track alternative |
| Crusti_g2io random-link probability | - | - | 0.2 | 0-1 | 36 | Calibration runs |
| Crusti_g2io calibration timeout | - | minutes | 10 | - | 36 | Easy/medium classification |

## Methods & Implementation Details

### Algorithm A: Crustabri dynamic update lifecycle

1. Initialize one SAT solver and retain it across the complete update/query stream. *(p.20)*
2. Associate every attack’s constraints with a selector variable. *(p.20)*
3. On attack deletion, stop selecting the old constraint group; on addition, add a fresh constraint group with a fresh selector. *(p.20)*
4. On argument addition, allocate a variable; on deletion, remove incident attacks and mark its SAT variable unused. *(p.20)*
5. Invoke the existing semantic algorithm against the current selector state, preserving learned SAT information. *(p.20)*

### Algorithm B: fargo-limited admissible-superset search

1. If the current seed $S$ is admissible, return TRUE with that witness. *(p.22)*
2. If the remaining depth is zero, return FALSE. *(p.22)*
3. For each attacker $b$ of $S$ not already counterattacked by $S$, enumerate conflict-free candidate defenders $c$ that attack $b$. *(p.22)*
4. If no candidate defender exists for some $b$, return FALSE. *(p.22)*
5. Recursively search from $S\cup\{c\}$ with depth $n-1$; return TRUE on the first successful branch, otherwise FALSE. *(p.22)*

### Algorithm C: k-Solutions update reuse

1. Precompute up to $k=3$ witnesses of the query polarity: containing the query for credulous acceptance or omitting it for skeptical stable acceptance. *(pp.29-30)*
2. After each AF update, validate every stored witness by fixing its variables in a current-extension formula. *(p.30)*
3. Discard invalid witnesses. If any remains, answer directly without generating new witnesses. *(pp.29-30)*
4. Only when none remains, compute up to $k$ new witnesses with Z3. *(pp.29-30)*

### Algorithm D: AcbAr ABA-to-AF route

1. Detect circular derivations in rule-dependency SCCs. *(p.16)*
2. Copy rules/atoms up to the SCC-size derivation-height bound to obtain an equivalent non-circular ABA framework. *(pp.16-17)*
3. Replace body atoms by derivability assumptions and add paired non-derivability assumptions, producing atomic ABA in polynomial time. *(p.17)*
4. Instantiate a polynomial-size AF whose arguments are assumptions and derivable rules. *(p.17)*
5. Call mu-toksia and translate its AF answer back to ABA. *(pp.16-17)*

## Key Equations / Statistical Models

The two explicit scoring equations in the volume up to this point are the ARIPOTER degree-ratio decision inequality and the recursive h-categorizer score above. The remaining described solvers use logical encodings, search invariants, or learned models without printing further mathematical equations on their description pages. *(pp.8-20)*

## Figures of Interest

- **Fig. 1 (p.14):** ASTRA pipeline: ABA input enters a parser/ASP-encoding/parameter layer, D-FLAT performs tree-decomposition DP, and results return through ASTRA.
- **Fig. 1 (p.16):** AcbAr pipeline branches on circularity, modifies circular ABA, converts to atomic form, builds an AF, and calls mu-toksia.
- **Fig. 1 (p.24):** flexABle five-step dispute showing attacks between constructed arguments and where a conservative forward move can preempt an opponent branch.
- **Fig. 1 (p.29):** k-Solutions architecture separating witness-producing `AFSolver` from post-update `Validation`.
- **Figs. 1-2 (p.36):** Crusti_g2io outer/inner/link/final generation stages and concrete CLI invocation patterns.

## Effect Sizes / Key Quantitative Results

This system-description volume reports architectures and calibrated parameters rather than controlled benchmark effect sizes; no confidence intervals, p-values, or comparative runtime tables appear on pp.3-20. *(pp.3-20)*

### fargo-limited v1.1.1

- An approximate C++ solver using a DPLL-like exhaustive search for an admissible superset of a seed set, truncated at maximum recursion depth $n$. For DC it returns YES when the query is found in an admissible set. For DS it also tests whether any attacker of the query is in an admissible set; if the query has a witness and no attacker does, it returns YES. *(pp.21-22)*
- `admSuperSet(AF,S,n)` first succeeds when $S$ is admissible; fails when depth is exhausted; otherwise chooses each currently undefended attacker $b$ of $S$, fails if no conflict-free defender exists, and recursively adds a candidate defender $c$ with depth $n-1$. *(pp.21-22)*
- With $n=\infty$ the search is complete. At finite depth, FALSE may be wrong because the witness can lie deeper, while TRUE is always sound because an admissible set was actually found. This asymmetric contract is central to its suitability for an approximate track. *(pp.21-22)*

| Name | Symbol | Units | Default | Range | Page | Notes |
|---|---|---:|---:|---:|---:|---|
| Maximum admissibility-search depth | $n$ | recursive levels | not stated | $\mathbb{N}\cup\{\infty\}$ | 21-22 | Infinite depth is complete; finite depth preserves positive-answer soundness only |

### flexABle

- Implements flexible ABA dispute derivations in Scala for DC-CO and DC-ST. Dispute state remembers every introduced argument/subargument, supports argument-based and rule-based representations, permits backward and forward moves, and can compute complete/stable assumption sets rather than merely decide acceptance. *(pp.23-24)*
- The automated search strategy has three dimensions: move-type priority, rule-selection parameters, and breadth-first versus depth-first traversal. *(p.24)*
- ICCMA uses depth-first search and prioritizes proponent conservative forward moves. Complete reasoning disables non-conservative forward moves. Stable reasoning first seeks an admissible set without non-conservative forward moves, then extends it with such moves only when possible. *(p.24)*
- Figure 1’s worked dispute shows how a conservative forward move can preempt an opponent rule and shorten a five-step dispute to four steps. *(pp.23-24)*

### Fudge v3.2.8

- A C++ reduction-based solver using CaDiCaL 1.3.1. It combines standard SAT encodings with specialized encodings for DS-PR and ideal semantics that avoid expensive explicit extension maximization. Version 3.2.8 streamlines encodings/call patterns and adds semi-stable and stage support. *(pp.25-26)*
- For stable semantics, variables $in_a$ and $out_a$ represent membership and being attacked. The printed encoding is: *(p.25)*

$$
\Phi_1(AF)=\bigwedge_{a\in A}(\neg in_a\lor\neg out_a)
$$

$$
\Phi_2(AF)=\bigwedge_{a\in A}\left(out_a\leftrightarrow\bigvee_{(b,a)\in R}in_b\right)
$$

$$
\Phi_3(AF)=\bigwedge_{a\in A}(in_a\lor out_a)
$$

Together the formulas are satisfiable exactly when the AF has a stable extension, which can be read from the assignment. *(p.25)*
- DS-PR uses a characterization that considers admissible sets attacking an admissible query-containing set rather than computing preferred extensions. The ideal-extension method uses the fact that an admissible $S$ is ideal iff no attacker of $S$ belongs to an admissible set; the largest admissible subset of arguments not attacked by any admissible set is ideal. *(p.26)*

### harper++ v1.1.1

- Uses only the grounded extension as a polynomial-time approximation for CO, ST, PR, SST, STG, and ID. For DS it returns YES iff the query is grounded. For DC it returns NO iff the query is attacked by a grounded argument; otherwise YES. *(pp.27-28)*
- The motivating empirical observation from prior work is that, over 426 AFs compiled from ICCMA 2017 ABA frameworks, the Jaccard distance between the grounded extension and the set of arguments appearing in each or some preferred extensions averaged 0.03 and 0.05, respectively. *(p.27)*

| Name | Symbol | Units | Default | Range | Page | Notes |
|---|---|---:|---:|---:|---:|---|
| AF sample size in prior similarity study | - | frameworks | 426 | - | 27 | Compiled from ICCMA 2017 ABA inputs |
| Grounded-to-each-preferred Jaccard distance | $J$ | - | 0.03 | 0-1 | 27 | Prior empirical average |
| Grounded-to-some-preferred Jaccard distance | $J$ | - | 0.05 | 0-1 | 27 | Prior empirical average |

### k-Solutions

- Dynamic-track solver using Z3 and two components: `AFSolver` computes up to $k$ witness extensions, while `Validation` checks whether stored witnesses remain valid after changes. Invalid witnesses are discarded; recomputation occurs only when none remain. *(pp.29-30)*
- The submitted setting is $k=3$. For credulous admissibility/complete acceptance, witnesses contain the query; for skeptical stable acceptance, dual witnesses are stable extensions omitting it. A witness that survives a change answers the query immediately. *(pp.29-30)*
- Validation constructs a Boolean formula fixed to the witness variables and satisfiable exactly when that set remains an extension of the current AF. This is direct witness validation rather than re-solving the full acceptance problem after every update. *(p.30)*

| Name | Symbol | Units | Default | Range | Page | Notes |
|---|---|---:|---:|---:|---:|---|
| Stored witness budget | $k$ | extensions | 3 | $k\geq1$ | 29 | Submitted configuration |

### mu-toksia

- Incremental SAT solver covering all Main and Dynamic subtracks. Complete/stable tasks use direct encodings; preferred, semi-stable, and stage use SAT-based CEGAR; ideal iteratively identifies complete-extension arguments not attacked by any complete extension and extracts a subset-maximal extension. *(p.31)*
- Dynamic attack presence is represented by variables $r_{a,b}$ added to complete/stable encodings and fixed per solve. Argument existence is likewise represented for incomplete-AF encodings. Added-argument capacity uses a reserved variable buffer; when exhausted, the buffer doubles and the solver is reinitialized. *(p.31)*
- Main-track portfolios use Glucose 4.1 and CryptoMiniSat 5.11.4. Dynamic submissions use Glucose and compare a persistent dynamic encoding against a static restart-from-scratch variant. *(p.31)*

### PORTSAT

- Rust SAT portfolio for DC-CO, DC-ST, DS-PR, DS-ST, SE-PR, and SE-ST. Complete and stable semantics use propositional encodings; preferred extensions are obtained by largest-complete-extension enumeration, and DS-PR naively enumerates/checks all preferred extensions. *(pp.32-33)*
- Portfolio members are MiniSat; ManySat, which runs DPLL variants in parallel; MapleSAT, combining MiniSat with learned branching; and two Glucose variants with and without preprocessing. The authors report preprocessing tends to help hard problems, while the no-preprocessing version can be better on easy ones. *(p.33)*
- Future work explicitly proposes replacing naive DS-PR enumeration with CEGAR and adding semi-stable, stage, and ideal semantics. *(p.33)*

### Crusti_g2io benchmark generator

- Builds community-structured AFs from an outer skeleton graph, disjoint inner graphs replacing outer nodes, and a linker that connects inner graphs according to outer edges. Outer/inner generators can mix trees, paths, Erdos-Renyi, Barabasi-Albert, and Watts-Strogatz families. *(p.35)*
- Rust CLI supports directed/undirected generation, discoverable generators/linkers/output formats, Graphviz DOT, GraphML, APX, and ICCMA 2023 DIMACS output. Extension requires implementing four functions of a trait and registering the generator/linker/format. *(pp.35-36)*
- A supplied or random seed is always logged. Inner graphs and links are computed in parallel. *(p.36)*
- Authors calibrated SE-ST/SE-PR difficulty using Erdos-Renyi inner graphs, tree outer graphs, random linker probability 0.2, and a 10-minute timeout. For SE-ST, $(175,0.2,511)$ or $(125,0.5,31)$ were easy for mu-toksia 2019, $(225,0.1,31)$ or $(250,0.2,255)$ medium; increasing the first or third parameter, or decreasing the second, increases difficulty. For SE-PR, easy settings were $(150,0.1,255)$ or $(225,0.2,127)$, and medium settings were $(200,0.1,127)$, $(300,0.2,255)$, or $(350,0.5,255)$. *(p.36)*

| Name | Symbol | Units | Default | Range | Page | Notes |
|---|---|---:|---:|---:|---:|---|
| Random-link probability | - | - | 0.2 | 0-1 | 36 | Calibration runs |
| Calibration timeout | - | minutes | 10 | - | 36 | Difficulty classification |
| SE-ST easy tuple | $(n_{inner},p,n_{outer})$ | nodes, probability, nodes | $(175,0.2,511)$ | - | 36 | Alternative $(125,0.5,31)$ |
| SE-ST medium tuple | $(n_{inner},p,n_{outer})$ | nodes, probability, nodes | $(225,0.1,31)$ | - | 36 | Alternative $(250,0.2,255)$ |
| SE-PR easy tuple | $(n_{inner},p,n_{outer})$ | nodes, probability, nodes | $(150,0.1,255)$ | - | 36 | Alternative $(225,0.2,127)$ |
| SE-PR medium tuple | $(n_{inner},p,n_{outer})$ | nodes, probability, nodes | $(200,0.1,127)$ | - | 36 | Alternatives $(300,0.2,255)$, $(350,0.5,255)$ |

## Methodology

The volume is a collection of submitted system and benchmark descriptions, not one controlled comparison. Each contribution states its supported ICCMA tasks, core representation/algorithm, implementation language and backend, and selected operational parameters; direct result rankings are outside this volume. *(pp.5-36)*

## Results Summary

- Across exact solvers, incremental state reuse is implemented at different granularities: persistent SAT clauses/selectors in Crustabri and mu-toksia, incremental ASP solving in ASPforABA, and witness retention/validation in k-Solutions. *(pp.18-20, 29-31)*
- Hard second-level tasks are handled either by CEGAR/maximality loops (ASPforABA, mu-toksia), characterizations avoiding explicit preferred enumeration (Fudge), or naive enumerate-and-check (PORTSAT). *(pp.18-19, 25-26, 31-33)*
- Approximate solvers expose different correctness profiles: fargo-limited preserves sound positive answers at finite depth; AFGCN uses learned probabilities; ARIPOTER uses calibrated scores; harper++ uses deterministic grounded-based defaults. *(pp.8-13, 21-22, 27-28)*
- Community-structured generation gives a tunable family whose difficulty responds monotonically in the authors’ tested regimes to inner size, density, and outer size. *(pp.35-36)*

## Limitations

- Crustabri’s ABA path cannot check non-assumption atoms, may regress when seeking stage/semi-stable extensions, and its new maximal-subset enumeration lacks some advances of the older specialized engine. *(p.20)*
- AFGCN correctness depends on training generalization and thresholds rather than proof; fargo-limited finite-depth negative answers may be false; ARIPOTER and harper++ deliberately approximate unresolved statuses. *(pp.8-13, 21-22, 27-28)*
- ASTRA’s tree-decomposition benefit is structurally contingent; AcbAr pays for translations and circularity expansion; PORTSAT’s DS-PR method is acknowledged as naive. *(pp.14-17, 32-33)*
- k-Solutions only avoids recomputation while at least one stored witness survives; mu-toksia reinitializes when its reserved argument-variable buffer is exhausted. *(pp.29-31)*
- The volume contains architectural descriptions rather than standardized result tables or ablations, so it cannot by itself establish which technique caused competition performance. *(pp.5-36)*

## Arguments Against Prior Work

- Crustabri rejects CoQuiAAS’s embedded (co)MSS black-box integration as difficult to reuse mid-enumeration and replaces it with a generic iterative SAT backend. *(p.20)*
- AcbAr avoids conventional ABA argument construction because it can create exponentially many arguments; its atomic translation gives a polynomial AF after circularity handling. *(pp.16-17)*
- Fudge and the ASP/mu-toksia CEGAR routes avoid or reduce explicit preferred-extension enumeration, whereas PORTSAT identifies its enumerate-and-check DS-PR path as a target for replacement. *(pp.18-19, 25-26, 31-33)*
- flexABle argues earlier dispute derivations repeat arguments, restrict movement direction, and can induce dispute-tree limitations; its omniscient state and forward moves address these constraints. *(pp.23-24)*

## Design Rationale

- Persistent selectors/assumptions are the common mechanism for retaining solver learning across dynamic changes while toggling model facts. *(pp.20, 31)*
- Witness validation is useful when updates are small enough that prior solutions often remain valid; keeping multiple witnesses amortizes update sequences. *(pp.29-30)*
- The strongest exact solvers separate semantic encodings from iterative optimization/maximality orchestration, enabling one SAT/ASP backend to cover multiple tasks. *(pp.18-20, 25-26, 31-33)*
- Structure-sensitive routes exploit different forms of locality: treewidth for ASTRA, SCC-bounded derivation height for AcbAr, grounded kernels for approximate solvers, and community templates for benchmark generation. *(pp.10-17, 27-28, 35-36)*

## Testable Properties

- With finite depth, fargo-limited TRUE answers must correspond to an actual admissible witness; FALSE is not guaranteed complete. *(pp.21-22)*
- Crustabri attack deletion must deactivate the old selector and attack addition must allocate fresh constraints plus a fresh selector; argument deletion must remove incident attacks and retire its variable. *(p.20)*
- A k-Solutions update must not invoke witness generation while at least one previously stored witness still validates for the current AF and query polarity. *(pp.29-30)*
- mu-toksia’s dynamic/static variants must agree semantically; the dynamic version should retain one solver until its argument-variable buffer requires doubling/reinitialization. *(p.31)*
- AcbAr’s circularity transformation bound uses the size of each rule-dependency SCC as maximum derivation height and must preserve all possible derivations. *(pp.16-17)*
- Crusti_g2io must log the chosen seed, and equal seeds/configurations must reproduce the same output despite parallel inner/link generation. *(p.36)*
- In the reported Crusti_g2io calibration regime, increasing inner-node count or outer-node count, or lowering inner Erdos-Renyi edge probability, should increase SE-ST difficulty. *(p.36)*
- ARIPOTER-hcat scores must remain in $(0,1]$ and satisfy the recursive attacker equation. *(p.12)*

## Relevance to Project

The highest-value implementation patterns for this repository are the operational routes that can be stated as executable contracts: bounded solver calls for direct encodings, retained incremental state for dynamic updates, maximality/CEGAR only on the semantics that require it, witness validation before recomputation, and structure-gated routes for bounded-treewidth or bounded-SCC instances. *(pp.14-20, 25-33)* Crustabri and mu-toksia independently reinforce persistent SAT plus selector/assumption-based changes, while Fudge supplies a route-specific example of replacing preferred-extension enumeration with a direct characterization. *(pp.20, 25-26, 31)* Crusti_g2io supplies parameterized community structure useful for tests that distinguish topology-sensitive solver behavior from raw graph size. *(pp.35-36)*

## Open Questions

- [ ] Which exact CaDiCaL maximal-subset enumeration loop does Crustabri use, and which omitted advances from the older (co)MSS engine account for its stated regressions? *(p.20)*
- [ ] What selector lifecycle and clause-growth policy prevents dynamic Crustabri from accumulating excessive inactive constraints over long update streams? *(p.20)*
- [ ] What measured survival rate of $k=3$ witnesses justified k-Solutions’ submitted budget? *(pp.29-30)*
- [ ] On which structural classes does ASTRA’s tree-decomposition route outperform direct ABA SAT/ASP or ABA-to-AF translations? *(pp.14-19)*
- [ ] How do the community-generator parameters correlate with SCC structure, treewidth, and residual sizes observed by this project’s solvers? *(pp.35-36)*

## Related Work Worth Reading

- Lagniez, Lonca, and Mailly, “CoQuiAAS: A constraint-based quick abstract argumentation solver,” ICTAI 2015, for the predecessor encodings and specialized (co)MSS engine. *(p.20)*
- Niskanen and Järvisalo, “mu-toksia: An efficient abstract argumentation reasoner,” KR 2020, for detailed SAT/CEGAR algorithms. *(pp.17, 31)*
- Thimm, Cerutti, and Vallati, “Skeptical reasoning with preferred semantics in abstract argumentation without computing preferred extensions,” IJCAI 2021, for Fudge’s DS-PR characterization. *(p.26)*
- Lehtonen, Wallner, and Järvisalo, “Harnessing incremental answer set solving for reasoning in assumption-based argumentation,” TPLP 2021. *(p.19)*
- Lehtonen, Rapberger, Ulbricht, and Wallner, “Argumentation frameworks induced by assumption-based argumentation: Relating size and complexity,” KR 2023, for AcbAr’s polynomial construction. *(p.17)*

## Collection Cross-References

### Already in Collection

- [mu-toksia: An Efficient Abstract Argumentation Reasoner](../Niskanen_2020_MuToksiaEfficientAbstractArgumentationReasoner/notes.md) — cited by AcbAr and the mu-toksia submission; supplies the detailed incremental-SAT, CEGAR, and dynamic-selector algorithms summarized here.
- [Skeptical Reasoning with Preferred Semantics in Abstract Argumentation without Computing Preferred Extensions](../Thimm_2021_SkepticalReasoningPreferredSemantics/notes.md) — cited as the direct DS-PR characterization implemented by Fudge.
- [Declarative Algorithms and Complexity Results for Assumption-Based Argumentation](../Lehtonen_2021_DeclarativeAlgorithmsComplexityABA/notes.md) — cited as the full direct ASP foundation for ASPforABA.
- [Complexity-Sensitive Decision Procedures for Abstract Argumentation](../Dvorak_2014_ComplexitySensitiveDecisionProcedures/notes.md) — cited as the CEGAR foundation used by mu-toksia and identified by PORTSAT as the route that should replace its naive DS-PR enumeration.

### New Leads (Not Yet in Collection)

- Lagniez, Lonca, and Mailly (2015), “CoQuiAAS: A constraint-based quick abstract argumentation solver” — needed to compare Crustabri’s generic iterative CaDiCaL maximal-subset loop against the predecessor’s specialized (co)MSS machinery.
- Lehtonen, Rapberger, Ulbricht, and Wallner (2023), “Argumentation frameworks induced by assumption-based argumentation: Relating size and complexity” — formal source for AcbAr’s polynomial ABA-to-AF construction and SCC-bounded circularity handling.
- Niskanen and Järvisalo (2020), “Algorithms for dynamic argumentation frameworks: An incremental SAT-based approach” — full source for mu-toksia’s dynamic attack/argument existence-variable encoding.

### Supersedes or Recontextualizes

- The volume recontextualizes the earlier mu-toksia and Fudge papers as ICCMA 2023 submissions, documenting the submitted backend portfolios, dynamic/static variants, streamlined Fudge call pattern, and added semi-stable/stage surface. *(pp.26, 31)*

### Cited By (in Collection)

- [mu-toksia: An Efficient Abstract Argumentation Reasoner](../Niskanen_2020_MuToksiaEfficientAbstractArgumentationReasoner/notes.md) — its related-work notes identify the Crustabri description as the primary record of the CoQuiAAS successor.

### Conceptual Links (not citation-based)

- [Fudge: A light-weight solver for abstract argumentation based on SAT reductions](../Thimm_2021_FudgeLight-weightSolverAbstract/notes.md) — the standalone system paper gives the fuller baseline architecture; this volume records the ICCMA 2023 version’s changed SAT invocation, streamlined encodings, and added semi-stable/stage surface.
- [Reasoning in Assumption-Based Argumentation via SAT](../Niskanen_2025_ReasoningAssumptionBasedArgumentationSAT/notes.md) — later direct ABA SAT encodings provide a contrasting route to the 2023 systems’ direct ASP, tree-decomposition, dispute-derivation, and ABA-to-AF approaches.
