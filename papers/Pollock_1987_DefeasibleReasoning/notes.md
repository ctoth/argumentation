---
title: "Defeasible Reasoning"
authors: "John L. Pollock"
year: 1987
venue: "Cognitive Science"
doi_url: "https://doi.org/10.1207/s15516709cog1104_4"
pages: "481-518"
institution: "University of Arizona, Department of Philosophy"
---

# Defeasible Reasoning

## One-Sentence Summary
Develops a formal theory of defeasible (nonmonotonic) reasoning grounded in epistemology, distinguishing prima facie reasons from conclusive reasons, rebutting from undercutting defeaters, and implements these distinctions in a computer program called OSCAR that performs belief adoption, defeat, and reinstatement. *(p.481)*

## Problem Addressed
Both epistemology and AI deal with nonmonotonic reasoning (where conclusions can be withdrawn given new information), but AI approaches are simplistic and overlook the fine structure of defeasible reasoning that epistemologists have identified. *(p.482)* Conversely, epistemological theories are too abstract to implement. *(p.482)* Pollock bridges this gap by constructing a theory precise enough to implement as a computer program, while being grounded in the philosophical analysis of reasons and defeaters. *(p.482)*

## Key Contributions
- Distinguishes **prima facie reasons** (defeasible) from **conclusive reasons** (nondefeasible/deductive), and formalizes both as building blocks of arguments *(p.484)*
- Distinguishes **rebutting defeaters** (reasons for denying the conclusion) from **undercutting defeaters** (reasons for denying the connection between reason and conclusion), arguing that undercutting defeat has been generally overlooked in AI *(p.485)*
- Defines **warrant** as what an ideal reasoner would believe: a proposition is warranted iff supported by an ultimately undefeated argument *(p.492)*
- Formalizes warrant via **levels of defeat and reinstatement**: level 0 arguments are all arguments; level n+1 arguments are level 0 arguments not defeated by any level n argument; ultimately undefeated arguments are those that are level n arguments for every n > m *(p.491-492)*
- Introduces the **principle of collective defeat** (4.4): if a set of propositions is believed and each member has an equally good defeasible argument, but the conjunction of their premises defeats the original argument, then none of the propositions in the set is warranted on those defeasible arguments *(p.493)*
- Identifies **self-defeating arguments** (4.5): arguments that support a defeater for one of their own defeasible steps, and argues these should be excluded from competition *(p.495)*
- Extends the theory to **nonlinear (indirect) arguments** using conditionalization and weak conditionalization rules *(p.496-498)*
- Proves **logical properties of warrant**: warranted propositions are deductively consistent (5.4), closed under deductive consequence (5.5), and satisfy a deduction theorem analogue (5.7) *(p.499)*
- Generalizes collective defeat to **collective undercutting defeat** (5.8) and proves the **principle of joint defeat** (5.9, 5.10) *(p.500-501)*
- Distinguishes warrant (ideal reasoner) from **justified belief** (real reasoner with finite memory), formulating rules for belief formation that appeal to local context rather than global argument structure *(p.504)*
- Identifies three categories of belief-formation rules: **adoption rules**, **defeat rules**, and **reinstatement rules** *(p.505)*
- Implements the theory in **OSCAR**, a computer program for defeasible reasoning, with concrete rules for adoption (ADOPT-ON, ADOPT-CON), retraction (UNDERCUT, REBUTa/b), collective defeat (NEG-COL-DEFa/b, POS-COL-DEFa/b), backtracking (BACKTRACK), reinstatement (U-REINSTATE, R-REINSTATE/U, R-REINSTATE/R), and hereditary retraction (H-RETRACT) *(p.512-514)*
- Introduces key data structures: **onset** (believed on defeasible basis), **conset** (believed on conclusive basis), **beliefs** (all believed propositions), **adoptionset** (newly adopted), **retractionset** (newly retracted), **rebut** (pairs entering collective defeat) *(p.509-511)*
- Argues that reasoning is governed by internalized rules constituting procedural knowledge, giving rise to a competence/performance distinction analogous to linguistics *(p.483)*
- Argues that reasons need not be beliefs -- perceptual states are nondoxastic foundational states that can serve as reasons *(p.483-484)*
- Introduces the mnemonic prima facie reason: memory itself provides defeasible justification for remembered beliefs *(p.487)*
- Discusses the role of **projectibility** in constraining the statistical syllogism to avoid paradoxes *(p.488)*
- Introduces the concept of **prima facie warranted** propositions as an analogue to default assumptions in AI *(p.502)*
- Contrasts OSCAR's approach (storing only immediate bases) with Doyle's TMS (storing all arguments), arguing the latter creates an excessive memory burden *(p.508)*

## Methodology
The paper proceeds in three parts: Part I (pp. 481-489) establishes the philosophical foundations (human rational architecture, types of reasons, kinds of defeaters, substantive examples from perception, memory, statistical syllogism, and induction). Part II (pp. 490-504) constructs the formal theory of warrant for an ideal reasoner, addressing collective defeat, self-defeating arguments, indirect arguments, and logical properties. Part III (pp. 504-518) moves from warrant to justified belief, constructing concrete rules for defeasible reasoning implementable in a computer program (OSCAR), and assessing its strengths and limitations. *(p.482)*

