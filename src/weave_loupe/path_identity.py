"""Portable public identities for audit inputs and published evidence."""

from __future__ import annotations

import json
import os
import re
import subprocess
import unicodedata
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, cast

PORTABLE_PATH_FORMAT = "weave-loupe-portable-path-v1"
_DRIVE_PREFIX = re.compile(r"^[A-Za-z]:")
_PRIVATE_ENVIRONMENT = ("GITHUB_WORKSPACE", "RUNNER_WORKSPACE")


class PathIdentityError(ValueError):
    """Raised when an input cannot receive a safe portable public identity."""


@dataclass(frozen=True)
class PublicPath:
    """Resolved execution path plus its location-independent public identity."""

    execution_path: Path
    identity: str
    scope: str
    symlinked: bool

    def metadata(self) -> dict[str, Any]:
        return {
            "format": PORTABLE_PATH_FORMAT,
            "path": self.identity,
            "scope": self.scope,
            "symlinked": self.symlinked,
        }


@dataclass(frozen=True)
class PathPlan:
    """Common identity root and ordered source identities."""

    root: Path
    root_kind: str
    sources: tuple[PublicPath, ...]

    def source_names(self) -> tuple[str, ...]:
        return tuple(item.identity for item in self.sources)


def plan_public_paths(
    sources: Sequence[Path],
    *,
    audit_root: Path | None = None,
    logical_names: Sequence[str] | None = None,
) -> PathPlan:
    """Resolve ordered sources and assign portable public identities."""
    if not sources:
        raise PathIdentityError("at least one source is required")
    expanded = tuple(Path(source).expanduser() for source in sources)
    resolved = tuple(_safe_resolve(source) for source in expanded)
    names = _logical_names(logical_names, len(resolved))
    root, root_kind = _select_root(resolved, audit_root)

    public: list[PublicPath] = []
    for index, (lexical, execution) in enumerate(zip(expanded, resolved, strict=True)):
        try:
            relative = execution.relative_to(root)
        except ValueError:
            logical = names[index]
            if logical is None:
                raise PathIdentityError(
                    "source is outside the audit root and requires "
                    f"--source-name: {lexical}"
                ) from None
            identity = f"external/{normalize_portable_path(logical)}"
            scope = "external"
        else:
            identity = normalize_portable_path(relative.as_posix())
            scope = "root"
        public.append(
            PublicPath(
                execution_path=execution,
                identity=identity,
                scope=scope,
                symlinked=_is_symlinked(lexical),
            )
        )
    _reject_identity_collisions(public)
    return PathPlan(root=root, root_kind=root_kind, sources=tuple(public))


def canonical_sidecar_identity(sidecar: Path, plan: PathPlan) -> str:
    """Return a portable identity for one discovered audit sidecar."""
    resolved = _safe_resolve(sidecar.expanduser())
    try:
        relative = resolved.relative_to(plan.root)
    except ValueError:
        for source in plan.sources:
            if resolved.parent == source.execution_path.parent:
                return str(PurePosixPath(source.identity).with_suffix(".audit.json"))
        raise PathIdentityError(
            "runtime sidecar is outside the audit root and is not adjacent to "
            "an explicitly named external source"
        ) from None
    return normalize_portable_path(relative.as_posix())


def normalize_portable_path(value: str) -> str:
    """Normalize a caller-supplied logical name to a safe POSIX identity."""
    normalized = unicodedata.normalize("NFC", value).replace("\\", "/").strip()
    if _DRIVE_PREFIX.match(normalized):
        normalized = normalized[2:].lstrip("/")
    path = PurePosixPath(normalized)
    if not normalized or path.is_absolute():
        raise PathIdentityError("portable path must be relative")
    if any(part in {"", ".", ".."} for part in path.parts):
        raise PathIdentityError(
            "portable path must not contain empty, dot, or parent parts"
        )
    if any(ord(character) < 32 for character in normalized):
        raise PathIdentityError("portable path must not contain control characters")
    return path.as_posix()


