---
title: "A generalised framework for dispute derivations in assumption-based argumentation"
authors: "Francesca Toni"
year: 2013
venue: "Artificial Intelligence"
doi_url: "https://doi.org/10.1016/j.artint.2012.09.010"
pages: "1-43"
---

# A generalised framework for dispute derivations in assumption-based argumentation

## One-Sentence Summary
Toni defines a parameterized family of X-dispute derivations for assumption-based argumentation (ABA), shows that GB-, AB-, and IB-dispute derivations are instances of it, and then extends the framework to structured X-dispute derivations that explicitly compute arguments and attacks, with soundness and completeness results for grounded, admissible, and ideal semantics. *(p.1, p.2)*

## Problem Addressed
Existing ABA proof procedures for grounded, admissible, and ideal semantics are useful but awkward to implement and deploy: their parameters are implicit, the procedures are separate variants of one another, and they compute sets of supporting assumptions while hiding the explicit arguments and attacks that applications usually need as justifications. *(p.1, p.2)* The paper addresses these issues by making the implementation choices explicit in one X-dispute derivation schema and by adding structured derivations that carry argument and attack information. *(p.2, p.8, p.16)*

## Key Contributions
- Defines X-dispute derivations, a single tuple-based proof-procedure framework parameterized by filtering mechanisms, an update operation for the pending failed-support component, and implementation-choice functions such as selection, member choice, and turn choice. *(p.8-p.11)*
- Shows that GB-, AB-, and IB-dispute derivations are recovered as specific choices of X-dispute parameters, so existing procedures are special cases rather than separate implementation targets. *(p.13-p.14)*
- Relates X-dispute derivations to proof procedures for logic programming, especially SLDNF and abductive refutations, while identifying the extra state used by X-dispute derivations: marking, accumulated culprits, the `F` component, and nested-proof mixing. *(p.15-p.16)*
- Defines structured X-dispute derivations with `Args` and `Att` components so that derivations compute explicit potential arguments and attacks in addition to assumption supports. *(p.16)*

## Study Design (empirical papers)

## Methodology
The paper is a formal-methods paper. It first reviews ABA, ABA semantics, dispute trees, p-acyclicity, and the existing GB-/AB-/IB-dispute procedures; then it abstracts their common state into X-dispute derivations; then it proves correspondence/soundness/completeness results for appropriate parameter instances and defines a structured variant that records arguments and attacks. *(p.2-p.16)*

## Key Equations / Statistical Models

An ABA framework is a tuple:

$$
\langle L, R, A, \overline{\ } \rangle
$$

Where `L` is a language, `R` is a set of inference rules, `A` is a set of assumptions with `A subseteq L`, and `\overline{\ }` is a total mapping from assumptions to contraries in `L`. Rules have syntax `sigma_0 <- sigma_1, ..., sigma_m`; `sigma_0` is the head and the remaining sentences are the body. *(p.3)*

An AB- or GB-dispute derivation state is:

$$
(P, O, D, C)
$$

Where `P` and `O` hold assumptions underlying some proponent and opponent arguments, `D` is the set of defenses, and `C` is the set of culprits. *(p.6)*

An IB-dispute derivation state is:

$$
(P, O, D, C, F)
$$

Where `F` holds sets of assumptions supporting opponent arguments that need a later `Fail` check. *(p.6)*

The `Fail` predicate is:

$$
Fail(S) \text{ holds iff there exists no admissible } A \subseteq A_0
\text{ such that for each } \sigma \in S, \text{ there exists an argument for } \sigma
\text{ supported by some } A' \text{ with } A' \subseteq A.
$$

Where `A_0` is the assumption set of the ABA framework; the paper notes that the computation of `Fail` is ignored here, because the Fail-dispute derivation notion from prior work can be deployed. *(p.6)*

The filtering mechanism parameters are:

$$
f_{DbyC}: \wp(L) \times \wp(L) \to \{true,false\}
$$

Filters defenses `R` by culprits `C`. *(p.8)*

$$
f_{DbyD}: \wp(L) \times \wp(L) \to \wp(L)
$$

Filters defenses `R` by defenses `D`. *(p.8)*

$$
f_{CbyD}: L \times \wp(L) \to \{true,false\}
$$

Filters a culprit candidate `sigma` by defenses `D`. *(p.8)*

$$
f_{CbyC}: \wp(L) \times \wp(L) \to \{true,false\}
$$

Filters culprits `S` by culprits `C`. *(p.8)*

Canonical filtering mechanisms satisfy:

$$
f_{DbyC}(R,C) = (R \cap C = \{\})
$$

$$
f_{CbyD}(\sigma,D) = (\sigma \notin D)
$$

$$
f_{DbyD}(R,D) \subseteq R
$$

$$
f_{CbyC}(S,C)=true \Rightarrow S \cap C \ne \{\}
$$

