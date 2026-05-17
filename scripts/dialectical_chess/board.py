"""Owned chess move generation substrate for dialectical chess experiments."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any, Iterable

import chess


START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
PIECE_VALUES = {"P": 100, "N": 320, "B": 330, "R": 500, "Q": 900, "K": 0}
FILES = "abcdefgh"
PROMOTIONS = ("q", "r", "b", "n")
KNIGHT_DELTAS = ((1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2))
KING_DELTAS = ((1, 1), (1, 0), (1, -1), (0, 1), (0, -1), (-1, 1), (-1, 0), (-1, -1))
BISHOP_DELTAS = ((1, 1), (1, -1), (-1, 1), (-1, -1))
ROOK_DELTAS = ((1, 0), (-1, 0), (0, 1), (0, -1))


@dataclass(frozen=True, order=True)
class OwnedMove:
    from_square: int
    to_square: int
    promotion: str | None = None
    kind: str = "normal"

    @classmethod
    def from_uci(cls, text: str) -> "OwnedMove":
        if len(text) not in {4, 5}:
            raise ValueError(f"invalid UCI move: {text}")
        promotion = text[4] if len(text) == 5 else None
        if promotion is not None and promotion not in PROMOTIONS:
            raise ValueError(f"invalid promotion piece: {promotion}")
        return cls(square_index(text[:2]), square_index(text[2:4]), promotion)

    def uci(self) -> str:
        return square_name(self.from_square) + square_name(self.to_square) + (self.promotion or "")


@dataclass(frozen=True)
class OwnedBoard:
    squares: tuple[str | None, ...]
    turn: str
    castling: str
    ep_square: int | None
    halfmove_clock: int
    fullmove_number: int

    @classmethod
    def from_fen(cls, fen: str, *, legal_game: bool = True) -> "OwnedBoard":
        fields = fen.split()
        if len(fields) != 6:
            raise ValueError("FEN must contain six fields")
        placement, turn, castling, ep_square, halfmove, fullmove = fields
        if turn not in {"w", "b"}:
            raise ValueError("FEN side-to-move field must be 'w' or 'b'")
        if castling != "-":
            if any(char not in "KQkq" for char in castling) or len(set(castling)) != len(castling):
                raise ValueError("invalid FEN castling rights")
            castling = "".join(char for char in "KQkq" if char in castling)
        ep_index = None if ep_square == "-" else square_index(ep_square)
        if ep_index is not None and rank_of(ep_index) not in {2, 5}:
            raise ValueError("invalid en-passant square rank")
        try:
            halfmove_clock = int(halfmove)
            fullmove_number = int(fullmove)
        except ValueError as exc:
            raise ValueError("invalid FEN clocks") from exc
        if halfmove_clock < 0 or fullmove_number < 1:
            raise ValueError("invalid FEN clocks")
        squares = parse_placement(placement)
        if legal_game:
            if sum(1 for piece in squares if piece == "K") != 1 or sum(1 for piece in squares if piece == "k") != 1:
                raise ValueError("legal-game FEN must contain exactly one king per side")
        return cls(squares, turn, castling, ep_index, halfmove_clock, fullmove_number)

    def fen(self) -> str:
        return " ".join(
            [
                serialize_placement(self.squares),
                self.turn,
                self.castling or "-",
                "-" if self.ep_square is None else square_name(self.ep_square),
                str(self.halfmove_clock),
                str(self.fullmove_number),
            ]
        )

    def piece_at(self, square: str | int) -> str | None:
        return self.squares[square_index(square) if isinstance(square, str) else square]

    def material_balance(self) -> int:
        white = black = 0
        for piece in self.squares:
            if piece is None:
                continue
            value = PIECE_VALUES[piece.upper()]
            if piece.isupper():
                white += value
            else:
                black += value
        return white - black

    def side_to_move_material(self) -> int:
        balance = self.material_balance()
        return balance if self.turn == "w" else -balance

    def pseudo_legal_moves(self) -> tuple[OwnedMove, ...]:
        moves: list[OwnedMove] = []
        for index, piece in enumerate(self.squares):
            if piece is None or piece_color(piece) != self.turn:
                continue
            kind = piece.lower()
            if kind == "p":
                self._pawn_moves(index, piece, moves)
            elif kind == "n":
                self._jump_moves(index, KNIGHT_DELTAS, moves)
            elif kind == "b":
                self._ray_moves(index, BISHOP_DELTAS, moves)
            elif kind == "r":
                self._ray_moves(index, ROOK_DELTAS, moves)
            elif kind == "q":
                self._ray_moves(index, BISHOP_DELTAS + ROOK_DELTAS, moves)
            elif kind == "k":
                self._jump_moves(index, KING_DELTAS, moves)
                self._castle_moves(index, moves)
        return tuple(sorted(moves, key=lambda move: move.uci()))

    def legal_moves(self) -> tuple[OwnedMove, ...]:
        legal: list[OwnedMove] = []
        color = self.turn
        for move in self.pseudo_legal_moves():
            try:
                child = self.apply(move)
            except ValueError:
                continue
            if not child.in_check(color):
                legal.append(move)
        return tuple(sorted(legal, key=lambda move: move.uci()))

    def in_check(self, color: str | None = None) -> bool:
        color = color or self.turn
        return self.is_square_attacked(self.king_square(color), opposite(color))

    def is_square_attacked(self, square: int, by_color: str) -> bool:
        sf, sr = file_of(square), rank_of(square)
        pawn_rank_delta = -1 if by_color == "w" else 1
        for file_delta in (-1, 1):
            attacker = square_from_file_rank(sf + file_delta, sr + pawn_rank_delta)
            if attacker is not None and self.squares[attacker] == ("P" if by_color == "w" else "p"):
                return True
        for df, dr in KNIGHT_DELTAS:
            attacker = square_from_file_rank(sf + df, sr + dr)
            if attacker is not None and self.squares[attacker] == ("N" if by_color == "w" else "n"):
                return True
        if self._ray_attacked(sf, sr, by_color, BISHOP_DELTAS, {"b", "q"}):
            return True
        if self._ray_attacked(sf, sr, by_color, ROOK_DELTAS, {"r", "q"}):
            return True
        for df, dr in KING_DELTAS:
            attacker = square_from_file_rank(sf + df, sr + dr)
            if attacker is not None and self.squares[attacker] == ("K" if by_color == "w" else "k"):
                return True
        return False

    def king_square(self, color: str) -> int:
        king = "K" if color == "w" else "k"
        for index, piece in enumerate(self.squares):
            if piece == king:
                return index
        raise ValueError(f"missing {color} king")

    def apply(self, move: OwnedMove | str) -> "OwnedBoard":
        move = OwnedMove.from_uci(move) if isinstance(move, str) else move
        piece = self.squares[move.from_square]
        if piece is None:
            raise ValueError(f"no piece on {square_name(move.from_square)}")
        color = piece_color(piece)
        if color != self.turn:
            raise ValueError("cannot move opponent piece")
        target = self.squares[move.to_square]
        if target is not None and piece_color(target) == color:
            raise ValueError("cannot capture own piece")

        board = list(self.squares)
        board[move.from_square] = None
        captured = target
        moving_piece = piece
        is_pawn = piece.lower() == "p"
        is_ep = is_pawn and self.ep_square == move.to_square and target is None and file_of(move.from_square) != file_of(move.to_square)
        if is_ep:
            capture_square = move.to_square - 8 if color == "w" else move.to_square + 8
            captured = board[capture_square]
            if captured != ("p" if color == "w" else "P"):
                raise ValueError("invalid en-passant capture")
            board[capture_square] = None

        if move.promotion is not None:
            if not is_pawn or rank_of(move.to_square) not in {0, 7}:
                raise ValueError("invalid promotion")
            moving_piece = move.promotion.upper() if color == "w" else move.promotion

        is_castle = piece.lower() == "k" and abs(file_of(move.to_square) - file_of(move.from_square)) == 2
        if is_castle:
            self._apply_castle_rook(board, move, color)
        board[move.to_square] = moving_piece

        castling = self._updated_castling(move, piece, captured)
        ep_square = None
        if is_pawn and abs(rank_of(move.to_square) - rank_of(move.from_square)) == 2:
            ep_square = (move.from_square + move.to_square) // 2
        halfmove = 0 if is_pawn or captured is not None else self.halfmove_clock + 1
        fullmove = self.fullmove_number + (1 if self.turn == "b" else 0)
        return OwnedBoard(tuple(board), opposite(self.turn), castling, ep_square, halfmove, fullmove)

    def _pawn_moves(self, index: int, piece: str, moves: list[OwnedMove]) -> None:
        color = piece_color(piece)
        direction = 1 if color == "w" else -1
        start_rank = 1 if color == "w" else 6
        promotion_rank = 7 if color == "w" else 0
        file_index, rank_index = file_of(index), rank_of(index)
        one = square_from_file_rank(file_index, rank_index + direction)
        if one is not None and self.squares[one] is None:
            self._append_pawn_move(index, one, promotion_rank, moves)
            two = square_from_file_rank(file_index, rank_index + 2 * direction)
            if rank_index == start_rank and two is not None and self.squares[two] is None:
                moves.append(OwnedMove(index, two))
        for df in (-1, 1):
            target = square_from_file_rank(file_index + df, rank_index + direction)
            if target is None:
                continue
            occupant = self.squares[target]
            if occupant is not None and piece_color(occupant) != color:
                self._append_pawn_move(index, target, promotion_rank, moves)
            elif self.ep_square == target:
                moves.append(OwnedMove(index, target, kind="en_passant"))

    def _append_pawn_move(
        self,
        from_square: int,
        to_square: int,
        promotion_rank: int,
        moves: list[OwnedMove],
    ) -> None:
        if rank_of(to_square) == promotion_rank:
            for promotion in PROMOTIONS:
                moves.append(OwnedMove(from_square, to_square, promotion))
        else:
            moves.append(OwnedMove(from_square, to_square))

    def _jump_moves(
        self,
        index: int,
        deltas: Iterable[tuple[int, int]],
        moves: list[OwnedMove],
    ) -> None:
        piece = self.squares[index]
        assert piece is not None
        color = piece_color(piece)
        file_index, rank_index = file_of(index), rank_of(index)
        for df, dr in deltas:
            target = square_from_file_rank(file_index + df, rank_index + dr)
            if target is None:
                continue
            occupant = self.squares[target]
            if occupant is None or piece_color(occupant) != color:
                moves.append(OwnedMove(index, target))

    def _ray_moves(
        self,
        index: int,
        deltas: Iterable[tuple[int, int]],
        moves: list[OwnedMove],
    ) -> None:
        piece = self.squares[index]
        assert piece is not None
        color = piece_color(piece)
        for df, dr in deltas:
            file_index, rank_index = file_of(index) + df, rank_of(index) + dr
            while True:
                target = square_from_file_rank(file_index, rank_index)
                if target is None:
                    break
                occupant = self.squares[target]
                if occupant is None:
                    moves.append(OwnedMove(index, target))
                else:
                    if piece_color(occupant) != color:
                        moves.append(OwnedMove(index, target))
                    break
                file_index += df
                rank_index += dr

    def _castle_moves(self, index: int, moves: list[OwnedMove]) -> None:
        if self.in_check(self.turn):
            return
        if self.turn == "w" and index == square_index("e1"):
            self._maybe_castle("K", "f1", "g1", moves)
            self._maybe_castle("Q", "d1", "c1", moves, extra_clear="b1")
        elif self.turn == "b" and index == square_index("e8"):
            self._maybe_castle("k", "f8", "g8", moves)
            self._maybe_castle("q", "d8", "c8", moves, extra_clear="b8")

    def _maybe_castle(
        self,
        right: str,
        transit: str,
        destination: str,
        moves: list[OwnedMove],
        *,
        extra_clear: str | None = None,
    ) -> None:
        if right not in self.castling:
            return
        clear_squares = [transit, destination] + ([] if extra_clear is None else [extra_clear])
        if any(self.piece_at(square) is not None for square in clear_squares):
            return
        opponent = opposite(self.turn)
        if self.is_square_attacked(square_index(transit), opponent):
            return
        if self.is_square_attacked(square_index(destination), opponent):
            return
        moves.append(OwnedMove(self.king_square(self.turn), square_index(destination), kind="castle"))

    def _apply_castle_rook(self, board: list[str | None], move: OwnedMove, color: str) -> None:
        rook_from_to = {
            ("w", "g1"): ("h1", "f1"),
            ("w", "c1"): ("a1", "d1"),
            ("b", "g8"): ("h8", "f8"),
            ("b", "c8"): ("a8", "d8"),
        }
        key = (color, square_name(move.to_square))
        if key not in rook_from_to:
            raise ValueError("invalid castle destination")
        rook_from_name, rook_to_name = rook_from_to[key]
        rook_from = square_index(rook_from_name)
        rook_to = square_index(rook_to_name)
        expected_rook = "R" if color == "w" else "r"
        if board[rook_from] != expected_rook:
            raise ValueError("missing castling rook")
        board[rook_from] = None
        board[rook_to] = expected_rook

    def _updated_castling(self, move: OwnedMove, piece: str, captured: str | None) -> str:
        rights = set(self.castling)
        if piece == "K":
            rights.discard("K")
            rights.discard("Q")
        elif piece == "k":
            rights.discard("k")
            rights.discard("q")
        rook_rights = {
            square_index("a1"): "Q",
            square_index("h1"): "K",
            square_index("a8"): "q",
            square_index("h8"): "k",
        }
        if piece.lower() == "r" and move.from_square in rook_rights:
            rights.discard(rook_rights[move.from_square])
        if captured is not None and move.to_square in rook_rights:
            rights.discard(rook_rights[move.to_square])
        return "".join(char for char in "KQkq" if char in rights)

    def _ray_attacked(
        self,
        file_index: int,
        rank_index: int,
        by_color: str,
        deltas: Iterable[tuple[int, int]],
        attackers: set[str],
    ) -> bool:
        for df, dr in deltas:
            file_cursor, rank_cursor = file_index + df, rank_index + dr
            while True:
                target = square_from_file_rank(file_cursor, rank_cursor)
                if target is None:
                    break
                piece = self.squares[target]
                if piece is not None:
                    if piece_color(piece) == by_color and piece.lower() in attackers:
                        return True
                    break
                file_cursor += df
                rank_cursor += dr
        return False


def parse_placement(placement: str) -> tuple[str | None, ...]:
    ranks = placement.split("/")
    if len(ranks) != 8:
        raise ValueError("FEN placement must contain eight ranks")
    squares: list[str | None] = [None] * 64
    for fen_rank_index, rank_text in enumerate(ranks):
        board_rank = 7 - fen_rank_index
        file_index = 0
        previous_digit = False
        for char in rank_text:
            if char.isdigit():
                if char == "0" or previous_digit:
                    raise ValueError("invalid FEN rank digit")
                file_index += int(char)
                previous_digit = True
                continue
            previous_digit = False
            if char.upper() not in PIECE_VALUES:
                raise ValueError(f"unknown FEN piece: {char}")
            if file_index >= 8:
                raise ValueError("too many files in FEN rank")
            squares[board_rank * 8 + file_index] = char
            file_index += 1
        if file_index != 8:
            raise ValueError("FEN rank does not contain eight files")
    return tuple(squares)


def serialize_placement(squares: tuple[str | None, ...]) -> str:
    ranks: list[str] = []
    for rank_index in range(7, -1, -1):
        empties = 0
        text = []
        for file_index in range(8):
            piece = squares[rank_index * 8 + file_index]
            if piece is None:
                empties += 1
            else:
                if empties:
                    text.append(str(empties))
                    empties = 0
                text.append(piece)
        if empties:
            text.append(str(empties))
        ranks.append("".join(text))
    return "/".join(ranks)


def square_index(square: str) -> int:
    if len(square) != 2 or square[0] not in FILES or square[1] not in "12345678":
        raise ValueError(f"invalid square: {square}")
    return (int(square[1]) - 1) * 8 + FILES.index(square[0])


def square_name(index: int) -> str:
    if index < 0 or index >= 64:
        raise ValueError(f"invalid square index: {index}")
    return FILES[file_of(index)] + str(rank_of(index) + 1)


def file_of(index: int) -> int:
    return index % 8


def rank_of(index: int) -> int:
    return index // 8


def square_from_file_rank(file_index: int, rank_index: int) -> int | None:
    if 0 <= file_index < 8 and 0 <= rank_index < 8:
        return rank_index * 8 + file_index
    return None


def piece_color(piece: str) -> str:
    return "w" if piece.isupper() else "b"


def opposite(color: str) -> str:
    return "b" if color == "w" else "w"


def owned_perft(board: OwnedBoard, depth: int) -> int:
    if depth < 0:
        raise ValueError("perft depth must be non-negative")
    if depth == 0:
        return 1
    total = 0
    for move in board.legal_moves():
        total += owned_perft(board.apply(move), depth - 1)
    return total


def oracle_perft(board: chess.Board, depth: int) -> int:
    if depth == 0:
        return 1
    total = 0
    for move in board.legal_moves:
        board.push(move)
        try:
            total += oracle_perft(board, depth - 1)
        finally:
            board.pop()
    return total


def owned_divide(board: OwnedBoard, depth: int) -> dict[str, int]:
    if depth < 1:
        raise ValueError("divide depth must be at least one")
    return {move.uci(): owned_perft(board.apply(move), depth - 1) for move in board.legal_moves()}


def oracle_legal_moves(fen: str) -> set[str]:
    return {move.uci() for move in chess.Board(fen).legal_moves}


def compare_to_oracle(fen: str) -> dict[str, object]:
    board = OwnedBoard.from_fen(fen)
    owned = {move.uci() for move in board.legal_moves()}
    oracle = oracle_legal_moves(fen)
    return {
        "fen": fen,
        "match": owned == oracle,
        "owned_count": len(owned),
        "oracle_count": len(oracle),
        "missing": sorted(oracle - owned),
        "extra": sorted(owned - oracle),
    }


CURATED_FENS = {
    "startpos": START_FEN,
    "mate_smoke": "7k/6pp/8/8/8/8/6PP/R5K1 w - - 0 1",
    "stalemate": "7k/5K2/6Q1/8/8/8/8/8 b - - 0 1",
    "single_check": "4k3/8/8/8/8/8/4r3/4K3 w - - 0 1",
    "double_check": "4k3/8/8/8/8/3b4/4r3/4K3 w - - 0 1",
    "pinned_piece": "4k3/8/8/8/4r3/8/4N3/4K3 w - - 0 1",
    "castling_both": "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1",
    "en_passant_legal": "4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 1",
    "en_passant_illegal_pin": "4k3/8/8/r2pP2K/8/8/8/8 w - d6 0 1",
    "promotion_quiet": "4k3/P7/8/8/8/8/8/4K3 w - - 0 1",
    "promotion_capture": "1n2k3/P7/8/8/8/8/8/4K3 w - - 0 1",
    "underpromotion": "4k3/6P1/8/8/8/8/8/4K3 w - - 0 1",
}


PERFT_FIXTURES = {
    "startpos": (START_FEN, {1: 20, 2: 400, 3: 8902}),
    "kiwipete": (
        "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1",
        {1: 48, 2: 2039, 3: 97862},
    ),
    "promotion": ("4k3/P7/8/8/8/8/8/4K3 w - - 0 1", {1: 9, 2: 41, 3: 500}),
}


def command_payload(board: OwnedBoard, args: Any) -> dict[str, object]:
    payload: dict[str, object] = {
        "fen": board.fen(),
        "board": asdict(board) | {"ep_square": None if board.ep_square is None else square_name(board.ep_square)},
        "material_balance": board.material_balance(),
        "side_to_move_material": board.side_to_move_material(),
    }
    if args.square:
        payload["piece_at"] = {args.square: board.piece_at(args.square)}
    if args.pseudo_legal:
        payload["pseudo_legal"] = [move.uci() for move in board.pseudo_legal_moves()]
    if args.legal:
        payload["legal"] = [move.uci() for move in board.legal_moves()]
    if args.compare_oracle:
        payload["oracle_comparison"] = compare_to_oracle(board.fen())
    if args.perft is not None:
        payload["perft"] = owned_perft(board, args.perft)
        payload["oracle_perft"] = oracle_perft(chess.Board(board.fen()), args.perft)
    if args.divide is not None:
        payload["divide"] = owned_divide(board, args.divide)
    return payload


def run_selftest() -> int:
    failures: list[dict[str, object]] = []
    for name, fen in CURATED_FENS.items():
        comparison = compare_to_oracle(fen)
        if not comparison["match"]:
            failures.append({"name": name, **comparison})
    perft_results = []
    for name, (fen, depths) in PERFT_FIXTURES.items():
        board = OwnedBoard.from_fen(fen)
        for depth, expected in depths.items():
            actual = owned_perft(board, depth)
            perft_results.append({"name": name, "depth": depth, "expected": expected, "actual": actual})
            if actual != expected:
                failures.append({"name": name, "depth": depth, "expected": expected, "actual": actual})
    payload = {
        "differential_cases": len(CURATED_FENS),
        "perft_cases": len(perft_results),
        "perft": perft_results,
        "failures": failures,
        "ok": not failures,
    }
    print(json.dumps(payload, indent=2))
    return 0 if not failures else 1
