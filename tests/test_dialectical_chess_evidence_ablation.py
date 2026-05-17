from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from dialectical_chess.arguments import (  # noqa: E402
    MoveProbe,
    build_root_argument_graph,
    choose_move,
)
from dialectical_chess.bench import (  # noqa: E402
    ablation_selector_modes,
    run_lichess,
    settings as bench_settings,
)
from dialectical_chess.probe import owned_board_from_fen, probe_moves  # noqa: E402
from dialectical_chess.engine import EngineSettings  # noqa: E402
from dialectical_chess.search import (  # noqa: E402
    ReplyAnalysisCache,
    ReplyAnalysisSettings,
    bounded_reply_attacks,
    owned_is_checkmate,
)
from dialectical_chess.smt import smt_fork_moves, smt_mate_in_one_moves  # noqa: E402
from dialectical_chess.uci import choose_uci_move  # noqa: E402


SELECTOR_MODES = ("argument", "score", "grounded", "support", "categoriser")


def quiet_probe(uci: str, score: int, reasons: tuple[str, ...] = ()) -> MoveProbe:
    return MoveProbe(
        uci=uci,
        san=uci,
        score=score,
        is_checkmate=False,
        gives_check=False,
        is_capture=False,
        captured_value=0,
        promotion_value=0,
        reasons=reasons,
        objections=() if reasons else ("objection:no_immediate_tactical_warrant",),
    )


def test_score_selector_ignores_argument_support() -> None:
    supported = quiet_probe("a2a3", 10, ("development:minor_piece",))
    high_score = quiet_probe("h2h4", 100)
    probes = [supported, high_score]

    graph = build_root_argument_graph(probes)

    assert choose_move(probes, graph, selector_mode="argument") == supported
    assert choose_move(probes, graph, selector_mode="score") == high_score


@given(st.sampled_from(SELECTOR_MODES))
def test_engine_settings_accept_supported_selector_modes(mode: str) -> None:
    settings = EngineSettings(selector_mode=mode)

    assert settings.selector_mode == mode


def test_engine_settings_reject_unknown_selector_mode() -> None:
    with pytest.raises(ValueError, match="selector_mode"):
        EngineSettings(selector_mode="unknown")


def test_bench_settings_report_selector_mode() -> None:
    args = argparse.Namespace(
        dialectic_depth=1,
        search_depth=2,
        search_backend="alphabeta",
        smt_mate=False,
        selector_mode="support",
        positional_reasons=False,
    )

    assert bench_settings(args)["selector_mode"] == "support"
    assert bench_settings(args)["positional_reasons"] is False


def test_ablation_selector_modes_are_explicitly_gated() -> None:
    default_args = argparse.Namespace(selector_mode="argument", selector_mode_ablation=False)
    ablation_args = argparse.Namespace(selector_mode="argument", selector_mode_ablation=True)

    assert ablation_selector_modes(default_args) == ("argument",)
    assert set(ablation_selector_modes(ablation_args)) == set(SELECTOR_MODES)


def test_uci_info_reports_selector_mode() -> None:
    board = owned_board_from_fen("7k/6pp/8/8/8/8/6PP/R5K1 w - - 0 1")
    output = io.StringIO()

    choose_uci_move(board, settings=EngineSettings(selector_mode="score"), output_stream=output)

    assert "info string selector_mode=score" in output.getvalue()


def test_lichess_summary_reports_rating_bucket_totals() -> None:
    args = argparse.Namespace(
        lichess_puzzles=SCRIPTS / "dialectical_chess_puzzles_sample.csv",
        limit=None,
        rating_min=None,
        rating_max=None,
        theme_include=[],
        theme_exclude=[],
        side_to_move=None,
        full_line=False,
        dialectic_depth=1,
        search_depth=0,
        search_backend="negamax",
        smt_mate=True,
        selector_mode="argument",
        progress_every=0,
    )

    payload = run_lichess(args)

    assert payload["by_rating_bucket"]["800-999"]["total"] == 1
    assert payload["by_rating_bucket"]["1200-1399"]["total"] == 1


