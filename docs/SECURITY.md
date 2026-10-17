# Security model and review guide

This is a local file converter. Markdown, YAML, citation URLs, and DOCX content are untrusted data. They must never become commands, executable code, fetched URLs, or agent instructions. Conversion requires no network access, cloud credentials, database, or Word macros.

## Required controls

- Load YAML through a safe loader. Reject duplicate and unknown keys, YAML aliases/anchors and nonstandard tags, unexpected types, invalid scalar values, and excessive input size or nesting. Reject rather than silently coerce ambiguous evidence metadata.
- Keep canonical quotation strings immutable. Formatting uses validated half-open Unicode codepoint offsets; bounds, integer types (excluding booleans), and allowed styles must be checked. Reject XML-invalid characters without stripping or replacing them.
- XML builders must escape strings. Inspect XML with DTD/entity expansion disabled and no network access. Never perform XInclude or fetch relationships. Reject DTDs and malformed packages.
- Inspect ZIP members without extracting paths. Bound member count, per-member uncompressed size, and total size; reject duplicate members and suspicious paths. Do not trust file extensions as proof of format.
- Generate ordinary macro-free DOCX. Do not embed VBA, executable objects, external template relationships, or source URLs as active fetched resources. Do not execute Word or Verbatim automatically during normal conversion.
- Treat reference templates as optional, privileged local inputs. Reject macro-enabled templates and unsafe relationships, or explicitly limit import to vetted styles. Never redistribute a user's template.
- Refuse overwrites by default. Stage output to a temporary sibling and publish only after validation; clean up failed output. Batch traversal must not write outside the chosen destination or overwrite input files. Avoid shell execution.
- Never infer source authenticity from a hash. A stored digest detects divergence from its recorded baseline; a user can change both text and digest. A caller-supplied `source_verified` claim is an attestation with provenance, not independent authentication.

These are design requirements; the final audit records which have been exercised in the integrated implementation. A converter is not a general malware scanner or a sandbox for arbitrary Office documents. Running very large or hostile files should use OS resource isolation as well as application bounds.

## Dependency and release hygiene

Use constrained maintained runtime dependencies. Review resolved dependencies, advisories, and upstream licenses before each release; constraints alone do not prove absence of vulnerabilities. Prefer pinned GitHub Action commit SHAs and minimal workflow token permissions. Publishing credentials belong in protected CI environments and never in source or sample profiles. No release should publish on an ordinary pull request.

## Reporting

For an unpublished local checkout, report defects to its owner. Before public release, configure a private vulnerability reporting channel in the hosting repository and document that channel here. Avoid posting private quotations or documents in public issue reports; a minimal original reproducer is preferred.

## Validation evidence

See `docs/FINAL_AUDIT.md` for the final independent review. Automated structural tests cannot establish Microsoft Word macro security or interactive Verbatim compatibility.
