"""Inspect actual generated OOXML, not merely rendering helper calls."""
from zipfile import ZipFile
from xml.etree import ElementTree as ET

from verbatim_md.config import Profile
from verbatim_md.evidence import inspect_docx
from verbatim_md.renderer import render_document
from verbatim_md.schema import Card, Document, Heading, Source, Span

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'


def document(text='abcdef\ngh😀ij\n'):
    return Document('Test', (Source('s', 'Writer 2026, Example',
                    citation_spans=(Span(0, 6, 'cite'), Span(7, 11, 'cite'))),),
                    tuple(Heading(i, str(i)) for i in range(1, 5)) +
                    (Card('card', 's', text, (Span(1, 8, 'highlight'),
                      Span(2, 10, 'underline'), Span(4, 11, 'emphasis'),
                      Span(0, 1, 'small'))),))


def test_exact_text_and_reproducible_package(tmp_path):
    doc = document()
    first = render_document(doc, tmp_path / 'a.docx')
    second = render_document(doc, tmp_path / 'b.docx')
    assert first.read_bytes() == second.read_bytes()
    report = inspect_docx(first)
    assert report['internally_preserved']
    assert report['cards'][0]['text'] == doc.blocks[-1].text


def test_styles_and_crossing_spans(tmp_path):
    path = render_document(document(), tmp_path / 'case.docx')
    with ZipFile(path) as package:
        styles = ET.fromstring(package.read('word/styles.xml'))
        body = ET.fromstring(package.read('word/document.xml'))
    for level, alias in enumerate(('Pocket', 'Hat', 'Block', 'Tag'), 1):
        style = next(s for s in styles if s.get(W+'styleId') == f'Heading{level}')
        assert style.find(W+'aliases').get(W+'val') == alias
    cite = next(s for s in styles if s.get(W+'styleId') == 'Style13ptBold')
    assert cite.get(W+'type') == 'character'
    assert cite.find(W+'aliases').get(W+'val') == 'Cite'
    paragraphs = body.find(W+'body').findall(W+'p')
    citation = paragraphs[4]
    styled = [r for r in citation.findall(W+'r') if r.find(W+'rPr/'+W+'rStyle') is not None]
    assert [''.join(r.itertext()) for r in styled] == ['Writer', '2026']
    # Character e has highlight + emphasis + underline simultaneously.
    run = next(r for r in paragraphs[5].findall(W+'r') if r.find(W+'t').text == 'ef')
    props = run.find(W+'rPr')
    assert props.find(W+'highlight').get(W+'val') == 'yellow'
    assert props.find(W+'u').get(W+'val') == 'single'
    assert props.find(W+'b') is not None
    assert props.find(W+'rStyle').get(W+'val') == 'Emphasis'


def test_shrink_uses_non_underlined_context(tmp_path):
    path = render_document(document(), tmp_path / 'case.docx', Profile(shrink_unread=True))
    with ZipFile(path) as package:
        body = ET.fromstring(package.read('word/document.xml'))
    paragraphs = body.find(W+'body').findall(W+'p')
    runs = paragraphs[5].findall(W+'r')
    sizes = {r.find(W+'t').text: r.find(W+'rPr/'+W+'sz').get(W+'val') for r in runs}
    assert sizes['a'] == '16'
    assert sizes['b'] == '16'  # Highlight alone does not prevent documented Shrink.
    assert sizes['cd'] == '22'
    assert sizes['ef'] == '22'
