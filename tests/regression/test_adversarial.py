"""Independent invalid programmatic input and exact range regressions."""
from dataclasses import replace
from zipfile import ZipFile
from xml.etree import ElementTree as ET

import pytest

from verbatim_md.api import export_document
from verbatim_md.schema import Card, Document, Heading, Source, Span
from verbatim_md.validator import require_valid

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'


def document(card):
    return Document('Audit', (Source('s', 'Author 2026', citation_spans=(Span(0, 6, 'cite'),)),),
                    tuple(Heading(i, f'Level {i}') for i in range(1, 5)) + (card,))


@pytest.mark.parametrize('span', [Span(-1, 2, 'highlight'), Span(0, 99, 'small'),
                                 Span(1, 1, 'underline'), Span(True, 2, 'emphasis'),
                                 Span(0, 2, 'cite')])
def test_invalid_api_spans(span):
    with pytest.raises(ValueError):
        require_valid(document(Card('c', 's', 'abcd', (span,))))


@pytest.mark.parametrize('text', ['', '  ', 'nul\x00', 'surrogate\ud800', 'line\rbreak'])
def test_invalid_api_evidence_is_actionable(text):
    with pytest.raises(ValueError):
        require_valid(document(Card('c', 's', text)))


@pytest.mark.parametrize('bad', [None, 42, [], {'text': 'quote'}])
def test_wrong_api_card_text_is_actionable(bad):
    with pytest.raises(ValueError):
        require_valid(document(Card('c', 's', bad)))


def test_unknown_block_is_actionable():
    with pytest.raises(ValueError):
        require_valid(Document('Audit', (), (object(),)))


def test_exact_crossing_ranges_and_card_reset(tmp_path):
    text = 'a😀e\u0301\tb\ncdef'
    spans = (Span(0, 4, 'highlight'), Span(2, 8, 'underline'),
             Span(3, 9, 'emphasis'), Span(1, 3, 'small'))
    first = Card('first', 's', text, spans)
    doc = document(first)
    doc = replace(doc, blocks=doc.blocks + (Heading(4, 'Second'), Card('second', 's', 'plain')))
    path = tmp_path/'ranges.docx'
    export_document(doc, path)
    with ZipFile(path) as z:
        root = ET.fromstring(z.read('word/document.xml'))
    paragraphs = root.find(W+'body').findall(W+'p')
    offset = 0
    for p in paragraphs[5:7]:
        for run in p.findall(W+'r'):
            chars = ''.join((node.text or '') if node.tag == W+'t' else '\t' if node.tag == W+'tab' else '' for node in run)
            props = run.find(W+'rPr')
            for character in chars:
                active = {s.kind for s in spans if s.start <= offset < s.end}
                assert (props.find(W+'highlight') is not None) == ('highlight' in active)
                assert (props.find(W+'u') is not None) == bool(active & {'underline', 'emphasis'})
                assert props.find(W+'sz').get(W+'val') == ('16' if 'small' in active else '22')
                offset += 1
        offset += 1
    assert offset - 1 == len(text)
    plain = paragraphs[-1]
    assert ''.join(plain.itertext()) == 'plain'
    assert plain.find('.//'+W+'highlight') is None
    assert plain.find('.//'+W+'u') is None


def test_api_duplicate_spans_match_parser_rejection():
    span = Span(0, 2, 'highlight')
    with pytest.raises(ValueError, match='duplicate'):
        require_valid(document(Card('c', 's', 'abcd', (span, span))))


def test_api_verified_provenance_cannot_be_whitespace():
    doc = document(Card('c', 's', 'abcd'))
    bad = Source('s', 'Author 2026', url=' ', verification='source_verified',
                 verified_by=' ', verified_at=' ')
    with pytest.raises(ValueError):
        require_valid(replace(doc, sources=(bad,)))


def test_immutable_api_requires_tuple_collections():
    doc = document(Card('c', 's', 'abcd'))
    with pytest.raises(ValueError):
        require_valid(replace(doc, blocks=list(doc.blocks)))


