from __future__ import annotations

import json
from pathlib import Path

import pytest

from weave_loupe.path_identity import (
    PORTABLE_PATH_FORMAT,
    PathIdentityError,
    canonical_sidecar_identity,
    canonicalize_audit_metadata,
    canonicalize_compiler_audit,
    normalize_portable_path,
    plan_public_paths,
    redact_private_paths,
)


def test_root_produces_relative_posix_identity(tmp_path: Path) -> None:
    source = tmp_path / "nested" / "α.weave"
    source.parent.mkdir()
    source.write_text("(module)", encoding="utf-8")

    plan = plan_public_paths([source], audit_root=tmp_path)

    assert plan.root == tmp_path.resolve()
    assert plan.sources[0].identity == "nested/α.weave"
    assert plan.sources[0].metadata() == {
        "format": PORTABLE_PATH_FORMAT,
        "path": "nested/α.weave",
        "scope": "root",
        "symlinked": False,
    }


def test_windows_logical_name_normalizes_to_posix() -> None:
    assert normalize_portable_path(r"C:\project\src\main.weave") == (
        "project/src/main.weave"
    )


@pytest.mark.parametrize(
    "value",
    ["../escape.weave", "/absolute.weave", "a/../b.weave"],
)
def test_parent_and_absolute_logical_names_are_rejected(value: str) -> None:
    with pytest.raises(PathIdentityError):
        normalize_portable_path(value)


def test_external_source_requires_explicit_logical_name(tmp_path: Path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    source = tmp_path / "outside.weave"
    source.write_text("(module)", encoding="utf-8")

    with pytest.raises(PathIdentityError, match="requires --source-name"):
        plan_public_paths([source], audit_root=root)

    plan = plan_public_paths(
        [source],
        audit_root=root,
        logical_names=["fixtures/outside.weave"],
    )
    assert plan.sources[0].identity == "external/fixtures/outside.weave"
    assert plan.sources[0].scope == "external"


def test_symlink_escape_requires_explicit_name(tmp_path: Path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "outside.weave"
    outside.write_text("(module)", encoding="utf-8")
    link = root / "linked.weave"
    link.symlink_to(outside)

    with pytest.raises(PathIdentityError, match="requires --source-name"):
        plan_public_paths([link], audit_root=root)

    plan = plan_public_paths(
        [link],
        audit_root=root,
        logical_names=["linked.weave"],
    )
    assert plan.sources[0].identity == "external/linked.weave"
    assert plan.sources[0].symlinked is True


def test_portable_identities_reject_casefold_collisions(
    tmp_path: Path,
) -> None:
    first = tmp_path / "A.weave"
    second = tmp_path / "a.weave"
    first.write_text("A", encoding="utf-8")
    second.write_text("a", encoding="utf-8")

    with pytest.raises(PathIdentityError, match="collide"):
        plan_public_paths([first, second], audit_root=tmp_path)


def test_sidecar_identity_tracks_root_and_external_source(
    tmp_path: Path,
) -> None:
    root = tmp_path / "root"
    root.mkdir()
    local = root / "src" / "main.weave"
    local.parent.mkdir()
    local.write_text("(module)", encoding="utf-8")
    sidecar = local.with_suffix(".audit.json")
    sidecar.write_text("{}", encoding="utf-8")
    local_plan = plan_public_paths([local], audit_root=root)
    assert canonical_sidecar_identity(sidecar, local_plan) == ("src/main.audit.json")

    external = tmp_path / "external.weave"
    external.write_text("(module)", encoding="utf-8")
    external_sidecar = external.with_suffix(".audit.json")
    external_sidecar.write_text("{}", encoding="utf-8")
    external_plan = plan_public_paths(
        [external],
        audit_root=root,
        logical_names=["fixtures/external.weave"],
    )
    assert canonical_sidecar_identity(external_sidecar, external_plan) == (
        "external/fixtures/external.audit.json"
    )


def test_metadata_and_compiler_evidence_drop_host_paths(
    tmp_path: Path,
) -> None:
    root = tmp_path / "checkout"
    source = root / "src" / "main.weave"
    source.parent.mkdir(parents=True)
    source.write_text("(module)", encoding="utf-8")
    sidecar = source.with_suffix(".audit.json")
    sidecar.write_text("{}", encoding="utf-8")
    plan = plan_public_paths([source], audit_root=root)
    digest = "0" * 64

    metadata = canonicalize_audit_metadata(
        {
            "sources": [{"path": str(source), "sha256": digest, "size": 8}],
            "runtime_input": {
                "path": str(sidecar),
                "sha256": digest,
            },
            "source_repository": {"root": str(root), "sha": "abc"},
            "loupe_repository": {"root": "/private/loupe", "sha": "def"},
            "weavec": {
                "path": "/private/weavec",
                "repository": {
                    "root": "/private/compiler",
                    "sha": "ghi",
                },
            },
        },
        plan=plan,
        runtime_sidecar=sidecar,
    )
    compiler = canonicalize_compiler_audit(
        {
            "sources": [{"path": str(source)}],
            "baseline": {
                "compiler": {"path": "/private/baseline"},
                "runtime": {"sidecar": str(sidecar)},
            },
            "candidate": {
                "compiler": {"path": "/private/candidate"},
                "runtime": {"sidecar": str(sidecar)},
            },
        },
        plan=plan,
    )

    serialized = json.dumps({"metadata": metadata, "compiler": compiler})
    assert str(root) not in serialized
    assert "/private/" not in serialized
    assert metadata["sources"][0]["path"] == "src/main.weave"
    assert metadata["runtime_input"]["path"] == "src/main.audit.json"
    assert compiler["sources"][0]["path"] == "src/main.weave"


def test_redaction_is_checkout_location_independent(tmp_path: Path) -> None:
    first_root = tmp_path / "first"
    second_root = tmp_path / "second"
    first_source = first_root / "src" / "main.weave"
    second_source = second_root / "src" / "main.weave"
    first_source.parent.mkdir(parents=True)
    second_source.parent.mkdir(parents=True)
    first_source.write_text("(module)", encoding="utf-8")
    second_source.write_text("(module)", encoding="utf-8")
    first = plan_public_paths([first_source], audit_root=first_root)
    second = plan_public_paths([second_source], audit_root=second_root)

    first_text = redact_private_paths(
        f"source={first_source.resolve()}",
        plan=first,
    )
    second_text = redact_private_paths(
        f"source={second_source.resolve()}",
        plan=second,
    )

    assert first_text == second_text == "source=$AUDIT_ROOT/src/main.weave"
