---
title: "Answer-set programming encodings for argumentation frameworks"
authors: "Uwe Egly, Sarah Alice Gaggl, Stefan Woltran"
year: 2010
venue: "Argument & Computation 1(2):147-177"
doi_url: "https://doi.org/10.1080/19462166.2010.486479"
pages: "147-177"
affiliation: "Institute of Information Systems 184, Vienna University of Technology, Favoritenstrasse 9-11, A-1040 Vienna, Austria"
---

# Answer-set programming encodings for argumentation frameworks

## One-Sentence Summary
Presents fixed-query disjunctive-datalog (ASP) encodings for the principal abstract argumentation semantics — conflict-free, stable, admissible, complete, grounded, preferred, semi-stable — plus generalisations (value-based VAFs and bipolar BAFs), packaged as the ASPARTIX system; the encoding's data complexity matches the natural complexity class of each semantics, with disjunction + saturation reserved for the Σ₂ᴾ/Π₂ᴾ-hard preferred and semi-stable cases. *(p.147)*

## Problem Addressed
Reasoning in abstract argumentation frameworks (AFs) is intractable in general (NP-complete to Σ₂ᴾ-complete depending on semantics). Authors want to avoid building a dedicated solver per semantics and instead reduce all of them uniformly to ASP, where mature solvers (DLV) already exist. The encoding is a single fixed query π_e per semantics e; only the input AF F̂ varies. *(p.147-149)*

## Key Contributions
- Uniform fixed-query disjunctive-datalog encodings for cf, stable, admissible, complete, grounded, preferred, and semi-stable semantics. *(p.149, Theorem 3.9 p.168)*
- Saturation-based encodings (using disjunction with stratification meta-rules) for Σ₂ᴾ/Π₂ᴾ-complete preferred and semi-stable semantics so that complexity matches naturally. *(p.156-159, p.164-168)*
- Encodings for generalised AFs: value-based AFs (VAFs, Bench-Capon 2003), bipolar AFs (BAFs, Cayrol & Lagasquie-Schiex 2005) with safe / closed-under-support refinements (s-/c-admissible, s-/c-preferred). *(Section 4, p.170-173)*
- Combinator queries for Π₂ᴾ-complete metaproblems: coherence test (pref(F) ⊆ stable(F), Cor 3.10 p.169), VAF coherence (Cor 4.5 p.171), semi=preferred coincidence test (Cor 3.11 p.169).
- Implementation as ASPARTIX system, hosted at www.dbai.tuwien.ac.at/research/project/argumentation/systempage/ — reuses DLV. Preliminary tests handle 100+ arguments across all considered semantics. *(Section 5, p.173-174)*
- Splitting-set theorem applications to factor proofs (cf-guess + check, stability check, admissibility check, complete via undefended). *(p.150-151, 158-160, 161)*

## Methodology
- Fix the ASP formalism: disjunctive datalog under answer-set semantics (Gelfond–Lifschitz reduct), with constraints, default negation, disjunction, optional stratification.
- Represent an AF F = (A, R) as the input database F̂ = {arg(a) | a ∈ A} ∪ {defeat(a,b) | (a,b) ∈ R}.
- Use unary predicates in(·)/out(·) to guess subsets S ⊆ A.
- Layer encodings: π_cf (conflict-free guess + check) → π_stable, π_adm by adding "defeated/undefeated" rules → π_comp by adding completeness rules (undefended) → π_pref/π_semi via saturation over admissibility encoding using auxiliary inN/outN predicates and a forced fail atom.
- Express correctness via correspondence S ≅ I (Definition 3.1): bijection between extension collection and answer-set collection given by I ↦ {a | in(a) ∈ I}.
- Splitting Theorem (Lifschitz–Turner 1994 / Proposition 2.1) is the proof workhorse — split top from bottom on the {in, out, arg, defeat} predicates.
- Grounded extension uses an explicit total order on arguments (inf/succ/sup helper predicates) to derive a stratified loop computing defended_upto(X,Y) → defended(X) → in(X). Order is irrelevant semantically; any total order over the constants works. *(p.162-163)*
- Generalised AFs: keep the modules from Section 3 but **redefine the input database and a small adapter module** that derives defeat(·,·) from the new attack/preference/support relations (π_vaf, π_baf).

