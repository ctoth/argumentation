---
title: "Developing the Abstract Dialectical Framework"
authors: "Sylwia Polberg"
year: 2017
venue: "PhD Thesis, Vienna University of Technology"
doi_url: "https://doi.org/10.34726/hss.2017.47655"
institution: "Technische Universität Wien"
supervisor: "Stefan Woltran"
pages: 711
produced_by:
  agent: "claude-opus-4-7"
  skill: "paper-reader"
  status: "stated"
  timestamp: "2026-04-28T07:17:22Z"
---
# Developing the Abstract Dialectical Framework

## Status

All 15 chunks (0-49, 50-99, 100-149, 150-199, 200-249, 250-299, 300-349, 350-399, 400-449, 450-499, 500-549, 550-599, 600-649, 650-699, 700-710) have been fully ingested into this synthesis. Page-number convention is **PDF page index** matching `page-NNN.png` filenames; printed thesis pagination runs ~13 lower (e.g., PDF p.150 = printed p.137). Citations preserve `*(p.N)*` with PDF index throughout. The thesis body ends at PDF p.710 (printed p.697) with the close of §4.10 and Theorem 4.10.18; Chapter 5 (Related Work, p.463), Chapter 6 (Conclusions, p.466), Bibliography (p.472), and Proof Appendix (A1-A11, p.484-710) are also captured.

## One-Sentence Summary

A unified algebraic and computational treatment of nine abstract argumentation frameworks (AF, SETAF, AFRA, EAF, EAFC, BAF, AFN, EAS, ADF) that gives ADFs a complete extension-based semantics family (cc/aa/ac/ca₁/ca₂), a complexity table for it, a normal-form / subclass taxonomy, and ~90 inter-framework Translations classified along strength × functional × syntactical × semantical × computational axes.

## Problem Addressed

Prior abstract argumentation work was framework-balkanized: each new relation type (necessity, evidence, recursive attack, set-attack, defense-attack, support) led to a new framework with its own semantics, with **no systematic way** to compare expressiveness, share solvers, or know which inter-framework translations preserved which semantics. The original BW10 ADF extension semantics worked only on bipolar ADFs and "did not always produce desired results"; later labeling semantics (BES+13/Str13a) had opacity, self-influence under cycles, and info-vs-subset-maximality mismatches under support. For propstore: argumentation, ATMS, and Dung-AF construction all need a principled bridge between source-of-truth claim graphs and a chosen reasoning surface; this thesis is the catalogue of which bridges exist, which are exact, and where impossibility theorems block translation.

## Key Contributions
- New **extension-based ADF semantics** (cf, acy-cf, mod, stb, grd, acy-grd, plus admissible / preferred / complete in five flavors cc, aa, ac, ca₁, ca₂) replacing the BW10 semantics that worked only on bipolar ADFs.
- **Complete complexity table** (Table 3.5, p.122) for ADF reasoning across these families: verification, existence, credulous, skeptical, ranging from P up to Π₄^P.
- **AADF⁺ subclass** of "positive-dependency-acyclic" ADFs where all flavors collapse to a single semantics — used as a sanity zone for translation correctness.
- **Catalogue of ~90 framework translations** with formal classification along strength (exact/strong/faithful/⊆-weak/⊇-weak), functional (full/source-subclass/target-subclass/injective/overlapping), syntactical (argument-domain / structure preserving), semantical (generic/specialized; semantics-domain preserving), and computational (modular / ⊗-modular / ⊕-modular; structural / semi-structural / semantical) axes.
- **Pattern catalogue** for translation construction: **basic**, **coalition**, **attack-propagation**, **defender** (plus chained / hybrid).
- **Framework normal forms** (minimal, redundancy-free, cleansed, weakly/relation/strongly valid, bypass-consistent, self-attacker-consistent) with semantics-preservation theorems and structural characterizations (e.g., AFN strongly valid ⇔ DAG; EAS strongly valid ⇔ rooted DAG with η root; ADF strongly valid ⇔ positive-dependency graph DAG).
- **Impossibility theorems** mapping the genuine expressivity hierarchy: e.g., no full exact SETAF→AF, no full exact AFN→AF (stable), no full exact EAS→AF, no full exact EAF→{AF,SETAF,AFRA,AFN}, no full exact ADF→AF for any analyzed semantics.
- **EAFC** (collective-defense EAFs from MP10) embedded in the chain; **CKR-style** "overpowering support" recognized as the only non-bounded-hierarchical EAF→ADF route.
- **EAS→ADF, AFN→ADF** translations producing acceptance conditions in canonical CNF/DNF form (`att_a ∧ sup_a`) suitable for Z3 / Boolean reasoning.

## Methodology

The thesis is built on three primary technical devices:

1. **Tarski reducts** of acceptance conditions (`D^E = (E, L^E, C^E)` with `C_e^E = φ_e[b/f : b ∉ E]`) — used to define stable models and the BES+13 labeling semantics.
2. **Three-valued labelings** under information ordering `u ≤ᵢ t, u ≤ᵢ f`, with the characteristic operator `Γ_D(v)(a) = ⊓_{w ∈ [v]_2} w(φ_a)` (Def 3.2.1).
3. **Positive-dependency evaluations** as triples `(F, sequence, B)`: standard, partially-acyclic, and acyclic (Defs 3.1.7–3.1.9). The pd-function `pd_E^D` assigns each `a ∈ E` a minimal decisively-in interpretation; soundness, maximal soundness, and acyclicity of the induced sequence give the technical hooks the entire ADF semantic taxonomy hangs from.

Onto these are layered:

- **Decisiveness via interpretations and via sets** (Def 3.1.4 vs Def 3.1.5 `acc/reb`): both representations are kept since extension-based semantics need set form, labeling semantics need interpretation form.
- **Three flavors of range** (Def 3.1.13 standard `E^Ran = E ∪ E^+`, Def 3.1.18 partially-acyclic `E^{p+}`, Def 3.1.20 / 3.1.15-deprecated acyclic `E^{a+}`). Lemma 3.1.21: `E^+ ⊆ E^{p+} ⊆ E^{a+}` for conflict-free `E`.
- **xy-classification** of admissible / complete / preferred families with `x = "inside" ∈ {a,c}` (acyclic vs cyclic accepted args) and `y = "outside" ∈ {a,c}` (acyclic vs cyclic rejection of attackers); `ca₁` (Pol14a, discard cyclic args independently) vs `ca₂` (Pol15, exception when cycle is internal to accepted set).
- **Characteristic operator ϒ_F** (Def 2.1.5 for AFs, generalized) plus framework-specific operators (`F_FN, F_ES, F_EF, F_EFC, F_FR, d-F_BF`) for support frameworks.
- **σ-correspondence proofs**: each translation is anchored by a Theorem stating `E σ-extension of source ⇔ casting(extension(target))` for σ in the listed semantics.
- **Translation classification engine** (Def 4.1.4 strength, 4.1.5 sub `⊑`, 4.1.6 casting types {identity, removal, addition, union, extraction}, 4.1.7 functional, 4.1.8 syntactical, 4.1.9 semantical, 4.1.12 computational, with `⊗`/`⊕` ADF combine operators).
- **Pattern taxonomy** (basic / coalition / attack-propagation / defender, plus hybrids and chained) defined in §4.1.3 (p.143–145, Table 4.2 p.145).
- **Framework normal-form pipeline** (§4.2): minimal → redundancy-free / cleansed → weakly valid → relation valid → strongly valid → consistency form (bypass / self-attacker), each translation classified.
- **Subclass taxonomy** (§4.2.5): SETAF binary, AFRA recursion-depth `Rec_n`, EAF/EAFC NDef/NSym/Bin/SCons, BAF NoSupp / support-acyclic / support-depth-n, AFN NSup/SBin/SSig/SEle/WSt, EAS ABin/ASig/SBin/SSig/AllSup/EvSup, ADF Dung-style / SETAF-style / EAFC-style / EAF-style / BADF / AADF⁺ / WV / RV / SV / Cln / RFree.

## Key Equations / Statistical Models

$$
F_F(E) = \{a \mid a \text{ is defended by } E \text{ in } F\}
$$
Where: AF characteristic function; grounded extension is the least fixed point of `F_F`. *(p.23)*

$$
E^{\mathrm{Ran}} = E \cup E^+,\quad E^+ = \{a \in A \mid \exists e \in E,\, (e,a) \in R\}
$$
Where: standard range and discarded set in Dung's framework. *(p.22, p.75)*

$$
\Gamma_D(v)(a) = \bigsqcap_{w \in [v]_2} w(\varphi_a)
$$
Where: `v` three-valued, `[v]_2` two-valued completions, `⊓` meet under information ordering, `φ_a` propositional acceptance condition. *(p.79)*

$$
acc(G,B) = \{r \in A \mid G \subseteq A' \subseteq (A \setminus B) \Rightarrow C_r(A' \cap par(r)) = in\}
$$
Where: ADF set-form decisive-in. `reb(G,B)` is the dual for decisive-out. *(p.70)*

$$
E^+ \subseteq E^{p+} \subseteq E^{a+}
$$
Where: discarded sets under standard, partially-acyclic, and acyclic ranges; equality of the latter two when `E` is pd-acyclic conflict-free. *(p.77, Lemma 3.1.21)*

$$
\Sigma_i^P = NP^{\Sigma_{i-1}^P},\quad \Pi_i^P = coNP^{\Sigma_{i-1}^P},\quad \Delta_i^P = P^{\Sigma_{i-1}^P}
$$
Where: polynomial hierarchy classes used throughout §3.7. *(p.110)*

$$
C_1 \otimes_s C_2 = \begin{cases} \varphi_s^1 \wedge \varphi_s^2 & s \in A_1 \cap A_2 \\ \varphi_s^1 & s \in A_1 \setminus A_2 \\ \varphi_s^2 & \text{otherwise} \end{cases}
$$
Where: ⊗ is conjunctive ADF combine on shared atoms; ⊕ is the disjunctive dual. Used to define ⊗-/⊕-modularity of translations. *(p.140)*

$$
R^{\mathrm{ind}}_{i} = \{R^{\mathrm{sup}}_{E},\ R^{\mathrm{sec}}_{E},\ R^{\mathrm{med}}_{E},\ R^{\mathrm{ext}}_{E}\mid E \subseteq R^{\mathrm{ind}}_{i-1}\},\quad R^{\mathrm{ind}}_{0} = \emptyset
$$
Where: BAF tiered indirect attacks. The four kinds are supported / secondary / mediated / extended attacks. *(p.46–47)*

$$
C_a = \mathit{att}_a \wedge \mathit{sup}_a,\quad \mathit{att}_a = \bigwedge_{tRa} \neg t,\quad \mathit{sup}_a = \bigwedge_{Z N a} \bigvee Z
$$
Where: AFN→ADF (Translation 69, p.378) acceptance condition synthesis: attackers as conjunction of negations, supporters as conjunction of disjunctions over support sets.

$$
C_a = \bigwedge_{b: (b,a) \in R} \mathit{att}^b_a,\quad \mathit{att}^b_a = \neg b \vee \bigvee D_{b,a}
$$
Where: EAF→ADF (Translation 47, p.301), `D_{b,a} = {c | (c,(b,a)) ∈ D}` defense attackers. EAFC version replaces `⋁ D_{b,a}` with `⋁_i ⋀ B_i`. *(p.301, p.313)*

$$
C_a = \mathit{att}_a \wedge \mathit{sup}_a,\quad \mathit{att}_a = \bigvee_{i=1}^{n} \neg B_i,\quad \mathit{sup}_a = \bigvee_{i=1}^{m} \bigwedge Z_i
$$
Where: EAS→ADF (Translation 80, p.411) — DNF over evidence support sets, NNF over group attackers. CNF↔DNF dual of AFN form. *(p.411)*