These constrain filtering to avoid using defenses already conflicting with culprits and to make repeated culprit/defense work explicit. *(p.8)*

The update parameter is:

$$
updt: \wp(\wp(A)) \times \wp(\wp(A)) \to \wp(\wp(A))
$$

Given `F, S subseteq wp(A)`, `updt(F,S)` is the `S`-update of `F`. Canonical update requires `updt(F,S) superseteq F`. *(p.9)*

Implementation-choice parameters are:

$$
sel: \wp(L) \to L
$$

$$
memberO: \wp(\wp(L)) \to \wp(L)
$$

$$
memberF: \wp(\wp(L)) \to \wp(L)
$$

$$
turn: N \to \{P,O,F\}
$$

Canonical choices require `sel(S) in S` when `S` is nonempty, `memberO(O) in O` and `memberF(F) in F` when nonempty, and `turn(i)=S` only when the chosen component is nonempty. *(p.9)*

X-dispute derivations are finite sequences:

$$
(P_0,O_0,D_0,C_0,F_0), ..., (P_i,O_i,D_i,C_i,F_i), ..., (P_n,O_n,D_n,C_n,F_n)
$$

With initialization `P_0={delta}`, `D_0=A cap {delta}`, `O_0=C_0=F_0={}`, termination `P_n=O_n=F_n={}`, and output support `Delta=D_n`. *(p.10-p.11)*

Structured X-dispute derivations use states:

$$
(P, O, D, C, F, Args, Att)
$$

Where `D`, `C`, and `F` are as before; `P` and `O` hold potential arguments rather than just assumptions; `Args` is the currently computed set of potential arguments; and `Att` is the currently computed binary attack relation. *(p.16)*

## Parameters

| Name | Symbol | Units | Default | Range | Page | Notes |
|------|--------|-------|---------|-------|------|-------|
| ABA framework language | `L` | set | required | any formal language | 3 | Component of ABA framework. |
| Inference-rule set | `R` | set | required | rules `sigma_0 <- sigma_1,...,sigma_m` | 3 | Rule heads and bodies define backward proof trees. |
| Assumption set | `A` | set | required | subset of `L` | 3 | Flat ABA restriction: no rule has an assumption as head. |
| Contrary mapping | overbar | function | required | total mapping `A -> L` | 3 | Maps each assumption to its contrary. |
| Proponent pending component | `P` | multiset/set | `{delta}` initially | sentences/premises | 6, 10 | Holds assumptions underlying proponent arguments or pending premises. |
| Opponent pending component | `O` | multiset/set | `{}` initially | sets/arguments | 6, 10 | Holds opponent-side attacks/potential arguments. |
| Defense set | `D` | set | `A cap {delta}` initially | assumptions | 6, 10 | Accumulates assumptions defended by proponent. |
| Culprit set | `C` | set | `{}` initially | assumptions | 6, 10 | Accumulates opponent assumptions attacked by proponent. |
| Failed-support check component | `F` | set of sets | `{}` initially | subsets of assumptions | 6, 10 | Used especially for IB/ideal reasoning and Fail checks. |
| Defense-by-culprit filter | `f_DbyC` | predicate | canonical: `R cap C = {}` | true/false | 8 | Blocks defense expansions containing existing culprits. |
| Defense-by-defense filter | `f_DbyD` | function | canonical subset of `R` | subset of `R` | 8 | Drops defenses already dealt with. |
| Culprit-by-defense filter | `f_CbyD` | predicate | canonical: `sigma notin D` | true/false | 8 | Avoids choosing an existing defense as culprit. |
| Culprit-by-culprit filter | `f_CbyC` | predicate | canonical implication over `S cap C` | true/false | 8 | Detects arguments already dealt with through existing culprits. |
| Pending failed-support update | `updt` | function | canonical: expands `F` | set of sets | 9 | Adds argument supports to be checked by `Fail`. |
| Selection function | `sel` | function | any element of nonempty input | `L` | 9 | Chooses a sentence/premise. |
| Opponent member chooser | `memberO` | function | any element of nonempty `O` | subset of `L` | 9 | Chooses an opponent argument/support. |
| Failed-support member chooser | `memberF` | function | any element of nonempty `F` | subset of `L` | 9 | Chooses an element of `F` for Fail checking. |
| Turn chooser | `turn` | function | any nonempty component | `P`, `O`, or `F` | 9 | Decides which activity occurs at step `i`. |
| Logic-programming turn choice | `LP-turn` | function | most recently modified nonempty `P` or `O` | `P`/`O` | 15 | Used to relate X-disputes to SLDNF. |
| Logic-programming selection choice | `LP-sel` | function | most recently introduced element | element of set | 15 | Used for LP instance of ABA. |
| Structured argument set | `Args` | set | currently computed arguments | potential arguments | 16 | Added by structured X-dispute derivations. |
| Structured attack relation | `Att` | binary relation | currently computed attacks | attacks between potential arguments | 16 | Added by structured X-dispute derivations. |

