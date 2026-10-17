# Independent evidence and Verbatim structure audit

Audit date: 2026-10-17. The audit agent did not implement the parser, renderer,
validator or evidence inspector. This pass inspected production code, actual
exported OOXML and documented scope, then added adversarial regressions rather
than relying on implementation authors' reports.

## Method and findings

The independent suites are `tests/integration/test_integrity.py` and
`tests/regression/test_adversarial.py`. They exercise canonical LF/Unicode,
combining marks, astral characters, tabs, leading/trailing spaces, empty lines,
trailing newlines, a 3,000-line quotation, exact overlapping character ranges,
and formatting reset on the next card. Actual OOXML is inspected for Heading1–4
paragraph styles and outline levels, character style types, and Cite ranges.

Initial release-blocking findings were reproduced and sent to the lead:

- An additional evidence table escaped the original paragraph-only preservation
  comparison. The inspector now marks unsupported body content as unverifiable.
- Malformed programmatic text and unknown block types raised AttributeError
  instead of actionable input errors. Runtime model validation now rejects them.
- The API accepted duplicate spans, mutable block lists and whitespace-only
  verification provenance although the parser rejected them. Validation is now
  consistent across entry points.
- An invalid heading type contaminated later hierarchy comparisons; invalid
  surrogate text reached hashing before its semantic error. Regression coverage
  requires actionable rejection for both.

The final rerun status is recorded below after the lead's fixes. No production
source was changed by this audit agent.

## Evidence boundaries

Passing these checks establishes text preservation for supported generated
packages, not source authenticity. Source verification remains an explicit author
assertion. Hashes and the embedded manifest are not signatures: changing both
the manifest and document can evade corruption detection. Keep reviewed original
Markdown independently. The report's `internally_preserved` field describes text;
it does not certify that a later editor preserved every formatting property.

The supported Markdown v1 explicitly reserves the standalone three-backtick
literal line. Such quotations require the programmatic API; never remove that
line to make a card fit. CRLF must be explicitly saved as LF before offsets are
computed. These documented constraints reject input rather than rewrite it.

## Compatibility conclusion

Actual generated packages use the documented/inspected Verbatim 6 style IDs,
heading hierarchy, Cite character ranges and OOXML highlight/underline/font-size
properties. This is structural interoperability evidence only. No Microsoft Word
repair-warning, VBA macro, navigation, copying, Send to Speech, Shrink/Condense or
Word save/reopen workflow was executed by this audit. Those versioned manual
checks remain unverified in `COMPATIBILITY.md` and block universal compatibility
claims, not local generation of structurally tested DOCX.

## Final independent rerun

`PYTHONPATH=src .venv/bin/python -m pytest tests/integration/test_integrity.py tests/regression/test_adversarial.py -q`: **30 passed**.

`ruff check` on both independent test files: **passed**. No skipped, xfail or
expected-failure markers conceal the reproduced findings. All identified
release-blocking findings in these suites were resolved by the lead and the
independent rerun passed.

## Final renderer and external verification recheck

A second independent recheck followed the lead's LibreOffice/Word investigation
and renderer scaling changes. The independent suites now contain **42 passing
tests**, including the original regressions. Latest command:

```sh
PYTHONPATH=src .venv/bin/python -m pytest tests/integration/test_integrity.py tests/regression/test_adversarial.py -q
```

Result: **42 passed in 3.19 seconds**. Ruff on both files passed. This recheck
added these requirements against actual exports:

- `[Content_Types].xml` retains the conventional default OPC namespace rather
  than an `ns0:Types` root, preventing regression of the lead's observed
  LibreOffice compatibility failure.
- All eight authored styles have explicit Arial fonts without theme attributes;
  Heading1–4 explicitly disable italics. This avoids theme font precedence.
- Same-attribute overlapping spans retain their active state as one span ends;
  cross-paragraph range and reset tests continue passing with the endpoint sweep.
- API inputs exceeding the canonical byte or per-card span limits are rejected
  before rendering. The large 3,000-line text regression continues passing after
  paragraph proxy counting was replaced with an explicit index.
- Manifest inspection retains declared citation, URL, reviewer and date, while
  preserving the distinction between an author assertion and source verification.
- `verify_against_document` succeeds against trusted external canonical input
  both with and without the embedded manifest; detects changed text and added
  tables after manifest loss; and rejects invalid ZIP or unsafe XML input.
  Its result explicitly states that formatting was not verified.

The lead subsequently performed real Word observations; those versioned results
belong in `COMPATIBILITY.md`. This audit agent did not independently operate Word
or execute Verbatim macros, and the earlier no-interactive-test statements above
refer to this audit agent's own pass. In particular, failed Shrink dispatch must
not be presented as successful execution of Shrink formatting.
