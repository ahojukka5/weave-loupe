"""Offline command-line validation for compiler capability documents."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from .capabilities import (
    CompilerCapabilityError,
    capability_identity_from_document,
)


def main(argv: Sequence[str] | None = None) -> int:
    """Validate one saved registry offline and print its capture contract."""

    parser = argparse.ArgumentParser(
        prog="python -m weave_loupe.compiler_capabilities",
        description="Validate weavec-capabilities-v1 without network access.",
    )
    parser.add_argument("document", type=Path)
    arguments = parser.parse_args(list(argv) if argv is not None else None)
    try:
        raw_bytes = arguments.document.read_bytes()
        document = json.loads(raw_bytes.decode("utf-8"))
        identity = capability_identity_from_document(
            document,
            registry_sha256=hashlib.sha256(raw_bytes).hexdigest(),
            registry_bytes=len(raw_bytes),
        )
    except (
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        CompilerCapabilityError,
    ) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(identity, indent=2, sort_keys=True))
    return 0
