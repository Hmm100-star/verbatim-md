"""Independent OSS/security audit regression tests."""
import json
from zipfile import ZipFile

import pytest

from verbatim_md.api import build
from verbatim_md.cli import main
from verbatim_md.config import load_profile
from verbatim_md.evidence import MANIFEST, inspect_docx
from verbatim_md.renderer import render_document
from verbatim_md.schema import Card, Document, Heading, Source

MARKDOWN = '''---
version: 1
title: Audit
sources:
  - id: s
    citation: Original audit sample
---
# Pocket
## Hat
### Block
#### Tag
:::card
id: card
source: s
```text
Original audit text.
```
:::
'''


def document():
    return Document('Audit', (Source('s', 'Original audit sample'),),
                    tuple(Heading(n, f'Level {n}') for n in range(1, 5)) +
                    (Card('card', 's', 'Original audit text.'),))


def rewrite(path, updates):
    with ZipFile(path) as archive:
        parts = {n: archive.read(n) for n in archive.namelist()}
    parts.update(updates)
    with ZipFile(path, 'w') as archive:
        for name, data in parts.items():
            archive.writestr(name, data)


@pytest.mark.parametrize('contents', [b'not a zip', b'PK\x03\x04truncated'])
def test_cli_bad_zip_is_json_error(tmp_path, capsys, contents):
    path = tmp_path / 'bad.docx'
    path.write_bytes(contents)
    assert main(['inspect', str(path), '--json']) == 2
    report = json.loads(capsys.readouterr().out)
    assert report['ok'] is False and report['error']


def test_cli_missing_parts_is_json_error(tmp_path, capsys):
    path = tmp_path / 'missing.docx'
    with ZipFile(path, 'w') as archive:
        archive.writestr('nothing', b'')
    assert main(['inspect', str(path), '--json']) == 2
    assert json.loads(capsys.readouterr().out)['ok'] is False


def test_cli_malformed_xml_is_json_error(tmp_path, capsys):
    path = render_document(document(), tmp_path / 'bad.docx')
    rewrite(path, {'word/document.xml': b'<broken'})
    assert main(['inspect', str(path), '--json']) == 2
    assert json.loads(capsys.readouterr().out)['ok'] is False


@pytest.mark.parametrize('manifest', [[], {}, {'version': 1, 'cards': [], 'paragraphs': 'wrong'},
                                     {'version': 1, 'cards': [None], 'paragraphs': []}])
def test_bad_manifest_raises_domain_error(tmp_path, manifest):
    path = render_document(document(), tmp_path / 'bad.docx')
    rewrite(path, {MANIFEST: json.dumps(manifest).encode()})
    with pytest.raises(ValueError):
        inspect_docx(path)


@pytest.mark.parametrize('value', ['[]', '{}', 'null', 'false', '23'])
def test_bad_highlight_profile_is_domain_error(tmp_path, value):
    path = tmp_path / 'profile.yaml'
    path.write_text(f'highlight_color: {value}\n')
    with pytest.raises(ValueError):
        load_profile(path)


def test_api_strict_does_not_publish_unverified_evidence(tmp_path):
    path = tmp_path / 'source.md'
    path.write_text(MARKDOWN)
    output = tmp_path / 'out.docx'
    with pytest.raises(ValueError, match='(?i)(strict|warning|verified)'):
        build(path, output, strict=True)
    assert not output.exists()


def test_batch_rejects_destination_subdirectory_symlink(tmp_path, capsys):
    source = tmp_path / 'cases'
    (source / 'nested').mkdir(parents=True)
    (source / 'nested' / 'case.md').write_text(MARKDOWN)
    output = tmp_path / 'dist'
    output.mkdir()
    escaped = tmp_path / 'outside'
    escaped.mkdir()
    try:
        (output / 'nested').symlink_to(escaped, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip('OS does not permit directory symlinks')
    assert main(['build-all', str(source), '--out', str(output), '--json']) != 0
    assert not (escaped / 'case.docx').exists()
    assert json.loads(capsys.readouterr().out)


def test_template_macro_parts_rejected_without_output(tmp_path):
    template = render_document(document(), tmp_path / 'template.docx')
    rewrite(template, {'word/vbaProject.bin': b'inert marker'})
    path = tmp_path / 'source.md'
    path.write_text(MARKDOWN)
    out = tmp_path / 'output.docx'
    with pytest.raises(ValueError, match='macro'):
        build(path, out, template=template)
    assert not out.exists()


def test_added_table_cannot_claim_full_preservation(tmp_path):
    path = render_document(document(), tmp_path / 'table.docx')
    with ZipFile(path) as archive:
        xml = archive.read('word/document.xml')
    table = (b'<w:tbl><w:tr><w:tc><w:p><w:r><w:t>'
             b'Inserted duplicate evidence'
             b'</w:t></w:r></w:p></w:tc></w:tr></w:tbl>')
    rewrite(path, {'word/document.xml': xml.replace(b'</w:body>', table + b'</w:body>')})
    report = inspect_docx(path)
    assert report['internally_preserved'] is not True


def test_template_wrong_known_style_name_is_domain_error(tmp_path):
    from verbatim_md.schema import Span
    doc = document()
    doc = Document(doc.title,
                   (Source('s', 'Original audit sample', citation_spans=(Span(0, 8, 'cite'),)),),
                   doc.blocks)
    template = render_document(doc, tmp_path / 'template.docx')
    with ZipFile(template) as archive:
        styles = archive.read('word/styles.xml')
    styles = styles.replace(b'w:val="Style 13 pt Bold"', b'w:val="Mismatched name"')
    rewrite(template, {'word/styles.xml': styles})
    with pytest.raises(ValueError):
        render_document(doc, tmp_path / 'output.docx', template=template)
