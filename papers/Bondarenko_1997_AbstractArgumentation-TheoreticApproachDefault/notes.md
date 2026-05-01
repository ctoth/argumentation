---
title: "An abstract, argumentation-theoretic approach to default reasoning"
authors: "A. Bondarenko, P. M. Dung, R. A. Kowalski, F. Toni"
year: 1997
venue: "Artificial Intelligence"
doi_url: "10.1016/S0004-3702(97)00015-5"
pages: "63-101"
---

# An abstract, argumentation-theoretic approach to default reasoning

## One-Sentence Summary
Defines the Assumption-Based Argumentation (ABA) framework — a deductive system `(L, R)` with a distinguished assumption set `Ab ⊆ L` and a contrary mapping `¯: Ab → L` — and gives a unified family of argumentation-theoretic semantics (naive, stable, admissible, preferred, complete, well-founded; credulous and sceptical) that subsume Theorist, Reiter default logic, normal and extended/abductive logic programming, Marek/Nerode/Remmel non-monotonic rule systems, autoepistemic logic, non-monotonic modal logic, and certain Herbrand-model instances of circumscription as special cases *(p.63)*.

## Problem Addressed
Non-monotonic logics proliferated with incompatible vocabularies and semantics. The authors provide one abstract framework in which each appears as a special case, so that their semantic commitments can be compared on uniform terms, and so that argumentation-theoretic semantics from logic programming (admissibility, preferred, complete, well-founded) can be exported to the other formalisms *(p.64)*.

## Key Contributions
- **Assumption-based framework** as a tuple `(T, Ab, ¯)` over a deductive system `(L, R)`; `¯` primitive, not reduced to inconsistency *(p.69-70)*.
- Recasts Theorist, Reiter default logic, normal and extended/abductive logic programming, Marek/Nerode/Remmel non-monotonic rule systems, autoepistemic logic, non-monotonic modal logic, and Herbrand-case circumscription as ABA instances *(p.70-75, p.91-92)*.
- Abstract definition of **attack**: `Δ attacks α` iff `T ∪ Δ ⊢ ᾱ`; `Δ attacks Δ'` iff `Δ` attacks some `α ∈ Δ'` (Def 3.1, *(p.76)*).
- Five credulous semantics — naive, stable, admissibility, preferred, complete — plus sceptical counterparts including well-founded *(p.68)*.
- Stable semantics matches the native semantics of each embedded logic: Theorist extensions (Thm 3.12), stable models of LP (Thm 3.13), Reiter-extensions of default logic (Thm 3.16), Moore-stable-expansions of AEL (Thm 3.18), fixed points of NMML (Thm 3.19) *(p.79-83)*.
- Admissibility / preferred / complete match Dung [10] scenarios for LP (Thms 4.5, 5.9) *(p.84, p.89)*.
- Well-founded (intersection of all complete sets) = Van Gelder/Ross/Schlipf WFS for LP (Thm 6.3); for flat frameworks it is the least fixed point of the `Def` operator and is contained in every preferred and every stable set (Thms 6.2, 6.4, 6.5) *(p.89-90)*.
- Sceptical version of **naive** semantics = circumscription, when every model of `T` is Herbrand (Cor 6.8) *(p.92)*.
- Existence and coincidence theorems via **stratified** (attack graph well-founded) and **order-consistent** (two-sidedness relation well-founded) frameworks (Thms 7.5, 7.10, 7.11) *(p.93-95)*.

## Study Design (empirical papers)
*Pure theory paper — no empirical section.*

## Methodology
Fix a minimal apparatus — a deductive system `(L, R)` and an assumption-based framework `(T, Ab, ¯)`. Re-express each non-monotonic logic as a specific instantiation by choosing `L`, `R`, `T`, `Ab`, `¯`. Define semantics purely at the abstract level via the attack relation over `Ab`. Prove correspondence theorems with each source logic's native semantics. The whole enterprise focuses on *sets of assumptions*, not arguments-as-proof-trees; "arguments" are abstracted to the assumptions they rest on *(p.68)*.

## Key Equations / Statistical Models

### Deductive system inference rule schema

$$
\frac{\alpha_1, \ldots, \alpha_n}{\alpha}
$$
Where `α, α_1, ..., α_n ∈ L`, `n ≥ 0`. Rules with `n = 0` are logical axioms. `T ⊢ α` means there is a finite sequence of rule applications deriving `α` from `T`. `Th(T) = {α | T ⊢ α}`. Every such system is **compact** and **monotonic**. *(p.69)*

### Assumption-based framework

$$
\langle T, Ab, \overline{\phantom{x}} \rangle
$$
`T, Ab ⊆ L`, `Ab ≠ ∅`, `¯: Ab → L`. *(p.70)*

### Conflict-free (Def 2.2)

$$
\Delta \text{ conflict-free} \iff \forall \alpha \in \Delta.\ T \cup \Delta \not\vdash \overline{\alpha}
$$
*(p.70)*

### Attack (Def 3.1)

$$
\Delta \text{ attacks } \alpha \iff T \cup \Delta \vdash \overline{\alpha}
$$
$$
\Delta \text{ attacks } \Delta' \iff \exists \alpha \in \Delta'.\ \Delta \text{ attacks } \alpha
$$
*(p.76)*

### Closed (Def 3.3)

$$
\Delta \text{ closed} \iff \Delta = \{\alpha \in Ab \mid T \cup \Delta \vdash \alpha\}
$$
*(p.76)*

### Stable (Def 3.4)

`Δ` stable iff closed, does not attack itself, and attacks every `α ∈ Ab \ Δ`. *(p.77)*

### `S` operator (Def 3.8)

$$
S(\Delta) = \{\alpha \mid \Delta \text{ does not attack } \alpha\}
$$
Closed `Δ` stable iff `Δ = S(Δ)` (Thm 3.9). *(p.78)*

