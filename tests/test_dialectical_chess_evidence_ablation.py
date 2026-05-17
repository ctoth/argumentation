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
from dialectical_chess.bench import ablation_selector_modes, settings as bench_settings  # noqa: E402
from dialectical_chess.probe import owned_board_from_fen  # noqa: E402
from dialectical_chess.engine import EngineSettings  # noqa: E402
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
    )

    assert bench_settings(args)["selector_mode"] == "support"


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
