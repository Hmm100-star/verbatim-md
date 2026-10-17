# Verbatim-MD

Verbatim-MD converts structured debate Markdown into local, macro-free `.docx`
files with Verbatim-oriented Word styles. It preserves evidence quotations,
validates character-offset formatting, and compares extracted DOCX evidence
against the immutable input before publishing an output file.

**Compatibility scope:** DOCX structure and text integrity are automatically
tested. Microsoft Word and Verbatim interactive macro workflows require the
versioned observations and manual checks in [COMPATIBILITY.md](docs/COMPATIBILITY.md). Passing structural tests
does not establish that every Verbatim macro works. Local Word open/save and
navigation passed; the installed Verbatim Shrink ribbon command failed with error
5852 before dispatch, as recorded in the matrix. This project is independent
of Verbatim and distributes no Verbatim templates, macros, or source code.

## Quick start

Install Python 3.11 or later. From this repository, create an isolated environment:

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell instead: .venv\Scripts\Activate.ps1
python -m pip install .
verbatim-md validate examples/single-card.md
verbatim-md build examples/single-card.md -o single-card.docx
verbatim-md inspect single-card.docx
```

The resulting DOCX uses standard Word structure and needs no macros for generation. Use
Word with a legitimate Verbatim installation for debate macros. Conversion needs
no internet access, API keys, database, or Word installation after dependencies
are installed. Citation URLs are metadata and are never fetched.

The examples contain original tutorial passages, not externally verified evidence
or research suitable for a tournament. Their unverified warnings are intentional.

## Authoring

Use `#` Pocket, `##` Hat, `###` Block, and `####` Tag. Each card immediately follows
a Tag. Source metadata is YAML; quotations are fenced literal text. Formatting
uses independent half-open Unicode character ranges, allowing crossing overlaps:

````markdown
---
version: 1
title: Demonstration
sources:
  - id: tutorial
    citation: "Verbatim-MD contributors 2026, original tutorial passage"
    citation_spans:
      - {start: 0, end: 29, kind: cite}
---
# Affirmative
## Framework
### Education
#### Information supports choice
:::card
id: choice
source: tutorial
spans:
  - {start: 0, end: 9, kind: highlight}
  - {start: 4, end: 14, kind: underline}
```text
Education lets people make informed choices.
```
:::
````

Run `python scripts/demo.py --out artifacts/demo` for an end-to-end report.

Read [the full Markdown specification](docs/MARKDOWN_SPEC.md) before cutting real
cards. Inline `[hl]` tags are literal quotation characters, not formatting markup.
Never change quoted wording to fix an offset or pass validation.

## Commands

```bash
verbatim-md build case.md -o case.docx --profile ld
verbatim-md validate case.md --json
verbatim-md inspect case.md --json
verbatim-md inspect case.docx --json
verbatim-md inspect word-edited.docx --against case.md --json
verbatim-md build-all ./cases --out ./dist --profile profiles/ld.yaml
verbatim-md profiles list
verbatim-md --help
```

Existing outputs are protected; `--force` explicitly permits replacement.
`build-all` recursively processes `.md` files, preserves relative paths, and
reports each file independently. Keep the output directory outside the input tree.
`--strict` on `validate`, `build`, or `build-all` treats warnings (including
unverified sources) as failures. Use `--verbose` before the command for diagnostic
tracebacks. `--json` produces machine-readable reports; normal reports are also
structured JSON for easy inspection. Exit codes: `0` success, `1` failed validation
or batch work, `2` usage, input, configuration or I/O errors.

## Python API

```python
from verbatim_md.api import parse_markdown, export_document, inspect_file

with open("case.md", encoding="utf-8", newline="") as stream:
    document = parse_markdown(stream.read())
report = export_document(document, "case.docx", profile="ld")
assert report["integrity"]["internally_preserved"]
print(inspect_file("case.docx"))
```

The frozen dataclasses in `verbatim_md.schema` also support direct construction.
`export_document` validates them and refuses invalid evidence before rendering.
`build(input_path, output_path, ...)` combines file parsing and export.

## Documentation and agent skills

- [Installation and offline setup](docs/INSTALLATION.md)
- [Architecture](docs/ARCHITECTURE.md) and [format specification](docs/MARKDOWN_SPEC.md)
- [Formatting and profiles](docs/FORMATTING.md)
- [Evidence integrity and verification](docs/EVIDENCE_INTEGRITY.md)
- [Verbatim research](docs/VERBATIM_SPEC.md) and [compatibility matrix](docs/COMPATIBILITY.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md) and [contributing](CONTRIBUTING.md)
- [Author debate Markdown](skills/author-debate-markdown/SKILL.md)
- [Cut and verify evidence](skills/cut-and-verify-evidence/SKILL.md)
- [Export Verbatim](skills/export-verbatim/SKILL.md)

## Development and release

```bash
python -m pip install --require-hashes -r requirements-dev.lock
python -m pip install --no-build-isolation --no-deps -e .
python -m pytest
python -m ruff check src tests
python -m mypy src/verbatim_md
python scripts/reproducible_build.py
python -m twine check dist/*
```

CI exercises supported Python versions and platforms. Release automation builds
artifacts for review; publication is a separate authorized action. See the release
checklist and security/licensing review in `docs/`. Converter code is MIT licensed;
third-party packages retain their own licenses. Keep private evidence repositories
separate and confirm rights before redistributing quotation text.
