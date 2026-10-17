"""Strict parser for Verbatim-MD v1; evidence is never Markdown-decoded."""
from pathlib import Path
import re
from typing import Any, Hashable, cast

import yaml

from .schema import Analytic, Card, Document, Heading, Source, Span, SpanKind

MAX_INPUT_BYTES = 10 * 1024 * 1024
_ID = re.compile(r'[A-Za-z][A-Za-z0-9_-]{0,63}\Z')
_KINDS = {'highlight', 'underline', 'emphasis', 'small', 'cite'}


class ParseError(ValueError):
    """An actionable input error with a one-based source line."""

    def __init__(self, message: str, line: int = 1):
        self.line = line
        super().__init__(f'line {line}: {message}')


class _StrictLoader(yaml.SafeLoader):
    def __init__(self, stream: Any):
        super().__init__(stream)
        self._depth = 0

    def compose_node(self, parent: Any, index: Any) -> Any:
        if self.check_event(yaml.AliasEvent):
            event = self.peek_event()
            raise ParseError('YAML aliases are not supported', event.start_mark.line + 1)
        event = self.peek_event()
        if getattr(event, 'anchor', None) is not None:
            raise ParseError('YAML anchors and aliases are not supported', event.start_mark.line + 1)
        self._depth += 1
        try:
            if self._depth > 64:
                raise ParseError('YAML nesting exceeds 64 levels', self.peek_event().start_mark.line + 1)
            return super().compose_node(parent, index)
        finally:
            self._depth -= 1

    def construct_mapping(self, node: Any, deep: bool = False) -> dict[Hashable, Any]:
        result: dict[Hashable, Any] = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if not isinstance(key, str):
                raise ParseError('metadata keys must be strings', key_node.start_mark.line + 1)
            if key in result:
                raise ParseError(f'duplicate metadata key {key!r}', key_node.start_mark.line + 1)
            result[key] = self.construct_object(value_node, deep=deep)
        return result


def _yaml(text: str, line: int) -> dict[str, Any]:
    try:
        value = yaml.load(text, Loader=_StrictLoader)
    except ParseError as exc:
        raise ParseError(str(exc).split(': ', 1)[1], line + exc.line - 1) from exc
    except yaml.YAMLError as exc:
        mark = getattr(exc, 'problem_mark', None)
        raise ParseError(f'invalid YAML: {getattr(exc, "problem", str(exc))}', line + (mark.line if mark else 0)) from exc
    if not isinstance(value, dict):
        raise ParseError('metadata must be a YAML mapping', line)
    return value


def _keys(value: dict[str, Any], allowed: set[str], required: set[str], line: int) -> None:
    unknown = set(value) - allowed
    missing = required - set(value)
    if unknown:
        raise ParseError(f'unknown metadata keys: {", ".join(sorted(unknown))}', line)
    if missing:
        raise ParseError(f'missing metadata keys: {", ".join(sorted(missing))}', line)


def _text(value: Any, label: str, line: int, empty: bool = False) -> str:
    if not isinstance(value, str) or (not empty and not value.strip()):
        raise ParseError(f'{label} must be a {"nonempty " if not empty else ""}string', line)
    if any(not (c in '\t\n\r' or '\x20' <= c <= '\ud7ff' or '\ue000' <= c <= '\ufffd' or '\U00010000' <= c <= '\U0010ffff') for c in value):
        raise ParseError(f'{label} contains an XML-invalid character', line)
    return value


def _id(value: Any, label: str, line: int) -> str:
    value = _text(value, label, line)
    if not _ID.fullmatch(value):
        raise ParseError(f'{label} must use 1–64 ASCII letters, digits, underscores or hyphens, beginning with a letter', line)
    return value