## Key Equations / Programs

Encoding the input AF as facts: *(p.156)*

$$
\hat F = \{\arg(a) \mid a \in A\} \cup \{\mathrm{defeat}(a,b) \mid (a,b) \in R\}.
$$

Conflict-free guess + check: *(p.157)*

$$
\pi_{cf} = \{\, \mathrm{in}(X) :\!- \mathrm{not}\ \mathrm{out}(X), \arg(X);\quad \mathrm{out}(X) :\!- \mathrm{not}\ \mathrm{in}(X), \arg(X);\quad :\!-\, \mathrm{in}(X), \mathrm{in}(Y), \mathrm{defeat}(X,Y)\,\}.
$$

Stable extension encoding: *(p.158)*

$$
\pi_{\mathrm{stable}} = \pi_{cf} \cup \pi_{\mathrm{srules}};\quad \pi_{\mathrm{srules}} = \{\, \mathrm{defeated}(X) :\!- \mathrm{in}(Y), \mathrm{defeat}(Y,X);\quad :\!-\, \mathrm{out}(X), \mathrm{not}\ \mathrm{defeated}(X)\,\}.
$$

Admissible extension encoding: *(p.160)*

$$
\pi_{\mathrm{adm}} = \pi_{cf} \cup \{\, \mathrm{defeated}(X) :\!- \mathrm{in}(Y), \mathrm{defeat}(Y,X);\quad :\!-\, \mathrm{in}(X), \mathrm{defeat}(Y,X), \mathrm{not}\ \mathrm{defeated}(Y)\,\}.
$$

Complete extension encoding: *(p.161)*

$$
\pi_{\mathrm{comp}} = \pi_{\mathrm{adm}} \cup \{\, \mathrm{undefended}(X) :\!- \mathrm{defeat}(Y,X), \mathrm{not}\ \mathrm{defeated}(Y);\quad :\!-\, \mathrm{out}(X), \mathrm{not}\ \mathrm{undefended}(X)\,\}.
$$

Total-order helpers: *(p.162)*

$$
\pi_< = \{\,\mathrm{lt}(X,Y):\!-\arg(X),\arg(Y),X<Y;\ \mathrm{nsucc}(X,Z):\!-\mathrm{lt}(X,Y),\mathrm{lt}(Y,Z);\ \mathrm{succ}(X,Y):\!-\mathrm{lt}(X,Y),\mathrm{not}\,\mathrm{nsucc}(X,Y);\ \mathrm{ninf}(Y):\!-\mathrm{lt}(X,Y);\ \mathrm{inf}(X):\!-\arg(X),\mathrm{not}\,\mathrm{ninf}(X);\ \mathrm{nsup}(X):\!-\mathrm{lt}(X,Y);\ \mathrm{sup}(X):\!-\arg(X),\mathrm{not}\,\mathrm{nsup}(X)\,\}.
$$

Defended computation (rules 25-29) and π_ground = π_< ∪ π_defended ∪ {in(X) :- defended(X)}; stratified, constraint-free → exactly one answer set; |=c and |=s coincide for grounded. *(p.162)*

Preferred-extension saturation module π_satpref (rules 31-37 around the inN/outN guess of T): *(p.164)*

$$
\pi_{\mathrm{satpref}} = \{\,\mathrm{inN}(X)\vee\mathrm{outN}(X) :\!- \mathrm{out}(X);\ \mathrm{inN}(X) :\!- \mathrm{in}(X);\ \mathrm{fail} :\!- \mathrm{eq};\ \mathrm{fail} :\!- \mathrm{inN}(X),\mathrm{inN}(Y),\mathrm{defeat}(X,Y);\ \mathrm{fail} :\!- \mathrm{inN}(X),\mathrm{outN}(Y),\mathrm{defeat}(Y,X),\mathrm{undefeated}(Y);\ \mathrm{inN}(X) :\!- \mathrm{fail},\arg(X);\ \mathrm{outN}(X) :\!- \mathrm{fail},\arg(X);\ :\!- \mathrm{not}\,\mathrm{fail}\,\}.
$$

