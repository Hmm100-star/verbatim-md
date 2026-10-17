---
name: cut-and-verify-evidence
description: Locate original sources, transcribe and check debate evidence, preserve contextual fidelity, and record provenance for Verbatim-MD cards.
---

# Cut and verify evidence

Trigger when asked to find, cut, verify, recut, highlight or audit evidence. Read
`docs/EVIDENCE_INTEGRITY.md` and `docs/MARKDOWN_SPEC.md` first. This converter cannot
authenticate a source for you.

## Procedure

1. Locate a credible original publication using authorized search/browsing tools.
   Prefer the original publisher and inspect the full relevant passage, not a
   search snippet or unsourced secondary card. Follow applicable quotation and
   redistribution limits; source availability does not imply redistribution rights.
2. Record author, publication date, title, publisher, stable URL and access context
   in the exact citation string/URL. Mark author/date using `citation_spans` and
   the `cite` character style. If information is absent, report it as absent
   rather than guessing. Keep private full-text source material outside this repo.
3. Select a contiguous passage that supports the intended claim in context. Check
   qualifiers, negation, definitions, counterarguments and surrounding discussion.
   Avoid ellipses and synthesized fragments that require changing source wording.
4. Transcribe the authorized passage exactly into the card's literal text block.
   Preserve punctuation, capitalization and Unicode. If PDF/OCR extraction is
   unreliable, compare visually against the original. Never silently fix OCR,
   grammar or an author's spelling; resolve uncertainty before approval.
5. Verify character-for-character against the publication. Review strategic
   highlighting for misleading omissions. Highlight the reading text and optionally
   underline context using offset spans only. Shrinking must not delete text.
   With `shrink_unread: true`, non-underlined context shrinks even if highlighted;
   emphasis includes underline, and explicit `small` overrides the normal size.
6. Only after the actual check, set `verification: source_verified`, `url`,
   `verified_by`, and a quoted `verified_at` date. This records the reviewer's
   declaration; do not claim the tool independently verified it.
7. Compute SHA-256 over the exact canonical string's UTF-8 encoding, pin it in
   card metadata, then run `verbatim-md validate file.md --json`. Check the parsed
   quotation and spans with `inspect file.md --json` before exporting.

## Permitted operations and errors

You may search, quote within applicable limits, compare original text, document
provenance and adjust formatting spans. Do not fabricate publications, quote an
unopened source as verified, paraphrase a quotation or delete inconvenient context.
If access is blocked, a link is dead, attribution conflicts, or wording cannot be
confirmed, retain `unverified`, report the precise limitation and do not approve
the card as source verified. A mismatched hash requires source review, not an
automatic hash update. Never send or publish evidence to others without authority.

## Expected output

A source record, canonical quotation, stable card ID, truthful verification status,
reviewer/date when checked, precise spans, optional pinned digest and a successful
validation report. Report contextual and licensing uncertainties separately.
