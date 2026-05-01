---
title: "Problem Solving with the ATMS"
authors: "Johan de Kleer"
year: 1986
venue: "Artificial Intelligence"
doi_url: "https://doi.org/10.1016/0004-3702(86)90082-2"
---

# Problem Solving with the ATMS

## One-Sentence Summary
Presents a complete control regime and constraint language for building problem solvers on top of the Assumption-based Truth Maintenance System (ATMS), including consumer architecture, scheduling, dependency-directed backtracking, and comparison with Doyle's TMS, McAllester's RUP, McDermott's system, and MBR. *(p.197)*

## Problem Addressed
The ATMS provides soundness, completeness, and consistency guarantees for default reasoning, but these can be inadvertently lost if the problem solver does not interface correctly. This paper addresses how to build problem solvers that preserve those guarantees through a disciplined control regime. *(p.197)*

## Key Contributions
- Defines a **consumer architecture** for encoding problem-solving steps as modular units (consumers) attached to ATMS nodes *(p.201--202)*
- Introduces **class consumers**, **conjunctive class consumers**, and **constraint consumers** for efficient rule encoding *(p.207--208)*
- Presents scheduling strategies: simplest-label-first, before/after consumer ordering, dependency-directed backtracking via control disjunctions *(p.204--206)*
- Defines a **simple constraint language** (PLUS, TIMES, AND, OR, ONEOF, etc.) built entirely on ATMS primitives *(p.209--213)*
- Provides detailed comparison with Doyle's TMS, McAllester's RUP, McDermott's system, Martins' MBR, and Williams' ART *(p.215--222)*

## Methodology
The paper builds a layered architecture: *(p.197--198)*
1. **ATMS base**: nodes with labels (sets of environments), justifications, nogoods *(p.198)*
2. **Consumer layer**: rules that fire when antecedent nodes have nonempty labels; consumers run once per node, producing new justifications *(p.201--202)*
3. **Control layer**: scheduling (simplest environments first), dependency-directed backtracking (control disjunctions), delayed justifications, kernel environments *(p.204--206)*
4. **Constraint language**: translates arithmetic/logical constraints into sets of consumers and justifications *(p.209--213)*

## Key Equations

Justification form: *(p.198)*

$$
\alpha_1, \alpha_2, \ldots \Rightarrow \beta
$$

Where $\alpha_i$ are problem-solver data, assumptions, or falsity $\perp$. Interpreted as material implication: *(p.198)*

$$
\alpha_1 \wedge \alpha_2 \wedge \cdots \rightarrow \beta
$$

Node representation: *(p.198)*

$$
\langle \text{datum}, \text{label}, \text{justifications} \rangle
$$

Environment lattice: for $n$ assumptions, $2^n$ environments, at most $2^n$ contexts. *(p.198)*

Label for $x = 1$: *(p.198)*

$$
\langle x = 1, \{\{A, C\}, \{D, E\}\}, \{\ldots\} \rangle
$$

Constraint consumer inverse: *(p.207--208)*

$$
x_i = R_i^{-1}(x_1, \ldots, x_{i-1}, x_{i+1}, \ldots)
$$

PLUS constraint inverse: *(p.210)*

$$
v_i = -\sum_{j \neq i} v_j
$$

TIMES constraint inverse (when $v \neq 0$): *(p.212)*

$$
v_i = \frac{\prod_{j \neq i} v_j}{v}
$$

Parity encoding with delayed justifications: *(p.216)*

$$
p_{i-1} = 0, b_i = 1 \implies p_i = 1
$$

$$
p_{i-1} = 1, b_i = 0 \implies p_i = 1
$$

$$
p_{i-1} = 0, b_i = 0 \implies p_i = 0
$$

$$
p_{i-1} = 1, b_i = 1 \implies p_i = 0
$$

## Parameters

