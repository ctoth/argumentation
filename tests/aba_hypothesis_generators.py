from __future__ import annotations

from dataclasses import dataclass

from hypothesis import strategies as st

from argumentation.aba import ABAFramework
from argumentation.aspic import GroundAtom, Literal, Rule


@dataclass(frozen=True)
class RawABASpec:
    language: frozenset[Literal]
    assumptions: frozenset[Literal]
    contrary: dict[Literal, Literal]
    rules: tuple[Rule, ...]

    def to_framework(self) -> ABAFramework:
        return ABAFramework(
            language=self.language,
            assumptions=self.assumptions,
            contrary=self.contrary,
            rules=frozenset(self.rules),
        )


def lit(name: str) -> Literal:
    return Literal(GroundAtom(name))


def flat_aba_frameworks(
    *,
    min_assumptions: int = 1,
    max_assumptions: int = 4,
    max_rules: int = 8,
) -> st.SearchStrategy[ABAFramework]:
    return flat_aba_specs(
        min_assumptions=min_assumptions,
        max_assumptions=max_assumptions,
        max_rules=max_rules,
    ).map(RawABASpec.to_framework)


@st.composite
def flat_aba_specs(
    draw,
    *,
    min_assumptions: int = 1,
    max_assumptions: int = 4,
    max_rules: int = 8,
) -> RawABASpec:
    assumption_count = draw(st.integers(min_value=min_assumptions, max_value=max_assumptions))
    atom_count = draw(st.integers(min_value=assumption_count + 1, max_value=assumption_count + 6))
    assumptions = tuple(lit(f"a{index}") for index in range(assumption_count))
    atoms = tuple(lit(f"x{index}") for index in range(atom_count))
    contraries = {
        assumption: atoms[index % len(atoms)]
        for index, assumption in enumerate(assumptions)
    }
    non_assumption_heads = atoms
    rule_count = draw(st.integers(min_value=0, max_value=max_rules))
    rule_specs = draw(
        st.lists(
            st.tuples(
                st.integers(min_value=0, max_value=len(non_assumption_heads) - 1),
                st.lists(
                    st.integers(min_value=0, max_value=len(atoms) - 1),
                    min_size=0,
                    max_size=min(3, len(atoms)),
                    unique=True,
                ),
            ),
            min_size=rule_count,
            max_size=rule_count,
        )
    )
    rules = tuple(
        Rule(tuple(atoms[body_index] for body_index in body), non_assumption_heads[head], "strict")
        for head, body in rule_specs
    )
    rule_literals = {
        literal
        for rule in rules
        for literal in (rule.consequent, *rule.antecedents)
    }
    language = frozenset((*assumptions, *contraries.values(), *rule_literals))
    return RawABASpec(
        language=language,
        assumptions=frozenset(assumptions),
        contrary=contraries,
        rules=rules,
    )


@st.composite
def non_flat_aba_specs(draw) -> RawABASpec:
    base = draw(flat_aba_specs(min_assumptions=1, max_assumptions=3, max_rules=3))
    assumption = sorted(base.assumptions, key=repr)[0]
    rules = (*base.rules, Rule((), assumption, "strict"))
    return RawABASpec(
        language=base.language,
        assumptions=base.assumptions,
        contrary=base.contrary,
        rules=rules,
    )


@st.composite
def p_acyclic_frameworks(draw) -> ABAFramework:
    assumption_count = draw(st.integers(min_value=1, max_value=3))
    atom_count = draw(st.integers(min_value=2, max_value=5))
    assumptions = tuple(lit(f"a{index}") for index in range(assumption_count))
    atoms = tuple(lit(f"x{index}") for index in range(atom_count))
    contraries = {
        assumption: atoms[index % len(atoms)]
        for index, assumption in enumerate(assumptions)
    }
    rules: list[Rule] = [Rule((assumptions[0],), atoms[0], "strict")]
    for head_index in range(1, atom_count):
        body = draw(
            st.lists(
                st.integers(min_value=0, max_value=head_index - 1),
                min_size=0,
                max_size=min(2, head_index),
                unique=True,
            )
        )
        rules.append(Rule(tuple(atoms[index] for index in body), atoms[head_index], "strict"))
    return ABAFramework(
        language=frozenset((*assumptions, *atoms)),
        assumptions=frozenset(assumptions),
        contrary=contraries,
        rules=frozenset(rules),
    )


