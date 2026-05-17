"""SMT-backed tactical witnesses for dialectical chess."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from dialectical_chess.board import (
    BISHOP_DELTAS,
    ROOK_DELTAS,
    file_of,
    piece_color,
    rank_of,
    square_from_file_rank,
)
from dialectical_chess.search import owned_is_checkmate


@dataclass(frozen=True)
class SmtSettings:
    mate_in_one: bool = True
    fork: bool = True


def smt_mate_in_one_moves(board: Any) -> frozenset[str]:
    try:
        from z3 import Bool, Or, Solver, sat
    except ImportError:
        return frozenset()

    mate_moves: dict[str, Any] = {}
    for move in board.legal_moves():
        if owned_is_checkmate(board.apply(move)):
            mate_moves[move.uci()] = Bool(f"mate_{move.uci()}")

    if not mate_moves:
        return frozenset()

    solver = Solver()
    solver.add(Or(*mate_moves.values()))
    if solver.check() != sat:
        return frozenset()
    model = solver.model()
    witnesses = {
        move
        for move, variable in mate_moves.items()
        if model.eval(variable, model_completion=True)
    }
    return frozenset(move for move in witnesses if verifies_mate_in_one(board, move))


def verifies_mate_in_one(board: Any, move_text: str) -> bool:
    legal_by_uci = {move.uci(): move for move in board.legal_moves()}
    move = legal_by_uci.get(move_text)
    return move is not None and owned_is_checkmate(board.apply(move))


def smt_fork_moves(
    board: Any,
    *,
    min_targets: int = 2,
    min_target_value: int = 500,
) -> frozenset[str]:
    try:
        from z3 import And, Int, Or, Solver, sat
    except ImportError:
        return frozenset()

    legal_moves = tuple(board.legal_moves())
    candidates: list[tuple[int, Any, tuple[int, int]]] = []
    for index, move in enumerate(legal_moves):
        target_count, target_value = fork_targets_after(board, move)
        if target_count >= min_targets and target_value >= min_target_value:
            candidates.append((index, move, (target_count, target_value)))

    if not candidates:
        return frozenset()

    move_index = Int("fork_move_index")
    solver = Solver()
    solver.add(Or(*(move_index == index for index, _, _ in candidates)))
    solver.add(
        Or(
            *(
                And(move_index == index, target_count >= min_targets, target_value >= min_target_value)
                for index, _, (target_count, target_value) in candidates
            )
        )
    )
    if solver.check() != sat:
        return frozenset()
    selected_index = solver.model().eval(move_index, model_completion=True).as_long()
    return frozenset(move.uci() for index, move, _ in candidates if index == selected_index)


def fork_targets_after(board: Any, move: Any) -> tuple[int, int]:
    moving_piece = board.piece_at(move.from_square)
    if moving_piece is None:
        return (0, 0)
    child = board.apply(move)
    targets = []
    for square, piece in enumerate(child.squares):
        if piece is None or piece_color(piece) == piece_color(moving_piece):
            continue
        if moved_piece_attacks_square(child, move.to_square, square, moving_piece):
            targets.append(piece_value(piece))
    return (len(targets), sum(targets))


def moved_piece_attacks_square(board: Any, source_square: int, target_square: int, piece: str) -> bool:
    kind = piece.lower()
    if kind == "p":
        direction = 1 if piece_color(piece) == "w" else -1
        return rank_of(target_square) - rank_of(source_square) == direction and abs(
            file_of(target_square) - file_of(source_square)
        ) == 1
    if kind == "n":
        return (abs(file_of(target_square) - file_of(source_square)), abs(rank_of(target_square) - rank_of(source_square))) in {
            (1, 2),
            (2, 1),
        }
    if kind == "k":
        return max(
            abs(file_of(target_square) - file_of(source_square)),
            abs(rank_of(target_square) - rank_of(source_square)),
        ) == 1
    if kind == "b":
        return ray_attacks_square(board, source_square, target_square, BISHOP_DELTAS)
    if kind == "r":
        return ray_attacks_square(board, source_square, target_square, ROOK_DELTAS)
    if kind == "q":
        return ray_attacks_square(board, source_square, target_square, BISHOP_DELTAS + ROOK_DELTAS)
    return False


def ray_attacks_square(board: Any, source_square: int, target_square: int, deltas: tuple[tuple[int, int], ...]) -> bool:
    source_file = file_of(source_square)
    source_rank = rank_of(source_square)
    for df, dr in deltas:
        file_index = source_file + df
        rank_index = source_rank + dr
        while True:
            square = square_from_file_rank(file_index, rank_index)
            if square is None:
                break
            if square == target_square:
                return True
            if board.piece_at(square) is not None:
                break
            file_index += df
            rank_index += dr
    return False


def piece_value(piece: str) -> int:
    return {"p": 100, "n": 320, "b": 330, "r": 500, "q": 900, "k": 0}[piece.lower()]
