"""Machine-readable audit verdicts and reproducibility metadata."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from weave_loupe.bundle import Bundle
from weave_loupe.compiler_version import identify_weavec
from weave_loupe.weavec import resolve_weavec

_FAILED = re.compile(r"^FAILED:\s*([a-z0-9]+(?:-[a-z0-9]+)*):\s*(\S(?:.*\S)?)\s*$")


class AuditProtocolError(ValueError):
    """Raised when an LLM response does not obey the verdict contract."""


@dataclass(frozen=True)
class AuditVerdict:
    """Parsed first-line verdict returned by the reviewing model."""

    status: Literal["OK", "FAILED"]
    code: str | None
    reason: str | None
    body: str

    @property
    def passed(self) -> bool:
        return self.status == "OK"


def parse_audit_response(response: str) -> AuditVerdict:
    """Parse the mandatory first-line ``OK`` / ``FAILED`` audit protocol."""
    normalized = response.replace("\r\n", "\n").lstrip("\ufeff")
    lines = normalized.splitlines()
    if not lines:
        raise AuditProtocolError("LLM response was empty")
    first = lines[0].strip()
    body = "\n".join(lines[1:]).strip()
    if first == "OK":
        return AuditVerdict(status="OK", code=None, reason=None, body=body)
    failed = _FAILED.fullmatch(first)
    if failed is not None:
        return AuditVerdict(
            status="FAILED",
            code=failed.group(1),
            reason=failed.group(2),
            body=body,
        )
    raise AuditProtocolError(
        "first line must be exactly 'OK' or 'FAILED: <lowercase-kebab-code>: <reason>'"
    )


def collect_audit_metadata(
    *,
    sources: list[Path],
    weavec: Path | None,
    model: str,
    bundle: Bundle,
) -> dict[str, Any]:
    """Collect source, compiler, runtime, and machine facts for one audit."""
    binary = resolve_weavec(weavec)
    identity = identify_weavec(binary)
    return {
        "format": "weave-loupe-audit-metadata-v1",
        "timestamp_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "model": model,
        "source_repository": _git_metadata(_common_source_directory(sources)),
        "loupe_repository": _git_metadata(Path(__file__).resolve()),
        "weavec": {
            "path": str(binary),
            "sha256": _sha256(binary),
            "version": identity.display,
            "base_version": identity.base,
            "git_sha": identity.git_sha,
            "development": identity.development,
            "version_source": identity.source,
            "repository": _git_metadata(binary),
        },
        "machine": _machine_metadata(),
        "sources": [
            {
                "path": str(source),
                "sha256": _sha256(source),
                "size": source.stat().st_size,
            }
            for source in sources
        ],
        "bundle": {
            "format": bundle.manifest.get("format"),
            "compiler_exit_code": _compiler_exit_code(bundle),
            "artifacts": _artifact_hashes(bundle),
        },
        "github": _github_metadata(),
    }


def render_audit_report(
    *, verdict: AuditVerdict, metadata: dict[str, Any], model_response: str
) -> str:
    """Render a stable Markdown envelope around the model's review."""
    source_repo = _mapping(metadata.get("source_repository"))
    loupe_repo = _mapping(metadata.get("loupe_repository"))
    weavec = _mapping(metadata.get("weavec"))
    weavec_repo = _mapping(weavec.get("repository"))
    machine = _mapping(metadata.get("machine"))
    bundle = _mapping(metadata.get("bundle"))
    github = _mapping(metadata.get("github"))
    build_kind = "development" if weavec.get("development") else "release"

    lines = [
        "# Weave Loupe Audit Report",
        "",
        "## Verdict",
        "",
        f"- **Status:** {verdict.status}",
        f"- **Code:** {verdict.code or 'none'}",
        f"- **Reason:** {verdict.reason or 'No blocking defect found.'}",
        "",
        "## Reproducibility",
        "",
        f"- **Audit timestamp (UTC):** `{metadata['timestamp_utc']}`",
        f"- **Audited source Git SHA:** `{source_repo.get('sha', 'unavailable')}`",
        f"- **Source tree state:** `{source_repo.get('state', 'unavailable')}`",
        f"- **Weave Loupe Git SHA:** `{loupe_repo.get('sha', 'unavailable')}`",
        f"- **weavec Git SHA:** `{weavec_repo.get('sha', 'unavailable')}`",
        f"- **weavec binary SHA-256:** `{weavec.get('sha256', 'unavailable')}`",
        f"- **weavec version:** `{weavec.get('version', 'unavailable')}`",
        f"- **weavec build kind:** `{build_kind}`",
        f"- **weavec version source:** `{weavec.get('version_source', 'unavailable')}`",
        f"- **LLM model:** `{metadata['model']}`",
    ]
    if github.get("run_id"):
        lines.extend(
            [
                f"- **GitHub run ID:** `{github['run_id']}`",
                f"- **GitHub workflow SHA:** `{github.get('sha', 'unavailable')}`",
            ]
        )

    lines.extend(
        [
            "",
            "## Machine and running conditions",
            "",
            f"- **Operating system:** `{machine.get('os', 'unavailable')}`",
            f"- **Kernel:** `{machine.get('kernel', 'unavailable')}`",
            f"- **Architecture:** `{machine.get('architecture', 'unavailable')}`",
            f"- **CPU:** `{machine.get('cpu', 'unavailable')}`",
            f"- **Logical CPUs:** `{machine.get('logical_cpus', 'unavailable')}`",
            f"- **Memory:** `{machine.get('memory_bytes', 'unavailable')}` bytes",
            f"- **Python:** `{machine.get('python', 'unavailable')}`",
            f"- **libc:** `{machine.get('libc', 'unavailable')}`",
            "",
            "## Audited inputs",
            "",
        ]
    )
    for source in metadata.get("sources", []):
        item = _mapping(source)
        lines.append(
            f"- `{item.get('path', 'unknown')}` — SHA-256 "
            f"`{item.get('sha256', 'unavailable')}`"
        )

    lines.extend(["", "## Captured evidence", ""])
    artifacts = _mapping(bundle.get("artifacts"))
    if artifacts:
        for name, digest in sorted(artifacts.items()):
            lines.append(f"- `{name}` — SHA-256 `{digest}`")
    else:
        lines.append("- No compiler artifacts were published.")

    lines.extend(
        [
            "",
            "## LLM review",
            "",
            verdict.body or "No narrative review was returned.",
            "",
            "<details>",
            "<summary>Raw model response</summary>",
            "",
            "```text",
            model_response.rstrip(),
            "```",
            "</details>",
            "",
        ]
    )
    return "\n".join(lines)


