"""Fail-closed structural and content verification for evidence bundles."""

from __future__ import annotations

import hashlib
import json
import re
import stat
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any, cast

BUNDLE_FORMAT = "weave-loupe-bundle-v1"
BUNDLE_VERIFICATION_FORMAT = "weave-loupe-bundle-verification-v1"
MANIFEST_NAME = "bundle.json"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_WINDOWS_DRIVE = re.compile(r"^[A-Za-z]:")
_REQUIRED_SUCCESS_ARTIFACTS = frozenset(
    {
        "assembly",
        "build_manifest",
        "diagnostics",
        "disassembly",
        "llvm",
        "optimization_record",
        "optimized_llvm",
        "trace",
        "wir",
    }
)


@dataclass(frozen=True)
class BundleProblem:
    """One stable bundle-integrity problem."""

    code: str
    location: str
    message: str

    def as_dict(self) -> dict[str, str]:
        """Return a deterministic machine-readable representation."""
        return {
            "code": self.code,
            "location": self.location,
            "message": self.message,
        }


@dataclass(frozen=True)
class BundleVerification:
    """Complete integrity result for one bundle."""

    root: Path
    closed: bool
    checked_files: int
    legacy_unhashed_logs: tuple[str, ...]
    problems: tuple[BundleProblem, ...]
    manifest: Mapping[str, Any] | None = field(
        default=None,
        repr=False,
        compare=False,
    )

    @property
    def valid(self) -> bool:
        """Whether every structural and content check passed."""
        return not self.problems

    def as_dict(self) -> dict[str, Any]:
        """Return versioned deterministic verification evidence."""
        return {
            "format": BUNDLE_VERIFICATION_FORMAT,
            "bundle": str(self.root),
            "closed": self.closed,
            "valid": self.valid,
            "checked_files": self.checked_files,
            "legacy_unhashed_logs": list(self.legacy_unhashed_logs),
            "problem_count": len(self.problems),
            "problems": [problem.as_dict() for problem in self.problems],
        }

    def error_message(self) -> str:
        """Render all detected problems for fail-closed callers."""
        if self.valid:
            return "bundle verified"
        details = "; ".join(
            f"{problem.location}: {problem.message}" for problem in self.problems
        )
        return f"bundle integrity verification failed: {details}"


def verify_bundle(path: Path, *, closed: bool = True) -> BundleVerification:
    """Verify every declared byte and path in a bundle without trusting it."""
    expanded = path.expanduser()
    root = expanded.resolve()
    problems: list[BundleProblem] = []
    declared_paths: dict[str, str] = {}
    checked_files = 0
    legacy_logs: list[str] = []

    if expanded.is_symlink():
        _problem(
            problems,
            "bundle-root-symlink",
            ".",
            "bundle root must not be a symbolic link",
        )
    if not root.exists():
        _problem(problems, "bundle-missing", ".", "bundle directory does not exist")
        return _verification(
            root, closed, checked_files, legacy_logs, problems, manifest=None
        )
    if not root.is_dir():
        _problem(
            problems,
            "bundle-not-directory",
            ".",
            "bundle root is not a directory",
        )
        return _verification(
            root, closed, checked_files, legacy_logs, problems, manifest=None
        )

    manifest = _load_manifest(root, problems)
    if manifest is None:
        return _verification(
            root, closed, checked_files, legacy_logs, problems, manifest=None
        )

    if manifest.get("format") != BUNDLE_FORMAT:
        _problem(
            problems,
            "unsupported-format",
            "format",
            f"bundle format must be {BUNDLE_FORMAT!r}",
        )

    compiler_exit_code = _validate_compiler(manifest.get("compiler"), problems)
    checked_files += _validate_sources(
        root,
        manifest.get("sources"),
        declared_paths,
        problems,
    )
    artifacts, artifact_checks = _validate_artifacts(
        root,
        manifest.get("artifacts"),
        declared_paths,
        problems,
    )
    checked_files += artifact_checks
    log_checks, legacy_log_entries = _validate_logs(
        root,
        manifest.get("logs"),
        declared_paths,
        problems,
    )
    checked_files += log_checks
    legacy_logs.extend(legacy_log_entries)

    if compiler_exit_code == 0:
        for name in sorted(_REQUIRED_SUCCESS_ARTIFACTS - artifacts):
            _problem(
                problems,
                "required-artifact-missing",
                f"artifacts.{name}",
                "successful compiler run is missing a required artifact",
            )

    if closed:
        _validate_closed_bundle(root, set(declared_paths), problems)

    return _verification(
        root,
        closed,
        checked_files,
        legacy_logs,
        problems,
        manifest=manifest,
    )