| Name | Symbol | Units | Default | Range | Notes | Page |
|------|--------|-------|---------|-------|-------|------|
| Number of assumptions | $n$ | - | - | 1-$\infty$ | Determines environment lattice size $2^n$ | p.198 |
| Number of environments per label | - | - | - | 1-$2^n$ | Label is set of greatest lower bounds | p.198 |
| Consumer execution count | - | - | 1 | 1 | Consumers execute exactly once per node | p.202 |

## Implementation Details

### Data Structures
- **Node**: (datum, label, justifications) triple *(p.198)*
- **Environment lattice**: $2^n$ vertices for $n$ assumptions; nogoods are crossed-out vertices *(p.198--199)*
- **Consumer queue**: nodes with pending consumers and nonempty labels; no separate agenda needed *(p.203)*
- **Control disjunctions**: `control{C1, C2, ...}` — scheduler maintains current environment satisfying all control disjunctions *(p.205)*

### Consumer Restrictions
Consumers must obey four restrictions *(p.202)*:
1. Only examine data of nodes (not labels or justifications)
2. Only examine antecedent nodes (those the consumer is attached to)
3. Antecedents of every justification must be exactly the consumer's antecedents, no more and no less (may include additional assumptions; see Section 5.2)
4. No internal state or control decisions

### Consumer Types
1. **Basic consumer** $F$: attached to single node, runs once per node when label becomes nonempty *(p.202)*
2. **Conjunctive consumer**: attached to list of nodes, runs when conjunction of antecedent labels yields consistent environment; invoked on cross-product of antecedent-class node sets (tuple-based) *(p.202)*
3. **Class consumer**: attached to a class (generalized variable), runs once per node-class instance *(p.207)*
4. **Conjunctive class consumer**: conjunctive consumer over multiple classes, invoked per cross-product tuple of member nodes *(p.207)*
5. **Constraint consumer**: triggers constraint $R(x_1, x_2, \ldots)$ when all but one antecedent hold; suppresses spurious retriggering via type system *(p.207--208)*
6. **Conditional constraint consumer**: like constraint consumer but conditional on a node being in a particular operating region (e.g., transistor ON/OFF/saturated/reverse-active) *(p.208)*
7. **Implication consumer** (exclusive/inclusive): encodes $a \rightarrow b \oplus c$ using `choose{B', C'}` disjunction; builds environment consumers that delay until efficient *(p.208--209)*
8. **Environment consumer**: runs when a new environment is added to a node's label; used internally by implication consumers *(p.209)*

### Consumer Type System
All typed consumers record their type in the informants of justifications they produce. A consumer will not execute until it receives a valid justification with another type, preventing retriggering on own outputs. *(p.202--203)*

