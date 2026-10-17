# Final engineering report

Verbatim-MD **0.1.0** is a working local-first Python converter and a local open-source
release candidate. It preserves canonical quotation text, creates ordinary DOCX
with independently authored Verbatim style conventions, and verifies exported text
before publishing output. Its structural converter is tested; full interactive
Verbatim compatibility is **not established**. The installed Debate ribbon's Shrink
command failed before dispatch in the observed desktop environment.

Repository: this Git checkout, with package source in `src/verbatim_md`. No public repository, package upload or public release was created.
Inspect `git log -1` for the final local commit identity.

## Delivered software and architecture

The repository contains the installable Python package and `verbatim-md` CLI,
strict Markdown specification/parser, frozen document/source/card/span schema,
shared semantic validation, DOCX renderer, two formatting profiles, safe template
style import, integrity manifests, external canonical-text comparison, tests,
original LD case/block examples, three reusable agent skills, contributor guidance,
architecture decisions, security/license reviews and GitHub test/release workflows.

The implementation follows these decisions:

- Store quotations as immutable Unicode strings. Presentation uses independent
  half-open Unicode code-point spans; inline Markdown never rewrites evidence.
- Use genuine Heading1–4 paragraph styles with Pocket/Hat/Block/Tag aliases,
  Normal body/citation paragraphs, Style13ptBold/Cite and StyleUnderline character
  styles, plus Emphasis. Only explicit citation ranges receive Cite.
- Split rendering at formatting endpoints, preserving crossed spans and paragraph
  boundaries. A sweep and explicit paragraph counter avoid repeated full-document
  scans. XML-invalid text, unsupported syntax, bounds and type errors are rejected.
- Validate and render to a temporary sibling, compare extracted text with the
  immutable input, then publish atomically. Existing output requires explicit
  overwrite. Export never fetches source URLs or authenticates publications.
- Record SHA-256, full declared provenance and paragraph positions in a passive
  manifest. It detects changes against its baseline but is neither signed nor a
  source-authentication system. `inspect --against` uses original Markdown when
  Word discards the manifest.
- Keep conversion offline and macro-free. Runtime dependencies are python-docx,
  PyYAML and defusedxml. No upstream Verbatim code/template is incorporated.

ADRs explain the evidence model, independent DOCX/licensing boundary and atomic
verification design. Shared limits are 10 MiB canonical text/metadata, 10,000 spans
per card/citation and 100,000 generated paragraphs. Markdown input has its own
10 MiB UTF-8 limit and YAML nesting is bounded to 64 levels.

## Actual agent assignments

Eight actual agents participated through staged, nonconflicting ownership. The
lead coordinated contracts, integrated changes, implemented shared integrity/API
work and fixes, and performed desktop checks.

| Agent | Specialized assignments and completed work |
| --- | --- |
| research | A research and C rendering: official references, style facts, compatibility matrix, styles/renderer and renderer tests |
| parser | B parser/schema and initial G documentation: strict syntax, fixtures, parser tests, examples, docs and skills |
| security | H initial licensing/security and F packaging: dependency/license inventory, CLI, profiles, locks, CI and packaging tests |
| integrity_scaling | D evidence model completion: rendering scalability, provenance retention, shared limits and regressions |
| audit_evidence | E independent QA and Audit A: adversarial text/style/span/package tests and evidence audit; no production ownership |
| audit_oss | Independent Audit B: malformed-input, template/path, dependency, wheel/sdist/install and release review |
| cli_acceptance | Dedicated F acceptance: installation/CLI/DX verification and contributor installation guidance |
| docs_acceptance | Dedicated G acceptance: examples/spec/skills consistency, final skills updates and this engineering report |

Independent auditors reproduced defects rather than accepting implementation
reports. The lead resolved detected blockers, and auditors reran their regressions.
See [Audit A](AUDIT_EVIDENCE.md) and [Audit B](AUDIT_OSS.md).

