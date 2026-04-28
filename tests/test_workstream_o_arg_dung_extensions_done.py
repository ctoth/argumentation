from __future__ import annotations

import importlib

import pytest

from argumentation import bipolar, dung, labelling


pytestmark = pytest.mark.unit


def test_workstream_o_arg_dung_extensions_public_surface_is_done() -> None:
    for name in (
        "legally_in",
        "legally_out",
        "complete_labellings",
        "grounded_labelling",
        "preferred_labellings",
        "stable_labellings",
        "semi_stable_labellings",
        "eager_labelling",
        "stage2_labellings",
    ):
        assert hasattr(labelling, name)

    for name in (
        "eager_extension",
        "stage2_extensions",
        "indirect_attacks",
        "prudent_conflict_free",
        "prudent_admissible",
        "prudent_preferred_extensions",
        "prudent_grounded_extension",
    ):
        assert hasattr(dung, name)

    for name in ("bipolar_grounded_extension", "bipolar_complete_extensions"):
        assert hasattr(bipolar, name)

    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("argumentation.dung_z3")

    assert not hasattr(dung, "_AUTO_BACKEND_MAX_ARGS")
