---
title: "On the Acceptability of Arguments and its Fundamental Role in Nonmonotonic Reasoning, Logic Programming and n-Person Games"
authors: "Phan Minh Dung"
year: 1995
venue: "Artificial Intelligence"
doi_url: "https://doi.org/10.1016/0004-3702(94)00041-X"
pages: "321-357"
affiliation: "Division of Computer Science, Asian Institute of Technology, Bangkok, Thailand"
---

# On the Acceptability of Arguments and its Fundamental Role in Nonmonotonic Reasoning, Logic Programming and n-Person Games

## One-Sentence Summary

Introduces abstract argumentation frameworks --- a pair (AR, attacks) of arguments and an attack relation --- and defines multiple semantics (admissible, preferred, stable, grounded, complete extensions) that unify nonmonotonic reasoning, logic programming semantics, and n-person game solutions under a single formal theory of argument acceptability. *(p.321)*

## Problem Addressed

Prior to this work, the notion of *acceptability* of arguments had not been formalized despite extensive work on argument *structure*. *(p.322)* The paper addresses the gap between argument structure analysis and determining which arguments a rational agent should accept. It also addresses the disconnect between "internal stability" approaches (logic programming, nonmonotonic reasoning) and "external stability" approaches (argumentation), showing they are two sides of the same coin. *(p.323)* The basic principle of argumentation is captured by the saying "*The one who has the last word laughs best*". *(p.322)*

## Key Contributions

- Defines **argumentation frameworks** as abstract pairs AF = (AR, attacks) where AR is a set of arguments and attacks is a binary relation on AR *(p.326)*
- Introduces a hierarchy of semantics: **admissible sets**, **preferred extensions**, **stable extensions**, **grounded extensions**, and **complete extensions** *(pp.326--330)*
- Proves that most major approaches to nonmonotonic reasoning (Reiter's default logic, Pollock's defeasible logic, logic programming with negation as failure) are special forms of argumentation *(pp.339--347)*
- Shows that solutions to **n-person games** (Von Neuman-Morgenstern solutions) and the **stable marriage problem** correspond exactly to stable extensions of corresponding argumentation frameworks *(pp.334--338)*
- Introduces a **meta-interpreter generation method** for argumentation systems using logic programming, analogous to the compiler-compiler idea *(pp.348--349)*

## Methodology

The paper proceeds in two steps: (1) develop an abstract, formal theory of argumentation based on acceptability of arguments, then (2) demonstrate its "correctness" through two arguments --- first showing it unifies nonmonotonic reasoning and logic programming, second showing it captures the logical structure of n-person games and the stable marriage problem. *(pp.324--325)*

## Key Definitions and Formal Framework

### Definition 2: Argumentation Framework *(p.326)*

$$
AF = \langle AR, attacks \rangle
$$

Where: AR is a set of arguments, and attacks is a binary relation on AR, i.e. attacks $\subseteq AR \times AR$. An argument is an abstract entity whose role is solely determined by its relations to other arguments.
*(p.326)*

### Definition 5: Conflict-Free *(p.326)*

A set S of arguments is **conflict-free** if there are no arguments A and B in S such that A attacks B. *(p.326)*

### Definition 6: Acceptability and Admissibility *(p.326)*

(1) An argument $A \in AR$ is **acceptable** with respect to a set S of arguments iff for each argument $B \in AR$: if B attacks A then B is attacked by S. *(p.326)*

(2) A conflict-free set of arguments S is **admissible** iff each argument in S is acceptable with respect to S. *(p.326)*

### Definition 7: Preferred Extension *(p.327)*

A **preferred extension** of AF is a maximal (with respect to set inclusion) admissible set of AF. *(p.327)*

### Definition 13: Stable Extension *(p.328)*

A conflict-free set of arguments S is a **stable extension** iff S attacks each argument which does not belong to S. *(p.328)*

### Definition 16: Characteristic Function *(pp.328--329)*

$$
F_{AF} : 2^{AR} \rightarrow 2^{AR}
$$

$$
F_{AF}(S) = \{A \mid A \text{ is acceptable with respect to } S\}
$$
*(p.329)*

### Definition 20: Grounded Extension *(p.329)*

The **grounded extension**, denoted $GE_{AF}$, is the least fixed point of $F_{AF}$. *(p.329)*

### Definition 23: Complete Extension *(p.329)*

An admissible set S of arguments is a **complete extension** iff each argument which is acceptable with respect to S belongs to S. *(p.329)*

### Definition 27: Finitary Framework *(p.330)*

An argumentation framework AF = (AR, attacks) is **finitary** iff for each argument A, there are only finitely many arguments in AR which attack A. *(p.330)*

### Definition 29: Well-Founded Framework *(p.331)*

An argumentation framework is **well-founded** iff there exists no infinite sequence $A_0, A_1, \ldots, A_n, \ldots$ such that for each $i$, $A_{i+1}$ attacks $A_i$. *(p.331)*

