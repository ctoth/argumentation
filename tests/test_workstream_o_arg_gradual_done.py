from __future__ import annotations

import importlib
from dataclasses import fields

import pytest


def test_workstream_o_arg_gradual_public_surface_is_complete() -> None:
    import argumentation
    from argumentation import dfquad, equational, gradual, gradual_principles, matt_toni

    assert argumentation.dfquad is dfquad
    assert argumentation.matt_toni is matt_toni
    assert argumentation.equational is equational
    assert argumentation.gradual_principles is gradual_principles
    assert hasattr(gradual, "quadratic_energy_strengths_continuous")
    assert hasattr(dfquad, "dfquad_bipolar_strengths")
    assert "integration_method" in {
        field.name for field in fields(gradual.GradualStrengthResult)
    }

    with pytest.raises((AttributeError, ImportError)):
        module = importlib.import_module("argumentation.probabilistic_dfquad")
        getattr(module, "compute_dfquad_strengths")