### Admissibility (Def 4.3)

`Δ` admissible iff closed, does not attack itself, and for every closed `Δ' ⊆ Ab` that attacks `Δ`, `Δ` attacks `Δ'`. *(p.83)*

### Preferred (Def 4.4)

$$
\Delta \text{ preferred} \iff \Delta \text{ is maximal (}\subseteq\text{-) admissible}
$$
*(p.84)*

### Flatness (Def 4.10)

$$
\text{Framework flat} \iff \forall \Delta \subseteq Ab.\ \Delta \text{ is closed}
$$
equivalently `∀β ∈ Ab. T ∪ Δ ⊢ β ⇔ β ∈ Δ`. *(p.86)*

### Defence and `Def` operator (Def 5.1, 5.2)

$$
\Delta \text{ defends } \alpha \iff \forall \text{ closed } \Delta'.\ \Delta' \text{ attacks } \alpha \Rightarrow \Delta \text{ attacks } \Delta' - \Delta
$$
$$
Def(\Delta) = \{\alpha \mid \Delta \text{ defends } \alpha\}
$$
*(p.87)*

### Admissibility via `Def` (Thm 5.3)

$$
\Delta \text{ admissible} \iff \Delta \text{ closed} \land \Delta \subseteq Def(\Delta)
$$
*(p.87)*

### Complete (Def 5.4)

$$
\Delta \text{ complete} \iff \Delta \text{ closed} \land \Delta = Def(\Delta)
$$
*(p.87)*

### Well-founded (Def 6.1)

$$
\Delta_{WF} = \bigcap \{\Delta \mid \Delta \text{ complete}\}
$$
For flat frameworks, `Δ_WF = ⋃_i Def^i(∅)` — the least fixed point of the monotonic operator `Def` (Thm 6.2). *(p.89-90)*

### Circumscription `Ab` (Section 6.2)

$$
Ab = HB^P_\neg \cup HB^Q_\neg \cup HB^Q
$$
Where `P` is minimised predicates, `Q` fixed predicates, `Z` varied predicates; `HB^P_\neg = {¬p(t_1,...,t_n) | p ∈ P}`, `HB^Q_\neg = {¬q(...) | q ∈ Q}`, `HB^Q = {q(...) | q ∈ Q}`; `ᾱ = ¬α`. *(p.91)*

### Default rule form (Reiter)

$$
\frac{\alpha, M\beta_1, \ldots, M\beta_n}{\gamma}
$$
*(p.73, footnote 8)*

### Necessitation rule (non-monotonic modal logic)

$$
\frac{\alpha}{L\alpha}
$$
*(p.75)*

### Marek/Nerode/Remmel non-monotonic rule

$$
\frac{\alpha_1, \ldots, \alpha_n, M\beta_1, \ldots, M\beta_m}{\gamma}
$$
*(p.74, footnote 9)*

## Parameters
*Pure theory — no numeric parameters. The framework's "parameters" are the instantiation choices: `(L, R)`, `T`, `Ab`, `¯`, and the semantics chosen (naive / stable / admissible / preferred / complete / well-founded / sceptical variant).*

## Effect Sizes / Key Quantitative Results
*Not applicable.*

## Methods & Implementation Details

### Core constructions every implementer must support
- **Deductive system `(L, R)`**: countable language plus a set of inference rules `α_1, ..., α_n / α`. Derive `T ⊢ α`; closure `Th(T)` *(p.69)*.
- **Assumption-based framework `(T, Ab, ¯)`**: `T ⊆ L`, `Ab ⊆ L`, `Ab ≠ ∅`, `¯: Ab → L`. `ᾱ` is not required to be `¬α` *(p.70)*.
- **Do not collapse `¯` onto inconsistency.** The paper intentionally keeps the contrary mapping primitive: (a) contrariness may be non-classical, (b) the underlying logic can be weaker than classical, (c) the framework does not rely on inconsistency-implies-everything *(p.70)*.
- **Attack**: `Δ attacks α` iff `T ∪ Δ ⊢ ᾱ` — the single attack predicate across all semantics *(p.76)*.
- **Closedness** prevents a `Δ` from attacking an implied-but-missing assumption *(p.76)*.
- **Flatness** — a sufficient, checkable structural condition ensuring every semantics is well-behaved. LP and default-logic instantiations are always flat; AEL never flat; Theorist and NMML sometimes *(p.86)*.
- **`Def` operator** monotonic; for flat frameworks has least fixed point = well-founded set *(p.89-90)*.
- **Attack relationship graph** (Def 7.1): directed graph whose nodes are `Ab` and whose edges `δ → α` mean `δ` participates in some minimal attack against `α` *(p.93)*.

### Translation table (ABA instantiation of each source logic)

