---
title: "ABA+: Assumption-Based Argumentation with Preferences"
authors: "Kristijonas Čyras; Francesca Toni"
year: 2016
venue: "arXiv preprint"
doi_url: "https://arxiv.org/abs/1610.03024"
pages: 45
---

# ABA+: Assumption-Based Argumentation with Preferences

## One-Sentence Summary
Introduces ABA+, an assumption-based argumentation formalism that incorporates preferences over assumptions directly into attack, reversing attacks whose support is strictly less preferred than the attacked assumption. *(p.1, p.8)*

## Problem Addressed
Standard ABA represents uncertain information as assumptions and defines attacks when one set of assumptions derives the contrary of an assumption in another set, but it has no native object-level preference handling. ABA+ adds a transitive preference relation over assumptions and changes attack itself rather than post-filtering extensions. *(p.2, p.7-p.8)*

## Key Contributions
- Defines ABA+ frameworks `(L, R, A, contrary, <=)` as ABA frameworks with a transitive binary preference relation over assumptions. *(p.7)*
- Defines `<-attack`: a normal attack succeeds only when no attacking assumption used in the derivation is strictly less preferred than the attacked assumption; otherwise a reverse attack is generated from the attacked side back to the weaker attacker. *(p.8)*
- Defines ABA+ conflict-freeness, defence, admissible, preferred, complete, stable, well-founded/grounded, and ideal extensions by replacing ABA attack/defence with `<-attack`/`<-defence`. *(p.9)*
- Shows in the referendum example that preference `alpha < beta` changes the unique acceptable extension from the ABA tie to `{beta}`. *(p.8-p.9)*

## Methodology
The paper starts from ABA as a deductive system with a language, rules, assumptions, and a total contrary map. It then adds preferences over assumptions and defines preference-aware attack by combining standard derivability of contraries with attack reversal. *(p.4-p.9)*

## Key Equations / Formal Definitions

ABA framework:

$$
(L, R, A, \overline{\phantom{x}})
$$

Where `L` is a language, `R` contains rules `phi_0 <- phi_1,...,phi_m`, `A` is a non-empty set of assumptions, and `contrary: A -> L` maps each assumption to its contrary. *(p.4)*

Conclusions of a set:

$$
Cn(E) = \{\varphi \in L : \exists S \vdash_R \varphi,\ S \subseteq E,\ R \subseteq \mathcal{R}\}
$$

Where `S` supports a deduction tree for `varphi` using rules in `R`. *(p.4)*

Closure under assumptions:

$$
Cl(E) = \{\alpha \in A : \exists S \vdash_R \alpha,\ S \subseteq E,\ R \subseteq \mathcal{R}\} = Cn(E) \cap A
$$

An assumption set is closed iff `A = Cl(A)`; a framework is flat iff every assumption subset is closed. *(p.5)*

ABA attack:

$$
A \leadsto B \iff \exists \beta \in B,\ \exists A' \subseteq A : A' \vdash_R \overline{\beta}
$$

An assumption set attacks another when it derives the contrary of at least one target assumption. *(p.5)*

ABA+ framework:

$$
(L, R, A, \overline{\phantom{x}}, \leq)
$$

Where `<=` is a transitive binary relation over assumptions; strict preference is `alpha < beta` iff `alpha <= beta` and not `beta <= alpha`. *(p.7)*

ABA+ normal attack:

$$
A \leadsto_{<} B
$$

Holds when `A' subseteq A` derives `contrary(beta)` for some `beta in B` and no `alpha' in A'` is strictly less preferred than `beta`. *(p.8)*

ABA+ reverse attack:

$$
A \leadsto_{<} B
$$

Also holds when `B' subseteq B` derives `contrary(alpha)` for some `alpha in A` and some `beta' in B'` is strictly less preferred than `alpha`; this reverses a blocked weaker attack. *(p.8)*

## Parameters

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| Preference relation | `<=` | - | none | transitive binary relation over assumptions | 7 | Need not be reflexive; strict part is derived from asymmetry. |
| Strict preference | `<` | - | derived | `alpha <= beta` and not `beta <= alpha` | 7 | Used to test weaker attackers. |
| Flatness condition | - | - | required by this workstream | every assumption subset is closed | 5 | WS-O-arg-aba-adf implements only flat ABA/ABA+. |

## Worked Examples

### Example 3: referendum as flat ABA

Language `L = {alpha, beta, leave, stay}`; rules `leave <- alpha` and `stay <- beta`; assumptions `A = {alpha, beta}`; contraries `contrary(alpha)=stay`, `contrary(beta)=leave`. The framework is flat. `{alpha}` and `{beta}` attack each other; preferred and stable extensions are `{alpha}` and `{beta}`; grounded/well-founded and ideal extension is empty; `{alpha}`, `{beta}`, and empty are admissible and complete. *(p.6)*

