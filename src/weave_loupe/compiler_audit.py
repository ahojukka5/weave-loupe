"""Baseline-versus-candidate compiler regression audits."""

from __future__ import annotations

import hashlib
import json
import shutil
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from weave_loupe.analysis import analyze_bundle
from weave_loupe.auditor_identity import sha256_file
from weave_loupe.bundle import Bundle, BundleError, capture_bundle, load_bundle
from weave_loupe.compiler_version import identify_weavec
from weave_loupe.diffing import compare_bundles
from weave_loupe.native_budget import evaluate_native_budget
from weave_loupe.optimized_llvm_budget import evaluate_optimized_llvm_budget
from weave_loupe.runtime_cases import execute_runtime_cases

COMPILER_AUDIT_FORMAT = "weave-loupe-compiler-audit-v1"
COMPILER_AUDIT_POLICY_FORMAT = "weave-loupe-compiler-audit-policy-v1"
COMPILER_AUDIT_SEAL_FORMAT = "weave-loupe-canonical-json-sha256-v1"

_DEFAULT_RULES: dict[str, tuple[int | None, int | None]] = {
    "analysis.optimized_llvm.functions": (None, 0),
    "analysis.optimized_llvm.instructions": (None, 0),
    "analysis.optimized_llvm.alloca": (None, 0),
    "analysis.optimized_llvm.load": (None, 0),
    "analysis.optimized_llvm.store": (None, 0),
    "analysis.optimized_llvm.call": (None, 0),
    "analysis.optimized_llvm.identity_adds": (None, 0),
    "analysis.optimized_llvm.undef_uses": (None, 0),
    "analysis.optimized_llvm.poison_uses": (None, 0),
    "analysis.native.unreachable_program_instructions": (None, 0),
    "analysis.native.reachable_indirect_calls": (None, 0),
}
_POLICY_FIELDS = {"format", "metric_deltas", "forbid_changes"}
_FORBIDDEN_KINDS = {
    "diagnostics",
    "evidence",
    "runtime",
    "native_budget",
    "optimized_llvm_budget",
}
_ALWAYS_FORBIDDEN = {"runtime", "native_budget", "optimized_llvm_budget"}
_RUNTIME_VOLATILE = {
    "elapsed_seconds",
    "executable_sha256",
    "limits",
    "sandbox",
    "sidecar",
    "timeout_seconds",
}


class CompilerAuditError(ValueError):
    """Raised when a differential audit cannot be configured or executed."""


@dataclass(frozen=True)
class MetricDeltaRule:
    """Allowed inclusive delta interval for one numeric evidence path."""

    minimum: int | None
    maximum: int | None

    def as_dict(self) -> dict[str, int | None]:
        return {"minimum": self.minimum, "maximum": self.maximum}


@dataclass(frozen=True)
class CompilerAuditPolicy:
    """Validated deterministic differential policy."""

    metric_deltas: Mapping[str, MetricDeltaRule]
    forbid_changes: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "format": COMPILER_AUDIT_POLICY_FORMAT,
            "metric_deltas": {
                path: rule.as_dict()
                for path, rule in sorted(self.metric_deltas.items())
            },
            "forbid_changes": list(self.forbid_changes),
        }


ReviewCallback = Callable[[Mapping[str, Any]], Mapping[str, Any]]


def resolve_compiler_input(path: Path) -> Path:
    """Resolve an executable or a repository checkout containing one."""
    resolved = path.expanduser().resolve()
    if resolved.is_file():
        return resolved
    if resolved.is_dir():
        candidates = (resolved / "build" / "weavec", resolved / "weavec")
        for candidate in candidates:
            if candidate.is_file():
                return candidate
        raise CompilerAuditError(
            f"compiler checkout has no built weavec binary: {resolved}; "
            "run its build before auditing"
        )
    raise CompilerAuditError(f"compiler input does not exist: {resolved}")