## Supported Markdown and formatting

Version 1 supports YAML source/provenance metadata, stable source/card IDs,
`#` through `####` hierarchy, `:::card` evidence and `:::analytic` original reasoning.
Literal fenced text preserves Unicode, tabs, punctuation, internal blank lines,
leading/trailing spaces and explicitly represented trailing LF characters.
Optional SHA-256 pins detect changed quotation text.

Evidence spans support highlight, underline, emphasis (bold plus underline) and
explicit small text. Citation spans additionally support Cite. Spans can overlap,
cross, nest and cross paragraphs. `shrink_unread` follows the documented
non-underlined selection rule; highlighting alone does not protect text from
shrinking. `small` explicitly overrides normal size. Profiles control fonts,
sizes, highlight color, margins and shrink policy. Reference DOCX imports only
recognized passive style definitions, while retaining required semantic aliases.

This is a strict Markdown subset. It rejects CRLF rather than normalizing it,
does not parse ordinary Markdown inline formatting, and reserves an exact standalone
three-backtick body line. Such a quotation must use the programmatic API rather
than deleting or rewriting evidence to fit the syntax. Missing citation Cite
ranges produce a warning; the converter cannot safely infer author/date boundaries.

## Automated verification and independent review

Actual local test environment: macOS **26.6.1**, CPython **3.12.13**.

| Check | Actual result |
| --- | --- |
| Full unit/integration/regression suite, documentation acceptance rerun | **116 passed** (final lead coverage run) |
| Final measured statement coverage | **91%** |
| Ruff over src, tests and scripts | Passed |
| mypy over all 11 package modules | Passed |
| Independent evidence/style suites | 42 passed on final renderer/API recheck |
| Independent security regressions | 18 passed before final packaging follow-up |
| All three original examples | Validate/build/extract/style report passed |
| README and Markdown-spec embedded examples | Parsed successfully |
| Wheel and sdist build, Twine metadata | Passed in independent packaging audit |
| Separate wheel installation outside checkout and CLI flow | Passed in independent packaging audit |
| Locked dependency advisory scan after setuptools upgrade | No known vulnerabilities found at review time |
| Repeated normalized wheel and sdist builds | Byte-identical for the same source/toolchain/epoch |

Tests include exact per-character overlapping styles, LF/Unicode/combining
characters/tabs/trailing whitespace, multi-card reset, a 3,000-line quotation,
malformed YAML/XML/ZIP/metadata, template identities, pinned hashes, API/CLI parity,
no-clobber writes, batch symlink escapes, missing manifests and post-export tampering.
A semantic golden style contract is independently authored; no third-party binary
reference document is redistributed.

Important resolved findings included ignored added table content, malformed API
objects escaping validation, non-actionable malformed DOCX exceptions, strict API
warnings being ignored, batch output symlink escape, template identity errors,
font themes overriding selected fonts, and LibreOffice rejecting a prefixed OPC
content-type root. Initial setuptools 82.0.1 advisory exposure was resolved by
upgrading locked build tooling to 83.0.0. An advisory scan is time-bounded evidence,
not proof of absence of all vulnerabilities.

## End-to-end demonstration

From an installed checkout:

```bash
python scripts/demo.py --out artifacts/demo
```

The script processes `single-card.md`, `ld-aff-case.md` and `ld-blockfile.md` through
validation, DOCX generation, extraction against canonical input, style verification
and an explicitly scoped compatibility report. It writes DOCX files and
`report.json`. All three passed. The single-card quotation's UTF-8 SHA-256 is:

```text
d344311c585259251026a5f717def0732b888ed30e3ae08c52dccacce1240e22
```

The same quotation hash and full paragraph sequence matched the supplied canonical
Markdown after the observed Word save workflows. This is internal text preservation,
not evidence that the tutorial passage is an authenticated research source.

## Real Word and Verbatim observations

