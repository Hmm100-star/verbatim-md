"""Verbatim-MD: evidence-preserving Markdown to DOCX."""
__version__ = '0.1.0'

from .api import verify_against_document, build, export_document, inspect_file, parse_file, parse_markdown, validate_file

__all__ = ['verify_against_document', 'build', 'export_document', 'inspect_file', 'parse_file', 'parse_markdown', 'validate_file']