def canonicalize_audit_metadata(
    metadata: Mapping[str, Any],
    *,
    plan: PathPlan,
    runtime_sidecar: Path | None = None,
) -> dict[str, Any]:
    """Replace host paths in audit metadata with public identities."""
    result = _deep_copy(metadata)
    raw_sources = result.get("sources")
    if isinstance(raw_sources, list):
        for item, public in zip(raw_sources, plan.sources, strict=False):
            if isinstance(item, dict):
                item["path"] = public.identity
                item["identity"] = public.metadata()
    runtime = result.get("runtime_input")
    if isinstance(runtime, dict) and runtime_sidecar is not None:
        runtime["path"] = canonical_sidecar_identity(runtime_sidecar, plan)
        runtime["identity_format"] = PORTABLE_PATH_FORMAT
    for key in ("source_repository", "loupe_repository"):
        repository = result.get(key)
        if isinstance(repository, dict):
            repository.pop("root", None)
    weavec = result.get("weavec")
    if isinstance(weavec, dict):
        weavec.pop("path", None)
        repository = weavec.get("repository")
        if isinstance(repository, dict):
            repository.pop("root", None)
    return _redact_mapping(result, plan)


def canonicalize_compiler_audit(
    document: Mapping[str, Any],
    *,
    plan: PathPlan,
) -> dict[str, Any]:
    """Rewrite public paths in compiler-audit evidence."""
    result = _deep_copy(document)
    raw_sources = result.get("sources")
    if not isinstance(raw_sources, list):
        raise PathIdentityError("compiler audit sources must be a list")
    if raw_sources:
        if len(raw_sources) != len(plan.sources):
            raise PathIdentityError(
                "compiler audit source evidence does not match the input plan"
            )
        canonical_sources: list[dict[str, Any]] = []
        for index, (raw_source, public) in enumerate(
            zip(raw_sources, plan.sources, strict=True)
        ):
            if not isinstance(raw_source, dict):
                raise PathIdentityError(
                    f"compiler audit source {index} must be an object"
                )
            item = dict(raw_source)
            item["index"] = index
            item["path"] = public.identity
            item["identity"] = public.metadata()
            canonical_sources.append(item)
        result["sources"] = canonical_sources
    for side in ("baseline", "candidate"):
        branch = result.get(side)
        if not isinstance(branch, dict):
            continue
        compiler = branch.get("compiler")
        if isinstance(compiler, dict):
            compiler.pop("path", None)
        for name in (
            "runtime",
            "native_budget",
            "optimized_llvm_budget",
        ):
            contract = branch.get(name)
            if not isinstance(contract, dict):
                continue
            raw_sidecar = contract.get("sidecar")
            if isinstance(raw_sidecar, str):
                contract["sidecar"] = _canonical_recorded_sidecar(
                    raw_sidecar,
                    plan,
                )
    return _redact_mapping(result, plan)


def redact_private_paths(
    text: str,
    *,
    plan: PathPlan,
    extra_prefixes: Sequence[Path | str] = (),
) -> str:
    """Replace known private filesystem prefixes in published text."""
    prefixes: list[tuple[str, str]] = []
    candidates: list[tuple[Path | str, str]] = [
        (plan.root, "$AUDIT_ROOT"),
        (Path.home(), "$HOME"),
    ]
    candidates.extend((value, "$WORKSPACE") for value in extra_prefixes)
    candidates.extend(
        (environment_path, "$WORKSPACE")
        for name in _PRIVATE_ENVIRONMENT
        if (environment_path := os.environ.get(name))
    )
    for value, replacement in candidates:
        raw = str(value)
        if not raw:
            continue
        variants = {
            raw,
            raw.replace("\\", "/"),
            raw.replace("/", "\\"),
        }
        prefixes.extend((variant.rstrip("/\\"), replacement) for variant in variants)
    ordered = sorted(set(prefixes), key=lambda item: -len(item[0]))
    for prefix, replacement in ordered:
        if prefix:
            text = text.replace(prefix, replacement)
    return text