## Effect Sizes / Key Quantitative Results

Not applicable. This is a theoretical paper; no empirical effect sizes are reported in pages read so far.

## Methods & Implementation Details
- ABA arguments are proofs for a conclusion supported by assumptions, usually represented as finite trees with a root conclusion and leaves in the support set. For flat ABA, no assumption can appear as a rule head. *(p.3)*
- ABA support semantics are defined in assumption space: admissible sets do not attack themselves and attack every assumption set attacking them; preferred sets are maximal admissible sets; grounded sets are minimally complete; ideal sets are admissible and contained in all preferred sets. *(p.4)*
- The paper relies on the correspondence between acceptable assumption supports and acceptable sets of arguments: an admissible/grounded/ideal assumption set induces an admissible/grounded/ideal union of supported arguments, and conversely argument sets induce corresponding assumption supports. *(p.4)*
- Dispute trees are alternating proponent/opponent argument trees; for every proponent node all attackers appear as opponent children, while every opponent node has exactly one proponent child that attacks it. Grounded dispute trees must be finite; admissible dispute trees cannot label the same argument both proponent and opponent; ideal dispute trees are admissible and have no opponent node that itself has an admissible dispute tree. *(p.4)*
- P-acyclicity is defined over the dependency graph of the assumption-deleted framework `AF+`; top-down dispute derivations rely on p-acyclicity for completeness because it rules out cycles in positive dependency expansion. *(p.5)*
- Existing GB-, AB-, and IB-dispute derivations manipulate sets/multisets of assumptions, not explicit arguments; their filtering prevents self-attack and repeated work. *(p.5-p.7)*
- X-dispute derivations make explicit four implementation-choice classes that were implicit in GB-/AB-/IB-derivations: selection from `P`/`O`, choosing an element of `C`, choosing an element of `F`, and choosing which activity/turn to perform. *(p.7-p.8)*
- Figure 3 gives the decision-tree control flow for X-disputes: if `P`, `O`, and `F` are empty, return defenses `D`; otherwise use `turn` to operate on `P`, `O`, or `F`; `P` can drop assumptions and start attacks, or unfold non-assumption premises using rules; `O` can ignore/mark assumptions, move supports to `F`, expand culprits, or start counter-attacks; `F` performs Fail checks. *(p.10-p.12)*
- Cases 1(ii) and 2(i)(c) in Definition 4.6 can require nondeterministic choices, creating implementation backtracking points: rule choice for expanding a premise and choice whether to ignore an assumption or attack it. *(p.12)*
- GB-, AB-, and IB-choices differ mainly in `f_DbyD`, `f_CbyC`, and `updt`; the resulting X-dispute instances inherit the prior soundness/completeness results for their semantics. *(p.13-p.14)*
- Logic programming is represented as flat ABA with language made from the Herbrand base plus default negations, assumptions `not p`, and contrary `not p` mapped to `p`; grounded ABA corresponds to well-founded semantics, admissible ABA to admissible LP semantics, and ideal ABA to ideal LP semantics. *(p.15)*
- X-dispute derivations differ from SLDNF and abductive refutations by using marking, accumulated culprits, the `F` component, and nested proof mixing; Toni notes no known computational mechanism for ideal semantics in logic programming, but IB/X-dispute choices can be used for that purpose. *(p.16)*

## Figures of Interest
- **Fig. 1 (p.3):** Example argument trees for Example 2.1: argument `a` for `p` supported by `{a}` via `p <- q,a` and `q <- true`, and argument `b` for `r` supported by `{b}`.
- **Fig. 2 (p.5):** Four dispute trees for Example 2.2 showing when the tree is grounded/admissible/ideal, admissible but infinite, admissible but not grounded/ideal, and not acceptable under the considered semantics.
- **Fig. 3 (p.10):** High-level decision tree for X-dispute derivations, with diamonds as control decisions and rectangular boxes as commands; the numbered links map to Definition 4.6 cases.

## Results Summary
- Proposition 5.1: X-dispute derivations with GB-choices exist for support `Delta` for `delta` iff GB-dispute derivations of defense set `Delta` exist for `delta`. *(p.13)*
- Proposition 5.2: X-dispute derivations with AB-choices exist for support `Delta` for `delta` iff AB-dispute derivations of defense set `Delta` exist for `delta`. *(p.14)*
- Proposition 5.3: X-dispute derivations with IB-choices for support `Delta` for `delta` are IB-dispute derivations of ideal support `Delta` for `delta`, and vice versa. *(p.14)*
- Corollary 5.1: Under GB-choices, an X-dispute support `Delta` is admissible and contained in the grounded set of assumptions, and there exists `Delta' subseteq Delta` supporting an argument for `delta`. *(p.14)*
- Corollary 5.2: Under AB-choices, an X-dispute support `Delta` is admissible, and some `Delta' subseteq Delta` supports an argument for `delta`. *(p.14)*
- Corollary 5.3: Under AB-choices, a preferred set `Delta*` exists with `Delta subseteq Delta*` and an argument for `delta` supported by some `Delta' subseteq Delta*`. *(p.15)*
- Corollary 5.4: Under IB-choices, `Delta` is contained in the ideal set of assumptions and some `Delta' subseteq Delta` supports an argument for `delta`. *(p.15)*
- Proposition 5.4: With GB-choices plus LP `turn` and `sel`, X-dispute derivations correspond to SLDNF derivations. *(p.16)*
- Proposition 5.5: With AB-choices plus LP `turn` and `sel`, X-dispute derivations correspond to abductive refutations. *(p.16)*

