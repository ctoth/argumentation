from __future__ import annotations

import json

from tools.iccma_run_selected import run_selected


def test_run_selected_executes_single_iccma_row(tmp_path) -> None:
    instance_path = tmp_path / "extracted" / "instances" / "case.apx"
    instance_path.parent.mkdir(parents=True)
    instance_path.write_text("arg(a).\narg(b).\natt(a,b).\n", encoding="utf-8")

    row = run_selected(
        root=tmp_path,
        relative_path="case.apx",
        kind="apx",
        subtrack="SE-STG",
        backend="auto",
        timeout_seconds=15.0,
        arguments_or_atoms=2,
    )

    assert row["status"] == "solved"
    assert json.loads(json.dumps(row)) == row