def _spans(value: Any, text: str, line: int, citation: bool = False) -> tuple[Span, ...]:
    if not isinstance(value, list):
        raise ParseError('spans must be a list', line)
    result = []
    for entry in value:
        if not isinstance(entry, dict):
            raise ParseError('each span must be a mapping', line)
        _keys(entry, {'start', 'end', 'kind'}, {'start', 'end', 'kind'}, line)
        start, end, kind = entry['start'], entry['end'], entry['kind']
        if type(start) is not int or type(end) is not int or not 0 <= start < end <= len(text):
            raise ParseError(f'span requires integer 0 <= start < end <= {len(text)}', line)
        if not isinstance(kind, str) or kind not in _KINDS or (kind == 'cite' and not citation):
            raise ParseError(f'unsupported span kind {kind!r}', line)
        result.append(Span(start, end, cast(SpanKind, kind)))
    if len(set(result)) != len(result):
        raise ParseError('duplicate formatting span', line)
    return tuple(result)


def _source(value: Any, line: int) -> Source:
    if not isinstance(value, dict):
        raise ParseError('each source must be a mapping', line)
    _keys(value, {'id', 'citation', 'url', 'verification', 'verified_by', 'verified_at', 'citation_spans'}, {'id', 'citation'}, line)
    citation = _text(value['citation'], 'citation', line)
    verification = value.get('verification', 'unverified')
    if verification not in ('unverified', 'source_verified'):
        raise ParseError('verification must be unverified or source_verified', line)
    by = _text(value.get('verified_by', ''), 'verified_by', line, empty=True)
    at = _text(value.get('verified_at', ''), 'verified_at', line, empty=True)
    if verification == 'source_verified' and (not by.strip() or not at.strip()):
        raise ParseError('source_verified requires verified_by and verified_at provenance', line)
    return Source(_id(value['id'], 'source id', line), citation,
                  _text(value.get('url', ''), 'url', line, empty=True), verification,
                  by, at, _spans(value.get('citation_spans', []), citation, line, citation=True))


