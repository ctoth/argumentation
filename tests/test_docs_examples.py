from __future__ import annotations

from argumentation.core.dung import (
    ArgumentationFramework,
    grounded_extension,
    preferred_extensions,
    stable_extensions,
)
from argumentation.core.solver_results import SolverUnavailable
from argumentation.frameworks.setaf import SETAF, conflict_free
from argumentation.probabilistic.probabilistic import (
    ProbabilisticAF,
    compute_probabilistic_acceptance,
)
from argumentation.solving.solver import ICCMAConfig, solve_dung_extensions
from argumentation.structured.aba.aba import (
    ABAFramework,
    preferred_extensions as aba_preferred_extensions,
)
from argumentation.structured.aspic.aspic import GroundAtom, Literal, Rule


def lit(name: str) -> Literal:
    return Literal(GroundAtom(name))


def test_docs_example_dung_extensions() -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b", "c", "d"}),
        defeats=frozenset({("a", "b"), ("b", "c"), ("c", "d"), ("d", "a")}),
    )

    assert grounded_extension(framework) == frozenset()
    assert preferred_extensions(framework) == [
        frozenset({"a", "c"}),
        frozenset({"b", "d"}),
    ]
    assert stable_extensions(framework) == preferred_extensions(framework)


def test_docs_example_iccma_witness_is_not_enumeration() -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"1", "2", "3"}),
        defeats=frozenset({("1", "2"), ("2", "1")}),
    )

    result = solve_dung_extensions(
        framework,
        semantics="preferred",
        backend="iccma",
        iccma=ICCMAConfig(binary="external-solver"),
    )

    assert isinstance(result, SolverUnavailable)
    assert (
        result.reason
        == "ICCMA AF SE tasks return one extension witness, not enumeration"
    )


def test_docs_example_flat_aba_preferred_extensions() -> None:
    alpha = lit("alpha")
    beta = lit("beta")
    leave = lit("leave")
    stay = lit("stay")

    framework = ABAFramework(
        language=frozenset({alpha, beta, leave, stay}),
        rules=frozenset(
            {
                Rule((alpha,), leave, "strict"),
                Rule((beta,), stay, "strict"),
            }
        ),
        assumptions=frozenset({alpha, beta}),
        contrary={alpha: stay, beta: leave},
    )

    assert aba_preferred_extensions(framework) == (
        frozenset({alpha}),
        frozenset({beta}),
    )


def test_docs_example_probabilistic_extension_probability() -> None:
    framework = ArgumentationFramework(
        arguments=frozenset({"a", "b"}),
        defeats=frozenset({("a", "b")}),
    )
    praf = ProbabilisticAF(
        framework=framework,
        p_args={"a": 1.0, "b": 1.0},
        p_defeats={("a", "b"): 0.5},
    )

    result = compute_probabilistic_acceptance(
        praf,
        semantics="grounded",
        strategy="exact_enum",
        query_kind="extension_probability",
        queried_set={"a"},
    )

    assert result.extension_probability is not None
    assert abs(result.extension_probability - 0.5) < 1e-12


def test_docs_example_setaf_collective_attack() -> None:
    framework = SETAF(
        arguments=frozenset({"a", "b", "c"}),
        attacks=frozenset({(frozenset({"a", "b"}), "c")}),
    )

    assert conflict_free(framework, frozenset({"a", "c"})) is True
    assert conflict_free(framework, frozenset({"a", "b", "c"})) is False
