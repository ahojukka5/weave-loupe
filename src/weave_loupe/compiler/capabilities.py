"""Validate the compiler-authoritative capability registry contract."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, NoReturn

CAPABILITIES_FORMAT = "weavec-capabilities-v1"
CAPABILITY_IDENTITY_FORMAT = "weave-loupe-weavec-capability-identity-v1"
CAPTURE_PROFILE_FORMAT = "weave-loupe-capture-profile-v1"
CAPABILITIES_SCHEMA_ID = "urn:weavec:schema:capabilities:v1"
CAPABILITIES_SCHEMA_VERSION = 1
EXPECTED_SURFACE_VERSION = "weave-surface-v1"
EXPECTED_GRAMMAR_ID = "weave-surface-grammar-v1"
EXPECTED_WIR_CORE_VERSION = 2

REQUIRED_PROTOCOLS: Mapping[str, int] = {
    "weavec-capabilities-v1": 1,
    "weavec-build-manifest-v1": 1,
    "weavec-diagnostics-v1": 1,
    "weavec-compilation-trace-v1": 1,
    "weave-wir-core-v2": 2,
}
REQUIRED_CAPTURE_OUTPUTS = (
    "executable",
    "wir",
    "llvm",
    "optimized_llvm",
    "assembly",
    "disassembly",
    "optimization_record",
    "diagnostics",
    "trace",
    "build_manifest",
    "llvm_provenance",
)


class CompilerCapabilityError(ValueError):
    """Raised when an installed compiler cannot satisfy Loupe's public contract."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message}


def validate_capability_document(value: Any) -> dict[str, Any]:
    """Validate `weavec-capabilities-v1` without network or compiler access."""

    document = dict(_object(value, "root"))
    if document.get("format") != CAPABILITIES_FORMAT:
        _fail(
            "WEAVEC_CAPABILITIES_FORMAT_UNSUPPORTED",
            "capability format must be weavec-capabilities-v1",
        )
    if document.get("schema_id") != CAPABILITIES_SCHEMA_ID:
        _fail(
            "WEAVEC_CAPABILITIES_SCHEMA_UNSUPPORTED",
            "capability schema identifier is incompatible",
        )
    if document.get("schema_version") != CAPABILITIES_SCHEMA_VERSION:
        _fail(
            "WEAVEC_CAPABILITIES_SCHEMA_UNSUPPORTED",
            "capability schema version is incompatible",
        )

    compiler = dict(_object(document.get("compiler"), "compiler"))
    if compiler.get("name") != "weavec" or compiler.get("public_variant") != "final":
        _fail(
            "WEAVEC_VARIANT_UNSUPPORTED",
            "Loupe requires the final user-facing weavec compiler",
        )
    _nonempty(compiler.get("version"), "compiler.version")

    language = dict(_object(document.get("language"), "language"))
    expected_language = {
        "name": "Weave",
        "surface_version": EXPECTED_SURFACE_VERSION,
        "grammar_id": EXPECTED_GRAMMAR_ID,
        "syntax": "s-expression",
        "case_sensitive": True,
        "wir_core_version": EXPECTED_WIR_CORE_VERSION,
    }
    if any(
        language.get(key) != expected for key, expected in expected_language.items()
    ):
        _fail(
            "WEAVEC_LANGUAGE_UNSUPPORTED",
            "installed weavec language or WIR contract is incompatible",
        )

    protocols = _validate_protocols(document.get("protocols"))
    commands = _validate_commands(document.get("commands"), protocols)
    targets = _validate_targets(document.get("targets"))
    features = _validate_features(document.get("features"))
    surface = _validate_surface(document.get("surface"), features)
    return {
        **document,
        "compiler": compiler,
        "language": language,
        "protocols": protocols,
        "commands": commands,
        "targets": targets,
        "features": features,
        "surface": surface,
    }


