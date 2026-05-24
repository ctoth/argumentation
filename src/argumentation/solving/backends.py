"""Backend capability detection and default selection rules."""

from __future__ import annotations

import importlib.util
import shutil


def has_clingo() -> bool:
    return shutil.which("clingo") is not None or importlib.util.find_spec("clingo") is not None


def has_z3() -> bool:
    return importlib.util.find_spec("z3") is not None


def default_backend(
    semantics: str,
    theory_size: int,
    has_preferences: bool,
    weakest_link: bool,
) -> str:
    """Return the documented default backend for an argumentation query."""
    del has_preferences
    if weakest_link:
        return "materialized_reference"
    if semantics == "grounded":
        return "asp"
    if theory_size > 30 and has_clingo():
        return "asp"
    if has_z3():
        return "sat"
    return "materialized_reference"


def backend_choice_reason(
    semantics: str,
    theory_size: int,
    has_preferences: bool,
    weakest_link: bool,
) -> str:
    backend = default_backend(semantics, theory_size, has_preferences, weakest_link)
    return (
        f"default_backend={backend}; semantics={semantics}; "
        f"theory_size={theory_size}; has_preferences={has_preferences}; "
        f"weakest_link={weakest_link}; has_clingo={has_clingo()}; has_z3={has_z3()}"
    )


__all__ = ["backend_choice_reason", "default_backend", "has_clingo", "has_z3"]