def private_path_leaks(
    text: str,
    *,
    plan: PathPlan,
    extra_prefixes: Sequence[Path | str] = (),
) -> tuple[str, ...]:
    """Return known private prefixes still present in published text."""
    redacted = redact_private_paths(
        text,
        plan=plan,
        extra_prefixes=extra_prefixes,
    )
    if redacted == text:
        return ()
    leaks: list[str] = []
    for candidate in (plan.root, Path.home(), *extra_prefixes):
        raw = str(candidate)
        if raw and (raw in text or raw.replace("\\", "/") in text):
            leaks.append(raw)
    return tuple(dict.fromkeys(leaks))


def _select_root(
    sources: tuple[Path, ...],
    explicit: Path | None,
) -> tuple[Path, str]:
    if explicit is not None:
        root = _safe_resolve(explicit.expanduser())
        if not root.is_dir():
            raise PathIdentityError(f"audit root is not a directory: {explicit}")
        return root, "explicit"

    roots = tuple(_git_root(source.parent) for source in sources)
    available = {root for root in roots if root is not None}
    if len(available) == 1 and all(root is not None for root in roots):
        return available.pop(), "git"

    try:
        common = Path(os.path.commonpath([str(source.parent) for source in sources]))
    except ValueError as exc:
        raise PathIdentityError(
            "sources do not share a filesystem root; pass --audit-root"
        ) from exc
    return _safe_resolve(common), "common-parent"


def _git_root(directory: Path) -> Path | None:
    try:
        completed = subprocess.run(
            ["git", "-C", str(directory), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if completed.returncode != 0:
        return None
    value = completed.stdout.strip()
    return _safe_resolve(Path(value)) if value else None


def _logical_names(
    values: Sequence[str] | None,
    size: int,
) -> tuple[str | None, ...]:
    if values is None:
        return (None,) * size
    if len(values) != size:
        raise PathIdentityError(
            "the number of --source-name values must match the number of sources"
        )
    return tuple(value if value.strip() else None for value in values)


def _reject_identity_collisions(items: Sequence[PublicPath]) -> None:
    seen: dict[str, str] = {}
    for item in items:
        key = unicodedata.normalize("NFC", item.identity).casefold()
        previous = seen.get(key)
        if previous is not None:
            raise PathIdentityError(
                f"portable source identities collide: {previous!r} and "
                f"{item.identity!r}"
            )
        seen[key] = item.identity


def _canonical_recorded_sidecar(value: str, plan: PathPlan) -> str:
    path = Path(value)
    if path.is_file():
        return canonical_sidecar_identity(path, plan)
    normalized = value.replace("\\", "/")
    for source in plan.sources:
        suffix = str(PurePosixPath(source.identity).with_suffix(".audit.json"))
        if normalized.endswith(suffix) or Path(normalized).name == Path(suffix).name:
            return suffix
    return normalize_portable_path(Path(normalized).name)


def _redact_mapping(value: Mapping[str, Any], plan: PathPlan) -> dict[str, Any]:
    serialized = json.dumps(value, ensure_ascii=False)
    redacted = redact_private_paths(serialized, plan=plan)
    return cast(dict[str, Any], json.loads(redacted))


def _is_symlinked(path: Path) -> bool:
    try:
        return path.is_symlink()
    except OSError:
        return False


def _safe_resolve(path: Path) -> Path:
    try:
        return path.resolve(strict=False)
    except OSError:
        return path.absolute()


def _deep_copy(value: Mapping[str, Any]) -> dict[str, Any]:
    return cast(
        dict[str, Any],
        json.loads(json.dumps(value, ensure_ascii=False)),
    )
