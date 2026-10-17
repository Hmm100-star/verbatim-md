# Evidence integrity

Canonical evidence is a frozen Unicode string in each `Card`. Formatting spans
never modify that string. Offsets count code points, not graphemes, bytes or UTF-16
units. There is no trimming, typographic replacement, Unicode normalization,
Markdown decoding, summarization, paraphrasing, source fetching or hidden editing.
Files with unsupported newline conventions fail explicitly.

Three different claims must remain distinct:

- **Source verified:** the author declares a check against an original publication
  and records its URL, reviewer and date. This is provenance, not a claim that this
  converter authenticated the publication or the reviewer.
- **Internally preserved:** DOCX text extracted after rendering exactly equals the
  canonical input quotation, with the same order, characters and SHA-256 hash.
- **Unverified:** no source-verification declaration exists. Internally preserving
  an unverified quotation never upgrades it to source verified.

Optional card `sha256` pins a previously reviewed quotation. It must equal
`hashlib.sha256(text.encode('utf-8')).hexdigest()`. A mismatch stops conversion;
review against the original source before deliberately changing a stored hash.
The hash establishes change detection, not authorship, accuracy or authenticity.

Exports contain a passive `verbatim/manifest.json` package part with canonical
quotation text, hashes, source-verification declarations and paragraph locations.
Export verification compares extracted text both to that manifest and directly
to the in-memory input. It detects internal omissions, duplication, reordered
cards and character changes before publishing a file. Output is written to a
same-directory temporary file and atomically published after checks pass.

`inspect case.docx` compares current DOCX text and order to the embedded manifest.
Its manifest is not signed: an attacker changing both the text and manifest can
forge consistency. Retain the reviewed Markdown and any external source records.
Inspection is a tamper/change check for this export workflow, not a digital
signature or independent source audit. It does not authenticate an arbitrary DOCX.

Word may remove custom package parts or change paragraph structure during
save/reopen, copy/paste and macro operations. The manual compatibility tests must
check those workflows. If a manifest is missing, preservation is unknown rather
than successful. Compare against the original Markdown using the extraction API
or a reviewed export; do not simply recreate a manifest from edited Word text.

After Word editing, run `verbatim-md inspect edited.docx --against case.md --json`.
This compares the complete text/order and each quotation against the supplied
canonical Markdown without trusting an embedded manifest. The Python equivalent
is `verify_against_document(parse_file("case.md"), "edited.docx")`. It validates
text only; inspect formatting separately.