## Limitations
- The early sections identify implementation friction in prior dispute derivations but do not yet give an executable algorithm; X-dispute derivations are a formal schema requiring parameter instantiation. *(p.2, p.8-p.12)*
- The paper explicitly ignores computation of `Fail` in Definition 3.1 and delegates it to the existing Fail-dispute derivation machinery. *(p.6)*
- Rule choice and whether to ignore or attack assumptions remain nondeterministic backtracking points in X-dispute construction. *(p.12)*

## Arguments Against Prior Work
- Prior GB-, AB-, and IB-dispute derivations use implicit parameters even though implementations must instantiate those parameters and the choices affect behavior. *(p.2)*
- The three existing derivation kinds are variations for different semantics, but still require separate implementation effort. *(p.2)*
- Existing derivations lose the dialectical structure because they track only some assumptions underlying arguments rather than explicit arguments and attacks. *(p.2, p.8)*

## Design Rationale
- Use a common tuple shape `(P,O,D,C,F)` because it generalizes the state already present in IB-dispute derivations and can represent GB/AB behavior by suitable parameter choices. *(p.8-p.11)*
- Keep filtering, update, and implementation choices as parameters so the same abstract derivation can instantiate prior proof procedures and expose implementation decisions. *(p.8-p.9)*
- Add `Args` and `Att` only for structured X-disputes because the base X-dispute framework should preserve the assumption-level correspondence with existing derivations, while structured derivations serve applications that need explicit justifications. *(p.16)*

## Testable Properties
- A purported ABA framework instance must provide a language, inference rules, assumptions, and a total contrary mapping for assumptions. *(p.3)*
- For flat ABA, no assumption may be the head of an inference rule. *(p.3)*
- For a successful X-dispute derivation, the final `P_n`, `O_n`, and `F_n` components are empty and the returned support is `D_n`. *(p.10-p.11)*
- Canonical `sel`, `memberO`, `memberF`, and `turn` choices may only choose from nonempty inputs. *(p.9)*
- Under GB-choices, the `F` component and marking play no semantic role because `updt` leaves `F` empty. *(p.13)*
- Under AB-choices, `f_CbyC` differs from GB choices and captures the additional culprit-by-culprit filtering used in AB-disputes. *(p.13-p.14)*
- Under IB-choices, `updt(F,S)=F union S`, so `F` can accumulate supports for later Fail checks. *(p.14)*

## Relevance to Project
This paper is directly relevant to an argumentation/proof-procedure implementation because it separates the abstract ABA dispute state from parameter choices, making it possible to encode one reusable derivation engine with pluggable semantics-specific behavior. The structured variant is especially relevant for systems that must emit provenance-bearing arguments and attacks rather than only final assumption supports. *(p.8-p.16)*

## Open Questions
- [ ] How should this codebase represent the X-dispute tuple and the structured `Args`/`Att` extension without duplicating separate GB/AB/IB engines? *(p.8-p.16)*
- [ ] Which canonical parameter choices are required for the project's target semantics, and which should be exposed as implementation strategy hooks? *(p.8-p.15)*
- [ ] How should `Fail` be implemented or delegated if ideal semantics are needed? *(p.6, p.14-p.16)*

## Additional Page-Image Extraction, pp.17-26

### Structured Potential Arguments and Labels
- A single proof tree can be represented by different potential arguments. For an assumption `alpha in A`, both `{} |-_{alpha} alpha` and `{alpha} |-_{empty} alpha` are potential arguments for `alpha`. *(p.17)*
- A potential argument may produce no actual argument, one actual argument, or multiple actual arguments depending on the available inference rules. Example: with `A={a,b,c}` and `R={p <- a,q} union R'`, `{a} |-_{q} p` produces no actual argument if `R'={}`, one actual argument `{a} |-_{empty} p` if `R'={q <-}`, and two actual arguments `{a,b} |-_{empty} p` and `{a,c} |-_{empty} p` if `R'={q <- b; q <- c}`. *(p.17)*
- Labels are introduced for potential arguments: `Args` contains expressions `l : A |-S sigma`; `Att` contains expressions `l -> l'`; `P` and `O` contain expressions `l : A |-S sigma -> l'` meaning that the labelled potential argument attacks another labelled argument. *(p.17)*
- `newLabel()` returns a fresh label; `newLabel(l)` returns a fresh label of the form `l(...)`; a special label `emptyset` marks the initial claim argument as not attacking any prior argument. *(p.17)*
- Structured X-dispute derivations eliminate the need for explicit marking by representing potential arguments in `P` and `O`: marked versus unmarked support is encoded in the potential-argument notation. *(p.17)*
- Structured derivations interleave construction and semantic evaluation. Potential arguments remain in `P`/`O`; when evaluated they are removed from `P`/`O` and added to `Args`, with `Att` modified as needed. *(p.17)*

