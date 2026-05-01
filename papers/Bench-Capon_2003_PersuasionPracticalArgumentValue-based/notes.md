# Trevor J. M. Bench-Capon (2003), "Persuasion in Practical Argument Using Value-based Argumentation Frameworks"

## Bibliographic Details

- Title: "Persuasion in Practical Argument Using Value-based Argumentation Frameworks"
- Author: Trevor J. M. Bench-Capon
- Venue: Journal of Logic and Computation 13(3), 429-448
- Year: 2003
- DOI: 10.1093/logcom/13.3.429
- Page images read directly: printed pages 429-448.

## Core Problem

Bench-Capon argues that practical disagreement is often not resolved by proving one side false. In law, ethics, and policy, parties may advance sound arguments that promote different values. Persuasion therefore depends on showing that an argument should be accepted relative to an audience's value ordering, or that it is accepted no matter how the relevant values are ordered (pp. 429-430).

Standard Dung argumentation frameworks identify defensible positions but are often silent about which defensible position should be preferred. The paper extends AFs with values so that the success of an attack depends on the relative strength of the values promoted by attacker and target for a given audience (pp. 430, 435-436).

## Standard AF Background

Section 2 restates Dung AF definitions (p. 431):

- An argumentation framework is `AF = (AR, attacks)`, with `AR` a set of arguments and `attacks subset AR x AR`.
- `attacks(A, B)` means argument `A` attacks argument `B`.
- An argument `A` is acceptable with respect to set `S` when every attacker of `A` is attacked by some member of `S`.
- A set is conflict-free when it contains no pair in the attack relation.
- A set is admissible when it is conflict-free and every member is acceptable with respect to the set.
- A preferred extension is a maximal admissible set.

The paper recalls that every finite AF has a preferred extension, possibly empty, and that credulous acceptance means membership in at least one preferred extension while skeptical acceptance means membership in all preferred extensions (p. 431).

For finite AFs without self-attacks, multiple preferred extensions require a simple directed cycle of even length (Theorem 2.6, p. 432). Acyclic frameworks can be solved by repeatedly selecting unattacked arguments, removing the arguments they attack, and recursing on the remainder. Bench-Capon names this algorithm `EXTEND(AF, attacks)` (pp. 432-433).

## Practical Argument Motivation

The practical argument pattern used in the paper is: perform action `A` in circumstances `C` because performing `A` in `C` would promote some good `G` (p. 434). Such an argument may be attacked by disputing circumstances, disputing whether the action promotes the good, proposing an incompatible action that promotes another good, or arguing that the stated good is not a good worthy of promotion (pp. 434-435).

The paper assumes the promoted values are acceptable and focuses on the value-sensitive question: when does an attack succeed? An attack may fail when the target argument promotes a value preferred to the attacker's value. This motivates distinguishing attack from defeat: an attack is a structural relation; defeat is a successful attack for an audience (p. 435).

## Value-Based Argumentation Frameworks

Definition 5.1 (p. 435): a value-based argumentation framework is a 5-tuple

```text
VAF = (AR, attacks, V, val, P)
```

where:

- `AR` is a finite set of arguments.
- `attacks` is an irreflexive binary relation on `AR`.
- `V` is a nonempty set of values.
- `val` maps every argument in `AR` to an element of `V`.
- `P` is the set of possible audiences.

`val(A)` is the value promoted or defended by accepting `A` (p. 435).

Definition 5.2 (pp. 435-436): an audience-specific VAF is

```text
VAF_a = (AR, attacks, V, val, Valpref_a)
```

where `Valpref_a` is a transitive, irreflexive, asymmetric preference relation on `V`. The paper writes `valpref(v1, v2)` to mean that `v1` is preferred to `v2`.

Definition 5.3 (p. 436): for audience `a`, argument `A` defeats argument `B` iff:

```text
attacks(A, B) and not valpref(val(B), val(A))
```

All attacks succeed when both arguments promote the same value, or when no preference between the two values has been defined. If `V` is a singleton, or if there are no preferences, the audience-specific VAF behaves like a standard AF. Defeat is always relative to a particular audience (p. 436).

Definitions 5.4-5.7 lift Dung-style acceptability, conflict-freeness, admissibility, and preferred extension to audience-relative defeat rather than raw attack (p. 436). For any AVAF, one can construct a corresponding ordinary AF by removing attacks that fail against the audience's value ordering. The preferred extension of this derived AF contains the same arguments as the audience-specific VAF preferred extension (p. 436).

If a VAF has no cycles in which all arguments pertain to the same value, then the corresponding AF will contain no cycles for a given audience because a cycle is broken where an inferior value attacks a superior value. Such cases have a unique, nonempty preferred extension for each audience (p. 436).

## Objective and Subjective Acceptance

The two-value example in Figure 2 has `A(red) -> B(blue) -> C(blue)` (p. 437). If red is preferred to blue, the preferred extension is `{A, C}`. If blue is preferred to red, the preferred extension is `{A, B}`. Thus `A` is accepted under both audiences, while `B` and `C` are each accepted only under some audience (p. 437).

Definition 6.1 (p. 437): argument `A` is objectively acceptable iff for every audience `p in P`, `A` is in every `preferred_p`.

Definition 6.2 (p. 437): argument `A` is subjectively acceptable iff for some audience `p in P`, `A` is in some `preferred_p`.

