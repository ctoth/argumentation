# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "chess>=1.11.0",
#   "z3-solver>=4.12",
# ]
# ///
"""Benchmark runner for the dialectical chess scripts."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import chess


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
PROBE_PATH = SCRIPT_DIR / "dialectical_chess_probe.py"
OWNED_PATH = SCRIPT_DIR / "dialectical_chess_owned.py"
RANDOM_BASELINE_PATH = SCRIPT_DIR / "dialectical_chess_random_uci.py"
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
    parser.add_argument("--no-smt-mate", action="store_false", dest="smt_mate")
    parser.add_argument("--uci-match-command", action="store_true")
    parser.add_argument("--run-uci-match", action="store_true")
    parser.add_argument("--internal-uci-match", action="store_true")
    parser.add_argument("--match-baseline", choices=("nosmt", "random"), default="nosmt")
    parser.add_argument("--match-openings", type=Path, default=OPENINGS_PATH)
    parser.add_argument("--match-games", type=int, default=2)
    parser.add_argument("--match-max-plies", type=int, default=40)
    parser.add_argument("--match-tc", default="1+0.01")
    parser.set_defaults(smt_mate=True)
    args = parser.parse_args()

    started = time.perf_counter()
    if args.perft:
        payload = run_perft()
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


def run_epd(args: argparse.Namespace) -> dict[str, Any]:
    probe = load_module("dialectical_chess_probe", PROBE_PATH)
    lines = read_epd_lines(args.epd)
    if args.limit is not None:
        lines = lines[: args.limit]
    results = []
    for index, line in enumerate(lines, start=1):
        try:
            case = parse_epd_case(line, index=index)
            result = score_board(
                probe,
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
    return {
        "ok": all("error" not in result for result in results),
        "mode": "epd",
        "suite": str(args.epd) if args.epd else "built-in-smoke",
        "total": len(results),
        "solved": solved,
        "hit_rate": solved / len(results) if results else 0.0,
        "settings": settings(args),
        "positions": results,
    }


def run_ablation(args: argparse.Namespace) -> dict[str, Any]:
    base_epd = args.epd
    runs = []
    for smt_mate in (True, False):
        for dialectic_depth in (0, 1, 2):
            for search_depth in (0, 1, 2, 3):
                for backend in ("negamax", "alphabeta"):
                    case_args = argparse.Namespace(**vars(args))
                    case_args.epd = base_epd
                    case_args.smt_mate = smt_mate
                    case_args.dialectic_depth = dialectic_depth
                    case_args.search_depth = search_depth
                    case_args.search_backend = backend
                    started = time.perf_counter()
                    payload = run_epd(case_args)
                    runs.append(
                        {
                            "settings": settings(case_args),
                            "total": payload["total"],
                            "solved": payload["solved"],
                            "hit_rate": payload["hit_rate"],
                            "elapsed_ms": (time.perf_counter() - started) * 1000.0,
                        }
                    )
    return {"ok": True, "mode": "ablation", "suite": str(base_epd) if base_epd else "built-in-smoke", "runs": runs}


def run_lichess(args: argparse.Namespace) -> dict[str, Any]:
    probe = load_module("dialectical_chess_probe", PROBE_PATH)
    rows = []
    with args.lichess_puzzles.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if include_puzzle(row, args):
                rows.append(row)
            if args.limit is not None and len(rows) >= args.limit:
                break
    results = []
    by_rating: Counter[str] = Counter()
    by_theme: Counter[str] = Counter()
    theme_totals: Counter[str] = Counter()
    for row in rows:
        board = chess.Board(row["FEN"])
        moves = row["Moves"].split()
        expected = {moves[0]} if moves else set()
        result = score_board(probe, board, expected, args)
        result["id"] = row.get("PuzzleId", "")
        result["rating"] = int(row.get("Rating") or 0)
        result["themes"] = row.get("Themes", "").split()
        if args.full_line and result["correct"]:
            result["full_line_correct"] = score_full_line(probe, board, moves, args)
        bucket = rating_bucket(result["rating"])
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
        "by_rating_bucket": dict(sorted(by_rating.items())),
        "by_theme": {
            theme: {"solved": by_theme[theme], "total": theme_totals[theme]}
            for theme in sorted(theme_totals)
        },
        "settings": settings(args),
        "positions": results,
    }


def run_perft() -> dict[str, Any]:
    owned = load_module("dialectical_chess_owned", OWNED_PATH)
    results = []
    ok = True
    for name, (fen, depths) in owned.PERFT_FIXTURES.items():
        board = owned.OwnedBoard.from_fen(fen)
        for depth, expected in depths.items():
            started = time.perf_counter()
            actual = owned.owned_perft(board, depth)
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


def run_uci_match(args: argparse.Namespace) -> dict[str, Any]:
    cutechess = shutil.which("cutechess-cli")
    fastchess = shutil.which("fastchess") or shutil.which("fast-chess")
    uv_executable = shutil.which("uv") or "uv"
    cutechess_args = [
        "-engine",
        'name=Dialectical cmd="uv" arg="run" arg=".\\scripts\\dialectical_chess_probe.py" arg="--uci" proto=uci',
        "-engine",
        'name=DialecticalNoSMT cmd="uv" arg="run" arg=".\\scripts\\dialectical_chess_probe.py" arg="--uci" arg="--no-smt-mate" proto=uci',
        "-each",
        f"tc={args.match_tc}",
        "-games",
        str(args.match_games),
        "-repeat",
    ]
    baseline_name, baseline_args = fastchess_baseline(args.match_baseline, uv_executable)
    games_per_round = 2 if args.match_games > 1 else 1
    rounds = max(1, (args.match_games + games_per_round - 1) // games_per_round)
    fastchess_args = [
        "-engine",
        "name=Dialectical",
        f"cmd={uv_executable}",
        "args=run .\\scripts\\dialectical_chess_probe.py --uci",
        "proto=uci",
        f"dir={ROOT}",
        "-engine",
        f"name={baseline_name}",
        *baseline_args,
        "-each",
        f"tc={args.match_tc}",
        "-rounds",
        str(rounds),
        "-games",
        str(games_per_round),
        "-openings",
        f"file={args.match_openings}",
        "format=epd",
        "order=sequential",
        "-maxmoves",
        str(max(1, args.match_max_plies // 2)),
        "-concurrency",
        "1",
    ]
    if cutechess:
        command = [cutechess, *cutechess_args]
        runner = "cutechess-cli"
    elif fastchess:
        command = [fastchess, *fastchess_args]
        runner = "fastchess"
    else:
        return {
            "ok": False,
            "mode": "uci_match",
            "blocked": "missing cutechess-cli, fastchess, or fast-chess executable on PATH",
            "suggested_command": "fast-chess " + " ".join(fastchess_args),
        }
    if not args.run_uci_match:
        return {
            "ok": True,
            "mode": "uci_match",
            "runner": runner,
            "baseline": args.match_baseline,
            "requested_games": args.match_games,
            "command": command,
        }
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    failures = parse_uci_match_failures(completed.stdout)
    return {
        "ok": completed.returncode == 0 and not any(failures.values()),
        "mode": "uci_match",
        "runner": runner,
        "baseline": args.match_baseline,
        "requested_games": args.match_games,
        "command": command,
        "returncode": completed.returncode,
        "failures": failures,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def fastchess_baseline(baseline: str, uv_executable: str) -> tuple[str, list[str]]:
    if baseline == "nosmt":
        return (
            "DialecticalNoSMT",
            [
                f"cmd={uv_executable}",
                "args=run .\\scripts\\dialectical_chess_probe.py --uci --no-smt-mate",
                "proto=uci",
                f"dir={ROOT}",
            ],
        )
    if baseline == "random":
        return (
            "DialecticalRandom",
            [
                f"cmd={uv_executable}",
                "args=run .\\scripts\\dialectical_chess_random_uci.py",
                "proto=uci",
                f"dir={ROOT}",
            ],
        )
    raise ValueError(f"unknown match baseline: {baseline}")


def parse_uci_match_failures(stdout: str) -> dict[str, int]:
    timeouts = sum(int(match.group(1)) for match in re.finditer(r"\bTimeouts:\s+(\d+)", stdout))
    crashes = sum(int(match.group(1)) for match in re.finditer(r"\bCrashed:\s+(\d+)", stdout))
    losses_on_time = len(re.findall(r"\bloses on time\b", stdout, flags=re.IGNORECASE))
    return {
        "timeouts": timeouts,
        "crashes": crashes,
        "losses_on_time": losses_on_time,
    }


def run_internal_uci_match(args: argparse.Namespace) -> dict[str, Any]:
    games = []
    crashes = 0
    illegal_moves = 0
    for game_index in range(args.match_games):
        white_args = [] if game_index % 2 == 0 else ["--no-smt-mate"]
        black_args = ["--no-smt-mate"] if game_index % 2 == 0 else []
        result = play_internal_uci_game(white_args, black_args, args.match_max_plies)
        crashes += result["crashes"]
        illegal_moves += result["illegal_moves"]
        games.append(result)
    wdl = Counter(game["result"] for game in games)
    return {
        "ok": crashes == 0 and illegal_moves == 0,
        "mode": "internal_uci_match",
        "games": len(games),
        "max_plies": args.match_max_plies,
        "wdl": dict(sorted(wdl.items())),
        "crashes": crashes,
        "illegal_moves": illegal_moves,
        "results": games,
    }


def play_internal_uci_game(
    white_extra_args: list[str],
    black_extra_args: list[str],
    max_plies: int,
) -> dict[str, Any]:
    white = start_uci_engine(white_extra_args)
    black = start_uci_engine(black_extra_args)
    board = chess.Board()
    moves: list[str] = []
    crashes = 0
    illegal_moves = 0
    try:
        initialize_uci(white)
        initialize_uci(black)
        for _ply in range(max_plies):
            if board.is_game_over(claim_draw=True):
                break
            engine = white if board.turn == chess.WHITE else black
            send_uci(engine, "position startpos" + ("" if not moves else " moves " + " ".join(moves)))
            send_uci(engine, "go")
            bestmove = read_bestmove(engine)
            if bestmove == "0000":
                break
            move = chess.Move.from_uci(bestmove)
            if move not in board.legal_moves:
                illegal_moves += 1
                break
            board.push(move)
            moves.append(bestmove)
        result = board.result(claim_draw=True) if board.is_game_over(claim_draw=True) else "1/2-1/2"
    except Exception:
        crashes += 1
        result = "*"
    finally:
        stop_uci_engine(white)
        stop_uci_engine(black)
    return {
        "result": result,
        "plies": len(moves),
        "moves": moves,
        "final_fen": board.fen(),
        "crashes": crashes,
        "illegal_moves": illegal_moves,
    }


def start_uci_engine(extra_args: list[str]) -> subprocess.Popen[str]:
    return subprocess.Popen(
        ["uv", "run", str(PROBE_PATH), "--uci", *extra_args],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def initialize_uci(process: subprocess.Popen[str]) -> None:
    send_uci(process, "uci")
    read_until(process, "uciok")
    send_uci(process, "isready")
    read_until(process, "readyok")
    send_uci(process, "ucinewgame")


def send_uci(process: subprocess.Popen[str], command: str) -> None:
    if process.stdin is None:
        raise RuntimeError("UCI process has no stdin")
    process.stdin.write(command + "\n")
    process.stdin.flush()


def read_until(process: subprocess.Popen[str], needle: str) -> list[str]:
    lines = []
    if process.stdout is None:
        raise RuntimeError("UCI process has no stdout")
    while True:
        line = process.stdout.readline()
        if line == "":
            raise RuntimeError("UCI process exited")
        line = line.strip()
        lines.append(line)
        if line == needle:
            return lines


def read_bestmove(process: subprocess.Popen[str]) -> str:
    if process.stdout is None:
        raise RuntimeError("UCI process has no stdout")
    while True:
        line = process.stdout.readline()
        if line == "":
            raise RuntimeError("UCI process exited")
        line = line.strip()
        if line.startswith("bestmove "):
            return line.split()[1]


def stop_uci_engine(process: subprocess.Popen[str]) -> None:
    try:
        send_uci(process, "quit")
    except Exception:
        pass
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


def score_board(
    probe: Any,
    board: chess.Board,
    expected_uci: set[str],
    args: argparse.Namespace,
    *,
    avoid_uci: set[str] | None = None,
) -> dict[str, Any]:
    started = time.perf_counter()
    probes = probe.probe_moves(
        board,
        dialectic_depth=args.dialectic_depth,
        search_depth=args.search_depth,
        search_backend=args.search_backend,
        smt_mate=args.smt_mate,
    )
    selected = probe.choose_move(probes, probe.build_root_argument_graph(probes)) if probes else None
    elapsed_ms = (time.perf_counter() - started) * 1000.0
    selected_uci = None if selected is None else selected.uci
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


def score_full_line(probe: Any, board: chess.Board, moves: list[str], args: argparse.Namespace) -> bool:
    working = board.copy(stack=False)
    for index, move_text in enumerate(moves):
        expected = chess.Move.from_uci(move_text)
        if index % 2 == 0:
            result = score_board(probe, working, {move_text}, args)
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


def settings(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "dialectic_depth": args.dialectic_depth,
        "search_depth": args.search_depth,
        "search_backend": args.search_backend,
        "smt_mate": args.smt_mate,
        "movegen": "owned",
    }


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


if __name__ == "__main__":
    raise SystemExit(main())