def require_capture_capabilities(document: Mapping[str, Any]) -> dict[str, Any]:
    """Require the strongest capture contract expressible by registry version 1."""

    commands = {
        item["name"]: item for item in document["commands"] if isinstance(item, Mapping)
    }
    capabilities = commands.get("capabilities")
    build = commands.get("build")
    if capabilities is None or capabilities.get("status") != "stable":
        _fail(
            "WEAVEC_CAPABILITY_MISSING",
            "installed weavec does not advertise a stable capabilities command",
        )
    if build is None or build.get("status") != "stable":
        _fail(
            "WEAVEC_CAPABILITY_MISSING",
            "installed weavec does not advertise a stable build command",
        )
    capability_protocols = set(capabilities.get("protocols", ()))
    if "weavec-capabilities-v1" not in capability_protocols:
        _fail(
            "WEAVEC_PROTOCOL_UNSUPPORTED",
            "capabilities command does not advertise weavec-capabilities-v1",
        )
    build_protocols = set(build.get("protocols", ()))
    required_build_protocols = {
        "weavec-build-manifest-v1",
        "weavec-diagnostics-v1",
        "weavec-compilation-trace-v1",
    }
    missing = sorted(required_build_protocols - build_protocols)
    if missing:
        _fail(
            "WEAVEC_PROTOCOL_UNSUPPORTED",
            "build command is missing protocols: " + ", ".join(missing),
        )

    targets = document["targets"]
    default_target = targets["default"]
    target = next(
        (item for item in targets["installed"] if item["triple"] == default_target),
        None,
    )
    if target is None:
        _fail(
            "WEAVEC_TARGET_UNSUPPORTED",
            "compiler default target is not installed",
        )
    if target["native"] is not True:
        _fail(
            "WEAVEC_TARGET_UNSUPPORTED",
            "Loupe capture requires a native installed target",
        )
    if "O3" not in target["optimization_levels"]:
        _fail(
            "WEAVEC_OPTIMIZATION_UNSUPPORTED",
            "Loupe capture requires optimization level O3",
        )
    if "native" not in target["cpu_selection"]:
        _fail(
            "WEAVEC_CPU_SELECTION_UNSUPPORTED",
            "Loupe capture requires native CPU selection",
        )

    return {
        "format": CAPTURE_PROFILE_FORMAT,
        "command": "build",
        "optimization_level": "O3",
        "cpu_selection": "native",
        "target": {
            "triple": target["triple"],
            "runtime": target["runtime"],
            "native": target["native"],
        },
        "protocols": sorted(required_build_protocols | {"weave-wir-core-v2"}),
        "outputs": list(REQUIRED_CAPTURE_OUTPUTS),
        "output_contract": (
            "registry-v1-stable-build-interface-with-versioned-protocols"
        ),
    }


def capability_identity_from_document(
    document: Any,
    *,
    registry_sha256: str,
    registry_bytes: int,
    compiler_sha256: str | None = None,
    compiler_bytes: int | None = None,
) -> dict[str, Any]:
    """Build an offline identity for a retained validated registry document."""

    validated = validate_capability_document(document)
    profile = require_capture_capabilities(validated)
    result: dict[str, Any] = {
        "format": CAPABILITY_IDENTITY_FORMAT,
        "registry_format": CAPABILITIES_FORMAT,
        "registry_sha256": registry_sha256,
        "registry_bytes": registry_bytes,
        "compiler_version": validated["compiler"]["version"],
        "surface_version": validated["language"]["surface_version"],
        "grammar_id": validated["language"]["grammar_id"],
        "wir_core_version": validated["language"]["wir_core_version"],
        "protocols": {item["id"]: item["version"] for item in validated["protocols"]},
        "target": profile["target"],
        "capture_profile": profile,
    }
    if compiler_sha256 is not None:
        result["compiler_sha256"] = compiler_sha256
    if compiler_bytes is not None:
        result["compiler_bytes"] = compiler_bytes
    return result


def _validate_protocols(value: Any) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, raw in enumerate(_array(value, "protocols")):
        item = dict(_object(raw, f"protocols[{index}]"))
        identifier = _nonempty(item.get("id"), f"protocols[{index}].id")
        version = _positive_integer(item.get("version"), f"protocols[{index}].version")
        _nonempty(item.get("kind"), f"protocols[{index}].kind")
        if identifier in seen:
            _fail(
                "WEAVEC_CAPABILITIES_INVALID",
                f"duplicate compiler protocol {identifier!r}",
            )
        seen.add(identifier)
        expected = REQUIRED_PROTOCOLS.get(identifier)
        if expected is not None and version != expected:
            _fail(
                "WEAVEC_PROTOCOL_UNSUPPORTED",
                f"compiler protocol {identifier!r} has incompatible version {version}",
            )
        result.append(item)
    for identifier in REQUIRED_PROTOCOLS:
        if identifier not in seen:
            _fail(
                "WEAVEC_PROTOCOL_UNSUPPORTED",
                f"installed weavec does not advertise protocol {identifier!r}",
            )
    return result


