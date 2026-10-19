---
title: "Argumentative Large Language Models for Explainable and Contestable Claim Verification"
authors: "Gabriel Freedman, Adam Dejl, Denis Gorur, Xiang Yin, Antonio Rago, Francesca Toni"
year: 2025
venue: "AAAI 2025"
doi_url: "https://github.com/GabrielFreworworking/ArgLLMs"
affiliation: "Department of Computing, Imperial College London, UK"
---

# Argumentative Large Language Models for Explainable and Contestable Claim Verification

## One-Sentence Summary
This paper presents ArgLLMs, a method that uses LLMs to generate pro/con arguments with confidence scores, constructs Quantitative Bipolar Argumentation Frameworks (QBAFs), and applies DF-QuAD gradual semantics to produce explainable and contestable claim verification verdicts. *(p.0)*

## Problem Addressed
LLMs have extensive knowledge and can apply it to claim verification, but they are limited by: (1) inability to fully explain their reasoning in a way that reflects their "reasoning" and knowledge, (2) lack of contestability -- no mechanism for external agents to reliably challenge or override LLM judgments. Current approaches either use LLMs as black boxes or extract symbolic representations without grounded argumentation. *(p.0, p.2)*

## Key Contributions
- **ArgLLMs**: A method for using LLMs to generate arguments (pro/con) with confidence scores that are structured into QBAFs *(p.0)*
- **Explainability via argumentation**: QBAFs serve as the basis for formal explanations of claim verdicts *(p.0)*
- **Contestability**: Humans can override LLM-generated argument strengths, add/remove arguments, and the framework formally propagates these changes *(p.0, p.6)*
- **Novel properties**: Formal proofs that DF-QuAD satisfies base score monotonicity and argument relation contestability *(p.6-7, p.17-18)*
- **Competitive performance**: ArgLLMs perform comparably with Chain-of-Thought overall on the derived TruthfulClaim, StrategyClaim, and MedClaim datasets; results vary by model and dataset. This is not a uniform improvement over the baselines. *(printed pp.5-7; [Table 1](pngs/page-006.png), [evaluation discussion](paper.pdf#page=6))*

## Methodology

### Pipeline Overview (Figure 2, p.2)

The ArgLLMs pipeline has these stages:

1. **Claim Input**: A claim to verify, optionally with contextual information *(p.2)*
2. **LLM Argument Generation**: The LLM generates supporting and attacking arguments for the claim *(p.2)*
   - Uses one of several prompt strategies: Direct Questioning, Chain-of-Thought, or role-player prompts (ChatGPT, OPRO, analyst, debater) *(p.10-12)*
3. **LLM Uncertainty Estimation**: The LLM assigns confidence/strength scores to each argument *(p.2)*
   - Base strength τ(a) assigned to each argument a
   - The input claim's intrinsic score is either fixed at 0.5 or LLM-estimated; the other generated arguments receive LLM-estimated intrinsic scores in both variants. *(printed p.6; [page image](pngs/page-005.png))*
4. **QBAF Construction**: Arguments assembled into a Quantitative Bipolar Argumentation Framework *(p.2)*
5. **DF-QuAD Evaluation**: Gradual semantics computes final strength for the claim *(p.2)*
6. **Verdict**: Final strength > 0.5 → True; ≤ 0.5 → False *(p.2)*

### Prompt Variations (p.10-13)

Four argument generation strategies tested:
- **Direct questioning**: Simply ask whether the claim is true/false *(p.10)*
- **Direct questioning on confidence**: Ask for confidence level *(p.10)*
- **Chain-of-Thought**: Multi-step reasoning before verdict *(p.10)*
- **Role-player prompts**: LLM acts as debater/analyst generating arguments *(p.11-12)*
  - **ChatGPT prompt**: Generate arguments pro/con with strength attribution *(p.11-12)*
  - **OPRO prompt**: Optimization-style prompting *(p.12-13)*
  - **Analyst prompt**: Analytical role, evaluating validity and strength *(p.12)*
  - **Debater prompt**: Adversarial debate-style, argue both sides *(p.12)*

### Argument Strength Attribution Prompts (p.10-11)
- For the QBAF, each argument needs a strength in [0,1]
- The **Argument Strength Attribution** prompt asks the LLM to rate confidence that each argument is correct, accurate, and truthful on a scale from 0% to 100% *(p.10-11, Figure 11)*
- The **OPRO Uncertainty Estimator** prompt uses a numeric scale between 0 and 1 *(p.13, Figure 17)*

## Key Equations

### Claim Verification (Binary)
$$
v(c, \sigma) \in \{0, 1\}
$$
Where: v is the verification function, c is the claim, σ is the context. v(c,σ)=1 denotes the claim is true, v(c,σ)=0 denotes the claim is false.
*(p.2)*

### Quantitative Bipolar Argumentation Framework (QBAF)
$$
Q = \langle \mathcal{A}, \mathcal{R}^-, \mathcal{R}^+, \tau \rangle
$$
Where:
- A is a set of arguments
- R⁻ ⊆ A × A is the attack relation (binary)
- R⁺ ⊆ A × A is the support relation (binary)
- τ : A → [0,1] is the base score function assigning initial strength to each argument
*(p.2-3)*

### DF-QuAD Gradual Semantics
$$
\sigma(a) = f_{agg}(\tau(a), f_{comb}(v_a^+, v_a^-))
$$
Where:
- σ(a) is the final (dialectical) strength of argument a
- τ(a) is the base score of a
- v_a⁺ is the multiset of strengths of supporters of a
- v_a⁻ is the multiset of strengths of attackers of a
- f_comb combines supporter and attacker strengths
- f_agg aggregates base score with combined attack/support influence
*(p.3)*

### DF-QuAD Aggregation Function
$$
f_{agg}(\tau(a), v) = \begin{cases} \tau(a) + v \cdot (1 - \tau(a)) & \text{if } v \geq 0 \\ \tau(a) + v \cdot \tau(a) & \text{if } v < 0 \end{cases}
$$
Where:
- τ(a) is the base score
- v is the combined influence from attackers and supporters
- When v ≥ 0 (net support), strength increases toward 1 proportionally to remaining headroom (1 - τ(a))
- When v < 0 (net attack), strength decreases toward 0 proportionally to current strength τ(a)
*(p.3)*

### Base Score Contestability (Property 1)
The root-directed argument tree gives each non-root argument exactly one path to the root. An argument is **pro** when that path has an even number of attack edges, and **con** when it has an odd number. Increasing only its intrinsic score cannot decrease the root's final score in the pro case and cannot increase it in the con case. These are non-strict inequalities; the epsilon/delta equation formerly listed here is not a paper equation. *(printed pp.4,7; [path definitions](pngs/page-003.png), [Property 1](pngs/page-006.png))*

## Parameters

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| Base score | τ(a) | - | 0.5 or LLM-estimated | [0,1] | 3,5 | Initial strength of each argument |
| Final/dialectical strength | σ(a) | - | computed | [0,1] | 3 | Output of DF-QuAD |
| Verdict threshold | - | - | 0.5 | fixed | 2 | σ > 0.5 → True, ≤ 0.5 → False |
| Argumentation depth | D | - | 1 or 2 | {1,2} | 5 | Levels of sub-arguments generated |
| Number of arguments per claim | - | - | varies | - | 5 | Depends on LLM output |
| Confidence score (from LLM) | - | % or [0,1] | - | [0,1] | 10-11 | Mapped directly to τ(a) |

## Implementation Details

### QBAF Construction from LLM Output (p.2-3, p.5)
- The claim is the **root argument** (topic) of the QBAF
- LLM generates supporting arguments (R⁺ edges to claim) and attacking arguments (R⁻ edges to claim) *(p.2)*
- Each argument can recursively have its own supporters and attackers at depth D *(p.5)*
- At depth D=1: arguments directly support/attack the claim
- At depth D=2: sub-arguments support/attack depth-1 arguments
- The QBAF is acyclic (tree structure rooted at the claim) *(p.3, noted as most common form)*

### Base Score Assignment Strategies (p.5)
Three approaches for the base score of the claim and arguments:
1. **0.5 Base + Arg**: Claim base score fixed at 0.5, argument strengths from LLM *(p.5)*
2. **Estimated Base + Arg**: Claim base score estimated by LLM (via direct/CoT prompt), argument strengths from LLM *(p.5)*
3. **Estimated Base Only (baseline)**: Only the claim's base score is estimated, no argumentation *(p.5)*

### Uncertainty Estimation Methods (p.5)
- LLM is prompted to output a confidence score as a percentage or decimal
- This confidence directly becomes τ(a) for the argument
- For "Estimated Base" variants, a separate prompt estimates the claim's own base score

### Prompt for Argument Strength Attribution (p.10-11, Figure 11)
- Asks LLM to rate confidence that the argument is correct, accurate, and truthful
- Scale: 0% to 100%
- This becomes the base score τ(a) for that argument in the QBAF
- The selected prompt asks for confidence that the argument presents a compelling case for or against its parent statement, considering both how well it supports/refutes that statement and the argument's correctness, accuracy, and truthfulness. Its meaning is not correctness confidence alone. *(Figure 4, printed p.6; [page image](pngs/page-005.png))*

### Prompt for Argument Generation (p.10, Figures 8-9)
- Direct questioning prompt shows claim + context, asks if true/false
- For argumentation: asks LLM to generate supporting AND attacking arguments
- Chain-of-Thought: adds "Take a deep breath and come up with arguments step by step"

### MoClaim Template (p.13)
- For the MoClaim dataset: includes contextual information
- Template: "Consider the following background information: [information]. Given the background information the following is correct: [claim]"

## Figures of Interest
- **Fig 1 (p.0):** Comparison of ArgLLM pipeline with existing alternatives — shows how direct answer (68% confidence) vs ArgLLM (79% confidence via QBAF aggregation) differ. The ArgLLM decomposes into pro/con arguments with individual strengths.
- **Fig 2 (p.2):** Full pipeline diagram — Claim → LLM (argument generation) → Argument Miner → QBAF → DF-QuAD Evaluation → Verdict. Shows parallel with baselines (direct, CoT).
- **Fig 3 (printed p.6):** Selected argument-generation prompt, requesting one supporting or attacking argument. *([page image](pngs/page-005.png))*
- **Fig 5 (printed p.8):** Human reduces the attacking argument's intrinsic score from **0.9 to 0.5**, changing the claim verdict from False to True; the supporting argument remains at 0.7. *([original PDF p.8](paper.pdf#page=8); checked with an opaque visual render because the stored PNG has obscured text)*
- **Fig 6 (p.7):** Base score contestability visualization.
- **Fig 7 (p.7):** Argument relation contestability visualization.
- **Fig 8 (p.10):** Direct questioning prompt template.
- **Fig 9 (p.10):** Direct questioning on confidence prompt.
- **Fig 10 (p.10):** Chain-of-thought baseline prompt.
- **Fig 11 (p.10):** Argument Strength Attribution prompt — key for understanding how LLM confidence maps to QBAF base scores.
- **Fig 12 (p.12):** ChatGPT Argument Generator prompt.
- **Fig 13 (p.12):** ChatGPT Argument Strength Attribution prompt.
- **Figs 14-17 (p.12-13):** Role-player variant prompts (Debater, Analyst, OPRO).

## Results Summary

### Main Results (Table 1, p.5; Table 2, p.11)
- Tested on **TruthfulClaim, StrategyClaim, and MedClaim**, constructed by converting question-answer pairs from TruthfulQA, StrategyQA, and MedQA into true/false claims. The original QA datasets were not used directly for the main claim-verification experiments. *(printed p.5; [original PDF](paper.pdf#page=5), checked with an opaque visual render)*
- Seven main models include Mistral, Mixtral, Gemma 7B, Gemma 2 9B, Llama 3 8B, GPT-3.5-turbo, and GPT-4o mini; an additional MedClaim experiment uses GPT-4o. *(printed pp.5-7; [Table 1](pngs/page-006.png), [original setup page](paper.pdf#page=5))*
- **Examples from Table 1**: On TruthfulClaim, Mixtral reaches 0.81 accuracy with estimated-base arguments at depth 1; GPT-4o mini reaches 0.81 at both depths. The best variant depends on the model and dataset; the table does not report the former 0.675/0.795 claims. *(printed p.7; [page image](pngs/page-006.png))*
- ArgLLMs perform comparably with Chain-of-Thought overall, but individual variants can score below the baselines. For example, on StrategyClaim with Mistral, estimated-base arguments at depth 1 score 0.62 versus Chain-of-Thought's 0.68. *([Table 1, printed p.7](pngs/page-006.png))*
- **Key finding**: Using LLM-estimated base scores ("Estimated Base + Arg") generally outperforms fixed 0.5 base scores *(p.5)*
- The estimated base score alone (no argumentation) is often competitive, suggesting the LLM's initial confidence is informative *(p.5-6)*
- **Role-player prompts**: Analyst and debater roles sometimes outperform ChatGPT-style prompts (Tables 4-7, p.14) *(p.14)*

### Performance on Smaller Models (Tables 8-16, p.15-16)
- Mistral (smaller than Mixtral) shows similar patterns but lower absolute performance
- Argumentation helps more when the base model is weaker *(p.15-16)*

## Limitations
- The conclusion says ArgLLMs' added value does not compromise prediction accuracy relative to state-of-the-art prompting methods; it does not report a "predictive variance" result. The evaluation discussion and Table 1 qualify this as comparable overall performance, with variation across configurations. *([printed p.7](pngs/page-006.png); [discussion, printed p.6](paper.pdf#page=6))*
- The method relies on LLM-generated arguments which may be fabricated or hallucinated *(p.6)*
- Acyclic QBAFs only (trees) — does not handle cyclic argumentation graphs *(p.3)*
- Claim verification uses a binary verdict at a 0.5 threshold, but the method also outputs a graded final strength and the QBAF as its reasoning trail. *(printed p.5; [original PDF](paper.pdf#page=5), checked with an opaque visual render)*
- The "semantic uncertainty" method is not integrated — only sampling-based approaches tested *(p.7)*
- Performance varies significantly across prompt strategies and models *(p.5-6)*

## Arguments Against Prior Work
- **Direct LLM verdicts lack explainability**: Users cannot see why the LLM reached a conclusion, cannot identify which knowledge was used *(p.0)*
- **NLI-based approaches** (e.g., stance detection) operate as black boxes without structured reasoning *(p.2)*
- **Prior argumentation work** (Freedman et al. 2024, earlier approaches) trained extra models to measure argument strengths and final output, relying on external trained models rather than LLM self-assessment *(p.2)*
- **Chain-of-Thought** provides explanations but they are not structured, not formally grounded, and not contestable *(p.2)*

## Design Rationale
- **Why QBAFs over Dung AFs**: QBAFs support graded strengths (base scores in [0,1]) which naturally map to LLM confidence levels. Dung AFs are binary (attack only, no strengths). QBAFs also support both attack and support relations. *(p.2-3)*
- **Why DF-QuAD**: It is the most commonly used gradual semantics for QBAFs. It satisfies desirable properties: base score monotonicity and argument relation contestability (formally proven in the paper). *(p.3, p.6-7)*
- **Why tree-structured QBAFs**: Simplifies the framework (acyclic, no cycles to resolve), and the LLM naturally generates tree-structured arguments (claim → arguments → sub-arguments). *(p.3)*
- **Why LLM self-assessment for base scores**: Avoids training separate models for strength estimation. The LLM that generates the argument also rates its confidence. *(p.5)*
- **Alternatives rejected**: Using external NLI models for strength (used in prior work but adds complexity), training argument quality classifiers (data-intensive). *(p.2)*

## Testable Properties

### Property 1: Base Score Contestability (printed pp.7,17)
For a QBAF Q rooted at α*, keep the argument set and both edge relations unchanged, and increase only one intrinsic score `τ(β) < τ′(β)`:
- If β is pro (even attack parity along its unique path to α*), `σ_Q(α*) ≤ σ_Q′(α*)`.
- If β is con (odd attack parity), `σ_Q(α*) ≥ σ_Q′(α*)`.

The property concerns any pro/con argument in the paper's restricted rooted trees, not just a leaf directly supporting or attacking the root. *([Property 1](pngs/page-006.png), [path definitions](pngs/page-003.png); [supplementary proof, original PDF p.17](paper.pdf#page=17), checked with an opaque visual render)*

### Property 2: Argument Relation Contestability (printed pp.7,17)
Add a fresh argument β and a single attack/support edge from β to an existing argument α, retaining all old intrinsic scores and all old edges. If β is pro in the new rooted tree, the root's final score cannot decrease; if β is con, it cannot increase. This is an **argument-addition** property, not a definition about switching an existing edge between attack and support. *([Property 2 begins](pngs/page-006.png); [full supplementary statement, original PDF p.17](paper.pdf#page=17), checked with an opaque visual render)*

### Property 3: Strong Base Score Contestability (p.17)
The strong property replaces the non-strict inequalities in Property 1 with strict ones, subject to the displayed condition `σ_Q(α*) ≠ 1`. **Proposition 2 attributes the strong properties to QEM**, not DF-QuAD. *([original PDF p.17](paper.pdf#page=17), checked with an opaque visual render)*

### Property 4: Strong Argument Relation Contestability (p.17)
The strong property applies strict inequalities to the argument-addition construction of Property 2, again under the displayed `σ_Q(α*) ≠ 1` condition. Proposition 2 establishes it for QEM. The proof explicitly says the strict-inequality guarantee is not satisfied by DF-QuAD. *([original PDF p.17](paper.pdf#page=17), checked with an opaque visual render)*

### Proposition 3: DF-QuAD and QEM satisfy base score monotonicity (p.18)
This supplementary result is **local monotonicity**: when β has a single outgoing edge to α, increasing only β's intrinsic score cannot decrease α's strength for a support edge or increase it for an attack edge. It does not require β to be a leaf. Proposition 4 similarly establishes argument-relation monotonicity for DF-QuAD and QEM. *([supplementary definitions and propositions, printed p.18](pngs/page-017.png))*

### Implementable Tests
- Increasing one non-root argument's intrinsic score must change the root score in the non-strict direction determined by the parity of attack edges on its unique root path. *(Property 1; [page image](pngs/page-006.png))*
- For the argument-addition construction, pro additions cannot lower the root score and con additions cannot raise it. Strict changes are not guaranteed for DF-QuAD. *(Properties 2-4; [main statement](pngs/page-006.png), [supplement](paper.pdf#page=17))*
- DF-QuAD output must be in [0,1] for all inputs in [0,1] *(p.3)*
- For a claim with no arguments: σ(claim) = τ(claim) *(p.3)*
- The aggregation function is bounded: f_agg(τ, v) ∈ [0,1] when τ ∈ [0,1] and v ∈ [-1,1] *(p.3)*

## Contestability Mechanism (p.6-7)

### How Contestability Works
Another unique feature of ArgLLMs is contestability. The system allows external agents (humans) to:

1. **Override base scores**: Change τ(a) for any argument a. The change propagates through DF-QuAD to the claim's final score. *(p.6)*
2. **Add/remove arguments**: Add new supporting or attacking arguments, or remove existing ones. *(p.6)*
3. **Change argument relations**: Move an argument from R⁺ to R⁻ (support to attack) or vice versa. *(p.6-7)*

### Two Notions of Contestability (p.6)
1. **Base score contestability**: Increasing a pro argument's intrinsic score cannot lower the root score; increasing a con argument's cannot raise it. Pro/con status depends on attack parity across the full root path. *([Property 1](pngs/page-006.png))*
2. **Argument relation contestability**: Adding a fresh argument and its single edge changes the root score in the non-strict direction determined by the new argument's pro/con status. *([Property 2](paper.pdf#page=17), checked with an opaque visual render)*

### Formal Properties (p.6-7)
- Property 1: Base score contestability — formally proven for DF-QuAD *(Proposition 1; [page image](pngs/page-006.png))*
- Property 2: Argument relation contestability — formally proven for DF-QuAD *(p.7)*
- These ensure that human overrides have predictable, formally guaranteed effects on the output

### Selected Argument-Generation Prompt (Figure 3, printed p.6)
- Requests one short argument supporting or attacking the supplied claim.
- Requires the argument to concern the claim's truthfulness and permits `N/A` when no valid and convincing argument is available.
- The badminton score-contestation example is Figure 5, not Figure 3, and reduces an attacker's score rather than removing its argument. *([generation prompt](pngs/page-005.png), [contestation example](paper.pdf#page=8), latter checked with an opaque visual render)*

### Example (Figure 5, printed p.8)
- The human lowers the existing attacker's intrinsic score from 0.9 to 0.5, correcting the False verdict to True.
- Adding an additional supporter is the separate supplementary example in **Figure 18**, printed p.17. *([Figure 5](paper.pdf#page=8), [Figure 18](paper.pdf#page=17), both checked with opaque visual renders)*

## Relevance to Project

### Direct Relevance to Propstore
This paper is highly relevant to propstore's need to bridge LLM outputs with formal argumentation:

1. **LLM confidence → base scores**: The paper shows exactly how LLM-generated confidence percentages become base scores τ(a) in QBAFs. This directly applies to propstore's need to convert NLI stance confidence into formal argumentation structures. *(p.5, p.10-11)*

2. **QBAFs as intermediate representation**: Between raw LLM output and formal reasoning. Propstore currently uses bare-float NLI — QBAFs would add structure, explainability, and contestability. *(p.2-3)*

3. **DF-QuAD for aggregation**: Instead of using raw NLI scores, propstore could use DF-QuAD to aggregate multiple evidence sources (claims supporting/attacking a stance) into a graded verdict. The aggregation function is simple, well-defined, and has proven monotonicity properties. *(p.3)*

4. **Contestability for propstore's non-commitment principle**: The formal contestability properties align with propstore's design principle of holding multiple rival normalizations without forcing one to be canonical. Users could override LLM-generated stances, and the formal framework guarantees the override propagates correctly. *(p.6-7)*

5. **Structural bridge**: The paper states that ignoring intrinsic scores yields a bipolar argumentation framework. An attack-only graph also has an AF-shaped structure, but restricting scores to {0,1} does not by itself establish equivalence between gradual strengths and Dung extension semantics. *([printed p.4](pngs/page-003.png))*

6. **QBAF → ASPIC+ connection**: The paper notes QBAFs can be composed of components from ASPIC+ style argumentation. The structured arguments (premises → conclusion) naturally map to ASPIC+ strict/defeasible rules. *(p.2-3)*

### Implementation Path for Propstore
- Replace bare-float NLI scores with QBAF base scores
- Implement DF-QuAD aggregation (simple, ~20 lines of code)
- Structure claim-stance relationships as QBAF attack/support relations
- Allow user overrides via base score modification (contestability)
- Multiple render policies could use different semantics (DF-QuAD vs QEM vs others)

## Open Questions
- [ ] How to handle the case where LLM confidence is poorly calibrated (the paper acknowledges this but doesn't solve it)
- [ ] Can DF-QuAD work with cyclic QBAFs (needed if propstore has circular argument structures)?
- [ ] How to integrate with ATMS — can QBAF base scores map to assumption labels?
- [ ] The paper uses binary verdicts (>0.5 = True); propstore may need the graded σ(a) values directly
- [ ] How does argument depth D interact with computational cost? The paper only tests D=1 and D=2
- [ ] What is QEM (Quantitative Energy Model)? Referenced in proofs but not defined in the main paper [Likely refers to Potyka 2018's quadratic energy model — see [[Potyka_2018_ContinuousDynamicalSystemsWeighted]]]

## Related Work Worth Reading
- **Baroni et al. 2019**: Gradual semantics for argumentation frameworks — foundational theory behind DF-QuAD
- **Potyka 2018**: Continuous dynamical systems approach to gradual argumentation semantics → NOW IN COLLECTION: [[Potyka_2018_ContinuousDynamicalSystemsWeighted]]
- **Rago et al. 2016**: DF-QuAD original paper — need for full algorithm specification → NOW IN COLLECTION: [[Rago_2016_DiscontinuityFreeQuAD]]
- **Cayrol and Lagasquie-Schiex 2005**: Bipolar argumentation frameworks — theoretical foundation for QBAFs
- **Freedman et al. 2024 (earlier)**: Prior ArgLLMs work that this paper extends — used external models for strength estimation
- **Amgoud and Ben-Naim 2018**: Acceptability semantics for weighted argumentation frameworks — alternative to DF-QuAD
- **Amgoud, Ben-Naim, and Vesic 2022**: Measuring the intensity of attacks in argumentation graphs with shapley value
- **Kampik, Gabbay, and Prakken 2024**: Argumentation and LLMs tutorial at KR 2024
- **Noor, Rago, and Toni 2024**: Argumentative large language models for explainable medical decision-making