### Definition 31: Coherent and Relatively Grounded *(p.332)*

(1) AF is **coherent** if each preferred extension of AF is stable. *(p.332)*
(2) AF is **relatively grounded** if its grounded extension coincides with the intersection of all preferred extensions. *(p.332)*

### Definition 32: Controversial, Limited Controversial, Uncontroversial *(p.332)*

An argument B **indirectly attacks** A if there exists a finite sequence $A_0, \ldots, A_{2n+1}$ such that $A = A_0$ and $B = A_{2n+1}$, and for each $i$, $0 \leq i \leq 2n$, $A_{i+1}$ attacks $A_i$. B **indirectly defends** A if there exists a similar sequence of length $2n$. *(p.332)*

An argument B is **controversial** with respect to A if B both indirectly attacks and indirectly defends A. *(p.332)*

(1) AF is **uncontroversial** if none of its arguments is controversial. *(p.332)*
(2) AF is **limited controversial** if there exists no infinite sequence $A_0, \ldots, A_n, \ldots$ such that $A_{i+1}$ is controversial with respect to $A_i$. *(p.332)*

### Definition 41: arg and flat Mappings *(p.340)*

For a default theory $T = (D, W)$ and first-order theory S, and set of arguments S' of $AF(T)$:

$$arg(S) = \{(K, k) \in AR_T \mid \forall j \in K: \{j\} \cup S \text{ is consistent}\}$$

$$flat(S') = \{k \mid \exists (K, k) \in S'\}$$
*(p.340)*

### Definition 44: Indefeasible Argument *(p.342)*

An argument A is **indefeasible** iff there is an $m$ such that for each $n > m$, the argument is a level-$n$ argument (where level-0 arguments are all arguments, and level-$(n+1)$ arguments are those not attacked by any level-$n$ argument). *(p.342)*

## Key Theorems

### Lemma 10 (Fundamental Lemma) *(p.327)*

Let S be an admissible set of arguments, and A and A' be arguments which are acceptable with respect to S. Then:
(1) $S' = S \cup \{A\}$ is admissible, and
(2) A' is acceptable with respect to S'. *(p.327)*

### Theorem 11 *(p.327)*

(1) The set of all admissible sets of AF form a complete partial order with respect to set inclusion. *(p.327)*
(2) For each admissible set S of AF, there exists a preferred extension E of AF such that $S \subseteq E$. *(p.327)*

### Corollary 12 *(p.327)*

Every argumentation framework possesses at least one preferred extension. *(p.327)*

### Lemma 14: Characterization of Stable Extensions *(p.328)*

S is a stable extension iff $S = \{A \mid A \text{ is not attacked by } S\}$. *(p.328)*

### Lemma 15 *(p.328)*

Every stable extension is a preferred extension, but not vice versa. *(p.328)*

### Lemma 18 *(p.329)*

A conflict-free set S of arguments is admissible iff $S \subseteq F(S)$. *(p.329)*

### Lemma 19 *(p.329)*

$F_{AF}$ is monotonic (with respect to set inclusion). *(p.329)*

### Lemma 24 *(p.330)*

A conflict-free set of arguments E is a complete extension iff $E = F_{AF}(E)$. *(p.330)*

### Theorem 25: Relations Between Semantics *(p.330)*

(1) Each preferred extension is a complete extension, but not vice versa. *(p.330)*
(2) The grounded extension is the least (with respect to set inclusion) complete extension. *(p.330)*
(3) The complete extensions form a complete semilattice with respect to set inclusion. *(p.330)*

### Lemma 28 *(p.330)*

If AF is finitary, then $F_{AF}$ is $\omega$-continuous. *(p.330)*

### Theorem 30 *(p.331)*

Every well-founded argumentation framework has exactly one complete extension which is grounded, preferred, and stable. *(p.331)*

### Theorem 33 *(p.332)*

(1) Every limited controversial argumentation framework is coherent. *(p.332)*
(2) Every uncontroversial argumentation framework is coherent and relatively grounded. *(p.332)*

### Lemma 34 *(p.333)*

Let AF be a limited controversial argumentation framework. Then there exists a nonempty complete extension E of AF. *(p.333)*

### Lemma 35 *(p.333)*

Let AF be an uncontroversial argumentation framework, and A be an argument such that A is not attacked by the grounded extension GE of AF and $A \notin GE$. Then:
(1) there exists a complete extension $E_1$ such that $A \in E_1$, and
(2) there exists a complete extension $E_2$ such that $E_2$ attacks A. *(pp.333--334)*

### Corollary 36 *(p.334)*

Every limited controversial argumentation framework possesses at least one stable extension. *(p.334)*

### Theorem 37: N-Person Games *(p.336)*

Let IMP be the set of imputations of a cooperative n-person game G and let attacks be the corresponding domination relation between them. Then each NM-solution of (IMP, attacks) interpreted as an argumentation framework is a stable extension, and vice versa. *(p.336)*