### Structured X-Dispute Definition Details
- Structured derivations add `memberP` to choose a labelled potential argument in `P`; `memberO` in the structured case chooses a labelled potential argument rather than only a support set. Canonicality requires `memberO(O) in O` when `O` is nonempty and `memberP(P) in P` when `P` is nonempty. *(p.17)*
- A successful structured X-dispute derivation is a finite sequence `(P_i,O_i,D_i,C_i,F_i,Args_i,Att_i)` ending with `P_n=O_n=F_n={}`, output support `Delta=D_n`, output arguments `Args=Args_n`, and output attacks `Att=Att_n`. *(p.17-p.18)*
- Initial structured state has `P_0={l_1:{}|-_{delta} delta -> emptyset}` for `l_1=newLabel()`, `D_0=A cap {delta}`, and `O_0=C_0=F_0=Args_0=Att_0={}`. *(p.18)*
- Case 1, proponent turn: if the selected premise is an assumption, the derivation marks/moves it by adding a new attacker obligation in `O`, updating `Args` and `Att`, and preserving `D`, `C`, and `F`; if the selected premise is not an assumption, a rule `sigma <- R` may unfold it, adding new potential arguments, adding assumptions in the rule body to `D`, and updating `Args`/`Att`. *(p.18)*
- Case 2, opponent turn: if the selected premise is an assumption it may be ignored, moved to `F` as already dealt with, or made a new culprit and used to start a counter-attack in `P`; if the selected premise is not an assumption, all applicable rule unfoldings are split according to culprit filtering into newly pursued opponent arguments and failed/dealt-with supports. *(p.18-p.19)*
- Case 3, failed-support turn: if `turn(i)=F_i`, `memberF(F_i)=S`, and `Fail(S)` holds, then the derivation removes `S` from `F` and leaves the other components unchanged. *(p.19)*
- The support and dialectical structure computed by a structured X-dispute derivation are `(D_n, (Args_n, Att_n))`; the culprits computed are `C_n`. *(p.19)*

### Figures and Examples, pp.20-22
- **Fig. 4 (p.20):** Structured decision tree extending Fig. 3. The main changes are choosing p-arguments from `P`/`O`, returning the dialectical structure `(Args, Att)`, moving supports of p-arguments to `F`, adding full new p-arguments to `O`, and modifying `Args`/`Att`.
- **Fig. 5 (p.21):** Structured X-dispute derivation for GB-choices in Example 6.1. It computes support `{a,c}` for `p`, `Args_6={l_1:{a}|-empty p, l_2:{b}|-empty q, l_3:{c}|-empty r}`, and `Att_6={l_1->emptyset, l_2->l_1, l_3->l_2}`. *(p.21)*
- **Fig. 6 (p.22):** Structured X-dispute derivation for IB-choices on the same Example 6.1; it adds a final step obtained by case 3 after carrying `{b}` in `F`. *(p.22)*
- **Fig. 7 (p.22):** Larger structured derivation for Example 6.2 with support `{a,f}` for `p`, showing multiset-sensitive behavior and how some choices valid for AB/IB are not valid for GB because GB filtering rejects some rule bodies containing existing culprits. *(p.21-p.22)*
- Example 6.1 also shows a failed attempt to derive `q`: the sequence reaches a nonempty `P_4` and cannot be extended to a successful structured derivation. *(p.21)*
- Example 6.2 shows that an IB-choice counterpart can have different `F` components; if `F_11={{c},{b,r},{c,t}}` and `Fail({c})` does not hold because `{c,e}` is admissible, the sequence cannot extend to a successful structured derivation for IB-choices. *(p.23)*

