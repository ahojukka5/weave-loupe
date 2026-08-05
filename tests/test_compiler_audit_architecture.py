"""Architecture tests for the staged compiler audit pipeline."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from weave_loupe.compiler_audit import (
    COMPILER_AUDIT_FORMAT,
    COMPILER_AUDIT_POLICY_FORMAT,
    COMPILER_AUDIT_SEAL_FORMAT,
    CompilerAuditError,
    CompilerAuditPolicy,
    MetricDeltaRule,
    audit_compilers,
    load_compiler_audit_policy,
    resolve_compiler_input,
    seal_compiler_audit,
)
from weave_loupe.compiler_audit.policy import evaluate_compiler_audit_policy


def test_public_compiler_audit_facade_remains_compatible() -> None:
    assert COMPILER_AUDIT_FORMAT == "weave-loupe-compiler-audit-v1"
    assert COMPILER_AUDIT_POLICY_FORMAT == "weave-loupe-compiler-audit-policy-v1"
    assert COMPILER_AUDIT_SEAL_FORMAT == "weave-loupe-canonical-json-sha256-v1"
    assert issubclass(CompilerAuditError, ValueError)
    assert CompilerAuditPolicy
    assert MetricDeltaRule
    assert callable(audit_compilers)
    assert callable(load_compiler_audit_policy)
    assert callable(resolve_compiler_input)
    assert callable(seal_compiler_audit)


def test_policy_evaluation_is_independent_of_compiler_acquisition() -> None:
    observation = _observation()
    policy = CompilerAuditPolicy(metric_deltas={}, forbid_changes=())
    failures = evaluate_compiler_audit_policy(
        baseline=observation,
        candidate=observation,
        policy=policy,
        comparison={"metric_deltas": []},
    )
    assert failures == []


def test_pure_stages_do_not_import_compiler_execution() -> None:
    package = Path(__file__).parents[1] / "src" / "weave_loupe" / "compiler_audit"
    forbidden = {
        "weave_loupe.bundle.capture",
        "weave_loupe.compiler_version",
        "weave_loupe.runtime_cases",
        "weave_loupe.weavec",
    }
    for name in ("comparison.py", "policy.py", "reporting.py"):
        imported = _imports(package / name)
        assert imported.isdisjoint(forbidden), (name, imported & forbidden)
    reporting_imports = _imports(package / "reporting.py")
    assert "weave_loupe.compiler_audit.acquisition" not in reporting_imports


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    result: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            result.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            if node.level:
                package = "weave_loupe.compiler_audit"
                components = package.split(".")
                prefix = components[: len(components) - node.level + 1]
                result.add(".".join([*prefix, node.module]))
            else:
                result.add(node.module)
    return result


def _observation() -> dict[str, Any]:
    return {
        "compiler_exit_code": 0,
        "runtime": {"passed": True},
        "optimized_llvm_budget": {"passed": True},
        "native_budget": {"passed": True},
        "analysis": {
            "diagnostics": {},
            "evidence": {},
        },
    }
