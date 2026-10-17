from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import pytest

from verbatim_md import build, parse_file, verify_against_document
from verbatim_md.evidence import inspect_docx


def test_even_entity_free_dtd_is_rejected(tmp_path):
    source = Path(__file__).resolve().parents[2] / 'examples/single-card.md'
    output = tmp_path / 'dtd.docx'
    build(source, output)
    with ZipFile(output) as archive:
        parts = {name: archive.read(name) for name in archive.namelist()}
    xml = parts['word/document.xml']
    end = xml.index(b'?>') + 2
    parts['word/document.xml'] = xml[:end] + b'<!DOCTYPE document>' + xml[end:]
    with ZipFile(output, 'w', ZIP_DEFLATED) as archive:
        for name, data in parts.items():
            archive.writestr(name, data)
    with pytest.raises(ValueError):
        inspect_docx(output)
    with pytest.raises(ValueError):
        verify_against_document(parse_file(source), output)
