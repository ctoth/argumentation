"""Benchmark suite parsing and scoring for the dialectical chess sidecar."""

from __future__ import annotations

import argparse
import csv
import json
import re
import time
from collections import Counter
from pathlib import Path
from typing import Any

import chess

from dialectical_chess.arguments import SELECTOR_MODES
from dialectical_chess.board import PERFT_FIXTURES, OwnedBoard, owned_perft
from dialectical_chess.engine import DialecticalChessEngine, EngineSettings
from dialectical_chess.loss_mining import mine_loss_turning_points, reviewed_epd_lines
from dialectical_chess.matches import run_internal_uci_match, run_uci_match


SCRIPT_DIR = Path(__file__).resolve().parents[1]
ROOT = SCRIPT_DIR.parent
PROBE_PATH = SCRIPT_DIR / "dialectical_chess_probe.py"
OWNED_PATH = SCRIPT_DIR / "dialectical_chess_owned.py"
OPENINGS_PATH = SCRIPT_DIR / "dialectical_chess_openings.epd"
BUILT_IN_EPD = '7k/6pp/8/8/8/8/6PP/R5K1 w - - bm Ra8#; id "mate-in-one-smoke";'
BM_RE = re.compile(r"\bbm\s+([^;]+);")
AM_RE = re.compile(r"\bam\s+([^;]+);")
ID_RE = re.compile(r"\bid\s+\"([^\"]+)\";")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--epd", type=Path)
    parser.add_argument("--lichess-puzzles", type=Path)
    parser.add_argument("--perft", action="store_true")
    parser.add_argument("--ablation", action="store_true")
    parser.add_argument("--mine-loss-pgn", type=Path)
    parser.add_argument("--loss-epd-out", type=Path)
    parser.add_argument("--loss-engine-name", default="Dialectical")
    parser.add_argument("--loss-mate-depth", type=int, default=1)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--fail-fast", action="store_true")
    parser.add_argument("--full-line", action="store_true")
    parser.add_argument("--rating-min", type=int)
    parser.add_argument("--rating-max", type=int)
    parser.add_argument("--theme-include", action="append", default=[])
    parser.add_argument("--theme-exclude", action="append", default=[])
    parser.add_argument("--side-to-move", choices=("w", "b"))
    parser.add_argument("--dialectic-depth", type=int, default=1)
    parser.add_argument("--search-depth", type=int, default=0)
    parser.add_argument("--search-backend", choices=("negamax", "alphabeta"), default="negamax")
    parser.add_argument("--selector-mode", choices=sorted(SELECTOR_MODES), default="argument")
    parser.add_argument("--selector-mode-ablation", action="store_true")
    parser.add_argument("--no-smt-mate", action="store_false", dest="smt_mate")
    parser.add_argument("--uci-match-command", action="store_true")
    parser.add_argument("--run-uci-match", action="store_true")
    parser.add_argument("--internal-uci-match", action="store_true")
    parser.add_argument("--match-baseline", choices=("nosmt", "random", "stockfish"), default="nosmt")
    parser.add_argument("--match-openings", type=Path, default=OPENINGS_PATH)
    parser.add_argument("--match-games", type=int, default=2)
    parser.add_argument("--match-max-plies", type=int, default=40)
    parser.add_argument("--match-pgn-out", type=Path)
    parser.add_argument("--match-tc", default="1+0.01")
    parser.add_argument("--stockfish-path")
    parser.add_argument("--stockfish-elo", type=int, default=1320)
    parser.set_defaults(smt_mate=True)
    args = parser.parse_args()

    started = time.perf_counter()
    if args.perft:
        payload = run_perft()
    elif args.mine_loss_pgn:
        payload = run_loss_mining(args)
    elif args.lichess_puzzles:
        payload = run_lichess(args)
    elif args.ablation:
        payload = run_ablation(args)
    elif args.internal_uci_match:
        payload = run_internal_uci_match(args)
    elif args.uci_match_command or args.run_uci_match:
        payload = run_uci_match(args)
    else:
        payload = run_epd(args)
    payload["elapsed_ms"] = (time.perf_counter() - started) * 1000.0
    payload["script_paths"] = {
        "probe": str(PROBE_PATH.relative_to(ROOT)),
        "owned": str(OWNED_PATH.relative_to(ROOT)),
    }
    text = json.dumps(payload, indent=2)
    print(text)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")
    return 0 if payload.get("ok", True) else 1


def run_loss_mining(args: argparse.Namespace) -> dict[str, Any]:
    pgn_text = args.mine_loss_pgn.read_text(encoding="utf-8")
    points = mine_loss_turning_points(
        pgn_text,
        engine_name=args.loss_engine_name,
        mate_depth=args.loss_mate_depth,
    )
    epd_lines = reviewed_epd_lines(points)
    if args.loss_epd_out:
        args.loss_epd_out.parent.mkdir(parents=True, exist_ok=True)
        args.loss_epd_out.write_text("\n".join(epd_lines) + ("\n" if epd_lines else ""), encoding="utf-8")
    return {
        "ok": True,
        "mode": "loss_mining",
        "pgn": str(args.mine_loss_pgn),
        "engine_name": args.loss_engine_name,
        "mate_depth": args.loss_mate_depth,
        "turning_points": [point.__dict__ for point in points],
        "epd_lines": epd_lines,
        "loss_epd_out": None if args.loss_epd_out is None else str(args.loss_epd_out),
    }


