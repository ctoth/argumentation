"""Shared semantic-reduct value objects."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Generic, TypeVar


TFramework = TypeVar("TFramework")
TAtom = TypeVar("TAtom")


@dataclass(frozen=True)
class SemanticReduct(Generic[TFramework, TAtom]):
    """A semantics-preserving reduct plus its lift-back map.

    The reducer owns how the reduct is computed. This value object only records
    the relation it established: residual extensions lift to original extensions
    by unioning the atoms already fixed IN, and atoms fixed OUT cannot occur in a
    valid lifted extension.
    """

    original: TFramework
    residual: TFramework
    fixed_in: frozenset[TAtom]
    fixed_out: frozenset[TAtom]

    @property
    def is_trivial(self) -> bool:
        """True when the residual is the whole framework."""
        return not self.fixed_in and not self.fixed_out

    def lift(self, residual_extension: Iterable[TAtom]) -> frozenset[TAtom]:
        """Map an extension of ``residual`` back to an extension of ``original``."""
        return frozenset(residual_extension) | self.fixed_in

    def lift_all(
        self,
        residual_extensions: Iterable[Iterable[TAtom]],
    ) -> list[frozenset[TAtom]]:
        """Map residual extensions back, de-duplicated in encounter order."""
        seen: set[frozenset[TAtom]] = set()
        lifted: list[frozenset[TAtom]] = []
        for extension in residual_extensions:
            value = self.lift(extension)
            if value not in seen:
                seen.add(value)
                lifted.append(value)
        return lifted

    def project_requirements(
        self,
        *,
        required_in: Iterable[TAtom] = (),
        required_out: Iterable[TAtom] = (),
    ) -> tuple[frozenset[TAtom], frozenset[TAtom]] | None:
        """Project original required-IN/OUT atoms, or return ``None`` if unsatisfiable."""
        required_in_set = frozenset(required_in)
        required_out_set = frozenset(required_out)
        projected_in = required_in_set - self.fixed_in
        projected_out = required_out_set - self.fixed_out
        if (
            required_in_set & self.fixed_out
            or required_out_set & self.fixed_in
            or projected_in & projected_out
        ):
            return None
        return projected_in, projected_out


__all__ = ["SemanticReduct"]