def load_compiler_audit_policy(path: Path | None) -> CompilerAuditPolicy:
    """Load an optional policy and merge it with fail-closed defaults."""
    document = _read_policy(path)
    rules = {
        name: MetricDeltaRule(minimum=limits[0], maximum=limits[1])
        for name, limits in _DEFAULT_RULES.items()
    }
    raw_rules = document.get("metric_deltas", {})
    if not isinstance(raw_rules, dict):
        raise CompilerAuditError("metric_deltas must be a JSON object")
    for path_name, raw_rule in raw_rules.items():
        rules[_rule_name(path_name)] = _parse_rule(path_name, raw_rule)

    raw_forbidden = document.get("forbid_changes", ["diagnostics", "evidence"])
    if not isinstance(raw_forbidden, list) or not all(
        isinstance(item, str) for item in raw_forbidden
    ):
        raise CompilerAuditError("forbid_changes must be a list of strings")
    forbidden = set(raw_forbidden) | _ALWAYS_FORBIDDEN
    unknown = sorted(forbidden - _FORBIDDEN_KINDS)
    if unknown:
        raise CompilerAuditError(
            "forbid_changes contains unknown values: " + ", ".join(unknown)
        )
    return CompilerAuditPolicy(
        metric_deltas=dict(sorted(rules.items())),
        forbid_changes=tuple(sorted(forbidden)),
    )


def audit_compilers(
    *,
    sources: Sequence[Path],
    baseline_weavec: Path,
    candidate_weavec: Path,
    work_dir: Path,
    policy_path: Path | None = None,
    compiler_timeout_seconds: float | None = None,
    compiler_output_bytes: int | None = None,
    runtime_timeout_seconds: float | None = None,
    runtime_output_bytes: int | None = None,
    reviewer: ReviewCallback | None = None,
) -> dict[str, Any]:
    """Compile identical inputs twice and return a sealed regression verdict."""
    ordered_sources = [Path(source) for source in sources]
    if not ordered_sources:
        raise CompilerAuditError("at least one source is required")
    baseline_binary = resolve_compiler_input(baseline_weavec)
    candidate_binary = resolve_compiler_input(candidate_weavec)
    policy = load_compiler_audit_policy(policy_path)
    baseline_bundle, candidate_bundle = _capture_pair(
        sources=ordered_sources,
        baseline_weavec=baseline_binary,
        candidate_weavec=candidate_binary,
        work_dir=work_dir,
        compiler_timeout_seconds=compiler_timeout_seconds,
        compiler_output_bytes=compiler_output_bytes,
    )
    baseline = _compiler_result(
        bundle=baseline_bundle,
        compiler=baseline_binary,
        sources=ordered_sources,
        runtime_timeout_seconds=runtime_timeout_seconds,
        runtime_output_bytes=runtime_output_bytes,
    )
    candidate = _compiler_result(
        bundle=candidate_bundle,
        compiler=candidate_binary,
        sources=ordered_sources,
        runtime_timeout_seconds=runtime_timeout_seconds,
        runtime_output_bytes=runtime_output_bytes,
    )
    metric_deltas = _metric_deltas(baseline, candidate, policy)
    failures = _failures(
        baseline=baseline,
        candidate=candidate,
        policy=policy,
        metric_deltas=metric_deltas,
    )
    infrastructure = any(
        failure["category"] == "infrastructure" for failure in failures
    )
    report: dict[str, Any] = {
        "format": COMPILER_AUDIT_FORMAT,
        "status": _status(failures=failures, infrastructure=infrastructure),
        "passed": not failures,
        "sources": _source_identities(ordered_sources),
        "policy": policy.as_dict(),
        "baseline": baseline,
        "candidate": candidate,
        "comparison": {
            "bundle_diff": compare_bundles(
                baseline_bundle,
                candidate_bundle,
                before_context=baseline,
                after_context=candidate,
            ),
            "metric_deltas": metric_deltas,
            "runtime_equal": _stable_runtime(baseline["runtime"])
            == _stable_runtime(candidate["runtime"]),
            "diagnostics_equal": baseline["analysis"]["diagnostics"]
            == candidate["analysis"]["diagnostics"],
            "evidence_equal": baseline["analysis"]["evidence"]
            == candidate["analysis"]["evidence"],
        },
        "failures": failures,
        "review": None,
    }
    if reviewer is not None:
        review = reviewer(report)
        if not isinstance(review, Mapping):
            raise CompilerAuditError("compiler audit reviewer must return a mapping")
        report["review"] = dict(review)
    return seal_compiler_audit(report)