### Theorem 38: Core of N-Person Games *(p.337)*

Let IMP be the set of imputations of an n-person game G and let attacks be the corresponding domination relation. Then the core of G coincides with $F(\phi)$ where F is the characteristic function of (IMP, attacks) interpreted as an argumentation framework. *(p.337)*

### Theorem 39: Stable Marriage Problem *(p.337)*

A set $S \subseteq AR$ constitutes a solution to the SMP iff S is a stable extension of the corresponding argumentation framework. *(p.337)*

### Lemma 40 *(p.340)*

Let S be an admissible set of arguments in $AF(T)$. Let $H = \bigcup\{K \mid (K, k) \in S\}$. Then $T, H \not\vdash \text{false}$ iff T is consistent. *(p.340)*

### Lemma 42 *(p.340)*

Let T be a default theory, and E be a first-order theory. Then E is an R-extension of T iff $E = flat(arg(E))$. *(p.340)*

### Theorem 43: Default Logic Correspondence *(pp.340--341)*

Let $T = (D, W)$ be a default theory. Let E be an R-extension of T and E' be a stable extension of $AF(T)$. Then:
(1) $arg(E)$ is a stable extension of $AF(T)$. *(p.341)*
(2) $flat(E')$ is an R-extension of T. *(p.341)*

### Lemma 45 *(p.342)*

$F_{AF} = Pl_{AF} \circ Pl_{AF}$, where $Pl_{AF}(S) = \{A \mid \text{no argument in } S \text{ attacks } A\}$. *(p.342)*

### Lemma 46 *(p.342)*

Let $GE_{AF}$ be the grounded extension of AF. Then:
$\phi \subseteq AR_1 \subseteq \cdots \subseteq AR_{2i+1} \subseteq AR_{2i+1} \subseteq \cdots \subseteq GE_{AF} \subseteq \cdots \subseteq AR_{2i} \subseteq \cdots \subseteq AR_2 \subseteq AR_0 = AR$. *(p.342)*

### Theorem 47: Pollock's Defeasible Reasoning *(p.342)*

(1) An argument A is indefeasible iff $A \in AR_{inf}$. *(p.342)*
(2) $AR_{inf} \subseteq GE_{AF}$. *(p.342)*
(3) If AF is finitary, then $AR_{inf} = GE_{AF}$. *(p.342)*

### Theorem 49: Logic Programming (Negation as Possibly Infinite Failure) *(p.344)*

Let P be a logic program. Then a Herbrand interpretation M is a stable model of P iff there is a stable extension E of $AF_{napif}(P)$ such that $M \cup \neg.CM = \{k \mid \exists(K,k) \in E\}$. *(p.344)*

### Theorem 50: Well-Founded Model *(p.344)*

Let P be a logic program, and WFM be the well-founded model of P. Let GE be the grounded extension of $AF_{napif}(P)$. Then $WFM = \{h \mid \exists(K,h) \in GE\}$. *(p.344)*

### Lemma 51 *(p.345)*

Let P be an arbitrary logic program and $AF_{napif}(P) = (AR, attacks)$. Then, in general, AR is not recursively decidable, i.e. there is no algorithm which always terminates and decides for each pair $(K, k)$ whether or not $(K, k) \in AR$. *(p.345)*

### Theorem 52 *(p.345)*

Let P be an arbitrary logic program. Then the stable, well-founded and preferred extension semantics of P are in general incomputable. *(p.345)*

### Lemma 54 *(p.345)*

The set of arguments in $AF_{naff}(P)$ for each logic program P is computable. *(p.345)*

### Theorem 55: Clark's Completion (Negation as Finite Failure) *(p.346)*

Let P be an arbitrary logic program. Then a Herbrand interpretation M is a model of Clark's completion of P, $comp(P)$, if there is a stable extension E of $AF_{naff}(P)$ such that $M \cup \neg.CM = \{k \mid \exists(K,k) \in E\}$. *(p.346)*

### Theorem 56: Fitting's Model *(p.346)*

Let P be a logic program, and FM be Fitting's model of P. Let GE be the grounded extension of $AF_{naff}(P)$. Then $FM = \{h \mid \exists(K,h) \in GE\}$. *(p.346)*

### Theorem 57 *(p.347)*

(1) If P is stratified, then $AF_{napif}(P)$ is well-founded. *(p.347)*
(2) If P is hierarchical, then $AF_{naff}(P)$ is well-founded. *(p.347)*

### Theorem 58 *(p.347)*

(1) If P is strict, then both $AF_{napif}(P)$ and $AF_{naff}(P)$ are uncontroversial. *(p.347)*
(2) If P is call-consistent, then both $AF_{napif}(P)$ and $AF_{naff}(P)$ are limited controversial. *(p.347)*

### Corollary 59 *(p.347)*

(1) The stable and well-founded semantics of stratified logic programs coincide. *(p.347)*
(2) Clark's completion of a hierarchical program P has exactly one Herbrand model which coincides with Fitting's model of P. *(p.347)*

### Corollary 60 *(p.347)*

(1) The well-founded semantics, stable semantics and preferred extension semantics of any strict logic program P coincide in the sense that for each ground literal k, $k \in WFM_P$ iff k is true in each stable model of P. *(p.347)*

### Corollary 61 *(p.348)*

(1) There exists at least one stable model for each call-consistent logic program. *(p.348)*
(2) Clark's completion of a call-consistent program P, $comp(P)$, is consistent. *(p.348)*

### Theorem 62: Meta-Interpreter Architecture *(p.349)*

Let AF = (AR, attacks) be an argumentation framework and E be an extension of AF. Then:
(1) E is a stable extension of AF iff m(E) is a stable model of $P_{AF}$. *(p.349)*
(2) E is a grounded extension of AF iff $m(E) \cup \{\neg defeat(A) \mid A \in E\}$ is the well-founded model of $P_{AF}$. *(p.349)*
(3) The well-founded model and Fitting's model of $P_{AF}$ coincide. *(p.349)*

Where $P_{AF} = APU + AGU$ with:
- $APU = \{C1, C2\}$ where $C1: acc(X) \leftarrow \neg defeat(X)$ and $C2: defeat(X) \leftarrow attack(Y, X), acc(Y)$
- $AGU = \{attack(A,B) \leftarrow \mid (A,B) \in attacks\}$
*(pp.348--349)*

## Parameters

This is a purely theoretical/formal paper. There are no empirical parameters, numerical constants, or measurable quantities. *(throughout)*

## Implementation Details

### Meta-Interpreter Architecture (Section 5) *(pp.348--349)*

An argumentation system consists of two components:
1. **AGU (Argument Generation Unit)**: generates arguments and the attack relationship between them *(p.348)*
2. **APU (Argument Processing Unit)**: determines acceptability of arguments *(p.348)*

The APU is a logic program with two clauses:
- C1: $acc(X) \leftarrow \neg defeat(X)$ --- an argument X is acceptable if it is not defeated *(p.348)*
- C2: $defeat(X) \leftarrow attack(Y, X), acc(Y)$ --- an argument X is defeated if it is attacked by an acceptable argument Y *(p.348)*

The AGU generates facts of the form $attack(A, B)$ for each $(A, B) \in attacks$. *(p.349)*

This architecture acts as a **schema for generating meta-interpreters** for argumentation systems, analogous to a compiler-compiler. *(p.348)*

Logic-based knowledge bases can be viewed as argumentation systems where the knowledge is coded in the structure of arguments and the logic is used to determine acceptability. Kowalski's equation: **Knowledge Base = Knowledge + Logic**. *(p.350)*

### Argumentation Framework for Default Logic (Section 4.1) *(pp.339--340)*

Given a default theory $T = (D, W)$:
- $AR_T = \{(K, k) \mid K \subseteq Jus(D), K$ is a support for $k$ with respect to $T\}$ *(p.340)*
- $(K, k)$ attacks $(K', k')$ iff $\neg k \in K'$ *(p.340)*

### Argumentation Framework for Logic Programming --- Negation as Possibly Infinite Failure (Section 4.3.1) *(p.343)*

Given logic program P:
- $AR = \{(K, k) \mid K$ is a support for $k$ with respect to $P\} \cup \{(\{\neg k\}, \neg k) \mid k$ is a ground atom$\}$ *(p.343)*
- $(K, h)$ attacks $(K', h')$ iff $h^* \in K'$ *(p.343)*

Note: The set of arguments $AR$ in $AF_{napif}(P)$ is in general not recursively decidable (Lemma 51), making these semantics incomputable (Theorem 52). *(p.345)*

### Argumentation Framework for Logic Programming --- Negation as Finite Failure (Section 4.3.2) *(p.345)*

Given logic program P:
- $AR = \{(K, k) \mid \exists C \in G_P: head(C) = k$ and $body(C) = K\} \cup \{(\{\neg k\}, \neg k) \mid k$ is a ground atom$\}$ *(p.345)*
- $(K, h)$ attacks $(K', h')$ iff $h^* \in K'$ *(p.345)*

Note: Each ground instance of a clause constitutes an argument for its head (Remark 53), making $AR$ computable (Lemma 54). *(p.345)*

### Stable Marriage Problem Encoding (Section 3.2) *(p.337)*

Given sets M (men) and W (women):
- $AR = M \times W$ *(p.337)*
- $(C, D)$ attacks $(A, B)$ iff (1) $A = C$ and A prefers D to B, or (2) $D = B$ and B prefers C to A *(p.337)*

### N-Person Game Encoding (Section 3.1) *(pp.335--336)*

Given a cooperative n-person game with characteristic function V:
- $AR = IMP$ (set of imputations, i.e. payoff vectors) *(p.335)*
- $(p_1, \ldots, p_n)$ attacks $(q_1, \ldots, q_n)$ iff there exists a coalition $K \subseteq \{1, \ldots, n\}$ such that for each $i \in K$, $p_i > q_i$ and $p_{i1} + \cdots + p_{ik} \leq V(K)$ *(p.335)*

NM-solutions satisfy two postulates:
- (NM1) No s in S is dominated by an s' in S (internal stability / conflict-free) *(p.335)*
- (NM2) Every s not in S is dominated by some s' in S (external stability) *(p.335)*

## Figures of Interest

- **Dependency tree** (p.325): Section 2 is prerequisite for Sections 3, 4, and 5
- **AGU/APU architecture diagram** (p.349): AGU feeds attack relations to APU, which outputs acceptable arguments

## Results Summary

The paper establishes a complete hierarchy of argumentation semantics and proves their correspondences: *(pp.327--334)*
- Stable $\subset$ Preferred $\subset$ Complete (as sets) *(pp.328, 330)*
- Grounded = least Complete extension = least fixed point of $F_{AF}$ *(pp.329--330)*
- Every stable extension is preferred, but not vice versa *(p.328)*
- Every preferred extension is complete, but not vice versa *(p.330)*
- Well-founded frameworks have a single extension that is simultaneously grounded, preferred, and stable *(p.331)*
- Limited controversial frameworks are coherent (preferred = stable) *(p.332)*
- Uncontroversial frameworks are coherent and relatively grounded *(p.332)*
- The framework unifies Reiter's default logic, Pollock's defeasible reasoning, and logic programming (both finite and infinite failure) as special cases *(pp.339--347)*

### Logic Programming Coincidence Results *(p.347)*

- Stratified programs: $AF_{napif}(P)$ is well-founded, so stable and well-founded semantics coincide *(p.347)*
- Hierarchical programs: $AF_{naff}(P)$ is well-founded *(p.347)*
- Strict programs: both AF constructions are uncontroversial, so all semantics coincide *(p.347)*
- Call-consistent programs: both AF constructions are limited controversial, guaranteeing at least one stable model *(pp.347--348)*

### Key Insight on Stable Semantics *(p.338)*

The paper argues that a knowledge base lacking stable semantics is "not necessarily a bug" --- the Stable Marriage Problem with Gays (SMPG) naturally has no stable semantics when a love triangle exists, reflecting genuine indeterminacy in the problem. *(p.338)*

## Limitations

- Arguments are treated as abstract entities with no internal structure --- this abstraction is powerful but means the theory cannot differentiate between types of attacks (e.g., rebutting vs. undercutting) *(p.326)*
- The theory does not address the **strength** of arguments or attacks --- all attacks are treated equally *(throughout)*
- For logic programming with negation as possibly infinite failure, the resulting semantics are in general **incomputable** (Theorem 52) *(p.345)*
- The problem of self-defeating arguments (e.g., argumentation framework $\langle\{A,B\}, \{(A,A), (A,B)\}\rangle$) is acknowledged but not resolved *(p.328)*
- The theory provides no mechanism for **preference** among arguments beyond the basic attack relation *(throughout)*
- The paper acknowledges that attacks may have different strengths ("some attacks against some arguments may have different strengths, one may be more 'deadly' than the others") but does not address this; deferred to future work [13] *(p.351)*

## Arguments Against Prior Work

- **Prior work on argument structure ignored acceptability.** Extensive work existed on the *structure* of arguments (Birnbaum [5,6], Cohen [9], Vreeswijk [61]), but none had formalized the central question of which arguments a rational agent should *accept*. "It is still not clear how to understand the acceptability of arguments." *(pp.322--323)*
- **False dichotomy between "internal" and "external" stability.** Prior approaches split into extension-based (Reiter's default logic [52], stable models [22]) emphasizing internal consistency, and argument-based (Pollock [45,46], Simari and Loui [57]) emphasizing defense against attack. Dung argues these are "two sides of the same coin" --- the relationship "is very much similar to the relationship between Hintikka's game-theoretic semantics and Tarkian semantics of logic and natural language." *(p.323)*
- **Mozer's distinction between default and autoepistemic reasoning is superficial.** Mozer [42] distinguished default reasoning (arguing with Nature) from autoepistemic reasoning (arguing with oneself). Dung argues both are forms of argumentation, since "all forms of reasoning with incomplete information rest on the simple intuitive idea that a defeasible statement can be believed only in the absence of any evidence to the contrary which is very much like the principle of argumentation." *(pp.323--324)*
- **"No stable semantics = bug" is wrong.** The AI and logic programming community commonly held that if a knowledge base has no stable semantics, "there is something 'wrong' in it." Dung defeats this view by showing the Stable Marriage Problem with Gays (SMPG) naturally has no stable semantics when a love triangle exists --- reflecting genuine indeterminacy, not a defect. "Let P be a knowledge base represented either as a logic program, or as a nonmonotonic theory or as an argumentation framework. Then there is not necessarily a 'bug' in P if P has no stable semantics." *(p.338)*
- **Von Neuman and Morgenstern's existence conjecture was wrong.** Von Neuman and Morgenstern believed every cooperative n-person game has an NM-solution. Lucas constructed a ten-person game with no NM-solution [56], and Shubik pointed out that games without NM-solutions model meaningful economic systems. Dung's preferred extensions provide a new solution concept for these cases. *(p.336)*
- **R-extension semantics has a "paradox" that preferred extension semantics avoids.** The default $(:\neg p/p)$ can prevent concluding $q$ in the theory $T = (\{(:\neg p/p)\}, \{q\})$. R-extension semantics does exactly that (a bug), while preferred extension semantics does not. "How can we know that the bug is in D and not in W? We know it thanks to the preferred extension of AF(T)!" *(p.341)*
- **Other argument systems focus only on structure, not acceptability.** Many argument systems (Lin and Shoham [36], Vreeswijk [61], Simari and Loui [57]) classify arguments by structure (deductive, inductive, etc.) but "the attack-relationship between arguments and their acceptability are not discussed at all" in [36], and [57] adopts Pollock's criterion without providing a general mechanism. *(p.351)*

## Design Rationale

- **"The one who has the last word laughs best."** The entire theory is built on this principle: an argument is acceptable if every attack against it can be counterattacked. This is formalized as: argument A is acceptable w.r.t. set S iff for each attacker B, S attacks B. *(p.322, 326)*
- **Abstraction by design.** Arguments are deliberately treated as abstract entities "whose role is solely determined by its relations to other arguments. No special attention is paid to the internal structure of the arguments." This enables the theory to unify disparate formalisms (default logic, LP, game theory) that differ in argument structure but share acceptability principles. *(p.326)*
- **Rational agent model drives definitions.** "For a rational agent G, an argument A is acceptable if G can defend A (from within his world) against all attacks on A." The requirement that accepted arguments form a conflict-free, self-defending set leads naturally to admissibility. *(p.326)*
- **Correctness via unification, not axioms.** The theory's "correctness" cannot be proved formally; instead it is demonstrated by showing it captures existing formalisms as special cases. Two "examples": (1) nonmonotonic reasoning and LP are forms of argumentation; (2) n-person game solutions and stable marriages are stable extensions. *(pp.324--325)*
- **Multiple semantics for different reasoning attitudes.** Preferred extensions capture credulous reasoning (believe everything defensible); grounded extension captures skeptical reasoning (believe only what is forced). Complete extensions bridge the two. This deliberate spectrum lets the framework model different agents with different epistemological commitments. *(pp.327--330)*
- **Fixpoint theory for skeptical semantics.** The characteristic function $F_{AF}$ is monotonic, guaranteeing a least fixed point (grounded extension). This provides an elegant, constructive characterization of skeptical reasoning. *(pp.328--329)*
- **Meta-interpreter architecture separates concerns.** The AGU (Argument Generation Unit) handles domain-specific argument construction; the APU (Argument Processing Unit) is a fixed, domain-independent two-clause logic program. This separation makes argumentation systems implementable as logic programs, analogous to compiler-compilers. *(pp.348--349)*
- **Kowalski's equation as architectural principle.** "Knowledge Base = Knowledge + Logic" --- knowledge is encoded in argument structure (AGU), logic determines acceptability (APU). Different argumentation systems share the same APU but differ in their AGU. *(p.350)*

## Testable Properties

- Every argumentation framework has at least one preferred extension (Corollary 12) *(p.327)*
- Every stable extension is a preferred extension (Lemma 15) *(p.328)*
- Not every preferred extension is stable (Lemma 15, counterexample: AF with AR={A} and attacks={(A,A)}) *(p.328)*
- The empty set is always admissible *(p.327)*
- $F_{AF}$ is monotonic with respect to set inclusion (Lemma 19) *(p.329)*
- Every well-founded framework has exactly one complete extension which is grounded, preferred, and stable (Theorem 30) *(p.331)*
- Every limited controversial framework is coherent (Theorem 33(1)) *(p.332)*
- Every limited controversial framework has at least one stable extension (Corollary 36) *(p.334)*
- For finitary frameworks, $F_{AF}$ is $\omega$-continuous (Lemma 28) *(p.330)*
- Grounded extension = intersection of all preferred extensions, for uncontroversial frameworks (Theorem 33(2)) *(p.332)*
- NM-solutions of cooperative n-person games = stable extensions of corresponding argumentation framework (Theorem 37) *(p.336)*
- Solutions to stable marriage problem = stable extensions of corresponding argumentation framework (Theorem 39) *(p.337)*
- R-extensions of default theories = stable extensions of corresponding argumentation framework (Theorem 43) *(pp.340--341)*
- Indefeasible arguments $\subseteq$ grounded extension; equality holds for finitary frameworks (Theorem 47) *(p.342)*
- Stable models of P $\leftrightarrow$ stable extensions of $AF_{napif}(P)$ (Theorem 49) *(p.344)*
- Well-founded model of P = grounded extension of $AF_{napif}(P)$ (Theorem 50) *(p.344)*
- Models of Clark's completion $\leftrightarrow$ stable extensions of $AF_{naff}(P)$ (Theorem 55) *(p.346)*
- Fitting's model = grounded extension of $AF_{naff}(P)$ (Theorem 56) *(p.346)*
- Stratified programs: stable and well-founded semantics coincide (Corollary 59) *(p.347)*
- Strict programs: all semantics (well-founded, stable, preferred) coincide (Corollary 60) *(p.347)*
- Call-consistent programs have at least one stable model (Corollary 61) *(p.348)*
- E is stable extension of AF iff m(E) is stable model of $P_{AF}$ (Theorem 62(1)) *(p.349)*

## Relevance to Project

This paper is foundational for the propstore's world model architecture. Argumentation frameworks provide the theoretical basis for reasoning about conflicting claims: when two claims from different papers contradict each other, they can be modeled as arguments that attack each other. The different semantics (preferred, stable, grounded) offer different strategies for resolving conflicts --- credulous (preferred) vs. skeptical (grounded). *(pp.326--330)* The paper also connects directly to the truth maintenance systems already in the collection (Doyle 1979, de Kleer 1986) since both TMS and argumentation deal with maintaining consistent belief sets under conflicting evidence. The meta-interpreter architecture (Section 5) provides a concrete implementation path via logic programming. *(pp.348--349)*

## Open Questions

- [ ] How to extend the framework with argument strength/preference (addressed in Dung's later work [13]) *(p.?)*
- [ ] How to handle self-defeating arguments systematically *(p.328)*
- [ ] Practical computational complexity of preferred/stable extension computation for real-world argumentation frameworks *(p.345)*
- [ ] Connection to structured argumentation frameworks (ASPIC+, ABA) that build on this abstract foundation [Addressed by Modgil_2014_ASPICFrameworkStructuredArgumentation -- ASPIC+ builds structured arguments from strict/defeasible rules and knowledge bases, then generates Dung-style AFs and applies Dung's semantics]

## Related Work Worth Reading

- Bondarenko, Toni and Kowalski [7] --- assumption-based framework unifying many nonmonotonic approaches *(p.324)*
- Pollock [45, 46] --- defeasible reasoning theory based on prima facie reasons and defeaters *(p.341)*
- Reiter [52] --- default logic (R-extensions correspond to stable extensions) *(p.339)*
- Lin and Shoham [36] --- argument systems as uniform basis for nonmonotonic reasoning *(p.323)*
- Kakas, Kowalski and Toni [27] --- argumentational approach to logic programming *(p.324)*
- Vreeswijk [61] --- feasibility of defeat in defeasible reasoning *(p.323)*
- Von Neuman and Morgenstern [62] --- original theory of n-person games *(p.334)*

## Collection Cross-References

### Already in Collection
- [[Reiter_1980_DefaultReasoning]] — cited as [52]; Dung proves that R-extensions of default theories correspond exactly to stable extensions of the corresponding argumentation framework (Theorem 43). *(pp.339--341)*
- [[Pollock_1987_DefeasibleReasoning]] — cited as [45]; Dung proves that Pollock's indefeasible arguments correspond to the grounded extension (Theorem 47), showing defeasible reasoning is a special case of abstract argumentation. *(pp.341--342)*

### New Leads (Not Yet in Collection)
- Bondarenko, Toni and Kowalski (1993) — assumption-based framework (ABA) that extends Dung's work *(p.324)*
- Pollock, J.L. (1994) — "Justification and defeat" — later Pollock work that Dung references *(p.341)*
- Lin and Shoham (1989) — "Argument systems: a uniform basis for nonmonotonic reasoning" *(p.323)*
- Lucas, F.W. — constructed a ten-person game with no NM-solution *(p.336)*
- Shubik — pointed out that games without NM-solutions model meaningful economic systems *(p.336)*

### Supersedes or Recontextualizes
- (none)

### Cited By (in Collection)
- [[Modgil_2014_ASPICFrameworkStructuredArgumentation]] — builds structured argumentation on top of Dung's abstract framework, generating Dung-style AFs from knowledge bases with strict/defeasible rules and applying Dung's semantics to determine justified arguments
- [[Cayrol_2005_AcceptabilityArgumentsBipolarArgumentation]] — extends Dung's framework with an independent support relation, defining bipolar argumentation frameworks (BAFs) with three new admissibility semantics (d-admissible, s-admissible, c-admissible) that generalize Dung's preferred and stable extensions by enforcing coherence between support and defeat
- [[Modgil_2018_GeneralAccountArgumentationPreferences]] — cited as [23]; builds on Dung's framework to provide a general account of structured argumentation with preferences via ASPIC+, proving rationality postulates hold for attack-based conflict-free extensions and connecting stable extensions to Brewka's preferred subtheories
- [[Odekerken_2023_ArgumentationReasoningASPICIncompleteInformation]] — cited as ref 11; extends ASPIC+ (which builds on Dung's grounded semantics) to handle incomplete information, defining four justification statuses and stability/relevance decision problems for literals under grounded semantics
- [[Niskanen_2020_ToksiaEfficientAbstractArgumentation]] — implements SAT-based computation of all Dung semantics (complete, preferred, stable, semi-stable, stage, grounded, ideal) with concrete encodings; ICCMA 2019 competition winner demonstrating practical scalability of Dung's framework
- [[Charwat_2015_MethodsSolvingReasoningProblems]] — cited as ref [1]; comprehensive survey of SAT, ASP, CSP, labelling, dialogue game, and dynamic programming methods for computing Dung's semantics, providing formal encodings and complexity analysis for all standard reasoning problems

### Conceptual Links (not citation-based)
- [[Doyle_1979_TruthMaintenanceSystem]] — **Strong.** Doyle's TMS maintains a single consistent belief set under contradictions; Dung's argumentation frameworks provide the abstract semantics for determining which beliefs (arguments) should be accepted. The TMS's dependency-directed backtracking when contradictions arise is an operational procedure for computing something like a grounded or preferred extension.
- [[deKleer_1986_AssumptionBasedTMS]] — **Strong.** ATMS environments (consistent assumption sets) correspond to conflict-free sets in argumentation frameworks. ATMS nogoods correspond to attack relations. The ATMS's management of multiple simultaneous consistent contexts maps to the multiple extensions (preferred, stable) that Dung defines.
- [[Clark_2014_Micropublications]] — **Strong.** Clark's micropublication model is grounded in Toulmin-Verheij defeasible argumentation theory, with explicit support and challenge relations. Dung's abstract argumentation frameworks provide the formal semantics for the challenge/attack relations that Clark models. Clark's bipolar claim-evidence networks (Use Case 8) are instances of Dung's argumentation frameworks with both support and attack.
- [[Alchourron_1985_TheoryChange]] — **Moderate.** AGM belief revision and Dung's argumentation both address rational management of contradictory beliefs. AGM provides postulates for how belief sets should change; Dung provides semantics for which arguments to accept. Different formalizations of the consistency-maintenance problem.
- [[Pollock_1987_DefeasibleReasoning]] — **Strong.** Pollock provides the epistemological theory of defeasible reasoning (prima facie reasons, rebutting/undercutting defeaters, warrant via defeat levels); Dung proves this is a special case of abstract argumentation. Pollock's OSCAR implementation and Dung's meta-interpreter architecture are complementary computational approaches.
- [[Shapiro_1998_BeliefRevisionTMS]] — **Moderate.** Shapiro surveys TMS architectures as belief revision mechanisms; Dung's argumentation frameworks provide an alternative abstract framework for the same problem of maintaining consistent beliefs under conflict.
- [[Mahmood_2025_Structure-AwareEncodingsArgumentationProperties]] — **Strong.** Provides complete SAT/QSAT encodings for computing all of Dung's extension semantics (stable, admissible, complete, preferred, semi-stable, stage), with tight complexity bounds. Makes Dung's theoretical semantics computationally tractable via SAT solvers.
- [[Tang_2025_EncodingArgumentationFrameworksPropositional]] — **Strong.** Encodes Dung's AF semantics into multi-valued and fuzzy propositional logic systems, proving that stable semantics = normal encoding + Kleene PL3, and complete semantics = normal encoding + Lukasiewicz PL3. Also establishes connections to Gabbay's equational semantics and proposes new fuzzy semantics Eq^L. Provides a precise logical characterization of Dung's abstract definitions.
- [[Popescu_2024_ProbabilisticArgumentationConstellation]] — **Strong.** Popescu & Wallner provide exact tree-decomposition DP algorithms for computing probabilities over Dung's extension semantics (admissible, complete, stable, preferred) under the constellation approach. The I/O/U labelling in the DP is a direct encoding of Caminada's labelling characterization of Dung's semantics, making this the probabilistic computation layer for Dung's foundational definitions.
- [[Brewka_2010_AbstractDialecticalFrameworks]] — **Strong.** Brewka & Woltran generalize Dung AFs by replacing the single attack relation with per-node acceptance conditions (arbitrary propositional formulas over parents). Dung AFs are the special case where each acceptance condition is the conjunction of negated attackers. All of Dung's semantics (grounded, complete, preferred, stable) are lifted to ADFs, with stable/preferred requiring restriction to bipolar ADFs.
