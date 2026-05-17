"""UCI protocol loop for the dialectical chess probe engine."""

from __future__ import annotations

from typing import TextIO

from dialectical_chess.board import START_FEN
from dialectical_chess.engine import DialecticalChessEngine, EngineSettings
from dialectical_chess.probe import owned_board_from_fen
from dialectical_chess.search import ReplyAnalysisSettings


UciSettings = EngineSettings


def run_uci(
    input_stream: TextIO,
    output_stream: TextIO,
    *,
    dialectic_depth: int = 1,
    search_depth: int = 0,
    search_backend: str = "negamax",
    smt_mate: bool = True,
    smt_fork: bool = True,
    selector_mode: str = "argument",
    positional_reasons: bool = True,
    reply_analysis: ReplyAnalysisSettings | None = None,
) -> int:
    settings = EngineSettings(
        dialectic_depth=dialectic_depth,
        search_depth=search_depth,
        search_backend=search_backend,
        smt_mate=smt_mate,
        smt_fork=smt_fork,
        selector_mode=selector_mode,
        positional_reasons=positional_reasons,
        reply_analysis=reply_analysis or ReplyAnalysisSettings(),
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
    smt_fork: bool = True,
    selector_mode: str = "argument",
    positional_reasons: bool = True,
    reply_analysis: ReplyAnalysisSettings | None = None,
    output_stream: TextIO | None = None,
) -> str:
    settings = settings or EngineSettings(
        dialectic_depth=dialectic_depth,
        search_depth=search_depth,
        search_backend=search_backend,
        smt_mate=smt_mate,
        smt_fork=smt_fork,
        selector_mode=selector_mode,
        positional_reasons=positional_reasons,
        reply_analysis=reply_analysis or ReplyAnalysisSettings(),
    )
    try:
        decision = DialecticalChessEngine(settings).choose_move(board)
    except ValueError as exc:
        if output_stream is not None:
            _uci_write(output_stream, f"info string {exc}")
        return "0000"
    if decision.selected is None:
        return "0000"
    if output_stream is not None:
        _uci_write(output_stream, f"info string selector_mode={settings.selector_mode}")
        _uci_write(output_stream, f"info string positional_reasons={settings.positional_reasons}")
        _uci_write(output_stream, f"info string reply_analysis={settings.reply_analysis}")
        if decision.selected.optimizer_trace:
            _uci_write(
                output_stream,
                f"info string optimizer_status={decision.selected.optimizer_trace.get('status')}",
            )
        _uci_write(output_stream, f"info score cp {decision.selected.score} pv {decision.move_uci}")
    return decision.move_uci


def _uci_write(output_stream: TextIO, line: str) -> None:
    print(line, file=output_stream, flush=True)
