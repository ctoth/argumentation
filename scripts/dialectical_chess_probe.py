# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "chess>=1.11.0",
#   "z3-solver>=4.12",
# ]
# ///
"""PEP 723 entrypoint for the dialectical chess probe engine."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

import chess

from dialectical_chess.adapters import build_pgn, build_svg, final_board, load_game
from dialectical_chess.arguments import build_argument_payload
from dialectical_chess.engine import DialecticalChessEngine, EngineSettings
from dialectical_chess.probe import owned_board_from_fen
from dialectical_chess.uci import run_uci


DEFAULT_FEN = "7k/6pp/8/8/8/8/6PP/R5K1 w - - 0 1"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fen")
    parser.add_argument("--pgn-in", type=Path)
    parser.add_argument("--pgn-out", type=Path)
    parser.add_argument("--pgn", type=Path)
    parser.add_argument("--svg", type=Path)
    parser.add_argument("--emit-af", type=Path)
    parser.add_argument("--list-legal", action="store_true")
    parser.add_argument("--choose", action="store_true")
    parser.add_argument("--uci", action="store_true")
    parser.add_argument("--dialectic-depth", type=int, default=1)
    parser.add_argument("--search-depth", type=int, default=0)
    parser.add_argument(
        "--search-backend",
        choices=("negamax", "alphabeta"),
        default="negamax",
    )
    parser.add_argument("--no-smt-mate", action="store_false", dest="smt_mate")
    parser.add_argument("--size", type=int, default=480)
    args = parser.parse_args(argv)

    if args.uci:
        return run_uci(
            sys.stdin,
            sys.stdout,
            dialectic_depth=args.dialectic_depth,
            search_depth=args.search_depth,
            search_backend=args.search_backend,
            smt_mate=args.smt_mate,
        )

    game = load_game(args.pgn_in) if args.pgn_in else None
    notation_board = final_board(game) if game else chess.Board(args.fen or DEFAULT_FEN)
    board = owned_board_from_fen(notation_board.fen())
    engine = DialecticalChessEngine(
        EngineSettings(
            dialectic_depth=args.dialectic_depth,
            search_depth=args.search_depth,
            search_backend=args.search_backend,
            smt_mate=args.smt_mate,
        )
    )
    analysis = engine.analyze(board)
    selected = analysis.decision.selected

    if args.svg:
        args.svg.parent.mkdir(parents=True, exist_ok=True)
        args.svg.write_text(build_svg(notation_board, size=args.size), encoding="utf-8")

    pgn_path = args.pgn_out or args.pgn
    if pgn_path and selected is not None:
        pgn_path.parent.mkdir(parents=True, exist_ok=True)
        pgn_path.write_text(build_pgn(notation_board, selected, game=game), encoding="utf-8")

    if args.list_legal:
        for probe in analysis.probes:
            print(f"{probe.uci:5} {probe.san:8} score={probe.score:6} {', '.join(probe.reasons)}")

    if args.emit_af:
        af_payload = build_argument_payload(list(analysis.probes), analysis.graph)
        args.emit_af.parent.mkdir(parents=True, exist_ok=True)
        args.emit_af.write_text(json.dumps(af_payload, indent=2), encoding="utf-8")

    if args.choose:
        print(json.dumps(asdict(selected), indent=2) if selected is not None else json.dumps(asdict(analysis.decision), indent=2))

    if not any([args.svg, pgn_path, args.list_legal, args.emit_af, args.choose]):
        print(f"fen: {board.fen()}")
        if selected is None:
            print("bestmove: 0000")
            print("reasons: no legal moves")
        else:
            print(f"bestmove: {selected.uci} ({selected.san})")
            print(f"reasons: {', '.join(selected.reasons)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
