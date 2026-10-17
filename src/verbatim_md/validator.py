"""Validate both parsed and programmatically constructed immutable documents."""
import re

from .evidence import text_hash
from .schema import Analytic, Card, Document, Heading, Source, Span

ID = re.compile(r'^[A-Za-z][A-Za-z0-9_-]{0,63}$')
KINDS = {'highlight', 'underline', 'emphasis', 'small', 'cite'}
MAX_CANONICAL_BYTES = 10 * 1024 * 1024
MAX_SPANS = 10_000
MAX_PARAGRAPHS = 100_000


def valid_text(text: str) -> bool:
    return isinstance(text, str) and all(
        c in '\t\n\r' or 0x20 <= ord(c) <= 0xD7FF or 0xE000 <= ord(c) <= 0xFFFD
        or 0x10000 <= ord(c) <= 0x10FFFF for c in text)


def validate_spans(text: str, spans: tuple[Span, ...], label: str, citation: bool = False) -> list[str]:
    errors = []
    if len(spans) > MAX_SPANS:
        return [f'{label}: exceeds {MAX_SPANS:,} formatting spans']
    for span in spans:
        if (not isinstance(span, Span) or type(span.start) is not int or type(span.end) is not int
                or not 0 <= span.start < span.end <= len(text)
                or not isinstance(span.kind, str) or span.kind not in KINDS or (span.kind == 'cite' and not citation)):
            errors.append(f'{label}: invalid formatting span {span!r}')
    valid = [span for span in spans if isinstance(span, Span) and isinstance(span.kind, str)
             and type(span.start) is int and type(span.end) is int]
    if len(set(valid)) != len(valid):
        errors.append(f'{label}: duplicate formatting span')
    return errors


def _check_model(document: Document) -> None:
    """Type hints are not runtime checks: reject malformed programmatic objects."""
    if (not isinstance(document, Document) or not isinstance(document.title, str)
            or not isinstance(document.sources, tuple) or not isinstance(document.blocks, tuple)):
        raise ValueError('Document requires a string title and immutable source/block tuples')
    for source in document.sources:
        if not isinstance(source, Source) or any(not isinstance(getattr(source, f), str)
                for f in ('id', 'citation', 'url', 'verification', 'verified_by', 'verified_at')):
            raise ValueError('Source metadata must contain strings')
        if not isinstance(source.citation_spans, tuple):
            raise ValueError('Citation spans must be an immutable tuple')
    for block in document.blocks:
        if not isinstance(block, (Heading, Analytic, Card)):
            raise ValueError('Unknown document block; expected Heading, Analytic or Card')
        if not isinstance(block.text, str) or type(block.line) is not int or block.line < 1:
            raise ValueError('Block requires string text and a positive integer line')
        if isinstance(block, Heading) and type(block.level) is not int:
            raise ValueError('Heading level must be an integer')
        if isinstance(block, Card):
            if (not isinstance(block.id, str) or not isinstance(block.source_id, str)
                    or not isinstance(block.spans, tuple)
                    or (block.expected_sha256 is not None and not isinstance(block.expected_sha256, str))):
                raise ValueError('Card requires string identifiers, tuple spans and optional string hash')


def validate_document(document: Document) -> dict:
    _check_model(document)
    texts = [document.title]
    for source in document.sources:
        texts.extend((source.citation, source.url, source.verified_by, source.verified_at))
    texts.extend(block.text for block in document.blocks)
    total_bytes = sum(len(text.encode('utf-8', errors='surrogatepass')) for text in texts)
    if total_bytes > MAX_CANONICAL_BYTES:
        raise ValueError('Document canonical text and metadata exceed 10 MiB')
    paragraphs = sum(block.text.count('\n') + 1 + isinstance(block, Card)
                     for block in document.blocks)
    if paragraphs > MAX_PARAGRAPHS:
        raise ValueError(f'Document exceeds {MAX_PARAGRAPHS:,} generated paragraphs')
    errors = []
    warnings = []
    if not valid_text(document.title) or not document.title.strip():
        errors.append('Document title must be nonempty XML-safe text')
    sources = {}
    for source in document.sources:
        if not ID.fullmatch(source.id) or source.id in sources:
            errors.append(f'Invalid or duplicate source identifier: {source.id}')
        sources[source.id] = source
        if not valid_text(source.citation) or not source.citation.strip() or '\n' in source.citation or '\r' in source.citation:
            errors.append(f'Source {source.id}: citation must be a nonempty single paragraph')
        for field in (source.url, source.verified_by, source.verified_at):
            if not valid_text(field):
                errors.append(f'Source {source.id}: invalid provenance text')
        if source.verification not in ('unverified', 'source_verified'):
            errors.append(f'Source {source.id}: invalid verification status')
        if source.verification == 'source_verified' and not (source.verified_by.strip() and source.verified_at.strip() and source.url.strip()):
            errors.append(f'Source {source.id}: verified evidence requires URL, verifier and date')
        if not any(span.kind == 'cite' for span in source.citation_spans if isinstance(span, Span)):
            warnings.append(f'Source {source.id}: no Cite span marks the author/date; Verbatim card detection is unverified')
        if source.verification == 'unverified':
            warnings.append(f'Source {source.id}: source text has not been independently verified')
        errors.extend(validate_spans(source.citation, source.citation_spans, f'Source {source.id}', True))
    cards = []
    seen = set()
    last_level = 0
    tag_ready = False
    for block in document.blocks:
        label = f'line {block.line}'
        if isinstance(block, Heading):
            if type(block.level) is not int or not 1 <= block.level <= 4 or block.level > last_level + 1:
                errors.append(f'{label}: heading levels must be 1–4 without skipping levels')
            last_level = block.level
            tag_ready = block.level == 4
            if not valid_text(block.text) or not block.text.strip() or '\n' in block.text or '\r' in block.text:
                errors.append(f'{label}: invalid heading text')
        elif isinstance(block, Analytic):
            tag_ready = False
            if not valid_text(block.text) or not block.text.strip():
                errors.append(f'{label}: analytic must have XML-safe nonempty text')
        elif isinstance(block, Card):
            if not tag_ready:
                errors.append(f'{label}: every card requires an immediately preceding level 4 Tag')
            tag_ready = False
            if not ID.fullmatch(block.id) or block.id in seen:
                errors.append(f'{label}: invalid or duplicate card identifier {block.id}')
            seen.add(block.id)
            if block.source_id not in sources:
                errors.append(f'{label}: unknown source {block.source_id}')
            if not valid_text(block.text) or not block.text.strip() or '\r' in block.text:
                errors.append(f'{label}: quotation must be nonempty XML-safe text with LF newlines')
            errors.extend(validate_spans(block.text, block.spans, f'{label} card {block.id}'))
            if not valid_text(block.text):
                continue
            digest = text_hash(block.text)
            if block.expected_sha256 is not None and block.expected_sha256 != digest:
                errors.append(f'{label} card {block.id}: SHA-256 mismatch; restore text or explicitly review and repin')
            cards.append({'id': block.id, 'sha256': digest, 'characters': len(block.text)})
        else:
            errors.append('Unknown document block')
    if not document.blocks:
        errors.append('Document has no content')
    return {'valid': not errors, 'errors': errors, 'warnings': warnings, 'cards': cards,
            'source_verification': 'author declarations only; converter does not authenticate sources'}


def require_valid(document: Document) -> dict:
    report = validate_document(document)
    if not report['valid']:
        raise ValueError('\n'.join(report['errors']))
    return report
