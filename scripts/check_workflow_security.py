#!/usr/bin/env python3
"""Enforce least-privilege and immutable GitHub Actions workflows."""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

import yaml

_ACTION_LINE = re.compile(r"^\s*(?:-\s+)?uses:\s+([^\s#]+)(?:\s+#\s+(.+?))?\s*$")
_PINNED_ACTION = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+@[0-9a-f]{40}$")
_RELEASE_TAG = re.compile(r"^v[0-9]+(?:\.[0-9]+){0,2}$")
_WRITE = "write"

_ALLOWED_WRITE_PERMISSIONS: dict[tuple[str, str], dict[str, str]] = {
    (
        ".github/workflows/publish-audit.yml",
        "publish",
    ): {
        "contents": "write",
        "pull-requests": "write",
    },
    (
        ".github/workflows/scheduled-reaudit.yml",
        "publish-reports",
    ): {
        "contents": "write",
    },
}

_ALLOWED_PUBLICATION_SECRET_JOBS = {
    (
        ".github/workflows/scheduled-reaudit.yml",
        "publish-findings",
    )
}

_PROJECT_EXECUTION_MARKERS = (
    ".weave-tools",
    "./build.sh",
    "loupe ",
    "python ",
    "scripts/",
    "uv run",
)


def check_workflows(root: Path) -> list[str]:
    """Return deterministic policy violations for checked-in workflows."""
    workflow_root = root / ".github" / "workflows"
    failures: list[str] = []
    for path in sorted(workflow_root.glob("*.y*ml")):
        relative = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        failures.extend(_check_action_pins(relative, text))
        failures.extend(_check_workflow(relative, text))
    if not list(workflow_root.glob("*.y*ml")):
        failures.append(".github/workflows: no workflow files found")
    return sorted(failures)


def _check_action_pins(relative: str, text: str) -> list[str]:
    failures: list[str] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if "uses:" not in line:
            continue
        match = _ACTION_LINE.match(line)
        if match is None:
            failures.append(
                f"{relative}:{line_number}: uses must be a single pinned action line"
            )
            continue
        reference, release_tag = match.groups()
        if reference.startswith("./"):
            continue
        if _PINNED_ACTION.fullmatch(reference) is None:
            failures.append(
                f"{relative}:{line_number}: action is not pinned to a full SHA: "
                f"{reference}"
            )
        if release_tag is None or _RELEASE_TAG.fullmatch(release_tag.strip()) is None:
            failures.append(
                f"{relative}:{line_number}: pinned action must document its release tag"
            )
    return failures


def _check_workflow(relative: str, text: str) -> list[str]:
    failures: list[str] = []
    if "pull_request_target:" in text:
        failures.append(f"{relative}: pull_request_target is forbidden")
    try:
        document = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        return [f"{relative}: invalid YAML: {exc}"]
    if not isinstance(document, Mapping):
        return [f"{relative}: workflow document must be a mapping"]

    top_permissions = _permission_mapping(document.get("permissions"))
    top_writes = _write_permissions(top_permissions)
    if top_writes:
        failures.append(
            f"{relative}: top-level write permissions are forbidden: "
            + ", ".join(top_writes)
        )

    jobs = document.get("jobs")
    if not isinstance(jobs, Mapping):
        return failures + [f"{relative}: jobs must be a mapping"]

    for raw_name, raw_job in jobs.items():
        job_name = str(raw_name)
        if not isinstance(raw_job, Mapping):
            failures.append(f"{relative}:{job_name}: job must be a mapping")
            continue
        job_permissions = _permission_mapping(raw_job.get("permissions"))
        writes = _write_permissions(job_permissions)
        expected = _ALLOWED_WRITE_PERMISSIONS.get((relative, job_name), {})
        if job_permissions != expected and writes:
            failures.append(
                f"{relative}:{job_name}: unexpected write permissions: "
                + ", ".join(
                    f"{name}={value}" for name, value in job_permissions.items()
                )
            )
        if expected and job_permissions != expected:
            failures.append(
                f"{relative}:{job_name}: publication permissions must be exactly "
                + ", ".join(f"{name}={value}" for name, value in expected.items())
            )

        strings = tuple(_string_values(raw_job))
        uses_publication_secret = any(
            "WEAVE_GITHUB_TOKEN" in value for value in strings
        )
        secret_allowed = (relative, job_name) in _ALLOWED_PUBLICATION_SECRET_JOBS
        if uses_publication_secret and not secret_allowed:
            failures.append(
                f"{relative}:{job_name}: WEAVE_GITHUB_TOKEN is restricted to the "
                "cross-repository findings publisher"
            )
        credentialed = bool(expected) or uses_publication_secret
        if credentialed:
            failures.extend(
                _check_credentialed_job(relative, job_name, raw_job, strings)
            )
        else:
            failures.extend(_check_read_only_checkout(relative, job_name, raw_job))

    return failures


def _check_credentialed_job(
    relative: str,
    job_name: str,
    job: Mapping[str, Any],
    strings: tuple[str, ...],
) -> list[str]:
    failures: list[str] = []
    if any("WEAVE_LLM_" in value for value in strings):
        failures.append(
            f"{relative}:{job_name}: publication credentials and LLM secrets "
            "must not share a job"
        )
    for step in _steps(job):
        command = step.get("run")
        if not isinstance(command, str):
            continue
        marker = next(
            (item for item in _PROJECT_EXECUTION_MARKERS if item in command),
            None,
        )
        if marker is not None:
            failures.append(
                f"{relative}:{job_name}: credentialed job executes project code "
                f"through {marker!r}"
            )
    return failures


def _check_read_only_checkout(
    relative: str,
    job_name: str,
    job: Mapping[str, Any],
) -> list[str]:
    failures: list[str] = []
    for step in _steps(job):
        reference = step.get("uses")
        if not isinstance(reference, str) or not reference.startswith(
            "actions/checkout@"
        ):
            continue
        options = step.get("with")
        persist = (
            options.get("persist-credentials") if isinstance(options, Mapping) else None
        )
        if persist is not False:
            failures.append(
                f"{relative}:{job_name}: read-only checkout must set "
                "persist-credentials: false"
            )
    return failures


def _steps(job: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    value = job.get("steps")
    if not isinstance(value, list):
        return []
    return [step for step in value if isinstance(step, Mapping)]


def _permission_mapping(value: object) -> dict[str, str]:
    if value is None:
        return {}
    if isinstance(value, str):
        return {"*": value}
    if not isinstance(value, Mapping):
        return {"<invalid>": repr(value)}
    return {str(name): str(level) for name, level in sorted(value.items())}


def _write_permissions(permissions: Mapping[str, str]) -> list[str]:
    return sorted(
        name
        for name, level in permissions.items()
        if level == _WRITE or level == "write-all"
    )


def _string_values(value: object) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, Mapping):
        for key, item in value.items():
            yield from _string_values(key)
            yield from _string_values(item)
    elif isinstance(value, list):
        for item in value:
            yield from _string_values(item)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="repository root containing .github/workflows",
    )
    arguments = parser.parse_args(argv)
    failures = check_workflows(arguments.root.resolve())
    if failures:
        for failure in failures:
            print(f"workflow security: {failure}", file=sys.stderr)
        return 1
    print("workflow security: all workflows satisfy the policy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