def _load_manifest(
    root: Path,
    problems: list[BundleProblem],
) -> dict[str, Any] | None:
    manifest_path = root / MANIFEST_NAME
    if manifest_path.is_symlink():
        _problem(
            problems,
            "manifest-symlink",
            MANIFEST_NAME,
            "bundle manifest must not be a symbolic link",
        )
    try:
        manifest_stat = manifest_path.stat(follow_symlinks=False)
    except FileNotFoundError:
        _problem(
            problems,
            "manifest-missing",
            MANIFEST_NAME,
            "bundle manifest does not exist",
        )
        return None
    except OSError as exc:
        _problem(
            problems,
            "manifest-unreadable",
            MANIFEST_NAME,
            f"bundle manifest cannot be inspected: {exc}",
        )
        return None
    if not stat.S_ISREG(manifest_stat.st_mode):
        _problem(
            problems,
            "manifest-not-regular",
            MANIFEST_NAME,
            "bundle manifest is not a regular file",
        )
        return None

    duplicate_keys: list[str] = []
    try:
        raw_manifest = json.loads(
            manifest_path.read_text(encoding="utf-8"),
            object_pairs_hook=_duplicate_key_hook(duplicate_keys),
        )
    except (OSError, json.JSONDecodeError) as exc:
        _problem(
            problems,
            "manifest-invalid-json",
            MANIFEST_NAME,
            f"bundle manifest is not valid UTF-8 JSON: {exc}",
        )
        return None
    for key in duplicate_keys:
        _problem(
            problems,
            "manifest-duplicate-key",
            MANIFEST_NAME,
            f"bundle manifest repeats JSON object key {key!r}",
        )
    if not isinstance(raw_manifest, dict):
        _problem(
            problems,
            "manifest-not-object",
            MANIFEST_NAME,
            "bundle manifest must be a JSON object",
        )
        return None
    return cast(dict[str, Any], raw_manifest)


def _validate_compiler(
    raw: object,
    problems: list[BundleProblem],
) -> int | None:
    if not isinstance(raw, dict):
        _problem(
            problems,
            "compiler-not-object",
            "compiler",
            "compiler metadata must be an object",
        )
        return None

    binary = raw.get("binary")
    if not isinstance(binary, str) or not binary:
        _problem(
            problems,
            "compiler-binary-invalid",
            "compiler.binary",
            "compiler binary must be a non-empty string",
        )

    command = raw.get("command")
    if not isinstance(command, list) or not all(
        isinstance(argument, str) for argument in command
    ):
        _problem(
            problems,
            "compiler-command-invalid",
            "compiler.command",
            "compiler command must be a list of strings",
        )

    exit_code = raw.get("exit_code")
    if not isinstance(exit_code, int) or isinstance(exit_code, bool):
        _problem(
            problems,
            "compiler-exit-code-invalid",
            "compiler.exit_code",
            "compiler exit code must be an integer",
        )
        return None
    return exit_code


def _validate_sources(
    root: Path,
    raw: object,
    declared_paths: dict[str, str],
    problems: list[BundleProblem],
) -> int:
    if not isinstance(raw, list):
        _problem(
            problems,
            "sources-not-list",
            "sources",
            "bundle sources must be a list",
        )
        return 0
    if not raw:
        _problem(
            problems,
            "sources-empty",
            "sources",
            "bundle must declare at least one source",
        )

    checked = 0
    for expected_index, item in enumerate(raw):
        location = f"sources[{expected_index}]"
        if not isinstance(item, dict):
            _problem(
                problems,
                "source-not-object",
                location,
                "source entry must be an object",
            )
            continue
        index = item.get("index")
        if (
            not isinstance(index, int)
            or isinstance(index, bool)
            or index != expected_index
        ):
            _problem(
                problems,
                "source-index-invalid",
                f"{location}.index",
                f"source index must equal ordered position {expected_index}",
            )
        input_name = item.get("input")
        if input_name is not None and not isinstance(input_name, str):
            _problem(
                problems,
                "source-input-invalid",
                f"{location}.input",
                "source input identity must be a string when present",
            )
        if _validate_file_entry(
            root,
            item,
            location,
            declared_paths,
            problems,
        ):
            checked += 1
    return checked


def _validate_artifacts(
    root: Path,
    raw: object,
    declared_paths: dict[str, str],
    problems: list[BundleProblem],
) -> tuple[set[str], int]:
    if not isinstance(raw, dict):
        _problem(
            problems,
            "artifacts-not-object",
            "artifacts",
            "bundle artifacts must be an object",
        )
        return set(), 0

    names: set[str] = set()
    checked = 0
    for name, item in raw.items():
        location = f"artifacts.{name}"
        if not isinstance(name, str) or not name:
            _problem(
                problems,
                "artifact-name-invalid",
                "artifacts",
                "artifact names must be non-empty strings",
            )
            continue
        names.add(name)
        if not isinstance(item, dict):
            _problem(
                problems,
                "artifact-not-object",
                location,
                "artifact entry must be an object",
            )
            continue
        if _validate_file_entry(
            root,
            item,
            location,
            declared_paths,
            problems,
        ):
            checked += 1
    return names, checked


