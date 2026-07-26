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

from weave_loupe.weavec import BuildRequest, WeavecError, normalize_sources, run_build

BUNDLE_FORMAT = "weave-loupe-bundle-v1"


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
        path = _bundle_path(self.root, cast(str, item["path"]))
        return path if path.is_file() else None

    def artifact_text(self, name: str) -> str | None:
        path = self.artifact_path(name)
        return path.read_text(encoding="utf-8") if path is not None else None

    def artifact_json(self, name: str) -> Any | None:
        text = self.artifact_text(name)
        return json.loads(text) if text is not None else None


def capture_bundle(
    *,
    sources: Sequence[Path],
    output: Path,
    weavec: Path | None = None,
    include_executable: bool = False,
) -> CaptureResult:
    """Compile ordered sources and atomically publish a portable evidence bundle."""
    original_inputs = tuple(str(source) for source in sources)
    try:
        normalized = normalize_sources(sources)
    except WeavecError as exc:
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
        for index, source in enumerate(normalized):
            target = source_dir / f"{index:03d}-{source.name}"
            shutil.copyfile(source, target)
            source_entries.append(
                _file_entry(
                    work,
                    target,
                    extra={"index": index, "input": original_inputs[index]},
                )
            )

        request = BuildRequest(
            sources=normalized,
            executable=artifact_dir / "program",
            wir=artifact_dir / "program.wir",
            llvm=artifact_dir / "program.ll",
            diagnostics=artifact_dir / "diagnostics.json",
            trace=artifact_dir / "trace.json",
            build_manifest=artifact_dir / "build-manifest.json",
        )
        result = run_build(request, weavec=weavec)
        (log_dir / "stdout.txt").write_text(result.stdout, encoding="utf-8")
        (log_dir / "stderr.txt").write_text(result.stderr, encoding="utf-8")

        artifact_paths: dict[str, Path] = {
            "wir": request.wir,
            "llvm": request.llvm,
            "diagnostics": request.diagnostics,
            "trace": request.trace,
            "build_manifest": request.build_manifest,
        }
        if include_executable:
            artifact_paths["executable"] = request.executable
        elif request.executable.exists():
            request.executable.unlink()

        artifacts: dict[str, dict[str, Any]] = {}
        for name, path in artifact_paths.items():
            if path.is_file():
                artifacts[name] = _file_entry(work, path)

        manifest: dict[str, Any] = {
            "format": BUNDLE_FORMAT,
            "compiler": {
                "binary": Path(result.command[0]).name,
                "command": _portable_command(source_entries),
                "exit_code": result.returncode,
            },
            "sources": source_entries,
            "artifacts": artifacts,
            "logs": {
                "stdout": str((log_dir / "stdout.txt").relative_to(work)),
                "stderr": str((log_dir / "stderr.txt").relative_to(work)),
            },
        }
        (work / "bundle.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        _replace_directory(work, destination)
        return CaptureResult(bundle=destination, compiler_exit_code=result.returncode)
    except (OSError, WeavecError, ValueError) as exc:
        shutil.rmtree(work, ignore_errors=True)
        raise BundleError(str(exc)) from exc


def load_bundle(path: Path) -> Bundle:
    """Load and validate a bundle directory."""
    root = path.expanduser().resolve()
    manifest_path = root / "bundle.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BundleError(f"invalid bundle manifest: {exc}") from exc
    if not isinstance(manifest, dict) or manifest.get("format") != BUNDLE_FORMAT:
        raise BundleError(f"unsupported bundle format in {manifest_path}")
    return Bundle(root=root, manifest=cast(Mapping[str, Any], manifest))


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
        "path": str(path.relative_to(root)),
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
