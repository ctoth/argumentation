# SOTA Paper Retrieval List

Date: 2026-04-26

Purpose: acquire local PDFs for the page-image reread gates in
`plans/sota-completeness-and-ecosystem-workstream-2026-04-26.md`.

Target location for retrieved PDFs:

- `papers/<slug>/paper.pdf`
- `papers/<slug>/metadata.json` if convenient, but the PDF is the
  important artifact.

Do not use extracted text as the paper-reading basis. The later
implementation gates need page images rendered from these PDFs.

## Retrieval Rules

- Prefer official publisher, proceedings, arXiv, institutional, or
  author-hosted PDFs.
- If only a landing page is listed, download the PDF linked from that
  landing page.
- Preserve the exact paper identity in the target slug.
- If a listed paper cannot be acquired, leave a short note in this file
  under the entry instead of substituting a nearby paper.
- Two entries below are marked `citation defect`; retrieve the corrected
  paper, not the mistaken citation text.

## Phase 1: Self-Confessed Surfaces

- [ ] `papers/popescu-wallner-2024-probabilistic-constellation-dp/paper.pdf`
  - Status: citation defect in the workstream. The plan says Meier,
    Niskanen, Mailly 2024 for arXiv `2407.05058`, but the matching
    paper is Popescu and Wallner 2024.
  - Title: Advancing Algorithmic Approaches to Probabilistic
    Argumentation under the Constellation Approach
  - Authors: Andrei Popescu; Johannes P. Wallner
  - Year: 2024
  - URL: `https://arxiv.org/abs/2407.05058`
  - URL: `https://proceedings.kr.org/2024/55/`

- [ ] `papers/lehtonen-odekerken-wallner-jarvisalo-2024-preferential-aspic/paper.pdf`
  - Title: Complexity Results and Algorithms for Preferential
    Argumentative Reasoning in ASPIC+
  - Authors: Tuomo Lehtonen; Daphne Odekerken; Johannes P. Wallner;
    Matti Jarvisalo
  - Year: 2024
  - URL: `https://proceedings.kr.org/2024/49/`

- [ ] `papers/niskanen-wallner-jarvisalo-2020-mu-toksia/paper.pdf`
  - Title: mu-toksia: An Efficient Abstract Argumentation Reasoner
  - Authors: Andreas Niskanen; Johannes P. Wallner; Matti Jarvisalo
  - Year: 2020
  - URL: `https://www.cs.helsinki.fi/u/mjarvisa/papers/nj.kr20b.pdf`

- [ ] `papers/lehtonen-wallner-jarvisalo-2020-aspic-asp/paper.pdf`
  - Title: An Answer Set Programming Approach to Argumentative Reasoning
    in the ASPIC+ Framework
  - Authors: Tuomo Lehtonen; Johannes P. Wallner; Matti Jarvisalo
  - Year: 2020
  - Note: needed for the ASPIC+ ASP backend, even though the workstream
    also cites the 2024 preferential ASPIC+ paper.

- [ ] `papers/gaggl-woltran-2013-cf2-sat/paper.pdf`
  - Status: exact citation should be pinned before implementation.
  - Purpose: CF2 SAT/backend work.

- [ ] `papers/sat-encodings-af-semantics-source-pack/paper.pdf`
  - Status: placeholder, do not fetch as one paper.
  - Purpose: Track 1.3 cites broad author families
    (Besnard-Doutre, Caminada, Gaggl-Woltran,
    Wallner-Niskanen-Jarvisalo). Exact paper identities must be pinned
    before retrieval.

## Phase 2: ICCMA Solver Ecosystem

- [ ] `papers/bistarelli-kotthoff-lagniez-etal-iccma-third-fourth-report/paper.pdf`
  - Title: The third and fourth international competitions on
    computational models of argumentation: Design, results and analysis
  - Authors: Bistarelli; Kotthoff; Lagniez; et al.
  - Year: 2024/2025 metadata to verify
  - URL: `https://www.eecs.uwyo.edu/~larsko/papers/bistarelli_third_2024.pdf`

- [ ] `papers/iccma-2025-tracks-and-rules/paper.pdf`
  - Status: HTML/spec, not a normal paper.
  - URL: `https://argumentationcompetition.org/2025/tracks.html`
  - URL: `https://argumentationcompetition.org/2025/rules.html`
  - Note: save as PDF from browser if no official PDF exists.