| Source logic | `L` | `T` | `Ab` | `ᾱ` | Properties | Page |
|---|---|---|---|---|---|---|
| Theorist (Poole [43]) | classical FOL | consistent `T ⊆ L_0` | given `Ab` of abductive framework | `¬α` | normal (Thm 3.11); not always flat | *(p.70-71, p.79)* |
| Normal logic programming | `Lit ∪ {clauses}`, `Lit = HB ∪ HB_not` | `∅` (rules live in `R`) | `HB_not` | `\overline{not\ α} = α` | flat (Thm 4.12); not always normal | *(p.71-72, p.86)* |
| Default logic (Reiter [49]) | `L_0 ∪ {Mα | α ∈ L_0}` | `T ⊆ L_0` | `{Mβ | Mβ in some default rule}` | `\overline{Mα} = ¬α` | flat (Thm 4.12); normal if default theory is normal (Thm 3.17) | *(p.73, p.81, p.86)* |
| Marek/Nerode/Remmel non-monotonic rule systems | `L_0 ∪ {Mα}` | `T ⊆ L_0` | `{Mα | α ∈ L_0}` | `\overline{Mα} = ¬α` | — | *(p.74)* |
| Autoepistemic logic (Moore [40]) | modal `L` with `L` operator | given `T` | `{Lα} ∪ {¬Lα}` | `\overline{Lα} = ¬Lα`, `\overline{¬Lα} = α` | never flat; stable extensions ↔ consistent stable expansions (Thm 3.18) | *(p.75, p.81-82, p.86)* |
| Non-monotonic modal logic (McDermott [39]) | first-order modal with `L` and necessitation in `R` | given `T ⊊ L` | `{¬Lα}` | `\overline{¬Lα} = α` | may be flat; stable extensions ↔ fixed points of consistent `T` (Thm 3.19) | *(p.75, p.82-83)* |
| Extended / abductive logic programming [14, 21, 25, 26] | — | — | — | — | one-to-one with admissible/preferred sets (Thm 4.5 extension) | *(p.84)* |
| Circumscription (McCarthy [38]), Herbrand case | first-order `L` | `T ⊆ L` with all models Herbrand | `HB^P_\neg ∪ HB^Q_\neg ∪ HB^Q` | `¬α` | Cor 6.8: `α ∈ CIRC[T; P; Z]` iff `α` holds in all maximal conflict-free extensions — i.e., the *sceptical* version of naive semantics | *(p.91-92)* |

### Correspondence theorems with source-logic native semantics
- **Thm 3.11**: Theorist framework always normal *(p.79)*.
- **Thm 3.12**: Theorist extension of `(T, Ab)` iff stable extension of ABA framework *(p.79)*.
- **Thm 3.13**: stable model (Gelfond/Lifschitz) of LP `P` iff stable extension `E` with `M = E ∩ HB` *(p.80)*.
- **Thm 3.16**: `E ⊆ L_0` is a Reiter-extension of `(T, D)` iff there is a stable extension `E'` with `E = E' ∩ L_0` *(p.81)*.
- **Thm 3.17**: For normal default theories, the ABA framework is normal *(p.81)*.
- **Thm 3.18**: `E` is Moore-stable-expansion of AEL theory `T` iff `E` is consistent stable extension of ABA framework *(p.81-82)*.
- **Thm 3.19**: `E` is stable extension of ABA(NMML theory `T`) iff `T` is consistent and `E` is fixed point of `T` *(p.82-83)*.
- **Thm 4.5**: `T ∪ Δ` is admissible/preferred scenario (Dung [10]) iff `Δ` is admissible/preferred in ABA *(p.84)*.
- **Thm 5.9**: complete scenario of Dung [10] iff complete set of assumptions *(p.89)*.
- **Thm 6.3**: `{p | P ∪ Δ ⊢ p} ∪ {¬p | not p ∈ Δ}` is VGRS well-founded model iff `Δ` well-founded in ABA *(p.90)*.
- **Thm 6.7 + Cor 6.8 (circumscription)**: If every model of `T` is a Herbrand model, then `α ∈ CIRC[T; P; Z]` iff `α` holds in all maximal conflict-free extensions of `(T, Ab, ¯)` *(p.92)*.

### Algorithm / operator specs
- **Thm 2.3 (constructive max-conflict-free extension)**: enumerate `Ab \ Δ = α_0, α_1, ...`; `Δ_0 = Δ`; `Δ_{n+1} = Δ_n ∪ {α_n}` if conflict-free, else `Δ_n`; `Δ' = ⋃_i Δ_i`. Maximal conflict-free containing `Δ` *(p.70)*.
- **Thm 3.10 (four equivalent forms of stable extension)** — given framework and `E ⊆ L`, let `Δ_E = {α ∈ Ab | ᾱ ∉ E}`; equivalent *(p.78)*:
  1. `E` stable extension.
  2. `E = Th(T ∪ Δ_E)` and `Δ_E` closed.
  3. `E = ⋃_{i=1}^∞ E_i` with `E_1 = T ∪ Δ_E`, `E_{i+1} = E_i ∪ {β | (α_1,...,α_n)/β ∈ R, α_1,...,α_n ∈ E_i}`, `Δ_E` closed.
  4. `E = Γ(E)` where `Γ(S)` is smallest set containing `T ∪ Δ_S` and closed under `R`, with `Δ_E` closed.
- **Thm 4.9 (preferred existence)**: every admissible `Δ` extends to a preferred set — Zorn's lemma on admissible chains *(p.85)*.
- **Cor 4.11**: every flat framework has a preferred extension (`∅` admissible in flat framework) *(p.86)*.
- **Thm 5.7**: for flat frameworks, `Δ admissible, S ⊆ Def(Δ)` ⇒ `Δ ∪ S` admissible *(p.88)*.
- **Cor 5.8**: every preferred of a flat framework is complete *(p.89)*.
- **Thm 6.2**: for flat framework, well-founded = least fixed point of `Def` = `⋃_i Def^i(∅)` (bottom-up computation) *(p.89)*.
- **Thm 6.4 / 6.5**: for flat framework, well-founded ⊆ every preferred and every stable set *(p.90)*.

### Existence and coincidence theory (Section 7)

