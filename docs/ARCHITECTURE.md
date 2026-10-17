# Architecture

Verbatim-MD is an independently authored Python package. Parsing produces frozen dataclasses. Evidence strings contain no presentation markup; half-open Unicode code-point spans describe presentation. The validator is shared by Markdown and programmatic entry points. The renderer creates ordinary macro-free DOCX with genuine paragraph and character styles.

`api.export_document` validates, renders to a temporary sibling file, extracts every card, compares it against the immutable input, and publishes atomically only after success. Existing destinations require explicit overwrite. This is internal preservation, never source authentication.

The passive JSON export manifest records card text, hashes, paragraph positions, and provenance declarations. Inspection compares the complete paragraph sequence and each quotation. A manifest is neither a signature nor independent evidence of source truth: somebody who changes both it and the document can defeat the comparison. Keep original Markdown and externally reviewed hashes under version control.

Formatting endpoints are swept once per card and queried by binary search for
each paragraph; appending paragraphs uses an explicit counter instead of
rebuilding the entire paragraph proxy list. The shared validator caps canonical
text and metadata at 10 MiB, formatting at 10,000 spans per card or citation, and
output at 100,000 paragraphs.

The parser and inspector impose size limits, reject unsafe YAML and XML constructs, and never fetch URLs. Runtime conversion works offline. Inspection of external DOCX files is passive and does not execute macros. Template input, when supported, contributes style definitions only.

## Modules

- `schema`: immutable document/source/card/span contracts.
- `parser`: strict syntax, YAML and exact literal text.
- `validator`: semantic and programmatic validation.
- `evidence`: SHA-256, bounded ZIP/XML inspection, export manifests.
- `config`: constrained formatting profiles.
- `styles`, `renderer`: Word style definitions and run segmentation.
- `api`, `cli`: validated conversion, inspection and batch workflows.
- `compatibility`: structural report with explicit interactive-test status.

## Scope

The converter does not cut, paraphrase, authenticate or retrieve evidence. It does not ship Verbatim code, templates or macros. It cannot prove macro compatibility without interactive Word plus Verbatim testing. See the compatibility matrix.
