"""Public local-first conversion API with validated, atomic output publication."""
from __future__ import annotations

import os
from dataclasses import asdict
from pathlib import Path
from tempfile import NamedTemporaryFile

from .config import Profile, load_profile
from .evidence import inspect_docx
from .parser import parse_file, parse_markdown
from .schema import Document
from .validator import require_valid, validate_document


def validate_file(path: str | Path) -> dict:
    return validate_document(parse_file(path))


def inspect_file(path: str | Path) -> dict:
    path = Path(path)
    if path.suffix.lower() == '.docx':
        return inspect_docx(path)
    document = parse_file(path)
    return {'kind': 'markdown', **validate_document(document), 'document': asdict(document)}


def export_document(document: Document, output_path: str | Path,
                    profile: Profile | str | Path | None = None, overwrite: bool = False,
                    template: str | Path | None = None, strict: bool = False) -> dict:
    from .renderer import render_document
    report = require_valid(document)
    if strict and report['warnings']:
        raise ValueError('Strict validation failed: ' + '; '.join(report['warnings']))
    output = Path(output_path)
    if output.suffix.lower() != '.docx':
        raise ValueError('Output must have a .docx extension')
    if output.exists() and not overwrite:
        raise ValueError(f'Output exists: {output}; use overwrite=True or --force')
    resolved = profile if isinstance(profile, Profile) else load_profile(profile)
    output.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(suffix='.docx', dir=output.parent, delete=False) as stream:
        temporary = Path(stream.name)
    try:
        render_document(document, temporary, resolved, template=template)
        integrity = inspect_docx(temporary)
        if not integrity['internally_preserved']:
            raise ValueError(f'Export integrity check failed: {integrity["errors"]}')
        # Compare against immutable input too: a self-consistent manifest alone is insufficient.
        from .schema import Card
        expected = [(b.id, b.text) for b in document.blocks if isinstance(b, Card)]
        if [(c['id'], c['text']) for c in integrity['cards']] != expected:
            raise ValueError('Export changed, omitted, reordered or duplicated evidence')
        if overwrite:
            os.replace(temporary, output)
        else:
            os.link(temporary, output)  # Atomic no-clobber publication, including races.
            temporary.unlink()
        return {'output': str(output), 'validation': report, 'integrity': integrity}
    finally:
        temporary.unlink(missing_ok=True)


def build(input_path: str | Path, output_path: str | Path,
          profile: Profile | str | Path | None = None, overwrite: bool = False,
          template: str | Path | None = None, strict: bool = False) -> dict:
    if Path(input_path).resolve() == Path(output_path).resolve():
        raise ValueError('Input and output paths must differ')
    document = parse_file(input_path)
    return export_document(document, output_path, profile, overwrite, template, strict)


__all__ = ['verify_against_document', 'build', 'export_document', 'validate_file', 'inspect_file', 'parse_markdown', 'parse_file']


def verify_against_document(document: Document, docx_path: str | Path) -> dict:
    """Compare a Word-edited DOCX to trusted input even if Word removed its manifest.

    Verifies text and order only. Source authenticity and formatting are separate checks.
    """
    from .evidence import NS, paragraph_texts, read_package, text_hash
    from .schema import Analytic, Card, Heading
    from defusedxml import ElementTree as ET
    require_valid(document)
    parts = read_package(docx_path)
    try:
        actual = paragraph_texts(parts)
        body = ET.fromstring(parts['word/document.xml'], forbid_dtd=True).find('w:body', NS)
    except (KeyError, ET.ParseError) as exc:
        raise ValueError(f'Invalid DOCX document: {exc}') from exc
    expected: list[str] = []
    cards = []
    sources = {s.id: s for s in document.sources}
    for block in document.blocks:
        if isinstance(block, Heading):
            expected.append(block.text)
        elif isinstance(block, Analytic):
            expected.extend(block.text.split('\n'))
        elif isinstance(block, Card):
            expected.append(sources[block.source_id].citation)
            start = len(expected)
            lines = block.text.split('\n')
            expected.extend(lines)
            extracted = '\n'.join(actual[start:start + len(lines)])
            cards.append({'id': block.id, 'internally_preserved': extracted == block.text,
                          'sha256': text_hash(extracted), 'text': extracted})
    unsupported = body is None or any(n.tag not in (f"{{{NS['w']}}}p", f"{{{NS['w']}}}sectPr") for n in body)
    return {'internally_preserved': actual == expected and not unsupported,
            'comparison_basis': 'supplied canonical Document, not embedded manifest',
            'cards': cards, 'errors': ([] if actual == expected else ['Paragraph text or order differs from canonical input'])
            + (['Unsupported body content'] if unsupported else []),
            'source_verification': 'not independently checked', 'formatting_verified': False}