- **Def 7.1 (attack relationship graph)**: directed graph on `Ab` with edge `δ → α` iff `δ` belongs to a minimal (⊆-) attack against `α` *(p.93)*.
- **Def 7.2 (stratified framework)**: flat framework whose attack graph is well-founded (no infinite path `α_1, α_2, ...` with edge `α_{n+1} → α_n`) *(p.93)*.
- **Thm 7.5**: every stratified framework has a *unique* stable set of assumptions, coinciding with the well-founded set — so WF = stable = preferred and all three are unique *(p.93-94)*.
- **Def 7.6 (friendly / hostile / two-sided)**: `δ` friendly to `α` iff even-length path exists from `δ` to `α` in attack graph; hostile iff odd-length path exists; two-sided (`δ ≺ α`) iff both *(p.94)*.
- **Def 7.7 (order-consistent)**: flat framework where `≺` is well-founded (no infinite `≺`-descending sequence) *(p.94)*.
- **Thm 7.9**: every stratified framework is order-consistent *(p.94)*.
- **Thm 7.10**: for every order-consistent framework, preferred sets = stable sets (existence guaranteed by Cor 4.11; may not be unique) *(p.94)*.
- **Thm 7.11**: the abstract stratification / order-consistency notions generalise the corresponding LP notions (Apt/Blair/Walker [4], Sato [51]) *(p.95)*.

### Edge cases and negative results (witnesses)
- LP `{p ← not p}` has *no* stable extension but `∅` admissible; `{not p}` attacks itself (Ex 4.1) *(p.83)*.
- AEL/NMML theory `{¬Ls → ¬r, ¬Lt → r}` has no stable extension but `{¬Ls}` and `{¬Lt}` each admissible (Ex 4.2) *(p.83)*.
- LP `{p ← not q, q ← not r, r ← not p}` has only `∅` preferred; `{not p}, {not q}, {not r}` are maximal conflict-free but not admissible (Ex 4.7) *(p.85)*.
- A consistent AEL theory can have an inconsistent stable expansion: `T = {¬Lp}` has expansion `E = L` (Section 3.4) *(p.81)*.
- NMML fixed points of a consistent `T` are always consistent — so NMML is better behaved than AEL (Section 3.5) *(p.82)*.
- Example 4.13: LP `{r* ← not s, r ← not t, s ← r, r*, t ← r, r*}` simulates Ex 4.2 and shows admissibility can still be insufficient, motivating Kakas/Mancarella stable-theory/acceptability semantics (mentioned, not expanded) *(p.86-87)*.
- Ex 5.6: NMML `{¬Lp → q, ¬Lr → ¬q}` — `{¬Lp}` admissible, `¬Lr` defended, but `{¬Lp, ¬Lr}` attacks itself, so preferred sets need not be complete in non-flat frameworks *(p.88)*.
- Ex 6.6 LP `{p ← not q, q ← not p, r ← p, r ← q}` — two stable/preferred sets `{not p}, {not q}` each justify `r`, but well-founded set is `∅` and does not justify `r`. Shows well-founded is strictly more sceptical than intersection-of-stable *(p.91)*.
- Ex 7.3 LP `{p ← not q, q ← not p}` is not stratified (infinite path `not p, not q, not p, ...`) *(p.93)*.
- Ex 7.4 LP `{p(X) ← not p(s(X)), p(0)}` is not stratified *(p.93)*.
- Ex 7.8 LP `{p ← not p}` is not order-consistent *(p.94)*.
- LP stratified (Apt/Blair/Walker) ⇒ ABA stratified; LP order-consistent (Sato) ⇒ ABA order-consistent (Thm 7.11) *(p.95)*.

## Figures of Interest
*No figures in the paper — pure prose and displayed math throughout all 39 pages.*

## Results Summary
- **Thm 2.3**: every conflict-free `Δ` extends to maximal conflict-free *(p.70)*.
- **Thm 2.4**: Theorist scenarios ↔ conflict-free `Δ`; Theorist extensions ↔ naive extensions *(p.71)*.
- **Thm 3.5**: stable ⇒ maximal conflict-free (converse fails) *(p.77)*.
- **Thm 3.7**: sufficient condition for normality *(p.77)*.
- **Thm 3.9**: closed `Δ` stable iff `Δ = S(Δ)` *(p.78)*.
- **Thm 3.10**: four equivalent characterisations of stable extension *(p.78)*.
- **Thm 3.11**: Theorist framework normal *(p.79)*.
- **Thm 3.12, 3.13, 3.16, 3.17, 3.18, 3.19**: stable-extension identifications for Theorist, LP, default logic, normal default, AEL, NMML *(p.79-83)*.
- **Thm 4.5**: admissible/preferred = Dung LP admissible/preferred *(p.84)*.
- **Thm 4.6**: every stable is preferred (converse fails) *(p.84)*.
- **Thm 4.8**: normal framework — maximal conflict-free = stable = preferred *(p.85)*.
- **Thm 4.9 + Cor 4.11**: admissibility → preferred existence; flat framework → preferred exists *(p.85-86)*.
- **Thm 4.12**: LP and default-logic frameworks are flat; AEL never *(p.86)*.
- **Thm 5.3**: admissible ≡ closed ∧ `Δ ⊆ Def(Δ)` *(p.87)*.
- **Thm 5.5**: stable ⇒ complete *(p.88)*.
- **Thm 5.7 / Cor 5.8**: flat framework: preferred ⇒ complete *(p.88-89)*.
- **Thm 5.9**: complete set ≡ Dung LP complete scenario *(p.89)*.
- **Thm 6.2**: flat framework: well-founded = least fixed point of `Def` *(p.89)*.
- **Thm 6.3**: well-founded set ≡ VGRS well-founded model *(p.90)*.
- **Thm 6.4, 6.5**: flat framework: well-founded ⊆ every preferred, every stable *(p.90)*.
- **Thm 6.7 + Cor 6.8**: Herbrand-case circumscription ≡ sceptical naive *(p.92)*.
- **Thm 7.5**: stratified framework has unique stable = well-founded *(p.93)*.
- **Thm 7.10**: order-consistent framework: preferred = stable (exist, possibly non-unique) *(p.94)*.
- **Thm 7.11**: LP stratification/order-consistency lift to ABA *(p.95)*.