## Key Equations

Definition of reason:

$$
\text{Being in states } M_1, \ldots, M_n \text{ is a reason for S to believe Q iff it is logically possible for S to be justified in believing Q on the basis of being in states } M_1, \ldots, M_n
$$

Definition (2.1). *(p.484)*

Prima facie reason:

$$
\text{P is a prima facie reason for S to believe Q iff P is a reason for S to believe Q and there is an R such that R is logically consistent with P but (P \& R) is not a reason for S to believe Q}
$$

Definition (2.2). *(p.484)*

Defeater:

$$
\text{R is a defeater for P as a prima facie reason for Q iff P is a prima facie reason for S to believe Q and R is logically consistent with P but (P \& R) is not a reason for S to believe Q}
$$

Definition (2.3). *(p.484)*

Rebutting defeater:

$$
\text{R is a rebutting defeater for P as a prima facie reason for Q iff R is a defeater and R is a reason for believing } \neg Q
$$

Definition (2.4). *(p.485)*

Undercutting defeater:

$$
\text{R is an undercutting defeater for P as a prima facie reason for S to believe Q iff R is a defeater and R is a reason for denying that P wouldn't be true unless Q were true}
$$

Definition (2.5). Symbolized as P->Q (a material-like conditional). *(p.485)*

Defeat relation between argument lines:

$$
\langle \eta, j \rangle \text{ defeats } \langle \sigma, i \rangle \text{ iff } \langle \sigma, i \rangle \text{ is obtained by rule } \mathbf{R} \text{ using } \{P_1, \ldots, P_n\} \text{ as a prima facie reason for Q, and } \eta_j \text{ is either } \neg Q \text{ or } \neg[(P_1 \& \ldots \& P_n) \rightarrow Q]
$$

Definition (4.1) for linear arguments. *(p.491)*

Level n+1 argument:

$$
\sigma \text{ is a level } (n+1) \text{ argument iff } \sigma \text{ is a level 0 argument and there is no level } n \text{ argument } \eta \text{ such that for some } i \text{ and } j, \langle \eta, j \rangle \text{ defeats } \langle \sigma, i \rangle
$$

Definition (4.2). *(p.492)*

Ultimately undefeated:

$$
\sigma \text{ is ultimately undefeated iff there is some } m \text{ such that } \sigma \text{ is a level } n \text{ argument for every } n > m
$$

*(p.492)*

Warrant:

$$
\text{P is warranted relative to an epistemic basis iff P is supported by some ultimately undefeated argument proceeding from that epistemic basis}
$$

Principle (4.3). *(p.492)*

Self-defeating argument:

$$
\sigma \text{ is self-defeating iff } \sigma \text{ supports a defeater for one of its own defeasible steps, i.e., for some } i \text{ and } j, \langle \sigma, i \rangle \text{ defeats } \langle \sigma, j \rangle
$$

Definition (4.5). *(p.495)*

Defeat for indirect arguments:

$$
\langle \eta, j \rangle \text{ defeats } \langle \sigma, i \rangle \text{ iff (1) } \langle \sigma, i \rangle \text{ is obtained by rule } \mathbf{R} \text{ using } \{P_1, \ldots, P_n\} \text{ as a prima facie reason for Q, (2) } \eta_j \text{ is either } \neg Q \text{ or } \neg[(P_1 \& \ldots \& P_n) \rightarrow Q], \text{ and (3) } p(\eta,j) = p(\sigma,i)
$$

Definition (5.1). Generalizes (4.1) to require shared premise sets. *(p.498)*

Statistical syllogism:

$$
\text{If G is projectible with respect to F, } \text{prob}(Gx/Fx) \text{ is high, and } Fa, \text{ then this is a prima facie reason for } Ga
$$

Principle (3.10). Strength of the reason determined by how high the probability is. *(p.488)*

Undercutting defeater for statistical syllogism:

$$
\text{If G is projectible with respect to } (F \& H), \text{ prob}(Gx/Fx \& Hx) < \text{prob}(Gx/Fx), \text{ and } Ha, \text{ then this is an undercutting defeater for (3.10)}
$$

Principle (3.11). *(p.489)*

Logical properties of warrant (selected):

$$
\text{If } \Gamma \vdash P \text{ then } \Gamma \models_E P
$$

Principle (5.3): deductive consequences of warranted propositions are warranted. *(p.499)*

$$
\text{If } \Gamma \text{ is deductively consistent, so is } \{P \mid \Gamma \models_E P\}
$$

Principle (5.4): the set of warranted propositions is deductively consistent. *(p.499)*

$$
\text{If for every P in } \Gamma, A \models_E P, \text{ and } \Gamma \models_E Q, \text{ then } A \models_E Q
$$

Principle (5.6): warrant is closed under deductive consequence. *(p.499)*

$$
\text{If } \Gamma \cup \{P\} \models_E Q \text{ then } \Gamma \models_E (P \supset Q)
$$

Principle (5.7): deduction theorem analogue for warrant. *(p.499)*

Principle of joint defeat:

$$
\text{(5.9) Given P is a prima facie reason for Q and R is a prima facie reason for S, and T = } \neg(P \rightarrow Q) \text{ and U = } \neg(R \rightarrow S), \text{ if "T v U" is warranted but neither T nor U is, then no argument using P as a reason for Q or R as a reason for S is ultimately undefeated.}
$$

*(p.501)*

$$
\text{(5.10) Given a finite set of triples } \langle P_i, Q_i, R_i \rangle \text{ where } P_i \text{ is a prima facie reason for } Q_i \text{ and } R_i = \neg(P_i \rightarrow Q_i), \text{ if the disjunction of all } R_i\text{'s is warranted but every proper subset's disjunction is unwarranted, then no argument using } P_i \text{ as a reason for } Q_i \text{ is ultimately undefeated.}
$$

*(p.501)*

Prima facie warrant:

$$
\text{P is prima facie warranted iff, relative to every epistemic basis, P is automatically warranted in the absence of a reason for believing } \neg P
$$

Definition (5.11). *(p.502)*

## Parameters

This paper is primarily a theoretical/philosophical work and does not contain quantitative parameters or measurements in the conventional sense. The framework is entirely qualitative.

## Implementation Details

### Three Simplifying Assumptions for OSCAR
1. All arguments are linear (no conditionalization or indirect arguments) *(p.507)*
2. The system is interested in everything (draws all possible conclusions from input) *(p.507-508)*
3. All reasons have the same strength (whenever there is a reason for P and a reason for ~P, collective defeat occurs) *(p.508)*

### Data Structures
- **beliefs**: set of all believed propositions *(p.508)*
- **onset**: set of pairs <P,X> where P is believed on basis of defeasible reason X *(p.509)*
- **conset**: set of pairs <P,X> where P is believed on basis of conclusive reason X *(p.509)*
- **adoptionset**: set of newly adopted beliefs (cleared each cycle) *(p.508)*
- **retractionset**: set of newly retracted propositions *(p.511)*
- **rebut**: set of pairs of argument endpoints entering collective rebutting defeat *(p.510)*
- **adoptionflag**: 0/1 flag, set to 1 when any new adoption occurs *(p.511)*
- **retractionflag**: 0/1 flag, set to 1 when any retraction occurs *(p.511-512)*
- **reason schemas**: pairs <X,P> where X is a set of proposition-forms and P is a proposition-form *(p.512)*
- **proposition-forms**: represented via whole_p and parts_p functions; assignments map variables to objects *(p.512)*

### Auxiliary Definitions
- (7.1) S *believes* P *on* X iff S believes P on the basis of defeasible reason X *(p.509)*
- (7.2) S *believes* P *con* X iff S believes P on the basis of conclusive reason X *(p.509)*
- (7.3) Nondefeasible ancestor: q is a nondefeasible ancestor of p if there is a sequence of beliefs linked by conset entries *(p.510)*
- (7.4) Nondefeasible ancestor-set: defined recursively using conset *(p.510)*
- (7.5) q is a nondefeasible ancestor of p iff q is a member of some nondefeasible ancestor-set of p *(p.510)*
- (7.6) q is a nondefeasible ancestor of a set X iff q is a nondefeasible ancestor of some member of X *(p.510)*
- (7.7) X is a nearest defeasible ancestor of proposition p iff X is a set of ordered pairs, the domain of X is a nondefeasible ancestor-set of p, and X is a subset of onset *(p.511)*
- (7.8) X is a nearest defeasible ancestor of a set {p1,...,pn} iff for each i, Xi is a nearest defeasible ancestor for pi, and X = X1 union ... union Xn *(p.511)*
- (7.9) A proposition P is rebutted iff for some set A, <P,X> is in rebut *(p.511)*
- (7.10) Adopting: inserting into beliefs, putting in adoptionset, deleting from retractionset, setting adoptionflag to 1. To adopt P on X: insert <P,X> in onset. To adopt P con X: insert <P,X> in conset. *(p.511)*
- (7.11) Retracting: deleting from beliefs, inserting in retractionset, deleting from adoptionset if there, deleting all <P,X> from onset, setting retractionflag to 1. (For BACKTRACK: also delete <P,X> from conset.) *(p.511-512)*

### OSCAR Algorithm (Figure 7)
1. **Adopt input**: add new beliefs from external sources *(p.515)*
2. **Loop 1 (Adoption module)**: repeatedly run ADOPT-ON, ADOPT-CON, NEG-COL-DEFa, NEG-COL-DEFb, POS-COL-DEF, and R-REINSTATE/U until adoptionflag = 0 *(p.515)*
3. **Run UNDERCUT and REBUT**: apply defeat rules, clear adoptionset, reset retractionflag *(p.515)*
4. **Loop 2 (Retraction and reinstatement module)**: repeatedly run H-RETRACT, BACKTRACK, U-REINSTATE, and R-REINSTATE/R until retractionflag = 0 *(p.515)*
5. **Outer loop**: if adoptionflag = 1 or retractionset is nonempty, clear retractionset and return to Loop 1; otherwise stop *(p.515)*

### Key Rules

**Adoption:** *(p.512)*
- **ADOPT-ON**: For prima facie reason schema <X,q>, if you adopt X!s and don't believe ~(AX!s->q!s) and neither q!s nor ~q!s is rebutted, adopt q!s on X!s
- **ADOPT-CON**: For conclusive reason schema <X,q>, if you adopt X!s and neither q!s nor ~q!s is rebutted, adopt q!s con X!s

**Retraction by undercutting defeat:** *(p.512)*
- **UNDERCUT**: If you adopt ~(AX!s->q!s) and believe q!s on X!s, delete <q!s,X!s> from onset, retract q!s if not believed on any other basis

**Retraction by rebutting defeat:** *(p.513)*
- **REBUTa**: For prima facie reasons, if you believe ~q!s and adopt X!s (or it is newly adopted), then find nearest defeasible ancestors of ~q!s, retract ~q!s and intermediate nondefeasible ancestors, add pairs to rebut
- **REBUTb**: Same for conclusive reasons

**Collective defeat enlargement:** *(p.513)*
- **NEG-COL-DEFa/b**: When adopting X!s and ~q!s is rebutted, add relevant pairs to rebut for negatively-based collective defeat
- **POS-COL-DEFa/b**: When adopting X!s and q!s is rebutted, add relevant pairs for positively-based collective defeat

**Hereditary retraction:** *(p.513)*
- **H-RETRACT**: If you believe q con X or q on X, but retract some member of X, then retract q and delete <q,X> from conset/onset

**Backtracking for conclusive reasons:** *(p.514)*
- **BACKTRACK**: If you believe q con X but retract q, retract X

**Reinstatement:** *(p.514)*
- **U-REINSTATE**: From undercutting defeat: if you retract ~(AX!s->q!s) and neither q!s nor ~q!s is rebutted, adopt every member of X!s
- **R-REINSTATE/U**: From rebutting defeat (during adoption): if you adopt ~(AX!s->q!s) and <q!s,X!s> is in rebut, delete from rebut and adopt every member of range of the sets
- **R-REINSTATE/R**: From rebutting defeat (during retraction): if you retract some member of X and {<q!s,X!s>} is in rebut, delete from rebut and adopt every member of range

## Figures of Interest
- **Fig 1 (p.492):** Three arguments alpha, beta, gamma showing defeat and reinstatement at different levels; gamma is ultimately undefeated. Alpha supports V via Q and R; beta defeats alpha at line (i) via ~R at line (k); gamma defeats beta at line (j) via ~(T->U) at line (m).
- **Fig 2 (p.494):** Lottery paradox: argument sigma supporting R extended by argument eta supporting ~R, illustrating self-defeating argument structure. Sigma leads from premises through R; eta extends sigma through ~T1, ~T2, ..., ~T1000000 to ~R.
- **Fig 3 (p.495):** Paradox of statistical induction with nested arguments showing how self-defeating arguments arise from statistical reasoning. Shows sigma and eta with prob(Bx/Ax) approximately r/n leading to prob(Bx/Ax) approximately (r+k)/(n+k) which contradicts the original conclusion.
- **Fig 4 (p.500):** Collective undercutting defeat example (Smith/Jones reliability). Two arguments from P and Q through R lead to S and T, which generate undercutting defeaters ~[(Q&R)->T] and ~[(P&R)->S].
- **Fig 5 (p.501):** Mixed rebutting/undercutting defeat reducing to collective rebutting defeat. Sigma: P->Q->~R. Eta: S->R->~(P->Q). Shows the symmetry that makes this a case of collective rebutting defeat.
- **Fig 6 (p.510):** Two linear argument chains leading to contradictory conclusions (V and ~V), entering collective rebutting defeat. Shows P->R->T->V and Q->S->U->~V.
- **Fig 7 (p.515):** OSCAR system architecture flowchart showing adoption module (Loop 1), retraction and reinstatement module (Loop 2), and outer control loop with adopt input, flag checks, and stop condition.
- **Fig 8 (p.517):** Two long parallel argument chains (p1->p2->...->pn->~(q1->q2) and q1->q2->...->qn->~(p1->p2)) requiring collective undercutting defeat detection, illustrating a case OSCAR cannot currently handle because it requires tracing back arbitrarily long chains.

## Results Summary
OSCAR correctly handles most cases of defeasible reasoning involving rebutting defeat, undercutting defeat, and reinstatement. *(p.514-515)* It correctly resolves the lottery paradox (self-defeating arguments are excluded). *(p.494-495)* However, it has known defects:
- Cannot handle conditional reasoning (no conditionalization rule implemented) *(p.516)*
- Cannot detect collective undercutting defeat when it requires tracing back arbitrarily long chains (Figure 8) *(p.516-517)*
- The self-defeating argument constraint is not implemented *(p.517)*
- All reasons are treated as equally strong (no strength comparison) *(p.508)*
- The system is interested in all possible conclusions, requiring careful choice of reason schemes to avoid combinatorial explosion *(p.517)*
- An ad hoc fix exists for the conclusive reason contraposition problem but the real solution requires conditional reasoning *(p.516)*

## Arguments Against Prior Work

- **AI theories of nonmonotonic reasoning are simplistic.** "Current theories of nonmonotonic reasoning coming out of AI are simplistic and overlook much of the fine structure of defeasible reasoning." Philosophy has extensive background knowledge about prima facie reasons, defeaters, and warrant that AI has not incorporated. *(p.482)*
- **Undercutting defeaters have been overlooked.** "Undercutting defeaters have generally been overlooked both in philosophy and in AI." Most work on nonmonotonic reasoning (Doyle 1979, McCarthy 1980, Reiter 1980, McDermott and Doyle 1980) focuses only on rebutting defeaters --- reasons for denying the conclusion. Undercutting defeaters attack the *connection* between reason and conclusion rather than the conclusion itself, and are equally important. *(p.485)*
- **Epistemic rules are not independent of psychology.** Pollock argues against the view that epistemic rules (rules for correct reasoning) are "normative" and independent of psychological implementation. He argues this is "a mistake" --- "reasoning is governed by internalized rules. The possession of such internalized rules constitutes procedural knowledge." The competence/performance distinction from linguistics applies: epistemic rules describe what we *should* do, but we don't always conform because reasoning is embedded in a larger system. *(p.483)*
- **Reasoning is not just deduction.** "A common misconception about reasoning is that reasoning is deducing, and in good reasoning the conclusions follow logically from the premises." Nondeductive reasoning (induction, perception, statistical reasoning) is "at least as common as deductive reasoning" and epistemology must accommodate both. *(p.481)*
- **Prior approaches lack a general theory of warrant.** Philosophers "know a lot about some aspects of defeasible reasoning" --- prima facie reasons, defeaters --- "but they do not have a good understanding of precisely how these constituents are used in reasoning." The paper aims to fill this gap with a formal theory of warrant based on defeat levels. *(p.482)*
- **Abstract theory alone is insufficient.** "A theory that looks good in the abstract may not work when you write a program to implement it. From the comfort of his armchair, an epistemologist may be able to find a certain number of counterexamples to a false epistemological theory, but my experience has been that when a program is constructed to implement a theory, it will almost invariably work incorrectly at first." Implementation is the ultimate test. *(p.482)*

## Design Rationale

- **Reasons as the primitive unit.** Reasoning proceeds in terms of *reasons* --- being in states $M_1, \ldots, M_n$ constitutes a reason for $S$ to believe $Q$. Reasons are strung together into arguments, and arguments' conclusions become justified. This reason-based architecture is more primitive than the rule-based or formula-based approaches common in AI. *(pp.483--484)*
- **Two kinds of reasons: defeasible and nondefeasible.** Nondefeasible (conclusive) reasons logically entail their conclusions. Defeasible (prima facie) reasons support their conclusions but can be defeated by additional information. This distinction is fundamental to the architecture. *(p.484)*
- **Two kinds of defeaters: rebutting and undercutting.** Rebutting defeaters are reasons for denying the conclusion. Undercutting defeaters attack the connection between reason and conclusion without supporting the negation of the conclusion. Both are necessary for an adequate theory. *(pp.484--485)*
- **Warrant via defeat levels.** A proposition is warranted (should be believed by an ideal reasoner) if it survives an infinite hierarchy of defeat levels: level 0 = supported by an undefeated argument; level $n+1$ = argument not defeated at level $n$; warranted = eventually stable across all levels. This recursive definition handles chains of defeater-defeaters. *(pp.499--504)*
- **Foundational states ground the system.** Reasoning begins from *foundational states* (perceptual states, memory states) that need not themselves be beliefs. This avoids infinite regress: perception gives you reasons without requiring prior beliefs. *(pp.483--484)*
- **Local rather than global reasoning.** "No real human reasoner is in a position to survey all possible arguments for and against a proposition before deciding what to believe." Rules for belief formation must appeal to local context (the arguments the reasoner has actually constructed), not the global argument structure. *(p.504)*
- **Implementation as epistemological test.** The theory is designed to be implementable in a computer program (OSCAR). Building the program serves as "a mechanical way of generating counterexamples" to the epistemological theory, providing a discipline that armchair analysis cannot. *(p.482)*
- **Simplifying assumptions acknowledged.** The paper explicitly lists simplifications: (1) restricting to linear arguments, (2) assuming the system is interested in everything, (3) treating all reasons as equal strength. These are acknowledged as temporary and the subject of future work. *(pp.507--508)*

## Limitations
- Restricted to linear arguments (no conditionalization/indirect argument support) *(p.507)*
- All reasons treated as equal strength (simplification 3) *(p.508)*
- System interested in everything (may cause combinatorial explosion without interest constraints) *(p.507-508)*
- Self-defeating argument check not implemented (requires expensive backtracking) *(p.517)*
- Collective undercutting defeat not detectable without conditional reasoning *(p.516-517)*
- No theory of projectibility available for constraining statistical syllogism *(p.488)*
- The theory of warrant involves infinitely many levels of defeat/reinstatement; actual reasoners must approximate this *(p.504)*
- Rules for belief formation must appeal to local context rather than global argument structure, because no one can survey all possible arguments *(p.504)*
- Interest-driven deductive reasoning not yet incorporated *(p.518)*

## Additional Findings

### Part I: Philosophical Foundations
- Reasoning is governed by internalized epistemic rules constituting procedural knowledge; these rules comprise a production system *(p.483)*
- Foundational states are nondoxastic: perceptual states can be reasons without being beliefs *(p.483-484)*
- The general notion of a reason (2.1) allows reasons to be mental states, not just beliefs *(p.484)*
- Conclusive (nondefeasible) reasons logically entail their conclusions; e.g., (P & Q) is a conclusive reason for P *(p.484)*
- Undercutting defeaters attack the connection between reason and conclusion, not the conclusion itself; symbolized via P->Q conditional *(p.485)*
- Defeaters can themselves be defeated ("defeater defeaters"), creating chains of arbitrary depth *(p.485)*
- Perception: "I am appeared to as if P" is a prima facie reason to believe P (3.4) *(p.486)*
- Reliability defeaters: discovering the present circumstances are of type C where P's conditional probability is low given C undercuts the perceptual prima facie reason (3.5) *(p.486)*
- Memory provides defeasible justification via the mnemonic prima facie reason (3.6): S's recalling P is a prima facie reason for S to believe P *(p.487)*
- Memory has its own undercutting defeaters: recalling P on basis of a set of beliefs one of which is false (3.7), or not originally believing P for reasons other than the mnemonic reason (3.8) *(p.487)*
- Statistical syllogism (3.9/3.10) requires projectibility constraint to avoid generating self-defeating rebuttals *(p.488)*
- Enumerative induction (3.12): if F is projectible with respect to G, X is a set of F's, all members of X are G, then prima facie reason for "All F's are G" *(p.489)*
- Statistical induction (3.13): similar but for proportions rather than universals *(p.489)*
- Pollock argues the prima facie reasons involved in induction are not primitive but derived from statistical syllogism and probability calculus *(p.489)*

### Part II: Warrant Theory
- Arguments are constructed from foundational states using rules of inference; Rule F (foundations) and Rule R (closure under reasons) govern linear argument formation *(p.491)*
- A line of an argument is an ordered triple <P, R, {m,n,...}> where P is a proposition, R is a rule of inference, and {m,n,...} are line numbers of premises *(p.490)*
- The defeat relation between argument lines requires the defeating line to cite a prima facie reason step in the defeated argument *(p.491)*
- The concept of levels of defeat provides a fixed-point characterization: ultimately undefeated = level n for all sufficiently large n *(p.491-492)*
- The lottery paradox (Kyburg, 1961) is resolved by the self-defeating argument analysis: the extended argument eta that derives ~R is self-defeating because it defeats its own earlier step *(p.494-495)*
- The paradox of statistical induction is similarly resolved via self-defeating arguments *(p.495)*
- Modifying "level 0 argument" to require non-self-defeating arguments resolves the paradoxes while preserving the correctness of collective defeat *(p.496)*
- For nonlinear arguments: Rule F' and Rule R' generalize to include premise sets; Rule P (premise introduction) and Rule C (conditionalization) handle indirect arguments *(p.497)*
- Weak conditionalization (Rule WC) discharges all assumptions at once; differs from Rule C in not requiring the principle of exportation *(p.498)*
- The conservative approach to indirect arguments precludes importing conclusions from enclosing arguments into subsidiary arguments, to avoid accidentally creating self-defeating arguments *(p.496-497)*
- Defeat for indirect arguments (5.1) adds constraint (3): premise sets must match, i.e., p(eta,j) = p(sigma,i) *(p.498)*
- Warranted consequence (5.2) is defined relative to ultimately undefeated arguments containing lines with specific premise sets *(p.498)*
- The deduction theorem analogue (5.7) follows from Rule C and contrasts with the nonmonotonic logic of McDermott and Doyle (1980) *(p.499)*
- Collective undercutting defeat (5.8): analogous to collective rebutting defeat but for undercutting defeaters; the supporting arguments involve defeasible steps from premises S1,...,Sn to conclusion T *(p.500)*
- Mixed rebutting/undercutting cases reduce to collective rebutting defeat (Figure 5) *(p.501)*
- Prima facie warranted propositions (5.11) are analogous to default assumptions but differ: they are not assumptions held until given up, but rather automatically warranted absent specific defeaters *(p.502)*
- Pollock argues defeasible reasoning cannot be replaced by default reasoning from prima facie warranted conditionals, because reason schemas encompass infinitely many cases and defeating one instance does not defeat others *(p.503-504)*

### Part III: OSCAR Implementation
- Warrant is a "global" concept requiring survey of all possible arguments; justified belief must use "local" rules *(p.504)*
- Justified belief only approximates warrant; deductively inconsistent justified beliefs are possible, unlike warrant *(p.504)*
- Rules for reasoning are not modus ponens obligations but permission rules (epistemic permissions) *(p.505)*
- Rule form (6.2): "If you have beliefs P1,...,Pn and you are interested in whether Q is true, then you should believe Q" *(p.505)*
- Rules must be interest-driven to avoid belief clutter, following Harman (1986) *(p.505)*
- Rules must be local (6.3): instantiable without first forming beliefs about how beliefs were formed *(p.506)*
- Defeat rules (6.5/6.6): when you believe Q on basis of argument using P as prima facie reason and adopt a defeater, you should cease believing Q on that basis *(p.506-507)*
- Defeat often proceeds automatically without higher-order monitoring *(p.507)*
- OSCAR must avoid infinite cycling: the theory of warrant handles this via infinite levels, but actual rules must work in finite time *(p.507)*
- OSCAR stores only immediate bases for beliefs, not entire arguments (contrast with Doyle 1979 TMS) *(p.508-509)*
- OSCAR newly adopted beliefs stored in adoptionset; only adoptionset is searched for new inferences (efficiency optimization) *(p.508)*
- In rebutting defeat, the system must backtrack to the last defeasible step of reasoning and rebut that *(p.510)*
- The rebut set stores pairs of argument endpoints entering collective defeat to enable reinstatement *(p.510-511)*
- A proposition is defeated by defeating the last defeasible step of the argument supporting it, either by retracting the premise or undercutting the prima facie reason *(p.510)*

## Testable Properties
- Warranted propositions must be deductively consistent: if P and Q are both warranted from epistemic basis E, then P and Q must not be contradictory *(p.499)*
- Warrant is closed under deductive consequence: if P1,...,Pn are all warranted and Q is a deductive consequence of P1,...,Pn, then Q must be warranted *(p.499)*
- Self-defeating arguments must not contribute to warrant: if an argument's own conclusion defeats one of its own steps, the argument cannot be ultimately undefeated *(p.495-496)*
- In the lottery paradox, no individual ticket-non-draw proposition should be warranted even though each has a high-probability prima facie reason *(p.493-494)*
- Rebutting defeaters and undercutting defeaters must be handled differently: rebutting attacks the conclusion, undercutting attacks the reason-conclusion link *(p.485)*
- Reinstatement must occur: if a defeater is itself defeated, the original conclusion should be restored *(p.492)*
- Collective defeat must handle symmetrical cases: when two equally strong arguments lead to contradictory conclusions, neither should be warranted *(p.493)*
- The deduction theorem analogue must hold: if P is warranted relative to gamma union {Q}, then (Q superset P) is warranted relative to gamma *(p.499)*
- Joint defeat must propagate: if a disjunction of defeaters is warranted but no individual defeater is, all arguments using the corresponding prima facie reasons are defeated *(p.501)*

## Relevance to Project
This paper provides the philosophical and formal foundations for defeasible reasoning that connects directly to the truth maintenance systems already in the propstore collection (Doyle 1979, de Kleer 1986). Pollock's distinction between rebutting and undercutting defeat, his formalization of warrant through levels of defeat and reinstatement, and his concrete implementation in OSCAR provide a complementary epistemological perspective to the more engineering-oriented TMS/ATMS approaches. The principle of collective defeat and the handling of self-defeating arguments are particularly relevant to the propstore's need to manage conflicting claims from different papers.

## Open Questions
- [ ] How does OSCAR's approach compare to ATMS environments for handling multiple competing hypotheses?
- [ ] Can the self-defeating argument constraint be efficiently implemented?
- [ ] How should collective undercutting defeat be detected without full conditional reasoning?
- [ ] What is the relationship between Pollock's warrant levels and de Kleer's assumption labels?
- [ ] How does the equal-strength simplification affect real-world claim adjudication?

## Related Work Worth Reading
- Pollock, J.L. (1986). *Contemporary theories of knowledge*. Totowa, NJ: Rowman and Allanheld. [Full account of the epistemological theory underlying this paper] *(p.483)*
- Doyle, J. (1979). A truth maintenance system. *Artificial Intelligence, 12*, 231-272. [The TMS that OSCAR's approach contrasts with; already in collection] *(p.508)*
- Reiter, R. (1980). A logic for default reasoning. *Artificial Intelligence, 13*, 81-132. [Default logic, the main AI alternative to Pollock's approach; already in collection] *(p.482)*
- McCarthy, J. (1980). Circumscription -- a form of non-monotonic reasoning. *Artificial Intelligence, 13*, 27-39. [Another major AI nonmonotonic approach] *(p.482)*
- Harman, G. (1986). *Change in view*. Cambridge, MA: MIT Press. [Philosophical account of belief revision that Pollock responds to] *(p.505)*
- Pollock, J.L. (1983). Epistemology and probability. *Synthese, 55*, 231-252. [Foundation for statistical syllogism and projectibility] *(p.488)*
- Harman, G. (1984). Positive versus negative undermining in belief revision. *Nous, 18*, 39-49. [Objection about conditional probability reasoning being computationally explosive] *(p.508)*
- Kyburg, H., Jr. (1961). *Probability and the logic of rational belief*. [Source of the lottery paradox] *(p.493)*
- McDermott, D., & Doyle, J. (1980). Non-monotonic logic I. *Artificial Intelligence, 13*, 41-72. [Nonmonotonic logic that lacks deduction theorem; contrast with Pollock's approach] *(p.499)*

## Collection Cross-References

### Already in Collection
- [[Doyle_1979_TruthMaintenanceSystem]] -- cited as Doyle (1979); Pollock contrasts OSCAR's approach (storing only immediate bases, not all arguments) with Doyle's TMS (storing all arguments, creating memory burden). *(p.508)*
- [[Reiter_1980_DefaultReasoning]] -- cited as Reiter (1980); Pollock argues his epistemological approach provides richer structure than Reiter's default logic, particularly the rebutting/undercutting defeat distinction that default logic lacks. *(p.482)*

### New Leads (Not Yet in Collection)
- Pollock, J.L. (1986) -- "Contemporary theories of knowledge" -- full epistemological theory underlying this paper *(p.483)*
- Harman, G. (1986) -- "Change in view" -- competing philosophical account of belief revision *(p.505)*

### Now in Collection (previously listed as leads)
- [[McCarthy_1980_CircumscriptionFormNon-MonotonicReasoning]] -- McCarthy's circumscription formalism formalizes the conjecture that entities satisfying a predicate are only those provably required, using a sentence schema in first-order logic. Pollock critiques this approach (along with Reiter and McDermott-Doyle) for overlooking undercutting defeaters — circumscription handles only predicate minimization, not the epistemological distinction between rebutting and undercutting defeat that Pollock identifies as essential.

### Supersedes or Recontextualizes
- (none)

### Cited By (in Collection)
- [[Dung_1995_AcceptabilityArguments]] -- cited as [45]; Dung proves Pollock's indefeasible arguments correspond to the grounded extension of the corresponding argumentation framework (Theorem 47)
- [[Modgil_2018_GeneralAccountArgumentationPreferences]] -- cited as [37]; Pollock's rebutting/undercutting defeater distinction is formalized as two of ASPIC+'s three attack types (rebutting and undercutting attacks)

### Conceptual Links (not citation-based)
- [[Dung_1995_AcceptabilityArguments]] -- **Strong.** Dung proves that Pollock's defeasible reasoning is a special case of abstract argumentation (Theorem 47). Pollock provides the epistemological content (prima facie reasons, rebutting/undercutting defeaters, warrant via defeat levels); Dung provides the abstract mathematical framework. OSCAR's adoption/retraction/reinstatement cycle is an operational procedure for computing something like the grounded extension.
- [[Reiter_1980_DefaultReasoning]] -- **Strong.** Both provide formal frameworks for nonmonotonic reasoning. Reiter's defaults have prerequisite/justification/consequent; Pollock's reasons are prima facie or conclusive with rebutting or undercutting defeaters. Key difference: Pollock distinguishes rebutting defeat (attacking the conclusion) from undercutting defeat (attacking the reason-conclusion link), a distinction Reiter's defaults cannot express. Dung (1995) proves both are special cases of argumentation.
- [[deKleer_1986_AssumptionBasedTMS]] -- **Moderate.** Both manage belief sets under contradictions: the ATMS tracks multiple consistent environments, while OSCAR manages a single evolving belief set with defeat and reinstatement. The ATMS's nogood management corresponds to Pollock's defeat detection, and ATMS context switching corresponds to Pollock's reinstatement.
- [[Clark_2014_Micropublications]] -- **Moderate.** Clark's micropublication model is grounded in Toulmin-Verheij defeasible argumentation theory, which Pollock's work directly informs. Clark's support/challenge relations map to Pollock's prima facie reasons and defeaters. Clark's bipolar networks are practical instances of the kind of argumentation structure Pollock formalizes.
- [[Alchourron_1985_TheoryChange]] -- **Moderate.** Pollock's warrant theory and AGM's belief revision both address rational belief management under contradictions, but from different traditions. Pollock's approach is constructive (build arguments, compute warrant via defeat levels); AGM's is axiomatic (specify postulates for rational contraction/revision). Both agree on minimal change and consistency preservation.
- [[Falkenhainer_1987_BeliefMaintenanceSystem]] -- **Moderate.** Both address graded or defeasible support for beliefs. The BMS provides quantitative mechanisms (Dempster-Shafer intervals); Pollock provides qualitative ones (prima facie reasons with defeat levels). Pollock's undercutting defeaters are conceptually related to the BMS's evidence subtraction via inverted Dempster's rule.

---

**See also:** [[Prakken_2012_AppreciationJohnPollock'sWork]] - A 25-year retrospective survey by Prakken and Horty that contextualizes, extends, and critiques this 1987 paper's contributions, identifying limitations (unclear attack/defeat distinction, ad hoc argument strength) and connecting Pollock's ideas to modern structured argumentation (ASPIC+).
