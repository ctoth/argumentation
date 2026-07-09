"""Eager arc-acyclic foundedness in the sparse-narrow stable solver.

The solver must enforce well-foundedness through the eager SCC-local
arc-justification encoding, never through lazy literal-SCC loop formulas
(`native_sparse_narrow_loop_formulas` stays 0 on every solve).
"""

from __future__ import annotations

from argumentation.structured.aba import aba_sat
from argumentation.structured.aba.aba import ABAFramework
from argumentation.structured.aspic.aspic import GroundAtom, Literal, Rule


def lit(name: str) -> Literal:
    return Literal(GroundAtom(name))


def _unfounded_contrary_cycle_framework() -> ABAFramework:
    """No stable extension; the ONLY completion+contrary models are unfounded.

    contrary(a) = c with rules {c <- a, c <- d, d <- c}: taking a derives its
    own contrary, and leaving a out requires c, which is only "derivable"
    through the unfounded c/d cycle. Every Clark-completion model therefore
    sets derived[c] = derived[d] = 1 through cyclic self-support, which the
    lazy loop-formula CEGAR can only reject by emitting loop formulas.
    """
    a, c, d = lit("a"), lit("c"), lit("d")
    return ABAFramework(
        language=frozenset({a, c, d}),
        assumptions=frozenset({a}),
        contrary={a: c},
        rules=frozenset({
            Rule((a,), c, "strict"),
            Rule((d,), c, "strict"),
            Rule((c,), d, "strict"),
        }),
    )


def _founded_stable_with_idle_cycle_framework() -> ABAFramework:
    """{a} is the unique stable extension; the c/d cycle must stay underived."""
    a, c, d = lit("a"), lit("c"), lit("d")
    return ABAFramework(
        language=frozenset({a, c, d}),
        assumptions=frozenset({a}),
        contrary={a: c},
        rules=frozenset({
            Rule((d,), c, "strict"),
            Rule((c,), d, "strict"),
        }),
    )


def test_unfounded_cycle_cannot_fake_stability_without_loop_formulas() -> None:
    framework = _unfounded_contrary_cycle_framework()

    result = aba_sat.native_sparse_narrow_sat_extension(framework, "stable")

    assert result.extension is None
    assert aba_sat.support_extensions(framework, "stable") == ()
    assert result.telemetry["native_sparse_narrow_loop_formulas"] == 0


def test_founded_stable_extension_ignores_idle_cycle_without_loop_formulas() -> None:
    framework = _founded_stable_with_idle_cycle_framework()

    result = aba_sat.native_sparse_narrow_sat_extension(framework, "stable")

    assert result.extension == frozenset({lit("a")})
    assert result.telemetry["native_sparse_narrow_loop_formulas"] == 0


def test_stable_solver_reports_arc_acyclicity_telemetry() -> None:
    framework = _unfounded_contrary_cycle_framework()

    result = aba_sat.native_sparse_narrow_sat_extension(framework, "stable")

    assert result.telemetry["native_sparse_narrow_acyc_recursive_rules"] == 2
    assert result.telemetry["native_sparse_narrow_acyc_edges"] == 2
    assert result.telemetry["native_sparse_narrow_edge_cycle_clauses"] >= 0