## Limitations
- **AEL never flat** — ABA machinery is more complicated for AEL than for LP/default logic *(p.86)*.
- **Admissibility still too weak for some cases** — Ex 4.13 motivates Kakas/Mancarella stable-theory and acceptability semantics; paper defines them abstractly but refers to [27] for formal statement *(p.86-87)*.
- **Circumscription embedding restricted to cases where every model of `T` is a Herbrand model** (e.g., unique-names + domain closure + no function symbols in the predicate-language subset). The general case is not covered by Cor 6.8 *(p.91)*.
- **Stratification is strictly stronger than order-consistency** — some meaningful frameworks (Ex 7.3, `{p ← not q, q ← not p}`) are order-consistent but not stratified, so they get preferred=stable (Thm 7.10) but may have multiple stable sets, not a unique one *(p.94)*.
- **Proof procedures are not developed in this paper**; they are deferred to companion paper [13] *(p.98)*.
- **Complete sets may fail to exist in non-flat frameworks** (Ex 5.6 in NMML) *(p.88)*.
- **Paper does not unify priorities between defaults** — handled by referenced work of Prakken, Sartor, Kowalski/Toni *(p.97-98)*.

## Arguments Against Prior Work
- **Classical representation** (`∀X[¬guilty(X) → innocent(X)]`) fails to capture default character; contrapositive `¬innocent → guilty` treats innocence and guilt symmetrically, which is wrong for an "innocent-by-default" principle *(p.64-65)*.
- **Earlier assumption-based formalisation [6]** (Bondarenko/Kowalski/Toni) reduced contrariness to inconsistency. This paper rejects that reduction: `¯` is primitive; `L` need not have `¬`; inconsistency need not trivialise the theory *(p.70, p.96)*.
- **Stable semantics too opinionated** — forces `Δ` to take a stand on every `α ∈ Ab`; motivates admissibility *(p.68, p.83)*.
- **Naive semantics too liberal** — admits intuitively unacceptable sets (e.g., `{not innocent}` in the guilt LP example) *(p.68, p.72)*.
- **Admissibility itself sometimes too weak** (Ex 4.13) — motivating stable-theory/acceptability semantics (mentioned, not developed) *(p.86-87)*.
- **Existing stable-model / default-logic fixed-point definitions** fail to exist for some LPs / default theories (Ex 4.1, Ex 4.2); admissibility/preferred/well-founded always exist (for flat frameworks) *(p.83)*.
- **Marek/Nerode/Remmel** non-monotonic rule systems reconstruct standard semantics but do not employ abduction or argumentation and do not cover circumscription *(p.97)*.
- **Geffner/Pearl [19]** proof procedure for conditional entailment circumscription is incomplete; the authors conjecture this is because it computes well-founded instead of circumscription *(p.97)*.
- **Dung's earlier abstract-argumentation formulation [11]** took attack and argument as primitive; this paper reverts to [25]/[6] by taking *assumptions* primitive and defining both attacks and arguments from monotonic derivability over sets of assumptions *(p.96)*.
- **Touretzky/Horty/Thomason [59]** claimed Pollock's argumentation system cannot formalise non-monotonic inheritance; Dung/Son [15] countered using argumentation-theoretic methods from this lineage *(p.96)*.

## Design Rationale
- **`¯` primitive, not derived from `¬`**: default reasoning uses meta-level operators (`M`, `L`, `not`) whose contrary is not classical negation; underlying logic may be weaker than classical; framework must not require inconsistency-implies-everything *(p.70)*.
- **Assumption-based rather than rule-structure-based argumentation**: abstract away from argument proof-tree detail and focus on the assumption set `Δ`; `Δ attacks α` is defined without naming a specific argument structure *(p.68, p.96)*.
- **Multiple semantics rather than a canonical one**: different non-monotonic logics make different credulous/sceptical commitments. Theorist ≈ naive; default / LP stable / AEL expansions / NMML fixed points ≈ stable; Dung LP admissibility ≈ admissibility; Dung LP complete ≈ complete; VGRS WFS ≈ well-founded; Herbrand-case circumscription ≈ sceptical naive *(p.68-69, p.92)*.
- **Flatness**: a sufficient, checkable structural condition under which every semantics behaves well. Both default logic and logic programming are flat, which is why they admit particularly clean semantics *(p.86)*.
- **Closure of sets of assumptions rather than sets of formulas**: closed sets play the role of extensions while staying inside `Ab`, which is much smaller than `L` and avoids spurious "extensions" *(p.76, p.84)*.
- **Admissibility via counter-attack rather than absence of attack**: forces "self-defence", escaping the over-opinionated stable commitment while ruling out the too-liberal naive semantics *(p.83)*.
- **Separate "friendly" / "hostile" relation in Section 7**: path-parity over the attack graph captures the idea that iterated attacks can support rather than undermine, so `≺` well-foundedness is a weaker but still-useful existence condition than full attack-graph well-foundedness *(p.94)*.