### Example 5-7: referendum as flat ABA+

Using the same flat ABA framework with preference `alpha < beta`, `{alpha}` tries to attack `{beta}` but is blocked because the attacker uses an assumption strictly less preferred than the attacked assumption. The attack reverses, so `{beta}` attacks `{alpha}`. The unique ABA+ complete, preferred, stable, ideal, and grounded extension is `{beta}`; its conclusions are `{beta, stay}`. *(p.7-p.9)*

### Example 4 and 8: non-flat boundary

Adding assumption `delta` and rule `beta <- delta` makes `beta` derivable from another assumption, so the framework is non-flat. The paper handles this generally, but WS-O-arg-aba-adf explicitly rejects this class at construction time and leaves non-flat ABA to a successor workstream. *(p.3, p.6, p.9)*

## Methods & Implementation Details
- Implement flatness as a type-boundary check: in a flat ABA framework, no assumption can be derivable from another assumption set beyond closure itself; a conservative constructor gate rejects any rule with an assumption as head. *(p.5-p.6)*
- Implement standard ABA attack by forward derivability of contraries from attacker assumptions. *(p.5)*
- Implement ABA+ attack with two branches: normal attack when no support assumption is strictly weaker than the target assumption, and reverse attack when the target side derives a contrary using a strictly weaker assumption. *(p.8)*
- Implement ABA+ semantics by swapping ABA attack/defence for ABA+ attack/defence, leaving the extension definitions otherwise parallel. *(p.9)*

## Figures of Interest
- **Figure 1 (p.6):** Flat ABA attack graph for referendum example; shows empty, singleton, and two-assumption nodes.
- **Figure 2 (p.8):** Flat ABA+ attack graph where preference reverses attack in favor of `{beta}`.

## Results Summary
The core implementation result for this workstream is the attack-reversal rule. On the flat referendum framework, plain ABA has two preferred/stable extensions `{alpha}` and `{beta}`, but ABA+ with `alpha < beta` has the unique complete/preferred/stable/ideal/grounded extension `{beta}`. *(p.6, p.9)*

## Limitations
The paper supports non-flat ABA+, but this workstream does not. Non-flat support requires assumption closure beyond the head-not-in-assumptions constructor gate and is tracked as a separate follow-up. *(p.3, p.6, p.9)*

## Design Rationale
- Preferences are object-level over assumptions, not meta-level over arguments or extensions. *(p.3)*
- Attack reversal is used instead of merely discarding preference-defeated attacks; this differentiates ABA+ from many other preference approaches. *(p.3)*
- The same extension labels as ABA are retained, with the preference-aware attack relation replacing ordinary attack. *(p.9)*

## Testable Properties
- In Example 3 without preferences, preferred and stable extensions are `{alpha}` and `{beta}`; grounded and ideal are empty. *(p.6)*
- In Example 7 with `alpha < beta`, the unique complete/preferred/stable/ideal/grounded ABA+ extension is `{beta}`. *(p.9)*
- Constructing the Example 4 non-flat framework should be rejected by the flat-only API boundary in this project. *(p.6)*
- ABA+ normal attack from `A` to `B` is blocked when some support assumption in `A` is strictly less preferred than the attacked assumption in `B`. *(p.8)*
- ABA+ reverse attack is generated from `B` to `A` when `A`'s ordinary attack on `B` is blocked by such a strict preference. *(p.8)*

## Relevance to Project
WS-O-arg-aba-adf uses this paper for the flat ABA+ preference rule and the worked referendum regression. Propstore does not consume ABA+ directly in this workstream, but the pinned dependency must expose behavior that future trust-calibration and assumption-level reasoning code can use.

## Open Questions
- [ ] Non-flat ABA+ remains out of scope for this workstream and needs a separate implementation plan.
- [ ] Weak Contraposition from later sections should be handled only in a future non-flat/advanced ABA+ workstream.

## Related Work Worth Reading
- Bondarenko, Dung, Kowalski, and Toni 1997 for the underlying ABA framework.
- Toni 2014 for a tutorial treatment of ABA deductions and attack views.
- Preference-based argumentation frameworks for attack-reversal comparison.

## Collection Cross-References
- Uses the ABA background formalized in [An Abstract, Argumentation-Theoretic Approach to Default Reasoning](../Bondarenko_1997_AbstractArgumentation-TheoreticApproachDefault/notes.md).
- Complements [A Tutorial on Assumption-Based Argumentation](../Toni_2014_TutorialAssumption-basedArgumentation/notes.md), which supplies the flat ABA tutorial framing used by WS-O-arg-aba-adf.
