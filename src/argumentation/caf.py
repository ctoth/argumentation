"""Claim-augmented argumentation frameworks.

CAFs attach claim identifiers to Dung arguments.  Inherited semantics computes
ordinary Dung extensions first and projects them to claim sets.  The claim-level
view uses the same generated argument candidates but maximizes after projection,
so duplicate arguments for the same claim do not inflate the result.

References:
    Dvorak, Gressler, Rapberger, and Woltran (2023). The complexity landscape
    of claim-augmented argumentation frameworks.
    Dvorak, Rapberger, and Woltran (2020). Argumentation semantics under a
    claim-centric view.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal, Mapping

from argumentation.dung import (
    ArgumentationFramework,
    cf2_extensions,
    complete_extensions,
    grounded_extension,
    naive_extensions,
    preferred_extensions,
    semi_stable_extensions,
    stable_extensions,
    stage_extensions,
)


CAFView = Literal["inherited", "claim_level"]


@dataclass(frozen=True)
class ClaimAugmentedAF:
    framework: ArgumentationFramework
    claims: Mapping[str, str]

    def __post_init__(self) -> None:
        claim_keys = set(self.claims)
        arguments = set(self.framework.arguments)
        missing = sorted(arguments - claim_keys)
        extra = sorted(claim_keys - arguments)
        if missing or extra:
            raise ValueError(
                "claims must contain exactly the framework arguments: "
                f"missing={missing!r}, extra={extra!r}"
            )
        object.__setattr__(
            self,
            "claims",
            {argument: str(claim) for argument, claim in self.claims.items()},
        )


def inherited_extensions(
    caf: ClaimAugmentedAF,
    *,
    semantics: str,
) -> tuple[frozenset[str], ...]:
    """Project Dung extensions to claim sets."""
    return _deduplicate_claim_sets(
        _project(caf, extension)
        for extension in _argument_extensions(caf.framework, semantics)
    )


def claim_level_extensions(
    caf: ClaimAugmentedAF,
    *,
    semantics: str,
) -> tuple[frozenset[str], ...]:
    """Return inclusion-maximal projected claim sets."""
    projected = list(inherited_extensions(caf, semantics=semantics))
    return tuple(
        claim_set
        for claim_set in projected
        if not any(claim_set < other for other in projected)
    )


def concurrence_holds(caf: ClaimAugmentedAF, *, semantics: str) -> bool:
    """Return whether inherited and claim-level views agree."""
    return set(inherited_extensions(caf, semantics=semantics)) == set(
        claim_level_extensions(caf, semantics=semantics)
    )


def extensions(
    caf: ClaimAugmentedAF,
    *,
    semantics: str,
    view: CAFView = "inherited",
) -> tuple[frozenset[str], ...]:
    """Dispatch CAF extensions by view."""
    if view == "inherited":
        return inherited_extensions(caf, semantics=semantics)
    if view == "claim_level":
        return claim_level_extensions(caf, semantics=semantics)
    raise ValueError(f"unsupported CAF view: {view}")


def _argument_extensions(
    framework: ArgumentationFramework,
    semantics: str,
) -> tuple[frozenset[str], ...]:
    if semantics == "grounded":
        return (grounded_extension(framework),)
    if semantics == "complete":
        return tuple(complete_extensions(framework))
    if semantics == "preferred":
        return tuple(preferred_extensions(framework))
    if semantics == "stable":
        return tuple(stable_extensions(framework))
    if semantics == "semi-stable":
        return tuple(semi_stable_extensions(framework))
    if semantics == "stage":
        return tuple(stage_extensions(framework))
    if semantics == "naive":
        return tuple(naive_extensions(framework))
    if semantics == "cf2":
        return tuple(cf2_extensions(framework))
    raise ValueError(f"unsupported CAF semantics: {semantics}")


def _project(caf: ClaimAugmentedAF, extension: frozenset[str]) -> frozenset[str]:
    return frozenset(caf.claims[argument] for argument in extension)


def _deduplicate_claim_sets(
    claim_sets: Iterable[frozenset[str]],
) -> tuple[frozenset[str], ...]:
    unique = set(claim_sets)
    return tuple(sorted(unique, key=lambda item: (len(item), tuple(sorted(item)))))