Helper π_eq tests T = S using inf/succ-driven loop over eq_upto. Helper π_undefeated computes undefeated(X) using inf/succ loop over outN. *(p.166)*

Combined preferred encoding: *(p.166)*

$$
\pi_{\mathrm{pref}} = \pi_{\mathrm{adm}} \cup \pi_< \cup \pi_{\mathrm{eq}} \cup \pi_{\mathrm{undefeated}} \cup \pi_{\mathrm{satpref}}.
$$

**Proposition 3.7**: pref(F) ≅ AS(π_pref(F̂)). *(p.166)*

Semi-stable: replace π_eq with π_eq⁺ (test S_R⁺ = T_R⁺ rather than S = T), and π_satpref with π_satsemi which saturates whenever S_R⁺ ⊊ T_R⁺ does not hold. *(p.167-168)*

$$
\pi_{\mathrm{semi}} = \pi_{\mathrm{adm}} \cup \pi_< \cup \pi_{\mathrm{eq}}^{+} \cup \pi_{\mathrm{undefeated}} \cup \pi_{\mathrm{satsemi}}.
$$

**Proposition 3.8**: semi(F) ≅ AS(π_semi(F̂)). *(p.168)*

**Theorem 3.9** (master): For any AF F and e ∈ {stable, adm, pref, semi, comp, ground}, e(F) ≅ AS(π_e(F̂)). *(p.168)*

Splitting Theorem (Proposition 2.1): For program Π with splitting set S and I ⊆ B_𝒰, I ∈ AS(Π) iff I ∈ AS(Π_S^t(J)) where J = I ∩ B_{Π_S^b} and J ∈ AS(Π_S^b). *(p.151)*

Grounded extension as least fixed point of Γ_F(S) = {a ∈ A | a is defended by S in F}. (Proposition 2.10, p.156)

VAF encoding (adapter): *(p.170)*

$$
\tilde F = \{\arg(a) \mid a \in A\} \cup \{\mathrm{att}(a,b) \mid (a,b)\in R\} \cup \{\mathrm{val}(a,\sigma(a))\mid a\in A\} \cup \{\mathrm{valpref}(v,w)\mid v<w\}.
$$

$$
\pi_{\mathrm{vaf}} = \{\,\mathrm{valpref}(X,Y) :\!- \mathrm{valpref}(X,Z),\mathrm{valpref}(Z,Y);\ \mathrm{pref}(X,Y) :\!- \mathrm{valpref}(U,V),\mathrm{val}(X,U),\mathrm{val}(Y,V);\ \mathrm{defeat}(X,Y) :\!- \mathrm{att}(X,Y),\mathrm{not}\ \mathrm{pref}(Y,X)\,\}.
$$

**Theorem 4.3**: For any VAF F and e ∈ {adm, pref}, e(F) ≅ AS(π_vaf ∪ π_e(F̃)). *(p.170)*

VAF stable (special handling because Bench-Capon 2003 defines stable via *attack*, not *defeat*): *(p.171)*

$$
\pi_{\mathrm{vaf\_stable}} = \pi_{cf} \cup \{\,\mathrm{attacked}(X) :\!- \mathrm{in}(Y), \mathrm{att}(Y,X);\ :\!-\,\mathrm{out}(X), \mathrm{not}\ \mathrm{attacked}(X)\,\}.
$$

**Theorem 4.4**: stable(F) ≅ AS(π_vaf ∪ π_vaf_stable(F̃)). VAF coherence corollary 4.5 p.171.

BAF encoding (defeat = att composed with transitive support): *(p.172)*

$$
\bar F = \{\arg(a) \mid a\in A\} \cup \{\mathrm{att}(a,b)\mid (a,b)\in R_d\} \cup \{\mathrm{support}(a,b)\mid (a,b)\in R_s\}.
$$

