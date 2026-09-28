from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from tools import iccma2025_run_native as runner


def test_timeout_dump_targets_worker_and_has_bounded_collection(tmp_path, monkeypatch):
    worker_pid = tmp_path / "worker.pid"
    worker_pid.write_text("456")
    job = {"root": str(tmp_path), "worker_pid_path": str(worker_pid)}
    calls = []
    monkeypatch.setattr(runner.shutil, "which", lambda _: "py-spy")

    def collect(command, **kwargs):
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0, "solver_hot_frame", "")

    monkeypatch.setattr(runner.subprocess, "run", collect)
    result = runner.capture_timeout_diagnostics(job, supervisor_pid=123)
    evidence = json.loads(Path(result["diagnostic_path"]).read_text())
    assert evidence["worker_pid"] == 456
    assert evidence["status"] == "captured"
    assert evidence["stdout"] == "solver_hot_frame"
    assert calls[0][0] == ["py-spy", "dump", "--pid", "456", "--subprocesses"]
    assert calls[0][1]["timeout"] == 2.0


@pytest.mark.parametrize("failure", ["missing", "hung", "denied"])
def test_diagnostic_failure_is_persisted(tmp_path, monkeypatch, failure):
    monkeypatch.setattr(
        runner.shutil, "which", lambda _: None if failure == "missing" else "py-spy"
    )

    def collect(command, **kwargs):
        if failure == "hung":
            raise subprocess.TimeoutExpired(command, kwargs["timeout"])
        return subprocess.CompletedProcess(command, 1, "", "access denied")

    monkeypatch.setattr(runner.subprocess, "run", collect)
    result = runner.capture_timeout_diagnostics(
        {"root": str(tmp_path)}, supervisor_pid=123
    )
    evidence = json.loads(Path(result["diagnostic_path"]).read_text())
    assert evidence["status"] != "captured"
    assert evidence["error"]


def test_timeout_collects_before_kill_and_reaps_even_when_dump_fails(
    tmp_path, monkeypatch
):
    from io import StringIO

    calls = []

    class Process:
        pid = 123
        stdout = StringIO("")
        stderr = StringIO("")

        def wait(self, timeout):
            calls.append(("wait", timeout))
            if len(calls) == 1:
                raise subprocess.TimeoutExpired("worker", timeout)
            return -1

        def kill(self):
            calls.append(("kill",))

    monkeypatch.setattr(runner.subprocess, "Popen", lambda *a, **kw: Process())
    monkeypatch.setattr(runner, "build_worker_command", lambda *a: ["worker"])

    def dump(*a, **kw):
        calls.append(("dump",))
        raise OSError("disk unavailable")

    def kill(process, job):
        calls.append(("kill_tree",))
        process.kill()
        process.wait(timeout=2.0)

    monkeypatch.setattr(runner, "capture_timeout_diagnostics", dump)
    monkeypatch.setattr(runner, "kill_worker_tree", kill)
    result = runner.run_child({"root": str(tmp_path)}, timeout_seconds=5)
    assert result["status"] == "timeout"
    assert "disk unavailable" in result["diagnostic_error"]
    assert [call[0] for call in calls] == ["wait", "dump", "kill_tree", "kill", "wait"]


def test_profile_wrapper_without_worker_pid_does_not_dump_the_wrapper(
    tmp_path, monkeypatch
):
    def unexpected(*a, **kw):
        pytest.fail("must not profile the wrapper as though it were the worker")

    monkeypatch.setattr(runner.subprocess, "run", unexpected)
    result = runner.capture_timeout_diagnostics(
        {"root": str(tmp_path), "profile_path": "profile.json"}, supervisor_pid=123
    )
    assert "did not publish its PID" in result["diagnostic_error"]


def test_windows_tree_cleanup_is_bounded_and_reaps_after_failure(monkeypatch):
    calls = []

    class Process:
        pid = 123

        def kill(self):
            calls.append("kill")

        def wait(self, timeout):
            calls.append(("reap", timeout))

    def tree_kill(command, **kwargs):
        calls.append((command, kwargs["timeout"]))
        raise subprocess.TimeoutExpired(command, kwargs["timeout"])

    with monkeypatch.context() as patch:
        patch.setattr(runner.os, "name", "nt")
        patch.setattr(runner.subprocess, "run", tree_kill)
        with pytest.raises(subprocess.TimeoutExpired):
            runner.kill_worker_tree(Process(), {})
    assert calls == [
        (["taskkill", "/PID", "123", "/T", "/F"], 2.0),
        "kill",
        ("reap", 2.0),
    ]


def test_posix_cleanup_kills_process_group_and_reaps(monkeypatch):
    calls = []

    class Process:
        pid = 123

        def kill(self):
            calls.append("kill")

        def wait(self, timeout):
            calls.append(("reap", timeout))

    with monkeypatch.context() as patch:
        patch.setattr(runner.os, "name", "posix")
        patch.setattr(
            runner.os,
            "killpg",
            lambda pid, sig: calls.append(("group", pid)),
            raising=False,
        )
        # SIGKILL is absent on Windows, where this contract also runs.
        patch.setattr(runner.signal, "SIGKILL", 9, raising=False)
        runner.kill_worker_tree(Process(), {})
    assert calls == [("group", 123), "kill", ("reap", 2.0)]


@pytest.mark.skipif(
    os.environ.get("ICCMA_DIAGNOSTIC_INTEGRATION") != "1" or not shutil.which("py-spy"),
    reason="opt-in real py-spy attachment: ICCMA_DIAGNOSTIC_INTEGRATION=1",
)
def test_real_worker_stack_is_saved_before_termination(tmp_path, monkeypatch):
    helper = tmp_path / "diagnostic_worker.py"
    helper.write_text(
        "import json, os, pathlib, sys, time\n"
        "job = json.loads(pathlib.Path(sys.argv[1]).read_text())\n"
        'pathlib.Path(job["worker_pid_path"]).write_text(str(os.getpid()))\n'
        "def diagnostic_target():\n"
        "    while True: time.sleep(0.01)\n"
        "diagnostic_target()\n"
    )
    monkeypatch.setattr(
        runner,
        "build_worker_command",
        lambda job, path: [sys.executable, str(helper), str(path)],
    )
    processes = []
    original = runner.subprocess.Popen

    def launch(command, **kwargs):
        process = original(command, **kwargs)
        if command[0] == sys.executable:
            processes.append(process)
        return process

    monkeypatch.setattr(runner.subprocess, "Popen", launch)
    result = runner.run_child({"root": str(tmp_path)}, timeout_seconds=2)
    assert result["status"] == "timeout"
    assert result["diagnostic_error"] is None
    evidence = json.loads(Path(result["diagnostic_path"]).read_text())
    assert evidence["status"] == "captured"
    assert "diagnostic_target" in evidence["stdout"]
    assert len(processes) == 1 and processes[0].poll() is not None
