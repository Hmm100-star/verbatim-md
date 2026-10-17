# Troubleshooting

**A line-numbered error stops validation.** Correct the structure or metadata
identified by the message, then rerun `validate`. Unknown keys and duplicate YAML
keys are intentional errors. Quote date strings and IDs that resemble numbers.
Never silently edit evidence to make a validation error disappear.

**A span is outside the quotation.** Count Python Unicode code points in the
canonical string, including tabs and newlines. Use `inspect case.md --json` to
read the parsed string. Offsets are `[start,end)`. Emoji and combining marks may
occupy different lengths in JavaScript, a Word selection, or your visual editor.
Recalculate formatting offsets; preserve quotation wording.

**A SHA-256 mismatch occurs.** Restore the reviewed text from version control or
compare it to the original source. Only repin the hash after explicit evidence
review. Formatting changes alone never require a new text hash.

**The source is unverified.** Default conversions succeed with a warning. Strict
mode fails on that warning. Verify against the original publication and record
truthful provenance, or keep the warning. Do not manufacture a reviewer/date to
silence it. Tutorial examples are intentionally unverified.

**CRLF is rejected.** Save the Markdown file with LF endings explicitly and review
the resulting canonical quotation text and offsets. The converter does not
silently normalize text. Git contributors should retain LF for `.md` fixtures.

**Output exists.** Choose another path, or deliberately pass `--force`. Inputs
cannot be overwritten by builds. Batch output must be outside the input tree.

**Word navigation or a macro behaves differently.** Check real paragraph style
IDs and aliases with `inspect`, then follow `COMPATIBILITY.md`. Use a legitimate
local Verbatim installation. A generic DOCX viewer cannot certify macros. Supply
a sanitized minimal reproduction without private or unlicensed evidence.

**A reference template is rejected.** Only trusted, macro-free `.docx` reference
files are supported. See `templates/README.md`. Do not rename a `.dotm` or `.docm`
file to bypass checks. Conversion never needs an upstream template.

**Pagination differs.** Install the profile font in the target viewer and check
page size/margins. Font substitution and Word versions affect line wrapping.

**Installation fails offline.** Install dependencies first, or prepare a wheelhouse
on an online computer using `pip download .`, then install with `--no-index
--find-links`. The actual converter has no runtime network operations.
