"""Helpers for invoking the weavec compiler."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


class WeavecError(RuntimeError):
    """Raised when weavec cannot be found or fails."""


@dataclass(frozen=True)
class CompilationArtifacts:
    """Surface Weave lowered through WIR to LLVM IR."""

    weave_source: str
    wir: str
    llvm_ir: str


def resolve_weavec(explicit: Path | None = None) -> Path:
    if explicit is not None:
        path = explicit.expanduser().resolve()
        if not path.is_file():
            raise WeavecError(f"weavec binary not found: {path}")
        return path

    env = os.environ.get("WEAVEC_BIN")
    if env:
        path = Path(env).expanduser().resolve()
        if not path.is_file():
            raise WeavecError(f"WEAVEC_BIN does not point to a file: {path}")
        return path

    found = shutil.which("weavec")
    if found is None:
        raise WeavecError("weavec not found; set WEAVEC_BIN or add weavec to PATH")
    return Path(found).resolve()


def compile_weave(weave_file: Path, weavec: Path | None = None) -> CompilationArtifacts:
    """Lower surface Weave to WIR and LLVM IR via weavec."""
    source = weave_file.expanduser().resolve()
    if not source.is_file():
        raise WeavecError(f"weave source not found: {source}")

    weave_source = source.read_text(encoding="utf-8")
    binary = resolve_weavec(weavec)
    with tempfile.TemporaryDirectory(prefix="loupe-") as tmp:
        tmp_path = Path(tmp)
        wir_path = tmp_path / "program.wir"
        ll_path = tmp_path / "program.ll"

        _run(
            [str(binary), "--frontend", str(wir_path), str(source)],
            label="weavec --frontend",
        )
        _run(
            [str(binary), "--backend", str(wir_path), str(ll_path)],
            label="weavec --backend",
        )
        return CompilationArtifacts(
            weave_source=weave_source,
            wir=wir_path.read_text(encoding="utf-8"),
            llvm_ir=ll_path.read_text(encoding="utf-8"),
        )


def _run(cmd: list[str], *, label: str) -> None:
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        raise WeavecError(
            f"{label} failed with exit {result.returncode}"
            + (f":\n{detail}" if detail else "")
        )