### Soundness of Structured X-Dispute Derivations
- Section 7 first proves support soundness by using a one-to-one correspondence between ordinary X-dispute derivations and structured X-dispute derivations; then it studies soundness of the computed dialectical structure `(Args, Att)`. *(p.23)*
- Theorem 7.1: a structured X-dispute derivation of support `Delta` and dialectical structure `(Args,Att)` for `delta` exists for some choices of parameters iff an ordinary X-dispute derivation of support `Delta` for `delta` exists for some choices of parameters. *(p.23)*
- Corollary 7.1: if a structured derivation exists, then under GB-choices `Delta` is admissible and contained in the grounded set and supports an argument for `delta`; under AB-choices `Delta` is admissible, extends to some preferred set, and supports an argument for `delta`; under IB-choices `Delta` is contained in the ideal set and supports an argument for `delta`. *(p.23)*
- Definition 7.1 maps a computed dialectical structure `(Args,Att)` into a labelled potential-argument tree `T*(Args,Att)`: its root is the potential argument labelled `l` such that `l -> emptyset in Att`, and children follow attack-label edges `l_M -> l_N`. *(p.23)*
- Trees `T*(Args,Att)` may not themselves be dispute trees because they can contain non-actual arguments. The paper therefore first expands potential arguments into actual arguments, then prunes labels into a dialectical forest, and then expands filtered/dealt-with subtrees to prove admissible/ideal soundness. *(p.23-p.24)*
- Definition 7.2 expands a potential argument `A |-S sigma` with nonempty `S` into a proof for `sigma` supported by `A union B`, where `B` is the union of supports for proofs of every sentence in `S`. *(p.24)*
- Definition 7.3 constructs the actual dialectical structure `Actual(Args,Att)` by replacing potential non-actual arguments that can be expanded with actual arguments, removing potential non-actual arguments that cannot be made actual, and rewriting attack edges to match the surviving actual arguments. *(p.24)*
- Proposition 7.1: if the selection function is patient, meaning it selects an assumption only when `S-A` is empty, then the actual dialectical structure equals the originally computed dialectical structure. Example 6.1 uses a patient selection function, while Example 6.2 does not. *(p.24)*
- Definition 7.4 turns the actual dialectical structure into a dialectical forest: roots are actual arguments attacking `emptyset` or actual arguments that attack no existing actual argument; child links follow actual attack labels. The pruned dialectical forest removes the labels. *(p.25)*
- Proposition 7.2: with a patient selection function, the dialectical forest is exactly the single tree `T*(Args,Att)`. *(p.25)*
- Theorem 7.2: for GB-choices, every tree in the pruned forest is a grounded dispute tree for the argument at its root, and there exists a grounded dispute tree in the forest for an argument for the input sentence `delta`. *(p.25-p.26)*

### Expanded Dialectical Forest for AB/IB Choices
- For AB- or IB-choices, the pruned forest may not itself be a set of admissible/ideal dispute trees; Fig. 10's right-hand tree fails dispute-tree conditions because some leaves that should be opponent nodes have no children, and one proponent leaf is attacked by three arguments but has no children for those attackers. *(p.26)*
- The missing children arise from `f_DbyD` and `f_CbyC` filtering under AB/IB choices. Adding the filtered arguments can yield a dispute tree, but the resulting tree may be infinite and reuses nodes already present in the forest. *(p.26)*
- Lemma 7.1: for AB/IB choices, every leaf in the pruned forest holding an attackable argument has a matching node in the forest with an argument for the contrary of one of its support assumptions, with parity depending on the leaf level. This supplies the expansion witness called `arg_F(alpha)`. *(p.26)*
- Definition 7.5 constructs an expanded dialectical tree by iteratively adding, to all attackable leaves, all `arg_F(alpha)` children for support assumptions if the leaf is at odd level and one `arg_F(alpha)` child for a culprit assumption if the leaf is at even level. The expanded forest is the set of all such limits. *(p.26)*

## Additional Page-Image Extraction, pp.27-43

