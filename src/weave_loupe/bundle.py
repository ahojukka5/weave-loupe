"""Portable compiler-evidence bundles."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from weave_loupe.bundle_verification import (
    BUNDLE_FORMAT,
    MANIFEST_NAME,
    BundleProblem,
    BundleVerification,
    verify_bundle,
)
from weave_loupe.path_identity import (
    PORTABLE_PATH_FORMAT,
    PathIdentityError,
    plan_public_paths,
)
from weave_loupe.schemas import (
    SchemaCatalogError,
    SchemaValidationError,
    require_valid_document,
)
from weave_loupe.weavec import BuildRequest, WeavecError, normalize_sources, run_build

__all__ = [
    "BUNDLE_FORMAT",
    "Bundle",
    "BundleError",
    "BundleProblem",
    "BundleVerification",
    "CaptureResult",
    "capture_bundle",
    "load_bundle",
    "verify_bundle",
]


class BundleError(RuntimeError):
    """Raised when a bundle is invalid or cannot be produced."""


@dataclass(frozen=True)
class CaptureResult:
    """Result of capturing one compiler invocation."""

    bundle: Path
    compiler_exit_code: int


@dataclass(frozen=True)
class Bundle:
    """Validated bundle directory and manifest."""

    root: Path
    manifest: Mapping[str, Any]

    @property
    def sources(self) -> tuple[Mapping[str, Any], ...]:
        raw = self.manifest.get("sources", [])
        if not isinstance(raw, list):
            raise BundleError("bundle sources must be a list")
        return tuple(cast(Mapping[str, Any], item) for item in raw)

    def read_text(self, relative_path: str) -> str:
        return _bundle_path(self.root, relative_path).read_text(encoding="utf-8")

    def artifact_path(self, name: str) -> Path | None:
        artifacts = self.manifest.get("artifacts", {})
        if not isinstance(artifacts, dict):
            raise BundleError("bundle artifacts must be an object")
        item = artifacts.get(name)
        if item is None:
            return None
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            raise BundleError(f"invalid artifact entry: {name}")
        return _bundle_path(self.root, cast(str, item["path"]))

    def artifact_text(self, name: str) -> str | None:
        path = self.artifact_path(name)
        return path.read_text(encoding="utf-8") if path is not None else None

    def artifact_json(self, name: str) -> Any | None:
        text = self.artifact_text(name)
        return json.loads(text) if text is not None else None

    def log_path(self, name: str) -> Path | None:
        """Return a verified log path, accepting legacy string entries."""
        logs = self.manifest.get("logs", {})
        if not isinstance(logs, dict):
            raise BundleError("bundle logs must be an object")
        item = logs.get(name)
        if item is None:
            return None
        relative_path = item if isinstance(item, str) else item.get("path")
        if not isinstance(relative_path, str):
            raise BundleError(f"invalid log entry: {name}")
        return _bundle_path(self.root, relative_path)

    def log_text(self, name: str) -> str | None:
        """Read a captured compiler log by logical name."""
        path = self.log_path(name)
        return path.read_text(encoding="utf-8") if path is not None else None


def capture_bundle(
    *,
    sources: Sequence[Path],
    output: Path,
    weavec: Path | None = None,
    include_executable: bool = False,
    compiler_timeout_seconds: float | None = None,
    compiler_output_bytes: int | None = None,
    audit_root: Path | None = None,
    source_names: Sequence[str] | None = None,
) -> CaptureResult:
    """Compile ordered sources and atomically publish a portable evidence bundle."""
    try:
        plan = plan_public_paths(
            sources,
            audit_root=audit_root,
            logical_names=source_names,
        )
        normalized = normalize_sources(
            [source.execution_path for source in plan.sources]
        )
    except (PathIdentityError, WeavecError) as exc:
        raise BundleError(str(exc)) from exc

    destination = output.expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    work = Path(
        tempfile.mkdtemp(prefix=f".{destination.name}.", dir=destination.parent)
    )
    try:
        source_dir = work / "sources"
        artifact_dir = work / "artifacts"
        log_dir = work / "logs"
        source_dir.mkdir()
        artifact_dir.mkdir()
        log_dir.mkdir()

        source_entries: list[dict[str, Any]] = []
        for index, (source, public) in enumerate(
            zip(normalized, plan.sources, strict=True)
        ):
            target = source_dir / f"{index:03d}-{source.name}"
            shutil.copyfile(source, target)
            source_entries.append(
                _file_entry(
                    work,
                    target,
                    extra={
                        "index": index,
                        "input": public.identity,
                        "identity": public.metadata(),
                    },
                )
            )

        request = BuildRequest(
            sources=normalized,
            executable=artifact_dir / "program",
            wir=artifact_dir / "program.wir",
            llvm=artifact_dir / "program.ll",
            optimized_llvm=artifact_dir / "program.optimized.ll",
            assembly=artifact_dir / "program.s",
            disassembly=artifact_dir / "program.disasm",
            optimization_record=artifact_dir / "program.opt.yaml",
            diagnostics=artifact_dir / "diagnostics.json",
            trace=artifact_dir / "trace.json",
            build_manifest=artifact_dir / "build-manifest.json",
        )
        result = run_build(
            request,
            weavec=weavec,
            timeout_seconds=compiler_timeout_seconds,
            output_bytes=compiler_output_bytes,
        )
        stdout_path = log_dir / "stdout.txt"
        stderr_path = log_dir / "stderr.txt"
        stdout_path.write_text(result.stdout, encoding="utf-8")
        stderr_path.write_text(result.stderr, encoding="utf-8")

        artifact_paths: dict[str, Path] = {
            "wir": request.wir,
            "llvm": request.llvm,
            "optimized_llvm": request.optimized_llvm,
            "assembly": request.assembly,
            "disassembly": request.disassembly,
            "optimization_record": request.optimization_record,
            "diagnostics": request.diagnostics,
            "trace": request.trace,
            "build_manifest": request.build_manifest,
        }
        if include_executable:
            artifact_paths["executable"] = request.executable
        elif request.executable.exists():
            request.executable.unlink()

        artifacts: dict[str, dict[str, Any]] = {}
        for name, artifact_path in artifact_paths.items():
            if artifact_path.is_file():
                artifacts[name] = _file_entry(work, artifact_path)

        manifest: dict[str, Any] = {
            "format": BUNDLE_FORMAT,
            "source_identity": {
                "format": PORTABLE_PATH_FORMAT,
                "root_kind": plan.root_kind,
            },
            "compiler": {
                "binary": Path(result.command[0]).name,
                "command": _portable_command(source_entries),
                "exit_code": result.returncode,
                "execution": result.execution.as_dict(),
            },
            "sources": source_entries,
            "artifacts": artifacts,
            "logs": {
                "stdout": _file_entry(work, stdout_path),
                "stderr": _file_entry(work, stderr_path),
            },
        }
        (work / MANIFEST_NAME).write_text(
            json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        verification = verify_bundle(work)
        if not verification.valid:
            raise BundleError(verification.error_message())

        _replace_directory(work, destination)
        return CaptureResult(
            bundle=destination,
            compiler_exit_code=result.returncode,
        )
    except BundleError:
        shutil.rmtree(work, ignore_errors=True)
        raise
    except (OSError, WeavecError, ValueError) as exc:
        shutil.rmtree(work, ignore_errors=True)
        raise BundleError(str(exc)) from exc


def load_bundle(path: Path) -> Bundle:
    """Load a bundle only after complete fail-closed integrity verification."""
    verification = verify_bundle(path)
    if not verification.valid or verification.manifest is None:
        raise BundleError(verification.error_message())
    try:
        require_valid_document(verification.manifest, BUNDLE_FORMAT)
    except (SchemaCatalogError, SchemaValidationError) as exc:
        raise BundleError(str(exc)) from exc
    return Bundle(root=verification.root, manifest=verification.manifest)


def _portable_command(source_entries: Sequence[Mapping[str, Any]]) -> list[str]:
    command = ["weavec", "build"]
    command.extend(str(entry["path"]) for entry in source_entries)
    command.extend(
        [
            "-o",
            "artifacts/program",
            "--emit-wir",
            "artifacts/program.wir",
            "--emit-llvm",
            "artifacts/program.ll",
            "--emit-optimized-llvm",
            "artifacts/program.optimized.ll",
            "--emit-assembly",
            "artifacts/program.s",
            "--emit-disassembly",
            "artifacts/program.disasm",
            "--optimization-record",
            "artifacts/program.opt.yaml",
            "-O3",
            "--native",
            "--diagnostics-json",
            "artifacts/diagnostics.json",
            "--trace-json",
            "artifacts/trace.json",
            "--manifest-json",
            "artifacts/build-manifest.json",
            "--llvm-provenance",
        ]
    )
    return command


def _file_entry(
    root: Path,
    path: Path,
    *,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    data = path.read_bytes()
    entry: dict[str, Any] = {
        "path": path.relative_to(root).as_posix(),
        "size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
    }
    if extra:
        entry.update(extra)
    return entry


def _bundle_path(root: Path, relative_path: str) -> Path:
    candidate = (root / relative_path).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise BundleError(f"bundle path escapes root: {relative_path}") from exc
    return candidate


def _replace_directory(source: Path, destination: Path) -> None:
    backup: Path | None = None
    if destination.exists():
        backup = destination.with_name(destination.name + ".previous")
        if backup.exists():
            shutil.rmtree(backup)
        os.replace(destination, backup)
    try:
        os.replace(source, destination)
    except OSError:
        if backup is not None and backup.exists() and not destination.exists():
            os.replace(backup, destination)
        raise
    if backup is not None:
        shutil.rmtree(backup, ignore_errors=True)
