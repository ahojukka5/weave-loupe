from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
SCRIPT = SCRIPTS / "regression_evidence_qualify.py"
SPEC = importlib.util.spec_from_file_location("regression_evidence_qualify", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
import regression_evidence_protocol as protocol  # noqa: E402


def git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def commit(repo: Path, message: str) -> str:
    git(repo, "add", ".")
    git(repo, "commit", "-m", message)
    return git(repo, "rev-parse", "HEAD")


def fake_weavec_repo(
    tmp_path: Path,
    *,
    bad_oracle_exit: int = 1,
) -> tuple[Path, str, str]:
    repo = tmp_path / "weavec"
    repo.mkdir()
    git(repo, "init")
    git(repo, "config", "user.name", "Regression Test")
    git(repo, "config", "user.email", "regression@example.invalid")

    scripts = repo / "scripts"
    scripts.mkdir()
    (scripts / "build.sh").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    (repo / "oracle.sh").write_text(
        f"#!/bin/sh\nexit {bad_oracle_exit}\n",
        encoding="utf-8",
    )
    bad = commit(repo, "bad")

    (repo / "oracle.sh").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    (repo / "marker.txt").write_text("good\n", encoding="utf-8")
    good = commit(repo, "good")
    return repo, bad, good


def draft_corpus(
    bad: str,
    good: str,
    *,
    oracle_command: list[str] | None = None,
    require_compiler_build: bool = True,
) -> dict[str, object]:
    corpus: dict[str, object] = {
        "schema": protocol.CORPUS_SCHEMA,
        "status": "draft",
        "loupe": {
            "repository": "ahojukka5/weave-loupe",
            "revision": "test-revision",
        },
        "compiler": {"repository": "ahojukka5/weavec"},
        "model_review": {
            "provider": "not-run",
            "model": "not-run",
            "configuration_id": "not-frozen",
            "prompt_id": "not-frozen",
        },
        "conditions": list(protocol.CONDITIONS),
        "cases": [
            {
                "id": "historical-case",
                "family": "frontend",
                "bad_revision": bad,
                "good_revision": good,
                "expected_stage": "frontend",
                "failure_mechanism": "fake historical defect",
                "oracle": {"command": oracle_command or ["bash", "oracle.sh"]},
                "relevant_tests": ["oracle.sh"],
                "qualification": {"require_compiler_build": require_compiler_build},
            }
        ],
    }
    normalized = protocol.validate_corpus(corpus)
    corpus["corpus_sha256"] = protocol.canonical_corpus_hash(normalized)
    return corpus


def test_qualifier_requires_bad_fail_and_good_pass(tmp_path: Path) -> None:
    repo, bad, good = fake_weavec_repo(tmp_path)

    result = MODULE.qualify_corpus(
        protocol.validate_corpus(draft_corpus(bad, good)),
        weavec_repo=repo,
        build_timeout_seconds=30,
        oracle_timeout_seconds=30,
    )

    assert result["all_qualified"] is True
    row = result["rows"][0]
    assert row["qualified"] is True
    assert row["bad"]["build"]["returncode"] == 0
    assert row["bad"]["oracle"]["returncode"] == 1
    assert row["good"]["build"]["returncode"] == 0
    assert row["good"]["oracle"]["returncode"] == 0


def test_qualifier_rejects_case_when_bad_revision_passes(tmp_path: Path) -> None:
    repo, bad, good = fake_weavec_repo(tmp_path, bad_oracle_exit=0)

    result = MODULE.qualify_corpus(
        protocol.validate_corpus(draft_corpus(bad, good)),
        weavec_repo=repo,
        build_timeout_seconds=30,
        oracle_timeout_seconds=30,
    )

    assert result["all_qualified"] is False
    assert result["qualified_count"] == 0


def test_qualifier_rejects_non_git_checkout(tmp_path: Path) -> None:
    with pytest.raises(protocol.ProtocolError, match="not a git checkout"):
        MODULE.qualify_corpus(
            protocol.validate_corpus(draft_corpus("a" * 40, "b" * 40)),
            weavec_repo=tmp_path,
        )


def test_qualifier_runs_independent_oracle_from_oracle_root(
    tmp_path: Path,
) -> None:
    repo, bad, good = fake_weavec_repo(tmp_path)
    oracle_root = tmp_path / "oracles"
    oracle_root.mkdir()
    (oracle_root / "check.sh").write_text(
        "#!/bin/sh\n"
        'test -n "$WEAVEC_ROOT" || exit 2\n'
        'test -f "$WEAVEC_ROOT/oracle.sh" || exit 3\n'
        'exec sh "$WEAVEC_ROOT/oracle.sh"\n',
        encoding="utf-8",
    )

    result = MODULE.qualify_corpus(
        protocol.validate_corpus(
            draft_corpus(
                bad,
                good,
                oracle_command=["sh", "check.sh"],
            )
        ),
        weavec_repo=repo,
        oracle_root=oracle_root,
        build_timeout_seconds=30,
        oracle_timeout_seconds=30,
    )

    assert result["all_qualified"] is True
    assert result["rows"][0]["bad"]["revision"] == bad
    assert result["rows"][0]["good"]["revision"] == good


def test_qualifier_can_skip_compiler_build(tmp_path: Path) -> None:
    repo, bad, good = fake_weavec_repo(tmp_path)
    (repo / "scripts" / "build.sh").write_text(
        "#!/bin/sh\nexit 99\n",
        encoding="utf-8",
    )
    git(repo, "add", ".")
    git(repo, "commit", "-m", "break default build")

    oracle_root = tmp_path / "oracles"
    oracle_root.mkdir()
    (oracle_root / "check.sh").write_text(
        "#!/bin/sh\n"
        'if grep -q good "$WEAVEC_ROOT/marker.txt" 2>/dev/null; then\n'
        "  exit 0\n"
        "fi\n"
        "exit 1\n",
        encoding="utf-8",
    )

    result = MODULE.qualify_corpus(
        protocol.validate_corpus(
            draft_corpus(
                bad,
                good,
                oracle_command=["sh", "check.sh"],
                require_compiler_build=False,
            )
        ),
        weavec_repo=repo,
        oracle_root=oracle_root,
        build_timeout_seconds=30,
        oracle_timeout_seconds=30,
    )

    assert result["all_qualified"] is True
    assert result["rows"][0]["bad"]["build"]["skipped"] is True
    assert result["rows"][0]["good"]["build"]["skipped"] is True


def test_draft_historical_corpus_keeps_exact_revisions() -> None:
    corpus_path = (
        Path(__file__).resolve().parents[1]
        / "experiments"
        / "compiler-evidence"
        / "corpus.json"
    )
    corpus = protocol.load_corpus(corpus_path)
    assert corpus["status"] == "draft"
    assert len(corpus["cases"]) == 10
    families = {case["family"] for case in corpus["cases"]}
    assert len(families) >= 4
    for case in corpus["cases"]:
        assert len(case["bad_revision"]) >= 40
        assert len(case["good_revision"]) >= 40
        assert case["bad_revision"] != case["good_revision"]
        command = case["oracle"]["command"]
        assert command[0] == "bash"
        assert command[1].startswith("experiments/compiler-evidence/oracles/")
