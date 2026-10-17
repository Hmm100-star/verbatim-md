import json
from pathlib import Path
from xml.etree import ElementTree as ET

from verbatim_md import build
from verbatim_md.compatibility import compatibility_report
from verbatim_md.evidence import NS, read_package


def test_original_style_contract(tmp_path):
    root = Path(__file__).resolve().parents[2]
    output = tmp_path / 'golden.docx'
    build(root / 'examples/single-card.md', output)
    styles = ET.fromstring(read_package(output)['word/styles.xml'])
    contract = json.loads((root / 'tests/golden/style-contract.json').read_text())
    for identifier, expected in contract.items():
        style = styles.find(f"w:style[@w:styleId='{identifier}']", NS)
        assert style is not None
        assert style.get(f"{{{NS['w']}}}type") == expected['type']
        assert style.find('w:aliases', NS).get(f"{{{NS['w']}}}val") == expected['alias']
    report = compatibility_report(output)
    assert report['structural_styles_present'] and report['internally_preserved']
    assert report['verbatim_macros'] == 'unverified'


def test_reference_template_cannot_remove_semantic_aliases(tmp_path):
    from docx import Document
    reference = tmp_path / 'reference.docx'
    Document().save(reference)
    root = Path(__file__).resolve().parents[2]
    output = tmp_path / 'reference-output.docx'
    build(root / 'examples/single-card.md', output, template=reference)
    styles = ET.fromstring(read_package(output)['word/styles.xml'])
    heading = styles.find("w:style[@w:styleId='Heading1']", NS)
    assert heading.find('w:aliases', NS).get(f"{{{NS['w']}}}val") == 'Pocket'
    assert heading.find('w:pPr/w:outlineLvl', NS).get(f"{{{NS['w']}}}val") == '0'


def test_unused_yaml_anchor_is_rejected():
    import pytest
    from verbatim_md.parser import load_yaml
    with pytest.raises(ValueError, match='anchors'):
        load_yaml('font_name: &unused Arial')
