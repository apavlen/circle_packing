#!/usr/bin/env python3
"""Zero-Darwin worker that runs the repo's own unit test and reports the score.

This script imports NOTHING from Darwin. It runs the candidate repo's test
suite (which writes ``metrics.json`` as a side effect), reads that file, and
emits a JSON document that validates against Darwin's ``RunResult`` model so the
existing ``RestGithubActionsClient`` can parse it unchanged.

Wire contract (all via environment):
  DARWIN_JOB           serialized EvaluationJob JSON (optional; supplies the
                       test command via evaluator.commands)
  DARWIN_RUN_ID        the run id the coordinator is awaiting (required)
  DARWIN_CANDIDATE_DIR directory to run the tests in (default: cwd)
  DARWIN_RESULT_PATH   where to write the RunResult JSON
                       (default: run-result-<run_id>.json)

Outcome semantics:
  * metrics.json produced with combined_score -> COMPLETED (even if the unit
    test went red: an invalid packing is a low score, not an infra failure).
  * test command times out                    -> TIMED_OUT.
  * no metrics.json / unexpected crash         -> FAILED.
"""

import json
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path

WORKER_ID = "circle-packing-test-runner"
DEFAULT_COMMANDS = ["python -m unittest discover -v"]
METRICS_FILE = "metrics.json"
DEFAULT_TIMEOUT_S = 120
LOG_TRUNCATE_CHARS = 4000


def _telemetry(t0, logs):
    return {
        "duration_s": time.monotonic() - t0,
        "resource_samples": [],
        "logs": logs[-LOG_TRUNCATE_CHARS:] if logs else None,
    }


def _result(run_id, outcome, payload, error, t0, logs):
    return {
        "run_id": run_id,
        "outcome": outcome,
        "payload": payload,
        "error": error,
        "telemetry": _telemetry(t0, logs),
        "worker_id": WORKER_ID,
    }


def main():
    run_id = os.environ.get("DARWIN_RUN_ID")
    if not run_id:
        print("DARWIN_RUN_ID must be set", file=sys.stderr)
        return 2

    candidate_dir = Path(os.environ.get("DARWIN_CANDIDATE_DIR") or os.getcwd())
    result_path = Path(
        os.environ.get("DARWIN_RESULT_PATH") or f"run-result-{run_id}.json"
    )

    commands = DEFAULT_COMMANDS
    timeout_s = DEFAULT_TIMEOUT_S
    job_raw = os.environ.get("DARWIN_JOB")
    if job_raw:
        try:
            job = json.loads(job_raw)
            evaluator = job.get("evaluator") or {}
            if evaluator.get("commands"):
                commands = list(evaluator["commands"])
            if job.get("timeout_s"):
                timeout_s = float(job["timeout_s"])
        except (ValueError, TypeError) as exc:
            print(f"could not parse DARWIN_JOB, using defaults: {exc}", file=sys.stderr)

    t0 = time.monotonic()
    logs = ""
    try:
        for cmd in commands:
            # No shell=True: the command is coordinator-controlled and split
            # with shlex so a candidate repo cannot inject shell metacharacters.
            proc = subprocess.run(
                shlex.split(cmd),
                cwd=str(candidate_dir),
                capture_output=True,
                text=True,
                timeout=timeout_s,
            )
            logs += f"$ {cmd}\n{proc.stdout}{proc.stderr}\n[exit {proc.returncode}]\n"

        metrics_path = candidate_dir / METRICS_FILE
        if not metrics_path.exists():
            # The unit test never produced a score -> the program crashed before
            # setUpClass finished, which is an evaluation failure, not a 0 score.
            raise RuntimeError(
                f"unit test did not produce {METRICS_FILE}; the program likely "
                f"crashed.\n{logs}"
            )

        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))["metrics"]
        if "combined_score" not in metrics:
            raise RuntimeError(f"{METRICS_FILE} is missing combined_score: {metrics}")

        payload = {"metrics": metrics, "artifacts": []}
        document = _result(run_id, "completed", payload, None, t0, logs)
    except subprocess.TimeoutExpired:
        document = _result(
            run_id, "timed_out", None, f"test command exceeded {timeout_s}s", t0, logs
        )
    except Exception as exc:  # noqa: BLE001 - any failure here is a FAILED run
        document = _result(run_id, "failed", None, f"{type(exc).__name__}: {exc}", t0, logs)

    result_path.write_text(json.dumps(document, indent=2), encoding="utf-8")
    print(f"wrote {result_path} (outcome={document['outcome']})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
