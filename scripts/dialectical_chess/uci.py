"""UCI protocol loop for the dialectical chess probe engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TextIO

from dialectical_chess.arguments import build_root_argument_graph, choose_move
from dialectical_chess.board import START_FEN
from dialectical_chess.probe import owned_board_from_fen, probe_moves


@dataclass(frozen=True)
class UciSettings:
    dialectic_depth: int = 1
    search_depth: int = 0
    search_backend: str = "negamax"
    smt_mate: bool = True


def run_uci(
    input_stream: TextIO,
    output_stream: TextIO,
    *,
    dialectic_depth: int = 1,
    search_depth: int = 0,
    search_backend: str = "negamax",
    smt_mate: bool = True,
) -> int:
    settings = UciSettings(
        dialectic_depth=dialectic_depth,
        search_depth=search_depth,
        search_backend=search_backend,
        smt_mate=smt_mate,
    )
    board = owned_board_from_fen(START_FEN)
    while True:
        raw = input_stream.readline()
        if raw == "":
            return 0
        command = raw.strip()
        if not command:
            continue

        if command == "uci":
            _uci_write(output_stream, "id name DialecticalChessProbe")
            _uci_write(output_stream, "id author argumentation")
            _uci_write(output_stream, "uciok")
        elif command == "isready":
            _uci_write(output_stream, "readyok")
        elif command == "ucinewgame":
            board = owned_board_from_fen(START_FEN)
        elif command.startswith("position "):
            try:
                board = parse_uci_position(command)
            except ValueError as exc:
                _uci_write(output_stream, f"info string invalid position: {exc}")
        elif command.startswith("go") or command == "stop":
            _uci_write(
                output_stream,
                "bestmove " + choose_uci_move(board, settings=settings, output_stream=output_stream),
            )
        elif command == "quit":
            return 0
        elif command.startswith("setoption ") or command == "ponderhit":
            continue
        else:
            _uci_write(output_stream, f"info string unsupported command: {command}")


def parse_uci_position(command: str):
    tokens = command.split()
    if len(tokens) < 2 or tokens[0] != "position":
        raise ValueError(command)

    index = 1
    if tokens[index] == "startpos":
        board = owned_board_from_fen(START_FEN)
        index += 1
    elif tokens[index] == "fen":
        index += 1
        fen_start = index
        while index < len(tokens) and tokens[index] != "moves":
            index += 1
        fen_fields = tokens[fen_start:index]
        if len(fen_fields) != 6:
            raise ValueError("fen position must contain six FEN fields")
        board = owned_board_from_fen(" ".join(fen_fields))
    else:
        raise ValueError("position must use startpos or fen")

    if index < len(tokens):
        if tokens[index] != "moves":
            raise ValueError(f"unexpected token: {tokens[index]}")
        legal_by_uci = {move.uci(): move for move in board.legal_moves()}
        for move_text in tokens[index + 1 :]:
            move = legal_by_uci.get(move_text)
            if move is None:
                raise ValueError(f"illegal move {move_text}")
            board = board.apply(move)
            legal_by_uci = {next_move.uci(): next_move for next_move in board.legal_moves()}
    return board


def choose_uci_move(
    board,
    *,
    settings: UciSettings | None = None,
    dialectic_depth: int = 1,
    search_depth: int = 0,
    search_backend: str = "negamax",
    smt_mate: bool = True,
    output_stream: TextIO | None = None,
) -> str:
    settings = settings or UciSettings(
        dialectic_depth=dialectic_depth,
        search_depth=search_depth,
        search_backend=search_backend,
        smt_mate=smt_mate,
    )
    try:
        probes = probe_moves(
            board,
            dialectic_depth=settings.dialectic_depth,
            search_depth=settings.search_depth,
            search_backend=settings.search_backend,
            smt_mate=settings.smt_mate,
        )
    except ValueError as exc:
        if output_stream is not None:
            _uci_write(output_stream, f"info string {exc}")
        return "0000"
    if not probes:
        return "0000"
    selected = choose_move(probes, build_root_argument_graph(probes))
    if output_stream is not None:
        _uci_write(output_stream, f"info score cp {selected.score} pv {selected.uci}")
    return selected.uci


def _uci_write(output_stream: TextIO, line: str) -> None:
    print(line, file=output_stream, flush=True)
