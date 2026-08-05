"""Shared models for compiler regression audits."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from weave_loupe.bundle import Bundle

COMPILER_AUDIT_FORMAT = "weave-loupe-compiler-audit-v1"
COMPILER_AUDIT_POLICY_FORMAT = "weave-loupe-compiler-audit-policy-v1"
COMPILER_AUDIT_SEAL_FORMAT = "weave-loupe-canonical-json-sha256-v1"


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


@dataclass(frozen=True)
class CompilerEvidence:
    """One verified compiler bundle and its derived audit observations."""

    bundle: Bundle
    result: Mapping[str, Any]


ReviewCallback = Callable[[Mapping[str, Any]], Mapping[str, Any]]
