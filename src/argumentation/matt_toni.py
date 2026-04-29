"""Matt-Toni game-theoretic argument strength."""

from __future__ import annotations

from itertools import combinations

from argumentation.dung import ArgumentationFramework, conflict_free


class MattToniIntractable(ValueError):
    """Raised when exact strategy enumeration would exceed the configured cap."""


def matt_toni_strength(
    framework: ArgumentationFramework,
    argument: str,
    *,
    max_arguments: int = 12,
) -> float:
    """Return the value of the argumentation-strategy game for ``argument``.

    Matt and Toni 2008, JELIA, p. 291, Definition 6 defines strength as the
    value of the zero-sum game; p. 289, Definition 5 defines the payoff.
    """

    if argument not in framework.arguments:
        raise ValueError(f"unknown argument: {argument!r}")
    if len(framework.arguments) > max_arguments:
        raise MattToniIntractable(
            f"Matt-Toni exact strength is capped at {max_arguments} arguments"
        )

    proponent = [
        subset
        for subset in _all_subsets(framework.arguments)
        if argument in subset and conflict_free(subset, framework.defeats)
    ]
    if not proponent:
        return 0.0

    opponents = [
        subset
        for subset in _all_subsets(framework.arguments)
        if subset
    ]
    if not opponents:
        return 1.0

    matrix = [
        [_reward(framework, p_strategy, o_strategy) for o_strategy in opponents]
        for p_strategy in proponent
    ]
    return _zero_sum_row_value(matrix)


def matt_toni_strengths(
    framework: ArgumentationFramework,
    *,
    max_arguments: int = 12,
) -> dict[str, float]:
    """Return Matt-Toni strengths for every argument in the framework."""

    return {
        argument: matt_toni_strength(
            framework,
            argument,
            max_arguments=max_arguments,
        )
        for argument in sorted(framework.arguments)
    }


def _reward(
    framework: ArgumentationFramework,
    proponent: frozenset[str],
    opponent: frozenset[str],
) -> float:
    if not conflict_free(proponent, framework.defeats):
        return 0.0
    attacks_o_to_p = _attack_count(framework, opponent, proponent)
    if attacks_o_to_p == 0:
        return 1.0
    attacks_p_to_o = _attack_count(framework, proponent, opponent)
    return 0.5 * (
        1.0
        + _normalised_attack_count(attacks_p_to_o)
        - _normalised_attack_count(attacks_o_to_p)
    )


def _attack_count(
    framework: ArgumentationFramework,
    source: frozenset[str],
    target: frozenset[str],
) -> int:
    return sum(
        1
        for attacker, attacked in framework.defeats
        if attacker in source and attacked in target
    )


def _normalised_attack_count(count: int) -> float:
    return count / (count + 1.0)


def _zero_sum_row_value(matrix: list[list[float]]) -> float:
    row_count = len(matrix)
    column_count = len(matrix[0])
    best = 0.0
    max_support = min(row_count, column_count)
    for size in range(1, max_support + 1):
        for rows in combinations(range(row_count), size):
            for columns in combinations(range(column_count), size):
                solution = _solve_active_system(matrix, rows, columns)
                if solution is None:
                    continue
                probabilities, value = solution
                if any(probability < -1e-9 for probability in probabilities):
                    continue
                payoffs = [
                    sum(
                        probabilities[index] * matrix[row][column]
                        for index, row in enumerate(rows)
                    )
                    for column in range(column_count)
                ]
                if min(payoffs) + 1e-8 >= value:
                    best = max(best, value)
    pure = max(min(row) for row in matrix)
    return min(1.0, max(0.0, max(best, pure)))


def _solve_active_system(
    matrix: list[list[float]],
    rows: tuple[int, ...],
    columns: tuple[int, ...],
) -> tuple[list[float], float] | None:
    size = len(rows)
    equations: list[list[float]] = []
    rhs: list[float] = []
    equations.append([1.0] * size + [0.0])
    rhs.append(1.0)
    for column in columns:
        equations.append([matrix[row][column] for row in rows] + [-1.0])
        rhs.append(0.0)
    solved = _gaussian_elimination(equations, rhs)
    if solved is None:
        return None
    return solved[:-1], solved[-1]


def _gaussian_elimination(
    matrix: list[list[float]],
    rhs: list[float],
) -> list[float] | None:
    n = len(rhs)
    rows = [row[:] + [value] for row, value in zip(matrix, rhs, strict=True)]
    for column in range(n):
        pivot = max(range(column, n), key=lambda row: abs(rows[row][column]))
        if abs(rows[pivot][column]) < 1e-12:
            return None
        rows[column], rows[pivot] = rows[pivot], rows[column]
        divisor = rows[column][column]
        rows[column] = [value / divisor for value in rows[column]]
        for row in range(n):
            if row == column:
                continue
            factor = rows[row][column]
            rows[row] = [
                current - factor * pivot_value
                for current, pivot_value in zip(rows[row], rows[column], strict=True)
            ]
    return [rows[row][-1] for row in range(n)]


def _all_subsets(arguments: frozenset[str]) -> list[frozenset[str]]:
    ordered = tuple(sorted(arguments))
    return [
        frozenset(ordered[index] for index in range(len(ordered)) if mask & (1 << index))
        for mask in range(1 << len(ordered))
    ]
