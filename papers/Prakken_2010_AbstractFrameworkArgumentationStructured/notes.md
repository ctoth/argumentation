---
title: "An abstract framework for argumentation with structured arguments"
authors: "Henry Prakken"
year: 2010
venue: "Argument & Computation"
doi_url: "https://doi.org/10.1080/19462160903564592"
---

# An abstract framework for argumentation with structured arguments

## One-Sentence Summary
Presents the ASPIC framework: a general model for argumentation with structured arguments built from strict and defeasible inference rules, instantiating Dung's abstract argumentation frameworks while satisfying rationality postulates under well-defined conditions.

## Problem Addressed
Dung (1995) provided an abstract framework for argumentation but fully abstracted from argument structure and attack relations. This makes it unsuitable for directly representing argumentation-based inference problems. Previous structured argumentation systems (Pollock 1994, Vreeswijk 1993/1997, Garcia/Simari 2004) each handled only some kinds of attack. The paper unifies undermining, rebutting, and undercutting defeat into a single framework while proving rationality postulates (closure, consistency) hold under stated conditions.

## Key Contributions
1. Unified framework combining three attack types: undermining (attacking premises), rebutting (attacking conclusions), and undercutting (attacking inference steps)
2. Four types of premises: axioms, ordinary premises, assumptions, and issues -- with distinct attackability
3. Proof that rationality postulates (closure under strict rules, direct/indirect consistency) hold for well-formed argumentation theories closed under contraposition or transposition
4. Formal connection to assumption-based argumentation (ABA): ABA is shown to be a special case
5. Framework for preference-based defeat resolution with last-link and weakest-link argument orderings
6. Treatment of self-defeat and its implications for grounded semantics

## Methodology
The paper defines an argumentation system as a tuple of logical language, contrariness function, strict/defeasible rules, and a preference ordering on defeasible rules. Arguments are inference trees built by chaining rules from a knowledge base. Attack and defeat relations are defined formally, then the whole structure instantiates Dung's abstract framework.

## Core Definitions

### Definition 3.1: Argumentation System
An argumentation system is a tuple $AS = (\mathcal{L}, \bar{}, \mathcal{R}, \leq)$ where:
- $\mathcal{L}$ is a logical language
- $\bar{}$ is a contrariness function from $\mathcal{L}$ to $2^\mathcal{L}$
- $\mathcal{R} = \mathcal{R}_s \cup \mathcal{R}_d$ is a set of strict ($\mathcal{R}_s$) and defeasible ($\mathcal{R}_d$) inference rules such that $\mathcal{R}_s \cap \mathcal{R}_d = \emptyset$
- $\leq$ is a partial preorder on $\mathcal{R}_d$

### Definition 3.2: Logical Language Contrariness
Let $\mathcal{L}$ be a set, $\bar{}$ a contrariness function from $\mathcal{L}$ to $2^\mathcal{L}$. If $\phi \in \bar{\psi}$ then:
- if $\psi \notin \bar{\phi}$, $\phi$ is called a *contrary* of $\psi$
- if $\psi \in \bar{\phi}$, $\phi$ and $\psi$ are called *contradictories*
- The latter case is denoted $\phi = -\psi$

### Definition 3.3: Consistency
Let $P \subseteq \mathcal{L}$. $P$ is *consistent* iff $\nexists \phi, \psi \in P$ such that $\phi \in \bar{\psi}$.

### Definition 3.4: Strict and Defeasible Rules
- A *strict rule* of the form $\phi_1, \ldots, \phi_n \to \phi$: if $\phi_1, \ldots, \phi_n$ hold, then without exception $\phi$ holds
- A *defeasible rule* of the form $\phi_1, \ldots, \phi_n \Rightarrow \phi$: if $\phi_1, \ldots, \phi_n$ hold, then presumably $\phi$ holds
- $\phi_1, \ldots, \phi_n$ are the antecedents; $\phi$ is the consequent

