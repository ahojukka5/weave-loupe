"""Shared test fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def fake_weavec(tmp_path: Path) -> Path:
    script = tmp_path / "weavec"
    script.write_text(
        """#!/usr/bin/env python3
import json
import pathlib
import sys

args = sys.argv[1:]


def value(flag):
    return pathlib.Path(args[args.index(flag) + 1])


source = pathlib.Path(args[1])
value('--emit-wir').write_text('(core-module (core-version 2))\\n')
value('--emit-llvm').write_text(
    '; weave.source kind=statement index=0 bytes=0..4 '
    'wir-bytes=0..10 path="demo.weave"\\n'
    'define i32 @main() {\\n'
    'entry:\\n'
    '  %x = add i32 1, 0\\n'
    '  ret i32 %x\\n'
    '}\\n'
)
value('--diagnostics-json').write_text(
    json.dumps(
        {'format': 'weavec-diagnostics-v1', 'diagnostics': []}
    ) + '\\n'
)
value('--trace-json').write_text(
    json.dumps(
        {
            'format': 'weavec-compilation-trace-v1',
            'events': [
                {
                    'action': 'typed-integer-wrap',
                    'pass': 'lowering',
                    'category': 'lowering',
                }
            ],
        }
    ) + '\\n'
)
value('--manifest-json').write_text(
    json.dumps(
        {
            'format': 'weavec-build-manifest-v1',
            'sources': [str(source)],
        }
    ) + '\\n'
)
value('-o').write_text('binary')
print('compiled')
""",
        encoding="utf-8",
    )
    script.chmod(0o755)
    return script


@pytest.fixture
def source_file(tmp_path: Path) -> Path:
    source = tmp_path / "demo.weave"
    source.write_text("(program (entry main))\n", encoding="utf-8")
    return source
