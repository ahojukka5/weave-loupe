"""Fail-closed ingestion of retained compiler evidence into portable bundles."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
import tempfile
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, cast

from weave_loupe.compiler.capabilities import (
    CompilerCapabilityError,
    require_capture_capabilities,
    validate_capability_document,
)
from weave_loupe.schemas import SchemaProblem
from weave_loupe.wir_syntax import (
    SUPPORTED_CORE_VERSIONS,
    describe_supported_core_versions,
)

from .ingest_contract import (
    COMPILER_ARTIFACT_PATHS,
    MAX_INGEST_ARTIFACT_BYTES,
    MAX_INGEST_LOG_BYTES,
    MAX_INGEST_NODE_MAP_BYTES,
    MAX_INGEST_REQUEST_BYTES,
    MAX_INGEST_SOURCE_BYTES,
    MAX_INGEST_TOTAL_BYTES,
    validate_ingest_request_document,
)
from .loading import load_bundle
from .model import BundleError
from .publication import file_entry, publish_directory
from .verification import BUNDLE_FORMAT, MANIFEST_NAME

_WIR_CORE_VERSION = re.compile(r"\(core-version\s+(\d+)\s*\)")


def require_supported_wir_core_version(wir: str) -> int:
    """Return the core version retained WIR declares, or reject it.

    Ingest is fail-closed, so WIR whose version cannot be read is refused rather
    than stored unvalidated. Every version Loupe can analyse is accepted here,
    including versions older than the one the current compiler emits: bundles
    retain WIR text, so evidence captured under an earlier contract must stay
    ingestible for as long as it exists.
    """
    declared = _WIR_CORE_VERSION.search(wir)
    if declared is None:
        raise BundleError("retained WIR does not declare a core version")
    version = int(declared.group(1))
    if version not in SUPPORTED_CORE_VERSIONS:
        raise BundleError(
            f"retained WIR declares unsupported core version {version}, "
            f"expected {describe_supported_core_versions()}"
        )
    return version


@dataclass(frozen=True)
class IngestResult:
    """Result of publishing retained compiler evidence without execution."""

    bundle: Path
    compiler_exit_code: int


def ingest_bundle(*, request: Path, output: Path) -> IngestResult:
    """Validate, copy, verify, and atomically publish retained compiler evidence."""
    request_path, document = _load_request(request)
    request_root = request_path.parent.resolve()
    destination = output.expanduser().resolve()
    _validate_destination(request_path, destination)

    destination.parent.mkdir(parents=True, exist_ok=True)
    work = Path(
        tempfile.mkdtemp(prefix=f".{destination.name}.", dir=destination.parent)
    )
    try:
        compiler = cast(dict[str, Any], document["compiler"])
        sources = cast(list[dict[str, Any]], document["sources"])
        artifacts = cast(dict[str, dict[str, Any]], document["artifacts"])
        logs = cast(dict[str, dict[str, Any]], document["logs"])
        registry = _FileRegistry(
            request_root=request_root,
            bundle_root=work,
            forbidden_root=destination,
        )

        source_dir = work / "sources"
        artifact_dir = work / "artifacts"
        log_dir = work / "logs"
        source_dir.mkdir()
        artifact_dir.mkdir()
        log_dir.mkdir()

        output_artifacts: dict[str, dict[str, Any]] = {}
        source_entries: list[dict[str, Any]] = []
        for index, source in enumerate(sources):
            target = source_dir / _source_name(index, str(source["path"]))
            retained = registry.copy(
                source,
                target,
                byte_limit=MAX_INGEST_SOURCE_BYTES,
                location=f"sources[{index}]",
            )
            entry: dict[str, Any] = {
                **retained,
                "index": index,
                "input": source["input"],
            }
            identity = source.get("identity")
            if isinstance(identity, dict):
                entry["identity"] = identity
            metadata = source.get("metadata")
            if isinstance(metadata, dict):
                entry["metadata"] = _retain_source_metadata(
                    index=index,
                    metadata=metadata,
                    registry=registry,
                    artifact_dir=artifact_dir,
                    output_artifacts=output_artifacts,
                )
            source_entries.append(entry)

        for name, declared in artifacts.items():
            target = work / COMPILER_ARTIFACT_PATHS[name]
            retained = registry.copy(
                declared,
                target,
                byte_limit=MAX_INGEST_ARTIFACT_BYTES,
                location=f"artifacts.{name}",
            )
            if name == "executable":
                target.chmod(0o755)
            output_artifacts[name] = retained

        output_logs = {
            name: registry.copy(
                declared,
                log_dir / f"{name}.txt",
                byte_limit=MAX_INGEST_LOG_BYTES,
                location=f"logs.{name}",
            )
            for name, declared in logs.items()
        }
        _validate_protocol_artifacts(
            work=work,
            artifacts=output_artifacts,
            sources=sources,
        )
        canonical_command = _validate_and_portabilize_command(
            compiler=compiler,
            sources=sources,
            artifacts=artifacts,
        )

        manifest: dict[str, Any] = {
            "format": BUNDLE_FORMAT,
            "compiler": {
                "binary": Path(str(compiler["binary"])).name,
                "command": canonical_command,
                "exit_code": compiler["exit_code"],
                "execution": compiler["execution"],
            },
            "sources": source_entries,
            "artifacts": dict(sorted(output_artifacts.items())),
            "logs": output_logs,
        }
        source_identity = document.get("source_identity")
        if isinstance(source_identity, dict):
            manifest["source_identity"] = source_identity
        (work / MANIFEST_NAME).write_text(
            json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        load_bundle(work)
        publish_directory(work, destination)
        return IngestResult(
            bundle=destination,
            compiler_exit_code=cast(int, compiler["exit_code"]),
        )
    except BundleError:
        shutil.rmtree(work, ignore_errors=True)
        raise
    except (OSError, ValueError, TypeError) as exc:
        shutil.rmtree(work, ignore_errors=True)
        raise BundleError(str(exc)) from exc


class _FileRegistry:
    """Verify each input once while copying its declared byte snapshot."""

    def __init__(
        self,
        *,
        request_root: Path,
        bundle_root: Path,
        forbidden_root: Path,
    ) -> None:
        self.request_root = request_root
        self.bundle_root = bundle_root
        self.forbidden_root = forbidden_root
        self.paths: set[Path] = set()
        self.inodes: set[tuple[int, int]] = set()
        self.total_bytes = 0

    def copy(
        self,
        declared: Mapping[str, Any],
        target: Path,
        *,
        byte_limit: int,
        location: str,
    ) -> dict[str, Any]:
        raw_path = cast(str, declared["path"])
        candidate, inspected = self._inspect(raw_path, location)
        if candidate in self.paths:
            raise BundleError(f"{location}: input path is declared more than once")
        inode = (inspected.st_dev, inspected.st_ino)
        if inode in self.inodes:
            raise BundleError(f"{location}: input file is declared more than once")
        self.paths.add(candidate)
        self.inodes.add(inode)

        declared_size = cast(int, declared["size"])
        declared_digest = cast(str, declared["sha256"])
        if declared_size > byte_limit:
            raise BundleError(
                f"{location}: declared size {declared_size} exceeds {byte_limit} bytes"
            )
        if self.total_bytes + declared_size > MAX_INGEST_TOTAL_BYTES:
            raise BundleError(
                f"{location}: retained evidence exceeds {MAX_INGEST_TOTAL_BYTES} bytes"
            )

        target.parent.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256()
        copied = 0
        with candidate.open("rb") as source, target.open("wb") as destination:
            opened = os.fstat(source.fileno())
            if not stat.S_ISREG(opened.st_mode):
                raise BundleError(f"{location}: input is not a regular file")
            if (opened.st_dev, opened.st_ino) != inode:
                raise BundleError(f"{location}: input changed during validation")
            while chunk := source.read(1024 * 1024):
                copied += len(chunk)
                if copied > byte_limit or copied > declared_size:
                    raise BundleError(f"{location}: input exceeds its declared size")
                digest.update(chunk)
                destination.write(chunk)
        observed_digest = digest.hexdigest()
        if copied != declared_size:
            raise BundleError(
                f"{location}: size mismatch; declared {declared_size}, "
                f"observed {copied}"
            )
        if observed_digest != declared_digest:
            raise BundleError(
                f"{location}: SHA-256 mismatch; declared {declared_digest}, "
                f"observed {observed_digest}"
            )
        self.total_bytes += copied
        return file_entry(self.bundle_root, target)

    def _inspect(self, raw_path: str, location: str) -> tuple[Path, os.stat_result]:
        relative = _relative_path(raw_path, location)
        current = self.request_root
        inspected: os.stat_result | None = None
        for index, component in enumerate(relative.parts):
            current = current / component
            try:
                inspected = current.lstat()
            except FileNotFoundError as exc:
                raise BundleError(f"{location}: input file does not exist") from exc
            if stat.S_ISLNK(inspected.st_mode):
                raise BundleError(f"{location}: symbolic links are not allowed")
            if index < len(relative.parts) - 1 and not stat.S_ISDIR(inspected.st_mode):
                raise BundleError(f"{location}: input parent is not a directory")
        if inspected is None or not stat.S_ISREG(inspected.st_mode):
            raise BundleError(f"{location}: input is not a regular file")
        candidate = current.resolve(strict=True)
        try:
            candidate.relative_to(self.request_root)
        except ValueError as exc:
            raise BundleError(f"{location}: input path escapes request root") from exc
        if candidate.is_relative_to(self.forbidden_root):
            raise BundleError(f"{location}: output bundle contains an input file")
        return candidate, inspected


def _load_request(path: Path) -> tuple[Path, dict[str, Any]]:
    expanded = path.expanduser()
    if expanded.is_symlink():
        raise BundleError("ingest request must not be a symbolic link")
    try:
        inspected = expanded.stat(follow_symlinks=False)
    except OSError as exc:
        raise BundleError(f"cannot inspect ingest request: {exc}") from exc
    if not stat.S_ISREG(inspected.st_mode):
        raise BundleError("ingest request must be a regular file")
    if inspected.st_size > MAX_INGEST_REQUEST_BYTES:
        raise BundleError(f"ingest request exceeds {MAX_INGEST_REQUEST_BYTES} bytes")
    try:
        data = expanded.read_bytes()
        duplicates: list[str] = []
        value = json.loads(
            data.decode("utf-8"),
            object_pairs_hook=_duplicate_key_hook(duplicates),
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BundleError(f"invalid ingest request: {exc}") from exc
    if duplicates:
        names = ", ".join(sorted(set(duplicates)))
        raise BundleError(f"ingest request contains duplicate object keys: {names}")
    problems = validate_ingest_request_document(value)
    if problems:
        raise BundleError(_schema_error(problems))
    return expanded.resolve(), cast(dict[str, Any], value)


def _duplicate_key_hook(
    duplicates: list[str],
) -> Callable[[list[tuple[str, Any]]], dict[str, Any]]:
    def hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                duplicates.append(key)
            result[key] = value
        return result

    return hook


def _validate_destination(request: Path, destination: Path) -> None:
    if destination == request.parent.resolve():
        raise BundleError("output bundle must not replace the ingest request root")
    if request.is_relative_to(destination):
        raise BundleError("output bundle contains the ingest request")
    if destination.is_symlink():
        raise BundleError("output bundle must not be a symbolic link")
    if destination.exists() and not destination.is_dir():
        raise BundleError("output bundle must be a directory or absent")


def _retain_source_metadata(
    *,
    index: int,
    metadata: Mapping[str, Any],
    registry: _FileRegistry,
    artifact_dir: Path,
    output_artifacts: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    retained = {name: value for name, value in metadata.items() if name != "node_map"}
    raw_node_map = metadata.get("node_map")
    if isinstance(raw_node_map, Mapping):
        logical_name = f"source_node_map_{index:03d}"
        target = artifact_dir / f"source-node-map-{index:03d}.json"
        entry = registry.copy(
            raw_node_map,
            target,
            byte_limit=MAX_INGEST_NODE_MAP_BYTES,
            location=f"sources[{index}].metadata.node_map",
        )
        output_artifacts[logical_name] = entry
        retained["node_map"] = {
            "artifact": logical_name,
            "size": entry["size"],
            "sha256": entry["sha256"],
        }
    return retained


def _validate_and_portabilize_command(
    *,
    compiler: Mapping[str, Any],
    sources: list[dict[str, Any]],
    artifacts: Mapping[str, dict[str, Any]],
) -> list[str]:
    command = cast(list[str], compiler["command"])
    binary = Path(str(compiler["binary"])).name
    if not binary or Path(command[0]).name != binary:
        raise BundleError("compiler command binary does not match compiler.binary")
    for index, argument in enumerate(command[1:], start=1):
        if "\x00" in argument:
            raise BundleError(f"compiler.command[{index}] contains a NUL byte")
        if Path(argument).is_absolute():
            raise BundleError(
                f"compiler.command[{index}] contains a non-portable absolute path"
            )
    positions = [
        _single_argument_position(command, str(source["path"]), f"sources[{index}]")
        for index, source in enumerate(sources)
    ]
    if positions != sorted(positions):
        raise BundleError("compiler command source arguments are out of order")

    replacements = {
        str(source["path"]): f"sources/{_source_name(index, str(source['path']))}"
        for index, source in enumerate(sources)
    }
    for name, declared in artifacts.items():
        if name == "compiler_capabilities":
            continue
        raw_path = str(declared["path"])
        _single_argument_position(command, raw_path, f"artifacts.{name}")
        replacements[raw_path] = COMPILER_ARTIFACT_PATHS[name]

    execution = compiler["execution"]
    if isinstance(execution, Mapping):
        execution_exit = execution.get("exit_code")
        if (
            isinstance(execution_exit, int)
            and not isinstance(execution_exit, bool)
            and execution_exit != compiler["exit_code"]
        ):
            raise BundleError(
                "compiler.execution.exit_code does not match compiler.exit_code"
            )
    return [binary, *(replacements.get(argument, argument) for argument in command[1:])]


def _single_argument_position(
    command: list[str],
    value: str,
    location: str,
) -> int:
    positions = [index for index, argument in enumerate(command) if argument == value]
    if len(positions) != 1:
        raise BundleError(
            f"{location}: declared path must occur exactly once in compiler command"
        )
    return positions[0]


def _validate_protocol_artifacts(
    *,
    work: Path,
    artifacts: Mapping[str, Mapping[str, Any]],
    sources: list[dict[str, Any]],
) -> None:
    capabilities = _json_artifact(work, artifacts, "compiler_capabilities")
    try:
        validated = validate_capability_document(capabilities)
        require_capture_capabilities(validated)
    except CompilerCapabilityError as exc:
        raise BundleError(f"compiler capabilities are incompatible: {exc}") from exc

    if "wir" in artifacts:
        wir_path = work / cast(str, artifacts["wir"]["path"])
        try:
            wir = wir_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise BundleError(f"retained WIR is not valid UTF-8: {exc}") from exc
        require_supported_wir_core_version(wir)

    if "diagnostics" in artifacts:
        diagnostics = _json_artifact(work, artifacts, "diagnostics")
        if diagnostics.get("format") != "weavec-diagnostics-v1":
            raise BundleError("retained diagnostics format is unsupported")
        if not isinstance(diagnostics.get("diagnostics"), list):
            raise BundleError("retained diagnostics must contain a diagnostics list")

    if "trace" in artifacts:
        trace = _json_artifact(work, artifacts, "trace")
        if trace.get("format") != "weavec-compilation-trace-v1":
            raise BundleError("retained compilation trace format is unsupported")
        if not isinstance(trace.get("events"), list):
            raise BundleError("retained compilation trace must contain an events list")

    if "build_manifest" in artifacts:
        manifest = _json_artifact(work, artifacts, "build_manifest")
        if manifest.get("format") != "weavec-build-manifest-v1":
            raise BundleError("retained build manifest format is unsupported")
        manifest_sources = manifest.get("sources")
        if not isinstance(manifest_sources, list) or not all(
            isinstance(item, str) for item in manifest_sources
        ):
            raise BundleError("retained build manifest must contain ordered sources")
        expected = [PurePosixPath(str(source["input"])).name for source in sources]
        observed = [PurePosixPath(item).name for item in manifest_sources]
        if observed != expected:
            raise BundleError(
                "retained build manifest source ordering does not match ingest request"
            )


def _json_artifact(
    work: Path,
    artifacts: Mapping[str, Mapping[str, Any]],
    name: str,
) -> dict[str, Any]:
    entry = artifacts[name]
    path = work / cast(str, entry["path"])
    duplicates: list[str] = []
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_duplicate_key_hook(duplicates),
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BundleError(f"retained {name} is not valid UTF-8 JSON: {exc}") from exc
    if duplicates:
        names = ", ".join(sorted(set(duplicates)))
        raise BundleError(f"retained {name} contains duplicate object keys: {names}")
    if not isinstance(value, dict):
        raise BundleError(f"retained {name} must be a JSON object")
    return value


def _relative_path(raw: str, location: str) -> PurePosixPath:
    if not raw or "\x00" in raw or "\\" in raw:
        raise BundleError(f"{location}: input path is not portable")
    path = PurePosixPath(raw)
    if (
        path.is_absolute()
        or not path.parts
        or any(part in {"", ".", ".."} for part in path.parts)
    ):
        raise BundleError(f"{location}: input path must be a contained relative path")
    return path


def _source_name(index: int, raw_path: str) -> str:
    name = PurePosixPath(raw_path).name
    return f"{index:03d}-{name}"


def _schema_error(problems: tuple[SchemaProblem, ...]) -> str:
    detail = "; ".join(
        f"{problem.path} [{problem.keyword}]: {problem.message}" for problem in problems
    )
    return f"ingest request schema validation failed: {detail}"
