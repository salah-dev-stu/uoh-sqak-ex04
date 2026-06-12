"""Typed models for the Graphify graph (consumed from ``graph.json``)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class Confidence(StrEnum):
    """Edge evidence layer (Graphify schema)."""

    EXTRACTED = "EXTRACTED"
    INFERRED = "INFERRED"
    AMBIGUOUS = "AMBIGUOUS"

    @classmethod
    def from_str(cls, value: Any) -> Confidence:
        return cls(str(value).upper())


# Certainty ordering for confidence filtering (higher = more certain).
RANK: dict[Confidence, int] = {
    Confidence.AMBIGUOUS: 0,
    Confidence.INFERRED: 1,
    Confidence.EXTRACTED: 2,
}


@dataclass
class Node:
    id: str
    label: str = ""
    file_type: str = ""
    source_file: str = ""

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Node:
        return cls(
            id=d["id"],
            label=d.get("label", ""),
            file_type=d.get("file_type", ""),
            source_file=d.get("source_file", ""),
        )


@dataclass
class Edge:
    source: str
    target: str
    relation: str = ""
    confidence: Confidence = Confidence.EXTRACTED
    weight: float = 1.0
    source_file: str = ""

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Edge:
        return cls(
            source=d["source"],
            target=d["target"],
            relation=d.get("relation", ""),
            confidence=Confidence.from_str(d.get("confidence", "EXTRACTED")),
            weight=float(d.get("weight", 1.0)),
            source_file=d.get("source_file", ""),
        )
