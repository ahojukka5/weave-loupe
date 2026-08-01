"""Architecture-specific native instruction classification."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

_X86_RETURNS = frozenset(
    {"iret", "iretd", "iretq", "lret", "lretq", "ret", "retf", "retq"}
)
_AARCH64_INDIRECT_CALLS = frozenset({"blr", "blraa", "blraaz", "blrab", "blrabz"})
_AARCH64_INDIRECT_BRANCHES = frozenset({"br", "braa", "braaz", "brab", "brabz"})
_AARCH64_RETURNS = frozenset({"ret", "retaa", "retab"})
_AARCH64_CONDITIONAL_BRANCHES = frozenset({"cbz", "cbnz", "tbz", "tbnz"})


@dataclass(frozen=True)
class InstructionSemantics:
    """Architecture-neutral control-flow meaning of one instruction."""

    kind: str
    conditional: bool = False
    direct: bool | None = None
    target_operand: str | None = None


class ArchitectureParser(Protocol):
    """Classify architecture-specific instructions into normalized semantics."""

    architecture: str

    def semantics(self, mnemonic: str, operands: str) -> InstructionSemantics:
        """Return architecture-neutral semantics for one instruction."""


class X86Parser:
    """Classify x86 and x86-64 control-flow instructions."""

    architecture = "x86_64"

    def semantics(self, mnemonic: str, operands: str) -> InstructionSemantics:
        if mnemonic.startswith("nop") or mnemonic == "int3":
            return InstructionSemantics("padding")
        if mnemonic in _X86_RETURNS:
            return InstructionSemantics("return")
        if mnemonic.startswith("call") or mnemonic == "lcall":
            direct = not _x86_indirect_operand(operands)
            return InstructionSemantics(
                "call",
                direct=direct,
                target_operand=operands if direct else None,
            )
        if mnemonic.startswith("jmp") or mnemonic == "j":
            direct = not _x86_indirect_operand(operands)
            return InstructionSemantics(
                "branch",
                direct=direct,
                target_operand=operands if direct else None,
            )
        if (
            mnemonic.startswith("j")
            or mnemonic.startswith("loop")
            or mnemonic in {"jecxz", "jrcxz"}
        ):
            return InstructionSemantics(
                "branch",
                conditional=True,
                direct=True,
                target_operand=operands,
            )
        return InstructionSemantics("other")


class AArch64Parser:
    """Classify AArch64 control-flow instructions."""

    architecture = "aarch64"

    def semantics(self, mnemonic: str, operands: str) -> InstructionSemantics:
        if mnemonic == "nop":
            return InstructionSemantics("padding")
        if mnemonic in _AARCH64_RETURNS:
            return InstructionSemantics("return")
        if mnemonic == "bl":
            return InstructionSemantics(
                "call",
                direct=True,
                target_operand=operands,
            )
        if mnemonic in _AARCH64_INDIRECT_CALLS:
            return InstructionSemantics("call", direct=False)
        if mnemonic == "b":
            return InstructionSemantics(
                "branch",
                direct=True,
                target_operand=operands,
            )
        if mnemonic in _AARCH64_INDIRECT_BRANCHES:
            return InstructionSemantics("branch", direct=False)
        if mnemonic.startswith("b."):
            return InstructionSemantics(
                "branch",
                conditional=True,
                direct=True,
                target_operand=operands,
            )
        if mnemonic in _AARCH64_CONDITIONAL_BRANCHES:
            return InstructionSemantics(
                "branch",
                conditional=True,
                direct=True,
                target_operand=operands.rsplit(",", 1)[-1],
            )
        return InstructionSemantics("other")


_PARSERS: dict[str, ArchitectureParser] = {
    "aarch64": AArch64Parser(),
    "x86_64": X86Parser(),
}


def parser_for(architecture: str) -> ArchitectureParser | None:
    """Return the classifier for a normalized architecture name."""
    return _PARSERS.get(architecture)


def _x86_indirect_operand(operands: str) -> bool:
    value = operands.strip().lower()
    return (
        value.startswith("*")
        or " ptr [" in value
        or value.startswith("[")
        or ("%" in value and "<" not in value)
    )
