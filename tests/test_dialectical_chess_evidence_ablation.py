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
    dialectic_depth_for_lichess_row,
    mate_theme_depth,
    run_lichess,
    run_experiment_matrix,
    settings as bench_settings,
    summarize_lichess_rows,
)
from dialectical_chess.probe import owned_board_from_fen, probe_moves  # noqa: E402
from dialectical_chess.engine import EngineSettings  # noqa: E402
from dialectical_chess.engine import DialecticalChessEngine  # noqa: E402
from dialectical_chess.search import (  # noqa: E402
    ReplyAnalysisCache,
    ReplyAnalysisSettings,
    bounded_reply_attacks,
    owned_is_checkmate,
)
from dialectical_chess.smt import smt_fork_moves, smt_mate_in_one_moves  # noqa: E402
from dialectical_chess.uci import choose_uci_move  # noqa: E402


SELECTOR_MODES = ("argument", "score", "grounded", "support", "categoriser", "optimizer")


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


def test_optimizer_selector_prefers_unrefuted_move_over_higher_score() -> None:
    """Optimizer selector should minimize unresolved reply attacks before base score."""
    refuted = MoveProbe(
        uci="h2h4",
        san="h2h4",
        score=999,
        is_checkmate=False,
        gives_check=False,
        is_capture=False,
        captured_value=0,
        promotion_value=0,
        reasons=("development:h2h4:space",),
        objections=(),
        reply_attacks=("reply_captures_moved_piece:undefended:h2h4:100",),
    )
    quiet = MoveProbe(
        uci="g2g3",
        san="g2g3",
        score=10,
        is_checkmate=False,
        gives_check=False,
        is_capture=False,
        captured_value=0,
        promotion_value=0,
        reasons=("development:g2g3:space",),
        objections=(),
    )
    probes = [refuted, quiet]
    graph = build_root_argument_graph(probes)

    selected = choose_move(probes, graph, selector_mode="optimizer")

    assert selected.uci == quiet.uci
    assert selected.optimizer_trace["status"] == "optimal"


def test_argument_selector_prefers_tactical_support_over_positional_count() -> None:
    """Mined positional deltas show shallow support counts can bury tactical moves."""
    positional = quiet_probe(
        "d4d1",
        75,
        (
            "center_control:d4d1:2",
            "piece_activity:d4d1:mobility_gain:1",
            "file_control:d4d1:open_file",
        ),
    )
    tactical = MoveProbe(
        uci="e5f6",
        san="e5f6",
        score=500,
        is_checkmate=False,
        gives_check=False,
        is_capture=True,
        captured_value=500,
        promotion_value=0,
        reasons=("material:capture:500",),
        objections=(),
    )
    probes = [positional, tactical]
    graph = build_root_argument_graph(probes)

    selected = choose_move(probes, graph, selector_mode="argument")

    assert selected.uci == "e5f6"


@pytest.mark.parametrize(
    ("puzzle_id", "fen", "expected_uci"),
    [
        (
            "000Zo",
            "4r3/1k6/pp3r2/1b2P2p/3R1p2/P1R2P2/1P4PP/6K1 w - - 0 35",
            "e5f6",
        ),
        (
            "00B3B",
            "2K5/3P4/5b2/p1B5/P7/3k4/6p1/8 w - - 7 77",
            "d7d8q",
        ),
    ],
)
def test_argument_d2_solves_mined_positional_regressions(
    puzzle_id: str,
    fen: str,
    expected_uci: str,
) -> None:
    assert puzzle_id
    board = owned_board_from_fen(fen)

    decision = DialecticalChessEngine(
        EngineSettings(
            selector_mode="argument",
            dialectic_depth=2,
            positional_reasons=True,
        )
    ).choose_move(board)

    assert decision.move_uci == expected_uci


