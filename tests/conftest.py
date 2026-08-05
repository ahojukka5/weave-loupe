"""Shared test fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.capability_fixtures import capability_document


@pytest.fixture(autouse=True)
def allow_explicit_unsandboxed_runtime_tests(monkeypatch) -> None:
    """Keep ordinary unit fixtures direct while sandbox tests opt back in."""
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    monkeypatch.setenv("WEAVE_LOUPE_UNSAFE_NO_SANDBOX", "1")


@pytest.fixture
def fake_weavec(tmp_path: Path) -> Path:
    script = tmp_path / "weavec"
    registry = repr(capability_document())
    script.write_text(
        "#!/usr/bin/env python3\n"
        "import json\n"
        "import pathlib\n"
        "import sys\n"
        f"CAPABILITIES = {registry}\n"
        "args = sys.argv[1:]\n"
        "if args == ['capabilities', '--json']:\n"
        "    print(json.dumps(CAPABILITIES, sort_keys=True, separators=(',', ':')))\n"
        "    raise SystemExit(0)\n"
        "if args == ['--version']:\n"
        "    print('weavec v0.3.0+git.test123')\n"
        "    raise SystemExit(0)\n"
        "def value(flag):\n"
        "    return pathlib.Path(args[args.index(flag) + 1])\n"
        "source = pathlib.Path(args[1])\n"
        "value('--emit-wir').write_text(\n"
        "    '; weavec-source-file-v1 0 \"demo.weave\"\\n'\n"
        "    '(core-module\\n'\n"
        "    '  (core-version 2)\\n'\n"
        "    '  (decls\\n'\n"
        "    '    ; weavec-source-span-v1 0 0 10\\n'\n"
        "    '    (; weavec-source-span-v1 0 1 2\\n'\n"
        "    '    fn ; weavec-source-span-v1 0 3 4\\n'\n"
        "    '    main (params) (returns i32) (do (return (const_i32 1)))))\\n'\n"
        "    ')\\n'\n"
        ")\n"
        "value('--emit-llvm').write_text(\n"
        "    '; weave.source kind=statement index=0 bytes=0..4 '\n"
        "    'wir-bytes=0..10 path=\"demo.weave\"\\n'\n"
        "    'define i32 @main() {\\n'\n"
        "    'entry:\\n'\n"
        "    '  %x = add i32 1, 0\\n'\n"
        "    '  ret i32 %x\\n'\n"
        "    '}\\n'\n"
        ")\n"
        "value('--emit-optimized-llvm').write_text(\n"
        "    'define i32 @main() {\\n'\n"
        "    'entry:\\n'\n"
        "    '  ret i32 1\\n'\n"
        "    '}\\n'\n"
        ")\n"
        "value('--emit-assembly').write_text('main:\\n  mov $1, %eax\\n  ret\\n')\n"
        "value('--emit-disassembly').write_text(\n"
        "    '0000000000000000 <main>:\\n'\n"
        "    '   0: b8 01 00 00 00 mov $0x1,%eax\\n'\n"
        "    '   5: c3 ret\\n'\n"
        ")\n"
        "value('--optimization-record').write_text(\n"
        "    '--- !Passed\\nPass: instcombine\\nName: Simplify\\n...\\n'\n"
        ")\n"
        "value('--diagnostics-json').write_text(\n"
        "    json.dumps(\n"
        "        {'format': 'weavec-diagnostics-v1', 'diagnostics': []}\n"
        "    ) + '\\n'\n"
        ")\n"
        "value('--trace-json').write_text(\n"
        "    json.dumps(\n"
        "        {\n"
        "            'format': 'weavec-compilation-trace-v1',\n"
        "            'events': [\n"
        "                {\n"
        "                    'action': 'typed-integer-wrap',\n"
        "                    'pass': 'lowering',\n"
        "                    'category': 'lowering',\n"
        "                }\n"
        "            ],\n"
        "        }\n"
        "    ) + '\\n'\n"
        ")\n"
        "value('--manifest-json').write_text(\n"
        "    json.dumps(\n"
        "        {\n"
        "            'format': 'weavec-build-manifest-v1',\n"
        "            'sources': [str(source)],\n"
        "        }\n"
        "    ) + '\\n'\n"
        ")\n"
        "program = value('-o')\n"
        "program.write_text(\n"
        "    f'#!{sys.executable}\\n'\n"
        "    'import os\\n'\n"
        "    'import sys\\n'\n"
        '    \'sys.stdout.write(os.environ.get("LOUPE_STDOUT", ""))\\n\'\n'
        '    \'sys.stderr.write(os.environ.get("LOUPE_STDERR", ""))\\n\'\n'
        '    \'raise SystemExit(int(os.environ.get("LOUPE_EXIT", "1")))\\n\'\n'
        ")\n"
        "program.chmod(0o755)\n"
        "print('compiled')\n",
        encoding="utf-8",
    )
    script.chmod(0o755)
    return script


@pytest.fixture
def source_file(tmp_path: Path) -> Path:
    source = tmp_path / "demo.weave"
    source.write_text("(program (entry main))\n", encoding="utf-8")
    return source
