"""Tests for pull-request audit source selection."""

from __future__ import annotations

import runpy
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast


def _selector() -> Callable[[list[Path]], list[Path]]:
    path = Path(__file__).parents[1] / "scripts" / "audit_pr.py"
    namespace = runpy.run_path(str(path))
    return cast(Callable[[list[Path]], list[Path]], namespace["_changed_weave_sources"])


def test_changed_runtime_sidecar_selects_adjacent_source(
    tmp_path: Path, monkeypatch: Any
) -> None:
    source = tmp_path / "demo.weave"
    source.write_text("(program (entry main))\n", encoding="utf-8")
    sidecar = tmp_path / "demo.audit.json"
    sidecar.write_text("{}\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    selected = _selector()([Path("demo.audit.json")])

    assert selected == [Path("demo.weave")]


def test_changed_or_deleted_report_selects_adjacent_source(
    tmp_path: Path, monkeypatch: Any
) -> None:
    source = tmp_path / "demo.weave"
    source.write_text("(program (entry main))\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    selected = _selector()([Path("demo.md")])

    assert selected == [Path("demo.weave")]


def test_non_generated_markdown_is_not_selected(
    tmp_path: Path, monkeypatch: Any
) -> None:
    readme = tmp_path / "README.md"
    readme.write_text("documentation\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    assert _selector()([Path("README.md")]) == []


def test_missing_sidecar_source_is_not_selected(
    tmp_path: Path, monkeypatch: Any
) -> None:
    sidecar = tmp_path / "orphan.audit.json"
    sidecar.write_text("{}\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    assert _selector()([Path("orphan.audit.json")]) == []


def test_source_sidecar_and_report_are_deduplicated(
    tmp_path: Path, monkeypatch: Any
) -> None:
    source = tmp_path / "demo.weave"
    source.write_text("(program (entry main))\n", encoding="utf-8")
    sidecar = tmp_path / "demo.audit.json"
    sidecar.write_text("{}\n", encoding="utf-8")
    report = tmp_path / "demo.md"
    report.write_text("# report\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    selected = _selector()(
        [Path("demo.weave"), Path("demo.audit.json"), Path("demo.md")]
    )

    assert selected == [Path("demo.weave")]