def cyclic_dependency_frameworks() -> st.SearchStrategy[ABAFramework]:
    a = lit("a0")
    x = lit("x0")
    y = lit("x1")
    return st.just(
        ABAFramework(
            language=frozenset({a, x, y}),
            assumptions=frozenset({a}),
            contrary={a: y},
            rules=frozenset({
                Rule((x,), y, "strict"),
                Rule((y,), x, "strict"),
            }),
        )
    )


def normal_candidate_frameworks() -> st.SearchStrategy[ABAFramework]:
    return st.integers(min_value=1, max_value=4).map(_normal_candidate_framework)


def _normal_candidate_framework(size: int) -> ABAFramework:
    assumptions = tuple(lit(f"a{index}") for index in range(size))
    contraries = tuple(lit(f"c{index}") for index in range(size))
    return ABAFramework(
        language=frozenset((*assumptions, *contraries)),
        assumptions=frozenset(assumptions),
        contrary=dict(zip(assumptions, contraries, strict=True)),
        rules=frozenset(),
    )


def dense_medium_arity_frameworks() -> st.SearchStrategy[ABAFramework]:
    return st.integers(min_value=5, max_value=8).map(_dense_medium_arity_framework)


def _dense_medium_arity_framework(size: int) -> ABAFramework:
    assumptions = tuple(lit(f"a{index}") for index in range(size))
    atoms = tuple(lit(f"x{index}") for index in range(size))
    rules = {
        Rule(tuple(assumptions[(index + offset) % size] for offset in range(3)), atoms[index], "strict")
        for index in range(size)
    }
    return ABAFramework(
        language=frozenset((*assumptions, *atoms)),
        assumptions=frozenset(assumptions),
        contrary={assumption: atoms[index] for index, assumption in enumerate(assumptions)},
        rules=frozenset(rules),
    )


def low_width_frameworks() -> st.SearchStrategy[ABAFramework]:
    return st.integers(min_value=2, max_value=6).map(_low_width_framework)


def _low_width_framework(size: int) -> ABAFramework:
    assumptions = tuple(lit(f"a{index}") for index in range(size))
    atoms = tuple(lit(f"x{index}") for index in range(size))
    rules = {
        Rule((assumptions[0],), atoms[0], "strict"),
        *(
            Rule((atoms[index - 1],), atoms[index], "strict")
            for index in range(1, size)
        ),
    }
    return ABAFramework(
        language=frozenset((*assumptions, *atoms)),
        assumptions=frozenset(assumptions),
        contrary={assumption: atoms[index] for index, assumption in enumerate(assumptions)},
        rules=frozenset(rules),
    )


def renamed_framework(framework: ABAFramework, *, prefix: str = "r") -> tuple[ABAFramework, dict[Literal, Literal]]:
    mapping = {
        literal: lit(f"{prefix}{index}")
        for index, literal in enumerate(sorted(framework.language, key=repr))
    }
    return (
        ABAFramework(
            language=frozenset(mapping[literal] for literal in framework.language),
            assumptions=frozenset(mapping[assumption] for assumption in framework.assumptions),
            contrary={
                mapping[assumption]: mapping[contrary]
                for assumption, contrary in framework.contrary.items()
            },
            rules=frozenset(
                Rule(
                    tuple(mapping[antecedent] for antecedent in rule.antecedents),
                    mapping[rule.consequent],
                    rule.kind,
                )
                for rule in framework.rules
            ),
        ),
        mapping,
    )
