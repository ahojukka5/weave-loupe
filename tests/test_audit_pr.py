"""Tests for pull-request audit source selection."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType


def _load_script() -> ModuleType:
    path = Path(__file__).parents[1] / "scripts" / "audit_pr.py"
    specification = importlib.util.spec_from_file_location("audit_pr_script", path)
    assert specification is not None
    assert specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def test_changed_runtime_sidecar_selects_adjacent_source(
    tmp_path: Path, monkeypatch
) -> None:
    source = tmp_path / "demo.weave"
    source.write_text("(program (entry main))\n", encoding="utf-8")
    sidecar = tmp_path / "demo.audit.json"
    sidecar.write_text("{}\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    module = _load_script()
    selected = module._changed_weave_sources([Path("demo.audit.json")])

    assert selected == [Path("demo.weave")]


def test_missing_sidecar_source_is_not_selected(tmp_path: Path, monkeypatch) -> None:
    sidecar = tmp_path / "orphan.audit.json"
    sidecar.write_text("{}\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    module = _load_script()

    assert module._changed_weave_sources([Path("orphan.audit.json")]) == []


def test_source_and_sidecar_are_deduplicated(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "demo.weave"
    source.write_text("(program (entry main))\n", encoding="utf-8")
    sidecar = tmp_path / "demo.audit.json"
    sidecar.write_text("{}\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    module = _load_script()
    selected = module._changed_weave_sources(
        [Path("demo.weave"), Path("demo.audit.json")]
    )

    assert selected == [Path("demo.weave")]