### Definition 3.5: Knowledge Base
A knowledge base in an argumentation system $(\mathcal{L}, \bar{}, \mathcal{R}, \leq)$ is a pair $(\mathcal{K}, \leq')$ where:
- $\mathcal{K} \subseteq \mathcal{L}$
- $\leq'$ is a partial preorder on $\mathcal{K} \setminus \mathcal{K}_n$
- $\mathcal{K} = \mathcal{K}_n \cup \mathcal{K}_p \cup \mathcal{K}_a \cup \mathcal{K}_i$ where these four subsets are disjoint:
  - $\mathcal{K}_n$: necessary premises (axioms) -- cannot be attacked
  - $\mathcal{K}_p$: ordinary premises
  - $\mathcal{K}_a$: assumptions
  - $\mathcal{K}_i$: issues

### Definition 3.6: Arguments
An argument $A$ on the basis of a knowledge base $(\mathcal{K}, \leq')$ in an argumentation system $(\mathcal{L}, \bar{}, \mathcal{R}, \leq)$ is constructed as follows:

1. **Atomic**: $\phi$ if $\phi \in \mathcal{K}$ with $Prem(A) = \{\phi\}$, $Conc(A) = \phi$, $Sub(A) = \{\phi\}$, $DefRules(A) = \emptyset$, $TopRule(A) = $ undefined

2. **Strict rule application**: $A_1, \ldots, A_n \to \phi$ if there exists a strict rule $Conc(A_1), \ldots, Conc(A_n) \to \phi$ in $\mathcal{R}_s$
   - $Prem(A) = Prem(A_1) \cup \ldots \cup Prem(A_n)$
   - $Conc(A) = \phi$
   - $Sub(A) = Sub(A_1) \cup \ldots \cup Sub(A_n) \cup \{A\}$
   - $DefRules(A) = DefRules(A_1) \cup \ldots \cup DefRules(A_n)$
   - $TopRule(A) = Conc(A_1), \ldots, Conc(A_n) \to \phi$

3. **Defeasible rule application**: $A_1, \ldots, A_n \Rightarrow \phi$ if there exists a defeasible rule $Conc(A_1), \ldots, Conc(A_n) \Rightarrow \phi$ in $\mathcal{R}_d$
   - Same as above but $DefRules(A) = DefRules(A_1) \cup \ldots \cup DefRules(A_n) \cup \{TopRule(A)\}$

Functions on arguments:
- $Prem(A)$: set of all premises
- $Conc(A)$: conclusion
- $Sub(A)$: set of all sub-arguments
- $DefRules(A)$: set of all defeasible rules used
- $TopRule(A)$: last inference rule used

### Definition 3.8: Argument Properties
An argument $A$ is:
- **strict** if $DefRules(A) = \emptyset$
- **defeasible** if $DefRules(A) \neq \emptyset$
- **firm** if $Prem(A) \subseteq \mathcal{K}_n$
- **plausible** if $Prem(A) \not\subseteq \mathcal{K}_n$

### Definition 3.11: Argumentation Theory
An argumentation theory is a triple $AT = (AS, KB, \leq')$ where $AS$ is an argumentation system, $KB$ is a knowledge base for $AS$, and $\leq'$ is an argument ordering on the set of arguments constructible from $KB$ in $AS$ (below called the set of arguments on the basis of $AT$).

### Three Attack Types

**Definition 3.12: Undermining attack**
Argument $A$ *undermines* argument $B$ (on $B'$) iff $Conc(A) \in \bar{\phi}$ for some $B' \in Sub(B)$ of the form $\phi_1, \ldots, \phi_n \to/\Rightarrow \phi$ where $\phi \in \mathcal{K}_p \cup \mathcal{K}_a \cup \mathcal{K}_i$, i.e. $\phi$ is an ordinary premise, assumption, or issue.

**Definition 3.14: Rebutting attack**
Argument $A$ *rebuts* argument $B$ (on $B'$) iff $Conc(A) \in \bar{\phi}$ for some $B' \in Sub(B)$ of the form $B'_1, \ldots, B'_n \Rightarrow \phi$. So rebutting attacks only target defeasible-rule conclusions.

**Definition 3.16: Undercutting attack**
Argument $A$ *undercuts* argument $B$ (on $B'$) iff $Conc(A) \in \bar{n}$ for some $B' \in Sub(B)$ of the form $B'_1, \ldots, B'_n \Rightarrow \phi$ where $n$ names the application of that defeasible rule. Requires naming convention for defeasible rules.

### Defeat Relations

**Definition 3.19: Successful rebuttal**
Argument $A$ *successfully rebuts* argument $B$ if $A$ rebuts $B$ on $B'$ and either $A$ is a contrary underminer of $B'$ (asymmetric conflict), or $A \not<' B'$ (not strictly weaker by the argument ordering).

**Definition 3.20: Defeat**
Argument $A$ *defeats* argument $B$ iff $A$ undercuts or successfully rebuts $B$ on some $B'$, or $A$ undermines $B$ on some $B'$ and either $B'$ is a contrary (not contradictory) or $A \not<' B'$.

**Definition 3.22: Argumentation Framework**
The argumentation framework $AF$ corresponding to an argumentation theory $AT$ is the pair $(\mathcal{A}, Def)$ such that:
- $\mathcal{A}$ is the set of arguments on the basis of $AT$ as defined by Definition 3.6
- $Def$ is the defeat relation on $\mathcal{A}$ given by Definition 3.21

## Argument Ordering

Two main approaches for deriving argument orderings from rule orderings:

### Definition 6.12: Last Defeasible Rule
- $LastDefRules(A) = \emptyset$ if $DefRules(A) = \emptyset$
- If $A = B_1, \ldots, B_n \Rightarrow \phi$, then $LastDefRules(A) = \{TopRule(A)\}$ if $Conc(A_i) = \phi_i$ for $i \leq n$ and $DefRules(A_i) = \emptyset$ for all $i$, else $LastDefRules(A) = LastDefRules(A_1) \cup \ldots \cup LastDefRules(A_n)$

### Definition 6.14: Last-Link Principle
Let $A$ and $B$ be two arguments. Then $A \prec B$ iff either:
1. $DefRules(A) \neq \emptyset$ and $DefRules(B) = \emptyset$; or
2. $LastDefRules(A) \neq \emptyset$ and $LastDefRules(B) \neq \emptyset$ and are empty and $Prem(A) \leq' Prem(B)$ (i.e. premises comparison)

### Definition 6.17: Weakest-Link Principle
Let $A$ and $B$ be two arguments. Then $A \prec B$ iff either:
1. $Prem(A) \leq' Prem(B)$; or
2. $DefRules(A) \leq DefRules(B)$; or
3. $LastDefRules(A) \leq LastDefRules(B)$ and $LastDefRules(B) \leq LastDefRules(A)$ and $Prem(A) \leq' Prem(B)$

(Simplified paraphrase; actual conditions are more nuanced -- see Definition 3.10 in the paper.)

## Transposition and Contraposition

### Definition 5.1: Transposition
A strict rule $s$ is a *transposition* of $\phi_1, \ldots, \phi_n \to \psi$ iff $s$ is of the form $\phi_1, \ldots, \phi_{i-1}, -\psi, \phi_{i+1}, \ldots, \phi_n \to -\phi_i$ for some $1 \leq i \leq n$.

### Definition 5.2: Closure under Transposition
Let $\mathcal{R}_s$ be a set of strict rules. $Cl_{\mathcal{R}_s}(\mathcal{R}_s)$ is the smallest set such that:
- $\mathcal{R}_s \subseteq Cl_{\mathcal{R}_s}(\mathcal{R}_s)$
- If $r \in Cl_{\mathcal{R}_s}(\mathcal{R}_s)$ and $t$ is a transposition of $r$ then $t \in Cl_{\mathcal{R}_s}(\mathcal{R}_s)$

### Definition 5.3: Closure under Transposition (Systems)
An argumentation system ($\mathcal{L}, \bar{}, \mathcal{R}_s, \leq$) is *closed under transposition* if $Cl_{\mathcal{R}_s}(\mathcal{R}_s) = \mathcal{R}_s$.

### Definition 5.5: Contraposition
An argumentation theory is *closed under contraposition* if for all $S \subseteq \mathcal{L}$, all $\phi$ and all $\psi$, it holds that if $S \vdash \phi$ then $S \setminus \{-\psi\} \cup \{-\phi\} \vdash \psi$. An argumentation theory is closed under contraposition if its argumentation system is.

## Rationality Postulates

### Proposition 6.1
Let $(\mathcal{A}, Def)$ be an argumentation framework as defined in Definition 3.22. Let $E$ be an extension under a given semantics $S$ subsumed by complete semantics. Then for all $A \in E$: if $A' \in Sub(A)$ then $A' \in E$.

### Proposition 6.2
Let $(\mathcal{A}, Def)$ be an argumentation framework corresponding to an argumentation theory, and $E$ any of its extensions under a given semantics $S$ subsumed by complete semantics. Then $Conc(A) | A \in E \subseteq Cl_{\mathcal{R}_s}(Conc(A) | A \in E)$.

### Definition 6.5: Maximal Fallible Subarguments
For any argument $A$, an argument $A' \in Sub(A)$ is a *maximal fallible subargument of A* iff:
1. $A'$'s final inference is defeasible or $A'$ is a non-axiom premise, and
2. There is no $a'' \in Sub(A)$ such that $A'' \neq A$ and $A' \in Sub(A'')$ and $A''$ satisfies condition 1.

### Definition 6.8: Well-Formed Argumentation Theory
An argumentation theory is *well-formed* if:
1. No consequent of a defeasible rule is a contrary of the consequent of a strict rule
2. If $r \in \mathcal{K}_n$ and $\phi$ is a contrary of $r$, then $\phi$ is not the conclusion of a rule in $\mathcal{R}$ and $\phi$ is not in $\mathcal{K}$

### Theorem 6.10 (Main Rationality Result)
Let $(\mathcal{A}, Def)$ be an argumentation framework corresponding to a well-formed argumentation theory that is closed under contraposition or transposition and has a reasonable argument ordering and a consistent $Cl_{\mathcal{R}_s}(\mathcal{K}_n)$, and let $E$ be any of its extensions under a given semantics subsumed by complete semantics. Then the set $Cl_{\mathcal{R}_s}(\{Conc(A) | A \in E\})$ is consistent.

### Corollary 6.11
If the conditions of Theorem 6.10 are satisfied, then for any extension $E$ under a given semantics subsumed by complete semantics the set $\{\phi | \phi$ is a premise of an argument in $E\}$ is consistent.

## Self-Defeat (Section 7)

Self-defeating arguments are possible and cause problems if argumentation systems are not carefully defined, particularly with grounded semantics.

**Example 7.1** (Serial self-defeat): $\mathcal{R}_d = \{p \Rightarrow q\}$, $\mathcal{K} = \{p, \neg q, \neg r\}$. Then we have $A_1: p$, $A_2: p \Rightarrow q$, $A_3: \neg q$. Argument $A_2$ is self-defeating since it undermines itself via $A_3$.

**Example 7.2** (Parallel self-defeat): $\mathcal{R}_d = \{p, q, \neg q, r_1 \Rightarrow s\}$ and $\mathcal{K} = \{p, r, t\}$ while $\mathcal{R}_s$ contains all propositionally valid inferences. Then all defeasible arguments get defeated.

The problem with grounded semantics: since self-defeating arguments are in no extension, any defeasible argument unrelated to the self-defeating one could be vulnerable. Caminada (personal communication) suggests disallowing arguments with contradictory sub-conclusions.

## Relation with Assumption-Based Argumentation (Section 8)

### Definition 8.1: ABA Deductive System
A deductive system is a pair $(\mathcal{L}, \mathcal{R})$ where:
- $\mathcal{L}$ is a formal language of countably many sentences
- $\mathcal{R}$ is a countable set of inference rules of the form $\alpha_1, \ldots, \alpha_n \to \alpha$ ($n \geq 0$, $\alpha \in \mathcal{L}$)

### Theorem 8.9
For all ABFs, any semantics $S$ subsumed by complete semantics and any set $E$:
1. If $E$ is an $S$-extension of ABF then $E_{AF}$ is an $S$-extension of $AT$, where $E_{AF} = \{A | A \in S, A \text{ uses } E\}$
2. If $E$ is an $S$-extension of $AT$ then $E_{ABF}$ is an $S$-extension of $ABF$, where $E_{ABF} = \{A | A_{AF} \text{ uses the assumptions in } E\}$

### Corollary 8.10
For any ABF, any semantics $S$ subsumed by complete semantics, and for any formula $\phi$: $\phi$ is skeptically (credulously) $S$-acceptable in ABF iff $\phi$ is skeptically (credulously) $S$-acceptable in $AT_{ABF}$.

## Domain-Specific vs General Inference Rules (Section 4)

The framework can be used in two ways:
1. **Domain-specific**: inference rules are domain-specific (e.g., "Frisians are Dutch, Dutch are Tall")
2. **General**: inference rules encode general patterns of reasoning (e.g., modus ponens) applied to object language conditionals

The paper shows both approaches can be represented. With domain-specific rules, the framework uses object-language conditionals. With general inference rules, modus ponens and similar rules are added, and the material implication is represented in the object language.

Argument schemes (Walton et al. 2008) can be modeled as defeasible inference rules, with critical questions modeled as undercutting attacks.

## Parameters

| Name | Symbol | Units | Default | Range | Notes |
|------|--------|-------|---------|-------|-------|
| Logical language | $\mathcal{L}$ | - | - | - | Set of well-formed formulae |
| Contrariness function | $\bar{}$ | - | - | - | Maps each $\phi \in \mathcal{L}$ to its contraries/contradictories |
| Strict rules | $\mathcal{R}_s$ | - | - | - | Exceptionless inference rules |
| Defeasible rules | $\mathcal{R}_d$ | - | - | - | Defeasible inference rules |
| Rule ordering | $\leq$ | - | - | - | Partial preorder on $\mathcal{R}_d$ |
| Necessary premises | $\mathcal{K}_n$ | - | - | - | Axioms, cannot be attacked |
| Ordinary premises | $\mathcal{K}_p$ | - | - | - | Can be attacked by undermining |
| Assumptions | $\mathcal{K}_a$ | - | - | - | Can be attacked by undermining |
| Issues | $\mathcal{K}_i$ | - | - | - | Can be attacked by undermining |
| Argument ordering | $\leq'$ | - | - | - | Partial preorder on arguments |

## Figures of Interest
- **Fig 1 (page 7):** An argument for $v$ displayed in proof-tree format with strict (single line) and defeasible (double line) inferences
- **Fig 2 (page 11):** Domain-specific vs. general inference rules -- two representations of the same argument (Wobbe is tall)

## Implementation Details

### Data Structures
- **Argumentation System**: tuple $(\mathcal{L}, \bar{}, \mathcal{R}, \leq)$
- **Knowledge Base**: pair $(\mathcal{K}, \leq')$ with four partitions of $\mathcal{K}$
- **Argument**: tree structure with functions $Prem$, $Conc$, $Sub$, $DefRules$, $TopRule$
- **Argumentation Theory**: triple $(AS, KB, \leq')$
- **Argumentation Framework**: pair $(\mathcal{A}, Def)$ -- instantiates Dung's framework

### Argument Construction Algorithm
Arguments are constructed bottom-up by step-by-step rule chaining:
1. Start with premises from $\mathcal{K}$
2. Apply strict or defeasible rules whose antecedents match existing argument conclusions
3. Each application creates a new argument with accumulated premises, sub-arguments, and defeasible rules
4. Continue until no new arguments can be constructed

### Attack Determination
For each pair of arguments $(A, B)$:
1. Check if $Conc(A) \in \bar{\phi}$ for any premise $\phi$ of $B$ in $\mathcal{K}_p \cup \mathcal{K}_a \cup \mathcal{K}_i$ (undermining)
2. Check if $Conc(A) \in \bar{\phi}$ for any defeasible-rule conclusion $\phi$ in $Sub(B)$ (rebutting)
3. Check if $Conc(A)$ names a defeasible rule used in $Sub(B)$ and is its contrary (undercutting)

### Defeat from Attack
- Undercutting attacks always succeed (no preference comparison)
- Rebutting attacks succeed unless attacker is strictly weaker ($A \not<' B'$)
- Undermining attacks on contradictories succeed unless attacker is strictly weaker; on contraries always succeed

## Results Summary
- ASPIC framework satisfies closure under strict rules (Proposition 6.2)
- Under well-formedness + closure under contraposition/transposition + reasonable ordering + consistent axioms: extensions are consistent (Theorem 6.10)
- ABA is a special case (Theorem 8.9, Corollary 8.10)
- The framework is later extended (Modgil and Prakken 2014) as ASPIC+

## Limitations
- Self-defeat creates problems especially for grounded semantics (Section 7)
- Rationality postulates require closure under contraposition or transposition, which may not always hold
- The well-formedness condition (Definition 6.8) restricts defeasible rule consequents
- The framework does not directly handle preferences between arguments based on specificity
- Argument ordering derivation from rule/premise orderings is left as a parameter, not fully specified
- Does not cover all results from Caminada and Amgoud (2007) for the weakest-link principle

## Testable Properties
- Any sub-argument of an argument in an extension must also be in that extension (Proposition 6.1)
- The set of conclusions of arguments in an extension is closed under strict rules (Proposition 6.2)
- Under Theorem 6.10 conditions: the strict-rule closure of conclusions in any extension is consistent
- If Theorem 6.10 conditions hold: the premises of arguments in any extension are consistent (Corollary 6.11)
- For any ABF, skeptical/credulous acceptability is preserved when translating to the ASPIC AT (Corollary 8.10)
- An argument cannot be stronger than its weakest sub-argument (closure under sub-arguments)
- Strict arguments cannot be defeated by any other argument
- Firm and strict arguments are in every complete extension

## Relevance to Project
This paper provides the foundational definitions for ASPIC, the precursor to ASPIC+ (Modgil and Prakken 2014). It defines the formal structure of arguments as inference trees, three attack types (undermining, rebutting, undercutting), defeat relations incorporating preferences, and proves key rationality properties. For the propstore project's argumentation infrastructure, this paper provides the formal basis for structured argument construction and evaluation.

## Open Questions
- [ ] How does the self-defeat problem affect practical implementations?
- [ ] What is the exact relationship between this 2010 paper and the later ASPIC+ (Modgil and Prakken 2014)?
- [ ] How should argument ordering be implemented in practice (last-link vs weakest-link)?
- [ ] Can the framework handle cyclic dependencies in rule applications?

## Related Work Worth Reading
- Modgil and Prakken (2014) "The ASPIC+ framework for structured argumentation" -- extends this paper
- Modgil and Prakken (2018) "A general account of argumentation with preferences" -- further generalization
- Caminada and Amgoud (2007) "On the evaluation of argumentation formalisms" -- rationality postulates that motivate this work
- Dung (1995) "On the acceptability of arguments" -- the abstract foundation
- Vreeswijk (1997) "Abstract argumentation systems" -- predecessor framework
- Pollock (1994) "Justification and defeat" -- undercutting defeat origin
- Gordon et al. (2007) "Carneades model of argument and burden of proof" -- related structured argumentation
- Bondarenko et al. (1997) "An abstract, argumentation-theoretic approach to default reasoning" -- ABA framework
- [[Brewka_2010_AbstractDialecticalFrameworks]] — **Moderate.** Brewka & Woltran cite Prakken's ASPIC+ for structured argumentation. ADFs and ASPIC+ generalize Dung AFs in complementary directions: ADFs enrich the abstract level with per-node acceptance conditions (support, complex dependencies); ASPIC+ adds internal argument structure (premises, inference rules, conclusions). How the two interact remains an open question.
