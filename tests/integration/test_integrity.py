"""Independent export integrity and tampering regressions."""
from copy import deepcopy
from zipfile import ZipFile, ZIP_DEFLATED
from xml.etree import ElementTree as ET

import pytest

from verbatim_md.api import export_document
from verbatim_md.evidence import inspect_docx
from verbatim_md.schema import Card, Document, Heading, Source, Span

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'


def sample(text='  α e\u0301 😀\tquoted & <literal>  \n\nsecond line\n'):
    return Document('Audit', (Source('s', 'Original tutorial, 2026'),),
                    tuple(Heading(i, f'Heading {i}') for i in range(1, 5)) +
                    (Card('card', 's', text, (Span(0, 5, 'highlight'),
                                             Span(2, 10, 'underline'),
                                             Span(4, 12, 'small'))),))


def mutate(path, transform):
    with ZipFile(path) as z:
        parts = {n: z.read(n) for n in z.namelist()}
    root = ET.fromstring(parts['word/document.xml'])
    transform(root.find(W+'body'))
    parts['word/document.xml'] = ET.tostring(root, encoding='utf-8')
    with ZipFile(path, 'w', ZIP_DEFLATED) as z:
        for name, data in parts.items():
            z.writestr(name, data)


def test_unicode_whitespace_round_trip(tmp_path):
    original = sample()
    path = tmp_path/'out.docx'
    report = export_document(original, path)
    assert report['integrity']['cards'][0]['text'] == original.blocks[-1].text
    assert report['integrity']['internally_preserved'] is True
    assert report['integrity']['source_verification'] == 'not independently checked'
    assert inspect_docx(path)['cards'][0]['declared_source_verification'] == 'unverified'


@pytest.mark.parametrize('operation', ['alter', 'remove', 'duplicate', 'reorder'])
def test_detects_text_tampering(tmp_path, operation):
    path = tmp_path/'out.docx'
    export_document(sample(), path)
    def tamper(body):
        paragraphs = body.findall(W+'p')
        if operation == 'alter':
            paragraphs[5].find('.//'+W+'t').text = 'CHANGED'
        elif operation == 'remove':
            body.remove(paragraphs[5])
        elif operation == 'duplicate':
            body.insert(6, deepcopy(paragraphs[5]))
        else:
            body.remove(paragraphs[5])
            body.insert(7, paragraphs[5])
    mutate(path, tamper)
    try:
        result = inspect_docx(path)
    except ValueError:
        return  # Removed paragraph positions may invalidate manifest itself.
    assert result['internally_preserved'] is False
    assert result['errors']


def test_added_evidence_table_is_not_silently_ignored(tmp_path):
    path = tmp_path/'out.docx'
    export_document(sample(), path)
    def tamper(body):
        table = ET.SubElement(body, W+'tbl')
        row = ET.SubElement(table, W+'tr')
        cell = ET.SubElement(row, W+'tc')
        p = ET.SubElement(cell, W+'p')
        r = ET.SubElement(p, W+'r')
        ET.SubElement(r, W+'t').text = sample().blocks[-1].text
    mutate(path, tamper)
    report = inspect_docx(path)
    assert report['internally_preserved'] is False
    assert report['errors']


def test_large_case_exact_text(tmp_path):
    text = 'Evidence 😀\tline\n' * 3000
    report = export_document(sample(text), tmp_path/'large.docx')
    assert report['integrity']['cards'][0]['text'] == text


def test_no_overwrite_and_atomic_failed_export(tmp_path):
    path = tmp_path/'out.docx'
    path.write_bytes(b'untouched')
    with pytest.raises(ValueError, match='exists'):
        export_document(sample(), path)
    assert path.read_bytes() == b'untouched'


def drop_manifest(path):
    with ZipFile(path) as z:
        parts = {n: z.read(n) for n in z.namelist() if n != 'verbatim/manifest.json'}
    with ZipFile(path, 'w', ZIP_DEFLATED) as z:
        for name, data in parts.items():
            z.writestr(name, data)


@pytest.mark.parametrize('remove_manifest', [False, True])
def test_external_canonical_verification_does_not_require_manifest(tmp_path, remove_manifest):
    from verbatim_md.api import verify_against_document
    original = sample()
    path = tmp_path/'out.docx'
    export_document(original, path)
    if remove_manifest:
        drop_manifest(path)
        assert inspect_docx(path)['internally_preserved'] is None
    report = verify_against_document(original, path)
    assert report['internally_preserved'] is True
    assert report['cards'][0]['text'] == original.blocks[-1].text
    assert report['formatting_verified'] is False
    assert report['errors'] == []


@pytest.mark.parametrize('change', ['text', 'table'])
def test_external_verification_after_manifest_loss_detects_tampering(tmp_path, change):
    from verbatim_md.api import verify_against_document
    original = sample()
    path = tmp_path/'out.docx'
    export_document(original, path)
    drop_manifest(path)
    def tamper(body):
        if change == 'text':
            body.findall(W+'p')[5].find('.//'+W+'t').text = 'changed'
        else:
            ET.SubElement(body, W+'tbl')
    mutate(path, tamper)
    report = verify_against_document(original, path)
    assert report['internally_preserved'] is False
    assert report['errors']


def test_external_verification_invalid_zip_is_actionable(tmp_path):
    from verbatim_md.api import verify_against_document
    path = tmp_path/'broken.docx'
    path.write_bytes(b'not a zip')
    with pytest.raises(ValueError):
        verify_against_document(sample(), path)


def test_content_types_uses_default_opc_namespace(tmp_path):
    path = tmp_path/'opc.docx'
    export_document(sample(), path)
    with ZipFile(path) as z:
        content_types = z.read('[Content_Types].xml')
    assert b'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"' in content_types
    assert b'<ns0:Types' not in content_types
    root = ET.fromstring(content_types)
    assert any(n.get('Extension') == 'json' and n.get('ContentType') == 'application/json' for n in root)


def test_manifest_preserves_full_declared_provenance(tmp_path):
    from dataclasses import replace
    original = sample()
    source = replace(original.sources[0], url='https://example.org/tutorial',
                     verification='source_verified', verified_by='Human reviewer',
                     verified_at='2026-10-17')
    original = replace(original, sources=(source,))
    path = tmp_path/'provenance.docx'
    report = export_document(original, path)['integrity']['cards'][0]
    assert report['source_id'] == source.id
    assert report['url'] == source.url
    assert report['citation'] == source.citation
    assert report['verified_by'] == source.verified_by
    assert report['verified_at'] == source.verified_at
    assert report['declared_source_verification'] == 'source_verified'


def test_external_verification_rejects_unsafe_xml_as_domain_error(tmp_path):
    from verbatim_md.api import verify_against_document
    path = tmp_path/'unsafe.docx'
    export_document(sample(), path)
    with ZipFile(path) as z:
        parts = {n: z.read(n) for n in z.namelist()}
    parts['word/document.xml'] = b'<!DOCTYPE x [<!ENTITY xx "unsafe">]><x>&xx;</x>'
    with ZipFile(path, 'w', ZIP_DEFLATED) as z:
        for name, data in parts.items():
            z.writestr(name, data)
    with pytest.raises(ValueError):
        verify_against_document(sample(), path)
