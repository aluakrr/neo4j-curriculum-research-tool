"""Normalization helpers for human-oriented curriculum records."""

from __future__ import annotations


def split_elective_entry(value: str) -> tuple[str, ...]:
    """Split slash-separated elective alternatives and remove duplicates."""
    seen: set[str] = set()
    result: list[str] = []
    for part in value.split("/"):
        normalized = " ".join(part.split())
        if normalized and normalized.casefold() not in seen:
            result.append(normalized)
            seen.add(normalized.casefold())
    return tuple(result)

