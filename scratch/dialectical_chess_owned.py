# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Small owned chess-state substrate for dialectical chess experiments."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass


PIECE_VALUES = {
    "P": 100,
    "N": 320,
    "B": 330,
    "R": 500,
    "Q": 900,
    "K": 0,
}
FILES = "abcdefgh"


@dataclass(frozen=True)
class OwnedBoard:
    squares: tuple[str | None, ...]
    turn: str
    castling: str
    ep_square: str | None
    halfmove_clock: int
    fullmove_number: int

    @classmethod
    def from_fen(cls, fen: str) -> OwnedBoard:
        fields = fen.split()
        if len(fields) != 6:
            raise ValueError("FEN must contain six fields")
        placement, turn, castling, ep_square, halfmove, fullmove = fields
        if turn not in {"w", "b"}:
            raise ValueError("FEN side-to-move field must be 'w' or 'b'")
        squares = parse_placement(placement)
        return cls(
            squares=squares,
            turn=turn,
            castling=castling,
            ep_square=None if ep_square == "-" else ep_square,
            halfmove_clock=int(halfmove),
            fullmove_number=int(fullmove),
        )

    def piece_at(self, square: str) -> str | None:
        return self.squares[square_index(square)]

    def material_balance(self) -> int:
        white = 0
        black = 0
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


def parse_placement(placement: str) -> tuple[str | None, ...]:
    ranks = placement.split("/")
    if len(ranks) != 8:
        raise ValueError("FEN placement must contain eight ranks")

    squares: list[str | None] = [None] * 64
    for fen_rank_index, rank_text in enumerate(ranks):
        board_rank = 7 - fen_rank_index
        file_index = 0
        for char in rank_text:
            if char.isdigit():
                file_index += int(char)
                continue
            if char.upper() not in PIECE_VALUES:
                raise ValueError(f"unknown FEN piece: {char}")
            if file_index >= 8:
                raise ValueError("too many files in FEN rank")
            squares[board_rank * 8 + file_index] = char
            file_index += 1
        if file_index != 8:
            raise ValueError("FEN rank does not contain eight files")
    return tuple(squares)


def square_index(square: str) -> int:
    if len(square) != 2 or square[0] not in FILES or square[1] not in "12345678":
        raise ValueError(f"invalid square: {square}")
    return (int(square[1]) - 1) * 8 + FILES.index(square[0])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fen")
    parser.add_argument("--square")
    args = parser.parse_args()

    board = OwnedBoard.from_fen(args.fen)
    payload = {
        "board": asdict(board),
        "material_balance": board.material_balance(),
        "side_to_move_material": board.side_to_move_material(),
    }
    if args.square:
        payload["piece_at"] = {args.square: board.piece_at(args.square)}
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