$$
PDG^D = (A, L'),\quad L' = \{(a,b) \mid \exists v \in \min\!\_dec(\textit{in}, b)\ \text{s.t.}\ a \in v^t\}
$$
Where: positive dependency graph; `D` strongly valid iff `PDG^D` is a DAG (Theorem 4.2.45). *(p.185)*

$$
SG^{FN} = (A, N'),\quad N' = \{(a,b) \mid \exists E \subseteq A,\ a \in E\ \text{s.t.}\ ENb\}
$$
Where: AFN support graph; FN strongly valid iff `SG^FN` is a DAG (Theorem 4.2.34). *(p.181)*

$$
SG^{ES} = (A, E'),\quad E' = \{(a,b) \mid \exists X \subseteq A,\ a \in X\ \text{s.t.}\ XEb\}
$$
Where: EAS support graph; ES strongly valid iff `SG^ES` is a rooted DAG with η as root (Theorem 4.2.39). *(p.183)*

$$
F_{def}^{SF} = (A',R'),\ A' = A \cup R \cup X',\ X' = \{x' \mid x \in A\}
$$
$$
R' = \{(x,x') \mid x' \in X'\} \cup \{(x',(X,y)) \mid (X,y) \in R, x \in X\} \cup \{((X,y),y) \mid (X,y) \in R\}
$$
Where: SETAF→AF defender construction (Translation 26, p.230). Each set attack `(X,y)` becomes a 4-node gadget. *(p.230)*

$$
\mathit{rep}(S, P^b, D_{b,a}) = \begin{cases} D_{b,a} & D_{b,a} \cap S = \emptyset \\ (D_{b,a} \setminus S) \cup \{e^b \mid e \in D_{b,a} \cap S\} & \text{otherwise} \end{cases}
$$
Where: bypass replacement function for inconsistency-origin arguments. EAF (single-argument) and EAFC (set-of-arguments) versions both exist. *(p.188, p.190, p.308, p.317)*

$$
\mathit{iclo\text{-}}F^{BF} = (A',R''),\ A' = A \cup S
$$
$$
R'' = R \cup \bigcup R' \cup \{(x,x) \mid x \in S\} \cup \{(b,(b,a)),\ ((b,a),a) \mid (b,a) \in S\}
$$
Where: inverse-closure attack-propagation–defender AF for BAF i-admissibility (Translation 54). Closure variant flips orientation: `(a,(b,a)), ((b,a),b)`. *(p.326–327)*

$$
ES^{BF} = (A \cup \{\eta\},\ R',\ E),\quad R' = \{(\{a\},b) \mid (a,b) \in R\}
$$
$$
E = \{(\{\eta\},a) \mid \nexists c.\ cSa\} \cup \{(S^a, a) \mid S^a = \{b \mid bSa\}\}
$$
Where: support-acyclic BAF→EAS (Translation 60). Singular EAS — entire support set of `a` is the supporter. *(p.342)*

## Parameters

### Frameworks and semantics

| Name | Symbol | Domain | Default | Range | Page | Notes |
|------|--------|--------|---------|-------|------|-------|
| Argument domain | U | universal set | — | — | 21 | Hosts argument identifiers |
| Framework type | T | {AF, SETAF, AFRA, EAF, EAFC, BAF, AFN, EAS, ADF} | — | — | 20 | Framework discriminator |
| AF semantics | σ | {cf, adm, comp, pref, grd, stb, sst, lab-…} | — | — | 22–25 | Both extension and 3-valued labeling |
| Three-valued labels | — | {in, out, undec} ≡ {t, f, u} | — | — | 25 | Information ordering u ≤ᵢ t, u ≤ᵢ f |
| BAF indirect attack collection | R' | ⊆ R^ind | analyst choice | — | 47 | Determines which indirect attacks count |
| BAF defense parametrisation | R'' | ⊆ R^ind | typically R' | — | 48 | May differ from R' (Fundamental Lemma fails when ≠) |

### ADF link types and semantics

| Name | Symbol | Domain | Default | Notes | Page |
|------|--------|--------|---------|-------|------|
| ADF link types | — | {supporting, attacking, redundant, dependent} | — | BADF iff every link is supporting or attacking | 67 |
| ADF semantics flavor | xy | {a, c}² | — | aa, ac, cc, ca₁, ca₂; plus three-valued labelings | 81 |
| pd-evaluation type | X | {standard, partially-acyclic, acyclic} | — | Used in §3.7 to parameterize verification | 71–73 |
| weak vs normal pd-evaluation | y | {w, n} | — | weak = full interps, normal = minimal decisively-in | 114 |
| Decisiveness direction | x | {in, out} | — | Used in Ver_dec^x | 111 |
| Range types | — | {standard, partially-acyclic, acyclic} | — | E^Ran, E^{p+}, E^{a+} | 75–77 |

### ADF subclasses

| Subclass | Symbol | Definition | Page |
|----------|--------|------------|------|
| Bipolar | BADF | Every link supporting or attacking | 67 |
| AADF⁺ | AADF^+ | Every standard evaluation has acyclic refinement | 102 |
| Weakly valid | WV^ADF | Every arg has acyclic pd-evaluation | 166 |
| Relation valid | RV^ADF | Every minimal decisively-in interp can build acyclic pd-eval | 175 |
| Strongly valid | SV^ADF | PDG^D is a DAG | 184 |
| Cleansed | Cln^ADF | Every arg has standard evaluation | 157 |
| Redundancy-free | RFree^ADF | All links non-redundant | 155 |
| Dung-style | ADF^AF | C_a(∅)=in, C_a(B)=out for nonempty B | 202 |
| SETAF-style | ADF^SETAF | C_a(∅)=in + monotone-out condition | 202 |
| EAFC-style | ADF^EAFC | One negated literal per clause | 202 |
| EAF-style | ADF^EAF | EAFC-style + unique negations | 202 |

### Translation classification taxonomy

| Axis | Values | Page |
|------|--------|------|
| Strength (per σ, per casting) | exact / strong / faithful / ⊆-weak / ⊇-weak / semantics-bijective | 130, 138 |
| Casting type | identity / removal / addition / union / extraction | 131–132 |
| Functional | full / partial=source-subclass / surjective / target-subclass / injective / overlapping | 134 |
| Syntactical | argument-domain preserving/altering/weakly-altering / argument-introducing/removing / relation-introducing/removing / induced-relation adding/removing / structure preserving | 134–135 |
| Semantical | generic (≥3 σ strong) / specialized / semantics-domain preserving/altering / faithful / exact | 137–139 |
| Computational | structural / semi-structural / semantical / modular / ⊗-modular / ⊕-modular / polynomial / polysize | 139–142 |
| Pattern | basic / coalition (Cl) / attack-propagation (AP) / defender (Def) / chained (Ch) / hybrid / unknown (?) | 143–145, Table 4.2 |

### Complexity classes used

| Class | Definition | Page |
|-------|------------|------|
| P | Polytime decision problems | 110 |
| NP, coNP, Σ_i^P, Π_i^P, Δ_i^P | Polynomial hierarchy | 110 |
| D^P | L₁ ∩ L₂ with L₁ ∈ NP, L₂ ∈ coNP (SAT-UNSAT-complete) | 110 |
| D_i^P | L = L₁ ∩ L₂ with L₁ ∈ Σ_i^P, L₂ ∈ Π_i^P | 110 |

## Algorithms / Procedures

### Characteristic operator ϒ_F (Dung AF) — Proposition 2.1.7 (p.23)
Iterative grounded extension:
1. Put each `a ∈ A` not attacked in `F` into `E`. If none new, return `E`.
2. Remove from `F` all (new) arguments in `E` and all arguments attacked by `E` (with adjacent attacks). Continue at Step 1.

### Three-valued characteristic operator Γ_D (ADF labeling) — Def 3.2.1 (p.79)
For three-valued `v: A → {t,f,u}`:
- For each `a`, evaluate `φ_a` over every two-valued completion `w ∈ [v]_2`.
- `Γ_D(v)(a) = ⊓_w w(φ_a)` where `⊓` is the information-ordering meet.
- `v` admissible iff `v ≤ᵢ Γ_D(v)`; complete iff fixed point; preferred iff ≤ᵢ-maximal admissible; grounded iff ≤ᵢ-least fixed point.

### Standard range computation — Def 3.1.13 (p.76)
1. `M := E`; `v_E(a) := t` for `a ∈ E`.
2. For every `b ∈ A \ M` decisively out w.r.t. `v_E`, set `v_E(b) := f`, add `b` to `M`.
3. Repeat (2) until fixed point. `E^+ := v_E^f`, `E^Ran := E ∪ E^+`.

### Acyclic grounded extension — Def 3.3.8 (p.85)
1. `v := ∅`.
2. For every `a` decisively in w.r.t. `v`, set `v(a) := t`.
3. For every `b` such that all acyclic pd-evaluations of `b` are blocked by `v`, set `v(b) := f`.
4. Repeat to fixed point. Acyclic grounded `:= v^t`.

### Stable model via reduct — Def 3.2.4 (p.80)
1. Take candidate `M ⊆ A`.
2. Build reduct `D^M` with `C_e^M = φ_e[b/f : b ∉ M]`.
3. Compute grounded labeling `gv` of `D^M`.
4. `M` is stable iff `M = gv^t`.

### Stable extension via pd-acyclic cf model — Theorem 3.3.3 (p.84)
Bypass reduct construction:
1. Find all models `E` of `D`.
2. For each, check if `E` is pd-acyclic conflict-free in `D`.
3. `E` is stable iff yes.

### Bypass argument construction — Defs 4.2.48–4.2.49 (p.187–188), Translation 13 (p.188), restated for EAF (p.308)
For source framework with arguments not strongly consistent:
1. For each argument `a` with non-empty inconsistency origin `O^a` (those that both attack and support `a`), generate bypass argument `a^b`.
2. `A' = A ∪ A^b`, where `A^b = {a^b | a ∈ O^E}`.
3. For each support `(B,a) ∈ N` (or defense `(B,(b,a)) ∈ D`), apply `rep(a, O^a, A^b, (B,a))` to substitute bypass arguments for inconsistency-origin arguments.
4. For each `a ∈ O^E`, add support `({a}, a^b)` to N (so `a^b` traces back to `a`).
5. Resulting framework is strongly consistent.

### Self-attacker consistency — Translation 15 (p.192)
Identical to bypass construction but additionally adds `(a^b, a^b) ∈ R'` for every bypass argument. Yields exactness at the cost of breaking stable in one direction.

### Witness/preview operators (xy-σ ADF semantics) — §3.3.4 (p.86–91)
- **cc-admissible** (Def 3.3.9): cf + every `e ∈ E` decisively in w.r.t. standard range `v_E`.
- **aa-admissible** (Def 3.3.10): pd-acyclic cf + every `e ∈ E` has an acyclic pd-evaluation whose blocking set is mapped to f by `v_E^a` (acyclic range).
- **ac-admissible** (Def 3.3.11): pd-acyclic cf + acyclic pd-evaluation blocked by standard range.
- **ca₁-admissible** (Def 3.3.12): cf + decisively in w.r.t. acyclic range `v_E^a`.
- **ca₂-admissible** (Def 3.3.12): cf + decisively in w.r.t. partially-acyclic range `v_E^p`.

### η-sentinel construction (EAS-targeting translations) — Translation 22 (AF→EAS, p.216), Translation 30 (SETAF→EAS, p.241), Translation 60 (BAF→EAS, p.342), Translation 68 (AFN→EAS, p.373)
1. `A' := A ∪ {η}` where `η ∉ U`.
2. Lift attacks to singular form `R' = {({a},b) | (a,b) ∈ R}`.
3. Add evidence support `E = {({η}, a) | a ∈ A}` (or set-supporter form depending on framework).
4. η is fixed: cannot attack, cannot be attacked, cannot be supported.

### Sequence-existence DAG check (strong validity) — Theorems 4.2.34, 4.2.39, 4.2.45 (p.181–185)
- AFN: build `SG^FN`; check DAG via Tarjan SCC.
- EAS: build `SG^ES`; check rooted DAG with η root.
- ADF: build positive dependency graph `PDG^D` (over redundancy-free, cleansed ADF); check DAG.

### Breaker arguments (ADF→AF cc/ca semantics) — Translations 85, 86 (p.433, p.437)
1. `A^{ev}` := minimal partially-acyclic pd-evaluations `(F, G, B)`.
2. `A^b` := one breaker `a^b` per argument `a` appearing in some `F`.
3. cc: each `a^b` self-attacks; bidirectional ev↔breaker links per F vs F∪G.
4. ca₂: same as cc but breakers are NOT self-attackers (independence required for labeling).

### Primed defenders (defender pattern, generic) — Translations 26, 33, 38, 39, 65, 66, 75, 76
For each source argument `a`, introduce a primed copy `a'` meaning "a is rejected" (or "a is not powerful" / "a is not e-supported"). Source `a` attacks `a'`; `a'` attacks the conflict argument that targets `a`. Variants differ in which subset of primed copies are introduced (only attacked args / only supportable args / all non-η args).

## Definitions Catalogue

### Chapter 2 (Background)

- **2.1.1** Dung AF `(A, R)` *(p.22)*
- **2.1.2** AF cf/adm/pref/comp/stb *(p.22)*
- **2.1.3** Range `E^+, E^-, E^Ran` *(p.22)*
- **2.1.4** Semi-stable: range-maximal complete *(p.22)*
- **2.1.5** Characteristic function `F_F` *(p.23)*
- **2.1.12** Well-founded AF *(p.24)*
- **2.1.14** Three-valued labeling *(p.25)*
- **2.1.15** Conflict-free / admissible / complete / preferred / grounded / stable labelings *(p.25)*
- **2.1.19** SETAF (CAF) `(A, R ⊆ 2^A × A)` *(p.27)*
- **2.1.20** SETAF defense and standard semantics *(p.27)*
- **2.1.21** SETAF characteristic function *(p.27)*
- **2.1.26** SETAF discarded set / range *(p.28)*
- **2.1.28** AFRA `(A, R)`, `R ⊆ A × (A ∪ R)` *(p.29)*
- **2.1.29–31** Direct / indirect / full defeat *(p.29)*
- **2.1.32** AFRA acceptability *(p.29)*
- **2.1.34–35** AFRA cf / adm / pref / comp / stb *(p.29–30)*
- **2.1.36** AFRA characteristic function `F_FR` *(p.30)*
- **2.1.37** AFRA discarded set *(p.30)*
- **2.1.40** EAF `(A, R, D ⊆ A × R)` *(p.31)*
- **2.1.41** EAF `defeats_E` *(p.32)*
- **2.1.43** EAF conflict-free *(p.32)*
- **2.1.45** EAF reinstatement set `R_E` *(p.33)*
- **2.1.46** EAF acceptability *(p.33)*
- **2.1.48** EAF adm/pref/comp/stb *(p.34)*
- **2.1.49** EAF characteristic operator `F_EF: 2^CF → 2^A` *(p.34)*
- **2.1.50** Finitary EAF *(p.34)*
- **2.1.51** Iterative grounded EAF *(p.34)*
- **2.1.53** EAF discarded set *(p.35)*
- **2.1.56** Hierarchical EAF (HEAF) *(p.35)*
- **2.1.58** Bounded HEAF grounded *(p.35)*
- **2.1.62** EAFC `(A, R, D ⊆ 2^A × R)` *(p.41)*
- **2.1.63** EAFC defeat / cf / reinstatement *(p.41)*
- **2.2.1** BAF `(A, R, S)` *(p.43)*
- **2.2.2** BAF supported / secondary / mediated / extended attacks *(p.45)*
- **2.2.3** Super-mediated attack *(p.45)*
- **2.2.4** Tiered indirect attacks `R^ind` *(p.46)*
- **2.2.5** BAF defense parametrised on `R'` *(p.47)*
- **2.2.6** +cf / safe / closed-under-S / inverse-closed *(p.47–48)*
- **2.2.7** d-/s-/c-/i-admissible, stable *(p.48)*
- **2.2.9** d-complete *(p.49)*
- **2.2.10** d-characteristic operator `d-F_BF` *(p.49)*
- **2.2.14** d-grounded *(p.50)*
- **2.2.17** Binary AFN (deprecated) *(p.51)*
- **2.2.18** Extended necessity / extended attack *(p.51)*
- **2.2.19** N-cycle-free / coherent / strongly coherent (binary AFN) *(p.51)*
- **2.2.20** Binary AFN extension types *(p.51)*
- **2.2.21** Set AFN *(p.52)*
- **2.2.22** Powerful in E *(p.53)*
- **2.2.23** AFN coherent / strongly coherent *(p.53)*
- **2.2.24** AFN defends; characteristic function `F_FN` *(p.53)*
- **2.2.25** AFN deactivated set `E^+` *(p.53)*
- **2.2.26** AFN extension types *(p.53)*
- **2.2.27** AFN discarded set `E^att` *(p.54)*
- **2.2.32** EAS `(A, R, E, η)` *(p.55)*
- **2.2.33** Evidential support / minimal e-support *(p.56)*
- **2.2.34** Evidential sequence *(p.56)*
- **2.2.36** e-supported attack / minimal *(p.56)*
- **2.2.37** EAS acceptable *(p.56)*
- **2.2.38** EAS extension types *(p.56)*
- **2.2.39** EAS discarded set `S^+` *(p.57)*
- **2.2.41** EAS characteristic function `F_ES` *(p.57)*
- **2.3.1** Signature `Σ_σ^AF` *(p.59)*
- **2.3.2** `Args_S, Pair_S` *(p.59)*
- **2.3.3** Realizability properties (downward-closed / tight / incomparable / adm-closed / com-closed) *(p.59)*

### Chapter 3 (ADFs)

- **3.1.1** ADF `(A, L, C)`, acceptance condition `C_a: 2^par(a) → {in, out}` *(p.66)*
- **3.1.2** Supporting / attacking link, BADF *(p.67)*
- **3.1.3** Completion of an interpretation *(p.68)*
- **3.1.4** Decisive / decisively in / decisively out *(p.69)*
- **3.1.5** `acc(G,B)`, `reb(G,B)` *(p.70)*
- **3.1.6** Positive dependency function `pd_E^D`, soundness *(p.70)*
- **3.1.7** Standard pd-evaluation `(F, B)` *(p.71)*
- **3.1.8** Partially acyclic pd-evaluation `(F, sequence, B)` *(p.72–73)*
- **3.1.9** Acyclic pd-evaluation (F = ∅) *(p.73)*
- **3.1.10** Blocked evaluation *(p.74)*
- **3.1.11** Minimal evaluations *(p.75)*
- **3.1.12** Conflict-free / pd-acyclic conflict-free *(p.75)*
- **3.1.13** Standard range *(p.75)*
- **3.1.15 (Deprecated)** Original acyclic range *(p.76)*
- **3.1.18** Partially acyclic discarded set `E^{p+}` *(p.77)*
- **3.1.20** Partially acyclic range *(p.77)*
- **3.2.1** Three-valued characteristic operator `Γ_D` *(p.79)*
- **3.2.2** ADF labelings (model / admissible / complete / preferred / grounded) *(p.79)*
- **3.2.3** Reduct `D^E` *(p.80)*
- **3.2.4** Stable model *(p.80)*
- **3.3.1** ADF model *(p.83)*
- **3.3.6** Grounded model via `Γ'_D` *(p.85)*
- **3.3.8** Acyclic grounded *(p.85)*
- **3.3.9** CC family (admissible / complete / preferred) *(p.87)*
- **3.3.10** AA family *(p.88)*
- **3.3.11** AC family *(p.89)*
- **3.3.12** CA₁, CA₂ families *(p.90–91)*
- **3.4.1** Correspondence (3-valued v over A and E ⊆ A correspond iff v^t = E) *(p.96)*
- **3.5.1** AADF⁺ *(p.102)*
- **3.7.1** Polynomial hierarchy classes / D^P / D_i^P *(p.110)*
- **3.7.2** Weak positive dependency function / weak X pd-evaluation *(p.111)*

### Chapter 4 (Translations)

- **4.1.1** Framework translation *(p.127)*
- **4.1.2** Similarity relation `~` between semantics *(p.128)*
- **4.1.3** Singular & collective semantics casting *(p.129)*
- **4.1.4** Translation strength (⊆-weak / ⊇-weak / strong) *(p.130)*
- **4.1.5** Sub relation `⊑` *(p.131)*
- **4.1.6** Casting types (identity / removal / addition / union) *(p.131–132)*
- **4.1.7** Functional properties *(p.134)*
- **4.1.8** Syntactical properties *(p.134–135)*
- **4.1.9** Semantical properties (generic, faithful, exact, etc.) *(p.140)*
- **4.1.10** ⊗ / ⊕ on propositional ADFs *(p.140)*
- **4.1.11** ⊗ / ⊕ on functional ADFs *(p.140)*
- **4.1.12** Computational properties (modular / δ-modular / polynomial / polysize / structural / semi-structural / semantical) *(p.142)*
- **4.2.1** Subframework / full subframework (AF) *(p.146)*
- **4.2.2** Trimmed subframework (AFN) *(p.147)*
- **4.2.3** Reduct of an ADF (functional restatement) *(p.147)*
- **4.2.4** SETAF minimal form *(p.148)*
- **4.2.6** EAFC minimal form *(p.150)*
- **4.2.8** AFN minimal form *(p.151)*
- **4.2.10** EAS minimal form *(p.153)*
- **4.2.12** ADF redundancy-free form *(p.155)*
- **4.2.14** Cleansed form *(p.157)*
- **4.2.17** AFN weak validity form *(p.162)*
- **4.2.19** EAS weak validity form *(p.164)*
- **4.2.21** ADF weak validity form *(p.166)*
- **4.2.24** AFN relation validity form *(p.169)*
- **4.2.27** EAS relation validity form *(p.173)*
- **4.2.29** ADF relation validity form (open translation) *(p.175)*
- **4.2.30** AFN strong validity *(p.179)*
- **4.2.35** EAS strong validity *(p.181)*
- **4.2.40** ADF strong validity *(p.184)*
- **4.2.46** Consistent / strongly consistent AFN *(p.187)*
- **4.2.47** Consistent / strongly consistent EAS *(p.187)*
- **4.2.48** AFN inconsistency origin `O^a` *(p.188)*
- **4.2.49** AFN replacement function *(p.188)*
- **4.2.52** EAS inconsistency origin *(p.190)*
- **4.2.53** EAS replacement function *(p.190)*
- **4.2.60** Consistent EAF *(p.197)*
- **4.2.61** Consistent / strongly consistent EAFC *(p.197)*
- **4.2.62** Binary SETAF *(p.198)*
- **4.2.64** AFRA recursion depth *(p.198)*
- **4.2.65** EAF(C) without defense / symmetric attacks *(p.199)*
- **4.2.66** Binary EAFC *(p.199)*
- **4.2.68** BAF subclasses (no support, support-acyclic, support depth n) *(p.199)*
- **4.2.70** AFN subclasses (NSup, SBin, SSig, Sup_n, SEle_n, WSt) *(p.200)*
- **4.2.72** EAS subclasses (ABin, ASig, SBin, SSig, AllSup, EvSup) *(p.201)*
- **4.2.74** Dung-style ADF *(p.202)*
- **4.2.75** SETAF-style ADF *(p.202)*
- **4.2.76** EAFC-style and EAF-style ADF *(p.202)*
- **4.3.4** AFRA `→AFRA` operator *(p.206)*
- **4.5.5** AFRA source-complete set *(p.263)*
- **4.6.34** EAF inconsistency origin *(p.308)*
- **4.6.35** EAF replacement function *(p.308)*
- **4.6.44** EAFC inconsistency origin *(p.316)*
- **4.6.45** EAFC replacement function *(p.317)*
- **4.7.6** Coalition (Deprecated CLS10) *(p.318)*
- **4.7.7** Deductive coalition *(p.320)*

## Theorems / Propositions / Lemmas

(See chunk-merged catalogue. Highlights and impossibility theorems are below; full list is preserved in the merged synthesis. Pages cited are PDF page indices.)

### Chapter 2 highlights
- **Lemma 2.1.6** AF: cf E adm iff E ⊆ F_F(E); complete iff E = F_F(E). *(p.23)*
- **Lemma 2.1.8** Dung's Fundamental Lemma. *(p.23)*
- **Theorem 2.1.9** AF: stable ⇒ preferred. *(p.23)*
- **Theorem 2.1.13** Well-founded AF ⇒ unique extension that is grounded, preferred, stable. *(p.24)*
- **Theorem 2.1.39** AFRA: usual inclusions over A ∪ R. *(p.30)*
- **Theorem 2.1.55** Finitary EAF: every preferred is complete; every stable is complete; grounded is *minimal* (not necessarily least) complete. *(p.34)*
- **Lemma 2.2.8** BAF Fundamental Lemma — holds only when R' = R''; strict inclusion or s/c/i admissibility breaks it. *(p.48)*
- **Lemma 2.2.46** EAS Fundamental Lemma. *(p.58)*
- **Theorem 2.3.4** AF semantics signatures: cf={non-empty, downward-closed, tight}; stable={incomparable, tight}; adm={non-empty, adm-closed, contains ∅}; pref={non-empty, incomparable, adm-closed}. *(p.61)*
- **Theorem 2.3.6** Dyrek/Dyr14 lifted: any framework can be translated into a Dung AF realizing the same preferred or semi-stable labelings. *(p.61)*

### Chapter 3 highlights
- **Theorem 3.2.5** Each preferred labeling is complete; grounded is ≤ᵢ-least; complete labelings form complete meet-semilattice. *(p.80)*
- **Theorem 3.3.2** E pd-acyclic cf in D iff E is grounded extension of reduct D^E. *(p.84)*
- **Theorem 3.3.3** Model E is stable iff pd-acyclic conflict-free in D. *(p.84)*
- **Theorem 3.3.21** cc, ac, aa-complete extensions form complete meet-semilattices; ca₁, ca₂-complete may not. Grounded least ac/cc-complete; acyclic grounded least aa-complete and minimal (not least) ca₁/ca₂-complete. *(p.95)*
- **Theorem 3.4.4** Correspondence between ADF labelings and ca₁/ca₂ extensions; cc/ac/aa labelings → only ca₂-admissible counterpart in general. *(p.98)*
- **Theorem 3.5.2** AADF⁺ collapse: every cf is pd-acyclic cf; every model is stable; aa/cc/ac/ca₁/ca₂ admissible/complete/preferred coincide; grounded ↔ acyclic grounded. *(p.103)*
- Complete complexity catalog Propositions 3.7.3–3.7.63 across cf/grd/acy-grd/cc-/aa-/ac-/ca₁-/ca₂- adm/cmp/prf for verification, credulous, skeptical. Range from P (Ver_cf) up to Π_4^P (Skept_{ca₁-prf} ∈ Π_4^P, Π_3^P-hard).

### Chapter 4 highlights and impossibility theorems
- **Theorem 4.2.7, 4.2.9, 4.2.11, 4.2.13, 4.2.15** Minimal / redundancy-free / cleansed forms preserve all standard semantics (cf, adm, comp, pref, grd, stb), plus ADF-specific xy-σ. *(p.150–157)*
- **Theorem 4.2.34, 4.2.39, 4.2.45** Strong validity ⇔ DAG (AFN: support graph; EAS: rooted DAG with η root; ADF: positive dependency graph). *(p.181–185)*
- **Theorem 4.2.43** SV^ADF ⊊ AADF⁺; (RFree ∩ Cln ∩ AADF⁺) ⊆ SV^ADF. *(p.184)*
- **Theorem 4.3.16 (Impossibility)** No full exact AF→EAS translation under {adm, comp, pref, grd, stb} with identity casting. *(p.219)*
- **Theorem 4.3.17, 4.3.20** AF→ADF (Translation 23) is `AADF⁺ ∩ BADF`, redundancy-free, weakly/relation/strongly valid, cleansed; all six standard AF semantics correspond exactly under the xy-flavor collapse. *(p.220–221)*
- **Theorem 4.4.4 (Impossibility)** No full exact SETAF→AF under {cf, adm, comp, pref, stb} with identity casting (Example 91 triangle SETAF). *(p.235)*
- **Theorem 4.4.7 (Impossibility)** No full exact SETAF→AFN under {adm, pref}; stable open. *(p.241)*
- **Theorem 4.4.10 (Impossibility)** No full exact SETAF→EAS under {cf, adm, comp, pref, stb}. *(p.243)*
- **Theorem 4.4.15** SETAF→ADF (Translation 31) exact for cf, adm, comp, pref, grd, stb under xy ∈ {a,c}. Overlapping (not injective). ⊗-modular. *(p.245)*
- **Theorem 4.5.3** AFRA→BAF (Translation 34) exact under cf/stb/d-grd/d-adm/d-comp/d-pref with `R' = R^sec`. The only AFRA→target that is both modular and exact. *(p.260)*
- **Theorem 4.6.2, 4.6.4** EAF↔EAFC (Translations 36, 37) exact for {cf, adm, comp, pref, grd, stb} on `BH ∪ NSym` subclasses. *(p.269–271)*
- **Theorem 4.6.8 / 4.6.9 (Impossibility)** No full exact EAF→AF or EAFC→AF under {cf, comp, stb}. *(p.277)*
- **Theorem 4.6.13 / 4.6.14 (Impossibility)** No full exact EAF→SETAF, EAFC→SETAF under {cf, comp, stb}. *(p.283–284)*
- **Theorem 4.6.16 / 4.6.17 (Impossibility)** No full exact EAF→AFRA, EAFC→AFRA under {cf, adm, comp, pref, stb}, even from BH^EAF. *(p.286)*
- **Theorem 4.6.26 / 4.6.27 (Impossibility)** No full exact EAF→AFN, EAFC→AFN under {cf, comp, stb}. *(p.298)*
- **Theorems 4.6.28–4.6.47** EAF/EAFC→ADF translations (47 consistent EAF, 48 general EAF with bypass, 49 strongly-consistent EAFC, 50 general EAFC with bypass) preserve all six semantics on bounded hierarchical sources and ca₂-σ on general sources. EAFC→ADF is the **only EAF/EAFC translation that is both full and exact**. *(p.302–321)*
- **Theorem 4.7.1** BAF→AF attack-propagation (Translation 53) exact under +cf, d-σ for σ ∈ {adm, comp, pref}, d-grd, stb, with `R' = R'' ⊆ R^ind`. *(p.324)*
- **Theorem 4.7.4 / 4.7.5** Inverse-closure / closure attack-propagation–defender AF (Translations 54, 55) for i-/c-admissible / preferred. *(p.326–328)*
- **Theorem 4.7.8 (Deprecated)** CLS13 deductive-coalition correspondence — proof relies on union casting, not strong/1-1. *(p.320)*
- **Theorem 4.7.13 / 4.7.14** Support-acyclic BAF → AFN (Translation 59). The only modular and structural BAF translation. Eight-way bidirectional semantics correspondence. *(p.340–341)*
- **Theorem 4.7.16** Support-acyclic BAF→EAS (Translation 60), one-way conflict-free, bidirectional admissible/preferred/complete/grounded/stable modulo η. *(p.342–343)*
- **Theorem 4.8.6 (Existence-only)** Full exact AFN→AF translation under admissible/preferred exists; construction left open. *(p.355)*
- **Theorem 4.8.7 (Impossibility)** No full exact AFN→AF under stable. *(p.356)*
- **Theorem 4.8.24** Strongly consistent AFN→ADF (Translation 69): all standard AFN semantics correspond to **aa-σ** ADF semantics; AFN strongly coherent ↔ ADF pd-acyclic conflict-free; AFN grounded ↔ ADF acyclic-grounded; AFN stable ↔ ADF stable. *(p.381)*
- **Theorem 4.9.2 (Impossibility)** No full exact EAS→AF under {cf, adm, comp, pref, stb} with identity casting. *(p.390)*
- **Theorem 4.9.21** Strongly consistent EAS→ADF (Translation 80): {adm, pref, comp} ↔ aa-σ; stable ↔ stable; grounded ↔ acyclic-grounded. *(p.413)*
- **Theorem 4.10.1, 4.10.2, 4.10.3, 4.10.4, 4.10.5** ADF→AF translations 82 (aa, evaluation arguments), 83 (ac, evaluations + standard self-attackers), 85 (cc, breakers self-attacking), 86 (ca₂, breakers without self-attack), labeling correspondence via EV^p / ALL functions. *(p.420–441)*
- **Theorem 4.10.6 (Impossibility)** **No full or BADF/AADF⁺ source-subclass translation from ADF to AF is exact under cf, pd-acyclic cf, xy-{adm, comp, pref}, stable, model, three-valued model, or labeling-{adm, comp, pref}.** Reason: ADFs handle SETAFs trivially, AFs do not. *(p.443)*
- **Theorem 4.10.7, 4.10.8, 4.10.9, 4.10.10** ADF→SETAF translations 87 (cc), 88 (aa, weakly valid). *(p.444–449)*

## Translation Taxonomy

(Polberg presents and proves correctness of approximately 90 numbered Translations across the framework lattice. The table below covers Translations 1–88 captured so far; Translations 89+ remain to be merged from chunks 450+.)

| # | Source | Target | Pattern | Exact for σ ∈ {…} | Page | Limitation |
|---|--------|--------|---------|-------------------|------|------------|
| 1 | SETAF | SETAF (min) | basic | cf, adm, pref, comp, grd, stb | 148 | Not modular |
| 2 | EAFC | EAFC (min) | basic | cf, adm, comp, pref, grd, stb | 150 | Not modular |
| 3 | AFN | AFN (min) | basic | cf, coh, adm, pref, comp, grd, stb | 152 | Not modular |
| 4 | EAS | EAS (min) | basic | cf, ssup, adm, comp, pref, grd, stb | 153 | Not modular |
| 5 | ADF | ADF (rfree) | basic | all extension and labeling families | 155 | Not modular |
| 6 | ADF | ADF (cleansed) | basic / semi-structural | all extension; ⊇-weak for 3-valued model + admissible labelings | 158 | Asymmetric f-completion |
| 7 | AFN | AFN (wv) | basic / semantical | coh, str-coh, adm, pref, comp, grd, stb; cf only one-way | 162 | Not structural |
| 8 | EAS | EAS (wv) | basic / semantical | ssup, str-ssup, adm, pref, comp, grd, stb | 165 | Not structural |
| 9 | ADF | ADF (wv) | basic / semantical | aa-σ family + acyclic grounded + stable | 169 | Not structural |
| 10 | AFN (wv) | AFN (rv) | basic | coh, str-coh, adm, pref, comp, grd, stb | 169 | Pre-requires wv |
| 11 | AFN | AFN (rv composed) | basic | same; cf only one-way | 171 | Two-step |
| 12 | EAS | EAS (rv) | basic | cf, ssup, str-ssup, adm, pref, comp, grd, stb | 173 | Single-step |
| 13 | AFN | AFN (bypass-consistent) | basic | all standard | 188 | Faithful only |
| 14 | EAS | EAS (bypass-consistent) | basic | all standard | 190 | Faithful only |
| 15 | AFN | AFN (self-attacker-consistent) | basic | all except stable in one direction | 192 | Breaks stable |
| 16 | EAS | EAS (self-attacker-consistent) | basic | all standard | 194 | Faithful |
| 17 | AF | SETAF | basic | cf, adm, pref, comp, grd, stb | 204 | Target = Bin ⊊ Min |
| 18 | AF | AFRA | basic | comp, pref, grd, stb; cf, adm only ⊆-weak | 206 | Improvable to bijective adm via removal+extraction casting |
| 19 | AF | EAF | basic | all standard | 211 | Target ∈ NDef ∩ BH ∩ SCons |
| 20 | AF | BAF | basic | all (d-family with R' = R'' = ∅) | 213 | |
| 21 | AF | AFN | basic | all standard | 214 | Target ∈ NSup ∩ WSt ∩ SEle |
| 22 | AF | EAS | basic / argument-introducing | cf, adm strong; comp, pref, grd, stb only faithful (η addition) | 216 | Theorem 4.3.16 impossibility for full exact |
| 23 | AF | ADF | basic | cf, adm, comp, pref, grd, stb under xy ∈ {a,c} | 220 | Target = ADF^AF; AADF⁺ ∩ BADF ∩ RFree ∩ Cln ∩ SV |
| 24 | SETAF | AF | coalition (Deprecated) | — | 225 | Conflict-freeness propagation issues |
| 25 | SETAF | AF | basic-coalition hybrid | adm, comp, pref, grd, stb (union casting); ⊆-weak cf | 226 | Not modular |
| 26 | SETAF | AF | basic-defender hybrid | comp, pref, grd, stb faithful; ⊆-weak cf, adm | 230 | Modular but only faithful |
| 27 | SETAF | AF | improvement of 25 | comp, pref, grd, stb strong+bijective; ⊆-weak cf, adm | 234 | Cf fails completely |
| 28 | SETAF | AFN | coalition (Deprecated) | — | 238 | Replaced by 29 |
| 29 | SETAF | AFN | basic-coalition | comp, pref, grd, stb strong+bijective; ⊆-weak cf | 238 | Modular |
| 30 | SETAF | EAS | basic | comp, pref, grd, stb faithful; weakly faithful adm | 241 | η addition |
| 31 | SETAF | ADF | basic | cf, adm, comp, pref, grd, stb under xy | 243 | Overlapping; ⊗-modular only |
| 32 | AFRA | AF | basic-attack-propagation hybrid | cf, adm, comp, pref, grd, stb (identity casting) | 249 | Not modular |
| 33 | AFRA | AF | basic-defender hybrid | comp, pref, grd, stb faithful | 252 | Loses exactness adm |
| 34 | AFRA | BAF | basic | cf, stb, d-grd, d-adm, d-comp, d-pref under R' = R^sec | 259 | Modular AND exact — best AFRA target |
| 35 | AFRA | AFN | basic | comp, pref, grd, stb; adm only via source-complete | 262 | Target = WSt ∩ SEle_1 |
| 36 | EAF | EAFC | basic | cf, adm, comp, pref, grd, stb | 269 | Restricted to BH ∪ NSym |
| 37 | EAFC | EAF | basic-defender hybrid | adm, comp, pref, grd, stb faithful; ⊆-weak cf | 270 | BH ∪ NSym only |
| 38 | EAF (BH) | AF | basic-defender hybrid | comp, pref, grd, stb faithful; ⊆-weak cf, adm | 273 | Theorem 4.6.8 impossibility for exact |
| 39 | EAFC (BH) | AF | basic-defender hybrid | as 38 | 276 | Theorem 4.6.9 impossibility |
| 40 | EAF (BH) | SETAF | basic-defender hybrid | adm, comp, pref, grd, stb; ⊆-weak cf | 279 | Theorem 4.6.13 impossibility |
| 41 | EAFC (BH) | SETAF | basic-defender hybrid | as 40 | 282 | Theorem 4.6.14 impossibility |
| 42 | EAF (BH) | AFRA | basic | comp, grd, pref, stb; one-way cf, adm | 285 | Theorem 4.6.16 impossibility |
| 43 | EAF (BH) | AFN | basic (defense-as-support) | comp, pref, grd, stb faithful; ⊆-weak cf | 289 | Not modular |
| 44 | EAF (BH) | AFN | chained | comp, pref, grd, stb; one-way cf, adm | 293 | Same as 43 strength |
| 45 | EAFC (BH) | AFN | basic | as 43 | 295 | |
| 46 | EAFC (BH) | AFN | chained | as 44 | 296 | |
| 47 | EAF (consistent BH/NSym) | ADF | basic | cf, stable, grd, adm, comp, pref ↔ ca₂-σ | 301 | Source subclass |
| 48 | EAF (general) | ADF | basic + bypass | as 47, with `E ∪ E^b` casting | 310 | |
| 49 | EAFC (strongly consistent) | ADF | basic | cf, stable, grd, adm, comp, pref ↔ ca₂-σ; AADF⁺ if BH | 313 | |
| 50 | EAFC (general) | ADF | basic + bypass | as 49 | 317 | **Full and exact** for EAFC |
| 51 | BAF (deductive) | AF | attack propagation | per CLS13 | 323 | |
| 52 | BAF (necessary) | AF | attack propagation | per CLS15 | 324 | |
| 53 | BAF | AF | attack propagation | +cf, d-adm, d-comp, d-pref, d-grd, stb (R' = R'' ⊆ R^ind) | 324 | Generalizes CLS13 |
| 54 | BAF | AF | iclo attack-prop + defender | i-admissible, i-preferred | 326 | Inverse-closure variant |
| 55 | BAF | AF | clo variant | c-admissible, c-preferred | 327 | |
| 56 | BAF | AF | coalition (Deprecated CLS10) | — | 331 | Doesn't preserve semantics |
| 57 | BAF (deductive) | AF | deductive coalition | comp, pref, grd, stb (union casting) | 334 | Theorem 4.7.8 deprecated; 4.7.9, 4.7.10 corrected |
| 58 | BAF (necessary) | AF | basic-defender (CLS15) | adm, pref one-way (4.7.11, 4.7.12) | 338 | Reverse direction fails |
| 59 | BAF (support-acyclic) | AFN | basic | full bidirectional 8-way correspondence | 340 | Modular and structural — best BAF→? |
| 60 | BAF (support-acyclic) | EAS | basic | bidirectional admissible+ ; one-way cf | 342 | η added |
| 61 | AFN | AF | coalition | grd, comp, pref, stb (1-1 at comp); adm not 1-1; cf one-way | 350 | Not modular |
| 62 | AFN | AF | basic (drop support) | cf only | 351 | Specialized |
| 63 | AFN | SETAF | attack propagation (wv) | comp, pref, grd, stb strong+bijective; ⊆-weak str-coh, cf, adm | 358 | Target may not be minimal |
| 64 | AFN | SETAF | attack propagation (sv) | as 63 | 360 | Strongly valid only |
| 65 | AFN | SETAF | basic-defender hybrid | adm, pref, comp, grd, stb correspondences via E ∪ E_{np} | 362 | Not modular |
| 66 | AFN | SETAF | sv defender | same correspondences with simpler defenders | 366 | Strongly valid only |
| 67 | AFN (sv + SBin) | BAF | basic | full 8-way bidirectional with R' = R^sec | 371 | Strongly valid + support-binary only |
| 68 | AFN | EAS | basic | full 8-way bidirectional with η-addition | 373 | Not modular; non-minimal target |
| 69 | AFN (strongly consistent) | ADF | basic | coh ↔ pd-acyclic; str-coh ↔ pd-acyclic-cf; adm/comp/pref ↔ aa-σ; grd ↔ acy-grd; stb ↔ stb | 378 | Target = BADF |
| 70 | AFN (general) | ADF | chained (with 13 or 15) | as 69 modulo bypass; stb only one-way for 15 | 382 | |
| 71 | EAS | AF | coalition | cf, adm, comp, pref, grd, stb (union casting) | 387 | Theorem 4.9.2 impossibility for exact |
| 72 | EAS | SETAF | coalition | cf one-way; adm, comp, pref, grd, stb bidirectional | 391 | |
| 73 | EAS (wv) | SETAF | attack propagation | str-ssup ⇒ cf in target; comp, pref, grd, stb bidirectional; adm one-way | 393 | |
| 74 | EAS | SETAF | wv-then-73 | comp, pref, grd, stb strong+bijective; ⊆-weak others | 394 | |
| 75 | EAS | SETAF | basic-defender hybrid | adm, pref, comp, grd, stb via E ∪ S_{np}; cf one-way | 395 | |
| 76 | EAS (sv) | SETAF | sv defender | same as 75 with simpler S_{np} | 398 | Strongly valid only |
| 77 | EAS (sv, ABin, SSig) | BAF | basic | 8-way bidirectional with R'' = R^sec | 400 | |
| 78 | EAS (ABin) | AFN | basic | 8-way bidirectional | 402 | Not minimal-preserving |
| 79 | EAS (general) | AFN | basic + group-attack lift | adm, pref, comp, grd, stb via S' = S ∪ att(S) | 408 | |
| 80 | EAS (strongly consistent) | ADF | basic | adm, pref, comp ↔ aa-σ; stb ↔ stb; grd ↔ acy-grd | 411 | BADF target; cleansed iff AllSup; rfree iff AllSup ∩ Min |
| 81 | EAS (general) | ADF | chained (with 14 or 16) | as 80 modulo bypass | 415 | |
| 82 | ADF | AF | basic-evaluation | pd-acyclic cf, aa-σ, stb, acy-grd | 420 | Target = AF over evaluations |
| 83 | ADF | AF | basic + standard self-attackers | pd-acyclic cf, ac-σ, grd | 424 | |
| 84 | ADF | AF | (Deprecated) | — | 428 | Faulty cc translation |
| 85 | ADF | AF | basic + breakers (self-attacking) | cf, cc-σ, grd | 433 | Theorem 4.10.6 impossibility |
| 86 | ADF | AF | basic + breakers (no self-attack) | cf, ca₂-σ, model, grd | 437 | Partial only for ca₁ |
| 87 | ADF | SETAF | basic + breakers | cf, cc-σ, grd | 444 | Minimal target |
| 88 | ADF (wv) | SETAF | attack propagation | cf one-way, aa-comp, aa-pref, acy-grd, stb bidirectional | 448 | Weakly valid required |
| 89 | ADF (cleansed) | AFN | (escapes the four-pattern classification) | strong; bijective at coh/str-coh/aa-comp/aa-pref/acy-grd/stb | 452 | Semi-structural; not modular; argument duplication |
| 90 | ADF (cleansed) | AFN (grouped) | improvement over 89 | sketch only — groups by shared f-part | 457 | Future work |

### Impossibility theorems summarized
- **AF→EAS** (Theorem 4.3.16): no full exact under adm, comp, pref, grd, stb.
- **SETAF→AF** (Theorem 4.4.4): no full exact under cf, adm, comp, pref, stb.
- **SETAF→AFN** (Theorem 4.4.7): no full exact under adm, pref.
- **SETAF→EAS** (Theorem 4.4.10): no full exact under cf, adm, comp, pref, stb.
- **EAF/EAFC→AF** (4.6.8/9): no full exact under cf, comp, stb.
- **EAF/EAFC→SETAF** (4.6.13/14): no full exact under cf, comp, stb.
- **EAF/EAFC→AFRA** (4.6.16/17): no full exact under cf, adm, comp, pref, stb (even from BH^EAF).
- **EAF/EAFC→AFN** (4.6.26/27): no full exact under cf, comp, stb.
- **AFN→AF** (Theorem 4.8.7): no full exact under stable. Theorem 4.8.6 says exact admissible/preferred AFN→AF *exists* but construction is open.
- **EAS→AF** (Theorem 4.9.2): no full exact under cf, adm, comp, pref, stb.
- **ADF→AF** (Theorem 4.10.6): no full or BADF/AADF⁺ source-subclass exact under cf, pd-acyclic cf, xy-σ, stb, model, three-valued model, labeling-{adm, comp, pref}.
- **ADF→SETAF** (Theorems 4.10.12, 4.10.14, 4.10.15, 4.10.16): no full or BADF/AADF⁺ source-subclass exact translation under cf+pd-acyclic-cf, ca₁/ca₂-admissible, ca₁/ca₂-complete, (model) stable / (labeling) preferred. Uses Proposition 4.10.11 (SETAF cf is downward-closed) and Proposition 4.10.13 (SETAF admissible quasi-closure under non-conflicting union) as proof tools.

The thesis frames the impossibility constellation as a coherent expressivity hierarchy: ADFs are universal; AFs are at the bottom; SETAFs/AFRAs/EAFs/AFNs/EASs sit at intermediate "breaks" where the next-strongest semantics jump (cf-downward-closure, complete-least-element, stable-incomparability) cannot be matched.

## Semantics Catalogue

### ADF semantics families (extension-based + labeling-based)

| Family | Definition | Range used | Pages |
|--------|-----------|-----------|-------|
| cf | C_s(E ∩ par(s)) = in for all s ∈ E | — | 75, 82 |
| acy-cf | cf + every a ∈ E has unblocked acyclic pd-evaluation | — | 75, 82 |
| Naive | maximal cf | — | 83 |
| Pd-acyclic naive | maximal pd-acyclic cf | — | 83 |
| Model | cf + closure under acceptance | — | 83 |
| Stable | model + pd-acyclic cf (Theorem 3.3.3) | — | 84 |
| Grounded | least fixed point of decisive in/out propagation; ac-family | E^Ran | 85 |
| Acyclic grounded | grounded with acyclic-evaluation falsification; aa-family | E^{a+} | 85 |
| cc-{adm, comp, pref} | cf + decisively in w.r.t. standard range | E^Ran | 87 |
| aa-{adm, comp, pref} | pd-acyclic cf + acyclic pd-eval blocked by acyclic range | E^{a+} | 88 |
| ac-{adm, comp, pref} | pd-acyclic cf + acyclic pd-eval blocked by standard range | E^Ran | 89 |
| ca₁-{adm, comp, pref} | cf + decisively in w.r.t. acyclic range | E^{a+} | 90 |
| ca₂-{adm, comp, pref} | cf + decisively in w.r.t. partially-acyclic range | E^{p+} | 91 |
| Three-valued model | ∀a, v(a) ≠ u ⇒ v(a) = v(φ_a) | — | 79 |
| adm/comp/pref/grd labeling | v ≤ᵢ Γ_D(v) / fixed point / max / min | — | 79 |
| Stable labeling | M = gv^t in D^M | — | 80 |

### Subset relations (Lemma 3.3.15, p.93)
ac-adm ⊂ cc-adm; ac-adm ⊂ aa-adm; aa-adm ⊂ ca₂-adm; cc-adm ⊂ ca₂-adm; ca₂-adm ⊂ ca₁-adm. ca₁-adm ⊄ ca₂-adm.

### Coincidence with AF labeling semantics (Theorems 3.4.4–3.4.7, p.98–99)
- E cc/ac-adm ⇒ u-completion of v_E is admissible labeling.
- E aa-adm ⇒ u-completion of v_E^a is admissible labeling.
- E ca₂-adm ⇒ u-completion of v_E^p is admissible labeling.
- v admissible labeling ⇒ v^t is ca₁ AND ca₂-admissible.
- E ca₁-adm need not have admissible labeling counterpart.
- ca₂-preferred ⇔ preferred labeling correspondence; cc/ac/aa/ca₁ not in general.
- Grounded extension ⇔ grounded labeling via v^t.

### EAFC standard semantics (recapped, Defs 2.1.62–2.1.63 + §4.6, p.41–321)
EAFC carries cf, adm, comp, pref, grd, stb with:
- cf redefined: every internal attack must be collectively defended.
- defeats_E uses set-of-defenders: `(c, (a,b)) ∈ D` with `c ⊆ E`.
- Reinstatement set with collective defense attacks.
- On `BH ∪ NSym` subclass, EAF cf ↔ EAFC cf.

## Complexity Results

Polberg's complexity catalogue for ADF reasoning (Table 3.5, p.122; chunk-extracted Propositions 3.7.3–3.7.63 give one-shot results plus QBF reductions for hardness):

| Problem | cc | ac | aa | ca₁ | ca₂ |
|---------|----|----|----|----|----|
| Ver_adm | Δ_2^P | Σ_2^P | Σ_2^P | Δ_3^P | Σ_2^P |
| Cred_adm | Σ_2^P-c | Σ_2^P-c | Σ_2^P-c | Σ_3^P (Σ_2^P-hard) | Σ_2^P-c |
| Ver_cmp | Δ_2^P | Σ_2^P | Σ_2^P | Δ_3^P | Σ_2^P |
| Cred_cmp | Σ_2^P-c | Σ_2^P-c | Σ_2^P-c | Σ_3^P (Σ_2^P-hard) | Σ_2^P-c |
| Skept_cmp | coNP-c | coNP-c | Π_2^P | Π_3^P | Π_2^P |
| Ver_prf | Π_2^P | D_2^P | D_2^P | Π_3^P | D_2^P |
| Cred_prf | Σ_2^P-c | Σ_2^P-c | Σ_2^P-c | Σ_3^P (Σ_2^P-hard) | Σ_2^P-c |
| Skept_prf | Π_3^P-c | Π_3^P-c | Π_3^P-c | Π_3^P-hard, Π_4^P | Π_3^P-c |

Other results:
- Ver_cf ∈ P; Ver_acy-cf ∈ D^P (Propositions 3.7.24, 3.7.25)
- Cred_cf ∈ NP; Cred_acy-cf ∈ Σ_2^P (3.7.26, 3.7.27)
- Ver_grd ∈ D^P; Ver_acy-grd ∈ Δ_3^P (3.7.28, 3.7.29)
- Cred_grd coNP-c; Cred_acy-grd ∈ Π_2^P (3.7.30, 3.7.31)
- Verification of decisiveness: Ver_dec^in, Ver_dec^out coNP-c (3.7.3, 3.7.4)
- Existence of weak X pd-evaluations: Exists_X-pd^y ∈ NP for X ∈ {st, par, acy} (3.7.11–3.7.13)

QBF-based hardness reductions use AADF⁺ instances (Lemmas 3.7.39, 3.7.59) — proves that even on the well-behaved subclass, complexity does not collapse below Σ_2^P / Π_3^P.

## Figures of Interest

- **Fig 2.1 (p.24):** Sample AF for running example. **Fig 2.2 (p.28):** Sample SETAF. **Fig 2.3 (p.30):** Sample AFRA. **Fig 2.4–2.10 (pp.32–42):** EAF and EAFC samples illustrating non-semilattice complete extensions (Ex 8) and stable that isn't preferred (Ex 9).
- **Fig 2.11 (p.45) / 2.12 (p.46):** BAF supported / secondary / mediated / extended / super-mediated attacks.
- **Fig 3.1–3.12 (pp.69–99):** ADF semantics demonstrations including Fig 3.5/Table 3.1 (p.80) twenty-plus admissible labelings, Fig 3.7 (p.86) acyclic grounded, Fig 3.8 (p.87) cc/aa/ac comparison, Fig 3.9 (p.90) ca₁ vs ca₂, Fig 3.10 (p.91) ca subtlety, **Fig 3.11 (p.95) hierarchy diagram of all ADF semantics families** — critical reference.
- **Fig 3.13 (p.100):** Inclusion diagram between extension- and labeling-based ADF semantics.
- **Fig 3.19 (p.110):** Polynomial hierarchy diagram. **Fig 3.20, 3.21:** AADF⁺ used in QBF reductions for Σ_2^P / Π_3^P-hardness.
- **Tables 3.4 (p.109), 3.5 (p.122):** Existing and new complexity results.
- **Table 4.1 (p.125):** Translation chart between {AF, SETAF, AFRA, EAF, EAFC, BAF, AFN, EAS, ADF}.
- **Table 4.2 (p.145):** Pattern classification (Bas / Cl / AP / Def / Ch / ?).
- **Tables 4.3 (p.223), 4.4 (p.248), 4.5 (p.266), 4.6/4.7 (EAF/EAFC), 4.8 (p.349, BAF), 4.9 (p.385, AFN), 4.10 (p.406, EAS):** Per-source translation property summaries.
- **Fig 4.21 (p.221), 4.30 (p.246), 4.36, 4.41, 4.42, 4.46, 4.47, 4.50, 4.51, 4.56, 4.57, 4.58, 4.65, 4.71, 4.75, 4.81–4.92:** Translation illustrations with concrete acceptance conditions.

## Results Summary

What is now possible because of this thesis:
1. **A single semantics family for ADFs** with a complete xy-classification, complexity bounds, and a sanity subclass (AADF⁺) where everything collapses.
2. **A formal vocabulary** for comparing translations across the entire abstract-argumentation literature: every translation has a property bundle (strength × functional × syntactical × semantical × computational × pattern).
3. **A normal-form pipeline** with proven preservation theorems for moving from any framework to its minimal / cleansed / weakly / relation / strongly valid form.
4. **A subclass taxonomy** identifying when translations succeed (BH^EAF, support-acyclic BAF, ABin EAS, AADF⁺ ADF) vs fail.
5. **Impossibility theorems** that pin down the genuine expressivity hierarchy among the nine frameworks, justifying why ADF is the only universal target.
6. **Concrete acceptance-condition recipes** (`att_a ∧ sup_a` for AFN/EAS; `⋀ ¬X^a` for AF; `⋁ ¬X_i ∧ ⋀` shape for SETAF; `¬b ∨ ⋁ D_{b,a}` shape for EAF/EAFC) suitable for direct Z3/Boolean-solver implementation.
7. **A defensible recommendation that ADF is the canonical render-time normalization target** for cross-framework reasoning.

## Limitations

Captured by the author:

- **ADF relation-valid translation is open** (p.176). Two natural definitions both fail; future work.
- **Strong-validity translations open for AFN/EAS/ADF** (pp.165, 176). Argument-duplication is proposed but not fully constructed.
- **AFN→AF exact translation under admissible/preferred** is known to exist (Theorem 4.8.6) but the construction is left open (p.355).
- **AFN→AF stable** is impossible (Theorem 4.8.7) — fundamental cardinality / tightness mismatch.
- **EAS→AF exact** is impossible under any of cf/adm/comp/pref/stb (Theorem 4.9.2).
- **EAF/EAFC translations restricted to BH ∪ NSym subclass** for AF/SETAF/AFRA/AFN; "fullness" is left for future work (pp.270, 275, 286, 298).
- **No EAF→ADF without bounded hierarchical** restriction except via the ca₂ family — which over-generates on symmetric-attack EAFs.
- **No BAF→ADF translation** (p.345–348) — abstract support is conceptually orthogonal to ADF acceptance conditions.
- **No EAS→AFRA / EAS→EAF(C) translations** — explicitly deferred (p.405).
- **Self-attacker consistency breaks stable in one direction** (Theorem 4.2.56).
- **Bypass consistency is faithful, not exact** (p.187).
- **ADF→AF translations beyond grounded/acyclic-grounded are at best faithful** (Theorem 4.10.6).
- **Labeling-admissibility ADF→AF is only ⊆-weak** (Example 153, p.442).
- **SETAF signatures: no sufficient conditions known**, only necessary (downward-closed) (p.449).

## Arguments Against Prior Work

- **BW10 ADF extension semantics:** worked only on bipolar subclass, "did not always produce desired results" (p.16). Replaced.
- **BES+13 / Str13a labeling semantics:** opacity of Dung notions; self-influence under cycles; info-vs-subset maximality mismatch under support (p.16, p.64). Polberg keeps labeling but shows it fails to coincide with extension semantics in general — only ca₂ family aligns cleanly.
- **Graph-based generalizations of Dung (NP07, CLS13, Nou13, Mod09a, BCGG11):** become unwieldy as new relation types are added (p.15). ADF arbitrary acceptance conditions replace this proliferation.
- **BAF Fundamental Lemma fails outside `R' = R''`** (Lemma 2.2.8, p.50). Forces Polberg to define only `d-`complete and `d-`grounded with shared parameter (p.50). Cross-parameter complete semantics left to future work.
- **EAF design controversies** (§2.1.4.2, pp.36–40): non-semilattice complete extensions (Ex 8, BCGG11); grounded only minimal not least; stable that isn't preferred (Ex 9); conflict-free forces self-attack on perception-error case (Ex 10); induced symmetric attacks generated only for length-2 cycles (`EF_2` vs `EF_3`). MP10's collective-defense-attacks (EAFC) fixes most of this.
- **NR11 binary AFNs:** Example 14 (p.52) shows extensions like `{a,b}` satisfy the formal definition but violate authors' intentions. Binary AFNs are abandoned in favor of set-AFNs (Nou13).
- **Original CLS09 BAF assumption `R ∩ S = ∅`:** "supporting and attacking the same argument is not nonsensical" (footnote, p.43). Later works drop the assumption.
- **CLS10 coalition translation (Definition 4.7.6):** marked **Deprecated** because it does not preserve semantics in general (p.318–319, Ex 119). Replaced by Translation 57 (deductive) + Theorem 4.7.9.
- **CLS13 coalition Theorem 4.7.8:** "Unfortunately, the results are not entirely correct" — proof relies on union casting (p.320). Replaced.
- **Nou13 claim that AFNs strictly more expressive than AFs:** Polberg disagrees: "the sample frameworks they have provided produce sets of extensions consisting only of a single set containing a single argument [...] trivially realizable in AFs under complete, preferred and stable" (p.354). Theorem 4.8.6 then proves a full exact AFN→AF for adm/preferred *does* exist.
- **BGvdTV09 meta-level AF:** AFRA admissible "deepest attacks" lost in target (p.254). Polberg uses simplified MBC11-style instead.
- **ADF preferred semantics:** "too cautious" — Polberg's xy-classification gives ranges and corresponding semantics where preferred extensions are richer than the labeling-based version.
- **Supported attack imposes hidden completeness assumptions:** "supported attack as preemptive and hinting that we have already read the brochure and verified that the hotel is indeed not quiet" (p.348). Polberg argues ADFs handle this correctly via acceptance conditions.
- **CLS15 defender translation (Theorem 4.7.11/4.7.12):** Reverse direction fails — admissible in target may not give i-admissible in source.

## Design Rationale

### Why ADF as the canonical generalization
- Acceptance conditions zoom out from singular relations: "ADFs work somehow the other way around. Acceptance conditions 'zoom out' from singular relations and given a set of arguments, they tell us whether the argument can be accepted or not." (p.104).
- Falsum arguments are structural, not semantical: "I do not exist" vs "undecided" — distinct from self-attackers (p.104, p.105).
- ADFs are the only target where every other framework can be translated, and the only target where bounded-hierarchical restriction is not needed for EAF/EAFC.

### Why translations to ADF are the only ones that always work for many sources
EAF/EAFC: AF/SETAF/AFRA/AFN are blocked by impossibility theorems on at least one of cf/comp/stb (4.6.8/9, 4.6.13/14, 4.6.16/17, 4.6.26/27); only ADF (Translations 47–50) handles general EAF/EAFC. SETAF: AF blocked by 4.4.4; AFN blocked under adm/pref by 4.4.7; EAS blocked by 4.4.10; ADF (Translation 31) is exact for all six standard semantics. EAS: AF blocked by 4.9.2; ADF (Translation 80) is exact for the standard family.

### Why bipolar/p-marker subclasses help
- BADF: lower complexity than general ADFs (SW14, p.67). Polberg uses BADF as the AFN/EAS target subclass.
- AADF⁺: collapses xy-flavors so translation correctness only needs to be checked once. Many translation-derived ADFs are AADF⁺ automatically (Theorem 4.3.17 for AF, Theorem 4.4.11 for SETAF, Theorem 4.6.28 for BH-EAF, Theorem 4.9.16 for SV+min EAS).
- SV (strongly valid) ⊊ AADF⁺ ⊋ SV — strong validity additionally requires every argument has an evaluation (Theorem 4.2.43, p.184).

### Why the thesis abandons supported attack inside ADF
Supported attack imposes hidden completeness assumptions (p.348). ADF acceptance conditions can express attacks as direct relations; supported attack only adds expressive overhead.

### Why parametric BAF is the BAF section's organizing principle
"Our intent is merely to gather and organize the available approaches." (p.47) — different choices of `R' ⊆ R^ind` correspond to different prior literatures (CLS09 abstract, CLS13 attack propagation, CLS15 etc.). Polberg's `(R', R'')` parametrization is the unifying view.

### Why basic / coalition / attack-propagation / defender pattern catalogue
A reusable abstraction: every translation in the chapter falls into one (or a hybrid) of these patterns. Implementers can pick the pattern based on whether modularity (basic/AP), exactness (basic), or bidirectional admissibility (defender) matters most.

## Testable Properties

(Each property is checkable against a concrete ADF or framework instance. Page numbers cite the relevant theorem/definition.)

- BADF check: every link `(r,s) ∈ L` is supporting or attacking (Def 3.1.2). *(p.67)*
- AADF⁺ check: every standard pd-evaluation has acyclic refinement (Def 3.5.1). *(p.102)*
- BADF ⊊ AADF⁺ false; AADF⁺ ⊊ BADF false (Lemma 4.2.77). *(p.203)*
- For AADF⁺ D, all five flavors of admissible / complete / preferred coincide; cf ↔ pd-acyclic cf; model ↔ stable; grd ↔ acy-grd (Theorem 3.5.2). *(p.103)*
- AFN strongly valid ⇔ `SG^FN` is a DAG (Theorem 4.2.34). *(p.181)*
- EAS strongly valid ⇔ `SG^ES` is a rooted DAG with η as root (Theorem 4.2.39). *(p.183)*
- ADF strongly valid ⇔ `PDG^D` is a DAG (Theorem 4.2.45). *(p.185)*
- SV^ADF ⊊ AADF⁺; (RFree ∩ Cln ∩ AADF⁺) ⊆ SV^ADF (Theorem 4.2.43). *(p.184)*
- Translation 23 (AF→ADF) preserves cf, adm, comp, pref, grd, stb under xy ∈ {a,c} (Theorem 4.3.20). *(p.221)*
- Translation 31 (SETAF→ADF) preserves all six standard semantics; ⊗-modular only (Theorems 4.4.11, 4.4.15). *(p.244–245)*
- Translation 36 (EAF→EAFC) on BH ∪ NSym is exact for {cf, adm, comp, pref, grd, stb} (Theorems 4.6.1, 4.6.2). *(p.269)*
- EAFC standard / preferred / grounded labelling extension ⇔ extension on argument labels (Theorems 4.6.42, 4.6.43, 4.6.47). *(p.315–318)*
- Translation 50 (general EAFC→ADF) is full and exact via `E ∪ E^b` casting (Theorem 4.6.47). *(p.318)*
- Translation 59 (support-acyclic BAF → AFN) preserves +cf w.r.t. ∅ ⇔ cf, inverse-closed ⇔ coherent, +cf w.r.t. R^sec ⇔ strongly coherent, i-adm ⇔ adm, i-pref ⇔ pref, d-comp ⇔ comp, d-grd ⇔ grd, stb ⇔ stb (Theorem 4.7.14). *(p.340)*
- Translation 69 (strongly consistent AFN → ADF) maps coh ↔ pd-acyclic, str-coh ↔ pd-acyclic-cf, AFN-σ ↔ aa-σ for σ ∈ {adm, comp, pref}, grd ↔ acy-grd, stb ↔ stb (Theorem 4.8.24). *(p.381)*
- Translation 80 (strongly consistent EAS → ADF) maps ssup ↔ pd-acyclic, str-ssup ↔ pd-acyclic-cf, EAS-σ ↔ aa-σ, grd ↔ acy-grd, stb ↔ stb (Theorem 4.9.21). *(p.413)*
- ADF→AF impossibility: no full or BADF/AADF⁺ source-subclass translation is exact under cf, pd-acyclic cf, xy-σ, stb, model, three-valued model, labeling-{adm, comp, pref} (Theorem 4.10.6). *(p.443)*
- AFN stable extensions need not be tight ⇒ no full exact AFN→AF under stable (Theorem 4.8.7, witnessed by Example 126). *(p.356)*
- BAF Fundamental Lemma holds only when `R' = R''` (Lemma 2.2.8). Outside this, `s/c/i` admissibility families break. *(p.50)*

## Relevance to Project

### ASPIC+ bridge
- `propstore.aspic_bridge` already translates claims/stances/rule priorities to formal ASPIC+ types and `aspic.py` builds recursive arguments. Polberg's translation taxonomy (basic/coalition/attack-propagation/defender) is a reusable abstraction for any future `Y → AF` adapter the bridge ships. The classification dataclass should mirror Polberg's property bundle: `{strength: per_semantic_dict, functional: tags, syntactical: tags, semantical: tags, computational: tags, pattern: enum}`.

### Dung-AF construction
- propstore.world (ATMS) reading: bundle environments correspond to Polberg's evaluations (F, G, B). Translation 82 (ADF→AF for aa-semantics) gives the formal mapping: each minimal acyclic pd-evaluation becomes an AF argument; conflicts are blocking-set intersections.
- η-sentinel pattern (Translation 22, 30, 60, 68): when the propstore renders into an evidence-anchored substrate, all initial supporters are marked supported by η. Maps directly onto an ATMS-style "evidence is available" assumption.

### ADF semantics if propstore adopts them
- `att_a ∧ sup_a` (Translation 69) is the canonical acceptance-condition recipe. propstore CEL/Z3 layer can synthesize these directly from claim graphs (attackers as `⋀ ¬t`, supporters as `⋀ ⋁ Z`).
- xy-flavor selection becomes a render policy: `RenderPolicy(adf_semantics_family="ca₂")` chooses between cc/aa/ac/ca₁/ca₂.
- AADF⁺ check is a `RenderPolicy.fast_path` flag: when true, all five flavors collapse and the cheapest one suffices.

### Translation pattern catalogue as reusable abstraction
- Pattern enum: `{Basic, Coalition, AttackPropagation, Defender, Chained, Hybrid, Unknown}`. Mirror Polberg's Table 4.2 directly as metadata on every adapter.
- Casting function as first-class object: `cast(framework, extension, sigma) -> source_extension`. Some translations need two-step casting (removal + extraction, p.208–209) — interface must allow composition.

### Complexity bounds constrain query strategy
- Most ADF reasoning queries are at least Σ_2^P-complete; ca₁ family jumps to Σ_3^P / Π_3^P / Π_4^P. propstore should:
  - Cache `query_claim()` / `build_arguments_for()` results, marking cache entries with their PH level.
  - Default to ca₂ (matches labelings cleanly, lower complexity than ca₁).
  - Run AADF⁺ detection eagerly after vocabulary reconciliation; collapse to the cheapest semantic family when possible.
  - Run minimal-form / cleansed-form / weak-validity normal forms eagerly; they reduce attack count from `2^n` to `(n choose ⌊n/2⌋)` (Sperner bound, p.141).

### Honest non-commitment / impossibility theorems as load-bearing design
- The impossibility theorems (4.4.4, 4.6.8/9, 4.6.13/14, 4.6.16/17, 4.6.26/27, 4.8.7, 4.9.2, 4.10.6) say that EAF/EAFC/AFN/EAS/ADF semantics genuinely cannot be losslessly squeezed into AF. propstore must therefore:
  - Store source frameworks natively (don't collapse to AF in storage).
  - Use ADF as the lazy render-time rendezvous when cross-framework reasoning is required.
  - Tag any "translation lossy" warning with the relevant theorem reference so users know which semantics the lossy step affects.

### CKR-style overpowering support
- §4.6.6 introduces "overpowering support" — defense-attack-as-positive-relation in ADF acceptance conditions. The only EAF/EAFC translation that escapes the bounded-hierarchical restriction. Maps to `propstore.defeasibility`'s justifiable-exception design: contextual `ist(c, p)` applicability injecting Dung defeats at the ASPIC+ boundary, without making ASPIC+ own contextual exception semantics.

## Translation 89 / Translation 90 (ADF → AFN) — Detail

This is the only translation in the thesis that escapes the four-pattern (basic / coalition / attack-propagation / defender) classification system; Polberg explicitly leaves it unclassified and flags this as evidence that the system can be improved.

**Translation 89** (`aa-Tr_AFN^ADF: Cln^ADF → Min^AFN ∩ SCons^AFN`, p.452):

$$
A' = \{(a, v_a) \mid a \in A,\ v_a \in \min\!\_dec(in, a)\}
$$
$$
R' = \{((a, v_a), (b, v_b)) \mid v_b(a) = \mathbf{f}\}
$$
$$
N' = \{(B, (a, v_a)) \mid v_a(b) = \mathbf{t},\ B = \{(b, v_1),...,(b, v_m)\} = \text{all argument-pairs in } A' \text{ for } b\}
$$

Each ADF argument is duplicated into multiple AFN arguments — one per minimal decisively-in interpretation. Group support encodes the disjunctive nature of ADF acceptance conditions ("any representation suffices"). Casting function: extraction `SC(S) = ⋃_{i=1..n} {a_i}`.

Properties (Theorems 4.10.17, 4.10.18 + Lemmas 4.8.20–4.8.22):
- Source-subclass (cleansed required), target-subclass, overlapping; argument-domain altering, argument-introducing, relation-introducing, relation-removing; generic, semantics-domain altering; semi-structural; strong (not exact except where bijection holds for aa-comp/pref, acy-grd, stb); not ⊕-/⊗-modular.
- `FN^D_{AA}` always in minimal + (strongly) consistent normal form.
- $D$ relation-valid ⇒ $FN^D_{AA}$ weakly + relation-valid; $D$ strongly valid ⇒ $FN^D_{AA}$ strongly valid; weak validity not always preserved alone.
- ADF coherent ↔ AFN pd-acyclic; ADF strongly coherent ↔ pd-acyclic conflict-free; aa-σ ↔ AFN-σ for σ ∈ {admissible, complete, preferred}; stable ↔ stable; acyclic grounded ↔ grounded.
- Counter-example for non-modularity: `D_1 = ({a},{C_a=⊤,C_b=⊤})`, `D_2 = ({a,b},{C_a=¬a,C_b=⊤})`. `FN_2 ≠ FN_1 ∪ FN_2` under both ⊕ and ⊗. *(p.454)*

**Purging procedure** (proof of Theorem 4.10.18, p.706-707) — an algorithmic primitive for converting AFN powerful sequences (which may duplicate underlying arguments) to ADF acyclic pd-evaluations (which cannot):
1. Initialize `seq' := ((b_0, v_{b_0}))`.
2. Find the first `i` with `b_i ≠ b_0`; add `(b_i, v_{b_i})` to `seq'`.
3. Find the first occurrence of each underlying argument different from those already in `seq'`; append.
4. Output `seq'`.

**Translation 90** (sketch only, p.457): Improvement to Translation 89. Group `min_dec(in, a)` by f-part: collect maximal `v' ⊆ min_dec(in, a)` with shared `v^f`. For each group `(a, v')`, choose a minimal hitting set `E ⊆ ⋃_{v ∈ v'} v^t` and add `(B, (a, v'))` where `B` covers `E`. Yields fewer but larger AFN arguments. Correctness proof "similar to Translation 89" but not given.

## Labeling Correspondence Detail (Theorem 4.10.5)

ADF→AF labeling correspondence under Translation 86 (`F^D_lab`), p.690-697:
- `EV^p(a) = {(F,G,B) ∈ A^{ev} | a ∈ F ∪ G}` (partially-acyclic evaluations whose pd-set/sequence contains `a`).
- `ALL(E) = {a ∈ A | EV^p(a) ⊆ E}` (arguments whose every evaluation lies in `E`).
- Partition pd-evaluations as `O^ev = {(F,G,B) | v_2 \text{ blocks}}`, `I^ev = {(F,G,B) | F ∪ G ⊆ v^t, B ⊆ v^f}`; breakers as `I^b = {a^b | every related (F'',G'',B'') ∈ O^ev}`, `O^b = {a^b | exists (F,G,B) ∈ I^ev with a ∈ F ∪ G}`.
- `in(v') = I^{ev} ∪ I^b`; `out(v') = O^{ev} ∪ O^b`.
- Three-valued admissible / complete / preferred / grounded labelings of D ↔ admissible / complete / preferred / grounded labelings of `F^D_lab`, with `v^t = ⋃ in(v')` and `v^f = ALL(out(v'))` (complete/preferred/grounded). **Admissible direction is asymmetric** — Example 153 (p.429) shows AF admissible labelings that fail to give ADF admissible. Complete/preferred/grounded are bijective.

## Chapter 5 (Related Work) and Chapter 6 (Conclusions)

Chapter 5 (p.463-465) anchors Polberg's translations in the prior literature: DW11 (faithful/exact framework), GS14 (decomposing ADFs / ⊗-⊕ operators), CLS09/10/13/15 (BAFs), BES+13 (ADFs revisited), BDW11 (specialized ADF translations limited to stable/grounded/model — Ell12 critique), Ell12 (alternative ADF→AF, ADF→BADF — limited to propositional acceptance, no support cycles, no extension semantics), NP07, BCGG11, MBC11, BGvdTV09, Gab09, PO14a/PO14b, CK14, GRS15.

Chapter 6 (p.466-470) Conclusions:
- "ADFs emerged as one of the most general tools for abstract argumentation, capable of handling even the extended argumentation framework." *(p.467)*
- "In a certain sense, this thesis can be seen as an attempt to organize and unify various frameworks and translations available in the literature." *(p.466)*
- "The precise correspondence between the extension-based and labeling-based semantics that holds in the Dung setting, does not fully carry over." *(p.466)*
- Future-work bullets: (1) categorize ADF-AFN within DW11's classification, (2) complexity analysis (the least attention paid in this thesis), (3) more advanced ADF modularity, (4) BAF "missing" grounded/complete semantics, (5) BAF subclasses where semantic classification collapses analogously to AADF⁺ for ADFs, (6) labeling-based ADF→AF strengthening using Ell12 ideas.

## Proof Appendix Structure (A1-A11, p.484-710)

The appendix follows the same chapter sequence:
- **A1** Background — proofs for §2.1.4 EAF (Th 2.1.47, 2.1.55, 2.1.60, Lemma 2.1.61), §2.2.1 BAF (Lemma 2.2.8 BAF Fundamental Lemma, 2.2.12, 2.2.16, 2.2.28, 2.2.30).
- **A2** ADF / Chapter 3 — proofs for §3.1, §3.2, §3.3 lemmas, plus complexity proofs §A2.1 (Propositions 3.7.3-3.7.63 + Lemmas 3.7.39, 3.7.59 with QBF reductions).
- **A3** Normal forms / subclasses — proofs for §4.2 Theorems 4.2.5, 4.2.7, 4.2.13, 4.2.15 (long), 4.2.16, 4.2.18, 4.2.20, 4.2.22, 4.2.23, 4.2.25, 4.2.28, 4.2.31-45, 4.2.50, 4.2.51, 4.2.54, 4.2.56-58 (consistency forms), Lemmas 4.2.67, 4.2.71, 4.2.73, 4.2.77 (subclass-lattice).
- **A4** AF translations — Th 4.3.6, 4.3.7, 4.3.9, 4.3.10, 4.3.18, 4.3.19, 4.3.20.
- **A5** SETAF translations — Th 4.4.1, 4.4.2, 4.4.6, 4.4.11, 4.4.12, 4.4.15 + Lemmas 4.4.13, 4.4.14.
- **A6** AFRA translations — Th 4.5.2, 4.5.3, 4.5.6.
- **A7** EAF/EAFC translations — Th 4.6.2, 4.6.4, 4.6.11, 4.6.15, 4.6.18, 4.6.19, 4.6.20, 4.6.21, 4.6.28, 4.6.29, 4.6.32, 4.6.36, 4.6.37, 4.6.38, 4.6.39, 4.6.42, 4.6.47 + Lemmas 4.6.30, 4.6.31, 4.6.40, 4.6.41.
- **A8** BAF translations — Th 4.7.2, 4.7.3, 4.7.4, 4.7.9, 4.7.10, 4.7.12, 4.7.14, 4.7.15, 4.7.16.
- **A9** AFN translations — Th 4.8.2, 4.8.4, 4.8.5, 4.8.9, 4.8.11, 4.8.12, 4.8.13, 4.8.15, 4.8.16, 4.8.17, 4.8.18, 4.8.19, 4.8.23, 4.8.24 + Lemmas 4.8.20-4.8.22.
- **A10** EAS translations — Th 4.9.3, 4.9.4, 4.9.6, 4.9.7, 4.9.8, 4.9.10, 4.9.11, 4.9.12, 4.9.13, 4.9.14, 4.9.15, 4.9.16, 4.9.17, 4.9.18, 4.9.21 + Lemmas 4.9.19, 4.9.20.
- **A11** ADF translations — Th 4.10.1, 4.10.2, 4.10.3, 4.10.4, 4.10.5 (long), 4.10.8, 4.10.10, 4.10.17, 4.10.18 + Proposition 4.10.13.

Recurring proof patterns:
1. Pick σ-extension on source side; build target-side image (often using primed/bypass/η-sentinel auxiliary set); prove iff for each σ ∈ {cf, adm, comp, pref, grd, stb}; close via Theorems 2.1.11 / 2.2.31 / 2.2.48 / 3.3.21 to lift to preferred / grounded / stable.
2. Stable semantics requires a separate argument — model ↔ ⊆-maximal complete fails so direct attack-on-everything-outside is needed.
3. Conflict-free is the singularly asymmetric semantics — flagged in nearly every translation theorem.
4. AADF⁺ status is achieved iff source is bounded hierarchical (EAF) or strongly valid (AFN/EAS) or minimal+strongly-valid; otherwise only BADF + cleansed + weakly valid.
5. Range type chosen by source: EAF/EAFC use partially acyclic `v_E^p`; AFN uses fully acyclic `v_E^a`. Different defense-cycle structure drives the choice.

## Open Questions

- [ ] Several "open in this thesis" items: ADF relation-valid translation construction (p.176); strong-validity translation construction for AFN/EAS/ADF (p.165, p.179); exact AFN→AF admissible/preferred construction (Theorem 4.8.6 existence-only, p.355); EAS→SETAF modular translation (p.398).
- [ ] Whether *faithful* (not exact) translations exist for EAF→{AF/SETAF/AFRA/AFN} at admissible / preferred level — conjectured "no" but not proven (pp.279, 284, 286, 298).
- [ ] Sufficient conditions for SETAF conflict-free signatures (p.449) — only downward-closed is necessary.
- [ ] Tightening complexity gaps: Skept_{ca₁-prf} is Π_3^P-hard but only known to be in Π_4^P; Cred_{ca₁-cmp}, Cred_{ca₁-prf} are Σ_2^P-hard but only known to be in Σ_3^P (p.116, p.118, p.120).

## Related Work Worth Reading

- **BW10 (Brewka, Woltran)** — original Abstract Dialectical Frameworks. The semantics this thesis fixes.
- **BES+13 (Brewka et al.)**, **Str13a (Strass)** — labeling-based ADF semantics. Polberg's xy-classification clarifies their relation to extension semantics.
- **Pol14a (Polberg, Wallner, Woltran)**, **Pol15 (Polberg)** — earlier conference papers introducing ca₁ and ca₂ respectively.
- **PO14a, PO14b (Polberg, Oren)** — set-AFN and EAS minimal/relation/strong validity, used throughout §4.2 and §4.6–4.9.
- **CLS09, CLS10, CLS13, CLS15 (Cayrol, Lagasquie-Schiex, et al.)** — BAF lineage. Polberg extends, classifies, and corrects (Theorem 4.7.8 deprecation).
- **Nou13, NR11 (Nouioua, Risch)** — set-AFN and binary AFN. Polberg's Theorem 4.8.6 contradicts NR11's claim that AFNs are strictly more expressive than AFs at admissible level.
- **MP10 (Modgil, Prakken)** — collective defense attacks, EAFC; the fix for EAF design controversies.
- **Mod07, Mod09a, Mod09b, MBC11 (Modgil, Bench-Capon)** — EAF lineage and meta-level AF translations.
- **BCM09, BCGG09, BCGG11 (Cayrol, Devred, Lagasquie-Schiex et al.)** — AFRA original. Polberg adopts the framework, fixes proofs, adds the BAF target.
- **NP07 (Nielsen, Parsons)** — SETAF original.
- **VBVDT11 (Villata, Boella, van der Torre, Boucher-Genesse)** — attack semantics for AFs; rejected as primary AFRA-target path.
- **Gab09 (Gabbay)** — meta-level argumentation.
- **AC98, MP13 (Amgoud, Cayrol; Modgil, Prakken)** — preference-based and structured argumentation; cited for attack strengths that BAF lacks.
- **ABN13 (Amgoud, Ben-Naim)** — ranking-based semantics; closer to value/preference reasoning, suggested as alternative for support-as-weak-preference.
- **DDLW15, Dyr14, GLW16, DLSW16 (Dunne, Dvořák, Linsbichler, Spanring, Woltran et al.)** — realizability / signatures of AF semantics. Theorem 2.3.6 is lifted from this lineage.
- **GS14 (Gaggl, Strass)** — ⊗ / ⊕ ADF combine operators.
- **CK14 (Caminada, Kakas)** — subframework normal forms for AF.
- **GRS15 (Gaggl, Rudolph, Strass)** — minimum redundancy and reducts.
- **Wal14 (Walther)** — labeling-based ADF complexity baseline.
- **SW14, SW15 (Strass, Wallner)** — BADF complexity, D^P class.
- **DT09, JV99a (Dung, Toni; Jakobovits, Vermeir)** — argumentation as dialogue, motivation for inside/outside classification.
- **DW11 (Dvořák, Woltran)** — translation strength definitions, exact/faithful.
- **DGLW15 (Dyrkolbotn, Gaggl, Linsbichler, Woltran)** — EAF lineage.
- **ORL10, ON08 (Oren, Reed, Luck)** — evidential argumentation systems.
- **CMDM05a, CMDM05b (Coste-Marquis, Devred, Marquis)** — prudent / careful semantics, relevant to bypass consistency form preservation.
- **Imi87 (Imielinski)** — modularity origins.
- **Got95, Lib14, Jan99 (Gottlob; Liberatore; Janhunen)** — faithfulness of translations.
- **CA07** — rationality postulates referenced in MP10 / EAFC justification.

## Collection Cross-References

### Already in Collection
- [On the acceptability of arguments and its fundamental role in nonmonotonic reasoning, logic programming and n-person games](../Dung_1995_AcceptabilityArguments/notes.md) — cited as **[Dun95]**, the foundational AF this entire thesis generalizes from. Polberg's Chapter 2 §2.1 takes Dung's admissible/complete/preferred/grounded/stable/semi-stable directly as the AF baseline; every translation in Chapter 4 is measured against AF semantics.
- [Abstract Dialectical Frameworks](../Brewka_2010_AbstractDialecticalFrameworks/notes.md) — cited as **[BW10]**, the seminal ADF paper by Brewka & Woltran (KR 2010). The thesis's entire Chapter 3 develops semantics on top of the BW10 ADF formalism (acceptance conditions on argument nodes, link types attacker/supporter/redundant/dependent, three-valued labelings) and Chapter 4 places ADF as the most expressive translation target.
- [Abstract Dialectical Frameworks Revisited](../Brewka_2013_AbstractDialecticalFrameworksRevisited/notes.md) — cited as **[BES+13]** (Brewka, Ellmauthaler, Strass, Wallner, Woltran, IJCAI 2013). The cleaned-up ADF semantics that the thesis takes as Chapter 2's definitional starting point; Polberg explicitly extends this with new extension-based semantics that handle support cycles separately from labeling-based ones.
- [On the evaluation of argumentation formalisms](../Caminada_2007_EvaluationArgumentationFormalisms/notes.md) — cited as **[CA07]**, Caminada & Amgoud's rationality postulates paper. Polberg uses these postulates as the evaluation criteria in §3.6 across all 16 EAFC semantics × 24 properties.
- [Reasoning about preferences in argumentation frameworks](../Modgil_2009_ReasoningAboutPreferencesArgumentation/notes.md) — cited as **[Mod09a]/[Mod09b]** (the AIJ 173:901-934 paper, listed twice as a printing duplication in the thesis bibliography). Source for EAF preferences, which Polberg fixes via EAFC.
- [A general account of argumentation with preferences](../Modgil_2018_GeneralAccountArgumentationPreferences/notes.md) — cited as **[MP13]** (Modgil & Prakken, AIJ 195:361-397, 2013; the directory uses the canonical paper-of-record year for the AIJ version). The canonical ASPIC+ with preferences paper, used in the thesis's Chapter 2 §2.1 ASPIC argumentation definition (Definition 2.1.20) and as the reference structured-argumentation system the thesis compares to ADF.
- [Symmetric Argumentation Frameworks](../Coste-Marquis_2005_SymmetricArgumentationFrameworks/notes.md) — cited as **[CMDM05c]**. The symmetric AF subclass discussion ties into Polberg's normal-form pipeline in Chapter 4 §4.2 (minimal forms, redundancy-free forms).
- [Prudent Semantics for Argumentation Frameworks](../Coste-Marquis_2005_PrudentSemantics/notes.md) - cited as **[CMDM05b]**. The prudent-semantics odd-path exclusion rule is relevant to Polberg's discussion of bypass consistency and form preservation, because it constrains accepted sets by indirect attack structure rather than only direct attacks.
- [Ranking-based semantics for argumentation frameworks](../Amgoud_2013_Ranking-BasedSemanticsArgumentationFrameworks/notes.md) — cited as **[ABN13]** (Amgoud & Ben-Naim, SUM 2013). Background reference for graded acceptability that Polberg flags as orthogonal to ADF's xy-classified two/three-valued semantics.
- [A new approach for preference-based argumentation frameworks](../Amgoud_2011_NewApproachPreference-basedArgumentation/notes.md) — cited as **[AV11]** (Amgoud & Vesic, AMAI 63:149-183). Cited in Chapter 2 background for preference-based AF lineage.

### New Leads (Not Yet in Collection)
- **[BPW14]** Brewka, Polberg, Woltran (2014) — *Generalizations of Dung frameworks and their role in formal argumentation*, IEEE Intelligent Systems 29(1):30-38. Self-contained companion to this thesis; high relevance — survey-level companion to the translation taxonomy in Chapter 4.
- **[Str13a]** Strass (2013) — *Approximating operators and semantics for abstract dialectical frameworks*, AIJ 205:39-70. The approximation-fixpoint-theory foundation for ADF semantics that BES+13 and the thesis depend on.
- **[SW14] / [SW15]** Strass & Wallner — *Analyzing the Computational Complexity of Abstract Dialectical Frameworks via Approximation Fixpoint Theory*, KR 2014 / AIJ 226:34-74 (2015). The complexity-theory companion to the thesis's Chapter 3 §3.7 complexity table; relevant if propstore wants to reason about ADF query cost.
- **[GS14]** Gaggl & Strass (2014) — *Decomposing abstract dialectical frameworks*, COMMA 2014. SCC-style decomposition for ADFs; relevant for any propstore implementation that reuses Baroni-style modular extension computation.
- **[GRS15]** Gaggl, Rudolph, Strass (2015) — *On the computational complexity of naive-based semantics for ADFs*, IJCAI 2015. Naive-family complexity matching Polberg's xy-classification.
- **[Püh15]** Pührer (2015) — *Realizability of three-valued semantics for ADFs*, IJCAI 2015. Signature/realizability extension of DLSW16's binary-AF result to three-valued ADF labeling.
- **[DDLW15]** Dunne, Dvořák, Linsbichler, Woltran (2015) — *Characteristics of multiple viewpoints in abstract argumentation*, AIJ 228:153-178. Realizability and signature theory for AFs, foundational for the impossibility theorems Polberg uses in Chapter 4.
- **[Pra14]** Prakken (2014) — *On support relations in abstract argumentation as abstractions of inferential relations*, ECAI 2014. Directly relevant for propstore: when do bipolar/support edges in the source layer cleanly map to ASPIC+ inference rules, and when do they not.
- **[BDW11]** Brewka, Dunne, Woltran (2011) — *Relating the semantics of abstract dialectical frameworks and standard AFs*, IJCAI 2011. Predecessor for Chapter 4 ADF↔AF translation discussion (Translations 82-90 and the impossibility result).
- **[DW11]** Dvořák & Woltran (2011) — *On the intertranslatability of argumentation semantics*, JAIR 41(2):445-475. The translation-strength definitions (exact, faithful, modular, etc.) Polberg uses as her classification axes.
- **[CK14]** Croitoru & Kötzing (2014) — *A normal form for argumentation frameworks*, TAFA 2014. Predecessor for Chapter 4 §4.2 normal-form pipeline.
- **[Wal14]** Wallner (2014) — *Complexity Results and Algorithms for Argumentation*, PhD thesis Vienna University of Technology. Sister thesis at Vienna under Woltran; complementary complexity treatment.
- **[BCG11]** Baroni, Caminada, Giacomin (2011) — *An introduction to argumentation semantics*, KER 26(4):365-410. Background survey paper Polberg uses for AF semantics introduction.
- **[NR11] / [Nou13]** Nouioua & Risch / Nouioua — AFNs (Argumentation Frameworks with Necessities) papers. Source of the AFN formalism Polberg uses extensively.
- **[ON08] / [Ore07]** Oren & Norman / Oren PhD thesis — Evidential argumentation systems (EAS). Source of the EAS formalism Polberg uses.

### Supersedes or Recontextualizes
- **None directly.** This thesis is a research compendium, not a successor to any single collection paper. It does provide the most thorough single source for the basic / coalition / attack-propagation / defender translation pattern catalogue and the ADF semantics xy-classification — both of which subsume scattered earlier results.

### Cited By (in Collection)
- (none found)
- Note: Polberg's later co-authored work (Hunter & Polberg 2018/2019, Polberg & Doder 2014, Polberg/Hunter/Thimm 2017, Polberg & Hunter 2018, Hunter/Polberg/Potyka 2018, Hunter/Polberg/Thimm 2018/2020, Thimm/Polberg/Hunter 2018, Potyka/Polberg/Hunter 2018) is cited by [Hunter_2017](../Hunter_2017_ProbabilisticReasoningAbstractArgumentation/notes.md), [Hunter_2021](../Hunter_2021_ProbabilisticArgumentationSurvey/notes.md), [Doutre_2018](../Doutre_2018_ConstraintsChangesSurveyAbstract/notes.md), [Thimm_2012](../Thimm_2012_ProbabilisticSemanticsAbstractArgumentation/notes.md), [Potyka_2019](../Potyka_2019_PolynomialTimeEpistemicProbabilistic/notes.md), [Riveret_2017](../Riveret_2017_LabellingFrameworkProbabilisticArgumentation/notes.md), and others — but none cite *this 2017 thesis* directly. The thesis is the formal foundation Polberg's later probabilistic-argumentation papers rest on.

### Conceptual Links (not citation-based)
- [Acceptability of Arguments in Bipolar Argumentation Frameworks](../Cayrol_2005_AcceptabilityArgumentsBipolarArgumentation/notes.md) — **Strong**. Polberg cites later Cayrol & Lagasquie-Schiex BAF papers ([CLS09]/[CLS10]/[CLS13]/[CLS15]) but not this 2005 paper directly. The 2005 paper is the foundational BAF construction and the d/s/c-admissibility hierarchy that Polberg's Chapter 4 §4.6 BAF translations build on. The thesis's "BAF Fundamental-Lemma failure" criticism (which forces `d-`complete/`d-`grounded) directly engages issues introduced in this earlier Cayrol paper.
- [Issue of reinstatement in argumentation](../Caminada_2006_IssueReinstatementArgumentation/notes.md) — **Strong**. Caminada's three-valued reinstatement labelling (in/out/und) is the direct ancestor of Polberg's EAFC labelling chapter §3.4 (the Eq family). Polberg's standard/preferred/grounded/stable/complete/semi-stable/stage/ideal/eager EAFC labellings extend Caminada's framework to the EAFC setting.
- [Bipolarity in Argumentation Frameworks](../Amgoud_2008_BipolarityArgumentationFrameworks/notes.md) — **Strong**. Survey of BAF bipolarity (defeat + support, supported defeat). Conceptually adjacent to Polberg's BAF translation chapter §4.6 — same problem space (when does support combine with attack), different formal toolkit.
- [SCC-Recursiveness: General Schema for Argumentation Semantics](../Baroni_2005_SCC-recursivenessGeneralSchemaArgumentation/notes.md) — **Moderate**. Polberg cites BG07/BG08/BG09 (Baroni & Giacomin) extensively; BG05 is the original SCC-recursive schema and is the methodological precedent for compositional semantics evaluation Polberg performs at scale.
- [Principle-based Evaluation of Extension-based Argumentation Semantics](../Baroni_2007_Principle-basedEvaluationExtension-basedArgumentation/notes.md) — **Strong**. Polberg's §3.6 evaluates 16 EAFC semantics against 24 Caminada-style postulates; this is exactly Baroni & Giacomin's principle-based evaluation methodology applied at thesis scale to the EAFC setting.
- [The ASPIC+ Framework for Structured Argumentation](../Modgil_2014_ASPICFrameworkStructuredArgumentation/notes.md) — **Moderate**. Polberg's Chapter 2 §2.1 includes the full ASPIC structured-argumentation definition (Definition 2.1.20). For propstore: Polberg's translation pattern catalogue (basic / coalition / attack-propagation / defender) is a complementary lens for evaluating whether ASPIC+ instantiated arguments preserve their conflict structure when reduced to a Dung AF.
- [Revisiting Preferences in Argumentation](../Modgil_2011_RevisitingPreferencesArgumentation/notes.md) — **Moderate**. Polberg cites [MP10] and [MP13]; this Modgil 2011 paper is part of the same preference-handling lineage and is conceptually close to Polberg's EAFC fix.
- [Existence and Multiplicity of Extensions in Dialectical Argumentation](../Verheij_2002_ExistenceMultiplicityExtensionsDialectical/notes.md) — **Moderate**. Verheij's DEFLOG dialectical framework is conceptually related to ADFs; Polberg does not cite it directly but the dialectical lineage informs Chapter 6's positioning of ADF among logic-programming-style dialectical systems.
- [Merging Dung's Argumentation Systems](../Coste-Marquis_2007_MergingDung'sArgumentationSystems/notes.md) — **Moderate**. Polberg cites CMDM05a/b/c; CM07 on merging is conceptually adjacent to Polberg's translation work — both move between argumentation systems, one preserving extensions across translations, the other across merge operations.
- [Prudent Semantics for Argumentation Frameworks](../Coste-Marquis_2005_PrudentSemantics/notes.md) - **Moderate**. Polberg's translation and normal-form results repeatedly track which graph transformations preserve extension semantics; prudent semantics adds an indirect-attack closure constraint that any exact translation would have to preserve, not just ordinary direct conflict-freeness.
- [Characterizing Strong Equivalence between Argumentation Frameworks](../Oikarinen_2010_CharacterizingStrongEquivalenceArgumentation/notes.md) — **Moderate**. Strong equivalence kernel theory for AFs is conceptually adjacent to Polberg's normal-form pipeline (minimal/redundancy-free/cleansed forms); both characterize when AF/EAFC/ADF graphs can be simplified without changing extension semantics.
- [Probabilistic Reasoning in Abstract Argumentation](../Hunter_2017_ProbabilisticReasoningAbstractArgumentation/notes.md) — **Moderate**. Hunter's epistemic probabilistic AF is conceptually layered above a Dung AF; combining it with Polberg's ADF→AF translation impossibility result (Chapter 4 §4.10 Theorem 4.10.6) suggests propstore should not silently reduce probabilistic ADFs to probabilistic AFs.
- [AGM Meets Abstract Argumentation](../Baumann_2015_AGMMeetsAbstractArgumentation/notes.md) — **Moderate**. AGM revision over Dung AFs interacts with Polberg's translation-preservation theorems: a translation that is exact for σ also commutes with σ-AGM revision iff the kernel operator is preserved. Relevant for any propstore work that wants to integrate the existing belief_set AGM revision with ADF-shaped contexts.
