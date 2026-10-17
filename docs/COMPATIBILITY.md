# Compatibility test matrix

The supported target is a macro-free DOCX that implements the documented
Verbatim 6 Word style conventions. This is not certification of every Verbatim
macro or Word version. See [research specification](VERBATIM_SPEC.md).

| Feature | Automated structural check | Real Word plus Verbatim |
| --- | --- | --- |
| Heading1–4 plus Pocket/Hat/Block/Tag aliases | required | unverified |
| Normal evidence body | required | unverified |
| Cite character style on explicit citation ranges | required | unverified |
| Exact Unicode quotation and paragraph preservation | required | unverified after Word save |
| Word highlight, underline, emphasis, small sizes | required | unverified |
| Overlapping and cross-paragraph formatting | required | unverified |
| Navigation outline and drag organization | outline properties checked | unverified |
| Card/block copying and Send to Speech | no macro execution | unverified |
| Shrink and Unshrink | static profile output checked | unverified macro interaction |
| Condense and Uncondense | intentionally not implemented | unverified; can alter text |
| Update Styles and user profiles | converter profiles checked | unverified; can override appearance |
| Save/reopen without repair warnings | ZIP/XML checks only | unverified |
| Reference template import | styles-only boundary checked | unverified |

Automated test output and the final engineering report record actual pass/fail
results. A required test listed above is not a claim that it already passed.
No Microsoft Word/Verbatim interactive test was performed during initial
research. LibreOffice or other generic viewer rendering is layout evidence only.

## Reproducible manual suite

Run on both Windows desktop Word 2019+/365 and macOS desktop Word 2019+/365
using a legitimate Verbatim 6 installation; record exact OS, Word, Verbatim
versions, user style profile, date, and result for each operation.

1. Build all bundled examples; validate and inspect them. Preserve originals.
2. Open outputs in Word. Record any repair warnings. Compare visible paragraph
   breaks, Unicode punctuation, and citation surname/date emphasis.
3. Inspect Navigation Pane: hierarchy and section selection must match headings.
4. Copy one card and then a complete Block into a fresh Verbatim document. Verify
   text order, citation ranges, highlight, underline, and overlapping emphasis.
5. From Tag and Block positions, Send to Speech. Compare every quotation against
   the original, including surrounding context and card boundaries.
6. On disposable copies test Shrink, Unshrink, Standardize Highlight, Update Styles,
   Condense with/without pilcrows, and Uncondense. Record intended text changes
   separately from unexpected omissions or duplication. Never treat Condense as
   evidence-preserving by definition.
7. Save, close, reopen. Inspect resulting DOCX against canonical Markdown. If Word
   removed converter metadata, report inability to authenticate card boundaries
   rather than declaring preserved evidence without a comparison.
8. Repeat with multiline evidence, astral Unicode, adjacent cards, crossing spans,
   and custom local style settings. Record failures and attach legally shareable
   minimal reproductions, not copyrighted evidence or the upstream template.

Do not publish a completed interactive compatibility claim until this matrix
contains actual versioned observations. Template macros and settings remain the
user's responsibility; generation never installs or runs them.

## Observed local desktop results

2026-10-17, macOS (version recorded in FINAL_AUDIT.md), Word **16.114**, installed
Verbatim app **6.0.0**. These observations cover the original single-card example,
not a cross-platform certification.

| Operation | Actual result |
| --- | --- |
| Open generated DOCX | Passed; no repair dialog; opened in Compatibility Mode |
| Navigation pane | Passed; all four heading levels visible in order |
| Citation/highlight/underline/emphasis/small | Visible; OOXML checked before and after Word Save As; effective formatting retained |
| Word Save As modern DOCX, close, reopen | Passed; canonical text/order comparison passed; no repair dialog |
| Embedded JSON manifest after Word save | Removed by Word; standalone inspect correctly reports unknown preservation |
| Compare saved DOCX against original Markdown | Passed using `inspect --against` |
| Home Verbatimize | Attached Debate ribbon and updated appearance; saved text/order remained exact |
| Debate Shrink, heading focus and body cursor | Failed with VBA run-time error 5852 before Shrink dispatch |
| Send to Speech, Condense, card/block copy to native speech | Unverified; ribbon dispatch failure prevents claiming these workflows |
| Windows Word | Unverified |

VBA Debug located the failure in installed Verbatim `RibbonMain`, at the
customization-context/attached-template selection statement, before the command's
case dispatch. This is an observed integration failure, not proof that Shrink's
implementation or converter text is defective. No installed macro code or app
settings were changed. Do not promise Shrink or other Debate ribbon commands on
this environment until that prerequisite is resolved and the workflows rerun.
Use the converter's static shrinking profile independently of interactive macros.

Word may update styles when Verbatimize attaches the user's template; that is a
separate transformation from the original converter profile. Keep the original
Markdown and compare every quotation after Word workflows. The complete original
single-card paragraph sequence and quotation SHA-256 matched both after
Verbatimize/save and after modern Word Save As/reopen.

All three original examples also rendered to one page each with the bundled
LibreOffice renderer and were visually inspected for clipping and missing text.
An initial prefixed OPC content-type namespace caused LibreOffice import failure;
the converter now uses the conventional default namespace, with regression
coverage. Viewer rendering is layout evidence, not macro compatibility proof.