def parse_markdown(text: str) -> Document:
    """Parse strict UTF-8/LF Markdown without transforming quotation text.

    The line break immediately before a closing literal fence is structural.
    An extra blank body line preserves one trailing newline in canonical text.
    """
    if not isinstance(text, str):
        raise TypeError('Markdown input must be a string')
    try:
        size = len(text.encode('utf-8'))
    except UnicodeEncodeError as exc:
        raise ParseError('input contains an invalid Unicode surrogate') from exc
    if size > MAX_INPUT_BYTES:
        raise ParseError('input exceeds 10 MiB limit')
    if '\r' in text:
        raise ParseError('CR/CRLF line endings are unsupported; save as UTF-8 with LF to preserve exact offsets', text[:text.index('\r')].count('\n') + 1)
    lines = text.split('\n')
    if not lines or lines[0] != '---':
        raise ParseError('document must start with YAML frontmatter ---')
    try:
        front_end = lines.index('---', 1)
    except ValueError as exc:
        raise ParseError('missing closing frontmatter ---') from exc
    front = _yaml('\n'.join(lines[1:front_end]), 2)
    _keys(front, {'version', 'title', 'sources'}, {'version', 'title', 'sources'}, 2)
    if type(front['version']) is not int or front['version'] != 1:
        raise ParseError('version must be integer 1', 2)
    title = _text(front['title'], 'title', 2)
    if not isinstance(front['sources'], list):
        raise ParseError('sources must be a list', 2)
    sources = tuple(_source(s, 2) for s in front['sources'])
    source_ids = [s.id for s in sources]
    if len(set(source_ids)) != len(source_ids):
        raise ParseError('duplicate source id', 2)
    blocks: list[Heading | Card | Analytic] = []
    card_ids: set[str] = set()
    level = 0
    i = front_end + 1
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        heading = re.fullmatch(r'(#{1,4}) (\S.*)', line)
        if heading:
            next_level = len(heading[1])
            if next_level > level + 1:
                raise ParseError('heading skips a hierarchy level', i + 1)
            blocks.append(Heading(next_level, _text(heading[2], 'heading', i + 1), i + 1))
            level = next_level
            i += 1
            continue
        if line not in (':::card', ':::analytic'):
            raise ParseError('expected #–#### heading, :::card or :::analytic', i + 1)
        start = i
        is_card = line == ':::card'
        i += 1
        metadata_start = i
        while i < len(lines) and lines[i] != '```text':
            if lines[i] == ':::':
                raise ParseError('missing ```text literal quotation fence', i + 1)
            i += 1
        if i == len(lines):
            raise ParseError('missing ```text literal fence', start + 1)
        metadata = _yaml('\n'.join(lines[metadata_start:i]), metadata_start + 1) if is_card else {}
        if not is_card and any(s.strip() for s in lines[metadata_start:i]):
            raise ParseError('analytic blocks do not accept metadata', metadata_start + 1)
        i += 1
        body_start = i
        while i < len(lines) and lines[i] != '```':
            i += 1
        if i == len(lines):
            raise ParseError('missing closing ``` literal fence', start + 1)
        body = _text('\n'.join(lines[body_start:i]), 'evidence' if is_card else 'analytic', body_start + 1)
        i += 1
        if i >= len(lines) or lines[i] != ':::':
            raise ParseError('literal fence must be followed immediately by :::', i + 1)
        i += 1
        if not is_card:
            blocks.append(Analytic(body, start + 1))
            continue
        _keys(metadata, {'id', 'source', 'spans', 'sha256'}, {'id', 'source'}, metadata_start + 1)
        card_id = _id(metadata['id'], 'card id', metadata_start + 1)
        if card_id in card_ids:
            raise ParseError(f'duplicate card id {card_id!r}', start + 1)
        card_ids.add(card_id)
        source = _id(metadata['source'], 'source reference', metadata_start + 1)
        if source not in source_ids:
            raise ParseError(f'unknown source reference {source!r}', metadata_start + 1)
        digest = metadata.get('sha256')
        if digest is not None and (not isinstance(digest, str) or not re.fullmatch('[a-f0-9]{64}', digest)):
            raise ParseError('sha256 must be a quoted lowercase 64-character hexadecimal string', metadata_start + 1)
        blocks.append(Card(card_id, source, body, _spans(metadata.get('spans', []), body, metadata_start + 1), digest, start + 1))
    if not blocks:
        raise ParseError('document must contain at least one block', front_end + 2)
    document = Document(title, sources, tuple(blocks))
    from .validator import require_valid
    try:
        require_valid(document)
    except ValueError as exc:
        match = re.search(r'line (\d+):', str(exc))
        raise ParseError(str(exc), int(match[1]) if match else 2) from exc
    return document


def parse_file(path: str | Path) -> Document:
    """Read UTF-8 without universal-newline or BOM normalization."""
    path = Path(path)
    if path.stat().st_size > MAX_INPUT_BYTES:
        raise ParseError('input exceeds 10 MiB limit')
    try:
        with path.open('r', encoding='utf-8', newline='') as stream:
            return parse_markdown(stream.read())
    except UnicodeDecodeError as exc:
        raise ParseError('input must be UTF-8') from exc


def load_yaml(text: str) -> Any:
    """Load safe YAML, rejecting aliases, duplicate keys and custom tags.

    Intended for configuration as well as document metadata. Schema validation
    remains the caller's responsibility.
    """
    if len(text.encode('utf-8')) > MAX_INPUT_BYTES:
        raise ParseError('YAML exceeds 10 MiB limit')
    try:
        return yaml.load(text, Loader=_StrictLoader)
    except ParseError:
        raise
    except yaml.YAMLError as exc:
        mark = getattr(exc, 'problem_mark', None)
        raise ParseError(f'invalid YAML: {getattr(exc, "problem", str(exc))}', (mark.line if mark else 0) + 1) from exc