$$
\pi_{\mathrm{baf}} = \{\,\mathrm{support}(X,Y) :\!- \mathrm{support}(X,Z),\mathrm{support}(Z,Y);\ \mathrm{defeat}(X,Y) :\!- \mathrm{att}(X,Y);\ \mathrm{defeat}(X,Y) :\!- \mathrm{att}(Z,Y),\mathrm{support}(X,Z);\ \mathrm{defeat}(X,Y) :\!- \mathrm{att}(X,Z),\mathrm{support}(Z,Y)\,\}.
$$

**Theorem 4.8**: For any BAF F and e ∈ {stable, adm, pref}, e(F) ≅ AS(π_baf ∪ π_e(F̄)). *(p.172)*

Refined BAF semantics — safe vs. closed-under-Rs: *(p.172-173)*

- Definition 4.9 (safe / closed). S is safe in F if for each a ∈ A with S defeats a then a ∉ S, and there is no R_s-sequence a₁,...,a_n (n≥2) with a₁∈S, a_n=a. S is closed under R_s if for each (a,b)∈R_s, a∈S iff b∈S.
- Definition 4.10 (s-/c-admissible): S is s-adm if S is safe in F and each a∈S is defended by S; S is c-adm if S is closed under R_s, conflict-free, and each a∈S defended by S.
- Encoded as π_sadm (safe via supported(X) :- in(Y), support(Y,X); :- supported(X), defeated(X)) and π_cadm (closure constraints :- support(X,Y), in(X), out(Y); :- support(X,Y), out(X), in(Y)). *(p.172)*
- Definition 4.11 (s-/c-preferred): set-inclusion-maximal s-adm / c-adm.
- Encoded via π_spref / π_cpref by adding extra fail saturation rules to π_satpref. **Theorem 4.12**: For any BAF F and e ∈ {sadm, cadm, spref, cpref}, e(F) ≅ AS(π_baf ∪ π_e(F̄)). *(p.173)*

## Definitions Captured Verbatim (numbered)

- **Def 2.2 (AF, defeat, defended).** AF is a pair F = (A, R) with A ⊆ 𝒰 finite, R ⊆ A × A. (a,b) ∈ R = "a attacks/defeats b". S ⊆ A defeats b in F if ∃a ∈ S with (a,b) ∈ R. a is defended by S iff for each b ∈ A, if (b,a) ∈ R then S defeats b. *(p.153)*
- **Def 2.4 (conflict-free).** S ⊆ A conflict-free if no a,b ∈ S with (a,b) ∈ R. cf(F) is the collection. *(p.154)*
- **Def 2.5 (stable).** S ∈ cf(F) and each a ∈ A\S is defeated by S. stable(F). *(p.154)*
- **Def 2.6 (admissible).** S ∈ cf(F) and each a ∈ S is defended by S in F. adm(F). *(p.154)*
- **Def 2.7 (preferred).** Subset-maximal admissible. pref(F). *(p.154)*
- **Def 2.8 (semi-stable).** S ∈ adm(F); for each T ∈ adm(F), S_R^+ ⊄ T_R^+ where S_R^+ = S ∪ {b | ∃a ∈ S with (a,b) ∈ R}. (Caminada 2006; Dunne–Caminada 2008). *(p.155)*
- **Def 2.9 (complete, grounded).** S ∈ adm(F) and every a defended by S satisfies a ∈ S. The least complete extension under inclusion is the grounded extension. comp(F), ground(F). *(p.155)*
- **Def 3.1 (correspondence ≅).** Collections 𝒮 ⊆ 2^𝒰 and ℐ ⊆ 2^{B_𝒰} correspond iff (i) for each S ∈ 𝒮 there is I ∈ ℐ with {a | in(a) ∈ I} = S; (ii) for each I ∈ ℐ, {a | in(a) ∈ I} ∈ 𝒮. *(p.156)*
- **Def 4.1 (VAF).** 5-tuple F = (A, R, Σ, σ, <) with σ:A→Σ value-assigning and < an irreflexive, asymmetric preference over Σ. ≪ = transitive closure of <. a defeats b iff (a,b)∈R and (σ(b), σ(a)) ∉ ≪. *(p.170)*
- **Def 4.6 (BAF).** Triple (A, R_d, R_s) with R_d attack and R_s support. a defeats b in BAF if a sequence a₁,...,a_{n+1} from A exists with a₁=a, a_{n+1}=b, and either ((aᵢ,a_{i+1}) ∈ R_s for 1≤i≤n-1 and (a_n,a_{n+1}) ∈ R_d) or ((a₁,a₂)∈R_d and (aᵢ,a_{i+1})∈R_s for 2≤i≤n). *(p.171)*
- **Def 4.9 (safe / closed).** Page 172 — see encodings.
- **Def 4.10 (s-admissible / c-admissible).** Page 172.
- **Def 4.11 (s-preferred / c-preferred).** Page 173.

