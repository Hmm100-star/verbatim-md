# Verbatim-MD format version 1

The format is intentionally a strict Markdown subset. Evidence is literal text,
never inline Markdown. Unsupported text outside blocks is an error. Files must
be UTF-8 with LF line endings and at most 10 MiB. CRLF is rejected with an explicit
error, rather than silently changing canonical quotation text.

## Complete example

````markdown
---
version: 1
title: Example case
sources:
  - id: example
    citation: "Example Author 2026, original demonstration text"
    verification: unverified
    citation_spans:
      - {start: 0, end: 19, kind: cite}
---
# Affirmative
## Value
### Contention
#### Education supports agency
:::card
id: agency-card
source: example
spans:
  - {start: 0, end: 9, kind: highlight}
  - {start: 4, end: 14, kind: underline}
```text
Education lets people make informed choices.
```
:::
:::analytic
```text
This is an original analytical claim, not quoted evidence.
```
:::
````

## Metadata

Frontmatter starts on the first line with `---` and ends with a separate `---`.
Required keys are `version` (integer `1`), `title` (nonempty string) and `sources`
(a list, which may be empty when no cards are present). All unknown and duplicate
keys are rejected. YAML anchors, aliases and custom tags are rejected. YAML nesting is
limited to 64 levels. Quote dates and numeric-looking identifiers to keep their
string type. YAML comments are allowed in metadata only.

A source requires `id` and `citation`. Optional keys are `url`, `verification`,
`verified_by`, `verified_at`, and `citation_spans`. IDs use 1–64 ASCII letters,
digits, `_` or `-`, beginning with a letter. Source IDs and card IDs
are unique within their own namespaces. Citations are literal strings; the
converter does not fetch or infer bibliography data from URLs.

`verification` is `unverified` by default. `source_verified` requires nonempty
`url`, `verified_by` and `verified_at` strings. This is a user's provenance assertion,
not authentication or an automated source check. For example:

```yaml
verification: source_verified
url: "https://example.org/original-publication"
verified_by: "Human reviewer name"
verified_at: "2026-10-17"
```

## Hierarchy and analytics

One to four `#` characters followed by a space map respectively to Pocket, Hat,
Block and Tag. The first heading must be level 1; levels cannot skip forward
(e.g. level 1 directly to level 3). Returning to a shallower level is allowed.
Heading text is literal, with no inline Markdown parsing. Every card requires an immediately preceding level 4 Tag. Analytics may appear
before headings, but reset the card tag association.

An analytic is `:::analytic`, immediately followed by a ` ```text ` fence, its
literal body, a closing ` ``` ` fence and `:::`. It has no metadata and is never
classified as evidence. Blank lines between top-level blocks are ignored.

## Evidence cards and exact text

A card starts with `:::card`, followed by YAML metadata, then an exact-line
` ```text ` fence. It ends with an exact-line ` ``` ` followed immediately by
`:::`. Required metadata: `id` and `source`. Optional: `spans` and `sha256`.
`source` must refer to a defined source ID. Empty or whitespace-only cards are
rejected. `sha256`, if supplied, is a quoted 64-character lowercase hexadecimal
SHA-256 of the canonical quotation encoded as UTF-8. Export validation checks
this digest.

The opening fence's line break and the final line break immediately before the
closing fence are syntax, not quotation text. Every character between those
boundaries is preserved: spaces, tabs, Unicode, punctuation, internal blank lines
and trailing spaces. To preserve a trailing newline, add a blank body line before
the closing fence; to preserve two trailing newlines, add two. A newline between
literal body lines becomes canonical `\n`.

There are no escapes or substitutions inside the literal body. `[hl]`, backslashes,
asterisks, HTML, YAML, and `:::` are ordinary quotation characters. The one reserved
body line is exactly three backticks (` ``` ` without surrounding spaces): this
version cannot represent a quotation containing that standalone line. Reject or
use the programmatic API; never delete that line from evidence to fit the syntax.
XML-invalid controls and Unicode surrogates are rejected rather than removed.

## Formatting spans

`spans` and `citation_spans` are lists of mappings with exactly `start`, `end`,
`kind`. Offsets are zero-based, half-open Python Unicode code-point indices into
canonical text (`text[start:end]`), not UTF-8 bytes or UTF-16 units. Newlines and
tabs each count as one code point. Combining marks count separately; no Unicode
normalization occurs. Each range must satisfy `0 <= start < end <= len(text)`.
Booleans, fractional offsets, duplicate spans and unknown kinds are errors.
Each card or citation supports at most 10,000 spans. The shared validator also
limits total canonical text and source metadata to 10 MiB and generated content
to 100,000 paragraphs, including headings and citations. These bounds apply to
programmatically constructed documents as well as parsed Markdown; oversized
input is rejected without changing any quotation text.

Evidence kinds: `highlight`, `underline`, `emphasis`, `small`. Citation spans also
allow `cite`, which applies Verbatim's citation character style. Mark the author/date
with this span; absent Cite spans produce a warning because Verbatim uses the
style for citation detection. Spans may cross,
nest and cross newlines; they are independent ranges, so overlap is unambiguous.
Formatting changes presentation only. `[hl]...[/hl]` and similar inline markers
are deliberately not supported as markup, because they risk corrupting quotation
text and cannot represent crossing spans safely. See [FORMATTING.md](FORMATTING.md)
for effective font-size behavior.

## Errors and API

`parse_markdown(text)` and `parse_file(path)` return immutable schema dataclasses.
`ParseError` is a `ValueError` carrying `.line` and an actionable message prefixed
with a one-based source line. Nested YAML schema errors identify the metadata
block's start; YAML syntax and duplicate-key errors identify their exact line.
Parsing never rewrites malformed input. Parsing also performs semantic and hash checks; callers constructing schema objects directly must use
the validation API before rendering.
