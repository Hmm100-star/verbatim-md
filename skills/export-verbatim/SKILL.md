---
name: export-verbatim
description: Validate and export Verbatim-MD to DOCX, inspect evidence integrity and styles, and report actual Word and Verbatim compatibility limits.
---

# Export Verbatim

Trigger for Markdown-to-DOCX export, batch build, failed formatting diagnosis or
compatibility inspection. Read `docs/MARKDOWN_SPEC.md`, `docs/FORMATTING.md` and
`docs/COMPATIBILITY.md` before making compatibility claims.

## Procedure

1. Run `verbatim-md validate input.md --json`. Review errors and unverified-source
   warnings. Use `--strict` only when the workflow requires zero warnings.
2. Inspect `verbatim-md inspect input.md --json`. Confirm canonical evidence,
   IDs, citation spans and source status. Repair invalid metadata or offsets while
   preserving quotation strings. Do not automatically repin a mismatched hash.
3. Run `verbatim-md build input.md -o output.docx --profile ld --json` (or choose
   `default`/a reviewed local YAML profile). Existing output is protected; use a new
   path unless explicit overwrite is intended. `--force` permits replacement.
4. For a directory, run `verbatim-md build-all cases --out dist --json`; output
   must be outside the input tree. Check every batch result and process exit code.
5. Run `verbatim-md inspect output.docx --json`. Require `internally_preserved`
   true and no errors. This verifies internal consistency, not original-source
   accuracy. Also run `verbatim-md inspect output.docx --against input.md --json`
   to compare with immutable Markdown rather than trusting the embedded manifest.
   After Word save/copy operations, the manifest may be removed; `--against`
   still verifies text/order against the original. It does not verify formatting.
6. Inspect reported style IDs and, when needed, `word/styles.xml` and run
   properties against the documented structural matrix. Use automated regression
   tests for exact highlight, underline, citation and font ranges.
7. Where Word/Verbatim is available, follow the manual matrix for navigation,
   card copying, sending to speeches, shrink/condense and save/reopen. Record exact
   app versions and OS. Test only disposable copies with explicitly authorized
   use of a legitimate installed Verbatim version. A generic viewer or OOXML test
   cannot prove macro behavior. Consult the observed error 5852 limitation before
   claiming that Shrink or other Debate ribbon commands work in the tested setup.

## Permitted operations and errors

You may validate, generate local files, inspect ZIP/XML passively, and repair
presentation metadata. Use trusted macro-free reference DOCX files only. Do not
execute untrusted document macros or bypass template checks. Do not upload private
evidence, publish artifacts, or run interactive macros without authorization. If integrity fails, withhold the export
and diagnose the character discrepancy. If Word testing is unavailable, complete
structural checks and explicitly mark interactive features unverified.

## Expected output

A DOCX, conversion/inspection reports, actual test results, declared evidence
verification status and a compatibility statement that separates structural
checks from live Word/Verbatim testing. Report missing-manifest or failed
preservation findings; never relabel them as successful verification.
