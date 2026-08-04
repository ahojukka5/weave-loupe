"""Tests for installed console-script metadata."""

from __future__ import annotations

from importlib import metadata

from weave_loupe import scheduled_audit


def test_corpus_auditor_console_script_is_installed() -> None:
    scripts = {
        entry.name: entry for entry in metadata.entry_points(group="console_scripts")
    }

    assert scripts["loupe"].value == "weave_loupe.cli:main"
    corpus = scripts["loupe-corpus"]
    assert corpus.value == "weave_loupe.scheduled_audit:main"
    assert corpus.load() is scheduled_audit.main