def _validate_logs(
    root: Path,
    raw: object,
    declared_paths: dict[str, str],
    problems: list[BundleProblem],
) -> tuple[int, list[str]]:
    if not isinstance(raw, dict):
        _problem(
            problems,
            "logs-not-object",
            "logs",
            "bundle logs must be an object",
        )
        return 0, []

    checked = 0
    legacy_logs: list[str] = []
    for required_name in ("stdout", "stderr"):
        if required_name not in raw:
            _problem(
                problems,
                "required-log-missing",
                f"logs.{required_name}",
                "bundle must declare both compiler logs",
            )

    for name, item in raw.items():
        location = f"logs.{name}"
        if not isinstance(name, str) or not name:
            _problem(
                problems,
                "log-name-invalid",
                "logs",
                "log names must be non-empty strings",
            )
            continue
        if isinstance(item, str):
            legacy_logs.append(name)
            relative_path = _validate_path_text(item, location, problems)
            if relative_path is None:
                continue
            _register_path(relative_path, location, declared_paths, problems)
            if _validate_file(
                root,
                relative_path,
                location,
                problems,
                expected_size=None,
                expected_sha256=None,
            ):
                checked += 1
            continue
        if not isinstance(item, dict):
            _problem(
                problems,
                "log-entry-invalid",
                location,
                "log entry must be a file entry or legacy path string",
            )
            continue
        if _validate_file_entry(
            root,
            item,
            location,
            declared_paths,
            problems,
        ):
            checked += 1
    return checked, legacy_logs


def _validate_file_entry(
    root: Path,
    item: Mapping[str, Any],
    location: str,
    declared_paths: dict[str, str],
    problems: list[BundleProblem],
) -> bool:
    relative_path = _validate_path_text(item.get("path"), f"{location}.path", problems)

    size = item.get("size")
    if not isinstance(size, int) or isinstance(size, bool) or size < 0:
        _problem(
            problems,
            "file-size-invalid",
            f"{location}.size",
            "declared file size must be a non-negative integer",
        )
        expected_size: int | None = None
    else:
        expected_size = size

    digest = item.get("sha256")
    if not isinstance(digest, str) or _SHA256.fullmatch(digest) is None:
        _problem(
            problems,
            "file-digest-invalid",
            f"{location}.sha256",
            "declared SHA-256 must be 64 lowercase hexadecimal characters",
        )
        expected_digest: str | None = None
    else:
        expected_digest = digest

    if relative_path is None:
        return False
    _register_path(relative_path, location, declared_paths, problems)
    return _validate_file(
        root,
        relative_path,
        location,
        problems,
        expected_size=expected_size,
        expected_sha256=expected_digest,
    )


def _validate_path_text(
    raw: object,
    location: str,
    problems: list[BundleProblem],
) -> str | None:
    if not isinstance(raw, str) or not raw:
        _problem(
            problems,
            "file-path-invalid",
            location,
            "bundle file path must be a non-empty string",
        )
        return None
    if "\x00" in raw:
        _problem(
            problems,
            "file-path-nul",
            location,
            "bundle file path must not contain a NUL byte",
        )
        return None
    if "\\" in raw:
        _problem(
            problems,
            "file-path-backslash",
            location,
            "bundle file path must use POSIX separators",
        )
        return None

    path = PurePosixPath(raw)
    if path.is_absolute() or _WINDOWS_DRIVE.match(raw):
        _problem(
            problems,
            "file-path-absolute",
            location,
            "bundle file path must be relative",
        )
        return None
    normalized = path.as_posix()
    if any(part == ".." for part in path.parts):
        _problem(
            problems,
            "file-path-traversal",
            location,
            "bundle file path must not contain parent components",
        )
        return None
    if normalized != raw:
        _problem(
            problems,
            "file-path-noncanonical",
            location,
            f"bundle file path must be canonical POSIX form {normalized!r}",
        )
        return None
    if normalized == MANIFEST_NAME:
        _problem(
            problems,
            "file-path-manifest-conflict",
            location,
            "bundle content entries must not replace bundle.json",
        )
        return None
    return normalized


def _register_path(
    relative_path: str,
    location: str,
    declared_paths: dict[str, str],
    problems: list[BundleProblem],
) -> None:
    previous = declared_paths.get(relative_path)
    if previous is None:
        declared_paths[relative_path] = location
        return
    _problem(
        problems,
        "duplicate-declared-path",
        location,
        f"path {relative_path!r} is already declared by {previous}",
    )