## Propositions / Theorems

| ID | Statement | Page |
|---|---|---|
| Prop 2.1 | Splitting theorem for ASP | 151 |
| Prop 2.10 | Grounded extension = lfp Γ_F | 156 |
| Prop 3.2 | cf(F) ≅ AS(π_cf(F̂)) | 157 |
| Prop 3.3 | stable(F) ≅ AS(π_stable(F̂)) | 159 |
| Prop 3.4 | adm(F) ≅ AS(π_adm(F̂)) | 160 |
| Prop 3.5 | comp(F) ≅ AS(π_comp(F̂)) | 161 |
| Prop 3.6 | ground(F) ≅ AS(π_ground(F̂)) | 163 |
| Prop 3.7 | pref(F) ≅ AS(π_pref(F̂)) | 166 |
| Prop 3.8 | semi(F) ≅ AS(π_semi(F̂)) | 168 |
| Theorem 3.9 | Master correspondence for all six semantics | 168 |
| Cor 3.10 | Coherence (pref(F) ⊆ stable(F)) iff π_pref(F̂) ∪ {v :- out(X), not defeated(X); :- not v} has no answer set | 169 |
| Cor 3.11 | semi(F) = pref(F) iff π_coincide(F̂) has no answer set | 169 |
| Theorem 4.3 | VAF adm/pref correspondence | 170 |
| Theorem 4.4 | VAF stable correspondence (uses attack-based stability) | 171 |
| Cor 4.5 | VAF coherence | 171 |
| Theorem 4.8 | BAF stable/adm/pref correspondence | 172 |
| Theorem 4.12 | BAF s-/c-admissible & s-/c-preferred correspondence | 173 |

## Complexity Tables

Table 1 (datalog data complexity, completeness): *(p.153)*

| Reasoning | Stratified | Normal | General |
|---|---|---|---|
| ⊨_c (credulous) | P | NP | Σ₂ᴾ |
| ⊨_s (skeptical) | P | coNP | Π₂ᴾ |

Table 2 (decision problems in AFs): *(p.156)*

| Problem | stable | adm | pref | semi | comp | ground |
|---|---|---|---|---|---|---|
| Cred_e | NP-c | NP-c | NP-c | Σ₂ᴾ-c | NP-c | in P |
| Skept_e | coNP-c | (trivial) | Π₂ᴾ-c | Π₂ᴾ-c | in P | in P |

Decision problems: Cred_e (∃ S ∈ e(F) with a ∈ S?), Skept_e (∀ S ∈ e(F), a ∈ S?). *(p.155)*

Table 3 (queries used per task): *(p.169)*

| | stable | adm | pref | semi | comp | ground |
|---|---|---|---|---|---|---|
| Cred | π_stable ⊨_c a | π_adm ⊨_c a | π_adm ⊨_c a (reduces) | π_semi ⊨_c a | π_comp ⊨_c a | π_ground ⊨ a |
| Skept | π_stable ⊨_s a | trivial | π_pref ⊨_s a | π_semi ⊨_s a | π_ground ⊨ a (reduces) | π_ground ⊨ a |

Notes: skeptical preferred falls back to π_pref (Π₂ᴾ); skeptical complete reduces to grounded; credulous preferred reduces to credulous admissible. ground encoding is stratified, so |=_c and |=_s coincide. Only π_pref and π_semi are properly disjunctive (use disjunction in head). *(p.168)*

## Worked Example (running)