### Soundness, Completeness, and Other Semantics
- Theorem 7.3: for AB- or IB-choices, every tree in the expanded forest of the pruned forest is an admissible or ideal dispute tree respectively, and there exists an admissible or ideal dispute tree in that expanded forest for an argument for the queried sentence. Thus each finite pruned tree can represent a possibly infinite admissible/ideal dispute tree. *(p.27)*
- Section 8 gives completeness for p-acyclic ABA frameworks over finite languages. The p-acyclicity restriction ensures arguments, or finite failure to compute arguments, can be obtained top-down; dropping it would require loop-checking to detect finite failure to compute an X-dispute argument. *(p.27, p.29)*
- Theorem 8.1: if a p-acyclic finite-language ABA framework has an argument `a` for `delta` supported by `Sigma`, and a grounded/admissible/ideal argument set `A` contains `a`, then an X-dispute derivation exists with GB-/AB-/IB-choices respectively and support `Delta` such that `Sigma subseteq Delta` and `Delta subseteq Asm(A)`. *(p.27)*
- Corollary 8.1 transfers Theorem 8.1 to structured X-dispute support via Theorem 7.1: a structured X-dispute derivation exists with the same support constraints. *(p.27)*
- Theorem 8.2: for grounded semantics, if an argument for `delta` and a grounded dispute tree `T` rooted at that argument exist, then there is a structured X-dispute derivation whose computed dialectical structure has `T*(Args,Att)=T`. *(p.27)*
- Theorem 8.3: for admissible/ideal semantics, if an admissible/ideal dispute tree `T` exists, then a structured X-dispute derivation exists whose expanded forest contains an admissible/ideal dispute tree `T'` with the same trimmed version as `T`; the argument defense set of `T'` is a subset of the defense set of `T`. *(p.27-p.28)*
- Example 8.1 shows that not every admissible dispute tree can be obtained for AB-choices: in the given ABA framework, three admissible trees exist with defense sets `{a,c}`, `{a,d}`, and `{a,c,d}`, but no structured AB-derivation yields the third expanded forest because `f_CbyC` blocks it. With IB-choices a similar sequence can be obtained after carrying `F` and checking `Fail({b})` and `Fail({a,b})`; with GB-choices the third tree can also be constructed. *(p.27-p.29)*
- Section 9 extends structured X-dispute results to preferred semantics. Support soundness and completeness follow from the admissible case because every preferred set is admissible and every admissible set is contained in a preferred set. *(p.29-p.30)*
- Corollary 9.1: under AB-choices, a structured derivation of support `Delta` and dialectical structure exists only if some preferred assumption set `A*` contains `Delta`, and some `Delta' subseteq A*` supports an argument for `delta`. *(p.29)*
- Corollary 9.2: completeness for preferred support holds under p-acyclic finite-language ABA if a preferred argument set contains an argument for `delta`; a structured derivation exists with `Sigma subseteq Delta` and `Delta subseteq Asm(A)`. *(p.29)*
- Definition 9.1: a preferred dispute forest is a set of admissible dispute trees whose proponent-node argument set is preferred. Corollary 9.3 gives soundness for preferred dialectical structure; Corollary 9.4 gives completeness by producing a preferred dispute forest contained in the expanded forest. *(p.29-p.30)*
- Complete semantics are also covered: since every preferred set is complete and every admissible set is contained in a complete set, soundness and completeness can be given for AB-choices under complete semantics. GB-choices are sound but incomplete for complete semantics because the grounded set is complete but not every complete set is grounded. *(p.30)*

### Related Work and Positioning
- X-dispute derivations generalize AB-dispute derivations and GB-/IB-dispute derivations by obtaining each as an instantiation with appropriate parameter choices; the generalized framework also extends prior completeness results for p-acyclic ABA frameworks. *(p.30)*
- Structured X-dispute derivations resemble structured AB-dispute derivations for admissible semantics, but differ because structured AB-disputes can arbitrarily hang arguments below opponent arguments after successful filtering, whereas structured X-disputes compute a dialectical structure during the proponent/opponent construction. *(p.30)*
- Toni emphasizes that no prior formal result had been proven for the GB-style variant of structured AB-dispute derivations, whereas the IB instance of structured X-dispute derivations is new. *(p.30)*
- Kakas and Toni proof procedures vary parameters roughly corresponding to filtering and operate over dispute trees for admissibility, groundedness, weak stability, and acceptability for logic programs, but do not address ideal semantics. *(p.30)*
- DeLP is contrasted as a logic-programming approach for warranted/unwarranted/undecided query answers; ABA can model defeasible and strict rules and preferences, but X-dispute derivations focus on positive query answering and return a support set plus, for structured derivations, a dialectical structure. *(p.30)*
- Abstract-argumentation computational models fall into proponent-opponent games, labelling algorithms, and answer-set-programming methods. Structured X-dispute derivations fall in the game family but are defined for ABA, can apply even when the corresponding abstract argumentation framework is infinite, and exploit shared assumptions between different arguments. *(p.31)*
- Other engines by Bryant et al., South et al., and Efstathiou and Hunter are compared as implementation/proof-tree/argument-generation approaches; Toni's focus is the interleaving of construction of dispute trees, arguments, and attacks for grounded, admissible, and ideal semantics. *(p.31)*

### Conclusions and Future Work
- The paper concludes that X-dispute and structured X-dispute derivations explicitly isolate design choices hidden in GB-/AB-/IB-dispute derivations and support a unified, modular implementation path. *(p.31)*
- For logic programming, the framework goes beyond existing procedures by supporting query answering under ideal semantics and computing dialectical justifications, not only support sets. *(p.31)*
- Structured derivations provide justified query answering for all ABA instances, including logic programming, by computing arguments/counterarguments and a dialectical structure. *(p.31)*
- Future work directions: add justifications for queries that cannot be answered positively; build modular implementations with graphical interfaces to instantiate parameters and visualize the debate/dialectical structure; experiment with GB/IB parameter choices and distributed/cloud implementations; and infer heuristics from ABA structural characteristics such as the maximum number of rules for contraries. *(p.31-p.32)*
- The conclusion also notes that parameterization enables experiments that commit to a specific choice of parameters without risking computational explosion in the formal framework itself. *(p.32)*