def _validate_file(
    root: Path,
    relative_path: str,
    location: str,
    problems: list[BundleProblem],
    *,
    expected_size: int | None,
    expected_sha256: str | None,
) -> bool:
    candidate = root.joinpath(*PurePosixPath(relative_path).parts)
    symlink = _first_symlink(root, candidate)
    if symlink is not None:
        _problem(
            problems,
            "file-symlink",
            location,
            "bundle path contains symbolic link "
            f"{symlink.relative_to(root).as_posix()!r}",
        )
        return False

    try:
        file_stat = candidate.stat(follow_symlinks=False)
    except FileNotFoundError:
        _problem(
            problems,
            "file-missing",
            location,
            f"declared file {relative_path!r} does not exist",
        )
        return False
    except OSError as exc:
        _problem(
            problems,
            "file-unreadable",
            location,
            f"declared file {relative_path!r} cannot be inspected: {exc}",
        )
        return False
    if not stat.S_ISREG(file_stat.st_mode):
        _problem(
            problems,
            "file-not-regular",
            location,
            f"declared path {relative_path!r} is not a regular file",
        )
        return False

    try:
        data = candidate.read_bytes()
    except OSError as exc:
        _problem(
            problems,
            "file-unreadable",
            location,
            f"declared file {relative_path!r} cannot be read: {exc}",
        )
        return False
    if expected_size is not None and len(data) != expected_size:
        _problem(
            problems,
            "file-size-mismatch",
            location,
            f"declared size {expected_size} does not match {len(data)} bytes",
        )
    if expected_sha256 is not None:
        actual_digest = hashlib.sha256(data).hexdigest()
        if actual_digest != expected_sha256:
            _problem(
                problems,
                "file-digest-mismatch",
                location,
                f"declared SHA-256 does not match {actual_digest}",
            )
    return True


def _validate_closed_bundle(
    root: Path,
    declared_paths: set[str],
    problems: list[BundleProblem],
) -> None:
    try:
        candidates = sorted(
            root.rglob("*"),
            key=lambda path: path.relative_to(root).as_posix(),
        )
    except OSError as exc:
        _problem(
            problems,
            "bundle-enumeration-failed",
            ".",
            f"bundle contents cannot be enumerated: {exc}",
        )
        return

    for candidate in candidates:
        relative_path = candidate.relative_to(root).as_posix()
        if relative_path == MANIFEST_NAME:
            continue
        if candidate.is_symlink():
            if relative_path not in declared_paths:
                _problem(
                    problems,
                    "undeclared-symlink",
                    relative_path,
                    "closed bundle contains an undeclared symbolic link",
                )
            continue
        try:
            candidate_stat = candidate.stat(follow_symlinks=False)
        except OSError as exc:
            _problem(
                problems,
                "bundle-entry-unreadable",
                relative_path,
                f"bundle entry cannot be inspected: {exc}",
            )
            continue
        if stat.S_ISDIR(candidate_stat.st_mode):
            continue
        if not stat.S_ISREG(candidate_stat.st_mode):
            _problem(
                problems,
                "bundle-entry-not-regular",
                relative_path,
                "closed bundle contains a non-regular undeclared entry",
            )
            continue
        if relative_path not in declared_paths:
            _problem(
                problems,
                "undeclared-file",
                relative_path,
                "closed bundle contains a file not declared by bundle.json",
            )


def _first_symlink(root: Path, candidate: Path) -> Path | None:
    current = root
    for part in candidate.relative_to(root).parts:
        current /= part
        if current.is_symlink():
            return current
    return None


def _verification(
    root: Path,
    closed: bool,
    checked_files: int,
    legacy_logs: Sequence[str],
    problems: Sequence[BundleProblem],
    *,
    manifest: Mapping[str, Any] | None,
) -> BundleVerification:
    return BundleVerification(
        root=root,
        closed=closed,
        checked_files=checked_files,
        legacy_unhashed_logs=tuple(sorted(legacy_logs)),
        problems=tuple(
            sorted(
                problems,
                key=lambda problem: (
                    problem.location,
                    problem.code,
                    problem.message,
                ),
            )
        ),
        manifest=manifest,
    )


def _problem(
    problems: list[BundleProblem],
    code: str,
    location: str,
    message: str,
) -> None:
    problems.append(BundleProblem(code=code, location=location, message=message))


def _duplicate_key_hook(
    duplicate_keys: list[str],
) -> Callable[[list[tuple[str, Any]]], dict[str, Any]]:
    def build_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                duplicate_keys.append(key)
            result[key] = value
        return result

    return build_object
