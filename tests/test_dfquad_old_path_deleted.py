from __future__ import annotations

import ast
import importlib
from pathlib import Path

import pytest


def test_compute_dfquad_strengths_is_not_defined_in_argumentation() -> None:
    """Codex 2.21 deletion gate for the old PrAF-typed DF-QuAD path."""

    src_root = Path(__file__).resolve().parents[1] / "src" / "argumentation"
    definitions: list[str] = []
    for path in src_root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "compute_dfquad_strengths":
                definitions.append(str(path.relative_to(src_root)))

    assert definitions == []


def test_old_probabilistic_dfquad_function_is_not_importable() -> None:
    with pytest.raises((AttributeError, ImportError)):
        module = importlib.import_module("argumentation.probabilistic_dfquad")
        getattr(module, "compute_dfquad_strengths")