def run_epd(args: argparse.Namespace) -> dict[str, Any]:
    lines = read_epd_lines(args.epd)
    if args.limit is not None:
        lines = lines[: args.limit]
    results = []
    for index, line in enumerate(lines, start=1):
        try:
            case = parse_epd_case(line, index=index)
            result = score_board(
                case["board"],
                case["expected_uci"],
                args,
                avoid_uci=case["avoid_uci"],
            )
            result["id"] = case["id"]
            result["line"] = index
            result["fen"] = case["board"].fen()
            results.append(result)
        except Exception as exc:
            if args.fail_fast:
                raise
            results.append({"line": index, "error": str(exc), "correct": False})
    solved = sum(1 for result in results if result.get("correct"))
    avoided = sum(1 for result in results if result.get("avoided"))
    return {
        "ok": all("error" not in result for result in results),
        "mode": "epd",
        "suite": str(args.epd) if args.epd else "built-in-smoke",
        "total": len(results),
        "solved": solved,
        "hit_rate": solved / len(results) if results else 0.0,
        "avoided": avoided,
        "avoid_rate": avoided / len(results) if results else 0.0,
        "settings": settings(args),
        "positions": results,
    }


def run_ablation(args: argparse.Namespace) -> dict[str, Any]:
    base_epd = args.epd
    runs = []
    baseline_moves: list[str | None] | None = None
    for smt_mate in (True, False):
        for dialectic_depth in (0, 1, 2):
            for search_depth in (0, 1, 2, 3):
                for backend in ("negamax", "alphabeta"):
                    for selector_mode in ablation_selector_modes(args):
                        case_args = argparse.Namespace(**vars(args))
                        case_args.epd = base_epd
                        case_args.smt_mate = smt_mate
                        case_args.dialectic_depth = dialectic_depth
                        case_args.search_depth = search_depth
                        case_args.search_backend = backend
                        case_args.selector_mode = selector_mode
                        started = time.perf_counter()
                        payload = run_epd(case_args)
                        selected_moves = [
                            position.get("selected_uci")
                            for position in payload["positions"]
                        ]
                        if baseline_moves is None:
                            baseline_moves = selected_moves
                        runs.append(
                            {
                                "settings": settings(case_args),
                                "total": payload["total"],
                                "solved": payload["solved"],
                                "hit_rate": payload["hit_rate"],
                                "avoid_rate": payload["avoid_rate"],
                                "selected_move_deltas_vs_first": sum(
                                    left != right
                                    for left, right in zip(selected_moves, baseline_moves, strict=False)
                                ),
                                "elapsed_ms": (time.perf_counter() - started) * 1000.0,
                            }
                        )
    return {"ok": True, "mode": "ablation", "suite": str(base_epd) if base_epd else "built-in-smoke", "runs": runs}


def run_lichess(args: argparse.Namespace) -> dict[str, Any]:
    rows = []
    with args.lichess_puzzles.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if include_puzzle(row, args):
                rows.append(row)
            if args.limit is not None and len(rows) >= args.limit:
                break
    results = []
    by_rating: Counter[str] = Counter()
    rating_totals: Counter[str] = Counter()
    by_theme: Counter[str] = Counter()
    theme_totals: Counter[str] = Counter()
    for row in rows:
        board = chess.Board(row["FEN"])
        moves = row["Moves"].split()
        expected = {moves[0]} if moves else set()
        result = score_board(board, expected, args)
        result["id"] = row.get("PuzzleId", "")
        result["rating"] = int(row.get("Rating") or 0)
        result["themes"] = row.get("Themes", "").split()
        if args.full_line and result["correct"]:
            result["full_line_correct"] = score_full_line(board, moves, args)
        bucket = rating_bucket(result["rating"])
        rating_totals[bucket] += 1
        by_rating[bucket] += 1 if result["correct"] else 0
        for theme in result["themes"]:
            theme_totals[theme] += 1
            if result["correct"]:
                by_theme[theme] += 1
        results.append(result)
    solved = sum(1 for result in results if result.get("correct"))
    return {
        "ok": True,
        "mode": "lichess_csv",
        "suite": str(args.lichess_puzzles),
        "total": len(results),
        "solved": solved,
        "hit_rate": solved / len(results) if results else 0.0,
        "by_rating_bucket": {
            bucket: {"solved": by_rating[bucket], "total": rating_totals[bucket]}
            for bucket in sorted(rating_totals)
        },
        "by_theme": {
            theme: {"solved": by_theme[theme], "total": theme_totals[theme]}
            for theme in sorted(theme_totals)
        },
        "settings": settings(args),
        "positions": results,
    }


