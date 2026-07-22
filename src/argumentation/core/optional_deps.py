"""Optional third-party dependency loaders shared across layers.

These helpers lazily import optional solver backends so that the package
remains importable when the backend is absent. The import happens inside the
function body (never at module top) because the dependency is optional.
"""

from __future__ import annotations

from typing import Any


class OptionalDependencyUnavailable(RuntimeError):
    """A specific optional Python package required by a feature is absent."""

    def __init__(
        self,
        *,
        feature: str,
        package: str,
        install_hint: str,
    ) -> None:
        super().__init__(f"{feature} requires {package}")
        self.package = package
        self.install_hint = install_hint


def load_z3(feature: str) -> Any:
    """Lazily import and return the ``z3`` module.

    Raises ``OptionalDependencyUnavailable`` (chained from the original
    ``ImportError``) with exact dependency guidance when ``z3-solver`` is not
    installed.
    """
    try:
        import z3  # type: ignore[import-not-found]
    except ImportError as exc:
        raise OptionalDependencyUnavailable(
            feature=feature,
            package="z3-solver",
            install_hint="Install the z3-solver extra or use backend='native'.",
        ) from exc
    return z3
