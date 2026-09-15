#!/usr/bin/env python3
"""Qualify historical compiler-regression cases before corpus freeze."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

from regression_evidence_protocol import ProtocolError, load_corpus

QUALIFICATION_SCHEMA = "weave-loupe-regression-qualification-v1"
OUTPUT_LIMIT = 4096


def _run(
    command: list[str],
    *,
    cwd: Path,
    timeout_seconds: int,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    started = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            check=False,
            capture_output=True,
            timeout=timeout_seconds,
            env=env,
        )
        returncode = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        returncode = None
        stdout = exc.stdout or b""
        stderr = exc.stderr or b""
        timed_out = True
    elapsed = time.monotonic() - started
    return {
        "command": command,
        "returncode": returncode,
        "timed_out": timed_out,
        "seconds": elapsed,
        "stdout_sha256": hashlib.sha256(stdout).hexdigest(),
        "stderr_sha256": hashlib.sha256(stderr).hexdigest(),
        "stdout_tail": stdout[-OUTPUT_LIMIT:].decode("utf-8", errors="replace"),
        "stderr_tail": stderr[-OUTPUT_LIMIT:].decode("utf-8", errors="replace"),
    }


def _worktree_add(repo: Path, revision: str, destination: Path) -> None:
    command = [
        "git",
        "-C",
        str(repo),
        "worktree",
        "add",
        "--detach",
        str(destination),
        revision,
    ]
    subprocess.run(
        command,
        check=True,
        capture_output=True,
    )


def _worktree_remove(repo: Path, destination: Path) -> None:
    subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "worktree",
            "remove",
            "--force",
            str(destination),
        ],
        check=False,
        capture_output=True,
    )


def _resolve_oracle_command(
    command: list[str],
    oracle_root: Path | None,
) -> list[str]:
    if oracle_root is None:
        return command
    resolved: list[str] = []
    for item in command:
        candidate = oracle_root / item
        if not Path(item).is_absolute() and candidate.exists():
            resolved.append(str(candidate.resolve()))
        else:
            resolved.append(item)
    return resolved


def _require_compiler_build(case: dict[str, Any]) -> bool:
    qualification = case.get("qualification")
    if not isinstance(qualification, dict):
        return True
    required = qualification.get("require_compiler_build", True)
    if not isinstance(required, bool):
        raise ProtocolError(
            f"case {case.get('id')}: qualification.require_compiler_build "
            "must be a boolean"
        )
    return required


def _qualify_arm(
    *,
    repo: Path,
    revision: str,
    worktree: Path,
    oracle_command: list[str],
    oracle_cwd: Path,
    require_compiler_build: bool,
    build_timeout_seconds: int,
    oracle_timeout_seconds: int,
) -> dict[str, Any]:
    _worktree_add(repo, revision, worktree)
    try:
        env = os.environ.copy()
        env["WEAVEC_ROOT"] = str(worktree)
        env["WEAVEC"] = str(worktree / "build" / "weavec")
        if require_compiler_build:
            build = _run(
                ["bash", "scripts/build.sh"],
                cwd=worktree,
                timeout_seconds=build_timeout_seconds,
            )
            build_ok = build["returncode"] == 0 and not build["timed_out"]
        else:
            build = {
                "command": ["bash", "scripts/build.sh"],
                "returncode": 0,
                "timed_out": False,
                "seconds": 0.0,
                "skipped": True,
            }
            build_ok = True
        oracle: dict[str, Any] | None = None
        if build_ok:
            oracle = _run(
                oracle_command,
                cwd=oracle_cwd,
                timeout_seconds=oracle_timeout_seconds,
                env=env,
            )
        return {
            "revision": revision,
            "build": build,
            "oracle": oracle,
        }
    finally:
        _worktree_remove(repo, worktree)


def qualify_corpus(
    corpus: dict[str, Any],
    *,
    weavec_repo: Path,
    oracle_root: Path | None = None,
    build_timeout_seconds: int = 900,
    oracle_timeout_seconds: int = 120,
) -> dict[str, Any]:
    repo = weavec_repo.resolve()
    if not (repo / ".git").exists():
        raise ProtocolError(f"weavec repository is not a git checkout: {repo}")
    resolved_oracle_root = oracle_root.resolve() if oracle_root is not None else None

    rows: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="loupe-regression-qualify-") as raw_tmp:
        root = Path(raw_tmp)
        for index, case in enumerate(corpus["cases"]):
            case_id = str(case["id"])
            require_build = _require_compiler_build(case)
            oracle_command = _resolve_oracle_command(
                [str(item) for item in case["oracle"]["command"]],
                resolved_oracle_root,
            )
            if resolved_oracle_root is not None:
                shared_oracle_cwd: Path | None = resolved_oracle_root
            else:
                shared_oracle_cwd = None
            bad_path = root / f"{index:03d}-bad"
            good_path = root / f"{index:03d}-good"
            try:
                bad = _qualify_arm(
                    repo=repo,
                    revision=str(case["bad_revision"]),
                    worktree=bad_path,
                    oracle_command=oracle_command,
                    oracle_cwd=(
                        shared_oracle_cwd if shared_oracle_cwd is not None else bad_path
                    ),
                    require_compiler_build=require_build,
                    build_timeout_seconds=build_timeout_seconds,
                    oracle_timeout_seconds=oracle_timeout_seconds,
                )
                good = _qualify_arm(
                    repo=repo,
                    revision=str(case["good_revision"]),
                    worktree=good_path,
                    oracle_command=oracle_command,
                    oracle_cwd=(
                        shared_oracle_cwd
                        if shared_oracle_cwd is not None
                        else good_path
                    ),
                    require_compiler_build=require_build,
                    build_timeout_seconds=build_timeout_seconds,
                    oracle_timeout_seconds=oracle_timeout_seconds,
                )
                bad_oracle = bad["oracle"]
                good_oracle = good["oracle"]
                qualified = bool(
                    bad["build"]["returncode"] == 0
                    and good["build"]["returncode"] == 0
                    and bad_oracle is not None
                    and good_oracle is not None
                    and not bad_oracle["timed_out"]
                    and not good_oracle["timed_out"]
                    and bad_oracle["returncode"] != 0
                    and good_oracle["returncode"] == 0
                )
                rows.append(
                    {
                        "case_id": case_id,
                        "qualified": qualified,
                        "bad": bad,
                        "good": good,
                    }
                )
            except (OSError, subprocess.CalledProcessError) as exc:
                rows.append(
                    {
                        "case_id": case_id,
                        "qualified": False,
                        "infrastructure_error": str(exc),
                    }
                )

    return {
        "schema": QUALIFICATION_SCHEMA,
        "corpus_sha256": corpus["corpus_sha256"],
        "compiler_repository": corpus["compiler"]["repository"],
        "case_count": len(rows),
        "qualified_count": sum(bool(row["qualified"]) for row in rows),
        "all_qualified": all(bool(row["qualified"]) for row in rows),
        "rows": rows,
    }


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("corpus", type=Path)
    parser.add_argument("--weavec-repo", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--oracle-root",
        type=Path,
        default=None,
        help="Resolve independent oracle commands relative to this tree",
    )
    parser.add_argument("--build-timeout-seconds", type=int, default=900)
    parser.add_argument("--oracle-timeout-seconds", type=int, default=300)
    args = parser.parse_args()

    if shutil.which("git") is None:
        parser.error("git is required")
    corpus = load_corpus(args.corpus, require_frozen=False)
    result = qualify_corpus(
        corpus,
        weavec_repo=args.weavec_repo,
        oracle_root=args.oracle_root,
        build_timeout_seconds=args.build_timeout_seconds,
        oracle_timeout_seconds=args.oracle_timeout_seconds,
    )
    _write_json(args.output, result)
    return 0 if result["all_qualified"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