The lead tested disposable original examples on macOS **26.6.1**, Word **16.114**,
and installed Verbatim app **6.0.0**. The original user's brief was not modified,
converted into open-source fixtures or packaged.

- Generated single-card DOCX opened without a repair dialog, in Word Compatibility
  Mode. The Navigation Pane displayed all four expected heading levels.
- Citation style, highlight, underline, emphasis and explicit small text were
  visible. Word Save As modern DOCX, close and reopen succeeded without repair.
  Extracted text/order matched original Markdown. OOXML inspection retained the
  effective tested character formatting; Word removed some redundant direct sizes.
- Home's Verbatimize action attached the Debate ribbon and updated appearance.
  Saved text/order remained exact. Appearance changes from the user's template
  are separate from the converter's original profile.
- Word discarded the passive manifest. Standalone inspection therefore reports
  unknown preservation; comparison with `--against original.md` passed.
- Shrink failed with VBA error **5852** at Verbatim's `RibbonMain` customization
  context/attached-template statement, before command dispatch. Retrying with a
  body-text cursor produced the same error. No installed VBA or settings were
  changed. This blocks a successful Shrink or general ribbon-command claim.
- Send to Speech, Condense, speech-document card/block copying, Windows Word,
  other Word/Verbatim versions and unusual interactive multi-paragraph layouts
  remain unverified. See the full [compatibility matrix](COMPATIBILITY.md).

All three examples were also rendered with the bundled LibreOffice tool and
visually reviewed. Those checks support layout correctness only; they do not
establish Verbatim macro compatibility.

## Installation and use

Python **3.11+** is required. Generation needs neither Word nor Verbatim, cloud
credentials nor a database. Install dependencies once; conversion then works offline.

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install .
verbatim-md validate examples/single-card.md --json
verbatim-md build examples/single-card.md -o single-card.docx --profile ld --json
verbatim-md inspect single-card.docx --json
verbatim-md inspect word-edited.docx --against examples/single-card.md --json
verbatim-md build-all examples --out dist/examples --json
verbatim-md profiles list
```

`--force` permits output replacement. `--strict` treats warnings, including
unverified sources or missing Cite ranges, as failures. Exit codes are 0 success,
1 failed validation/batch work, and 2 input/configuration/usage/I/O error.

```python
from verbatim_md import parse_file, export_document, verify_against_document

document = parse_file('case.md')
report = export_document(document, 'case.docx', profile='ld')
assert report['integrity']['internally_preserved']
assert verify_against_document(document, 'case.docx')['internally_preserved']
```

## Licensing, security and release status

The original converter and tutorial samples use MIT. Verbatim is separately GPL-3.0;
its VBA, XML/template assets and installers are absent from distribution. Dependency
licenses remain their own. No proprietary evidence is bundled. See
[licensing](LICENSING.md) and [security review](SECURITY.md).

The release wrapper uses installed hash-locked build tools, SOURCE_DATE_EPOCH and
canonical source-archive metadata. Standard builds are supported, but standard
unnormalized sdist timestamps were not byte reproducible. For the reproducible path:

```bash
python -m pip install --require-hashes -r requirements-dev.lock
python -m pip install --no-build-isolation --no-deps -e .
python scripts/reproducible_build.py
python -m twine check dist/*
```

GitHub CI targets Linux/macOS/Windows and Python 3.11–3.13. Those remote jobs are
configured, not claimed to have run. The release workflow prepares review artifacts
and never publishes. No GitHub remote is configured in this local checkout.

No unresolved software/security blocker was identified by the two independent
reviews after fixes. The observed Verbatim ribbon failure remains a blocker to
claiming full interactive compatibility. Resolving that prerequisite, rerunning
versioned macro workflows, obtaining publication authorization, selecting/creating
the GitHub repository, configuring private vulnerability reporting and checking the
public package name are the exact remaining external release actions. The project
can be reviewed locally as a limited structural converter release candidate now.
