#!/usr/bin/env python3
"""Runs every SQL solution against its own PostgreSQL database and prints the result.

Usage:
    python3 runner.py            # all tasks
    python3 runner.py 74 93      # selected ids

Datasets are the ones shipped with the Hexlet catalogue (sql/<company>/tests/<id>/*.sql).
Each task gets a fresh database, so INSERT/VIEW tasks cannot leak into each other.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SQL_DIR = ROOT / "sql"
HOST = os.environ.get("PGHOST", "127.0.0.1")
PORT = os.environ.get("PGPORT", "55432")
USER = os.environ.get("PGUSER", "postgres")
PASSWORD = os.environ.get("PGPASSWORD", "pg")


def find_task(task_id: str) -> Path:
    matches = sorted(SQL_DIR.glob(f"*/tests/{task_id}"))
    if not matches:
        raise SystemExit(f"task {task_id} not found under {SQL_DIR}")
    return matches[0]


def psql(database: str, sql: str, file: Path | None = None) -> str:
    env = dict(os.environ, PGPASSWORD=PASSWORD)
    cmd = ["psql", "-X", "-q", "-v", "ON_ERROR_STOP=1", "-h", HOST, "-p", PORT,
           "-U", USER, "-d", database, "-P", "pager=off", "-P", "footer=off"]
    cmd += ["-f", str(file)] if file is not None else ["-c", sql]
    done = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if done.returncode != 0:
        raise RuntimeError(done.stderr.strip() or done.stdout.strip())
    return done.stdout


def run_task(task_id: str, solution: dict) -> str:
    folder = find_task(task_id)
    database = f"task_{task_id}"
    psql("postgres", f'DROP DATABASE IF EXISTS "{database}";')
    psql("postgres", f'CREATE DATABASE "{database}";')
    for schema in sorted(folder.glob("*.sql")):
        psql(database, "", schema)
    return psql(database, solution["sql"])


def main(argv: list[str]) -> int:
    solutions = json.loads((ROOT / "solutions.json").read_text(encoding="utf-8"))
    wanted = argv or sorted(solutions, key=int)
    failures = 0
    for task_id in wanted:
        solution = solutions[task_id]
        print("=" * 78)
        print(f"#{task_id} {solution['title']}")
        print(solution["sql"])
        print("-" * 78)
        try:
            print(run_task(task_id, solution).rstrip())
        except Exception as exc:
            failures += 1
            print(f"ERROR: {exc}")
    print("=" * 78)
    print(f"tasks: {len(wanted)}, failures: {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