### Unouting Problem
The consumer architecture automatically solves the unouting problem (what to do when multiple justifications contribute subset or disjoint environments to the same node's label). If antecedents do not yield a consistent environment, the consumer simply does not run; when a distant antecedent later becomes justified, the ATMS propagates label updates and the consumer fires automatically. *(p.203--204)*

### Scheduling Algorithm
1. Pick node with smallest environment (fewest assumptions) from consumer queue *(p.204)*
2. Execute consumer, discard it *(p.204)*
3. Repeat until no pending consumers with nonempty labels *(p.204)*
- Before/after ordering: "before" consumers (cheap checks like contradiction detection) run first; "after" consumers (expensive computation) run last *(p.205)*
- The scheduler schedules environments, not consumers; a consumer will not execute until all consumers of its subset environments have been executed *(p.204)*

### Dependency-Directed Backtracking
- Control disjunctions `control{C1, C2, ...}` partition the search space *(p.205)*
- The scheduler maintains a single current environment guaranteed consistent with all control disjunctions *(p.205)*
- `control{A, B}` also expresses search preference: solutions containing A are found before solutions containing B *(p.205)*
- When a contradiction is encountered, the scheduler finds the next consistent current environment; this achieves at least the efficiency of chronological backtracking but avoids contradictions from the current justification set (better than conventional DDB which only avoids past contradictions) *(p.205)*

### Delayed Justifications
A delayed justification (indicated with $\Longrightarrow$ instead of $\Rightarrow$) takes effect only when its antecedents hold in a consistent environment specified by the control strategy. Implemented by creating a temporary node with the delayed justification and attaching a basic consumer that installs a conventional justification to the actual consequent. *(p.205--206)*

### Kernel Environment
The problem solver can specify a kernel environment; a consumer is not run unless its antecedents hold in some consistent environment which is not inconsistent with the kernel. This allows specifying conditions that any solution must satisfy. If the kernel becomes inconsistent, problem solving halts. This is the control method the author uses most commonly. *(p.206)*

### Incremental Interpretation Construction
The scheduler can maintain a single current interpretation, updated after every problem-solver action. This is the third control method, combining ideas from kernel environments and interpretation tracking. *(p.206)*

### Problem Solver Responsibility
The advantage of all control schemes over ad-hoc tactics is that no solution will be missed if the control is later removed. Although control mechanisms purposely violate exhaustivity, the potential of exhaustivity is not surrendered. The problem solver can specify how focus should change when it becomes contradictory or inadequate. *(p.206)*

### Constraint Language Primitives
- `EQ(l, v1, v2)`: $v_1 = v_2$ iff $l = \text{TRUE}$ *(p.209)*
- `NOT(l1, l2)`: $l_1 = \text{TRUE}$ iff $l_2 = \text{FALSE}$ and vice versa *(p.209)*
- `MINUS(v1, v2)`: $v_1 = -v_2$ *(p.209)*
- `PLUS(v1, v2, ...)`: $\sum v_i = 0$ *(p.210)*
- `TIMES(v, v1, v2, ...)`: $v = \prod v_i$ *(p.210)*
- `DIVIDE(v, v1, v2)`: if $v_2 \neq 0$ then $v_1 = v \times v_2$ *(p.210)*
- `E(v1, v2)`: $v_1 = (v_2 + 1000)!$ — generic expensive computation used in examples *(p.210)*
- `AND(l, l1, l2, ...)`: $l = \text{TRUE}$ iff all $l_i = \text{TRUE}$ *(p.210)*
- `OR(l, l1, l2, ...)`: $l = \text{TRUE}$ iff at least one $l_i = \text{TRUE}$ *(p.210)*
- `ONEOF(l, l1, l2, ...)`: $l = \text{TRUE}$ iff exactly one $l_i = \text{TRUE}$ *(p.210)*
- `ELEMENT(l, v, v1, v2, ...)`: equivalent to ONEOF + EQ combinations *(p.210)*

### AND Implementation Detail
AND is encoded by expanding $a \equiv b \wedge c$ into clauses: $a \rightarrow b$, $a \rightarrow c$, $b \wedge c \rightarrow a$, plus contrapositives using implication consumers with `choose` disjunctions. Four observations optimize this: (1) don't create $a \Rightarrow b$ unless $a$ is true somewhere, (2) don't create $\gamma_{\neg b} \Rightarrow \gamma_{\neg a}$ unless $a$ or $b$ are false somewhere, (3) don't create $a, b \Rightarrow c$ unless both are true, (4) assumptions $\Gamma'_{\neg b}$ and $\Gamma'_{\neg c}$ need not be created unless $a$ is false somewhere. *(p.210--211)*

### TIMES Zero Handling
When any $v_i = 0$, $v$ is assigned zero. When $v = 0$, a `oneof` disjunction assumption set is created: each $v_i$ is assigned 0 under the justification of the node $v = 0$ and one of the assumptions. The disjunction must consist of assumptions (not assumed data) — the strongest result of $v = 0$ is that one of the $v_i = 0$. Hyperresolution rule H5 is needed to detect inconsistency. *(p.212)*

### ONEOF Implementation
ONEOF is quite complex. One class consumer computes $l$ from the set $\{l_i\}$: if all but one $l_i$ is FALSE, then $l$ = TRUE iff the remaining $l_i$ is TRUE. Another class consumer acts when $l$ = TRUE: it creates a `oneof` disjunction and assigns each $l_i$ = TRUE under the conjunction of $l$ = TRUE and an assumption. *(p.213)*

### Assertional Language Integration
The ATMS integrates with assertional languages like AMORD. Every assertion is an ATMS node, every antecedent pattern is an ATMS class. For the rule human(x)/mortal(x): define class human(x), attach consumer mortal(x); when human(Turing) is asserted, it triggers the consumer producing mortal(Turing). The ATMS has no model of data structure — the problem solver identifies instances. *(p.213--214)*

### Consequent Reasoning
Although examples focus on antecedent reasoning, the ATMS applies to consequent reasoning as well. Consequent reasoners tend to require far more control since they specifically avoid finding all solutions. For consequent reasoning, interpretation construction is usually inappropriate and resolution should be used. *(p.214)*

### Exclusivity of Variable Values
The class-node architecture applies even when values are not exclusive. Example: a five-value system $x < 0$, $x \leq 0$, $x = 0$, $x \geq 0$, $x > 0$. If $x < 0$ holds in a more general environment than $x \leq 0$, a special process removes the more general environment from $x \leq 0$'s label. *(p.214)*

### Key Design Decisions
- Consumers run exactly once, then are discarded (like compilation) *(p.202)*
- Consumer may not have internal state or make control decisions *(p.202)*
- All inferences recorded as ATMS justifications *(p.202)*
- ATMS is neutral to search order (depth-first, breadth-first, or mixed) *(p.204)*
- Control exercised only *before* running a consumer; once run, justifications are permanent *(p.204)*
- The ATMS never modifies or adds a justification to avoid a contradiction *(p.219)*

## Figures of Interest
- **Fig 1 (p.199):** Environment lattice for 5 assumptions {A,B,C,D,E} — shows all $2^5 = 32$ environments with nogoods crossed out and maximal consistent vertices boxed

## Results Summary
- The consumer architecture provides a clean separation between problem-solving logic and ATMS maintenance *(p.201--204)*
- Scheduling by simplest-label-first finds solutions with near-minimum effort *(p.204)*
- Dependency-directed backtracking via control disjunctions achieves at least the efficiency of chronological backtracking *(p.205)*
- For problems with many solutions where all are needed: ATMS has inherent advantage (avoids all dependency-directed backtracking and context switching) *(p.215)*
- For problems with one solution: advantage depends on whether dependency-directed backtracking cost exceeds ATMS overhead *(p.215)*
- For problems with many solutions but few needed: requires careful use of control disjunctions to avoid exponential label growth *(p.215)*

## Comparison to Other Systems

### Doyle's TMS *(p.216--217)*
- Doyle's TMS has two procedures: truth maintenance (constraint satisfaction) and dependency-directed backtracking (removes inconsistency by altering justifications) *(p.216)*
- CP-justification (conditional-proof) is a mechanism for recording results determined in another database state; the ATMS considers all justifications as CP and translates them into SL-justifications in terms of assumptions, making the CP-justification unnecessary *(p.217)*
- Both systems record contradictions the same way, but Doyle's additional justifications for search bookkeeping are unnecessary in the ATMS *(p.217)*

### McAllester's RUP *(p.217--218)*
- McAllester's system represents assumptions explicitly; easier to switch states, justifications not dominant, machinery streamlined *(p.218)*
- RUP's notion of "noticer" corresponds roughly to ATMS consumer, with one difference: a noticer runs even if its antecedent becomes invalid (RUP users adopted requeuing convention) *(p.218)*
- RUP's "intern-noticers" correspond to ATMS class consumers *(p.218)*
- Disadvantage of RUP: noticers can do too much, and the designer may inadvertently give up exhaustivity *(p.218)*

### McDermott's System *(p.218--220)*
- Similar in spirit: both augment justifications with propositional expression in disjunctive normal form *(p.218)*
- Equivalences: 'assertions' = 'data', 'premisses' = 'assumptions', 'data pool' = 'context' *(p.218)*
- Key difference: McDermott uses negated assumptions in labels (requires general constraint-satisfaction for label update); ATMS uses nogood database instead (simple local propagator, set operations via bit-vectors) *(p.219)*
- McDermott's insistence on single consistent data pool causes unnecessary complexity, inefficiency, and inadequate functionality *(p.219)*
- The ATMS handles contradictions by simply recording nogoods, never modifying justifications; this gives completeness and consistency guarantees *(p.220)*
- Data pool control can be approximately mimicked in the consumer architecture via current interpretation *(p.220)*

### Martins' MBR *(p.220--221)*
- MBR origin set = ATMS label, restriction set = ATMS nogoods *(p.220)*
- MBR uses restriction sets as alternative nogood implementation (check union operations, not all nogoods) — turned out inefficient for the ATMS *(p.220)*
- MBR's second derivation requires insertion of a supporting node with single origin set — cumbersome for disjunctive antecedents *(p.221)*
- MBR contradiction handling and interpretation construction mechanisms are inadequate *(p.221)*
- MBR insists on single current consistent context with no mechanism for changing or choosing another *(p.221)*
- MBR's relevance logic for control is provocative; incorporating ATMS efficiency and functionality into MBR would be interesting *(p.221)*

### Williams' ART *(p.221)*
- ART 'extent' = 'label', 'constraint' = justification whose consequent is $\gamma_\perp$, 'poison' = 'contradiction', 'believe' = contradict all competing extensions *(p.221)*
- ART allows negated assumptions (like McDermott), requiring dependency-directed backtracking *(p.221)*
- Does not allow disjunctions of extents; multiple justifications for same datum cause problems *(p.221)*
- ART is proprietary software with no detailed papers on internal architecture *(p.221)*

### Counterfactuals (Ginsberg) *(p.222)*
- Ginsberg's framework using David Lewis's possible-world semantics is very related to the ATMS *(p.222)*
- The ATMS extensions (maximally consistent sets of true defaults) correspond to Ginsberg's most similar worlds *(p.222)*
- Counterfactual "if p then q" corresponds to default $\neg p$ and $\neg p \rightarrow \neg q$; the ATMS or default logic represents this by maximally consistent sets of true defaults corresponding to minimal sets of false defaults *(p.222)*

## Arguments Against Prior Work

### Against Doyle's TMS *(p.216--217)*
- Doyle's TMS conflates two distinct procedures — truth maintenance (constraint satisfaction) and dependency-directed backtracking (removing inconsistency by altering justifications) — whereas the ATMS handles both uniformly through label propagation and nogood recording *(p.216)*
- The CP-justification mechanism is unnecessary: the ATMS considers all justifications as conditional-proof and translates them into SL-justifications in terms of assumptions, making a separate CP mechanism redundant *(p.217)*
- Doyle's additional justifications for search bookkeeping (recording where backtracking has been) are unnecessary in the ATMS, which implicitly computes all contexts *(p.217)*
- The inherent complexity of Doyle's scheme results primarily from ensuring exhaustivity of its search; the ATMS avoids this entirely because it considers all contexts simultaneously *(p.217)*

### Against McAllester's RUP *(p.217--218)*
- Although McAllester's system represents assumptions explicitly and is easier to switch states, it is not very useful because it cannot conveniently tell whether two antecedents to an inference are inconsistent *(p.218)*
- RUP's "noticer" runs even if its antecedent becomes invalid; RUP users adopted a requeuing convention to work around this, but the ATMS consumer architecture handles it automatically *(p.218)*
- The fundamental disadvantage of RUP is that noticers are permitted to do too much, and the problem-solver designer may inadvertently give up exhaustivity *(p.218)*

### Against McDermott's System *(p.218--220)*
- McDermott clung to the idea of a single current consistent data pool, which resulted in unnecessary complexity, inefficiency, and inadequate functionality *(p.218)*
- McDermott uses negated assumptions in labels, requiring a general constraint-satisfaction algorithm for label update; the ATMS uses a nogood database instead, enabling simple local propagation via set operations on bit-vectors *(p.219)*
- McDermott's stipulation outlawing odd loops is not necessary because the ATMS automatically treats them as contradictions *(p.219)*
- McDermott's erasure mechanism (erasing an assertion by conjoining its supporting justification with the negation of the characteristic premiss) is inelegant because it involves artificially modifying a problem-solver-supplied justification *(p.219)*
- The ATMS *never* modifies or adds a justification to avoid a contradiction; it simply records nogoods — this gives completeness and consistency guarantees that McDermott's system cannot provide *(p.219--220)*
- Without having specified a mechanism for handling contradictions, it is impossible to determine whether McDermott's scheme is exhaustive *(p.219)*
- McDermott's data pool control is purely a control mechanism (domain-dependent), and using it to handle contradictions almost inevitably results in inexhaustivity *(p.219--220)*

### Against Martins' MBR *(p.220--221)*
- MBR's use of restriction sets as an alternative nogood implementation turned out to be inefficient for the ATMS *(p.220)*
- MBR's handling of a second derivation requires insertion of a supporting node with a single origin set — a cumbersome data structure for representing disjunctive antecedents; one must presume all consequences of a multiply-derived datum are recorded this way, with no other way to represent disjunctive origin sets *(p.221)*
- MBR's contradiction handling mechanisms are inadequate — there is nothing corresponding to interpretation construction, so there is no way to actually identify extensions *(p.221)*
- MBR insists on a single current consistent context and provides neither a mechanism for changing the current context nor a method for choosing another one; the human user must query the overall problem solver *(p.221)*

### Against Williams' ART *(p.221)*
- ART allows negated assumptions (like McDermott), which necessarily requires dependency-directed backtracking *(p.221)*
- ART does not allow disjunctions of extents; if a second justification is found for a datum in a different environment, a new node must be created, causing problems with multiple justifications for the same datum *(p.221)*
- ART is proprietary software with no detailed papers on its internal architecture, making evaluation impossible *(p.221)*

## Design Rationale

### Why consumers run exactly once *(p.201--202)*
Running a consumer is like a compilation process: the consumer is compiled into a set of justifications. Because consumers only examine data (not labels or justifications), and data never changes, rerunning a consumer cannot produce new results. This design eliminates the need to track which consumers have run in which contexts. *(p.202)*

### Why consumers must not have internal state *(p.202)*
The same consumer can be attached to multiple nodes. If it had internal state, it could make decisions based on previous executions, which would make it order-sensitive and destroy the ATMS's ability to treat all contexts simultaneously. *(p.202)*

### Why consumer restrictions preserve ATMS guarantees *(p.200--202)*
The four consumer restrictions (examine only data, only antecedent nodes, include all and only antecedent nodes in justifications, no internal state) exist because incorrect justifications are far more damaging in the ATMS than in conventional reasoning. Too few antecedents make labels too general (nodes appear in wrong contexts); too many antecedents make labels too specific (solutions are missed). In conventional reasoning, extra antecedents do not affect correctness. *(p.200--201)*

### Why the ATMS uses a nogood database instead of negated assumptions *(p.219)*
The ATMS represents contradictions via a nogood database rather than allowing negated assumptions in labels. This is a deliberate design choice: with negated assumptions, label update requires a general constraint-satisfaction algorithm; with nogoods, labels are computed by a simple local propagator using set operations implementable as bit-vectors. All propositional operations can be expressed as set operations, and odd-loop detection is automatic. *(p.219)*

### Why the ATMS never modifies justifications *(p.219--220)*
Unlike Doyle's TMS and McDermott's system, the ATMS never modifies or adds a justification to resolve a contradiction. A contradiction simply ensures that the ATMS will never construct any environment containing it. This design makes it possible to talk about completeness and consistency with respect to the overall problem-solving effort, and enables handling positive clauses (choose's) cleanly. *(p.219--220)*

### Why scheduling is by simplest-label-first *(p.204)*
The most general environment of a node's label and the most general version of a contradiction should be found as early as possible. Finding the most general contradiction first avoids useless problem-solving steps within ultimately inconsistent environments. Finding the simplest label first means the problem solver works on nodes with fewer assumptions first. A consumer that adds an assumption to an environment constructs a justification that is scheduled after all consumers of all subset environments. *(p.204)*

### Why control is exercised before running consumers, not after *(p.204--206)*
Once a consumer has run and constructed its justifications, all control over those justifications is lost — they are permanent. Control can only be exercised by choosing which consumers to run and in what order. This design means no solution will be missed if the control is later removed — the potential of exhaustivity is not surrendered even though control mechanisms purposely violate exhaustivity. *(p.206)*

### Why parallelism is natural for the ATMS *(p.222)*
Consumers are both order-insensitive and status-insensitive: they can execute in any order, and they do not depend on whether antecedent nodes are currently "in" or "out." There is no global retraction, so no coordination between parallel processors is needed. If too few consumers are ready, processors can speculatively execute consumers on nodes with empty labels in hope they will eventually hold in some environment. *(p.222)*

## Limitations
- ATMS is slower than conventional TMS for problems needing only one solution (due to database access overhead) *(p.215)*
- Label sizes can grow exponentially ($2^{i+2} + 2^i$ environments for $i$-bit parity problem without control) *(p.216)*
- No built-in support for time/action modeling (ATMS is purely inferential; problem solvers that change the world cannot be modeled, as there is no way to prevent inheritance of a fact into a daughter context) *(p.223)*
- Weak notion of control compared to Doyle's TMS data pool mechanism *(p.220)*
- ONEOF implementation is quite complex *(p.213)*
- Symbolic algebra for infinite-valued variables not fully addressed (only covers finite domains cleanly); ONEOF/EQ/ONEOF(FALSE,...) undefined for infinite domains *(p.213)*
- For problems with many solutions but few needed, control mechanisms are inadequate; more research is needed *(p.222--223)*

## Testable Properties
- Environment lattice has exactly $2^n$ vertices for $n$ assumptions *(p.198)*
- A datum's label must be a subset of any of its environments *(p.198)*
- If a context is inconsistent (nogood), no datum should be derivable in that context alone *(p.198)*
- Consumers execute exactly once per node — rerunning produces no new justifications *(p.202)*
- Constraint consumer $R_i^{-1}$ must satisfy: if $R(x_1, \ldots, x_n)$ holds and all $x_j$ ($j \neq i$) are known, then $x_i = R_i^{-1}(x_1, \ldots, x_{i-1}, x_{i+1}, \ldots, x_n)$ *(p.207--208)*
- Control disjunctions partition the search space: the next consistent current environment found is guaranteed consistent with all control disjunctions *(p.205)*
- Parity problem with control: first solution found after creating $4i$ environments (linear), vs $2^{i+2} + 2^i$ without control (exponential) *(p.216)*
- Adding arbitrary antecedents to a justification forces the ATMS to consider more contexts than intended (over-general labels if too few; inconsistent results if wrong antecedents) *(p.200--201)*
- Typed consumers: a consumer with type T will not fire on justifications whose informant type is also T (prevents self-triggering) *(p.202--203)*
- Consumer architecture automatically solves the unouting problem: if antecedents do not yield a consistent environment, the consumer does not run *(p.203--204)*
- `control{A, B}` guarantees solutions with A are found before solutions with B *(p.205)*
- ATMS parallelism: consumers are order-insensitive and status-insensitive, so they can execute on parallel processors without coordination *(p.222)*

## Relevance to Project
This paper is foundational for the propstore project's world model and assumption-based reasoning. The ATMS architecture directly maps to: environments as assumption sets, labels as minimal environments supporting a datum, nogoods as contradictory assumption sets, and consumers as forward-chaining rules. The constraint language (Section 5.3) provides a template for implementing numeric and logical constraints over ATMS-tracked variables. The control regime (Section 4) is directly applicable to the hypothetical world exploration in propstore. *(p.197--224)*

## Open Questions
- [ ] How does the consumer architecture scale to very large numbers of assumptions (hundreds/thousands)?
- [ ] Can the constraint language be extended to support continuous/real-valued domains without symbolic algebra? *(p.213)*
- [ ] What is the practical overhead of the ATMS label-update algorithm compared to incremental constraint propagation?
- [ ] How to model temporal actions within the purely inferential ATMS framework (Section 7.3)? *(p.223)*

## Related Work Worth Reading
- de Kleer, J., "An assumption-based TMS", Artificial Intelligence 28 (1986) 127-162 [companion paper, defines the ATMS itself] *(ref [4], p.223)*
- de Kleer, J., "Extending the ATMS", Artificial Intelligence 28 (1986) 163-196 [extends ATMS with defaults, disjunctions, nonmonotonic justifications] *(ref [5], p.223)*
- Doyle, J., "A truth maintenance system", Artificial Intelligence 12 (1979) 231-272 [original TMS] *(ref [9], p.223)*
- McAllester, D., "A three-valued truth maintenance system" (1978) and "An outlook on truth maintenance" (1980) [RUP system] *(refs [14, 15], p.223--224)*
- McDermott, D., "Contexts and data dependencies: a synthesis", IEEE Trans. PAMI 5(3) (1983) 237-246 *(ref [18], p.224)*
- Martins, J.P. and Shapiro, S.C., "Reasoning in multiple belief spaces" (1983) [MBR] *(refs [12, 13], p.223)*
- Williams, C., "ART the advanced reasoning tool" (1984) [proprietary] *(ref [21], p.224)*
- de Kleer, J. and Brown, J.S., "A qualitative physics based on confluences", Artificial Intelligence 24 (1984) 7-83 *(ref [6], p.223)*
- Reiter, R., "A logic for default reasoning", Artificial Intelligence 13 (1980) 81-132 *(ref [19], p.224)*
- Ginsberg, M.L., "Counterfactuals", Proc. IJCAI (1985) 107-110 *(ref [11], p.223)*

## Collection Cross-References

### Already in Collection
- [[deKleer_1986_AssumptionBasedTMS]] — the foundational companion paper defining the ATMS itself (environments, labels, nogoods, contexts, label properties); this problem-solving paper builds the control regime and constraint language on top of that substrate

### Now in Collection (previously listed as leads)
- [[Doyle_1979_TruthMaintenanceSystem]] — The original justification-based TMS. Introduces SL/CP justifications, truth maintenance process, dependency-directed backtracking, and control patterns (defaults, sequences, equivalence classes) that this paper's consumer architecture and constraint language supersede. This paper compares the ATMS consumer approach favorably against Doyle's data pool mechanism for control.
- [[Reiter_1980_DefaultReasoning]] — Referenced as Reiter (1980); provides the formal framework for default reasoning that the ATMS supports computationally. Reiter's extensions (fixed-point belief sets under defaults) correspond to ATMS environments.

### New Leads (Not Yet in Collection)
- de Kleer (1986) — "Extending the ATMS" — extends the basic ATMS with default reasoning, disjunction axioms, nonmonotonic justifications

### Supersedes or Recontextualizes
- (none)

### Cited By (in Collection)
- [[Dixon_1993_ATMSandAGM]] — the ATMS functional specification from this and the companion paper is what Dixon proves equivalent to AGM operations

### Conceptual Links (not citation-based)
- [[deKleer_1986_AssumptionBasedTMS]] — direct companion; this paper defines the problem-solving architecture, that paper defines the ATMS substrate it runs on
- [[deKleer_1984_QualitativePhysicsConfluences]] — **Strong.** The constraint language (PLUS, TIMES, AND, OR, ONEOF) directly generalizes the qualitative constraint satisfaction demonstrated in the qualitative physics paper. The consumer architecture mirrors ENVISION's component models.
