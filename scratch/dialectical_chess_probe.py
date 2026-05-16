# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "chess>=1.11.0",
# ]
# ///
"""Sidecar probe for dialectical chess experiments.

This is intentionally outside the package source tree. It uses PEP 723 inline
metadata so `uv run scratch/dialectical_chess_probe.py ...` can fetch only the
prototype dependencies needed by this script.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import chess
import chess.pgn
import chess.svg


DEFAULT_FEN = "7k/6pp/8/8/8/8/6PP/R5K1 w - - 0 1"
PIECE_VALUE = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0,
}


@dataclass(frozen=True)
class MoveProbe:
    uci: str
    san: str
    score: int
    is_checkmate: bool
    gives_check: bool
    is_capture: bool
    captured_value: int
    promotion_value: int
    reasons: tuple[str, ...]
    objections: tuple[str, ...]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fen", default=DEFAULT_FEN)
    parser.add_argument("--pgn", type=Path)
    parser.add_argument("--svg", type=Path)
    parser.add_argument("--emit-af", type=Path)
    parser.add_argument("--list-legal", action="store_true")
    parser.add_argument("--choose", action="store_true")
    parser.add_argument("--size", type=int, default=480)
    args = parser.parse_args(argv)

    board = chess.Board(args.fen)
    probes = probe_moves(board)

    if args.svg:
        svg = chess.svg.board(board=board, size=args.size)
        args.svg.parent.mkdir(parents=True, exist_ok=True)
        args.svg.write_text(svg, encoding="utf-8")

    if args.pgn:
        args.pgn.parent.mkdir(parents=True, exist_ok=True)
        args.pgn.write_text(build_pgn(board, choose_move(probes)), encoding="utf-8")

    if args.list_legal:
        for probe in probes:
            print(f"{probe.uci:5} {probe.san:8} score={probe.score:6} {', '.join(probe.reasons)}")

    if args.emit_af:
        af_payload = build_argument_payload(probes)
        args.emit_af.parent.mkdir(parents=True, exist_ok=True)
        args.emit_af.write_text(json.dumps(af_payload, indent=2), encoding="utf-8")

    if args.choose:
        selected = choose_move(probes)
        print(json.dumps(asdict(selected), indent=2))

    if not any([args.svg, args.pgn, args.list_legal, args.emit_af, args.choose]):
        selected = choose_move(probes)
        print(f"fen: {board.fen()}")
        print(f"bestmove: {selected.uci} ({selected.san})")
        print(f"reasons: {', '.join(selected.reasons)}")

    return 0


def probe_moves(board: chess.Board) -> list[MoveProbe]:
    probes = []
    for move in board.legal_moves:
        san = board.san(move)
        is_capture = board.is_capture(move)
        captured_value = capture_value(board, move)
        promotion_value = PIECE_VALUE.get(move.promotion, 0)

        board.push(move)
        is_checkmate = board.is_checkmate()
        gives_check = board.is_check()
        board.pop()

        reasons: list[str] = []
        objections: list[str] = []
        score = 0

        if is_checkmate:
            score += 1_000_000
            reasons.append("terminal:checkmate")
        if gives_check:
            score += 1_000
            reasons.append("tactical:check")
        if is_capture:
            score += captured_value
            reasons.append(f"material:capture:{captured_value}")
        if promotion_value:
            score += promotion_value
            reasons.append(f"material:promotion:{promotion_value}")
        if not reasons:
            objections.append("objection:no_immediate_tactical_warrant")

        probes.append(
            MoveProbe(
                uci=move.uci(),
                san=san,
                score=score,
                is_checkmate=is_checkmate,
                gives_check=gives_check,
                is_capture=is_capture,
                captured_value=captured_value,
                promotion_value=promotion_value,
                reasons=tuple(reasons),
                objections=tuple(objections),
            )
        )
    return sorted(probes, key=lambda probe: (-probe.score, probe.uci))


def capture_value(board: chess.Board, move: chess.Move) -> int:
    if board.is_en_passant(move):
        return PIECE_VALUE[chess.PAWN]
    captured = board.piece_at(move.to_square)
    if captured is None:
        return 0
    return PIECE_VALUE[captured.piece_type]


def choose_move(probes: list[MoveProbe]) -> MoveProbe:
    if not probes:
        raise SystemExit("position has no legal moves")
    return probes[0]


def build_pgn(board: chess.Board, selected: MoveProbe) -> str:
    game = chess.pgn.Game()
    game.headers["Event"] = "Dialectical chess probe"
    game.headers["Site"] = "C:/Users/Q/code/argumentation"
    game.headers["Round"] = "-"
    game.headers["White"] = "DialecticalProbe" if board.turn == chess.WHITE else "Unknown"
    game.headers["Black"] = "Unknown" if board.turn == chess.WHITE else "DialecticalProbe"
    if board.board_fen() != chess.STARTING_BOARD_FEN or board.fullmove_number != 1:
        game.headers["SetUp"] = "1"
        game.headers["FEN"] = board.fen()

    move = chess.Move.from_uci(selected.uci)
    next_board = board.copy(stack=False)
    next_board.push(move)
    if next_board.is_checkmate():
        game.headers["Result"] = "1-0" if board.turn == chess.WHITE else "0-1"
    elif next_board.is_stalemate() or next_board.is_insufficient_material():
        game.headers["Result"] = "1/2-1/2"
    else:
        game.headers["Result"] = "*"

    node = game
    node.add_variation(move, comment="; ".join(selected.reasons or selected.objections))
    return str(game) + "\n"


def build_argument_payload(probes: list[MoveProbe]) -> dict[str, Any]:
    arguments: set[str] = set()
    defeats: set[tuple[str, str]] = set()
    move_args = {probe.uci: f"move:{probe.uci}" for probe in probes}

    for probe in probes:
        move_arg = move_args[probe.uci]
        arguments.add(move_arg)
        for reason in probe.reasons:
            reason_arg = f"reason:{probe.uci}:{reason}"
            arguments.add(reason_arg)
            if reason == "terminal:checkmate":
                for other in probes:
                    if other.uci != probe.uci:
                        defeats.add((reason_arg, move_args[other.uci]))
        for objection in probe.objections:
            objection_arg = f"{objection}:{probe.uci}"
            arguments.add(objection_arg)
            defeats.add((objection_arg, move_arg))

    ranking = local_argumentation_ranking(arguments, defeats)
    return {
        "arguments": sorted(arguments),
        "defeats": sorted([list(pair) for pair in defeats]),
        "move_scores": [asdict(probe) for probe in probes],
        "argumentation_ranking": ranking,
    }


def local_argumentation_ranking(
    arguments: set[str],
    defeats: set[tuple[str, str]],
) -> dict[str, Any]:
    root = Path(__file__).resolve().parents[1]
    src = root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
    try:
        from argumentation.dung import ArgumentationFramework
        from argumentation.ranking import categoriser_scores
    except ImportError as exc:
        return {"available": False, "reason": str(exc)}

    framework = ArgumentationFramework(
        arguments=frozenset(arguments),
        defeats=frozenset(defeats),
    )
    result = categoriser_scores(framework)
    return {
        "available": True,
        "scores": dict(sorted(result.scores.items())),
        "ranking": [sorted(tier) for tier in result.ranking],
        "semantics": result.semantics,
    }


if __name__ == "__main__":
    raise SystemExit(main())