def run_perft() -> dict[str, Any]:
    results = []
    ok = True
    for name, (fen, depths) in PERFT_FIXTURES.items():
        board = OwnedBoard.from_fen(fen)
        for depth, expected in depths.items():
            started = time.perf_counter()
            actual = owned_perft(board, depth)
            elapsed_ms = (time.perf_counter() - started) * 1000.0
            if actual != expected:
                ok = False
            results.append(
                {
                    "name": name,
                    "fen": fen,
                    "depth": depth,
                    "expected": expected,
                    "actual": actual,
                    "correct": actual == expected,
                    "elapsed_ms": elapsed_ms,
                    "nodes_per_second": actual / (elapsed_ms / 1000.0) if elapsed_ms else None,
                }
            )
    return {"ok": ok, "mode": "perft", "total": len(results), "passed": sum(1 for item in results if item["correct"]), "positions": results}


def score_board(
    board: chess.Board,
    expected_uci: set[str],
    args: argparse.Namespace,
    *,
    avoid_uci: set[str] | None = None,
) -> dict[str, Any]:
    started = time.perf_counter()
    decision = DialecticalChessEngine(
        EngineSettings(
            dialectic_depth=args.dialectic_depth,
            search_depth=args.search_depth,
            search_backend=args.search_backend,
            smt_mate=args.smt_mate,
            selector_mode=args.selector_mode,
        )
    ).choose_move(board)
    selected = decision.selected
    elapsed_ms = (time.perf_counter() - started) * 1000.0
    selected_uci = None if selected is None else decision.move_uci
    avoid_uci = avoid_uci or set()
    return {
        "expected_uci": sorted(expected_uci),
        "avoid_uci": sorted(avoid_uci),
        "selected_uci": selected_uci,
        "selected_san": None if selected is None else selected.san,
        "correct": selected_uci in expected_uci if expected_uci else selected_uci not in avoid_uci,
        "avoided": selected_uci not in avoid_uci,
        "score": None if selected is None else selected.score,
        "reasons": [] if selected is None else list(selected.reasons),
        "objections": [] if selected is None else list(selected.objections),
        "reply_attacks": [] if selected is None else list(selected.reply_attacks),
        "search_score": None if selected is None else selected.search_score,
        "search_line": [] if selected is None else list(selected.search_line),
        "smt_witnesses": [] if selected is None else list(selected.smt_witnesses),
        "elapsed_ms": elapsed_ms,
    }


def score_full_line(board: chess.Board, moves: list[str], args: argparse.Namespace) -> bool:
    working = board.copy(stack=False)
    for index, move_text in enumerate(moves):
        expected = chess.Move.from_uci(move_text)
        if index % 2 == 0:
            result = score_board(working, {move_text}, args)
            if not result["correct"]:
                return False
        if expected not in working.legal_moves:
            return False
        working.push(expected)
    return True


def include_puzzle(row: dict[str, str], args: argparse.Namespace) -> bool:
    rating = int(row.get("Rating") or 0)
    if args.rating_min is not None and rating < args.rating_min:
        return False
    if args.rating_max is not None and rating > args.rating_max:
        return False
    themes = set(row.get("Themes", "").split())
    if args.theme_include and not all(theme in themes for theme in args.theme_include):
        return False
    if args.theme_exclude and any(theme in themes for theme in args.theme_exclude):
        return False
    if args.side_to_move and chess.Board(row["FEN"]).turn != (args.side_to_move == "w"):
        return False
    return True


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
    am_match = AM_RE.search(operations)
    expected = set()
    avoid = set()
    if bm_match is not None:
        expected = {parse_expected_move(board, token).uci() for token in bm_match.group(1).split()}
    if am_match is not None:
        avoid = {parse_expected_move(board, token).uci() for token in am_match.group(1).split()}
    if not expected and not avoid:
        raise ValueError(f"EPD line {index} has no bm or am operation")
    id_match = ID_RE.search(operations)
    return {
        "id": id_match.group(1) if id_match else f"position-{index}",
        "board": board,
        "expected_uci": expected,
        "avoid_uci": avoid,
    }


def parse_expected_move(board: chess.Board, token: str) -> chess.Move:
    try:
        move = chess.Move.from_uci(token)
    except ValueError:
        move = chess.Move.null()
    if move in board.legal_moves:
        return move
    return board.parse_san(token)


def rating_bucket(rating: int) -> str:
    low = (rating // 200) * 200
    return f"{low}-{low + 199}"


def ablation_selector_modes(args: argparse.Namespace) -> tuple[str, ...]:
    if args.selector_mode_ablation:
        return tuple(sorted(SELECTOR_MODES))
    return (args.selector_mode,)


def settings(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "dialectic_depth": args.dialectic_depth,
        "search_depth": args.search_depth,
        "search_backend": args.search_backend,
        "smt_mate": args.smt_mate,
        "selector_mode": args.selector_mode,
        "movegen": "owned",
    }
