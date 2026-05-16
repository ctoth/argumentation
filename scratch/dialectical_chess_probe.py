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
from typing import Any, TextIO

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
    reply_attacks: tuple[str, ...] = ()
    search_score: int | None = None
    search_line: tuple[str, ...] = ()


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
    parser.add_argument("--size", type=int, default=480)
    args = parser.parse_args(argv)

    if args.uci:
        return run_uci(sys.stdin, sys.stdout)

    game = load_game(args.pgn_in) if args.pgn_in else None
    board = final_board(game) if game else chess.Board(args.fen or DEFAULT_FEN)
    probes = probe_moves(
        board,
        dialectic_depth=args.dialectic_depth,
        search_depth=args.search_depth,
    )
    graph = build_root_argument_graph(probes)
    selected = choose_move(probes, graph)

    if args.svg:
        svg = chess.svg.board(board=board, size=args.size)
        args.svg.parent.mkdir(parents=True, exist_ok=True)
        args.svg.write_text(svg, encoding="utf-8")

    pgn_path = args.pgn_out or args.pgn
    if pgn_path:
        pgn_path.parent.mkdir(parents=True, exist_ok=True)
        pgn_path.write_text(build_pgn(board, selected, game=game), encoding="utf-8")

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
            _uci_write(output_stream, "id name DialecticalChessProbe")
            _uci_write(output_stream, "id author argumentation")
            _uci_write(output_stream, "uciok")
        elif command == "isready":
            _uci_write(output_stream, "readyok")
        elif command == "ucinewgame":
            board = chess.Board()
        elif command.startswith("position "):
            try:
                board = parse_uci_position(command)
            except ValueError as exc:
                _uci_write(output_stream, f"info string invalid position: {exc}")
        elif command.startswith("go"):
            _uci_write(output_stream, f"bestmove {choose_uci_move(board)}")
        elif command == "stop":
            _uci_write(output_stream, f"bestmove {choose_uci_move(board)}")
        elif command == "quit":
            return 0
        elif command.startswith("setoption ") or command == "ponderhit":
            continue
        else:
            _uci_write(output_stream, f"info string unsupported command: {command}")


def _uci_write(output_stream: TextIO, line: str) -> None:
    print(line, file=output_stream, flush=True)


def parse_uci_position(command: str) -> chess.Board:
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


def choose_uci_move(board: chess.Board) -> str:
    probes = probe_moves(board, dialectic_depth=1)
    if not probes:
        return "0000"
    return choose_move(probes, build_root_argument_graph(probes)).uci


def probe_moves(
    board: chess.Board,
    *,
    dialectic_depth: int = 1,
    search_depth: int = 0,
) -> list[MoveProbe]:
    if dialectic_depth < 0:
        raise ValueError("dialectic_depth must be non-negative")
    if search_depth < 0:
        raise ValueError("search_depth must be non-negative")
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
        search_result = root_search_result(board, move, depth=search_depth)
        if search_result is not None:
            if search_result.score > 0:
                reasons.append(f"search:negamax:{search_result.score}")
            elif search_result.score < 0:
                objections.append(f"search:negamax:{search_result.score}")
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
            )
        )
    return sorted(probes, key=lambda probe: (-probe.score, probe.uci))


def root_search_result(
    board: chess.Board,
    move: chess.Move,
    *,
    depth: int,
) -> SearchResult | None:
    if depth <= 0:
        return None
    board.push(move)
    try:
        child = negamax(board, depth - 1)
        return SearchResult(score=-child.score, line=(move.uci(),) + child.line)
    finally:
        board.pop()


def negamax(board: chess.Board, depth: int) -> SearchResult:
    if board.is_checkmate():
        return SearchResult(score=-100_000 - depth, line=())
    if board.is_stalemate() or board.is_insufficient_material():
        return SearchResult(score=0, line=())
    if depth <= 0:
        return SearchResult(score=static_evaluation(board), line=())

    best: SearchResult | None = None
    best_move: chess.Move | None = None
    for move in board.legal_moves:
        board.push(move)
        try:
            child = negamax(board, depth - 1)
            candidate = SearchResult(score=-child.score, line=(move.uci(),) + child.line)
        finally:
            board.pop()
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


def static_evaluation(board: chess.Board) -> int:
    white = 0
    black = 0
    for piece in board.piece_map().values():
        value = PIECE_VALUE[piece.piece_type]
        if piece.color == chess.WHITE:
            white += value
        else:
            black += value
    material = white - black
    return material if board.turn == chess.WHITE else -material


def capture_value(board: chess.Board, move: chess.Move) -> int:
    if board.is_en_passant(move):
        return PIECE_VALUE[chess.PAWN]
    captured = board.piece_at(move.to_square)
    if captured is None:
        return 0
    return PIECE_VALUE[captured.piece_type]


def bounded_reply_attacks(
    board: chess.Board,
    move: chess.Move,
    *,
    reply_depth: int,
) -> tuple[str, ...]:
    if reply_depth <= 0:
        return ()
    moved_piece = board.piece_at(move.from_square)
    moved_piece_value = PIECE_VALUE.get(moved_piece.piece_type, 0) if moved_piece else 0
    moved_to = move.to_square
    attacks: list[str] = []

    board.push(move)
    if not board.is_game_over(claim_draw=False):
        for reply in board.legal_moves:
            reply_text = reply.uci()
            reply_captures_moved_piece = (
                board.is_capture(reply)
                and reply.to_square == moved_to
                and moved_piece_value > 0
            )
            board.push(reply)
            reply_piece = board.piece_at(reply.to_square)
            reply_piece_value = (
                PIECE_VALUE.get(reply_piece.piece_type, 0) if reply_piece else 0
            )
            defended = reply_depth > 1 and has_bounded_defense(
                board,
                reply_depth - 1,
                target_square=reply.to_square,
                target_value=reply_piece_value,
            )
            if board.is_checkmate():
                attacks.append(
                    defended_label("reply_mate", reply_text, defended=defended)
                )
            board.pop()
            if reply_captures_moved_piece:
                attacks.append(
                    defended_label(
                        "reply_captures_moved_piece",
                        f"{reply_text}:{moved_piece_value}",
                        defended=defended,
                    )
                )
    board.pop()
    return tuple(sorted(set(attacks)))


def defended_label(kind: str, payload: str, *, defended: bool) -> str:
    status = "defended" if defended else "undefended"
    return f"{kind}:{status}:{payload}"


def has_bounded_defense(
    board: chess.Board,
    depth: int,
    *,
    target_square: chess.Square | None = None,
    target_value: int = 0,
) -> bool:
    if depth <= 0:
        return False
    for move in board.legal_moves:
        if (
            target_square is not None
            and board.is_capture(move)
            and move.to_square == target_square
            and capture_value(board, move) >= target_value
        ):
            return True
        board.push(move)
        try:
            if board.is_checkmate():
                return True
            if depth > 1 and not has_unanswered_reply(board, depth - 1):
                return True
        finally:
            board.pop()
    return False


def has_unanswered_reply(board: chess.Board, depth: int) -> bool:
    if depth <= 0:
        return False
    for reply in board.legal_moves:
        board.push(reply)
        try:
            if board.is_checkmate():
                return True
            if depth > 1 and not has_bounded_defense(board, depth - 1):
                return True
        finally:
            board.pop()
    return False


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
    return sorted(candidates, key=lambda probe: (-probe.score, probe.uci))[0]


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
