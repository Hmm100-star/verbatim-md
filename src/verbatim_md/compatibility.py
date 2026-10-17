"""Honest structural compatibility reporting; never implies macro certification."""
from pathlib import Path

from .evidence import inspect_docx

REQUIRED_STYLES = ('Heading1', 'Heading2', 'Heading3', 'Heading4', 'Normal',
                   'Style13ptBold', 'StyleUnderline', 'Emphasis')


def compatibility_report(path: str | Path) -> dict:
    inspection = inspect_docx(path)
    missing = sorted(set(REQUIRED_STYLES) - set(inspection['style_ids']))
    return {'structural_styles_present': not missing, 'missing_styles': missing,
            'internally_preserved': inspection['internally_preserved'],
            'word_open_save_reopen': 'unverified',
            'verbatim_navigation': 'unverified', 'verbatim_macros': 'unverified',
            'scope': 'Structural DOCX tests only; see docs/COMPATIBILITY.md'}
