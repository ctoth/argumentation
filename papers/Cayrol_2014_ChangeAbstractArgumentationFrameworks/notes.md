---
title: "Change in Abstract Argumentation Frameworks: Adding an Argument"
authors: "Claudette Cayrol, Florence Dupin de Saint-Cyr, Marie-Christine Lagasquie-Schiex"
year: 2010
venue: "Journal of Artificial Intelligence Research (JAIR)"
doi_url: "https://doi.org/10.1613/jair.2965"
---

# Change in Abstract Argumentation Frameworks: Adding an Argument

The local directory retains a 2014 label, but the actual paper is JAIR **38 (2010), 49-84**, published May 2010. *([title-page image](pngs/page-000.png))*

## One-Sentence Summary
Provides a formal taxonomy of how adding an argument (with interactions) to a Dung AF changes the extension set, defining seven structural properties and monotony/acceptance properties with necessary or sufficient conditions under grounded and preferred semantics.

## Problem Addressed
When new information arrives (a new argument interacting with existing ones), what happens to the extensions of an argumentation framework? Prior work lacked a systematic characterization of the different types of change that can occur and the conditions that govern them. *(p.1-2)*

## Key Contributions
- Formal definition of four types of change operations on AFs: adding interaction, removing interaction, adding argument, removing argument *(p.5)*
- Seven structural properties for change: decisive, restrictive, questioning, destructive, expansive, conservative, altering *(p.6-10)*
- Status-based properties: Monotony and its Credulous/Skeptical variants, Partial Monotony for an argument, and Priority to Recency. *(Definitions 15-17; [p.61](pngs/page-012.png), [p.62](pngs/page-013.png))*
- Complete characterization of connections between structural and status-based properties (Propositions 3-6) *(p.13)*
- Necessary and/or sufficient conditions for the properties under grounded and preferred semantics, rather than an iff characterization for every row (Tables 4-5). *([p.70](pngs/page-021.png), [p.71](pngs/page-022.png))*
- Two key lemmas enabling proofs: Lemma 1 (no new cycles from adding one argument in certain conditions) and Lemma 2/3 (admissibility preservation) *(p.26, 30)*

## Methodology
The paper works purely at the abstract level of Dung AFs. It considers the change operation of adding a new argument Z (not in A) along with its interactions Z_r to an existing AF (A,R). It compares the original extension set E with the new extension set E' under grounded, preferred, and stable semantics. *(p.1-2)*

## Key Definitions

### Definition 7: Change Operation *(p.5)*
Let (A,R) be an AF. A change operation can be:
1. Adding one interaction r_0 between existing arguments: (A,R) -> (A, R union {r_0})
2. Removing one existing interaction r_0: (A,R) -> (A, R \ {r_0})
3. Adding one argument Z (not in A) and interactions Z_r: (A,R) -> (A union {Z}, R union Z_r)
4. Removing one argument Z in A and all its interactions

Here Z_r is a non-empty set of pairs of arguments (of the form (X,Z) or (Z,X) with X in A).

### Definition 8: Decisive Change *(p.6)*
The change is decisive iff the old family E is empty, is {empty set}, or has **at least two** extensions, and the new family E' contains exactly one nonempty extension. Definition 8 explicitly uses n >= 2; Example 2.4 has two old extensions. The summary tables print >2, which conflicts with that definition and example and must not be silently copied as the definition. *([Definition 8, p.55](pngs/page-006.png), [Example 2.4, p.56](pngs/page-007.png))*

### Definition 9: Restrictive Change *(p.7)*
The change is restrictive if |E| > |E'| >= 2, with n > p >= 2.

### Definition 10: Questioning Change *(p.8)*
The new family E' has p >= 2 extensions, and either E is empty or E has n extensions with p > n >= 1. In particular, transition from no extensions to one nonempty extension is decisive, not questioning. *([Definition 10, p.57 image](pngs/page-008.png))*

### Definition 11: Destructive Change *(p.8)*
The change is destructive if E = {E_1,...,E_n}, n >= 1, E_i != {} and E' = empty set or E' = {{}}.

### Definition 12: Expansive Change *(p.9)*
|E| = |E'| and for every E'_j in E', there exists E_i in E s.t. E_i is a strict subset of E'_j.

### Definition 13: Conservative Change *(p.9)*
E = E'.

### Definition 14: Altering Change *(p.10)*
|E| = |E'| and there exists an old extension E_i such that **for every** new extension E'_j, E_i is not a subset of E'_j. The second quantifier is universal, not existential. *([Definition 14, p.59 image](pngs/page-010.png))*

