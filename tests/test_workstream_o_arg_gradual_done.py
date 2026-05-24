from __future__ import annotations

import importlib
from dataclasses import fields

import pytest


def test_workstream_o_arg_gradual_public_surface_is_complete() -> None:
    from argumentation.gradual import dfquad, equational, gradual, gradual_principles
    from argumentation.ranking import matt_toni

    assert matt_toni is not None
    assert equational is not None
    assert gradual_principles is not None
    assert hasattr(gradual, "quadratic_energy_strengths_continuous")
    assert hasattr(dfquad, "dfquad_bipolar_strengths")
    assert "integration_method" in {
        field.name for field in fields(gradual.GradualStrengthResult)
    }

    with pytest.raises((AttributeError, ImportError)):
        module = importlib.import_module("argumentation.probabilistic_dfquad")
        getattr(module, "compute_dfquad_strengths")
