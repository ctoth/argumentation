from __future__ import annotations

import sys
from argparse import Namespace
from io import StringIO
from pathlib import Path

from hypothesis import given
from hypothesis import strategies as st


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


@given(
    dialectic_depth=st.integers(min_value=0, max_value=3),
    search_depth=st.integers(min_value=0, max_value=3),
    search_backend=st.sampled_from(("negamax", "alphabeta")),
    smt_mate=st.booleans(),
)
def test_engine_settings_are_plain_serializable(
    dialectic_depth: int,
    search_depth: int,
    search_backend: str,
    smt_mate: bool,
) -> None:
    from dataclasses import asdict

    from dialectical_chess.engine import EngineSettings

    settings = EngineSettings(
        dialectic_depth=dialectic_depth,
        search_depth=search_depth,
        search_backend=search_backend,
        smt_mate=smt_mate,
    )

    assert asdict(settings) == {
        "dialectic_depth": dialectic_depth,
        "search_depth": search_depth,
        "search_backend": search_backend,
        "smt_mate": smt_mate,
    }


def test_engine_selects_mate_in_one() -> None:
    from dialectical_chess import DialecticalChessEngine as PackageEngine
    from dialectical_chess.engine import DialecticalChessEngine
    from dialectical_chess.probe import owned_board_from_fen

    assert PackageEngine is DialecticalChessEngine
    board = owned_board_from_fen("7k/6pp/8/8/8/8/6PP/R5K1 w - - 0 1")

    decision = DialecticalChessEngine().choose_move(board)

    assert decision.move_uci == "a1a8"
    assert decision.selected is not None
    assert decision.selected.score == 2_001_000
    assert "smt:mate_in_one" in decision.selected.reasons


def test_engine_returns_null_decision_for_no_legal_moves() -> None:
    from dialectical_chess.engine import DialecticalChessEngine
    from dialectical_chess.probe import owned_board_from_fen

    board = owned_board_from_fen("7k/5K2/6Q1/8/8/8/8/8 b - - 0 1")

    decision = DialecticalChessEngine().choose_move(board)

    assert decision.move_uci == "0000"
    assert decision.selected is None


def test_benchmark_adapter_scores_through_engine(monkeypatch) -> None:
    import dialectical_chess.bench as bench
    from dialectical_chess.arguments import MoveProbe
    from dialectical_chess.engine import EngineDecision

    class FakeEngine:
        def __init__(self, settings):
            self.settings = settings

        def choose_move(self, board):
            selected = MoveProbe(
                uci="a1a8",
                san="a1a8",
                score=123,
                is_checkmate=True,
                gives_check=True,
                is_capture=False,
                captured_value=0,
                promotion_value=0,
                reasons=("fake:engine",),
                objections=(),
            )
            return EngineDecision(move_uci="a1a8", selected=selected)

    monkeypatch.setattr(bench, "DialecticalChessEngine", FakeEngine)

    args = Namespace(
        dialectic_depth=1,
        search_depth=0,
        search_backend="negamax",
        smt_mate=True,
    )

    result = bench.score_board(object(), {"a1a8"}, args)

    assert result["selected_uci"] == "a1a8"
    assert result["reasons"] == ["fake:engine"]


def test_uci_adapter_scores_through_engine(monkeypatch) -> None:
    import dialectical_chess.uci as uci
    from dialectical_chess.arguments import MoveProbe
    from dialectical_chess.engine import EngineDecision

    class FakeEngine:
        def __init__(self, settings):
            self.settings = settings

        def choose_move(self, board):
            selected = MoveProbe(
                uci="a1a8",
                san="a1a8",
                score=456,
                is_checkmate=True,
                gives_check=True,
                is_capture=False,
                captured_value=0,
                promotion_value=0,
                reasons=("fake:uci",),
                objections=(),
            )
            return EngineDecision(move_uci="a1a8", selected=selected)

    monkeypatch.setattr(uci, "DialecticalChessEngine", FakeEngine)
    output = StringIO()

    move = uci.choose_uci_move(object(), output_stream=output)

    assert move == "a1a8"
    assert "info score cp 456 pv a1a8" in output.getvalue()
