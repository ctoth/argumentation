"""Profile real benchmark workers with an independent bounded collector."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

from tools import iccma2025_run_native as runner


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--instance", required=True)
    parser.add_argument("--subtrack", required=True)
    parser.add_argument("--seconds", type=int, default=15)
    parser.add_argument("--backend", default="auto")
    args = parser.parse_args()
    binary = shutil.which("py-spy")
    assert binary, "py-spy must be installed"
    args.output.mkdir(parents=True, exist_ok=False)
    manifest_path, task_path = runner.discover_manifest_paths(args.root)
    instance = next(
        i
        for i in runner.load_json(manifest_path)
        if i["relative_path"] == args.instance
    )
    track = "aba" if instance["kind"] == "aba" else "main"
    task = next(
        t
        for t in runner.load_json(task_path)
        if t["track"] == track and t["subtrack"] == args.subtrack
    )
    with tempfile.TemporaryDirectory() as temp:
        pid_path = Path(temp) / "worker.pid"
        job = dict(
            root=str(args.root),
            backend=args.backend,
            iccma_binary=None,
            solver_timeout_seconds=1200,
            event_log_path=str(args.output / "events.jsonl"),
            worker_pid_path=str(pid_path),
            instance=instance,
            task=task,
        )
        job_path = Path(temp) / "job.json"
        job_path.write_text(json.dumps(job))
        (args.output / "job.json").write_text(json.dumps(job, indent=2))
        with (
            (args.output / "stdout.log").open("w") as out,
            (args.output / "stderr.log").open("w") as err,
        ):
            worker = subprocess.Popen(
                [sys.executable, runner.__file__, "_worker", str(job_path)],
                stdout=out,
                stderr=err,
                start_new_session=sys.platform != "win32",
            )
            try:
                deadline = time.monotonic() + 10
                while (
                    not pid_path.exists()
                    and worker.poll() is None
                    and time.monotonic() < deadline
                ):
                    time.sleep(0.01)
                assert pid_path.exists(), "worker PID not published"
                worker_pid = int(pid_path.read_text())
                profile_path = args.output / "profile.json"
                command = [
                    binary,
                    "record",
                    "--pid",
                    str(worker_pid),
                    "--subprocesses",
                    "--rate",
                    "100",
                    "--duration",
                    str(args.seconds),
                    "--format",
                    "speedscope",
                    "--output",
                    str(profile_path),
                ]
                result = subprocess.run(
                    command, capture_output=True, text=True, timeout=args.seconds + 10
                )
                (args.output / "collector.json").write_text(
                    json.dumps(
                        dict(
                            command=command,
                            worker_pid=worker_pid,
                            returncode=result.returncode,
                            stdout=result.stdout,
                            stderr=result.stderr,
                        ),
                        indent=2,
                    )
                )
                assert profile_path.exists(), result.stderr
                profile = json.loads(profile_path.read_text())
                assert any(p.get("samples") for p in profile["profiles"]), (
                    "no actual worker samples"
                )
                print(str(profile_path), flush=True)
            finally:
                runner.kill_worker_tree(worker, job)


if __name__ == "__main__":
    main()