def metadata_json(metadata: dict[str, Any]) -> str:
    """Serialize metadata for verbose diagnostics and tests."""
    return json.dumps(metadata, indent=2, sort_keys=True, ensure_ascii=False)


def _git_metadata(path: Path) -> dict[str, str]:
    directory = path if path.is_dir() else path.parent
    root = _run_git(directory, "rev-parse", "--show-toplevel")
    if root is None:
        return {"sha": "unavailable", "state": "not-a-git-worktree"}
    root_path = Path(root)
    sha = _run_git(root_path, "rev-parse", "HEAD") or "unavailable"
    status = _run_git(root_path, "status", "--porcelain", "--untracked-files=no")
    state = "clean" if status == "" else "dirty"
    return {"root": root, "sha": sha, "state": state}


def _run_git(directory: Path, *args: str) -> str | None:
    try:
        completed = subprocess.run(
            ["git", "-C", str(directory), *args],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout.strip()


def _machine_metadata() -> dict[str, Any]:
    libc_name, libc_version = platform.libc_ver()
    return {
        "os": _os_pretty_name(),
        "kernel": f"{platform.system()} {platform.release()}",
        "architecture": platform.machine(),
        "cpu": _cpu_model(),
        "logical_cpus": os.cpu_count() or 0,
        "memory_bytes": _memory_bytes(),
        "python": platform.python_version(),
        "libc": " ".join(part for part in (libc_name, libc_version) if part)
        or "unavailable",
        "byteorder": sys.byteorder,
    }


def _os_pretty_name() -> str:
    try:
        for line in Path("/etc/os-release").read_text(encoding="utf-8").splitlines():
            if line.startswith("PRETTY_NAME="):
                return line.split("=", 1)[1].strip().strip('"')
    except OSError:
        pass
    return platform.platform()


def _cpu_model() -> str:
    try:
        for line in Path("/proc/cpuinfo").read_text(encoding="utf-8").splitlines():
            if line.lower().startswith("model name"):
                return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or "unavailable"


def _memory_bytes() -> int:
    try:
        for line in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
            if line.startswith("MemTotal:"):
                return int(line.split()[1]) * 1024
    except (OSError, ValueError, IndexError):
        pass
    return 0


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _common_source_directory(sources: list[Path]) -> Path:
    if not sources:
        return Path.cwd()
    resolved = [source.resolve() for source in sources]
    common = Path(os.path.commonpath([str(path.parent) for path in resolved]))
    return common


def _artifact_hashes(bundle: Bundle) -> dict[str, str]:
    artifacts = bundle.manifest.get("artifacts", {})
    if not isinstance(artifacts, dict):
        return {}
    hashes: dict[str, str] = {}
    for name in artifacts:
        if not isinstance(name, str):
            continue
        path = bundle.artifact_path(name)
        if path is not None:
            hashes[name] = _sha256(path)
    return hashes


def _compiler_exit_code(bundle: Bundle) -> int | None:
    compiler = bundle.manifest.get("compiler")
    if not isinstance(compiler, dict):
        return None
    value = compiler.get("exit_code")
    return value if isinstance(value, int) else None


def _github_metadata() -> dict[str, str]:
    values = {
        "run_id": os.environ.get("GITHUB_RUN_ID", ""),
        "repository": os.environ.get("GITHUB_REPOSITORY", ""),
        "sha": os.environ.get("GITHUB_SHA", ""),
        "workflow": os.environ.get("GITHUB_WORKFLOW", ""),
    }
    return {key: value for key, value in values.items() if value}


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}
