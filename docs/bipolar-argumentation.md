# Bipolar Argumentation

Standard Dung AFs model only attacks between arguments. Bipolar argumentation frameworks (BAFs) add a second relation — support — which creates new defeat paths that pure attack graphs cannot express. A supporter of an attacker becomes an indirect attacker. An attacker of a supported argument reaches its benefactor. The implementation follows Cayrol & Lagasquie-Schiex (2005).

## The bipolar framework

A bipolar argumentation framework BAF = (A, Def, Sup) extends a Dung AF with a support relation (Cayrol 2005):

- **A** — a set of arguments (`frozenset[str]`)
- **Def** — direct defeat (attack) relation (`frozenset[tuple[str, str]]`)
- **Sup** — direct support relation (`frozenset[tuple[str, str]]`, default empty)

The `BipolarArgumentationFramework` dataclass (`argumentation/src/argumentation/bipolar.py:10`) is frozen. Direct defeats and supports are immutable inputs; derived defeats are computed functionally from them.

## Derived defeats

Support relations generate new defeat paths that are not present in the original attack graph. These are computed by `cayrol_derived_defeats()` (`argumentation/src/argumentation/bipolar.py:73`), implementing Cayrol 2005 Definition 3.

### Supported defeat (Def 3)

If A supports B and B defeats C, then A derivedly defeats C. The supporter inherits the attack: by lending support to an attacker, A becomes complicit in the attack on C.

```
A --supports--> B --defeats--> C
A - - - - derivedly defeats - - - -> C
```

### Indirect defeat (Def 3)

If A defeats B and B supports C, then A derivedly defeats C. The attack propagates through support: by attacking a supporter, A undermines everything that supporter sustains.

```
A --defeats--> B --supports--> C
A - - - - derivedly defeats - - - -> C
```

### Fixpoint computation

The algorithm (`argumentation/src/argumentation/bipolar.py:73`) computes derived defeats iteratively:

1. **Support reach**: compute the transitive closure of support successors for each argument. If A supports B and B supports C, then A support-reaches both B and C.
2. **Iterate**: scan all working defeats. For each defeat, generate supported defeats (via support reach of the source) and indirect defeats (via support reach of the target). Add any new derived defeats to the working set.
3. **Fixpoint**: repeat until no new defeats are discovered. Multi-pass iteration enables transitive chaining — e.g., A supports B, B defeats C, C supports D yields derived defeat (A, D) across two passes.

The function returns only derived defeats, not the original direct defeats. `derived_set_defeats()` (`argumentation/src/argumentation/bipolar.py:125`) returns the union of both.

## Admissibility variants

Bipolar frameworks admit three progressively stronger notions of admissibility. All are defined over the defeat closure (direct + derived defeats).

### d-admissible (Def 9)

Conflict-free under the defeat closure, and self-defending: for every attacker of a member, the set counter-defeats that attacker. This is the weakest bipolar admissibility — equivalent to Dung admissibility computed over the extended defeat set.

### s-admissible (Def 10)

Safe (Def 7) and self-defending. Strictly stronger than d-admissible. Safety requires that no argument in the entire framework is both set-defeated and set-supported (or a member of) the candidate set. A set can be d-admissible but not s-admissible when it set-defeats an argument it also set-supports — a safety violation that d-admissibility cannot detect.

### c-admissible (Def 11)

Conflict-free, support-closed, and self-defending. The strongest variant. Support closure requires that all support-successors of members are included in the set. A set can be s-admissible but not c-admissible if it includes an argument without including everything that argument supports.

### Hierarchy

c-admissible => s-admissible => d-admissible. Each level strictly implies the one below it. This hierarchy is tested as a property in `tests/test_bipolar_semantics.py`.

### Predicates

The following predicate functions implement the building blocks:

| Function | Definition | What it checks |
|----------|-----------|----------------|
| `conflict_free(args, framework)` | Def 6 | No member is set-defeated by the set itself |
| `safe(args, framework)` | Def 7 | No argument anywhere is both set-defeated and set-supported by the candidate |
| `defends(args, arg, framework)` | Def 5 | Every attacker of `arg` (under defeat closure) is counter-defeated by the set |
| `set_defeats(args, target, framework)` | — | Whether the set set-defeats a target under defeat closure |
| `set_supports(args, target, framework)` | — | Whether the set set-supports a target via transitive support reachability |
| `support_closed(args, framework)` | — | Whether `args` equals its own support closure |

## Extensions

Extension functions enumerate maximal admissible sets under each variant:

- **d-preferred** (`d_preferred_extensions`): maximal d-admissible sets
- **s-preferred** (`s_preferred_extensions`): maximal s-admissible sets
- **c-preferred** (`c_preferred_extensions`): maximal c-admissible sets
- **bipolar-stable** (`stable_extensions`, Def 8): conflict-free sets that set-defeat every outsider under the defeat closure

All extension functions enumerate all subsets (exponential complexity), suitable only for small frameworks. Results are sorted by (size, sorted tuple) for determinism.

## Integration

### PrAF (Monte Carlo sampling)

Each MC sample in the PrAF subsystem draws supports with opinion-based probabilities (`propstore/praf/engine.py`). Within each sampled world, `cayrol_derived_defeats` produces derived defeats from whichever support edges survived sampling. The derived defeats are added to the sampled `ArgumentationFramework.defeats`, so each MC world properly accounts for bipolar structure.

See [Probabilistic Argumentation](probabilistic-argumentation.md) for full PrAF details.

### Claim graph

The claim-graph bridge in `propstore.argumentation` routes `supports` and `explains` stance types into the bipolar support relation. All other stance types flow into the defeat relation as before. Derived defeats are computed via `cayrol_derived_defeats` and added to the defeat set before framework construction.

The bipolar semantics `d-preferred`, `s-preferred`, `c-preferred`, and `bipolar-stable` are selectable through `analyze_claim_graph` and through the worldline / Python policy surfaces. The current `pks world extensions` CLI only accepts `grounded`, `preferred`, and `stable`.

## CLI usage

```bash
# d-preferred via a worldline
pks worldline create bipolar_d --target concept1 --strategy argumentation --semantics d-preferred

# s-preferred via a worldline
pks worldline create bipolar_s --target concept1 --strategy argumentation --semantics s-preferred

# c-preferred via a worldline
pks worldline create bipolar_c --target concept1 --strategy argumentation --semantics c-preferred

# Bipolar-stable via a worldline
pks worldline create bipolar_stable --target concept1 --strategy argumentation --semantics bipolar-stable
```

## Known limitations

- **Exponential enumeration.** All extension functions enumerate all subsets. This is tractable only for small argument sets.
- **Rule ordering empty.** When bipolar frameworks are constructed via the ASPIC+ bridge, rule ordering is always empty — only premise ordering from metadata has discriminating power.

## References

- Cayrol, C. & Lagasquie-Schiex, M.-C. (2005). On the acceptability of arguments in bipolar argumentation frameworks. *ECSQARU 2005*. Definition numbers: Def 3 (derived defeats), Def 5 (defence), Def 6 (conflict-free), Def 7 (safe), Def 8 (stable), Def 9 (d-admissible), Def 10 (s-admissible), Def 11 (c-admissible).
- Dung, P.M. (1995). On the acceptability of arguments and its fundamental role in nonmonotonic reasoning, logic programming and n-person games. *Artificial Intelligence*, 77(2), 321-357.
- Modgil, S. & Prakken, H. (2018). An abstract framework for argumentation with structured arguments. *Argument & Computation*, 9(2), 93-132.
