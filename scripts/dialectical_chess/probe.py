"""Move probing for dialectical chess."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from dialectical_chess.arguments import MoveProbe
from dialectical_chess.board import OwnedBoard, file_of, piece_color, rank_of, square_index
from dialectical_chess.search import (
    OWNED_PIECE_VALUE,
    SearchSettings,
    bounded_reply_attacks,
    owned_capture_value,
    owned_is_capture,
    owned_is_checkmate,
    root_search_result,
)
from dialectical_chess.smt import (
    SmtSettings,
    moved_piece_attacks_square,
    smt_fork_moves,
    smt_mate_in_one_moves,
)


@dataclass(frozen=True)
class ProbeSettings:
    dialectic_depth: int = 1
    search: SearchSettings = field(default_factory=SearchSettings)
    smt: SmtSettings = field(default_factory=SmtSettings)
    positional_reasons: bool = True


def probe_moves(
    board: Any,
    *,
    dialectic_depth: int = 1,
    search_depth: int = 0,
    search_backend: str = "negamax",
    smt_mate: bool = True,
    positional_reasons: bool = True,
) -> list[MoveProbe]:
    settings = ProbeSettings(
        dialectic_depth=dialectic_depth,
        search=SearchSettings(depth=search_depth, backend=search_backend),
        smt=SmtSettings(mate_in_one=smt_mate),
        positional_reasons=positional_reasons,
    )
    return probe_moves_with_settings(board, settings)


def probe_moves_with_settings(board: Any, settings: ProbeSettings) -> list[MoveProbe]:
    if settings.dialectic_depth < 0:
        raise ValueError("dialectic_depth must be non-negative")
    if settings.search.depth < 0:
        raise ValueError("search_depth must be non-negative")
    board = ensure_owned_board(board)
    legal_moves = sorted(board.legal_moves(), key=lambda move: move.uci())
    smt_mate_moves = (
        smt_mate_in_one_moves(board) if settings.smt.mate_in_one else frozenset()
    )
    smt_fork_move_set = smt_fork_moves(board) if settings.smt.fork else frozenset()
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
        if settings.positional_reasons:
            positional = positional_reason_labels(board, move, child)
            if positional:
                score += 25 * len(positional)
                reasons.extend(positional)
        smt_witnesses: list[str] = []
        if move.uci() in smt_mate_moves:
            score += 1_000_000
            reasons.append("procedural:mate_in_one")
            smt_witnesses.append("procedural_mate_in_one")
        if move.uci() in smt_fork_move_set:
            score += 500
            reasons.append("smt:fork:2:500")
            smt_witnesses.append("fork")
        search_result = root_search_result(board, move, settings=settings.search)
        if search_result is not None:
            if search_result.score > 0:
                reasons.append(f"search:{settings.search.backend}:{search_result.score}")
            elif search_result.score < 0:
                objections.append(f"search:{settings.search.backend}:{search_result.score}")
            score += search_result.score
        reply_attacks = bounded_reply_attacks(
            board,
            move,
            reply_depth=settings.dialectic_depth,
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


def ensure_owned_board(board: Any) -> OwnedBoard:
    if isinstance(board, OwnedBoard):
        return board
    return owned_board_from_fen(board.fen())


def owned_board_from_fen(fen: str) -> OwnedBoard:
    return OwnedBoard.from_fen(fen)


def positional_reason_labels(board: OwnedBoard, move: Any, child: OwnedBoard) -> tuple[str, ...]:
    piece = board.piece_at(move.from_square)
    if piece is None:
        return ()
    labels: list[str] = []
    move_text = move.uci()
    kind = piece.lower()
    color = piece_color(piece)
    from_rank = rank_of(move.from_square)
    to_rank = rank_of(move.to_square)

    if kind == "p" and file_of(move.from_square) in {3, 4} and abs(to_rank - from_rank) == 2:
        labels.append(f"development:{move_text}:center_pawn")
    if kind in {"n", "b"} and from_rank == (0 if color == "w" else 7):
        labels.append(f"development:{move_text}:minor_piece")
    if move.kind == "castle":
        labels.append(f"king_safety:{move_text}:castle")

    center_count = moved_piece_center_control(child, move.to_square, piece)
    if center_count:
        labels.append(f"center_control:{move_text}:{center_count}")
    activity_gain = moved_piece_activity_gain(board, child, move.from_square, move.to_square, piece)
    if activity_gain > 0:
        labels.append(f"piece_activity:{move_text}:mobility_gain:{activity_gain}")
    if kind == "p" and is_passed_pawn(child, move.to_square, color):
        labels.append(f"pawn_structure:{move_text}:passed_pawn")
    if kind in {"r", "q"} and controls_open_file(child, move.to_square):
        labels.append(f"file_control:{move_text}:open_file")
    if kind == "n" and is_supported_outpost(child, move.to_square, color):
        labels.append(f"outpost:{move_text}:supported")
    return tuple(labels)


def moved_piece_center_control(board: OwnedBoard, source_square: int, piece: str) -> int:
    return sum(
        1
        for target in (
            square_index("d4"),
            square_index("e4"),
            square_index("d5"),
            square_index("e5"),
        )
        if moved_piece_attacks_square(board, source_square, target, piece)
    )


def controls_open_file(board: OwnedBoard, square: int) -> bool:
    file_index = file_of(square)
    return all(
        piece is None or piece.lower() != "p"
        for index, piece in enumerate(board.squares)
        if file_of(index) == file_index
    )


def moved_piece_activity_gain(
    before: OwnedBoard,
    after: OwnedBoard,
    from_square: int,
    to_square: int,
    piece: str,
) -> int:
    before_activity = moved_piece_activity(before, from_square, piece)
    after_activity = moved_piece_activity(after, to_square, piece)
    return after_activity - before_activity


def moved_piece_activity(board: OwnedBoard, square: int, piece: str) -> int:
    return sum(
        1
        for target in range(64)
        if target != square and moved_piece_attacks_square(board, square, target, piece)
    )


def is_passed_pawn(board: OwnedBoard, square: int, color: str) -> bool:
    opponent_pawn = "p" if color == "w" else "P"
    start_rank = rank_of(square) + (1 if color == "w" else -1)
    stop_rank = 8 if color == "w" else -1
    step = 1 if color == "w" else -1
    for file_index in range(max(0, file_of(square) - 1), min(7, file_of(square) + 1) + 1):
        for rank_index in range(start_rank, stop_rank, step):
            if board.piece_at(rank_index * 8 + file_index) == opponent_pawn:
                return False
    return True


def is_supported_outpost(board: OwnedBoard, square: int, color: str) -> bool:
    rank = rank_of(square)
    if color == "w" and rank < 3:
        return False
    if color == "b" and rank > 4:
        return False
    support_rank = rank - 1 if color == "w" else rank + 1
    support_piece = "P" if color == "w" else "p"
    for file_delta in (-1, 1):
        support_file = file_of(square) + file_delta
        if 0 <= support_file < 8:
            support_square = support_rank * 8 + support_file
            if 0 <= support_square < 64 and board.piece_at(support_square) == support_piece:
                return True
    return False
