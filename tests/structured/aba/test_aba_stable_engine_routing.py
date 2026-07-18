from __future__ import annotations

import pytest

from argumentation.structured.aba import aba_sat
from argumentation.structured.aba.aba import ABAFramework
from argumentation.structured.aspic.aspic import GroundAtom, Literal, Rule


def lit(name: str) -> Literal:
    return Literal(GroundAtom(name), True)


def _cyclic_support_framework() -> ABAFramework:
    # a,b assumptions; contraries derivable, with a small support cycle x<->y.
    a, b = lit("a"), lit("b")
    x, y, ca, cb = lit("x"), lit("y"), lit("ca"), lit("cb")
    rules = (
        Rule((a,), x, "strict"),
        Rule((x,), y, "strict"),
        Rule((y,), x, "strict"),  # cyclic support x->y->x
        Rule((b,), ca, "strict"),  # b attacks a
        Rule((a,), cb, "strict"),  # a attacks b
    )
    return ABAFramework(
        language=frozenset((a, b, x, y, ca, cb)),
        assumptions=frozenset((a, b)),
        contrary={a: ca, b: cb},
        rules=frozenset(rules),
    )


# --- 1. structural predicate is a pure function of measured features ---


def test_stable_engine_for_small_is_glucose4() -> None:
    engine = aba_sat._stable_engine_for(
        recursive_rules=10, edges=12, assumptions=30, rules=200
    )
    assert engine == "glucose4"


def test_stable_engine_for_giant_is_strong() -> None:
    engine = aba_sat._stable_engine_for(
        recursive_rules=373, edges=407, assumptions=1050, rules=30293
    )
    assert engine == aba_sat._STABLE_ENGINE_STRONG
    assert engine != "glucose4"


# --- 2. default engine unchanged for small frameworks ---


def test_default_engine_is_glucose4_for_small() -> None:
    solver = aba_sat._NativeSparseNarrowStableSolver(_cyclic_support_framework())
    assert solver.telemetry["native_sparse_narrow_engine"] == "glucose4"
    assert solver.engine == "glucose4"


# --- 3. engine override keeps the answer correct (parity vs oracle) ---


@pytest.mark.parametrize("engine", ["glucose4", "cadical195"])
def test_engine_override_matches_oracle(engine: str) -> None:
    framework = _cyclic_support_framework()
    solver = aba_sat._NativeSparseNarrowStableSolver(framework, engine=engine)
    ext = solver.stable_extension()
    oracle = aba_sat.support_extensions(framework, "stable")
    got = frozenset() if ext is None else frozenset(ext)
    assert (ext is None) == (len(oracle) == 0)
    if ext is not None:
        assert got in {frozenset(o) for o in oracle}


# --- 4. phase parity: the phase vector is engine-independent ---


def test_phase_vector_identical_across_engines() -> None:
    framework = _cyclic_support_framework()
    g = aba_sat._NativeSparseNarrowStableSolver(framework, engine="glucose4")
    c = aba_sat._NativeSparseNarrowStableSolver(framework, engine="cadical195")
    assert g.phase_vector == c.phase_vector
    assert len(g.phase_vector) > 0


# --- 5. no-row-loss fallback: strong-engine failure falls back to glucose4 ---


def test_fallback_to_glucose4_on_strong_engine_error(monkeypatch) -> None:
    framework = _cyclic_support_framework()
    # Force routing to an invalid engine so construction/solve raises.
    monkeypatch.setattr(
        aba_sat, "_stable_engine_for", lambda **kw: "totally_invalid_engine_xyz"
    )
    result = aba_sat.native_sparse_narrow_sat_extension(framework, "stable")
    oracle = aba_sat.support_extensions(framework, "stable")
    got = frozenset() if result.extension is None else frozenset(result.extension)
    assert (result.extension is None) == (len(oracle) == 0)
    if result.extension is not None:
        assert got in {frozenset(o) for o in oracle}
    # telemetry records that the fallback engine actually ran
    assert result.telemetry["native_sparse_narrow_engine"] == "glucose4"