def _validate_commands(
    value: Any,
    protocols: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    known_protocols = {str(item["id"]) for item in protocols}
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, raw in enumerate(_array(value, "commands")):
        item = dict(_object(raw, f"commands[{index}]"))
        name = _nonempty(item.get("name"), f"commands[{index}].name")
        _nonempty(item.get("spelling"), f"commands[{index}].spelling")
        _nonempty(item.get("audience"), f"commands[{index}].audience")
        if item.get("status") not in {"stable", "experimental"}:
            _fail(
                "WEAVEC_CAPABILITIES_INVALID",
                f"commands[{index}].status is invalid",
            )
        command_protocols = _array(
            item.get("protocols"), f"commands[{index}].protocols"
        )
        if any(
            not isinstance(identifier, str) or identifier not in known_protocols
            for identifier in command_protocols
        ):
            _fail(
                "WEAVEC_CAPABILITIES_INVALID",
                f"commands[{index}] references an unknown protocol",
            )
        if name in seen:
            _fail(
                "WEAVEC_CAPABILITIES_INVALID",
                f"duplicate compiler command {name!r}",
            )
        seen.add(name)
        result.append({**item, "protocols": list(command_protocols)})
    return result


def _validate_targets(value: Any) -> dict[str, Any]:
    targets = dict(_object(value, "targets"))
    default = _nonempty(targets.get("default"), "targets.default")
    installed: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, raw in enumerate(_array(targets.get("installed"), "targets.installed")):
        item = dict(_object(raw, f"targets.installed[{index}]"))
        triple = _nonempty(item.get("triple"), f"targets.installed[{index}].triple")
        for field in ("native", "cross_compilation"):
            if not isinstance(item.get(field), bool):
                _fail(
                    "WEAVEC_CAPABILITIES_INVALID",
                    f"targets.installed[{index}].{field} must be boolean",
                )
        _nonempty(item.get("runtime"), f"targets.installed[{index}].runtime")
        optimizations = _string_array(
            item.get("optimization_levels"),
            f"targets.installed[{index}].optimization_levels",
        )
        cpu_selection = _string_array(
            item.get("cpu_selection"),
            f"targets.installed[{index}].cpu_selection",
        )
        if triple in seen:
            _fail(
                "WEAVEC_CAPABILITIES_INVALID",
                f"duplicate installed compiler target {triple!r}",
            )
        seen.add(triple)
        installed.append(
            {
                **item,
                "optimization_levels": optimizations,
                "cpu_selection": cpu_selection,
            }
        )
    if not installed or default not in seen:
        _fail(
            "WEAVEC_CAPABILITIES_INVALID",
            "compiler default target must be present in installed targets",
        )
    return {**targets, "default": default, "installed": installed}


def _validate_features(value: Any) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, raw in enumerate(_array(value, "features")):
        item = dict(_object(raw, f"features[{index}]"))
        identifier = _nonempty(item.get("id"), f"features[{index}].id")
        if item.get("status") not in {"stable", "experimental", "planned"}:
            _fail(
                "WEAVEC_CAPABILITIES_INVALID",
                f"features[{index}].status is invalid",
            )
        issue = item.get("issue")
        if issue is not None:
            _positive_integer(issue, f"features[{index}].issue")
        if identifier in seen:
            _fail(
                "WEAVEC_CAPABILITIES_INVALID",
                f"duplicate compiler feature {identifier!r}",
            )
        seen.add(identifier)
        result.append(item)
    return result


def _validate_surface(
    value: Any,
    features: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    surface = dict(_object(value, "surface"))
    _nonempty(surface.get("grammar_document"), "surface.grammar_document")
    _nonempty(surface.get("canonical_document"), "surface.canonical_document")
    if surface.get("child_count_excludes_head") is not True:
        _fail(
            "WEAVEC_CAPABILITIES_INVALID",
            "surface child counts must explicitly exclude the list head",
        )
    _string_array(surface.get("types"), "surface.types", minimum=1)
    _array(surface.get("operators"), "surface.operators", minimum=1)
    _array(surface.get("casts"), "surface.casts")
    _array(surface.get("contextual_literals"), "surface.contextual_literals")
    forms = _array(surface.get("forms"), "surface.forms", minimum=1)
    families = _array(
        surface.get("compatibility_families"),
        "surface.compatibility_families",
    )
    feature_ids = {str(item["id"]) for item in features}
    seen: set[str] = set()
    validated_forms: list[dict[str, Any]] = []
    for index, raw in enumerate(forms):
        item = dict(_object(raw, f"surface.forms[{index}]"))
        head = _nonempty(item.get("head"), f"surface.forms[{index}].head")
        if item.get("status") not in {
            "canonical",
            "compatibility",
            "deprecated",
            "experimental",
        }:
            _fail(
                "WEAVEC_CAPABILITIES_INVALID",
                f"surface.forms[{index}].status is invalid",
            )
        arity = dict(_object(item.get("arity"), f"surface.forms[{index}].arity"))
        minimum = _nonnegative_integer(
            arity.get("min_children"),
            f"surface.forms[{index}].arity.min_children",
        )
        maximum = arity.get("max_children")
        if maximum is not None:
            maximum = _nonnegative_integer(
                maximum,
                f"surface.forms[{index}].arity.max_children",
            )
            if maximum < minimum:
                _fail(
                    "WEAVEC_CAPABILITIES_INVALID",
                    f"surface.forms[{index}] maximum arity is below minimum",
                )
        if item.get("type_information") not in {
            "none",
            "explicit",
            "contextual",
            "semantic",
        }:
            _fail(
                "WEAVEC_CAPABILITIES_INVALID",
                f"surface.forms[{index}].type_information is invalid",
            )
        feature = item.get("feature")
        if feature is not None and feature not in feature_ids:
            _fail(
                "WEAVEC_CAPABILITIES_INVALID",
                f"surface.forms[{index}] references an unknown feature",
            )
        replacement = item.get("canonical_replacement")
        if replacement is not None and not isinstance(replacement, str):
            _fail(
                "WEAVEC_CAPABILITIES_INVALID",
                f"surface.forms[{index}].canonical_replacement is invalid",
            )
        _array(item.get("roles"), f"surface.forms[{index}].roles")
        if head in seen:
            _fail(
                "WEAVEC_CAPABILITIES_INVALID",
                f"duplicate compiler surface form {head!r}",
            )
        seen.add(head)
        validated_forms.append(
            {**item, "arity": {"min_children": minimum, "max_children": maximum}}
        )
    return {
        **surface,
        "forms": validated_forms,
        "compatibility_families": list(families),
    }


def _object(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        _fail(
            "WEAVEC_CAPABILITIES_INVALID",
            f"capability field {field} must be an object",
        )
    return value


def _array(value: Any, field: str, *, minimum: int = 0) -> Sequence[Any]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        _fail(
            "WEAVEC_CAPABILITIES_INVALID",
            f"capability field {field} must be an array",
        )
    if len(value) < minimum:
        _fail(
            "WEAVEC_CAPABILITIES_INVALID",
            f"capability field {field} requires at least {minimum} items",
        )
    return value


def _string_array(value: Any, field: str, *, minimum: int = 0) -> list[str]:
    items = _array(value, field, minimum=minimum)
    if any(not isinstance(item, str) for item in items):
        _fail(
            "WEAVEC_CAPABILITIES_INVALID",
            f"capability field {field} must contain strings",
        )
    return list(items)


def _nonempty(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        _fail(
            "WEAVEC_CAPABILITIES_INVALID",
            f"capability field {field} must be a non-empty string",
        )
    return value


def _positive_integer(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        _fail(
            "WEAVEC_CAPABILITIES_INVALID",
            f"capability field {field} must be a positive integer",
        )
    return value


def _nonnegative_integer(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        _fail(
            "WEAVEC_CAPABILITIES_INVALID",
            f"capability field {field} must be a non-negative integer",
        )
    return value


def _fail(code: str, message: str) -> NoReturn:
    raise CompilerCapabilityError(code, message)