def test_lichess_runner_reports_progress(capsys: pytest.CaptureFixture[str]) -> None:
    args = argparse.Namespace(
        lichess_puzzles=SCRIPTS / "dialectical_chess_puzzles_sample.csv",
        limit=None,
        rating_min=None,
        rating_max=None,
        theme_include=[],
        theme_exclude=[],
        side_to_move=None,
        full_line=False,
        dialectic_depth=1,
        search_depth=0,
        search_backend="negamax",
        smt_mate=True,
        selector_mode="argument",
        positional_reasons=True,
        progress_every=1,
    )

    run_lichess(args)

    captured = capsys.readouterr()
    assert "progress lichess_csv 1/2" in captured.err
    assert "progress lichess_csv 2/2" in captured.err


def test_mate_in_one_smt_scaffold_matches_procedural_checker() -> None:
    board = owned_board_from_fen("7k/6pp/8/8/8/8/6PP/R5K1 w - - 0 1")
    procedural_moves = frozenset(
        move.uci()
        for move in board.legal_moves()
        if owned_is_checkmate(board.apply(move))
    )

    assert smt_mate_in_one_moves(board) == procedural_moves


def test_smt_fork_witness_finds_knight_fork() -> None:
    board = owned_board_from_fen("r3k3/8/8/1N6/8/8/8/4K3 w - - 0 1")

    assert "b5c7" in smt_fork_moves(board)

    fork_probe = next(probe for probe in probe_moves(board) if probe.uci == "b5c7")
    assert "smt:fork:2:500" in fork_probe.reasons
    assert "fork" in fork_probe.smt_witnesses


def test_positional_reasons_cover_quiet_opening_development() -> None:
    board = owned_board_from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    probes = {probe.uci: probe for probe in probe_moves(board)}

    assert "development:e2e4:center_pawn" in probes["e2e4"].reasons
    assert "center_control:e2e4:1" in probes["e2e4"].reasons
    assert "objection:no_immediate_tactical_warrant" not in probes["e2e4"].objections
    assert "development:g1f3:minor_piece" in probes["g1f3"].reasons
    assert "piece_activity:g1f3:mobility_gain:5" in probes["g1f3"].reasons


def test_positional_reasons_cover_castling_king_safety() -> None:
    board = owned_board_from_fen("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
    probes = {probe.uci: probe for probe in probe_moves(board)}

    assert "king_safety:e1g1:castle" in probes["e1g1"].reasons


def test_positional_reasons_cover_passed_pawn_structure() -> None:
    board = owned_board_from_fen("4k3/8/8/8/4P3/8/8/4K3 w - - 0 1")
    probes = {probe.uci: probe for probe in probe_moves(board)}

    assert "pawn_structure:e4e5:passed_pawn" in probes["e4e5"].reasons


def test_engine_settings_can_disable_positional_reasons() -> None:
    from dialectical_chess.engine import DialecticalChessEngine

    board = owned_board_from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    analysis = DialecticalChessEngine(EngineSettings(positional_reasons=False)).analyze(board)
    probes = {probe.uci: probe for probe in analysis.probes}

    assert probes["e2e4"].reasons == ()
    assert probes["e2e4"].objections == ("objection:no_immediate_tactical_warrant",)


def test_reply_analysis_cache_reuses_legal_moves_locally() -> None:
    board = owned_board_from_fen("4k3/8/8/8/8/8/3q4/3QK3 w - - 0 1")
    cache = ReplyAnalysisCache()

    first = cache.legal_moves(board)
    second = cache.legal_moves(board)

    assert first is second
    assert cache.legal_move_misses == 1
    assert cache.legal_move_hits == 1


def test_engine_settings_include_reply_analysis_settings() -> None:
    settings = EngineSettings(
        reply_analysis=ReplyAnalysisSettings(max_replies=7, max_defense_nodes=11)
    )

    assert settings.reply_analysis.max_replies == 7
    assert settings.reply_analysis.max_defense_nodes == 11


def test_reply_analysis_reports_budget_truncation() -> None:
    board = owned_board_from_fen("4k3/8/8/8/8/8/3q4/3QK3 w - - 0 1")
    move = next(move for move in board.legal_moves() if move.uci() == "d1d2")

    labels = bounded_reply_attacks(
        board,
        move,
        reply_depth=2,
        settings=ReplyAnalysisSettings(max_replies=0, max_defense_nodes=0),
    )

    assert "reply_analysis:truncated:reply_budget" in labels
