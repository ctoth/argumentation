---
title: "Change in Abstract Argumentation Frameworks: Adding an Argument"
authors: "Claudette Cayrol, Florence Dupin de Saint-Cyr, Marie-Christine Lagasquie-Schiex"
year: 2014
venue: "Journal of Artificial Intelligence Research (JAIR)"
doi_url: "https://doi.org/10.1613/jair.2965"
---

# Change in Abstract Argumentation Frameworks: Adding an Argument

## One-Sentence Summary
Provides a formal taxonomy of how adding an argument (with interactions) to a Dung AF changes the extension set, defining seven structural properties and three status-based properties with necessary/sufficient conditions under grounded and preferred semantics.

## Problem Addressed
When new information arrives (a new argument interacting with existing ones), what happens to the extensions of an argumentation framework? Prior work lacked a systematic characterization of the different types of change that can occur and the conditions that govern them. *(p.1-2)*

## Key Contributions
- Formal definition of four types of change operations on AFs: adding interaction, removing interaction, adding argument, removing argument *(p.5)*
- Seven structural properties for change: decisive, restrictive, questioning, destructive, expansive, conservative, altering *(p.6-10)*
- Three status-based properties: Monotony, Priority to Recency, Partial Monotony, Skeptical Monotony *(p.11-12)*
- Complete characterization of connections between structural and status-based properties (Propositions 3-6) *(p.13)*
- Necessary and sufficient conditions for each property under grounded and preferred semantics (Tables 4-5) *(p.21-22)*
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
The change from G to G' is decisive if E = empty set, or E = {{}} or |E| > 2, and |E'| = 1 and E' != {{}}.

### Definition 9: Restrictive Change *(p.7)*
The change is restrictive if |E| > |E'| >= 2, with n > p >= 2.

### Definition 10: Questioning Change *(p.8)*
The change is questioning if |E'| > |E|, with p > 2, or E = {E_1,...,E_p} and p > n >= 1.

### Definition 11: Destructive Change *(p.8)*
The change is destructive if E = {E_1,...,E_n}, n >= 1, E_i != {} and E' = empty set or E' = {{}}.

### Definition 12: Expansive Change *(p.9)*
|E| = |E'| and for every E'_j in E', there exists E_i in E s.t. E_i is a strict subset of E'_j.

### Definition 13: Conservative Change *(p.9)*
E = E'.

### Definition 14: Altering Change *(p.10)*
|E| = |E'| and there exists E_i in E and there exists E'_j in E' s.t. E_i is not a subset of E'_j.

### Definition 15: Monotony *(p.11)*
The change from G to G' satisfies Monotony if the intersection of the extensions of G is included in the union of the extensions of G'.
- **Credulous Monotony**: every argument credulously accepted before remains credulously accepted after
- **Skeptical Monotony**: every argument skeptically accepted before remains skeptically accepted after

### Definition 16: Partial Monotony for X *(p.12)*
For a particular argument X, X belongs to the extensions after change if it belonged before.

### Definition 17: Priority to Recency *(p.13)*
The change satisfies Priority to Recency if G' has at least one extension and the added argument Z belongs to each extension of G'.

## Key Equations

$$
(\mathbf{A}, \mathbf{R}) \oplus_i^a (Z, Z_r) = (\mathbf{A} \cup \{Z\}, \mathbf{R} \cup Z_r)
$$
Where: A = set of arguments, R = attack relation, Z = new argument, Z_r = new interactions
*(p.5)*

$$
\mathcal{E}' = \mathcal{E} \cup \{Z\} \cup \bigcup_{i \geq 1} \mathcal{F}^{ri}(\{Z\})
$$
Where: E' = new grounded extension when E defends Z and Z does not attack G
*(p.17)*

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
- Under grounded semantics, adding Z that is not attacked and does not attack E results in conservative change (Prop.9) *(p.16)*
- Under grounded semantics, if E defends Z and Z does not attack G, change is expansive (Prop.11) *(p.17)*
- Under grounded semantics, change is never questioning nor restrictive (Prop.12) *(p.17)*
- Under preferred semantics, if Z attacks no argument of G and E = {{}} or equivalently E = {{}}, the change is decisive only if Z is attacked and no even-length cycle exists (Prop.16-17) *(p.19)*
- Presence/absence of even-length cycles in the attack graph is critical for determining change type under preferred semantics *(p.19-21)*

