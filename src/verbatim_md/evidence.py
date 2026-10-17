"""Evidence hashes and bounded, passive DOCX inspection. No source verification."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from defusedxml import ElementTree as ET

from .schema import Card, Document

NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
MAX_PACKAGE = 100 * 1024 * 1024
MAX_PART = 32 * 1024 * 1024
MANIFEST = 'verbatim/manifest.json'


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def _read_package(path: str | Path) -> dict[str, bytes]:
    with ZipFile(path) as archive:
        entries = archive.infolist()
        if len(entries) > 2048 or sum(e.file_size for e in entries) > MAX_PACKAGE:
            raise ValueError('DOCX package exceeds inspection limits')
        if len({e.filename for e in entries}) != len(entries):
            raise ValueError('DOCX contains duplicate ZIP entries')
        for entry in entries:
            if entry.file_size > MAX_PART:
                raise ValueError(f'DOCX part too large: {entry.filename}')
            if entry.filename.startswith('/') or '..' in Path(entry.filename).parts:
                raise ValueError('Unsafe DOCX part path')
        return {e.filename: archive.read(e) for e in entries}



def read_package(path: str | Path) -> dict[str, bytes]:
    from zipfile import BadZipFile
    try:
        return _read_package(path)
    except (BadZipFile, RuntimeError, NotImplementedError) as exc:
        raise ValueError(f'Invalid or unsupported DOCX ZIP package: {exc}') from exc


def paragraph_texts(parts: dict[str, bytes]) -> list[str]:
    root = ET.fromstring(parts['word/document.xml'], forbid_dtd=True)
    texts = []
    for paragraph in root.findall('w:body/w:p', NS):
        chunks = []
        for node in paragraph.iter():
            if node.tag == f"{{{NS['w']}}}t":
                chunks.append(node.text or '')
            elif node.tag == f"{{{NS['w']}}}tab":
                chunks.append('\t')
            elif node.tag in (f"{{{NS['w']}}}br", f"{{{NS['w']}}}cr"):
                chunks.append('\n')
        texts.append(''.join(chunks))
    return texts


def attach_manifest(path: str | Path, document: Document,
                    card_paragraphs: dict[str, list[int]]) -> None:
    """Record expected text, then normalize ZIP metadata for reproducibility."""
    parts = read_package(path)
    sources = {source.id: source for source in document.sources}
    cards = []
    for block in document.blocks:
        if isinstance(block, Card):
            source = sources[block.source_id]
            cards.append({'id': block.id, 'text': block.text,
                          'sha256': text_hash(block.text),
                          'paragraph_indices': card_paragraphs[block.id],
                          'source_id': source.id, 'citation': source.citation, 'url': source.url,
                          'verification': source.verification,
                          'verified_by': source.verified_by, 'verified_at': source.verified_at})
    manifest = {'version': 1, 'paragraphs': paragraph_texts(parts), 'cards': cards}
    parts[MANIFEST] = json.dumps(manifest, ensure_ascii=False, sort_keys=True).encode('utf-8')
    # Register our passive JSON part in the OPC content type map.
    from xml.etree import ElementTree as StdET
    ct = ET.fromstring(parts['[Content_Types].xml'], forbid_dtd=True)
    namespace = 'http://schemas.openxmlformats.org/package/2006/content-types'
    # Preserve OPC's conventional default namespace; LibreOffice rejects a prefixed Types root.
    StdET.register_namespace('', namespace)
    if not any(n.get('Extension') == 'json' for n in ct):
        StdET.SubElement(ct, f'{{{namespace}}}Default',
                         Extension='json', ContentType='application/json')
    parts['[Content_Types].xml'] = StdET.tostring(ct, encoding='utf-8', xml_declaration=True)
    with ZipFile(path, 'w', compression=ZIP_DEFLATED) as archive:
        for name, data in sorted(parts.items()):
            info = ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o600 << 16
            archive.writestr(info, data)


def _inspect_docx(path: str | Path) -> dict:
    parts = read_package(path)
    actual = paragraph_texts(parts)
    styles = ET.fromstring(parts['word/styles.xml'], forbid_dtd=True)
    style_ids = [n.get(f"{{{NS['w']}}}styleId") for n in styles if n.tag == f"{{{NS['w']}}}style"]
    report: dict = {'kind': 'docx', 'paragraph_count': len(actual), 'style_ids': style_ids,
              'internally_preserved': None, 'cards': [], 'errors': [],
              'source_verification': 'not independently checked',
              'verbatim_macros': 'unverified'}
    if MANIFEST not in parts:
        report['errors'].append('No verbatim-md integrity manifest; preservation cannot be established')
        return report
    manifest = json.loads(parts[MANIFEST])
    if not isinstance(manifest, dict):
        raise ValueError('Integrity manifest must be an object')
    if manifest.get('version') != 1:
        raise ValueError('Unsupported integrity manifest version')
    if (not isinstance(manifest.get('paragraphs'), list)
            or not all(isinstance(t, str) for t in manifest['paragraphs'])
            or not isinstance(manifest.get('cards'), list)):
        raise ValueError('Invalid integrity manifest structure')
    body = ET.fromstring(parts['word/document.xml'], forbid_dtd=True).find('w:body', NS)
    if body is None or any(n.tag not in (f"{{{NS['w']}}}p", f"{{{NS['w']}}}sectPr") for n in body):
        report['errors'].append('Unsupported body content; preservation cannot be established')
    if actual != manifest['paragraphs']:
        report['errors'].append('Document paragraph text or order differs from export manifest')
    seen = set()
    for card in manifest['cards']:
        if (not isinstance(card, dict) or not isinstance(card.get('id'), str)
                or not isinstance(card.get('text'), str) or not isinstance(card.get('sha256'), str)
                or not isinstance(card.get('paragraph_indices'), list)
                or card.get('verification') not in ('unverified', 'source_verified')):
            raise ValueError('Invalid card integrity manifest structure')
        if any(key in card and not isinstance(card[key], str)
               for key in ('source_id', 'citation', 'url', 'verified_by', 'verified_at')):
            raise ValueError('Invalid card provenance metadata')
        indices = card['paragraph_indices']
        if (card['id'] in seen or not indices or any(type(i) is not int or i < 0 or i >= len(actual) for i in indices)
                or indices != list(range(indices[0], indices[-1] + 1))):
            raise ValueError('Invalid card integrity manifest')
        seen.add(card['id'])
        extracted = '\n'.join(actual[i] for i in indices)
        preserved = extracted == card['text'] and text_hash(extracted) == card['sha256']
        if not preserved:
            report['errors'].append(f"Card {card['id']}: quotation differs from export manifest")
        report['cards'].append({'id': card['id'], 'text': extracted,
                                'sha256': text_hash(extracted), 'internally_preserved': preserved,
                                'declared_source_verification': card['verification'],
                                'source_id': card.get('source_id', ''),
                                'citation': card.get('citation', ''), 'url': card.get('url', ''),
                                'verified_by': card.get('verified_by', ''),
                                'verified_at': card.get('verified_at', '')})
    report['internally_preserved'] = not report['errors']
    return report


def inspect_docx(path: str | Path) -> dict:
    """Inspect a bounded passive package; malformed data always produces ValueError."""
    from zipfile import BadZipFile
    from xml.etree.ElementTree import ParseError
    from defusedxml.common import DefusedXmlException
    try:
        return _inspect_docx(path)
    except (BadZipFile, KeyError, TypeError, IndexError, AttributeError,
            ParseError, DefusedXmlException, UnicodeError, RecursionError) as exc:
        raise ValueError(f'Invalid DOCX package or integrity manifest: {exc}') from exc
