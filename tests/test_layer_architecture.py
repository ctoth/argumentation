"""Layered-architecture contract for the ``argumentation`` package.

The package is organized into import layers. A module may import from its own
layer or any lower layer, never a higher one. This test pins that DAG so the
architecture is enforced by CI rather than by convention.

Layer ranks (lower = more foundational):

    0  core             dung, labelling, preference, solver_results,
                        preprocessing, scc_recursive, bipolar, accrual
    1  aspic / frameworks / gradual / ranking
    2  aba / probabilistic / dynamics / interop
    3  solver_adapters
    4  solving           af_sat, sat_encoding, backends, solver,
                        solver_differential, iccma_cli
    5  semantics

See ``docs/architecture.md`` and
``reports/package-decomposition-2026-05-22.md`` for the rationale. The ``LAYER``
map below is the executable specification of that DAG.
"""

from __future__ import annotations

import ast
from pathlib import Path


SRC = Path(__file__).resolve().parents[1] / "src" / "argumentation"

# Module key -> layer rank. Every non-``__init__`` module under
# ``src/argumentation/`` must appear here; ``test_layer_map_is_total`` enforces
# that, so a newly added module forces an explicit layer decision.
LAYER: dict[str, int] = {
    # -- 0: core --------------------------------------------------------
    "dung": 0,
    "labelling": 0,
    "preference": 0,
    "solver_results": 0,
    "preprocessing": 0,
    "scc_recursive": 0,
    "bipolar": 0,
    "accrual": 0,
    # -- 1: aspic -------------------------------------------------------
    "aspic": 1,
    "aspic_encoding": 1,
    "aspic_incomplete": 1,
    "subjective_aspic": 1,
    "datalog_grounding": 1,
    # -- 1: frameworks --------------------------------------------------
    "adf": 1,
    "setaf": 1,
    "setaf_io": 1,
    "caf": 1,
    "vaf": 1,
    "vaf_completion": 1,
    "partial_af": 1,
    "practical_reasoning": 1,
    # -- 1: gradual -----------------------------------------------------
    "gradual": 1,
    "dfquad": 1,
    "equational": 1,
    "gradual_principles": 1,
    "llm_surface": 1,
    "sensitivity": 1,
    # -- 1: ranking -----------------------------------------------------
    "ranking": 1,
    "ranking_axioms": 1,
    "weighted": 1,
    "matt_toni": 1,
    # -- 2: aba ---------------------------------------------------------
    "aba": 2,
    "aba_sat": 2,
    "aba_asp": 2,
    "aba_decomposition": 2,
    "aba_incremental": 2,
    "aba_preprocessing": 2,
    "aba_route_policy": 2,
    "aba_telemetry": 2,
    # -- 2: probabilistic ----------------------------------------------
    "probabilistic": 2,
    "probabilistic_components": 2,
    "probabilistic_treedecomp": 2,
    "epistemic": 2,
    # -- 2: dynamics ----------------------------------------------------
    "enforcement": 2,
    "dynamic": 2,
    "af_revision": 2,
    "approximate": 2,
    "optimization": 2,
    # -- 2: interop -----------------------------------------------------
    "iccma": 2,
    # -- 3: solver_adapters --------------------------------------------
    "solver_adapters": 3,
    "solver_adapters.clingo": 3,
    "solver_adapters.iccma_aba": 3,
    "solver_adapters.iccma_af": 3,
    # -- 4: solving -----------------------------------------------------
    "af_sat": 4,
    "sat_encoding": 4,
    "backends": 4,
    "solver": 4,
    "solver_differential": 4,
    "iccma_cli": 4,
    # -- 5: semantics ---------------------------------------------------
    "semantics": 5,
}

# Sanctioned upward edges. Both are function-local (deferred) imports of the
# clingo subprocess adapter, loaded only when an external clingo backend is
# requested; they never run at module-import time.
ALLOWED_UPWARD: frozenset[tuple[str, str]] = frozenset(
    {
        ("aspic_encoding", "solver_adapters.clingo"),
        ("aba_asp", "solver_adapters.clingo"),
    }
)


def _module_key(path: Path) -> str:
    """Map a source file to its ``LAYER`` key (dotted, relative to the package)."""
    return ".".join(path.relative_to(SRC).with_suffix("").parts)


def _iter_modules() -> list[Path]:
    """Every package source file except ``__init__.py`` markers."""
    return [p for p in sorted(SRC.rglob("*.py")) if p.name != "__init__.py"]


def _normalize(rest: str) -> str:
    """Reduce an ``argumentation.<rest>`` suffix to a ``LAYER`` key."""
    parts = rest.split(".")
    if parts[0] == "solver_adapters" and len(parts) > 1:
        return f"solver_adapters.{parts[1]}"
    return parts[0]


def _internal_targets(node: ast.AST) -> list[str]:
    """``LAYER`` keys an import node references within the ``argumentation`` package."""
    raw: list[str] = []
    if isinstance(node, ast.ImportFrom):
        module = node.module or ""
        if module == "argumentation":
            raw += [alias.name for alias in node.names]
        elif module == "argumentation.solver_adapters":
            raw += [f"solver_adapters.{alias.name}" for alias in node.names]
        elif module.startswith("argumentation."):
            raw.append(module[len("argumentation.") :])
    elif isinstance(node, ast.Import):
        for alias in node.names:
            if alias.name.startswith("argumentation."):
                raw.append(alias.name[len("argumentation.") :])
    return [key for key in (_normalize(r) for r in raw) if key in LAYER]


def test_layer_map_is_total() -> None:
    unmapped = sorted(
        _module_key(p) for p in _iter_modules() if _module_key(p) not in LAYER
    )
    assert unmapped == [], f"modules with no layer assignment: {unmapped}"


def test_no_upward_imports() -> None:
    violations: set[str] = set()
    for path in _iter_modules():
        importer = _module_key(path)
        importer_rank = LAYER.get(importer)
        if importer_rank is None:
            continue  # reported by test_layer_map_is_total
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            for target in _internal_targets(node):
                if importer_rank >= LAYER[target]:
                    continue
                if (importer, target) in ALLOWED_UPWARD:
                    continue
                violations.add(
                    f"{importer} (layer {importer_rank}) imports "
                    f"{target} (layer {LAYER[target]})"
                )
    assert not violations, "upward imports break the layer DAG:\n" + "\n".join(
        sorted(violations)
    )
