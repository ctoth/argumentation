# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "chess>=1.11.0",
# ]
# ///
"""Deterministic weak UCI baseline for dialectical chess evaluation."""

from __future__ import annotations

import hashlib
import sys
from typing import TextIO

import chess


def main() -> int:
    return run_uci(sys.stdin, sys.stdout)


def run_uci(input_stream: TextIO, output_stream: TextIO) -> int:
    board = chess.Board()
    while True:
        raw = input_stream.readline()
        if raw == "":
            return 0
        command = raw.strip()
        if not command:
            continue
        if command == "uci":
            write(output_stream, "id name DialecticalRandomBaseline")
            write(output_stream, "id author argumentation")
            write(output_stream, "uciok")
        elif command == "isready":
            write(output_stream, "readyok")
        elif command == "ucinewgame":
            board = chess.Board()
        elif command.startswith("position "):
            try:
                board = parse_position(command)
            except ValueError as exc:
                write(output_stream, f"info string invalid position: {exc}")
        elif command.startswith("go") or command == "stop":
            write(output_stream, f"bestmove {choose_move(board)}")
        elif command == "quit":
            return 0
        elif command.startswith("setoption ") or command == "ponderhit":
            continue
        else:
            write(output_stream, f"info string unsupported command: {command}")


def parse_position(command: str) -> chess.Board:
    tokens = command.split()
    if len(tokens) < 2 or tokens[0] != "position":
        raise ValueError(command)
    index = 1
    if tokens[index] == "startpos":
        board = chess.Board()
        index += 1
    elif tokens[index] == "fen":
        index += 1
        fen_start = index
        while index < len(tokens) and tokens[index] != "moves":
            index += 1
        fen_fields = tokens[fen_start:index]
        if len(fen_fields) != 6:
            raise ValueError("fen position must contain six FEN fields")
        board = chess.Board(" ".join(fen_fields))
    else:
        raise ValueError("position must use startpos or fen")
    if index < len(tokens):
        if tokens[index] != "moves":
            raise ValueError(f"unexpected token: {tokens[index]}")
        for move_text in tokens[index + 1 :]:
            move = chess.Move.from_uci(move_text)
            if move not in board.legal_moves:
                raise ValueError(f"illegal move {move_text}")
            board.push(move)
    return board


def choose_move(board: chess.Board) -> str:
    moves = sorted(board.legal_moves, key=lambda move: move.uci())
    if not moves:
        return "0000"
    digest = hashlib.blake2b(board.fen().encode("utf-8"), digest_size=8).digest()
    index = int.from_bytes(digest, "big") % len(moves)
    return moves[index].uci()


def write(output_stream: TextIO, line: str) -> None:
    print(line, file=output_stream, flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
