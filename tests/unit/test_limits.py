"""Bounded programmatic input and large formatting/evidence regressions."""
from dataclasses import replace

import pytest

from verbatim_md.api import export_document
from verbatim_md.evidence import inspect_docx
from verbatim_md.renderer import _formatting
from verbatim_md.schema import Card, Document, Heading, Source, Span
from verbatim_md.validator import MAX_CANONICAL_BYTES, MAX_PARAGRAPHS, MAX_SPANS, require_valid


def document(text='original', spans=()):
    source = Source('s', 'Writer 2026', url='https://example.org/original',
                    verification='source_verified', verified_by='Reviewer',
                    verified_at='2026-10-17')
    return Document('Limits', (source,), tuple(Heading(n, str(n)) for n in range(1, 5))
                    + (Card('c', 's', text, spans),))


def test_programmatic_text_limit():
    with pytest.raises(ValueError, match='10 MiB'):
        require_valid(document('x' * (MAX_CANONICAL_BYTES + 1)))


def test_programmatic_paragraph_limit():
    with pytest.raises(ValueError, match='generated paragraphs'):
        require_valid(document('x\n' * MAX_PARAGRAPHS))


def test_programmatic_span_limit():
    spans = tuple(Span(i, i + 1, 'highlight') for i in range(MAX_SPANS + 1))
    with pytest.raises(ValueError, match='formatting spans'):
        require_valid(document('x' * (MAX_SPANS + 1), spans))


def test_citation_span_limit():
    doc = document()
    source = replace(doc.sources[0], citation='x' * (MAX_SPANS + 1),
                     citation_spans=tuple(Span(i, i + 1, 'cite') for i in range(MAX_SPANS + 1)))
    with pytest.raises(ValueError, match='formatting spans'):
        require_valid(replace(doc, sources=(source,)))


def test_overlapping_same_kind_keeps_attribute_until_last_end():
    points, states = _formatting((Span(0, 4, 'highlight'), Span(2, 7, 'highlight'),
                                 Span(3, 5, 'underline')))
    assert points == [0, 2, 3, 4, 5, 7]
    assert states == [frozenset({'highlight'}), frozenset({'highlight'}),
                      frozenset({'highlight', 'underline'}),
                      frozenset({'highlight', 'underline'}), frozenset({'highlight'}),
                      frozenset()]


def test_export_retains_full_provenance_declarations(tmp_path):
    output = tmp_path / 'provenance.docx'
    export_document(document(), output)
    report = inspect_docx(output)
    card = report['cards'][0]
    assert card['text'] == 'original'
    assert card['source_id'] == 's'
    assert card['citation'] == 'Writer 2026'
    assert card['url'] == 'https://example.org/original'
    assert card['verified_by'] == 'Reviewer'
    assert card['verified_at'] == '2026-10-17'
    assert card['declared_source_verification'] == 'source_verified'
    assert report['source_verification'] == 'not independently checked'
