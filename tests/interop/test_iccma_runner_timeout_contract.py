from __future__ import annotations

import json
import sys

from tools.iccma2025_run_native import RunConfig, run_or_skip


def test_run_or_skip_enforces_configured_worker_timeout(tmp_path, monkeypatch) -> None:
    helper = tmp_path / "slow_solved_worker.py"
    helper.write_text(
        "\n".join(
            [
                "from __future__ import annotations",
                "import json",
                "import time",
                "time.sleep(0.25)",
                'print(json.dumps({"status": "solved", "answer": "true"}))',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    def slow_worker_command(_job, _job_path):
        return [sys.executable, str(helper)]

    monkeypatch.setattr(
        "tools.iccma2025_run_native.build_worker_command",
        slow_worker_command,
    )
    config = RunConfig(
        root=tmp_path,
        backend="auto",
        iccma_binary=None,
        max_af_arguments=100,
        max_aba_assumptions=100,
        timeout_seconds=0.05,
        progress=False,
        event_log_path=None,
    )

    row = run_or_skip(
        config,
        {
            "kind": "apx",
            "relative_path": "case.apx",
            "arguments_or_atoms": 1,
        },
        {
            "track": "contract",
            "subtrack": "SE-CO",
            "instance_kind": "af",
        },
    )

    assert row["status"] == "timeout"
    assert row["reason"] == "timeout>0.05"
    assert float(row["elapsed_seconds"]) < 0.20
