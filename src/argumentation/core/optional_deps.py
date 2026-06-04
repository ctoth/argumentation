"""Optional third-party dependency loaders shared across layers.

These helpers lazily import optional solver backends so that the package
remains importable when the backend is absent. The import happens inside the
function body (never at module top) because the dependency is optional.
"""

from __future__ import annotations

from typing import Any


def load_z3(feature: str) -> Any:
    """Lazily import and return the ``z3`` module.

    Raises ``RuntimeError`` (chained from the original ``ImportError``) with a
    feature-specific message when ``z3-solver`` is not installed, preserving
    each caller's original error text via ``feature``.
    """
    try:
        import z3  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError(f"{feature} requires z3-solver") from exc
    return z3
