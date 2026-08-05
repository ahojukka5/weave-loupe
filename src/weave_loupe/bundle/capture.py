"""Live compiler capture for portable evidence bundles."""

from __future__ import annotations

import json
import shutil
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from weave_loupe.bundle_verification import BUNDLE_FORMAT, MANIFEST_NAME, verify_bundle
from weave_loupe.compiler.capabilities import (
    CompilerCapabilityError,
    validate_capability_document,
)
from weave_loupe.path_identity import (
    PORTABLE_PATH_FORMAT,
    PathIdentityError,
    plan_public_paths,
)
from weave_loupe.weavec import BuildRequest, WeavecError, normalize_sources, run_build

from .model import BundleError
from .publication import file_entry, publish_directory


@dataclass(frozen=True)
class CaptureResult:
    """Result of capturing one compiler invocation."""

    bundle: Path
    compiler_exit_code: int


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
                file_entry(
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
        capabilities_path = artifact_dir / "compiler-capabilities.json"
        capabilities_path.write_bytes(result.capabilities.raw_bytes)
        try:
            validate_capability_document(
                json.loads(capabilities_path.read_text(encoding="utf-8"))
            )
        except (json.JSONDecodeError, CompilerCapabilityError) as exc:
            message = f"retained compiler capabilities are invalid: {exc}"
            raise BundleError(message) from exc

        stdout_path = log_dir / "stdout.txt"
        stderr_path = log_dir / "stderr.txt"
        stdout_path.write_text(result.stdout, encoding="utf-8")
        stderr_path.write_text(result.stderr, encoding="utf-8")

        artifact_paths: dict[str, Path] = {
            "compiler_capabilities": capabilities_path,
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
                artifacts[name] = file_entry(work, artifact_path)

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
                "stdout": file_entry(work, stdout_path),
                "stderr": file_entry(work, stderr_path),
            },
        }
        (work / MANIFEST_NAME).write_text(
            json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        verification = verify_bundle(work)
        if not verification.valid:
            raise BundleError(verification.error_message())

        publish_directory(work, destination)
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
