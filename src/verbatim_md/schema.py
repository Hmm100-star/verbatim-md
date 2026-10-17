"""Immutable, presentation-independent document model.

Offsets count Python Unicode code points, never bytes or UTF-16 units.
"""
from dataclasses import dataclass
from typing import Literal, TypeAlias

SpanKind = Literal['highlight', 'underline', 'emphasis', 'small', 'cite']
Verification = Literal['unverified', 'source_verified']


@dataclass(frozen=True)
class Span:
    start: int
    end: int
    kind: SpanKind


@dataclass(frozen=True)
class Source:
    id: str
    citation: str
    url: str = ''
    verification: Verification = 'unverified'
    verified_by: str = ''
    verified_at: str = ''
    citation_spans: tuple[Span, ...] = ()


@dataclass(frozen=True)
class Card:
    id: str
    source_id: str
    text: str
    spans: tuple[Span, ...] = ()
    expected_sha256: str | None = None
    line: int = 1


@dataclass(frozen=True)
class Heading:
    level: int
    text: str
    line: int = 1


@dataclass(frozen=True)
class Analytic:
    text: str
    line: int = 1


Block: TypeAlias = Heading | Card | Analytic


@dataclass(frozen=True)
class Document:
    title: str
    sources: tuple[Source, ...]
    blocks: tuple[Block, ...]