## Phase 3: Abstract Dialectical Frameworks

- [ ] `papers/brewka-woltran-2010-abstract-dialectical-frameworks/paper.pdf`
  - Title: Abstract Dialectical Frameworks
  - Authors: Gerhard Brewka; Stefan Woltran
  - Year: 2010

- [ ] `papers/brewka-strass-ellmauthaler-wallner-woltran-2013-adf-revisited/paper.pdf`
  - Title: Abstract Dialectical Frameworks Revisited
  - Authors: Gerhard Brewka; Hannes Strass; Stefan Ellmauthaler;
    Johannes P. Wallner; Stefan Woltran
  - Year: 2013

- [ ] `papers/linsbichler-pichler-spendier-2022-adf-sat-algorithms/paper.pdf`
  - Title: Advanced algorithms for abstract dialectical frameworks based
    on complexity analysis of subclasses and SAT solving
  - Authors: Thomas Linsbichler; Reinhard Pichler; Stefan Spendier
  - Year: 2022

- [ ] `papers/keshavarzi-zafarghandi-verbrugge-verheij-2022-strong-adf/paper.pdf`
  - Title: Strong Admissibility for Abstract Dialectical Frameworks
  - Authors: Atefeh Keshavarzi Zafarghandi; Rineke Verbrugge; Bart
    Verheij
  - Year: 2022
  - URL: `https://arxiv.org/abs/2012.05997`

## Phase 4: Assumption-Based Argumentation

- [ ] `papers/bondarenko-dung-kowalski-toni-1997-default-reasoning-aba/paper.pdf`
  - Title: An Abstract, Argumentation-Theoretic Approach to Default
    Reasoning
  - Authors: Andrei Bondarenko; Phan Minh Dung; Robert Kowalski;
    Francesca Toni
  - Year: 1997
  - DOI: `10.1016/S0004-3702(97)00015-5`

- [ ] `papers/toni-2014-aba-tutorial/paper.pdf`
  - Title: A tutorial on assumption-based argumentation
  - Author: Francesca Toni
  - Year: 2014
  - DOI: `10.1080/19462166.2013.869878`

- [ ] `papers/cyras-toni-2016-aba-plus/paper.pdf`
  - Title: ABA+: Assumption-Based Argumentation with Preferences
  - Authors: Kristijonas Cyras; Francesca Toni
  - Year: 2016
  - URL: `https://arxiv.org/abs/1610.03024`

- [ ] `papers/lehtonen-wallner-jarvisalo-2021-declarative-aba/paper.pdf`
  - Title: Declarative Algorithms and Complexity Results for
    Assumption-Based Argumentation
  - Authors: Tuomo Lehtonen; Johannes P. Wallner; Matti Jarvisalo
  - Year: 2021
  - URL: `https://www.cs.helsinki.fi/u/mjarvisa/papers/lwj.jair21.pdf`

- [ ] `papers/lehtonen-wallner-jarvisalo-2021-incremental-asp-aba/paper.pdf`
  - Title: Harnessing Incremental Answer Set Solving for Reasoning in
    Assumption-Based Argumentation
  - Authors: Tuomo Lehtonen; Johannes P. Wallner; Matti Jarvisalo
  - Year: 2021
  - URL: `https://arxiv.org/abs/2108.04192`

- [ ] `papers/apostolakis-saribatur-wallner-2024-aba-abstraction/paper.pdf`
  - Status: citation defect in the workstream. The plan names
    Apostolakis, Toni, Rapberger 2024, but the KR 2024 paper found is
    Apostolakis, Saribatur, Wallner.
  - Title: Abstraction in Assumption-based Argumentation
  - Authors: Iosif Apostolakis; Zeynep G. Saribatur; Johannes P.
    Wallner
  - Year: 2024
  - URL: `https://proceedings.kr.org/2024/5/`

- [ ] `papers/dimopoulos-dvorak-konig-rapberger-ulbricht-woltran-2024-aba-set-to-set/paper.pdf`
  - Title: Redefining ABA+ Semantics via Abstract Set-to-Set Attacks
  - Authors: Yannis Dimopoulos; Wolfgang Dvorak; Matthias Konig; Anna
    Rapberger; Markus Ulbricht; Stefan Woltran
  - Year: 2024
  - DOI: `10.1609/aaai.v38i9.28918`

## Phase 5: SETAFs