def test_heading_outline_levels_and_style_types(tmp_path):
    path = tmp_path/'styles.docx'
    export_document(document(Card('c', 's', 'abcd')), path)
    with ZipFile(path) as z:
        styles = ET.fromstring(z.read('word/styles.xml'))
        root = ET.fromstring(z.read('word/document.xml'))
    by_id = {n.get(W+'styleId'): n for n in styles}
    for level in range(1, 5):
        style = by_id[f'Heading{level}']
        assert style.get(W+'type') == 'paragraph'
        assert style.find(W+'pPr/'+W+'outlineLvl').get(W+'val') == str(level-1)
    for identifier in ('Style13ptBold', 'StyleUnderline', 'Emphasis'):
        assert by_id[identifier].get(W+'type') == 'character'
    paragraphs = root.find(W+'body').findall(W+'p')
    assert [p.find(W+'pPr/'+W+'pStyle').get(W+'val') for p in paragraphs[:4]] == [f'Heading{i}' for i in range(1, 5)]
    citation = paragraphs[4]
    runs = citation.findall(W+'r')
    assert runs[0].find(W+'rPr/'+W+'rStyle').get(W+'val') == 'Style13ptBold'
    assert runs[0].find(W+'t').text == 'Author'
    assert runs[1].find(W+'t').text == ' 2026'
    assert runs[1].find(W+'rPr/'+W+'rStyle') is None


def test_invalid_heading_type_has_actionable_error():
    doc = document(Card('c', 's', 'abcd'))
    with pytest.raises(ValueError):
        require_valid(replace(doc, blocks=(Heading('1', 'bad'),) + doc.blocks[1:]))


def test_invalid_unicode_reports_integrity_error_not_codec_traceback():
    with pytest.raises(ValueError, match='XML-safe'):
        require_valid(document(Card('c', 's', 'bad\ud800')))


def test_explicit_fonts_have_no_theme_override_and_headings_are_not_italic(tmp_path):
    path = tmp_path/'fonts.docx'
    export_document(document(Card('c', 's', 'abcd')), path)
    with ZipFile(path) as z:
        styles = ET.fromstring(z.read('word/styles.xml'))
    by_id = {n.get(W+'styleId'): n for n in styles}
    for identifier in ('Normal', 'Heading1', 'Heading2', 'Heading3', 'Heading4',
                       'Style13ptBold', 'StyleUnderline', 'Emphasis'):
        fonts = by_id[identifier].find(W+'rPr/'+W+'rFonts')
        assert not any(k.endswith('Theme') for k in fonts.attrib)
        assert [fonts.get(W+key) for key in ('ascii', 'hAnsi', 'eastAsia', 'cs')] == ['Arial'] * 4
    for level in range(1, 5):
        assert by_id[f'Heading{level}'].find(W+'rPr/'+W+'i').get(W+'val') in ('0', 'false')


def test_repeated_same_attribute_overlap_survives_sweep_endpoints(tmp_path):
    text = 'abcdefghij\nklmnopqrst\nuvwxyz'
    spans = (Span(0, 20, 'highlight'), Span(4, 24, 'highlight'),
             Span(2, 17, 'underline'), Span(8, 22, 'underline'))
    path = tmp_path/'sweep.docx'
    export_document(document(Card('c', 's', text, spans)), path)
    with ZipFile(path) as z:
        root = ET.fromstring(z.read('word/document.xml'))
    offset = 0
    for paragraph in root.find(W+'body').findall(W+'p')[5:]:
        for run in paragraph.findall(W+'r'):
            chars = ''.join(run.itertext())
            props = run.find(W+'rPr')
            for char in chars:
                active = {s.kind for s in spans if s.start <= offset < s.end}
                assert (props.find(W+'highlight') is not None) == ('highlight' in active)
                assert (props.find(W+'u') is not None) == ('underline' in active)
                offset += 1
        offset += 1
    assert offset - 1 == len(text)


def test_span_limit_rejects_before_rendering():
    from verbatim_md.validator import MAX_SPANS
    spans = tuple(Span(0, i+1, 'highlight') for i in range(MAX_SPANS+1))
    with pytest.raises(ValueError, match='formatting spans'):
        require_valid(document(Card('c', 's', 'a' * (MAX_SPANS+1), spans)))


def test_canonical_size_limit_rejects_before_rendering():
    from verbatim_md.validator import MAX_CANONICAL_BYTES
    with pytest.raises(ValueError, match='10 MiB'):
        require_valid(document(Card('c', 's', 'a' * (MAX_CANONICAL_BYTES+1))))
