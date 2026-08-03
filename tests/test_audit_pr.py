"""Tests for pull-request audit source selection."""

from __future__ import annotations

import runpy
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast


def _selector() -> Callable[[list[Path]], list[Any]]:
    path = Path(__file__).parents[1] / "scripts" / "audit_pr.py"
    namespace = runpy.run_path(str(path))
    return cast(Callable[[list[Path]], list[Any]], namespace["_changed_audit_targets"])


def _all_targets() -> Callable[[Path], list[Any]]:
    path = Path(__file__).parents[1] / "scripts" / "audit_pr.py"
    namespace = runpy.run_path(str(path))
    return cast(Callable[[Path], list[Any]], namespace["_all_audit_targets"])


def _write_source(path: Path) -> None:
    path.write_text("(program (entry main))\n", encoding="utf-8")


def test_changed_runtime_sidecar_selects_adjacent_source(
    tmp_path: Path, monkeypatch: Any
) -> None:
    source = tmp_path / "demo.weave"
    _write_source(source)
    sidecar = tmp_path / "demo.audit.json"
    sidecar.write_text("{}\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    selected = _selector()([Path("demo.audit.json")])

    assert [target.sources for target in selected] == [(Path("demo.weave"),)]


def test_changed_or_deleted_report_selects_adjacent_source(
    tmp_path: Path, monkeypatch: Any
) -> None:
    source = tmp_path / "demo.weave"
    _write_source(source)
    monkeypatch.chdir(tmp_path)

    selected = _selector()([Path("demo.md")])

    assert [target.sources for target in selected] == [(Path("demo.weave"),)]


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
    _write_source(source)
    sidecar = tmp_path / "demo.audit.json"
    sidecar.write_text("{}\n", encoding="utf-8")
    report = tmp_path / "demo.md"
    report.write_text("# report\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    selected = _selector()(
        [Path("demo.weave"), Path("demo.audit.json"), Path("demo.md")]
    )

    assert len(selected) == 1
    assert selected[0].sources == (Path("demo.weave"),)


def test_changed_companion_selects_declared_multisource_target(
    tmp_path: Path, monkeypatch: Any
) -> None:
    primary = tmp_path / "app.weave"
    companion = tmp_path / "math.weave"
    _write_source(primary)
    _write_source(companion)
    manifest = tmp_path / "app.audit.sources"
    manifest.write_text("app.weave\nmath.weave\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    selected = _selector()([Path("math.weave")])

    assert len(selected) == 1
    assert selected[0].sources == (Path("app.weave"), Path("math.weave"))
    assert selected[0].report == Path("app.md")


def test_changed_source_set_preserves_declared_order(
    tmp_path: Path, monkeypatch: Any
) -> None:
    primary = tmp_path / "app.weave"
    companion = tmp_path / "math.weave"
    _write_source(primary)
    _write_source(companion)
    manifest = tmp_path / "app.audit.sources"
    manifest.write_text(
        "# compiler input order\napp.weave\nmath.weave\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    selected = _selector()([Path("app.audit.sources")])

    assert selected[0].sources == (Path("app.weave"), Path("math.weave"))


def test_source_set_rejects_paths_outside_its_directory(
    tmp_path: Path, monkeypatch: Any
) -> None:
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    primary = corpus / "app.weave"
    outside = tmp_path / "outside.weave"
    _write_source(primary)
    _write_source(outside)
    manifest = corpus / "app.audit.sources"
    manifest.write_text("app.weave\n../outside.weave\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    try:
        _selector()([Path("corpus/app.audit.sources")])
    except ValueError as exc:
        assert "escapes its directory" in str(exc)
    else:
        raise AssertionError("unsafe source-set path was accepted")


def test_full_corpus_selection_collapses_grouped_sources(
    tmp_path: Path, monkeypatch: Any
) -> None:
    corpus = tmp_path / "docs" / "audit"
    corpus.mkdir(parents=True)
    primary = corpus / "app.weave"
    companion = corpus / "math.weave"
    standalone = corpus / "single.weave"
    for source in (primary, companion, standalone):
        _write_source(source)
    (corpus / "app.audit.sources").write_text(
        "app.weave\nmath.weave\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    selected = _all_targets()(Path("docs/audit"))

    assert [target.sources for target in selected] == [
        (
            Path("docs/audit/app.weave"),
            Path("docs/audit/math.weave"),
        ),
        (Path("docs/audit/single.weave"),),
    ]
