from __future__ import annotations

from argumentation import iccma_cli
from argumentation.labelling import ExactEnumerationExceeded


def test_iccma_cli_prints_single_extension(tmp_path, capsys) -> None:
    path = tmp_path / "instance.af"
    path.write_text("p af 2\n1 2\n", encoding="utf-8")

    status = iccma_cli.main(["-p", "SE-ST", "-f", str(path)])

    captured = capsys.readouterr()
    assert status == 0
    assert captured.out == "w 1\n"
    assert captured.err == ""


def test_iccma_cli_prints_credulous_yes_certificate(tmp_path, capsys) -> None:
    path = tmp_path / "instance.af"
    path.write_text("p af 2\n1 2\n", encoding="utf-8")

    status = iccma_cli.main(["-p", "DC-ST", "-f", str(path), "-a", "1"])

    captured = capsys.readouterr()
    assert status == 0
    assert captured.out == "YES\nw 1\n"
    assert captured.err == ""


def test_iccma_cli_prints_skeptical_no_counterexample(tmp_path, capsys) -> None:
    path = tmp_path / "instance.af"
    path.write_text("p af 2\n1 2\n", encoding="utf-8")

    status = iccma_cli.main(["-p", "DS-ST", "-f", str(path), "-a", "2"])

    captured = capsys.readouterr()
    assert status == 0
    assert captured.out == "NO\nw 1\n"
    assert captured.err == ""


def test_iccma_cli_rejects_acceptance_without_query(tmp_path, capsys) -> None:
    path = tmp_path / "instance.af"
    path.write_text("p af 1\n", encoding="utf-8")

    status = iccma_cli.main(["-p", "DC-ST", "-f", str(path)])

    captured = capsys.readouterr()
    assert status == 2
    assert captured.out == ""
    assert captured.err == "DC tasks require -a/--argument\n"


def test_iccma_cli_reports_exact_enumeration_limits(
    tmp_path,
    capsys,
    monkeypatch,
) -> None:
    path = tmp_path / "instance.af"
    path.write_text("p af 1\n", encoding="utf-8")

    def fake_solve_single_extension(*args, **kwargs):
        raise ExactEnumerationExceeded("too many candidate subsets")

    monkeypatch.setattr(
        "argumentation.iccma_cli.solve_dung_single_extension",
        fake_solve_single_extension,
    )

    status = iccma_cli.main(["-p", "SE-ST", "-f", str(path)])

    captured = capsys.readouterr()
    assert status == 2
    assert captured.out == ""
    assert captured.err == "too many candidate subsets\n"