### Necessary and sufficient conditions (Table 4, p.21)
For the change operation of adding argument Z:

**Grounded semantics:**
- Decisive: CS and CN when E = {} and Z not attacked (Prop.9)
- Restrictive: Never (Prop.12)
- Questioning: Never (Prop.12)
- Destructive: CN and CS when E != {} and Z attacks each unattacked arg in G and Z is attacked (Prop.13)
- Expansive: CS when E != {} and Z does not attack E and E defends Z (Prop.11)
- Conservative: CS when E = {} and Z attacked by G (Prop.9); CS' when E != {} and Z does not attack E and E does not defend Z (Prop.11)
- Altering: CN when E != {} and Z attacks E (Prop.10)

**Preferred semantics:**
- Decisive: CS when E = {{}} and Z not attacked and no even-length cycle in G (Prop.16); if E = {{}} CN: Z attacks G (Prop.17)
- Restrictive: CN when there exists even-length cycle in G and Z attacks at least one E_i (Prop.15)
- Questioning: CN when there exists even-length cycle in G' and Z attacks G (Prop.17, Prop.18)
- Destructive: CS when E != {{}} and Z is attacked and no even-length cycle in G' and Z attacks each unattacked arg in G (Prop.21)
- Expansive: CS when E != {{}} and Z does not attack G and for all i, E_i defends Z (Prop.18)
- Conservative: CS when E = {{}} and Z does not attack G (Prop.17); CS' when E != {{}} and Z does not attack G and for all i, E_i does not defend Z (Prop.18)
- Altering: CN when E != {{}} and there exists E_i s.t. Z attacks E_i (Prop.15)

### Status-based conditions (Table 5, p.22)
- **Monotony**: Under grounded: Monotony iff Z does not directly attack X (Prop.7); Under preferred: Z does not attack any E_i (Prop.16)
- **Priority to Recency**: Under grounded: CS when E != {} and Z does not attack E and E defends Z (Prop.11); Under preferred: Z not attacked (Prop.14), or Z attacks no extension of G and E defends Z (Prop.15)
- **Partial Monotony for X**: Under grounded: CS when X in E and Z does not directly attack X (Prop.7); Under preferred: Monotony (because for preferred, Partial Monotony for X is implied by Monotony)
- **Skeptical Monotony**: Under grounded: always satisfied (because Monotony is Skeptical Monotony for grounded); Under preferred: no controversial arg in G and Z does not attack extensions (Prop.20)

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
- A conservative change always satisfies Monotony and Skeptical Monotony (Conseq.3) *(p.13)*
- A destructive change never satisfies Monotony (Conseq.4) *(p.13)*
- An expansive change always satisfies Monotony, Skeptical Monotony, and (under stable/grounded/preferred) Priority to Recency (Conseq.3, Prop.6) *(p.13-14)*
- A conservative change never satisfies Priority to Recency (Conseq.5) *(p.13)*
- A destructive change never satisfies Priority to Recency (Conseq.5) *(p.13)*
- If Z is not attacked by G, Z does not attack E, and E defends Z under grounded semantics, the change is expansive (Prop.11) *(p.17)*
- Under grounded semantics, if Z attacks each unattacked argument and Z is attacked, the change is destructive; the converse also holds (Prop.13) *(p.17)*
- Under preferred semantics, if E != {{}} and Z is attacked and no even-length cycle in G' and Z attacks each unattacked arg in G, the change is destructive (Prop.21) *(p.21)*
- Adding argument Z that does not attack G and is not attacked produces decisive change under grounded semantics (Prop.9) *(p.16)*

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
