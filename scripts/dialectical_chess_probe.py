# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "chess>=1.11.0",
#   "z3-solver>=4.12",
# ]
# ///
"""Sidecar probe for dialectical chess experiments.

This is intentionally outside the package source tree. It uses PEP 723 inline
metadata so `uv run scripts/dialectical_chess_probe.py ...` can fetch only the
prototype dependencies needed by this script.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, TextIO

import chess
import chess.pgn
import chess.svg


DEFAULT_FEN = "7k/6pp/8/8/8/8/6PP/R5K1 w - - 0 1"
START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
PIECE_VALUE = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0,
}
OWNED_PIECE_VALUE = {"p": 100, "n": 320, "b": 330, "r": 500, "q": 900, "k": 0}


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
    reply_attacks: tuple[str, ...] = ()
    search_score: int | None = None
    search_line: tuple[str, ...] = ()
    smt_witnesses: tuple[str, ...] = ()


@dataclass(frozen=True)
class RootArgumentGraph:
    arguments: frozenset[str]
    defeats: frozenset[tuple[str, str]]
    move_arguments: dict[str, str]
    grounded_extension: frozenset[str]
    ranking: dict[str, Any]


@dataclass(frozen=True)
class SearchResult:
    score: int
    line: tuple[str, ...]


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
    parser.add_argument("--owned-movegen", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--allow-owned-divergence", action="store_true", help=argparse.SUPPRESS)
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
    probes = probe_moves(
        board,
        dialectic_depth=args.dialectic_depth,
        search_depth=args.search_depth,
        search_backend=args.search_backend,
        smt_mate=args.smt_mate,
    )
    graph = build_root_argument_graph(probes)
    selected = choose_move(probes, graph)

    if args.svg:
        svg = chess.svg.board(board=notation_board, size=args.size)
        args.svg.parent.mkdir(parents=True, exist_ok=True)
        args.svg.write_text(svg, encoding="utf-8")

    pgn_path = args.pgn_out or args.pgn
    if pgn_path:
        pgn_path.parent.mkdir(parents=True, exist_ok=True)
        pgn_path.write_text(build_pgn(notation_board, selected, game=game), encoding="utf-8")

    if args.list_legal:
        for probe in probes:
            print(f"{probe.uci:5} {probe.san:8} score={probe.score:6} {', '.join(probe.reasons)}")

    if args.emit_af:
        af_payload = build_argument_payload(probes, graph)
        args.emit_af.parent.mkdir(parents=True, exist_ok=True)
        args.emit_af.write_text(json.dumps(af_payload, indent=2), encoding="utf-8")

    if args.choose:
        print(json.dumps(asdict(selected), indent=2))

    if not any([args.svg, pgn_path, args.list_legal, args.emit_af, args.choose]):
        print(f"fen: {board.fen()}")
        print(f"bestmove: {selected.uci} ({selected.san})")
        print(f"reasons: {', '.join(selected.reasons)}")

    return 0


def run_uci(
    input_stream: TextIO,
    output_stream: TextIO,
    *,
    dialectic_depth: int = 1,
    search_depth: int = 0,
    search_backend: str = "negamax",
    smt_mate: bool = True,
) -> int:
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
        elif command.startswith("go"):
            _uci_write(
                output_stream,
                "bestmove "
                + choose_uci_move(
                    board,
                    dialectic_depth=dialectic_depth,
                    search_depth=search_depth,
                    search_backend=search_backend,
                    smt_mate=smt_mate,
                    output_stream=output_stream,
                ),
            )
        elif command == "stop":
            _uci_write(
                output_stream,
                "bestmove "
                + choose_uci_move(
                    board,
                    dialectic_depth=dialectic_depth,
                    search_depth=search_depth,
                    search_backend=search_backend,
                    smt_mate=smt_mate,
                    output_stream=output_stream,
                ),
            )
        elif command == "quit":
            return 0
        elif command.startswith("setoption ") or command == "ponderhit":
            continue
        else:
            _uci_write(output_stream, f"info string unsupported command: {command}")


def _uci_write(output_stream: TextIO, line: str) -> None:
    print(line, file=output_stream, flush=True)


def parse_uci_position(command: str) -> Any:
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
    board: Any,
    *,
    dialectic_depth: int = 1,
    search_depth: int = 0,
    search_backend: str = "negamax",
    smt_mate: bool = True,
    output_stream: TextIO | None = None,
) -> str:
    try:
        probes = probe_moves(
            board,
            dialectic_depth=dialectic_depth,
            search_depth=search_depth,
            search_backend=search_backend,
            smt_mate=smt_mate,
        )
    except ValueError as exc:
        if output_stream is not None:
            _uci_write(output_stream, f"info string {exc}")
        return "0000"
    if not probes:
        return "0000"
    return choose_move(probes, build_root_argument_graph(probes)).uci


def probe_moves(
    board: Any,
    *,
    dialectic_depth: int = 1,
    search_depth: int = 0,
    search_backend: str = "negamax",
    smt_mate: bool = True,
) -> list[MoveProbe]:
    if dialectic_depth < 0:
        raise ValueError("dialectic_depth must be non-negative")
    if search_depth < 0:
        raise ValueError("search_depth must be non-negative")
    board = ensure_owned_board(board)
    legal_moves = sorted(board.legal_moves(), key=lambda move: move.uci())
    smt_mate_moves = smt_mate_in_one_moves(board) if smt_mate else frozenset()
    probes = []
    for move in legal_moves:
        san = move.uci()
        is_capture = owned_is_capture(board, move)
        captured_value = owned_capture_value(board, move)
        promotion_value = OWNED_PIECE_VALUE.get(move.promotion or "", 0)
        child = board.apply(move)
        is_checkmate = owned_is_checkmate(child)
        gives_check = child.in_check(child.turn)

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
        smt_witnesses: list[str] = []
        if move.uci() in smt_mate_moves:
            score += 1_000_000
            reasons.append("smt:mate_in_one")
            smt_witnesses.append("mate_in_one")
        search_result = root_search_result(
            board,
            move,
            depth=search_depth,
            backend=search_backend,
        )
        if search_result is not None:
            if search_result.score > 0:
                reasons.append(f"search:{search_backend}:{search_result.score}")
            elif search_result.score < 0:
                objections.append(f"search:{search_backend}:{search_result.score}")
            score += search_result.score
        reply_attacks = bounded_reply_attacks(
            board,
            move,
            reply_depth=dialectic_depth,
        )
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
                reply_attacks=reply_attacks,
                search_score=None if search_result is None else search_result.score,
                search_line=() if search_result is None else search_result.line,
                smt_witnesses=tuple(smt_witnesses),
            )
        )
    return sorted(probes, key=lambda probe: (-probe.score, probe.uci))


def load_owned_module() -> Any:
    path = Path(__file__).resolve().with_name("dialectical_chess_owned.py")
    spec = importlib.util.spec_from_file_location("dialectical_chess_owned", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def ensure_owned_board(board: Any) -> Any:
    if hasattr(board, "legal_moves") and callable(board.legal_moves):
        return board
    return owned_board_from_fen(board.fen())


def owned_board_from_fen(fen: str) -> Any:
    return load_owned_module().OwnedBoard.from_fen(fen)


def smt_mate_in_one_moves(board: Any) -> frozenset[str]:
    try:
        from z3 import Bool, Or, Solver, sat
    except ImportError:
        return frozenset()

    mate_moves: dict[str, Any] = {}
    board = ensure_owned_board(board)
    for move in board.legal_moves():
        if owned_is_checkmate(board.apply(move)):
            mate_moves[move.uci()] = Bool(f"mate_{move.uci()}")

    if not mate_moves:
        return frozenset()

    solver = Solver()
    solver.add(Or(*mate_moves.values()))
    if solver.check() != sat:
        return frozenset()
    model = solver.model()
    witnesses = {
        move
        for move, variable in mate_moves.items()
        if model.eval(variable, model_completion=True)
    }
    return frozenset(move for move in witnesses if verifies_mate_in_one(board, move))


def verifies_mate_in_one(board: Any, move_text: str) -> bool:
    board = ensure_owned_board(board)
    legal_by_uci = {move.uci(): move for move in board.legal_moves()}
    move = legal_by_uci.get(move_text)
    return move is not None and owned_is_checkmate(board.apply(move))


def root_search_result(
    board: Any,
    move: Any,
    *,
    depth: int,
    backend: str,
) -> SearchResult | None:
    if depth <= 0:
        return None
    child_board = board.apply(move)
    if backend == "negamax":
        child = negamax(child_board, depth - 1)
    elif backend == "alphabeta":
        child = alphabeta(child_board, depth - 1, alpha=-1_000_000, beta=1_000_000)
    else:
        raise ValueError(f"unsupported search backend: {backend}")
    return SearchResult(score=-child.score, line=(move.uci(),) + child.line)


def negamax(board: Any, depth: int) -> SearchResult:
    if owned_is_checkmate(board):
        return SearchResult(score=-100_000 - depth, line=())
    if owned_is_stalemate(board):
        return SearchResult(score=0, line=())
    if depth <= 0:
        return SearchResult(score=static_evaluation(board), line=())

    best: SearchResult | None = None
    best_move: Any | None = None
    for move in board.legal_moves():
        child = negamax(board.apply(move), depth - 1)
        candidate = SearchResult(score=-child.score, line=(move.uci(),) + child.line)
        if (
            best is None
            or candidate.score > best.score
            or (candidate.score == best.score and move.uci() < best_move.uci())
        ):
            best = candidate
            best_move = move

    if best is None:
        return SearchResult(score=static_evaluation(board), line=())
    return best


def alphabeta(
    board: Any,
    depth: int,
    *,
    alpha: int,
    beta: int,
) -> SearchResult:
    if owned_is_checkmate(board):
        return SearchResult(score=-100_000 - depth, line=())
    if owned_is_stalemate(board):
        return SearchResult(score=0, line=())
    if depth <= 0:
        return SearchResult(score=static_evaluation(board), line=())

    best: SearchResult | None = None
    best_move: Any | None = None
    for move in board.legal_moves():
        child = alphabeta(board.apply(move), depth - 1, alpha=-beta, beta=-alpha)
        candidate = SearchResult(score=-child.score, line=(move.uci(),) + child.line)
        if (
            best is None
            or candidate.score > best.score
            or (candidate.score == best.score and move.uci() < best_move.uci())
        ):
            best = candidate
            best_move = move
        alpha = max(alpha, candidate.score)
        if alpha >= beta:
            break

    if best is None:
        return SearchResult(score=static_evaluation(board), line=())
    return best


def static_evaluation(board: Any) -> int:
    white = 0
    black = 0
    for piece in board.squares:
        if piece is None:
            continue
        value = OWNED_PIECE_VALUE[piece.lower()]
        if piece.isupper():
            white += value
        else:
            black += value
    material = white - black
    return material if board.turn == "w" else -material


def bounded_reply_attacks(
    board: Any,
    move: Any,
    *,
    reply_depth: int,
) -> tuple[str, ...]:
    if reply_depth <= 0:
        return ()
    moved_piece = board.piece_at(move.from_square)
    moved_piece_value = OWNED_PIECE_VALUE.get(moved_piece.lower(), 0) if moved_piece else 0
    moved_to = move.to_square
    attacks: list[str] = []

    child = board.apply(move)
    if not owned_is_terminal(child):
        for reply in child.legal_moves():
            reply_text = reply.uci()
            reply_captures_moved_piece = (
                owned_is_capture(child, reply)
                and reply.to_square == moved_to
                and moved_piece_value > 0
            )
            reply_child = child.apply(reply)
            reply_piece = reply_child.piece_at(reply.to_square)
            reply_piece_value = (
                OWNED_PIECE_VALUE.get(reply_piece.lower(), 0) if reply_piece else 0
            )
            defended = reply_depth > 1 and has_bounded_defense(
                reply_child,
                reply_depth - 1,
                target_square=reply.to_square,
                target_value=reply_piece_value,
            )
            if owned_is_checkmate(reply_child):
                attacks.append(
                    defended_label("reply_mate", reply_text, defended=defended)
                )
            if reply_captures_moved_piece:
                attacks.append(
                    defended_label(
                        "reply_captures_moved_piece",
                        f"{reply_text}:{moved_piece_value}",
                        defended=defended,
                    )
                )
    return tuple(sorted(set(attacks)))


def defended_label(kind: str, payload: str, *, defended: bool) -> str:
    status = "defended" if defended else "undefended"
    return f"{kind}:{status}:{payload}"


def has_bounded_defense(
    board: Any,
    depth: int,
    *,
    target_square: int | None = None,
    target_value: int = 0,
) -> bool:
    if depth <= 0:
        return False
    for move in board.legal_moves():
        if (
            target_square is not None
            and owned_is_capture(board, move)
            and move.to_square == target_square
            and owned_capture_value(board, move) >= target_value
        ):
            return True
        child = board.apply(move)
        if owned_is_checkmate(child):
            return True
        if depth > 1 and not has_unanswered_reply(child, depth - 1):
            return True
    return False


def has_unanswered_reply(board: Any, depth: int) -> bool:
    if depth <= 0:
        return False
    for reply in board.legal_moves():
        child = board.apply(reply)
        if owned_is_checkmate(child):
            return True
        if depth > 1 and not has_bounded_defense(child, depth - 1):
            return True
    return False


def owned_is_capture(board: Any, move: Any) -> bool:
    target = board.piece_at(move.to_square)
    if target is not None:
        return True
    piece = board.piece_at(move.from_square)
    return (
        piece is not None
        and piece.lower() == "p"
        and board.ep_square == move.to_square
        and move.from_square % 8 != move.to_square % 8
    )


def owned_capture_value(board: Any, move: Any) -> int:
    if not owned_is_capture(board, move):
        return 0
    target = board.piece_at(move.to_square)
    if target is None:
        return OWNED_PIECE_VALUE["p"]
    return OWNED_PIECE_VALUE[target.lower()]


def owned_is_terminal(board: Any) -> bool:
    return len(board.legal_moves()) == 0


def owned_is_checkmate(board: Any) -> bool:
    return owned_is_terminal(board) and board.in_check(board.turn)


def owned_is_stalemate(board: Any) -> bool:
    return owned_is_terminal(board) and not board.in_check(board.turn)


def choose_move(
    probes: list[MoveProbe],
    graph: RootArgumentGraph | None = None,
) -> MoveProbe:
    if not probes:
        raise SystemExit("position has no legal moves")
    graph = graph or build_root_argument_graph(probes)
    accepted = [
        probe
        for probe in probes
        if graph.move_arguments[probe.uci] in graph.grounded_extension
    ]
    candidates = accepted if accepted else probes
    return sorted(candidates, key=lambda probe: selection_key(probe, graph))[0]


def selection_key(probe: MoveProbe, graph: RootArgumentGraph) -> tuple[float, int, int, int, int, str]:
    move_arg = graph.move_arguments[probe.uci]
    ranking_scores = graph.ranking.get("scores", {}) if graph.ranking.get("available") else {}
    move_rank = float(ranking_scores.get(move_arg, 0.0))
    accepted_support = sum(
        1
        for reason in probe.reasons
        if f"reason:{probe.uci}:{reason}" in graph.grounded_extension
    )
    accepted_defenses = sum(
        1
        for reply_attack in probe.reply_attacks
        if f"defense:{probe.uci}:{reply_attack}" in graph.grounded_extension
    )
    unresolved_attacks = sum(
        1
        for reply_attack in probe.reply_attacks
        if f"reply_attack:{probe.uci}:{reply_attack}" in graph.grounded_extension
    )
    # Argument semantics decide first. Numeric chess score is only a final
    # tie-break among equally ranked/defended argument statuses.
    return (
        -move_rank,
        -accepted_support,
        unresolved_attacks,
        -accepted_defenses,
        -probe.score,
        probe.uci,
    )


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


def build_root_argument_graph(probes: list[MoveProbe]) -> RootArgumentGraph:
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
        for reply_attack in probe.reply_attacks:
            reply_arg = f"reply_attack:{probe.uci}:{reply_attack}"
            arguments.add(reply_arg)
            defeats.add((reply_arg, move_arg))
            if ":defended:" in reply_attack:
                defense_arg = f"defense:{probe.uci}:{reply_attack}"
                arguments.add(defense_arg)
                defeats.add((defense_arg, reply_arg))

    frozen_arguments = frozenset(arguments)
    frozen_defeats = frozenset(defeats)
    grounded_extension = local_grounded_extension(frozen_arguments, frozen_defeats)
    ranking = local_argumentation_ranking(frozen_arguments, frozen_defeats)
    return RootArgumentGraph(
        arguments=frozen_arguments,
        defeats=frozen_defeats,
        move_arguments=move_args,
        grounded_extension=grounded_extension,
        ranking=ranking,
    )


def build_argument_payload(
    probes: list[MoveProbe],
    graph: RootArgumentGraph | None = None,
) -> dict[str, Any]:
    graph = graph or build_root_argument_graph(probes)
    return {
        "arguments": sorted(graph.arguments),
        "defeats": sorted([list(pair) for pair in graph.defeats]),
        "move_scores": [asdict(probe) for probe in probes],
        "move_arguments": dict(sorted(graph.move_arguments.items())),
        "grounded_extension": sorted(graph.grounded_extension),
        "argumentation_ranking": graph.ranking,
    }


def local_argumentation_ranking(
    arguments: frozenset[str],
    defeats: frozenset[tuple[str, str]],
) -> dict[str, Any]:
    imported = import_local_argumentation()
    if isinstance(imported, str):
        return {"available": False, "reason": imported}
    ArgumentationFramework, _grounded_extension, categoriser_scores = imported
    framework = ArgumentationFramework(
        arguments=arguments,
        defeats=defeats,
    )
    result = categoriser_scores(framework)
    return {
        "available": True,
        "scores": dict(sorted(result.scores.items())),
        "ranking": [sorted(tier) for tier in result.ranking],
        "semantics": result.semantics,
    }


def local_grounded_extension(
    arguments: frozenset[str],
    defeats: frozenset[tuple[str, str]],
) -> frozenset[str]:
    imported = import_local_argumentation()
    if isinstance(imported, str):
        return frozenset()
    ArgumentationFramework, grounded_extension, _categoriser_scores = imported
    framework = ArgumentationFramework(
        arguments=arguments,
        defeats=defeats,
    )
    return grounded_extension(framework)


def import_local_argumentation() -> tuple[Any, Any, Any] | str:
    root = Path(__file__).resolve().parents[1]
    src = root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
    try:
        from argumentation.dung import ArgumentationFramework, grounded_extension
        from argumentation.ranking import categoriser_scores
    except ImportError as exc:
        return str(exc)
    return ArgumentationFramework, grounded_extension, categoriser_scores


if __name__ == "__main__":
    raise SystemExit(main())
