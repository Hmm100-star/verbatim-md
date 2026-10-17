---
name: author-debate-markdown
description: Author or repair a Verbatim-MD LD case, block file, original analytic, or evidence-card document using the strict version 1 schema.
---

# Author debate Markdown

Trigger when asked to write a Verbatim-MD document, structure LD arguments, or
repair its hierarchy and metadata. Read `docs/MARKDOWN_SPEC.md` before authoring.

## Procedure

1. Identify the side, resolution, audience, argument structure and available
   evidence. Distinguish original analytical claims from externally sourced text.
2. Create YAML frontmatter `version: 1`, `title`, and `sources`. Use stable IDs
   beginning with an ASCII letter. Record exact citation strings, source URLs and
   truthful provenance. Never invent an author, title, date, URL or quotation.
   Add explicit `citation_spans` with `kind: cite` around the author/date; the
   converter cannot infer that boundary safely. For the tutorial citation
   `Verbatim-MD contributors 2026`, the author/date range is `[0,29)`.
3. Use `#` Pocket, `##` Hat, `###` Block and `####` Tag without skipping levels.
   Every evidence card must immediately follow its own Tag.
4. Write `:::analytic` blocks for original reasoning. Put quotations only inside
   `:::card` literal ` ```text ` fences. Include `id` and `source` metadata. The
   line break immediately before the closing fence is structural.
5. Add independent `highlight`, `underline`, `emphasis`, or `small` spans using
   Python Unicode code-point `[start,end)` ranges. Spans may cross. Never insert
   inline formatting tags into an existing quotation as markup. `emphasis` is
   bold plus underline. `shrink_unread` protects underlined/emphasized ranges,
   not merely highlighted ranges; explicit `small` always uses the small size.
6. Run `verbatim-md validate file.md --json` and inspect the parsed text with
   `verbatim-md inspect file.md --json`. Check every card against supplied evidence.
7. If a source has not been checked, keep `verification: unverified`. Strict mode
   intentionally fails unverified warnings. Do not upgrade status merely because
   a DOCX export passes text-preservation checks.

## Permitted operations and errors

You may author analytics, structure headings, transcribe authorized supplied
quotations exactly, and change metadata or presentation ranges. Do not paraphrase
quoted text, fabricate evidence, invent verification, or silently remove omitted
context. Resolve malformed syntax without changing canonical evidence. If the
source wording is uncertain, stop that card and request/locate the original
source; mark it unverified and explain the unresolved issue.

## Expected output

A UTF-8/LF `.md` file that passes normal validation, plus its validation report
and explicit source-verification status. Any unresolved sourcing issue must be
reported. Conversion and macro compatibility are separate steps; use the
`export-verbatim` skill for them.