F (p.153): A = {a,b,c,d,e}, R = {(a,b),(c,b),(c,d),(d,c),(d,e),(e,e)}.
- cf(F) = {∅, {a},{b},{c},{d},{a,c},{a,d},{b,d}}
- adm(F) = {∅, {a},{c},{d},{a,c},{a,d}}
- stable(F) = {{a,d}}
- semi(F) = {{a,d}} (S_R^+ for {a,c} is {a,b,c,d} ⊊ {a,b,c,d,e} = T_R^+ for {a,d})
- complete(F) = {{a,c},{a,d},{a}}; grounded(F) = {a}; preferred(F) = {{a,c},{a,d}}.

Worked AS computation for π_cf(F̂) lists eight answer sets S_∅, S_a, …, S_bd with the in/out atom assignments (p.157), used to walk through stable/adm/comp/preferred constructions on the same example.

VAF example 4.2 (p.170): A={a,b,c}, R={(b,a),(c,b)}, Σ={red,blue}, σ(a)=σ(b)=blue, σ(c)=red, <={(red,blue)}. Then c defeats b but not b a (since (blue,red) ∉ ≪).

BAF example 4.7 (p.171): A={a,b,c,d,e}, R_d={(a,e),(d,c)}, R_s={(a,b),(b,c),(d,e)}. pref(F) = {{a,b,d}}, spref(F) = {{d},{a,b}}, cpref(F) = {∅}.

## Parameters / Quantities

| Name | Symbol | Units | Default | Range | Page | Notes |
|---|---|---|---|---|---|---|
| Number of arguments handled by ASPARTIX (preliminary) | — | args | — | >100 | 174 | All considered semantics, Dung framework. |
| Universe of constants | 𝒰 | set | — | — | 149 | Countable, with total order < (used by π_<). |
| Predicate arities used | — | — | 1 or 2 | — | various | in/out/arg/defeated/undefended unary; defeat/att/support/lt/succ binary. |

(No empirical effect-size table — paper is theoretical with one practical implementation note.)

## Algorithms / Modules (numbered overview)

1. Build F̂ from input AF: a single pass over arguments and attack tuples. *(p.156)*
2. For semantics e, run DLV on F̂ ∪ π_e and read off answer sets; in(·) ⊆ I gives the extension S = {a | in(a)∈I}. *(p.156, Theorem 3.9 p.168)*
3. For Π₂ᴾ-complete metaproblems (coherence, semi=preferred), wrap π_pref or π_pref + π_semi tests with extra ∃-saturation rules and check for emptiness of the answer-set collection. *(Cor 3.10, 3.11 p.169; Cor 4.5 p.171)*
4. For VAFs/BAFs, prepend the small adapter module (π_vaf or π_baf) that derives defeat(·,·) from the new relations; reuse Section 3 modules unchanged. *(Sections 4.1, 4.2)*

## Methods & Implementation Details
- ASP solver: DLV (Leone et al. 2006), accessed online. *(Section 2.1, p.149)*
- ASPARTIX system page: www.dbai.tuwien.ac.at/research/project/argumentation/systempage/ *(p.173)*
- Choice of saturation technique (rather than naive guess+complement) is what keeps preferred/semi-stable inside Σ₂ᴾ. Saturation proof technique cites Eiter & Polleres (2006). *(p.153)*
- Total order over arguments for π_ground is *implementation detail*; any total order works because the only relevant predicates derived are defended_upto(a,b) for all b — order independent semantically. *(p.162)*
- π_ground is stratified and constraint-free → unique answer set → credulous = skeptical. *(p.168)*
- Preferred/semi encodings reuse modules π_<, π_eq, π_undefeated; only differing in the saturation block.
- Splitting set proofs: each correspondence proof Pp.157-168 uses Splitting on C = {in,out,arg,defeat} to factor π_e into "guess" and "check" parts.
- Ideal semantics implemented in current ASPARTIX (not in paper); cite Faber & Woltran 2009 for the encoding. *(p.173)*

## Figures of Interest
- **Fig 1 (p.155):** Lattice of argumentation semantics — arrows indicate inclusion (stable → semi-stable → preferred → complete → admissible; grounded → complete).
- **Tables 1-3 (pp.153, 156, 169):** complexity and query overview.

