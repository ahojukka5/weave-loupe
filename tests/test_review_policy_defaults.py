"""Tests for public staged-review policy defaults."""

from weave_loupe.scalable_review import (
    DEFAULT_CHUNK_OUTPUT_TOKENS,
    ReviewPolicy,
)


def test_artifact_review_output_reserve_defaults_to_1024() -> None:
    policy = ReviewPolicy()

    assert DEFAULT_CHUNK_OUTPUT_TOKENS == 1024
    assert policy.chunk_output_tokens == 1024


def test_artifact_review_output_reserve_remains_overridable() -> None:
    policy = ReviewPolicy(chunk_output_tokens=768)

    assert policy.chunk_output_tokens == 768