## Testable Properties
- Every deductive system is compact and monotonic *(p.69)*.
- Every conflict-free `Δ` extends to maximal conflict-free (Thm 2.3) *(p.70)*.
- Conflict-free ⇒ does not attack itself; converse fails in general (Ex 3.2) *(p.76)*.
- Maximal conflict-free `Δ` is closed *(p.76)*.
- Closed `Δ` conflict-free iff `Δ` does not attack itself *(p.76)*.
- Closed `Δ` stable iff `Δ = S(Δ)` (Thm 3.9) *(p.78)*.
- Stable ⇒ maximal conflict-free; converse fails (Ex 2.6) *(p.77)*.
- Admissible ⇒ conflict-free (does not attack itself) *(p.83)*.
- Every stable set is admissible and preferred (Thm 4.6 proof) *(p.84)*.
- Not every preferred is stable (Ex 4.1) *(p.84)*.
- Flat framework: every `Δ ⊆ Ab` is closed (Def 4.10); `∅` admissible (Cor 4.11 proof) *(p.86)*.
- LP ABA and default-logic ABA are flat; AEL ABA never (Thm 4.12) *(p.86)*.
- Admissible ≡ closed ∧ `Δ ⊆ Def(Δ)` (Thm 5.3) *(p.87)*.
- Complete ≡ closed ∧ `Δ = Def(Δ)` (Def 5.4) *(p.87)*.
- Stable ⇒ complete (Thm 5.5) *(p.88)*.
- Flat framework: every preferred is complete (Cor 5.8) *(p.89)*.
- Flat framework: well-founded = least fixed point of `Def` (Thm 6.2) *(p.89)*.
- Flat framework: well-founded ⊆ every preferred and every stable (Thms 6.4, 6.5) *(p.90)*.
- `Def` is monotonic (remark before Thm 6.2) *(p.89)*.
- Well-founded ⊆ preferred (flat) but well-founded ⊈ admissible in general — `∅` admissible but need not be well-founded *(p.91)*.
- Herbrand-case: `α ∈ CIRC[T; P; Z]` iff `α` in all maximal conflict-free extensions (Cor 6.8) *(p.92)*.
- Stratified ⇒ order-consistent (Thm 7.9); converse fails (Ex 7.3 is order-consistent but not stratified) *(p.94)*.
- Stratified framework: unique stable = unique preferred = unique well-founded (Thm 7.5) *(p.93)*.
- Order-consistent framework: every preferred is stable (Thm 7.10) *(p.94)*.
- LP stratified ⇒ ABA stratified; LP order-consistent ⇒ ABA order-consistent (Thm 7.11) *(p.95)*.

## Relevance to Project
Direct grounding for the argumentation/reasoning layer (propstore CLAUDE.md layer 4). ABA is the formal backbone that generalises Dung AFs into an assumption-based setting; Reiter default logic, autoepistemic logic, non-monotonic modal logic, circumscription (Herbrand case), and logic programming stable models all appear as instantiations. Primitive `¯` (not classical `¬`) directly supports the propstore design choice to keep stance, rebuttal, and undermining as distinct relations rather than collapsing them into a single `¬`. The five semantics (naive, stable, admissible, preferred, complete) and their sceptical counterparts (well-founded, sceptical naive) give the render-policy menu. Flatness is a checkable structural property distinguishing LP/default-logic instantiations (always well-behaved) from AEL (never flat). Stratification and order-consistency are additional checkable graph-theoretic properties that, when present, guarantee uniqueness or coincidence of semantics. The `Def` operator's least-fixed-point computation via `⋃_i Def^i(∅)` is a directly implementable bottom-up procedure for the well-founded semantics. The explicit renunciation of "contrariness = inconsistency" matches propstore's commitment to honest ignorance and non-collapse of disagreement in storage.

Specific mappings to propstore constructs:
- `Ab` ↔ the distinguished set of defeasible propositions (assumptions) in a corpus.
- `¯: Ab → L` ↔ the stance-opposite or contrary-claim mapping, authored per claim rather than derived.
- `(T, Ab, ¯)` ↔ a propstore world / context bundle.
- Semantics choice (naive / stable / admissible / preferred / complete / well-founded + sceptical variant) ↔ render-policy choice.
- Flatness ↔ a property to test on a world before selecting which semantics to expose.
- `Def` operator ↔ the "defends" relation on claims; its least fixed point is the well-founded answer.

## Open Questions
- [ ] Can the Kakas/Mancarella stable-theory and acceptability semantics (mentioned, referred to [27, 28]) be added as two more layers between admissibility and stable, with abstract definitions?
- [ ] Does the Herbrand-restriction of Cor 6.8 lift to general circumscription via the "submodel contains a Herbrand model" generalisation at the top of *(p.92)*?
- [ ] Are there ABA frameworks that are not order-consistent but still have preferred=stable coincidence? (Thm 7.10 gives sufficient, not necessary, conditions.)
- [ ] Relation to Dung's abstract AFs [11, 12] is discussed in text (Section 8) but not as a formal theorem in this paper — the companion papers [11, 15] carry that out.

## Related Work Worth Reading
- [10] Dung — argumentation-theoretic foundation of LP (source of admissibility/preferred/complete).
- [11] Dung — acceptability of arguments in AFs (Dung AFs proper).
- [12] Dung — argumentation semantics for LP with explicit negation (grounded semantics).
- [20] Gelfond, Lifschitz — stable model semantics.
- [21] — answer sets for extended LP.
- [27] Kakas, Mancarella, Dung — acceptability semantics for LP.
- [28] Kakas, Mancarella — stable theories for LP.
- [29] Kakas, Mancarella — preferred extensions are partial stable models.
- [36, 37] Marek, Nerode, Remmel — non-monotonic rule systems.
- [38] McCarthy — circumscription.
- [39] McDermott — non-monotonic modal logic II.
- [40] Moore — autoepistemic logic.
- [41, 42] Pollock — defeasible reasoning; justification and defeat.
- [43] Poole — Theorist/abductive framework.
- [44, 45] Poole — explanation/prediction; default logic.
- [49] Reiter — default logic (foundational).
- [60] Van Gelder, Ross, Schlipf — well-founded semantics.
- [13] Dung, Kowalski, Toni (companion draft 1996) — proof procedures for this framework.
- [33] Lin, Shoham — argument systems (closely related abstract framework; uses complete set of *arguments* rather than *assumptions*).
- [6] Bondarenko, Toni, Kowalski — earlier ABA paper (superseded by this one).
- [25, 26] Kakas, Kowalski, Toni — abductive logic programming / role of abduction.
- [51] Sato — order-consistent LP (`local stratification`).
- [4] Apt, Blair, Walker — stratified LP.

---

## Reference List (verbatim from paper, p.99-101)

