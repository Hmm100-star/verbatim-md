# Verbatim interoperability specification

Research date: 2026-10-17. Target: Verbatim 6 desktop document conventions.
This project independently generates ordinary macro-free DOCX. It does not bundle
Verbatim, its GPL source, VBA projects, ribbon assets, or templates.

## Evidence levels

**Documented** means the official manual states the behavior. **Inspected** means
an official reference package's XML was read. **Inferred** means the converter
is designed to support the behavior but no Word macro execution established it.
**Experimentally verified** is reserved for tests actually executed against the
converter or Word; structural tests never imply macro compatibility.

## Required Word structures

| Debate role | Word style ID | Type | Name and alias | Evidence |
| --- | --- | --- | --- | --- |
| Pocket | Heading1 | paragraph | heading 1; Pocket | documented and inspected |
| Hat | Heading2 | paragraph | heading 2; Hat | documented and inspected |
| Block | Heading3 | paragraph | heading 3; Block | documented and inspected |
| Tag | Heading4 | paragraph | heading 4; Tag | documented and inspected |
| Evidence and citation paragraph | Normal | paragraph | Normal; Normal/Card | inspected |
| Citation surname/date | Style13ptBold | character | Style 13 pt Bold; Cite | inspected |
| Underlined text | StyleUnderline | character | Style Underline; Underline | inspected |
| Emphasized text | Emphasis | character | Emphasis | inspected |

Heading outline levels are 0, 1, 2, and 3 respectively. Creating unrelated custom
paragraph styles named Pocket/Tag is insufficient: built-in headings drive
organization. A citation is not an entire paragraph styled Cite. Only its
explicit surname/date ranges receive the Cite character style. Keep the full
citation in one paragraph directly below its Tag and before its evidence.

The inspected release uses heading sizes 26/22/16/13 pt; Cite is bold 13 pt;
Underline and Emphasis are 11 pt and underlined. User-configurable appearance is
not a normative interoperability requirement. The converter authors its own
style definitions and configurable typography instead of copying upstream XML.
Word allows only one character style per run: overlapping highlight, underline,
emphasis, and shrink use a character style plus explicit run properties.

## Formatting and macro interactions

The official manual documents: F8 applies Cite to surname/date; F9 toggles
underline (optional bold); F10 applies configurable emphasis; F11 toggles Word
highlight. Highlight uses `w:highlight`, not shading. Avoid light-gray highlight,
which the manual identifies as vulnerable to a Word save issue. Shrink operates
on **non-underlined** text, not simply non-highlighted text, and cycles font sizes.
The converter can offer a deterministic profile policy but must label any
highlight-based policy as its own behavior, not identical to Verbatim Shrink.

Condense intentionally changes whitespace and can replace paragraph breaks with
pilcrows. Clear Formatting resets style/direct formatting, except highlighting.
Update Styles copies the user's installed template appearance. These operations
may change text or override formatting: re-inspect after using them. Converter
export never condenses, inserts omission notes, or changes quotation wording.

A card is conventionally Tag, one citation paragraph, evidence body. Multiline
body is preserved; the manual recommends a simple three-paragraph pattern for
best automatic citation detection. Multiple evidence paragraphs are valid DOCX,
but macro processing of unusual layouts remains unverified. Analytic paragraphs
are converter content, not a built-in Verbatim Analytic style: the manual states
that analytics styles are custom and can be converted to Tags.

Sending selections/cards/blocks to speeches is documented as heading-sensitive.
Navigation, copying, and sending are inferred to work from the correct headings
and styles, but require actual Word/Verbatim testing. Never infer successful VBA
execution from ZIP/XML inspection or generic viewer rendering.

## Environment scope

The official requirements target desktop Word 2019+/Microsoft 365 with VBA on
Windows or macOS. Word 2016 and earlier are not thoroughly tested upstream.
Word Online, iPad, Android, Mac Word 2008/2011, and listed restricted Office
editions do not support Verbatim. Consult current upstream requirements for
installation-specific constraints; their README and current manual differ on
some Office edition wording. DOCX generation itself requires neither Word nor
Verbatim and is offline after installation.

Verbatim's installed Debate.dotm and DebateStartup.dotm (plus Verbatim.scpt on
Mac) supply functionality. Merely embedding style names in a DOCX does not
install/enable the ribbon or macros. A user must open/import the result in their
legitimate Verbatim installation. The converter must not enable macros or attach
remote templates automatically.

## Research provenance and licensing boundary

Inspected reference: official repository commit
`8cccf83b16cb84d2311796907cf0aa99e3212be1`,
`desktop/release/6.0.0/Debate.dotm`, read-only download to a temporary directory.
Only factual interoperability observations are recorded here. The package and
upstream source were not copied into this repository. Upstream is GPL-3.0;
redistributing its code/assets in an MIT package requires separate legal review.
Related projects include `shreerammodi/debate-scripts` (GPL-3.0 macro extensions)
and `ant981228/cardmirror` (separate editor). Neither is a dependency or source
for converter implementation; this project does not claim their compatibility.

## Primary references

- [Official organization guide](https://docs.paperlessdebate.com/verbatim/cutting-evidence/organization)
- [Official formatting guide](https://docs.paperlessdebate.com/verbatim/cutting-evidence/formatting)
- [Official citation guide](https://docs.paperlessdebate.com/verbatim/cutting-evidence/citations)
- [Official requirements](https://docs.paperlessdebate.com/verbatim/getting-started/requirements)
- [Official installation guide](https://docs.paperlessdebate.com/verbatim/getting-started/installation)
- [Official speech workflow](https://docs.paperlessdebate.com/verbatim/debating-paperless/paperless)
- [Official source and license](https://github.com/ashtarcommunications/verbatim)
- [Pinned reference template](https://github.com/ashtarcommunications/verbatim/blob/8cccf83b16cb84d2311796907cf0aa99e3212be1/desktop/release/6.0.0/Debate.dotm)
