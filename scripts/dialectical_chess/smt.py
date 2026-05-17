"""SMT-backed tactical witnesses for dialectical chess."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from dialectical_chess.search import owned_is_checkmate


@dataclass(frozen=True)
class SmtSettings:
    mate_in_one: bool = True


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