- [1] J.J. Alferes and L.M. Pereira, An argumentation-theoretic semantics based on non-refutable falsity, in: Dix, Pereira, Przymusinski, eds., *Proceedings ICLP'94 Workshop on Non-Monotonic Extensions of Logic Programming* (1994).
- [2] S.J. Alvarado, Argument comprehension, in: S. Shapiro, ed., *Encyclopedia of Artificial Intelligence* 30-52.
- [3] L. Birnbaum, M. Flowers and R. McGuire, Towards an artificial intelligence model of argumentation, in: *Proceedings AAAI-80*, Stanford, CA (1980) 313-315.
- [4] K.R. Apt, H. Blair and A. Walker, Towards a theory of declarative knowledge, in: J. Minker, ed., *Foundations of Deductive Databases and Logic Programming* (Morgan Kaufmann, Los Altos, CA, 1988).
- [5] A.B. Baker and M.L. Ginsberg, A theorem prover for prioritised circumscription, in: *Proceedings IJCAI-89*, Detroit, MI (1989) 463-467.
- [6] A. Bondarenko, F. Toni and R.A. Kowalski, An assumption-based framework for non-monotonic reasoning, in: A. Nerode and L. Pereira, eds., *Proceedings 2nd International Workshop on Logic Programming and Non-Monotonic Reasoning* (MIT Press, Cambridge, MA, 1993) 171-189.
- [7] G. Brewka and K. Konolige, An abductive framework for general logic programs and other non-monotonic systems, in: *Proceedings IJCAI-93*, Chambery, France (1993) 9-15.
- [8] A. Brogi, E. Lamma, P. Mello and P. Mancarella, Normal logic programs as open positive programs, in: *Proceedings ICSLP-92* (1992).
- [9] Y. Dimopoulos and A.C. Kakas, Logic programming without negation as failure, in: *Proceedings ILPS-95* (MIT Press, Cambridge, MA, 1995).
- [10] P.M. Dung, An argumentation theoretic foundation of logic programming, *J. Logic Programming* 22 (1995) 151-177.
- [11] P.M. Dung, The acceptability of arguments and its fundamental role in non-monotonic reasoning, logic programming and n-person games, *Artificial Intelligence* 77 (1995) 321-357.
- [12] P.M. Dung, An argumentation semantics for logic programming with explicit negation, in: *Proceedings ICLP'93* (MIT Press, Cambridge, MA) 616-630.
- [13] P.M. Dung, R.A. Kowalski and F. Toni, Argumentation-theoretic proof procedures for non-monotonic reasoning, Draft, 1996.
- [14] P.M. Dung and P. Ruamviboonsuk, Well-founded reasoning with classical negation, in: A. Nerode, V.W. Marek and D. Subrahmanian, eds., *Proceedings 1st International Workshop on Logic Programming and Nonmonotonic Reasoning* (1991) 120-135.
- [15] P.M. Dung and T.C. Son, Non-monotonic inheritance, argumentation and logic programming, in: V.W. Marek, A. Nerode and M. Truszczynski, eds., *Proceedings 3rd International Workshop on Logic Programming and Non-Monotonic Reasoning*, LNAI 928 (Springer, Berlin, 1995) 316-329.
- [16] K. Eshghi and R.A. Kowalski, Abduction through deduction, Technical Report, Imperial College, London (1988).
- [17] K. Eshghi and R.A. Kowalski, Abduction compared with negation as failure, in: *Proceedings ICLP-89* (MIT Press, Cambridge, MA, 1989).
- [18] H. Geffner, Beyond negation as failure, in: *Proceedings KR-91*, Cambridge, MA (1991) 218-229.
- [19] H. Geffner and J. Pearl, Conditional entailment: bridging to approaches to default reasoning, *Artificial Intelligence* 53 (1992) 209-244.
- [20] M. Gelfond and V. Lifschitz, The stable model semantics for logic programming, in: *Proceedings ICSLP-88* (MIT Press, Cambridge, MA, 1988).
- [21] M. Gelfond and V. Lifschitz, Logic programs with classical negation, in: D.H.D. Warren and P. Szeredi, eds., *Proceedings ICLP-90* (MIT Press, Cambridge, MA, 1990) 579-597.
- [22] M.L. Ginsberg, A circumscriptive theorem prover, *Artificial Intelligence* 39 (1989) 209-230.
- [23] K. Inoue and N. Helft, On theorem provers for circumscription, in: *Proceedings LPC-90* (1990) 115-123.
- [24] A.C. Kakas, Default reasoning via negation as failure, in: G. Lakemeyer and B. Nebel, eds., *Proceedings ECAI-92 Workshop on Foundations of Knowledge Representation and Reasoning*, LNAI 810 (Springer, Berlin).
- [25] A.C. Kakas, R.A. Kowalski and F. Toni, Abductive logic programming, *J. Logic and Computation* 2 (1993).
- [26] A.C. Kakas, R.A. Kowalski and F. Toni, The role of abduction in logic programming, in: *Handbook of Logic in Artificial Intelligence and Logic Programming* 5 (Oxford University Press, to appear).
- [27] A.C. Kakas, P. Mancarella and P.M. Dung, The acceptability semantics for logic programs, in: P. Van Hentenryck, ed., *Proceedings ICLP-94* (MIT Press, Cambridge, MA, 1994) 504-519.
- [28] A.C. Kakas and P. Mancarella, Stable theories for logic programs, in: *Proceedings ISLP-91* (MIT Press, Cambridge, MA, 1991).
- [29] A.C. Kakas and P. Mancarella, Preferred extensions are partial stable models, *J. Logic Programming* 14 (1992).
- [30] R.A. Kowalski and F. Toni, Argument and reconciliation, in: *Proceedings FGCS Workshop on Application of Logic Programming to Legal Reasoning*, Tokyo, Japan (1994).
- [31] R.A. Kowalski and F. Toni, Abstract argumentation, artificial intelligence and law, to appear.
- [32] V. Lifschitz, Circumscription, in: D. Gabbay, C. Hogger and J.A. Robinson, eds., *Handbook of Logic in Artificial Intelligence and Logic Programming* 3 (Oxford University Press, 1994) 297-352.
- [33] F. Lin and Y. Shoham, Argument systems: A uniform basis for non-monotonic reasoning, in: *Proceedings KR-89*, Cambridge, MA (1989).
- [34] P. Lorenzen and K. Lorenz, *Dialogische Logik* (Wissenschaftliche Buchgesellschaft, Darmstadt, 1977).
- [35] D. Makinson, General patterns in non-monotonic reasoning, in: D. Gabbay, C. Hogger and J.A. Robinson, eds., *Handbook of Logic in Artificial Intelligence and Logic Programming* 3 (Oxford University Press, 1994) 35-110.
- [36] W. Marek, A. Nerode and J. Remmel, A theory of non-monotonic rule systems I, *Ann. Math. Artif. Intell.* 1 (1990) 241-273.
- [37] W. Marek, A. Nerode and J. Remmel, A theory of non-monotonic rule systems II, *Ann. Math. Artif. Intell.* 5 (1992) 229-263.
- [38] J. McCarthy, Circumscription — A form of non-monotonic reasoning, *Artificial Intelligence* 13 (1980) 27-39.
- [39] D. McDermott, Nonmonotonic logic II: non-monotonic modal theories, *J. ACM* 29 (1982).
- [40] R. Moore, Semantical considerations on non-monotonic logic, *Artificial Intelligence* 25 (1985).
- [41] J.L. Pollock, Defeasible reasoning, *Cognitive Sci.* 11 (1987) 481-518.
- [42] J.L. Pollock, Justification and defeat, *Artificial Intelligence* 67 (1994) 377-407.
- [43] D. Poole, A logical framework for default reasoning, *Artificial Intelligence* 36 (1988) 27-47.
- [44] D. Poole, Explanation and prediction: an architecture for default and abductive reasoning, *Comput. Intell. J.* 5 (1989) 97-110.
- [45] D. Poole, Default logic, in: D. Gabbay, C. Hogger and J.A. Robinson, eds., *Handbook of Logic in Artificial Intelligence and Logic Programming* 3 (Oxford University Press, 1994) 189-215.
- [46] H. Prakken, Logical tools for modelling legal argument, Ph.D. Thesis, Free University Amsterdam (1993).
- [47] H. Prakken and G. Sartor, On the relation between legal language and legal argument: Assumptions, applicability and dynamic priorities, in: *Proceedings ICAIL-95* (1995) 1-10.
- [48] T.C. Przymusinski, Semantics of disjunctive logic programs and deductive databases, in: *Proceedings DOOD-91* (1991).
- [49] R. Reiter, A logic for default reasoning, *Artificial Intelligence* 13 (1980) 81-132.
- [50] D. Saccà and C. Zaniolo, Stable models and non-determinism for logic programs with negation, in: *Proceedings ACM SIGMOD-SIGACT Symposium on Principles of Database Systems* (1990).
- [51] T. Sato, Completed logic programs and their consistency, *J. Logic Programming* 9 (1990) 33-44.
- [52] K. Satoh and N. Iwayama, A correct top-down proof procedure for general logic programs with integrity constraints, in: E. Lamma and P. Mello, eds., *Proceedings 3rd International Workshop on Extensions of Logic Programming*, LNAI 660 (Springer, Berlin, 1992) 19-34.
- [53] G. Shvarts, Autoepistemic modal logics, in: *Proceedings Third Conference on Theoretical Aspects of Reasoning about Knowledge*, Pacific Grove, CA (1990).
- [54] G.R. Simari and R.P. Loui, A mathematical treatment of defeasible reasoning and its implementation, *Artificial Intelligence* 53 (1992) 125-157.
- [55] F. Toni and A.C. Kakas, Computing the acceptability semantics, in: V.W. Marek, A. Nerode and M. Truszczynski, eds., *Proceedings 3rd International Workshop on Logic Programming and Non-monotonic Reasoning*, LNAI 928 (Springer, Berlin, 1995) 401-415.
- [56] F. Toni and R.A. Kowalski, Reduction of abductive logic programs to normal logic programs, in: L. Sterling, ed., *Proceedings ICLP-95* (MIT Press, Cambridge, MA) 367-381.
- [57] A. Torres, Negation as failure to support, in: A. Nerode and L. Pereira, eds., *Proceedings 2nd International Workshop on Logic Programming and Non-Monotonic Reasoning* (MIT Press, Cambridge, MA, 1993) 223-243.
- [58] S. Toulmin, *The Uses of Arguments* (Cambridge University Press, Cambridge, MA, 1958).
- [59] D.S. Touretzky, J.F. Horty and R.H. Thomason, A sceptic's menagerie: conflictors, preemptors, reinstaters and zombies in non-monotonic inheritance, in: *Proceedings IJCAI-91*, Sydney (Morgan Kaufmann, Los Altos, CA, 1991) 478-483.
- [60] A. Van Gelder, K.A. Ross and J.S. Schlipf, Unfounded sets and the well-founded semantics for general logic programs, in: *Proceedings ACM SIGMOD-SIGACT Symposium on Principles of Database Systems* (1988).
- [61] G. Vreeswijk, The feasibility of defeat in defeasible reasoning, in: *Proceedings KR-91*, Cambridge, MA (Morgan Kaufmann, Los Altos, CA, 1991).
- [62] J.H. You and R. Cartwright, Tractable argumentation semantics via iterative belief revision, in: *Proceedings ILPS-94* (MIT Press, Cambridge, MA, 1994) 239-253.
