"""UCI match orchestration for dialectical chess benchmarks."""

from __future__ import annotations

import re
import shutil
import subprocess
from argparse import Namespace
from collections import Counter
from pathlib import Path
from typing import Any

import chess

from dialectical_chess.baselines import fastchess_baseline


SCRIPT_DIR = Path(__file__).resolve().parents[1]
ROOT = SCRIPT_DIR.parent
PROBE_PATH = SCRIPT_DIR / "dialectical_chess_probe.py"


def run_uci_match(args: Namespace) -> dict[str, Any]:
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
    baseline_name, baseline_args = fastchess_baseline(args.match_baseline, uv_executable, args)
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
    if cutechess and args.match_baseline == "nosmt":
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


def parse_uci_match_failures(stdout: str) -> dict[str, int]:
    timeouts = sum(int(match.group(1)) for match in re.finditer(r"\bTimeouts:\s+(\d+)", stdout))
    crashes = sum(int(match.group(1)) for match in re.finditer(r"\bCrashed:\s+(\d+)", stdout))
    losses_on_time = len(re.findall(r"\bloses on time\b", stdout, flags=re.IGNORECASE))
    return {
        "timeouts": timeouts,
        "crashes": crashes,
        "losses_on_time": losses_on_time,
    }


def run_internal_uci_match(args: Namespace) -> dict[str, Any]:
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