- [ ] `papers/nielsen-parsons-2006-setaf/paper.pdf`
  - Title: A Generalization of Dung's Abstract Framework for
    Argumentation: Arguing with Sets of Attacking Arguments
  - Authors: Soren Holbech Nielsen; Simon Parsons
  - Year: 2006
  - Note: landing pages found; direct PDF not confirmed in the
    availability pass.

- [ ] `papers/dvorak-konig-ulbricht-woltran-2024-setaf-principles/paper.pdf`
  - Title: Principles and their Computational Consequences for
    Argumentation Frameworks with Collective Attacks
  - Authors: Wolfgang Dvorak; Matthias Konig; Markus Ulbricht; Stefan
    Woltran
  - Year: 2024

- [ ] `papers/dvorak-konig-woltran-2025-setaf-parameterized-complexity/paper.pdf`
  - Title: Parameterized complexity of abstract argumentation with
    collective attacks
  - Authors: Wolfgang Dvorak; Matthias Konig; Stefan Woltran
  - Year: 2025
  - DOI: `10.1177/19462174251319186`

- [ ] `papers/flouris-bikakis-2024-collective-attack-justification/paper.pdf`
  - Title: Justifying argument acceptance with collective attacks:
    discussions and disputes
  - Authors: Giorgos Flouris; Antonis Bikakis
  - Year: 2024
  - Note: direct PDF not confirmed in the availability pass.

- [ ] `papers/buraglio-dvorak-konig-woltran-2024-setaf-splitting/paper.pdf`
  - Title: Splitting Argumentation Frameworks with Collective Attacks
  - Authors: Giovanni Buraglio; Wolfgang Dvorak; Matthias Konig;
    Stefan Woltran
  - Year: 2024
  - URL: `https://ceur-ws.org/Vol-3757/paper3.pdf`

## Phase 6: Enforcement

- [ ] `papers/baumann-2012-enforce-argument/paper.pdf`
  - Title: What does it take to enforce an argument? Minimal change in
    abstract argumentation
  - Author: Ringo Baumann
  - Year: 2012
  - Note: direct PDF not confirmed in the availability pass.

- [ ] `papers/wallner-niskanen-jarvisalo-2017-extension-enforcement/paper.pdf`
  - Title: Complexity Results and Algorithms for Extension Enforcement
    in Abstract Argumentation
  - Authors: Johannes P. Wallner; Andreas Niskanen; Matti Jarvisalo
  - Year: 2017
  - DOI: `10.1613/jair.5415`

- [ ] `papers/baumann-doutre-mailly-wallner-2021-enforcement-survey/paper.pdf`
  - Title: Enforcement in Formal Argumentation
  - Authors: Ringo Baumann; Sylvie Doutre; Jean-Guy Mailly; Johannes P.
    Wallner
  - Year: 2021

- [ ] `papers/mailly-2024-constrained-incomplete-af-enforcement/paper.pdf`
  - Title: Constrained incomplete argumentation frameworks:
    expressiveness, complexity and enforcement
  - Author: Jean-Guy Mailly
  - Year: 2024
  - Note: direct PDF not confirmed in the availability pass.

## Phase 7: Claim-Augmented Argumentation Frameworks

- [ ] `papers/dvorak-gressler-rapberger-woltran-2023-caf-complexity/paper.pdf`
  - Title: The complexity landscape of claim-augmented argumentation
    frameworks
  - Authors: Wolfgang Dvorak; Alexander Gressler; Anna Rapberger;
    Stefan Woltran
  - Year: 2023
  - DOI: `10.1016/j.artint.2023.103873`

- [ ] `papers/dvorak-rapberger-woltran-2020-claim-centric-semantics/paper.pdf`
  - Title: Argumentation Semantics under a Claim-centric View:
    Properties, Expressiveness and Relation to SETAFs
  - Authors: Wolfgang Dvorak; Anna Rapberger; Stefan Woltran
  - Year: 2020
  - URL: `https://www.dbai.tuwien.ac.at/staff/dvorak/files/kr2020_clsemantics.pdf`

- [ ] `papers/alfano-greco-parisi-trubitsyna-2025-featured-af/paper.pdf`
  - Title: Featured Argumentation Framework: Semantics and Complexity
  - Authors: Gianvincenzo Alfano; Sergio Greco; Francesco Parisi;
    Irina Trubitsyna
  - Year: 2025
  - URL: `https://www.ijcai.org/proceedings/2025/0480.pdf`