@pytest.mark.parametrize(
    ("puzzle_id", "fen", "expected_uci", "rejected_uci"),
    [
        (
            "002IE",
            "r3brk1/5pp1/p1nqpn1p/P2pN3/2pP4/2P1PN2/5PPP/RB1QK2R b KQ - 4 16",
            "c6e5",
            "d6e5",
        ),
        (
            "00H1C",
            "r3r3/1kpRnqpp/p4p2/Qp2P2P/1N6/4Pb2/PPP3P1/2K2R2 b - - 0 22",
            None,
            "f7h5",
        ),
    ],
)
def test_optimizer_d2_solves_mined_positional_regressions(
    puzzle_id: str,
    fen: str,
    expected_uci: str | None,
    rejected_uci: str,
) -> None:
    assert puzzle_id
    board = owned_board_from_fen(fen)

    baseline = DialecticalChessEngine(
        EngineSettings(
            selector_mode="optimizer",
            dialectic_depth=2,
            positional_reasons=False,
        )
    ).choose_move(board)

    decision = DialecticalChessEngine(
        EngineSettings(
            selector_mode="optimizer",
            dialectic_depth=2,
            positional_reasons=True,
        )
    ).choose_move(board)

    if expected_uci is not None:
        assert decision.move_uci == expected_uci
    assert baseline.move_uci != rejected_uci
    assert decision.move_uci != rejected_uci
    assert decision.selected is not None
    assert decision.selected.optimizer_trace["status"] == "optimal"
    assert "positional_support_effective" in decision.selected.optimizer_trace["objective_values"]
    assert decision.selected.optimizer_trace["positional_support_mode"] in {
        "quiet",
        "tactical_gated",
        "disabled",
    }


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


def test_lichess_sample_summary_reports_move_line_lengths_and_mate_themes() -> None:
    rows = [
        {"Moves": "a1a8", "Themes": "mate mateIn1"},
        {"Moves": "e2e4 e7e5 g1f3", "Themes": "opening middlegame"},
        {"Moves": "h5f7 e8f7", "Themes": "mate mateIn2"},
    ]

    summary = summarize_lichess_rows(rows)

    assert summary["line_move_counts"] == {"1": 1, "2": 1, "3": 1}
    assert summary["mate_theme_counts"] == {"mateIn1": 1, "mateIn2": 1}
    assert summary["scoring_target"] == "first engine move only"


def test_mate_theme_depth_parses_mate_in_names() -> None:
    assert mate_theme_depth(("mate", "mateIn1", "oneMove")) == 1
    assert mate_theme_depth(("mateIn3", "long")) == 3
    assert mate_theme_depth(("crushing", "fork")) is None


def test_lichess_row_can_use_mate_theme_as_dialectic_depth() -> None:
    args = argparse.Namespace(dialectic_depth=2, dialectic_depth_from_mate_theme=True)

    assert dialectic_depth_for_lichess_row({"Themes": "mate mateIn3"}, args) == 3
    assert dialectic_depth_for_lichess_row({"Themes": "crushing fork"}, args) == 2


def test_experiment_matrix_runs_named_lichess_cases() -> None:
    args = argparse.Namespace(
        lichess_puzzles=SCRIPTS / "dialectical_chess_puzzles_sample.csv",
        limit=2,
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
        selector_mode_ablation=False,
        positional_reasons=True,
        progress_every=0,
        matrix_preset="smoke",
        dialectic_depth_from_mate_theme=False,
        reply_max_replies=128,
        reply_max_defense_nodes=5000,
        reply_min_defense_material=300,
    )

    payload = run_experiment_matrix(args)

    assert payload["mode"] == "lichess_experiment_matrix"
    assert [run["name"] for run in payload["runs"]] == [
        "argument_d0",
        "argument_d1",
        "score_static",
        "argument_mate_theme_depth",
    ]
    assert payload["sample"]["total"] == 2


def test_core_experiment_matrix_includes_optimizer_rows() -> None:
    from dialectical_chess.bench import experiment_matrix_cases

    names = {case["name"] for case in experiment_matrix_cases("core")}

    assert {
        "optimizer_static",
        "optimizer_d2",
        "optimizer_d2_no_positional",
        "optimizer_mate_theme_depth",
    } <= names
