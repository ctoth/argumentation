"""PGN, SVG, and notation adapters for dialectical chess scripts."""

from __future__ import annotations

from pathlib import Path

import chess
import chess.pgn
import chess.svg

from dialectical_chess.arguments import MoveProbe


def load_game(path: Path) -> chess.pgn.Game:
    with path.open(encoding="utf-8") as handle:
        game = chess.pgn.read_game(handle)
    if game is None:
        raise SystemExit(f"no PGN game found in {path}")
    return game


def final_board(game: chess.pgn.Game) -> chess.Board:
    board = game.board()
    for move in game.mainline_moves():
        board.push(move)
    return board


def build_svg(board: chess.Board, *, size: int) -> str:
    return chess.svg.board(board=board, size=size)


def build_pgn(
    board: chess.Board,
    selected: MoveProbe,
    *,
    game: chess.pgn.Game | None = None,
) -> str:
    output = clone_game_without_variations(game) if game else chess.pgn.Game()
    if game is None:
        output.headers["Event"] = "Dialectical chess probe"
        output.headers["Site"] = "C:/Users/Q/code/argumentation"
        output.headers["Round"] = "-"
        output.headers["White"] = "DialecticalProbe" if board.turn == chess.WHITE else "Unknown"
        output.headers["Black"] = "Unknown" if board.turn == chess.WHITE else "DialecticalProbe"
        if board.board_fen() != chess.STARTING_BOARD_FEN or board.fullmove_number != 1:
            output.headers["SetUp"] = "1"
            output.headers["FEN"] = board.fen()

    move = chess.Move.from_uci(selected.uci)
    next_board = board.copy(stack=False)
    next_board.push(move)
    if next_board.is_checkmate():
        output.headers["Result"] = "1-0" if board.turn == chess.WHITE else "0-1"
    elif next_board.is_stalemate() or next_board.is_insufficient_material():
        output.headers["Result"] = "1/2-1/2"
    else:
        output.headers["Result"] = "*"

    node = last_mainline_node(output)
    node.add_variation(move, comment="; ".join(selected.reasons or selected.objections))
    return str(output) + "\n"


def clone_game_without_variations(game: chess.pgn.Game) -> chess.pgn.Game:
    cloned = chess.pgn.Game()
    cloned.headers.clear()
    for key, value in game.headers.items():
        cloned.headers[key] = value

    source_node: chess.pgn.GameNode = game
    target_node: chess.pgn.GameNode = cloned
    while source_node.variations:
        source_node = source_node.variations[0]
        target_node = target_node.add_variation(
            source_node.move,
            comment=source_node.comment,
            nags=source_node.nags,
            starting_comment=source_node.starting_comment,
        )
    return cloned


def last_mainline_node(game: chess.pgn.Game) -> chess.pgn.GameNode:
    node: chess.pgn.GameNode = game
    while node.variations:
        node = node.variations[0]
    return node