## Phase 8: Dynamic And Incremental Reasoning

- [ ] `papers/iccma-2025-dynamic-track/paper.pdf`
  - Status: HTML/spec, not a normal paper.
  - URL: `https://argumentationcompetition.org/2025/tracks.html`
  - URL: `https://argumentationcompetition.org/2025/rules.html`
  - Note: save as PDF from browser if no official PDF exists.

- [ ] `papers/dynamic-af-source-to-pin/paper.pdf`
  - Status: placeholder, do not fetch as one paper.
  - Purpose: the plan says "Greenwood et al. or
    Alfano-Greco-Parisi 2018"; exact source must be chosen before
    retrieval.

- [ ] `papers/fichte-hecher-meier-2024-counting-complexity-argumentation/paper.pdf`
  - Title: Counting Complexity for Reasoning in Abstract Argumentation
  - Authors: Johannes K. Fichte; Markus Hecher; Arne Meier
  - Year: 2024
  - DOI: `10.1613/jair.1.16210`
  - URL: `https://arxiv.org/abs/1811.11501`

## Phase 9: Approximate And k-Stable Semantics

- [ ] `papers/skiba-thimm-2024-k-stable-approximation/paper.pdf`
  - Title: Optimisation and Approximation in Abstract Argumentation:
    the Case of k-Stable Semantics
  - Authors: Kenneth Skiba; Matthias Thimm
  - Year: 2024
  - URL: `https://www.mthimm.de/pub/2024/Thimm_2024.pdf`

- [ ] `papers/thimm-2014-ranking-approximate-semantics/paper.pdf`
  - Status: exact citation should be pinned before implementation.
  - Purpose: ranking-based approximate semantics.

- [ ] `papers/kuhlmann-thimm-2019-gcn-approximate-argumentation/paper.pdf`
  - Title: Using Graph Convolutional Networks for Approximate Reasoning
    with Abstract Argumentation Frameworks
  - Authors: Julius Kuhlmann; Matthias Thimm
  - Year: 2019
  - URL: `https://www.mthimm.de/pub/2019/Kuhlmann_2019.pdf`

## Phase 10: Epistemic Graphs

- [ ] `papers/hunter-polberg-thimm-2020-epistemic-graphs/paper.pdf`
  - Title: Epistemic graphs for representing and reasoning with
    positive and negative influences of arguments
  - Authors: Anthony Hunter; Sylwia Polberg; Matthias Thimm
  - Year: 2020
  - URL: `https://arxiv.org/abs/1802.07489`

- [ ] `papers/hunter-thimm-2014-epistemic-extensions-incomplete-information/paper.pdf`
  - Title: Probabilistic Argumentation with Epistemic Extensions and
    Incomplete Information
  - Authors: Anthony Hunter; Matthias Thimm
  - Year: 2014
  - URL: `https://arxiv.org/abs/1405.3376`

- [ ] `papers/potyka-polberg-hunter-2019-polynomial-epistemic-updates/paper.pdf`
  - Status: citation defect in the workstream. The plan says
    Bona-Hunter-Vesic 2019, but the matching paper found is
    Potyka-Polberg-Hunter 2019.
  - Title: Polynomial-time Updates of Epistemic States in a Fragment of
    Probabilistic Epistemic Argumentation
  - Authors: Nico Potyka; Sylwia Polberg; Anthony Hunter
  - Year: 2019
  - URL: `https://arxiv.org/abs/1906.05066`

## Phase 11: Argumentative LLM Surfaces

- [ ] `papers/freedman-dejl-gorur-yin-rago-toni-2025-argllm/paper.pdf`
  - Title: Argumentative Large Language Models for Explainable and
    Contestable Claim Verification
  - Authors: Gabriel Freedman; Adam Dejl; Deniz Gorur; Xiang Yin;
    Antonio Rago; Francesca Toni
  - Year: 2025
  - URL: `https://arxiv.org/abs/2405.02079`
  - DOI: `10.1609/aaai.v39i14.33637`

## Lowest-Priority Follow-Ups

- [ ] Replace every placeholder entry with exact paper identities before
  the corresponding implementation phase starts.
- [ ] After PDFs land locally, render page images for each gate and mark
  the entry with the page-image directory.
- [ ] Update the main workstream to correct the citation defects before
  implementing the affected tracks.
