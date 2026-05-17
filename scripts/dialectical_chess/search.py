"""Tactical search helpers for dialectical chess move probing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


OWNED_PIECE_VALUE = {"p": 100, "n": 320, "b": 330, "r": 500, "q": 900, "k": 0}


@dataclass(frozen=True)
class SearchSettings:
    depth: int = 0
    backend: str = "negamax"


@dataclass(frozen=True)
class SearchResult:
    score: int
    line: tuple[str, ...]


def root_search_result(
    board: Any,
    move: Any,
    *,
    settings: SearchSettings,
) -> SearchResult | None:
    if settings.depth <= 0:
        return None
    child_board = board.apply(move)
    if settings.backend == "negamax":
        child = negamax(child_board, settings.depth - 1)
    elif settings.backend == "alphabeta":
        child = alphabeta(child_board, settings.depth - 1, alpha=-1_000_000, beta=1_000_000)
    else:
        raise ValueError(f"unsupported search backend: {settings.backend}")
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
                attacks.append(defended_label("reply_mate", reply_text, defended=defended))
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
