"""Shared test fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def fake_weavec(tmp_path: Path) -> Path:
    script = tmp_path / "weavec"
    script.write_text(
        r"""#!/usr/bin/env python3
import json
import pathlib
import sys

args = sys.argv[1:]

if args == ['--version']:
    print('weavec v0.3.0+git.test123')
    raise SystemExit(0)


def value(flag):
    return pathlib.Path(args[args.index(flag) + 1])


source = pathlib.Path(args[1])
value('--emit-wir').write_text(
    '; weavec-source-file-v1 0 "demo.weave"\n'
    '(core-module\n'
    '  (core-version 2)\n'
    '  (decls\n'
    '    ; weavec-source-span-v1 0 0 10\n'
    '    (; weavec-source-span-v1 0 1 2\n'
    '    fn ; weavec-source-span-v1 0 3 4\n'
    '    main (params) (returns i32) (do (return (const_i32 1)))))\n'
    ')\n'
)
value('--emit-llvm').write_text(
    '; weave.source kind=statement index=0 bytes=0..4 '
    'wir-bytes=0..10 path="demo.weave"\n'
    'define i32 @main() {\n'
    'entry:\n'
    '  %x = add i32 1, 0\n'
    '  ret i32 %x\n'
    '}\n'
)
value('--emit-optimized-llvm').write_text(
    'define i32 @main() {\n'
    'entry:\n'
    '  ret i32 1\n'
    '}\n'
)
value('--emit-assembly').write_text('main:\n  mov $1, %eax\n  ret\n')
value('--emit-disassembly').write_text(
    '0000000000000000 <main>:\n'
    '   0: b8 01 00 00 00 mov $0x1,%eax\n'
    '   5: c3 ret\n'
)
value('--optimization-record').write_text(
    '--- !Passed\nPass: instcombine\nName: Simplify\n...\n'
)
value('--diagnostics-json').write_text(
    json.dumps(
        {'format': 'weavec-diagnostics-v1', 'diagnostics': []}
    ) + '\n'
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
    ) + '\n'
)
value('--manifest-json').write_text(
    json.dumps(
        {
            'format': 'weavec-build-manifest-v1',
            'sources': [str(source)],
        }
    ) + '\n'
)
program = value('-o')
program.write_text(
    '#!/usr/bin/env python3\n'
    'import os\n'
    'import sys\n'
    'sys.stdout.write(os.environ.get("LOUPE_STDOUT", ""))\n'
    'sys.stderr.write(os.environ.get("LOUPE_STDERR", ""))\n'
    'raise SystemExit(int(os.environ.get("LOUPE_EXIT", "1")))\n'
)
program.chmod(0o755)
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
