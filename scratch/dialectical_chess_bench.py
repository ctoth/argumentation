# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "chess>=1.11.0",
#   "z3-solver>=4.12",
# ]
# ///
"""EPD benchmark runner for the dialectical chess probe."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

import chess


ROOT = Path(__file__).resolve().parents[1]
PROBE_PATH = ROOT / "scratch" / "dialectical_chess_probe.py"
BUILT_IN_EPD = (
    '7k/6pp/8/8/8/8/6PP/R5K1 w - - bm Ra8#; id "mate-in-one-smoke";'
)
BM_RE = re.compile(r"\bbm\s+([^;]+);")
ID_RE = re.compile(r"\bid\s+\"([^\"]+)\";")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--epd", type=Path)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--dialectic-depth", type=int, default=1)
    parser.add_argument("--search-depth", type=int, default=0)
    parser.add_argument(
        "--search-backend",
        choices=("negamax", "alphabeta"),
        default="negamax",
    )
    parser.add_argument("--no-smt-mate", action="store_false", dest="smt_mate")
    parser.set_defaults(smt_mate=True)
    args = parser.parse_args()

    probe = load_probe()
    lines = read_epd_lines(args.epd)
    results = []
    started = time.perf_counter()
    for index, line in enumerate(lines, start=1):
        case = parse_epd_case(line, index=index)
        case_started = time.perf_counter()
        probes = probe.probe_moves(
            case["board"],
            dialectic_depth=args.dialectic_depth,
            search_depth=args.search_depth,
            search_backend=args.search_backend,
            smt_mate=args.smt_mate,
        )
        selected = probe.choose_move(probes, probe.build_root_argument_graph(probes))
        elapsed_ms = (time.perf_counter() - case_started) * 1000.0
        results.append(
            {
                "id": case["id"],
                "fen": case["board"].fen(),
                "expected_uci": sorted(case["expected_uci"]),
                "selected_uci": selected.uci,
                "selected_san": selected.san,
                "correct": selected.uci in case["expected_uci"],
                "score": selected.score,
                "reasons": list(selected.reasons),
                "objections": list(selected.objections),
                "reply_attacks": list(selected.reply_attacks),
                "search_score": selected.search_score,
                "search_line": list(selected.search_line),
                "smt_witnesses": list(selected.smt_witnesses),
                "elapsed_ms": elapsed_ms,
            }
        )

    total_elapsed_ms = (time.perf_counter() - started) * 1000.0
    solved = sum(1 for result in results if result["correct"])
    payload = {
        "suite": str(args.epd) if args.epd else "built-in-smoke",
        "total": len(results),
        "solved": solved,
        "hit_rate": solved / len(results) if results else 0.0,
        "elapsed_ms": total_elapsed_ms,
        "ms_per_position": total_elapsed_ms / len(results) if results else 0.0,
        "settings": {
            "dialectic_depth": args.dialectic_depth,
            "search_depth": args.search_depth,
            "search_backend": args.search_backend,
            "smt_mate": args.smt_mate,
        },
        "positions": results,
    }
    text = json.dumps(payload, indent=2)
    print(text)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")
    return 0


def load_probe() -> Any:
    spec = importlib.util.spec_from_file_location("dialectical_chess_probe", PROBE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {PROBE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def read_epd_lines(path: Path | None) -> list[str]:
    if path is None:
        return [BUILT_IN_EPD]
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def parse_epd_case(line: str, *, index: int) -> dict[str, Any]:
    fields = line.split(maxsplit=4)
    if len(fields) < 5:
        raise ValueError(f"invalid EPD line {index}: {line}")
    fen = " ".join(fields[:4] + ["0", "1"])
    board = chess.Board(fen)
    operations = fields[4]
    bm_match = BM_RE.search(operations)
    if bm_match is None:
        raise ValueError(f"EPD line {index} has no bm operation")
    expected_uci = {
        parse_expected_move(board, token).uci()
        for token in bm_match.group(1).split()
    }
    id_match = ID_RE.search(operations)
    return {
        "id": id_match.group(1) if id_match else f"position-{index}",
        "board": board,
        "expected_uci": expected_uci,
    }


def parse_expected_move(board: chess.Board, token: str) -> chess.Move:
    try:
        move = chess.Move.from_uci(token)
    except ValueError:
        move = chess.Move.null()
    if move in board.legal_moves:
        return move
    return board.parse_san(token)


if __name__ == "__main__":
    raise SystemExit(main())
