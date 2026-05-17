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
class ReplyAnalysisSettings:
    max_replies: int | None = 128
    max_defense_nodes: int | None = 5000
    min_defense_material: int = 300


@dataclass
class ReplyAnalysisCache:
    legal_move_hits: int = 0
    legal_move_misses: int = 0
    apply_hits: int = 0
    apply_misses: int = 0
    checkmate_hits: int = 0
    checkmate_misses: int = 0
    defense_nodes: int = 0
    truncated: bool = False
    truncation_reasons: set[str] = None

    def __post_init__(self) -> None:
        self._legal_moves: dict[Any, tuple[Any, ...]] = {}
        self._applied: dict[tuple[Any, str], Any] = {}
        self._checkmates: dict[Any, bool] = {}
        if self.truncation_reasons is None:
            self.truncation_reasons = set()

    def legal_moves(self, board: Any) -> tuple[Any, ...]:
        if board in self._legal_moves:
            self.legal_move_hits += 1
            return self._legal_moves[board]
        self.legal_move_misses += 1
        moves = tuple(board.legal_moves())
        self._legal_moves[board] = moves
        return moves

    def apply(self, board: Any, move: Any) -> Any:
        key = (board, move.uci())
        if key in self._applied:
            self.apply_hits += 1
            return self._applied[key]
        self.apply_misses += 1
        child = board.apply(move)
        self._applied[key] = child
        return child

    def is_checkmate(self, board: Any) -> bool:
        if board in self._checkmates:
            self.checkmate_hits += 1
            return self._checkmates[board]
        self.checkmate_misses += 1
        result = board.in_check(board.turn) and len(self.legal_moves(board)) == 0
        self._checkmates[board] = result
        return result

    def consume_defense_node(self, settings: ReplyAnalysisSettings) -> bool:
        self.defense_nodes += 1
        if settings.max_defense_nodes is not None and self.defense_nodes > settings.max_defense_nodes:
            self.truncated = True
            self.truncation_reasons.add("defense_budget")
            return False
        return True


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
    settings: ReplyAnalysisSettings | None = None,
    cache: ReplyAnalysisCache | None = None,
) -> tuple[str, ...]:
    if reply_depth <= 0:
        return ()
    settings = settings or ReplyAnalysisSettings()
    cache = cache or ReplyAnalysisCache()
    moved_piece = board.piece_at(move.from_square)
    moved_piece_value = OWNED_PIECE_VALUE.get(moved_piece.lower(), 0) if moved_piece else 0
    moved_to = move.to_square
    attacks: list[str] = []

    child = cache.apply(board, move)
    if cache.legal_moves(child):
        for reply_index, reply in enumerate(cache.legal_moves(child), start=1):
            if settings.max_replies is not None and reply_index > settings.max_replies:
                cache.truncated = True
                cache.truncation_reasons.add("reply_budget")
                break
            reply_text = reply.uci()
            reply_captures_moved_piece = (
                owned_is_capture(child, reply)
                and reply.to_square == moved_to
                and moved_piece_value > 0
            )
            reply_child = cache.apply(child, reply)
            reply_piece = reply_child.piece_at(reply.to_square)
            reply_piece_value = (
                OWNED_PIECE_VALUE.get(reply_piece.lower(), 0) if reply_piece else 0
            )
            reply_gives_check = reply_child.in_check(reply_child.turn)
            reply_is_mate = reply_gives_check and cache.is_checkmate(reply_child)
            relevant_for_defense = (
                reply_is_mate
                or reply_captures_moved_piece
                or reply_piece_value >= settings.min_defense_material
                or reply_gives_check
            )
            defended = (
                reply_depth > 1
                and relevant_for_defense
                and has_bounded_defense(
                    reply_child,
                    reply_depth - 1,
                    target_square=reply.to_square,
                    target_value=reply_piece_value,
                    settings=settings,
                    cache=cache,
                )
            )
            if reply_is_mate:
                attacks.append(defended_label("reply_mate", reply_text, defended=defended))
            if reply_captures_moved_piece:
                attacks.append(
                    defended_label(
                        "reply_captures_moved_piece",
                        f"{reply_text}:{moved_piece_value}",
                        defended=defended,
                    )
                )
    for reason in sorted(cache.truncation_reasons):
        attacks.append(f"reply_analysis:truncated:{reason}")
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
    settings: ReplyAnalysisSettings | None = None,
    cache: ReplyAnalysisCache | None = None,
) -> bool:
    if depth <= 0:
        return False
    settings = settings or ReplyAnalysisSettings()
    cache = cache or ReplyAnalysisCache()
    if not cache.consume_defense_node(settings):
        return False
    if target_square is not None and target_value > 0 and board.is_square_attacked(target_square, board.turn):
        return True
    if depth <= 1:
        return False
    for move in cache.legal_moves(board):
        if (
            target_square is not None
            and owned_is_capture(board, move)
            and move.to_square == target_square
            and owned_capture_value(board, move) >= target_value
        ):
            return True
    for move in cache.legal_moves(board):
        child = cache.apply(board, move)
        if cache.is_checkmate(child):
            return True
        if not has_unanswered_reply(child, depth - 1, settings=settings, cache=cache):
            return True
    return False


def has_unanswered_reply(
    board: Any,
    depth: int,
    *,
    settings: ReplyAnalysisSettings | None = None,
    cache: ReplyAnalysisCache | None = None,
) -> bool:
    if depth <= 0:
        return False
    settings = settings or ReplyAnalysisSettings()
    cache = cache or ReplyAnalysisCache()
    for reply in cache.legal_moves(board):
        child = cache.apply(board, reply)
        if cache.is_checkmate(child):
            return True
        if depth > 1 and not has_bounded_defense(child, depth - 1, settings=settings, cache=cache):
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
