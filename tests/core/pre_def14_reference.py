"""Verbatim copy of the core semantics before issue #90 (main 753569f).

Used only by the single-relation differential test: frameworks whose attacks
are absent or equal their defeats must give the same extensions after the
Modgil & Prakken 2018 Def 14 change as before it.
"""

from __future__ import annotations

from collections import deque

from argumentation.core.dung import ArgumentationFramework, admissible
from argumentation.core.finite import (
    iter_subsets_bitmask,
    maximal_sets,
    predecessors_index,
    successors_index,
)


def grounded_extension(framework: ArgumentationFramework) -> frozenset[str]:
    attackers_index = predecessors_index(framework.defeats)
    targets_index = successors_index(framework.defeats)
    live_attackers = {
        argument: len(attackers_index.get(argument, frozenset()))
        for argument in framework.arguments
    }
    queue = deque(
        argument for argument in framework.arguments if live_attackers[argument] == 0
    )
    in_arguments: set[str] = set()
    out_arguments: set[str] = set()

    while queue:
        argument = queue.popleft()
        if argument in in_arguments or argument in out_arguments:
            continue

        in_arguments.add(argument)
        for defeated in targets_index.get(argument, frozenset()):
            if defeated in out_arguments:
                continue
            out_arguments.add(defeated)
            for defended in targets_index.get(defeated, frozenset()):
                live_attackers[defended] -= 1
                if (
                    live_attackers[defended] == 0
                    and defended not in in_arguments
                    and defended not in out_arguments
                ):
                    queue.append(defended)

    return frozenset(in_arguments)


def complete_extensions(framework: ArgumentationFramework) -> list[frozenset[str]]:
    from argumentation.core.labelling import (
        DEFAULT_COMPLETE_LABELLING_CANDIDATE_BUDGET,
        complete_labellings,
    )

    attackers_index = predecessors_index(framework.defeats)
    return [
        labelling.extension
        for labelling in complete_labellings(
            framework,
            max_candidates=DEFAULT_COMPLETE_LABELLING_CANDIDATE_BUDGET,
        )
        if admissible(
            labelling.extension,
            framework.arguments,
            framework.defeats,
            attacks=framework.attacks,
            attackers_index=attackers_index,
        )
    ]


def preferred_extensions(framework: ArgumentationFramework) -> list[frozenset[str]]:
    if framework.attacks is None or framework.attacks == framework.defeats:
        return maximal_sets(complete_extensions(framework))
    attackers_index = predecessors_index(framework.defeats)
    return maximal_sets(
        [
            candidate
            for candidate in iter_subsets_bitmask(framework.arguments)
            if admissible(
                candidate,
                framework.arguments,
                framework.defeats,
                attacks=framework.attacks,
                attackers_index=attackers_index,
            )
        ]
    )


def stable_extensions(framework: ArgumentationFramework) -> list[frozenset[str]]:
    from argumentation.core.dung import conflict_free
    from argumentation.core.labelling import stable_labellings

    cf_relation = (
        framework.attacks if framework.attacks is not None else framework.defeats
    )
    return [
        labelling.extension
        for labelling in stable_labellings(framework)
        if conflict_free(labelling.extension, cf_relation)
    ]
