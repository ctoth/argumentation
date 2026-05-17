"""Loss turning-point mining for dialectical chess match PGNs."""

from __future__ import annotations

import io
from dataclasses import dataclass

import chess
import chess.pgn


@dataclass(frozen=True)
class LossTurningPoint:
    game_index: int
    ply: int
    fen_before: str
    played_move: str
    side_to_move: str
    result: str
    reason: str
    suggested_avoid_uci: list[str]


def mine_loss_turning_points(
    pgn_text: str,
    *,
    engine_name: str,
    mate_depth: int = 1,
) -> list[LossTurningPoint]:
    if mate_depth != 1:
        raise ValueError("only mate_depth=1 is implemented")
    points: list[LossTurningPoint] = []
    stream = io.StringIO(pgn_text)
    game_index = 0
    while True:
        game = chess.pgn.read_game(stream)
        if game is None:
            return points
        game_index += 1
        engine_color = engine_color_for_loss(game, engine_name)
        if engine_color is None:
            continue
        board = game.board()
        for ply, move in enumerate(game.mainline_moves(), start=1):
            fen_before = board.fen()
            mover = board.turn
            move_uci = move.uci()
            board.push(move)
            if mover == engine_color and has_immediate_mate(board):
                points.append(
                    LossTurningPoint(
                        game_index=game_index,
                        ply=ply,
                        fen_before=fen_before,
                        played_move=move_uci,
                        side_to_move="w" if engine_color == chess.WHITE else "b",
                        result=game.headers.get("Result", "*"),
                        reason="allows_mate_in_1",
                        suggested_avoid_uci=[],
                    )
                )
                break


def engine_color_for_loss(game: chess.pgn.Game, engine_name: str) -> bool | None:
    result = game.headers.get("Result", "*")
    if game.headers.get("White") == engine_name and result == "0-1":
        return chess.WHITE
    if game.headers.get("Black") == engine_name and result == "1-0":
        return chess.BLACK
    return None


def has_immediate_mate(board: chess.Board) -> bool:
    for reply in board.legal_moves:
        child = board.copy(stack=False)
        child.push(reply)
        if child.is_checkmate():
            return True
    return False


def reviewed_epd_lines(points: list[LossTurningPoint]) -> list[str]:
    lines = []
    for point in points:
        epd_position = " ".join(point.fen_before.split()[:4])
        reason = escape_epd_string(point.reason)
        lines.append(
            f'{epd_position} am {point.played_move}; '
            f'id "loss-{point.game_index}-ply-{point.ply}: {reason}";'
        )
    return lines


def escape_epd_string(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')