### Appendices
- Appendix A restates GB-, AB-, and IB-dispute derivations using the convention that omitted tuple elements are unchanged. This appendix is the bridge for the correspondence proofs in the body. *(p.32-p.34)*
- Definition A.1 gives GB-dispute derivations as finite quadruple sequences `(P_i,O_i,D_i,C_i)` with initialization `P_0={delta}`, `D_0=A cap {delta}`, `O_0=C_0={}`, termination `P_n=O_n={}`, and `Delta=D_n`; selected proponent assumptions create opponent contrary obligations, non-assumptions unfold by rules whose bodies do not intersect culprits, and selected opponent assumptions can be ignored or made culprits. *(p.32)*
- Definition A.2 gives AB-dispute derivations with similar quadruples but different defense/culprit filtering: rule expansion removes already defended assumptions from the body, and variants of case 2(i)(c) handle whether the contrary is in the current culprits/defenses. The paper uses an equivalent variant that eliminates a further filtering case for modest performance improvement. *(p.33)*
- Definition A.3 gives IB-dispute derivations as tuple sequences `(P,O,D,C,F)` with marking. It adds `F` updates for supports needing later `Fail` checks and includes a case where selecting `S in F` requires `Fail(S)` and removes `S` from `F`. The paper uses an equivalent simplified case 2(i)(c). *(p.33-p.34)*
- Appendix B proves Section 7. Theorem 7.1 is shown constructively in both directions: from structured to ordinary X-disputes by mapping labelled potential arguments in `P`/`O` to ordinary marked/unmarked sentence sets using `m_P` and `m_O`, and from ordinary X-disputes to structured X-disputes by inverse construction while building `Args` and `Att`. *(p.34-p.36)*
- Lemma B.1: nodes in the dialectical forest are odd-level iff they hold proponent arguments and even-level iff they hold opponent arguments. *(p.37)*
- Lemma B.2: every attack on a proponent argument has an even-level node somewhere in the forest holding the attacking argument. Lemma B.3 strengthens this for GB-choices: the attacker labels a child of the proponent argument in the same tree. *(p.37)*
- Lemma B.4: every opponent argument in the forest has some odd-level node holding an argument that attacks it. Lemma B.5 strengthens this for GB-choices: the attacking argument is a child of the opponent argument in the same tree. *(p.38)*
- Lemma B.6: no actual argument can be both a proponent and opponent argument in the actual dialectical structure; the proof uses canonical `f_DbyC` and `f_CbyD` constraints to derive contradiction if the same actual argument appears on both sides. *(p.38)*
- Theorem 7.2 proof: every tree in the GB pruned forest is finite and satisfies dispute-tree conditions via Lemmas B.1, B.3, B.5 and structured-derivation/forest definitions; the root argument for `delta` yields a grounded dispute tree. *(p.38)*
- Theorem 7.3 proof for AB choices establishes admissible dispute trees in the expanded forest using Lemmas B.1, B.2, B.4, B.6 and expansion construction. For IB choices, the ideal case relies on `Fail` contradiction: if an even-level node had an admissible dispute tree, the support added to `F` could not have passed `Fail`. *(p.39)*
- Appendix C proves Section 8 completeness. For GB-choices, it constructs an X-dispute derivation from a grounded dispute tree using left-most depth-first node order, supports, culprit assignments, and sequences `seq(N_i)`/`e_seq(N_i)`. The computed support is exactly `Asm(A')`. *(p.39-p.40)*
- Theorem 8.2 adapts the Appendix C construction to structured X-disputes by adding labelled potential arguments and attacks so that the computed `T*(Args,Att)` is the original grounded dispute tree. *(p.40-p.41)*
- Theorem 8.3 uses a trimmed tree and conditions about already defended assumptions and existing culprits to obtain a structured X-dispute whose expanded forest contains a tree with the same trimmed version; soundness of structured derivations gives admissibility of that tree. *(p.41-p.42)*

### References Observed
The reference list spans pp.42-43 and includes 46 entries. Key references for follow-up are Dung et al. on ABA/dispute derivations and ideal skeptical argumentation, Bondarenko et al. on the ABA framework, Dung's abstract argumentation foundations, Toni's work on assumption-based argumentation for defeasible reasoning, Garcia/Toni on computing arguments and attacks in ABA, Kakas/Toni on acceptability semantics, and Prakken's abstract framework for structured arguments. *(p.42-p.43)*

## Related Work Worth Reading
- Dung et al. and Bondarenko et al. on ABA foundations and dispute derivations are repeatedly used as the base references for ABA semantics, dispute trees, and GB/AB/IB proof procedures. *(p.1-p.6)*
- Prior structured AB-dispute derivations are the immediate precursor to structured X-dispute derivations. *(p.2, p.16)*
