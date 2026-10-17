"""Independently authored Verbatim-compatible Word style definitions."""
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor

from .config import Profile

HEADING_ALIASES = ('Pocket', 'Hat', 'Block', 'Tag')
CITE_STYLE = 'Style13ptBold'
UNDERLINE_STYLE = 'StyleUnderline'


def _alias(style, alias: str) -> None:
    element = style.element.find(qn('w:aliases'))
    if element is None:
        element = OxmlElement('w:aliases')
        style.element.append(element)
    element.set(qn('w:val'), alias)


def setup_styles(document, profile: Profile) -> None:
    normal = document.styles['Normal']
    normal.font.name = profile.font_name
    normal.font.size = Pt(profile.font_size)
    normal.font.color.rgb = RGBColor(0, 0, 0)
    normal.paragraph_format.space_after = Pt(0)
    _alias(normal, 'Normal/Card')
    for level, (alias, size) in enumerate(zip(HEADING_ALIASES, (26, 22, 16, 13)), 1):
        style = document.styles[f'Heading {level}']
        _alias(style, alias)
        style.font.name = profile.font_name
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.italic = False
        style.font.color.rgb = RGBColor(0, 0, 0)
        style.paragraph_format.keep_with_next = True
        style.paragraph_format.space_before = Pt(8)
        style.paragraph_format.space_after = Pt(2)
        style.next_paragraph_style = normal
    for name, identifier, alias, char_size in (
        ('Style 13 pt Bold', CITE_STYLE, 'Cite', 13),
        ('Style Underline', UNDERLINE_STYLE, 'Underline', profile.font_size),
        ('Emphasis', 'Emphasis', 'Emphasis', profile.font_size),
    ):
        style = document.styles[name] if name in document.styles else document.styles.add_style(name, WD_STYLE_TYPE.CHARACTER)
        style.element.set(qn('w:styleId'), identifier)
        style.base_style = document.styles['Default Paragraph Font']
        _alias(style, alias)
        style.font.name = profile.font_name
        style.font.size = Pt(char_size)
        style.font.italic = False
        style.font.bold = identifier != UNDERLINE_STYLE
        style.font.underline = identifier != CITE_STYLE

    # Explicit fonts must take precedence over the stock document theme.
    for style in [normal] + [document.styles[f'Heading {n}'] for n in range(1, 5)] + [
            document.styles['Style 13 pt Bold'], document.styles['Style Underline'],
            document.styles['Emphasis']]:
        fonts = style.element.get_or_add_rPr().find(qn('w:rFonts'))
        if fonts is not None:
            for attribute in list(fonts.attrib):
                if attribute.endswith('Theme'):
                    del fonts.attrib[attribute]
            for attribute in ('ascii', 'hAnsi', 'eastAsia', 'cs'):
                fonts.set(qn('w:' + attribute), profile.font_name)


def ensure_style_contract(document) -> None:
    """Reference appearance must not replace required semantic style identities."""
    for level, alias in enumerate(HEADING_ALIASES, 1):
        style = document.styles[f'Heading {level}']
        _alias(style, alias)
        properties = style.element.get_or_add_pPr()
        outline = properties.find(qn('w:outlineLvl'))
        if outline is None:
            outline = OxmlElement('w:outlineLvl')
            properties.append(outline)
        outline.set(qn('w:val'), str(level - 1))
    for name, alias in [('Style 13 pt Bold', 'Cite'), ('Style Underline', 'Underline'),
                        ('Emphasis', 'Emphasis')]:
        _alias(document.styles[name], alias)