def seal_compiler_audit(document: Mapping[str, Any]) -> dict[str, Any]:
    """Attach a canonical SHA-256 seal without hashing the seal itself."""
    unsealed = dict(document)
    unsealed.pop("seal", None)
    canonical = json.dumps(
        unsealed,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return {
        **unsealed,
        "seal": {
            "format": COMPILER_AUDIT_SEAL_FORMAT,
            "sha256": hashlib.sha256(canonical).hexdigest(),
        },
    }


def _capture_pair(
    *,
    sources: list[Path],
    baseline_weavec: Path,
    candidate_weavec: Path,
    work_dir: Path,
    compiler_timeout_seconds: float | None,
    compiler_output_bytes: int | None,
) -> tuple[Bundle, Bundle]:
    root = work_dir.expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    outputs = (root / "baseline.loupe", root / "candidate.loupe")
    for output in outputs:
        _remove_existing(output)
    try:
        baseline = capture_bundle(
            sources=sources,
            output=outputs[0],
            weavec=baseline_weavec,
            include_executable=True,
            compiler_timeout_seconds=compiler_timeout_seconds,
            compiler_output_bytes=compiler_output_bytes,
        )
        candidate = capture_bundle(
            sources=sources,
            output=outputs[1],
            weavec=candidate_weavec,
            include_executable=True,
            compiler_timeout_seconds=compiler_timeout_seconds,
            compiler_output_bytes=compiler_output_bytes,
        )
        return load_bundle(baseline.bundle), load_bundle(candidate.bundle)
    except BundleError as exc:
        raise CompilerAuditError(str(exc)) from exc


def _compiler_result(
    *,
    bundle: Bundle,
    compiler: Path,
    sources: list[Path],
    runtime_timeout_seconds: float | None,
    runtime_output_bytes: int | None,
) -> dict[str, Any]:
    analysis = analyze_bundle(bundle)
    if analysis["compiler_exit_code"] == 0:
        optimized_budget = evaluate_optimized_llvm_budget(
            sources=sources,
            optimized_llvm=bundle.artifact_text("optimized_llvm") or "",
            metrics=analysis.get("optimized_llvm"),
        )
        native_budget = evaluate_native_budget(
            sources=sources,
            native_analysis=analysis.get("native"),
        )
        runtime = execute_runtime_cases(
            bundle=bundle,
            sources=sources,
            runtime_timeout_seconds=runtime_timeout_seconds,
            runtime_output_bytes=runtime_output_bytes,
        )
    else:
        skipped = {
            "configured": None,
            "passed": False,
            "skipped": True,
            "reason": "compiler did not produce a successful executable",
        }
        optimized_budget = dict(skipped)
        native_budget = dict(skipped)
        runtime = dict(skipped)
    return {
        "compiler": _compiler_identity(compiler),
        "compiler_exit_code": analysis["compiler_exit_code"],
        "analysis": analysis,
        "optimized_llvm_budget": optimized_budget,
        "native_budget": native_budget,
        "runtime": runtime,
        "artifacts": _artifact_identities(bundle),
    }


def _failures(
    *,
    baseline: Mapping[str, Any],
    candidate: Mapping[str, Any],
    policy: CompilerAuditPolicy,
    metric_deltas: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    baseline_exit = baseline.get("compiler_exit_code")
    candidate_exit = candidate.get("compiler_exit_code")
    if baseline_exit != 0:
        failures.append(
            _failure(
                "infrastructure",
                "baseline-compilation-failed",
                f"baseline compiler exited with {baseline_exit}",
            )
        )
    if baseline_exit == 0 and candidate_exit != 0:
        failures.append(
            _failure(
                "semantic",
                "candidate-compilation-failed",
                f"candidate compiler exited with {candidate_exit}",
            )
        )
    if baseline_exit != 0 or candidate_exit != 0:
        return failures

    _check_runtime(baseline, candidate, policy, failures)
    _check_contracts(baseline, candidate, policy, failures)
    _check_summaries(baseline, candidate, policy, failures)
    for delta in metric_deltas:
        if delta["passed"] is True:
            continue
        if delta["available"] is not True:
            detail = f"{delta['path']} is unavailable for deterministic comparison"
        else:
            detail = (
                f"{delta['path']} delta {delta['delta']} is outside "
                f"[{delta['minimum']}, {delta['maximum']}]"
            )
        failures.append(
            _failure(
                "quality",
                "metric-delta-outside-policy",
                detail,
                evidence=delta,
            )
        )
    return failures


def _check_runtime(
    baseline: Mapping[str, Any],
    candidate: Mapping[str, Any],
    policy: CompilerAuditPolicy,
    failures: list[dict[str, Any]],
) -> None:
    before = baseline["runtime"]
    after = candidate["runtime"]
    if after.get("passed") is not True:
        failures.append(
            _failure(
                "semantic",
                "candidate-runtime-failed",
                "candidate runtime matrix did not satisfy the versioned sidecar",
            )
        )
    if "runtime" in policy.forbid_changes and _stable_runtime(
        before
    ) != _stable_runtime(after):
        failures.append(
            _failure(
                "semantic",
                "runtime-observations-changed",
                "candidate runtime observations differ from the baseline",
            )
        )


def _check_contracts(
    baseline: Mapping[str, Any],
    candidate: Mapping[str, Any],
    policy: CompilerAuditPolicy,
    failures: list[dict[str, Any]],
) -> None:
    for name, code in (
        ("optimized_llvm_budget", "optimized-llvm-budget-failed"),
        ("native_budget", "native-budget-failed"),
    ):
        after = candidate[name]
        if after.get("passed") is not True:
            failures.append(
                _failure(
                    "quality",
                    code,
                    f"candidate {name.replace('_', ' ')} did not pass",
                )
            )
        if name in policy.forbid_changes and _stable_contract(
            baseline[name]
        ) != _stable_contract(after):
            failures.append(
                _failure(
                    "quality",
                    f"{name.replace('_', '-')}-changed",
                    f"candidate {name.replace('_', ' ')} evidence differs",
                )
            )


def _check_summaries(
    baseline: Mapping[str, Any],
    candidate: Mapping[str, Any],
    policy: CompilerAuditPolicy,
    failures: list[dict[str, Any]],
) -> None:
    before = baseline["analysis"]
    after = candidate["analysis"]
    if (
        "diagnostics" in policy.forbid_changes
        and before["diagnostics"] != after["diagnostics"]
    ):
        failures.append(
            _failure(
                "semantic",
                "diagnostics-changed",
                "candidate diagnostics summary differs from the baseline",
            )
        )
    if "evidence" in policy.forbid_changes and before["evidence"] != after["evidence"]:
        failures.append(
            _failure(
                "evidence",
                "artifact-presence-changed",
                "candidate evidence availability differs from the baseline",
            )
        )


def _metric_deltas(
    baseline: Mapping[str, Any],
    candidate: Mapping[str, Any],
    policy: CompilerAuditPolicy,
) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    for path, rule in sorted(policy.metric_deltas.items()):
        before = _numeric_path(baseline, path)
        after = _numeric_path(candidate, path)
        if before is None or after is None:
            delta = None
            passed = False
        else:
            delta = after - before
            passed = (rule.minimum is None or delta >= rule.minimum) and (
                rule.maximum is None or delta <= rule.maximum
            )
        changes.append(
            {
                "path": path,
                "available": before is not None and after is not None,
                "before": before,
                "after": after,
                "delta": delta,
                "minimum": rule.minimum,
                "maximum": rule.maximum,
                "passed": passed,
            }
        )
    return changes


def _compiler_identity(binary: Path) -> dict[str, Any]:
    version = identify_weavec(binary)
    return {
        "path": str(binary),
        "sha256": sha256_file(binary),
        "version": version.display,
        "base_version": version.base,
        "git_sha": version.git_sha,
        "development": version.development,
        "version_source": version.source,
    }


def _artifact_identities(bundle: Bundle) -> dict[str, dict[str, Any]]:
    raw = bundle.manifest.get("artifacts")
    if not isinstance(raw, Mapping):
        return {}
    result: dict[str, dict[str, Any]] = {}
    for name, item in sorted(raw.items()):
        if not isinstance(name, str) or not isinstance(item, Mapping):
            continue
        digest, size = item.get("sha256"), item.get("size")
        if isinstance(digest, str) and isinstance(size, int):
            result[name] = {"sha256": digest, "size": size}
    return result


def _source_identities(sources: Sequence[Path]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for index, source in enumerate(sources):
        data = source.expanduser().resolve().read_bytes()
        result.append(
            {
                "index": index,
                "path": str(source),
                "sha256": hashlib.sha256(data).hexdigest(),
                "size": len(data),
            }
        )
    return result


def _stable_runtime(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            key: _stable_runtime(item)
            for key, item in sorted(value.items())
            if key not in _RUNTIME_VOLATILE
        }
    if isinstance(value, list):
        return [_stable_runtime(item) for item in value]
    return value


def _stable_contract(value: Any) -> Any:
    if not isinstance(value, Mapping):
        return value
    return {
        key: _stable_contract(item)
        for key, item in sorted(value.items())
        if key not in {"sidecar", "sidecar_sha256"}
    }


def _numeric_path(document: Mapping[str, Any], path: str) -> int | None:
    value: Any = document
    for component in path.split("."):
        if not isinstance(value, Mapping) or component not in value:
            return None
        value = value[component]
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _status(*, failures: list[dict[str, Any]], infrastructure: bool) -> str:
    if infrastructure:
        return "infrastructure-failure"
    return "regression" if failures else "pass"


def _failure(
    category: str,
    code: str,
    detail: str,
    *,
    evidence: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "category": category,
        "code": code,
        "detail": detail,
    }
    if evidence is not None:
        result["evidence"] = dict(evidence)
    return result


def _read_policy(path: Path | None) -> Mapping[str, Any]:
    if path is None:
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        message = f"invalid compiler audit policy {path}: {exc}"
        raise CompilerAuditError(message) from exc
    if not isinstance(value, dict):
        raise CompilerAuditError("compiler audit policy must be a JSON object")
    if value.get("format") != COMPILER_AUDIT_POLICY_FORMAT:
        raise CompilerAuditError(
            f"compiler audit policy format must be {COMPILER_AUDIT_POLICY_FORMAT!r}"
        )
    unknown = sorted(set(value) - _POLICY_FIELDS)
    if unknown:
        raise CompilerAuditError(
            "compiler audit policy contains unknown fields: " + ", ".join(unknown)
        )
    return value


def _rule_name(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CompilerAuditError("metric delta paths must be non-empty strings")
    return value


def _parse_rule(path_name: object, value: object) -> MetricDeltaRule:
    if not isinstance(value, dict):
        raise CompilerAuditError(
            f"metric delta rule {path_name!r} must be a JSON object"
        )
    unknown = sorted(set(value) - {"minimum", "maximum"})
    if unknown:
        raise CompilerAuditError(
            f"metric delta rule {path_name!r} contains unknown fields: "
            + ", ".join(unknown)
        )
    minimum = _optional_integer(value.get("minimum"), f"{path_name}.minimum")
    maximum = _optional_integer(value.get("maximum"), f"{path_name}.maximum")
    if minimum is None and maximum is None:
        raise CompilerAuditError(
            f"metric delta rule {path_name!r} requires minimum or maximum"
        )
    if minimum is not None and maximum is not None and minimum > maximum:
        raise CompilerAuditError(
            f"metric delta rule {path_name!r} minimum exceeds maximum"
        )
    return MetricDeltaRule(minimum=minimum, maximum=maximum)


def _optional_integer(value: object, name: str) -> int | None:
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        raise CompilerAuditError(f"{name} must be an integer or null")
    return value


def _remove_existing(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()
