from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CHECKER = REPOSITORY_ROOT / "scripts" / "check_workflow_security.py"


def _run(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), "--root", str(root)],
        check=False,
        capture_output=True,
        text=True,
    )


def _write_workflow(root: Path, name: str, content: str) -> None:
    path = root / ".github" / "workflows" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_checked_in_workflows_satisfy_security_policy() -> None:
    result = _run(REPOSITORY_ROOT)

    assert result.returncode == 0, result.stderr
    assert "all workflows satisfy the policy" in result.stdout


def test_mutable_action_reference_is_rejected(tmp_path: Path) -> None:
    _write_workflow(
        tmp_path,
        "mutable.yml",
        """\
name: Mutable
permissions:
  contents: read
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false
""",
    )

    result = _run(tmp_path)

    assert result.returncode == 1
    assert "not pinned to a full SHA" in result.stderr
    assert "must document its release tag" in result.stderr


def test_unexpected_write_permission_is_rejected(tmp_path: Path) -> None:
    _write_workflow(
        tmp_path,
        "write.yml",
        """\
name: Unexpected write
permissions:
  contents: read
jobs:
  audit:
    permissions:
      contents: write
    runs-on: ubuntu-latest
    steps:
      - run: echo unsafe
""",
    )

    result = _run(tmp_path)

    assert result.returncode == 1
    assert "unexpected write permissions" in result.stderr


def test_publication_token_is_rejected_in_audit_job(tmp_path: Path) -> None:
    _write_workflow(
        tmp_path,
        "audit.yml",
        """\
name: Unsafe token
permissions:
  contents: read
jobs:
  audit:
    runs-on: ubuntu-latest
    env:
      TOKEN: ${{ secrets.WEAVE_GITHUB_TOKEN }}
    steps:
      - run: echo audit
""",
    )

    result = _run(tmp_path)

    assert result.returncode == 1
    assert "WEAVE_GITHUB_TOKEN is restricted" in result.stderr


def test_credentialed_job_cannot_execute_project_code(tmp_path: Path) -> None:
    _write_workflow(
        tmp_path,
        "publish-audit.yml",
        """\
name: Unsafe publisher
permissions:
  contents: read
jobs:
  publish:
    permissions:
      contents: write
      pull-requests: write
    runs-on: ubuntu-latest
    steps:
      - run: uv run python scripts/publish.py
""",
    )

    result = _run(tmp_path)

    assert result.returncode == 1
    assert "credentialed job executes project code" in result.stderr
