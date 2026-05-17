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

## Related Work Worth Reading
- Dung et al. and Bondarenko et al. on ABA foundations and dispute derivations are repeatedly used as the base references for ABA semantics, dispute trees, and GB/AB/IB proof procedures. *(p.1-p.6)*
- Prior structured AB-dispute derivations are the immediate precursor to structured X-dispute derivations. *(p.2, p.16)*