## Limitations
- No formal experimental section — only a one-line claim that "more than 100 arguments" works for Dung semantics. Comparison with other implementations explicitly listed as future work. *(p.174)*
- Encoding readability: π_pref is the union of six modules; debugging at scale is non-trivial — paper acknowledges saturation is "quite complicated to encode." *(p.164)*
- Disjunctive programs (π_pref, π_semi) inherit DLV's worst-case overhead; no claim of practical speed against dedicated SAT-based preferred solvers (PrefSat) in this paper.
- No grounded encoding for BAFs given, although authors note it can be put together. *(p.173)*
- Relies on assumption that input order < exists in the ASP solver — true for DLV; not portable to systems without a total order primitive without modification. *(p.162)*

## Arguments Against Prior Work
- Nieves, Osorio, Cortés (2008) and Wakaki & Nitta (2008) ASP encodings: their preferred/semi-stable encodings require **per-instance recompilation of the encoding** (meta-programming translation per AF), whereas ASPARTIX uses a *fixed* disjunctive query and only varies the input database. Authors argue their approach is "more reliable and easily extendible." *(p.174)*
- Wakaki & Nitta (2008): use *labellings* for complete/stable but require additional translations per AF for grounded/preferred/semi-stable. *(p.174)*
- Osorio et al. (2005): admissible-set characterisation via abductive logic programming — only handles preferred via a fixed program in the same manner ASPARTIX does for admissibility. *(p.174)*
- Dispute-derivation systems (CASAPI, Vreeswijk's tool): compute defence sets around a queried argument rather than the entire collection — different problem, less complete. *(p.174)*

## Design Rationale
- "Interpreter approach": single fixed encoding per semantics + variable input AF, justified because the input AF can be changed dynamically without retranslating; supports "what-if" debugging ("What happens if I add this new argument?"). *(p.149)*
- Choice of disjunctive datalog (DLV-style) over normal logic programming: needed for Σ₂ᴾ-complete preferred/semi-stable; saturation requires disjunction in head. *(p.152)*
- Choice of stratified encoding for grounded: tractable subclass; complexity matches polynomial-time grounded reasoning. *(p.161)*
- Modular construction: every harder semantics is a strict superset of an easier one's encoding (pref ⊃ adm ⊃ cf), which makes correctness proofs additive and reuse straightforward. *(Section 3)*
- Splitting Theorem proofs factor each correctness argument into "guess answer-sets are correspondences" and "check rules eliminate wrong guesses."

## Testable Properties
- For every AF F, |stable(F)| = |AS(π_stable(F̂))| with bijection induced by I ↦ {a | in(a)∈I}. *(p.159)*
- For every AF F, π_pref(F̂) is properly disjunctive; AS(π_pref(F̂)) is in Σ₂ᴾ. *(p.166, p.168)*
- π_ground(F̂) has exactly one answer set for any AF F. *(p.163)*
- coherence(F) holds iff a particular extended program has no answer set. *(Cor 3.10, p.169)*
- semi(F) = pref(F) iff π_coincide(F̂) has no answer set. *(Cor 3.11, p.169)*
- For VAF F with the attack-based stable definition (Bench-Capon 2003), stable(F) ≅ AS(π_vaf ∪ π_vaf_stable(F̃)). *(Theorem 4.4, p.171)*
- For BAF F, e(F) ≅ AS(π_baf ∪ π_e(F̄)) for e ∈ {stable, adm, pref}. *(Theorem 4.8, p.172)*
- ASPARTIX terminates on AFs with >100 arguments for all Section-3 semantics in preliminary tests. *(p.174)*

## Relevance to Project
Direct: ASPARTIX is the canonical "argumentation = ASP" reduction baseline that the wider Vienna/argumentation community has built on for over a decade. Any project doing extension enumeration over Dung AFs benefits from these encodings as a known-correct, reusable reference. The technique of (i) fixed query + variable input database, (ii) saturation with auxiliary inN/outN to saturate the second-level guess, and (iii) splitting-set factored proofs is reusable for any new semantics that fits the Σ₂ᴾ template (e.g., new "favoured" semantics, hybrid semantics, or extension-comparison metaproblems).

Specifically usable today:
- π_cf, π_stable, π_adm, π_comp, π_ground modules can be lifted verbatim into a comparison tool.
- The π_satpref saturation module pattern is a template for any "subset-maximal X" semantics where maximality is checked via "no proper superset is X."
- Cor 3.10 (coherence) is a template for any Π₂ᴾ "is e(F) ⊆ e'(F)" metaproblem.

Less directly useful: the BAF s-/c-admissibility refinements presuppose Cayrol & Lagasquie-Schiex's 2005 BAF formalisation; if the project uses a different bipolar formalism (e.g., evidential support, Oren–Norman) those encodings would need adaptation.

## Open Questions
- [ ] Does ASPARTIX scale beyond hundreds of arguments? (Empirical comparison promised as future work, p.174.)
- [ ] Is there an encoding for CF2 semantics (Baroni–Giacomin–Guida 2005) within the same fixed-query paradigm? Authors plan it. *(p.174)*
- [ ] Encoding for grounded extension on BAFs is stated as derivable but not exhibited. *(p.173)*
- [ ] Resolution-based, decomposition-based (SCC), and meta-attack semantics (Modgil 2009) — listed as planned. *(p.174)*

## Notable Cited Work (key follow-ups)
- Bench-Capon (2003) "Persuasion in Practical Argument Using Value-based Argumentation Frameworks" — VAF basis. *(p.170)*
- Bench-Capon & Dunne (2007) survey on argumentation. *(p.149)*
- Caminada (2006) and Dunne & Caminada (2008): semi-stable semantics. *(p.155)*
- Cayrol & Lagasquie-Schiex (2005): BAF basis. *(p.171)*
- Dung (1995): foundational AFs and grounded/admissible/preferred semantics. *(p.154-155)*
- Dunne & Bench-Capon (2002): coherence problem and Π₂ᴾ-completeness. *(p.156, 169)*
- Eiter & Polleres (2006): saturation in ASP. *(p.153)*
- Faber & Woltran (2009) "Manifold Answer-Set Programs for Meta-Reasoning": ideal-semantics encoding used by ASPARTIX. *(p.173)*
- Gelfond & Lifschitz (1991): foundational ASP / answer-set semantics. *(p.149)*
- Leone et al. (2006): DLV system. *(p.149)*
- Lifschitz & Turner (1994): Splitting Theorem. *(p.150)*
- Nieves et al. (2008, 2009), Osorio et al. (2005), Wakaki & Nitta (2008): closest related ASP-based AF systems. *(p.174)*

## Implementation Notes for Project
- If integrating ASPARTIX-style encodings into a Python pipeline, the natural shape is: (1) emit F̂ as DLV-syntax facts; (2) concatenate with a static π_e from a known directory (e.g., asp/aspartix/π_pref.dlv); (3) call DLV (or clingo with disjunctive support); (4) parse atoms in(_) out of each model line.
- The total-order primitive `X < Y` in π_< is DLV-specific; for clingo, replace with `<` over numerically-encoded constants (e.g., emit arg(1), arg(2), ...) or use an explicit total_order/2 fact set.
- Saturation programs (π_pref, π_semi) require disjunctive ASP — clingo --disjunctive (or just disjunction in head) rather than gringo+lp2sat for any tool that expects normal programs.
- For coherence test: build π_pref ∪ {v :- out(X), not defeated(X); :- not v} and check satisfiability — boolean answer.
- DLV's grounding overhead can dominate for AFs with thousands of arguments; this paper does not benchmark there.

## Quotes Worth Preserving
- "fixed queries, such that the input is the only part depending on the actual AF to process." *(p.147)*
- "the complexity of the encoded decision problem of AFs meets the corresponding complexity of the employed datalog fragment." *(p.168)*
- "we believe that our approach is thus more reliable and easily extendible to further formalisms." *(p.174)*

## Current State / Blocker
All 32 PDF pages have been read end-to-end. Notes are written. No outstanding blockers for paper-reader steps. Per the user's instructions I am NOT running steps 7 (reconcile), 8 (index.md), or 9 (provenance stamping). Remaining: write description.md, abstract.md, citations.md, metadata.json, and the per-paper report.