An argument that is neither objectively nor subjectively acceptable is indefensible (p. 437).

The paper notes a useful consequence: objective acceptance of an attacked argument requires fewer values than arguments. Otherwise an audience can always prefer the value of an attacker to the value of the target (p. 437).

## Chains, Lines of Argument, and Tractability

Definition 6.3 (p. 438): an argument chain is a sequence of same-valued arguments in which the first has no attacker in the chain, and every later argument is attacked only by the previous argument in the chain. Because all arguments in a chain share a value, all attacks in the chain succeed. If the first argument is accepted, every odd argument in the chain is accepted and every even argument is defeated; if the first is defeated, the parity is reversed (p. 438).

Theorem 6.4 (p. 438): every AVAF with no single-valued cycles has a unique, nonempty preferred extension. The proof removes failing attacks to obtain a standard AF. Any cycle involving multiple values is broken at an attack from a least-preferred value to a more-preferred value. The resulting AF is cycle-free, so `EXTEND` computes the unique extension (p. 438).

Without a fixed audience, deciding objective/subjective/indefensible status may require considering factorially many value orderings in the worst case. The suggested algorithm is to choose an ordering, compute the preferred extension, and stop early if the result suffices to establish subjective acceptability; objective acceptability or indefensibility may require all orderings (p. 438).

Definition 6.5 (p. 439): a line of argument for an argument `arg` is a set of argument chains, each relating to distinct values, such that `arg` is the last argument of the first chain and adjacent chains are connected by an attack from the last argument of one chain to the first argument of the previous chain. Lines terminate because values cannot repeat (p. 439).

Theorem 6.6 (p. 440): in a VAF with no single-valued cycles and at most one attacker per argument, an argument's status is determined by chain parity in its line of argument. Objective acceptance requires an odd position in the first chain and no later odd chain. Indefensibility requires an even position in the first chain and no later odd chain. Subjective acceptance requires a later odd chain (p. 440).

Corollary 6.7 (pp. 440-441) characterizes two-valued cycles: preferred extensions contain odd-numbered arguments of chains preceded by even chains, odd-numbered arguments of chains with the preferred value, and even-numbered arguments of other chains. Arguments under the first case are objectively acceptable; arguments under the latter two cases are subjectively acceptable; even-numbered arguments of a chain preceded by an even chain are indefensible.

For arguments with more than one attacker, own-value subgraphs and unattacked own-value arguments still help prune the reasoning, but all lines of argument may need to be considered in pathological cases (p. 441).

## Moral Debate Example

The Hal and Carla example illustrates persuasion with life and property values. Coleman-style arguments are `A(life)`, `B(property)`, `C(property)` with `C -> B -> A`; both `A` and `C` are objectively acceptable (pp. 442-443). Adding Christie's `D(life)` attacking `C` makes `C` subjectively acceptable: if property is preferred to life, `C` is accepted; if life is preferred to property, `B` is accepted because `C` is defeated by `D`, while `A` remains objectively acceptable (p. 443).

Adding further arguments `E(property)` and `F(life)` shows how a defender can use value repetition strategically. Reintroducing an argument with the defended value can terminate a line of reasoning so the original argument is not undermined (pp. 443-444).

## Facts as Highest-Priority Values

Section 8 introduces factual arguments by treating fact as a special value that is always given highest preference for every audience (p. 444). In the Hal and Carla example, a factual argument `G(fact)` attacking `F(life)` means `F` must fail if the facts show Carla has sufficient insulin. Reasonable value orders therefore include `fact > val_i` for every ordinary value (p. 444).

Uncertain facts can introduce single-valued cycles over the fact value. In Figure 8, `G(fact)` and `H(fact)` attack each other, producing multiple preferred extensions even for a fixed value ordering (pp. 444-446). The paper distinguishes four statuses under factual uncertainty: objectively acceptable skeptically, objectively acceptable credulously, subjectively acceptable skeptically, and subjectively acceptable credulously (p. 445).

For persuasion under uncertainty, only skeptically objectively acceptable arguments are fully persuasive to a determined challenger. Otherwise some choice of factual resolution and value preference can resist persuasion (p. 445).

## Implementation Consequences

- Implement `defeats_a(A, B)` as structural attack plus absence of a strict target-over-attacker value preference (p. 436).
- Keep raw attacks separate from successful attacks/defeats. The same VAF must produce different defeat relations under different audiences (p. 436).
- Treat objective and subjective acceptance as quantified over audiences and preferred extensions, not as properties of a single ranking (p. 437).
- Provide a derived standard AF for a given audience by removing attacks that fail against that audience (p. 436).
- For all possible audiences, use complete order permutations when no restricted audience set is supplied, but expose the audience set so callers can restrict it when the domain has known value orders (pp. 435, 438).
- A fact value can be modeled as a distinguished value ranked above ordinary values in every reasonable audience (p. 444), but factual uncertainty can reintroduce multiple preferred extensions (pp. 444-445).

## New Leads

- Dung (1995), "On the acceptability of arguments and its fundamental role in nonmonotonic reasoning, logic programming and n-person games."
- Dunne and Bench-Capon (2002), "Coherence in Finite Argument Systems."
- Bench-Capon (2002), "Value-based argumentation frameworks."
