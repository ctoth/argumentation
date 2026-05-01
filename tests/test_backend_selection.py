from __future__ import annotations

from argumentation import backends


def test_default_backend_uses_materialized_for_weakest_link() -> None:
    assert backends.default_backend("grounded", 100, True, True) == "materialized_reference"


def test_default_backend_prefers_asp_for_grounded() -> None:
    assert backends.default_backend("grounded", 1, False, False) == "asp"


def test_default_backend_uses_asp_for_large_theories_when_clingo_available(monkeypatch) -> None:
    monkeypatch.setattr(backends, "has_clingo", lambda: True)
    monkeypatch.setattr(backends, "has_z3", lambda: True)

    assert backends.default_backend("preferred", 31, False, False) == "asp"


def test_default_backend_uses_sat_before_materialized_when_z3_available(monkeypatch) -> None:
    monkeypatch.setattr(backends, "has_clingo", lambda: False)
    monkeypatch.setattr(backends, "has_z3", lambda: True)

    assert backends.default_backend("preferred", 30, False, False) == "sat"


def test_default_backend_falls_back_to_materialized(monkeypatch) -> None:
    monkeypatch.setattr(backends, "has_clingo", lambda: False)
    monkeypatch.setattr(backends, "has_z3", lambda: False)

    assert backends.default_backend("preferred", 30, False, False) == "materialized_reference"
