from dataclasses import FrozenInstanceError

import pytest

from verbatim_md.parser import ParseError, load_yaml, parse_file, parse_markdown
from verbatim_md.schema import Card

PREFIX = '''---
version: 1
title: Test
sources:
  - id: source
    citation: "Example 2026"
---
# Pocket
## Hat
### Block
#### Tag
:::card
id: card
source: source
'''


def case(body='A😀é\tline\nsecond line', metadata=''):
    return PREFIX + metadata + '```text\n' + body + '\n```\n:::\n'


def test_literal_preservation_and_immutable_schema():
    text = '  A😀é\tline  \n\n[u]literal[/u] \\ * < >\n'
    document = parse_markdown(case(text))
    card = document.blocks[-1]
    assert isinstance(card, Card)
    assert card.text == text
    with pytest.raises(FrozenInstanceError):
        card.text = 'changed'


def test_crossing_spans_codepoints():
    card = parse_markdown(case(metadata='spans:\n  - {start: 0, end: 4, kind: highlight}\n  - {start: 2, end: 6, kind: underline}\n')).blocks[-1]
    assert card.text[0:4] == 'A😀é'
    assert [(s.start, s.end) for s in card.spans] == [(0, 4), (2, 6)]


@pytest.mark.parametrize('old,new', [
    ('version: 1', 'version: true'),
    ('title: Test', 'title: Test\nunknown: x'),
    ('title: Test', 'title: Test\ntitle: Again'),
    ('source: source', 'source: missing'),
    ('id: card', 'id: 42'),
    ('#### Tag', '## Hat\n#### Tag'),
    ('citation: "Example 2026"', 'citation: "Example\\n2026"'),
])
def test_invalid_schema(old, new):
    with pytest.raises(ParseError, match='line'):
        parse_markdown(case().replace(old, new))


@pytest.mark.parametrize('span', [
    '{start: true, end: 2, kind: highlight}',
    '{start: 0, end: 999, kind: underline}',
    '{start: 2, end: 2, kind: small}',
    '{start: 0, end: 2, kind: cite}',
    '{start: 0, end: 2, kind: unknown}',
    '{start: 0, end: 2, kind: small, extra: x}',
])
def test_bad_spans(span):
    with pytest.raises(ParseError):
        parse_markdown(case(metadata=f'spans: [{span}]\n'))


@pytest.mark.parametrize('body', ['', '  ', 'bad\x01control', 'bad\rnewline'])
def test_bad_text(body):
    with pytest.raises(ParseError):
        parse_markdown(case(body))


def test_source_verification_requires_provenance():
    with pytest.raises(ParseError, match='requires'):
        parse_markdown(case().replace('citation: "Example 2026"', 'citation: "Example 2026"\n    verification: source_verified'))


def test_digest_mismatch_rejected():
    with pytest.raises(ParseError, match='SHA-256 mismatch'):
        parse_markdown(case(metadata='sha256: "' + '0' * 64 + '"\n'))


@pytest.mark.parametrize('payload', ['a: &a [1]\nb: *a', 'a: 1\na: 2', 'a: !exploit x', '[' * 70 + '0' + ']' * 70])
def test_yaml_security(payload):
    with pytest.raises(ParseError):
        load_yaml(payload)


def test_read_rejects_crlf(tmp_path):
    path = tmp_path / 'case.md'
    path.write_bytes(case().replace('\n', '\r\n').encode())
    with pytest.raises(ParseError, match='CR/CRLF'):
        parse_file(path)


def test_analytic():
    text = '---\nversion: 1\ntitle: X\nsources: []\n---\n:::analytic\n```text\nOriginal analysis.\n```\n:::\n'
    assert parse_markdown(text).blocks[0].text == 'Original analysis.'


def test_duplicate_cards_and_missing_tag():
    with pytest.raises(ParseError, match='duplicate card id'):
        parse_markdown(case() + '#### Again\n' + case().split(':::card', 1)[1].join([':::card', '']))
    with pytest.raises(ParseError, match='Tag'):
        parse_markdown(case().replace('#### Tag\n', ''))