### Definition 15: Monotony *(p.11)*
Monotony holds iff **every old extension is included in at least one new extension**: for every E_i in E, some E'_j in E' satisfies E_i subseteq E'_j.
- **Credulous Monotony**: union(E) subseteq union(E').
- **Skeptical Monotony**: intersection(E) subseteq intersection(E').

Monotony implies Credulous Monotony, but neither Monotony nor Skeptical Monotony implies the other in general. All three coincide under a semantics giving one extension. *([Definition 15 and discussion, p.61 image](pngs/page-012.png))*

### Definition 16: Partial Monotony for X *(p.12)*
For argument X, if X belongs to **some** old extension then X belongs to **at least one** new extension. *([Definition 16, p.61 image](pngs/page-012.png))*

### Definition 17: Priority to Recency *(p.13)*
The change satisfies Priority to Recency if G' has at least one extension and the added argument Z belongs to each extension of G'.

## Key Equations

$$
(\mathbf{A}, \mathbf{R}) \oplus_i^a (Z, Z_r) = (\mathbf{A} \cup \{Z\}, \mathbf{R} \cup Z_r)
$$
Where: A = set of arguments, R = attack relation, Z = new argument, Z_r = new interactions
*(p.5)*

$$
\mathcal{E}' = \mathcal{E} \cup \{Z\} \cup \bigcup_{i \geq 1} (\mathcal{F}')^{i}(\{Z\})
$$
Here mathcal E and mathcal E' denote the individual grounded extensions, not their singleton extension families. Proposition 11 assumes mathcal E != empty, Z does not attack mathcal E, and mathcal E defends Z; F' is the new framework's characteristic function (the superscript is iteration i, not "ri"). If Z attacks no argument of G, the result simplifies to mathcal E union {Z}. *([p.66 image](pngs/page-017.png))*

## Parameters

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| Original extension set | E | - | - | - | 6 | Set of extensions of G |
| New extension set | E' | - | - | - | 6 | Set of extensions of G' |
| New argument | Z | - | - | - | 5 | Argument not in A |
| New interactions | Z_r | - | - | - | 5 | Non-empty set of pairs involving Z |
| Characteristic function | F | - | - | - | 3 | Dung's characteristic function |

## Implementation Details

### Data structures needed
- Argumentation Framework: directed graph (A, R) *(p.3)*
- Extension set: set of sets of arguments *(p.3)*
- Change operation: tuple (Z, Z_r) where Z is new argument, Z_r is set of attack pairs *(p.5)*
- Attack graph G with nodes = arguments, edges = attacks *(p.3)*

### Key algorithmic insights
- Under grounded semantics, if the old grounded extension e is empty, the change is conservative iff Z is attacked by G; if Z is unattacked, it is decisive (Proposition 9 and Corollary 1). *([p.65 image](pngs/page-016.png))*
- If e is nonempty and Z does not attack e, the change is conservative when e does not defend Z, and expansive when e does defend Z (Proposition 11). Requiring Z not to attack any of G is stronger than necessary. *([p.66 image](pngs/page-017.png))*
- Under grounded semantics, change is never questioning nor restrictive (Prop.12) *(p.17)*
- Under preferred semantics, if E={empty set}, Z is **not attacked** by G, and G has no even-length cycle, the change is decisive (Proposition 16). If E={empty set} and Z attacks no old argument, the change is conservative (Proposition 17). These are separate results, not one condition. *([p.68 image](pngs/page-019.png))*
- Presence/absence of even-length cycles in the attack graph is critical for determining change type under preferred semantics *(p.19-21)*

### Necessary and sufficient conditions (Table 4, p.21)
For the change operation of adding argument Z:

**Grounded semantics:**
- In these bullets, e denotes the single old grounded extension, while E elsewhere denotes the family {e}.
- Decisive: CS and CN when e is empty and Z is not attacked (Prop.9).
- Restrictive: Never (Prop.12)
- Questioning: Never (Prop.12)
- Destructive: CN and CS when e is nonempty, Z attacks each unattacked argument in G, and Z is attacked in G' (Prop.13/Table 4).
- Expansive: CS when e is nonempty, Z does not attack e, and e defends Z (Prop.11).
- Conservative: CS when e is empty and Z is attacked by G (Prop.9); CS' when e is nonempty, Z does not attack e, and e does not defend Z (Prop.11).
- Altering: CN when e is nonempty and Z attacks e (Prop.10).

**Preferred semantics:**
- Decisive: CS when E = {{}} and Z not attacked and no even-length cycle in G (Prop.16); if E = {{}} CN: Z attacks G (Prop.17)
- Restrictive: CN when there exists even-length cycle in G and Z attacks at least one E_i (Prop.15)
- Questioning: CN when there exists an even-length cycle in **G** and Z attacks G (Prop.17, Prop.18). *([Table 4, p.70 image](pngs/page-021.png))*
- Destructive: CS when E != {{}} and Z is attacked and no even-length cycle in G' and Z attacks each unattacked arg in G (Prop.21)
- Expansive: CS when E != {{}} and Z does not attack G and for all i, E_i defends Z (Prop.18)
- Conservative: CS when E = {{}} and Z does not attack G (Prop.17); CS' when E != {{}} and Z does not attack G and for all i, E_i does not defend Z (Prop.18)
- Altering: CN when E != {{}} and there exists E_i s.t. Z attacks E_i (Prop.15)

### Status-based conditions (Table 5, p.22)
- **Monotony**: Grounded sufficient conditions: e is empty, or e is nonempty and Z does not attack e (Proposition 10). Preferred sufficient condition: Z attacks no old preferred extension (Proposition 19).
- **Priority to Recency**: Grounded sufficient conditions: Z is unattacked (Proposition 8), or e is nonempty, Z does not attack e, and e defends Z (Corollary 2). Preferred sufficient conditions: Z is unattacked (Proposition 14), or Z attacks no preferred extension and **each** old preferred extension defends Z (Corollary 3).
- **Partial Monotony for X**: Grounded sufficient condition: X in e and Z does not **indirectly** attack X (Proposition 7). In either semantics, Monotony implies Partial Monotony for each old argument.
- **Skeptical Monotony**: Under grounded semantics this is the same condition as Monotony, so it does **not** always hold. Under preferred semantics, a sufficient condition is that G has no controversial argument and Z does not attack the **intersection** of the old preferred extensions (Proposition 20).

These retain the CS (sufficient condition) qualification rather than promoting it to iff. *([Table 5, p.71](pngs/page-022.png), [Proposition 7](pngs/page-015.png), [Proposition 20](pngs/page-020.png))*

## Figures of Interest
- **Fig 1 (p.14):** Inclusion links between change types for adding argument - shows how conservative is contained in monotony, expansive implies both monotony and priority to recency, etc.
- **Table 2 (p.11):** Structural properties as function of extension set size changes
- **Table 3 (p.14):** Synthesis of connections between structural and status-based properties
- **Table 4 (p.21):** Necessary and sufficient conditions for structural properties under grounded/preferred
- **Table 5 (p.22):** Necessary and sufficient conditions for status-based properties under grounded/preferred

## Results Summary
The paper provides a complete taxonomy. Key results: under grounded semantics, adding an argument can never be restrictive or questioning (Prop.12). Under preferred semantics, the presence of even-length cycles is the key factor determining whether restrictive or questioning changes can occur. Conservative and expansive changes always satisfy Monotony (Prop.3). Destructive and altering changes never satisfy Monotony (Prop.4). Under stable, grounded, and preferred semantics, expansive change always satisfies Priority to Recency (Prop.6). *(p.13-14)*

## Limitations
- Only considers one type of change in detail: addition of a single argument with interactions *(p.25)*
- Does not handle simultaneous addition of multiple arguments *(p.25)*
- Does not address removal of arguments or interactions in equal depth *(p.25)*
- Connection to AGM belief revision postulates is noted but not formally developed *(p.22-23)*
- Appendix B shows some properties of other change operations but without full analysis *(p.32-33)*

## Arguments Against Prior Work
- Boella et al. (2009a, 2009b) study how extensions change when arguments/attacks are changed, but only consider the case when the semantics provides exactly one extension, and their notion of "conservative" only matches the authors' conservative property *(p.24)*
- Rotstein et al. (2008b) introduce dynamics by considering arguments built from evidence, but this works at a more abstract level and considers internal dynamics; the current paper remains at the abstract level and studies impact on the framework's outcome *(p.24)*
- The AGM framework for belief revision (Alchourron et al. 1985) cannot be directly applied because argumentation does not use standard belief revision formalism; the comparison with AGM is not appropriate because of two main reasons *(p.22-23)*

## Design Rationale
- Works at abstract Dung AF level rather than structured argumentation to maximize generality *(p.1)*
- Focuses on adding a single argument (rather than multiple) because this is the most fundamental and frequently encountered change operation *(p.2)*
- Separates structural properties (based on extension set cardinality/inclusion) from status-based properties (based on argument acceptance status) to provide complementary views *(p.5-6)*
- Studies grounded and preferred semantics specifically because grounded gives a unique extension (simpler analysis) while preferred allows multiple extensions (richer taxonomy) *(p.15)*

## Testable Properties
- Under grounded semantics, adding an argument is NEVER restrictive or questioning (Prop.12) *(p.17)*
- A conservative change always satisfies Monotony and Skeptical Monotony (Proposition 3). *([p.62 image](pngs/page-013.png))*
- A destructive change never satisfies Monotony (Proposition 4). *(p.62)*
- An expansive change always satisfies Monotony and Skeptical Monotony; under stable/grounded/preferred semantics, an expansive argument addition also satisfies Priority to Recency (Propositions 3 and 6). *(p.62)*
- A conservative argument addition never satisfies Priority to Recency (Proposition 5). *(p.62)*
- A destructive argument addition never satisfies Priority to Recency (Proposition 5). *(p.62)*
- If the old grounded extension e is nonempty, Z does not attack e, and e defends Z, the change is expansive (Proposition 11). *([p.66 image](pngs/page-017.png))*
- The grounded destructive condition additionally requires the old grounded extension to be nonempty: Z attacks every old unattacked argument and is itself attacked in G'. The nonempty-old-extension requirement prevents calling an unchanged empty grounded extension destructive. *([Proposition 13](pngs/page-017.png), [Table 4](pngs/page-021.png))*
- Under preferred semantics, if E != {{}} and Z is attacked and no even-length cycle in G' and Z attacks each unattacked arg in G, the change is destructive (Prop.21) *(p.21)*
- If the old grounded extension is empty and Z is unattacked by G, the change is decisive (Proposition 9). The paper's addition operation requires a nonempty set of interactions; an isolated added argument is outside that operation. *([p.65 image](pngs/page-016.png))*

## Relevance to Project
Directly relevant to propstore's argumentation layer. When new claims/arguments are added to the system, this paper provides the formal basis for predicting how extensions will change. The structural and status-based property taxonomy can be used to:
1. Classify the impact of adding new evidence/arguments to an existing AF
2. Determine whether previously accepted arguments remain accepted (Monotony)
3. Determine whether new arguments will be accepted (Priority to Recency)
4. Predict whether the change will be conservative (no change to extensions) or destructive

The necessary/sufficient conditions in Tables 4-5 are directly implementable as checks before/after adding arguments to an AF.

## Open Questions
- [ ] How to extend to simultaneous addition of multiple arguments?
- [ ] Connection to AGM belief revision postulates — can the structural properties be mapped to AGM postulates?
- [ ] How do these properties interact with bipolar argumentation (Cayrol 2005)?
- [ ] Impact on ASPIC+ structured argumentation when adding arguments?

## Related Work Worth Reading
- Boella, G., Kaci, S., & van der Torre, L. (2009a,b). Dynamics in argumentation with single extensions / with the grounded extension. (Related: dynamics under single extension)
- Rotstein, N. D., Moguillansky, M. O., Garcia, A. J., & Simari, G. R. (2008a,b). Argument theory change / abstract argumentation framework for handling dynamics.
- Alchourron, C. E., Gardenfors, P., & Makinson, D. (1985). On the logic of theory change. (AGM postulates — foundational for belief revision)
- Cayrol, C., Dupin de Saint-Cyr, F., & Lagasquie-Schiex, M. (2008). Revision of an argumentation system. (Earlier version of this work, restricted to one interaction)
- Baumann, R. (2012). What does it take to enforce an argument? Minimal change in abstract argumentation. (Enforcement approach to AF change)

---

**See also:** [[Doutre_2018_ConstraintsChangesSurveyAbstract]] - Comprehensive survey that subsumes and extends this paper's change operations within a broader typology of constraints (structural, semantic, acceptability), changes, and quality criteria for argumentation dynamics.

## Collection Cross-References

### Already in Collection
- [Prudent Semantics for Argumentation Frameworks](../Coste-Marquis_2005_PrudentSemantics/notes.md) - cited in the bibliography; defines prudent extensions by forbidding odd-path indirect conflicts inside accepted sets, a semantics-level change that complements this paper's structural analysis of how AF extensions change when an argument is added.
